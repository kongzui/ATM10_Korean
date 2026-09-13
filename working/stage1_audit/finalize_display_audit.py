"""저장된 조사에 표시 코드 근거와 최종 안전·퀘스트 검증을 추가해요."""

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
DEST = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_ae2_quests import parse_language_snbt, validate_value  # noqa: E402
from local_paths import resolve_source_root  # noqa: E402
from snapshot_instance import collect  # noqa: E402
from verify_compat_release import SnbtReader  # noqa: E402
from verify_stage1_translation import check_value  # noqa: E402


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(name, value):
    (DEST / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main():
    instance = resolve_source_root(None)
    javap = Path("C:/Program Files/Java/jdk-17/bin/javap.exe")
    client = Path(
        "C:/Users/moon9/curseforge/minecraft/Install/libraries/net/neoforged/"
        "neoforge/21.1.249/neoforge-21.1.249-client.jar"
    )
    classes = {
        instance / "mods/auroral-1.21.1-1.1.1.jar": [
            "com.breakinblocks.auroral.registry.ModItems",
            "com.breakinblocks.auroral.registry.ModBlocks",
            "com.breakinblocks.auroral.Auroral",
            "com.breakinblocks.auroral.integration.guideme.AuroralGuide",
            "com.breakinblocks.auroral.item.AuroralGuideItem",
        ],
        instance / "mods/guideme-21.1.17.jar": [
            "guideme.internal.GuideReloadListener",
            "guideme.internal.util.LangUtil",
        ],
        client: ["net.minecraft.world.item.BlockItem"],
        instance / "mods/modonomicon-1.21.1-neoforge-1.120.4.jar": [
            "com.klikli_dev.modonomicon.book.BookTextHolder",
            "com.klikli_dev.modonomicon.util.BookGsonHelper",
            "com.klikli_dev.modonomicon.book.page.BookTextPage",
            "com.klikli_dev.modonomicon.book.page.BookEntityPage",
        ],
        instance / "mods/ftb-quests-neoforge-2101.1.34.jar": [
            "dev.ftb.mods.ftbquests.quest.Quest",
            "dev.ftb.mods.ftbquests.quest.task.ItemTask",
        ],
    }
    evidence = []
    for jar, names in classes.items():
        with ZipFile(jar) as archive:
            for name in names:
                member = name.replace(".", "/") + ".class"
                command = [str(javap), "-p", "-c"]
                if name.endswith("LangUtil"):
                    command.append("-v")
                command += ["-classpath", str(jar), name]
                result = subprocess.run(command, capture_output=True, check=True)
                evidence.append(
                    {
                        "jar": str(jar),
                        "member": member,
                        "class_sha256": hashlib.sha256(
                            archive.read(member)
                        ).hexdigest(),
                        "command": command,
                        "javap": result.stdout.decode("utf-8"),
                    }
                )
    save(
        "bytecode_display_evidence.json",
        {
            "method": "JAR 읽기 전용: ZipFile 멤버 해시 및 설치된 javap 역어셈블. 실행/추출 없음.",
            "evidence": evidence,
            "conclusions": {
                "glow_leek_seeds": "ModItems.registerSimpleBlockItem(glow_leek_seeds, ModBlocks.GLOW_LEEK) -> BlockItem.getDescriptionId -> Block.getDescriptionId -> block.auroral.glow_leek",
                "auroral_guide": "Auroral -> isLoaded(guideme) -> AuroralGuide.init folder(auroral); AuroralGuideItem.use -> GuidesCommon.openGuide(auroral:guide)",
                "guide_ko_prefix": "resourcepack/ATM10_Korean/assets/auroral/auroral/_ko_kr/",
                "guide_locale": "GuideReloadListener.loadPages -> LangUtil.getTranslatedAsset(pageId,language) -> withPrefix('_'+language+'/'); 다시 contentRootFolder prefix",
                "neovitae_literals": "BookTextPage/BookEntityPage.fromJson -> BookGsonHelper.getAsBookTextHolder -> BookTextHolder.getString -> I18n.get(string,[]) 사용. 원문 전체를 추가 언어 키로 쓸 수 있는 정적 경로.",
            },
            "game_screen_validation": "not_run",
        },
    )
    inventory = read(DEST / "jar_classification.json")
    metadata = read(instance / "minecraftinstance.json")
    for row in inventory["rows"]:
        proof = [
            p
            for p in metadata["installedModpack"].get("filePaths", [])
            if p.replace("\\", "/").endswith("/overrides/mods/" + row["jar"])
        ]
        if proof and row["manifest_file_id"] is None:
            row["classification"] = "팩 overrides 제공 JAR"
            row["pack_override_evidence"] = proof
    inventory["counts"] = dict(Counter(x["classification"] for x in inventory["rows"]))
    save("jar_classification.json", inventory)
    compat = read(DEST / "english_baseline_and_compat.json")
    for chapter in compat["chapter_structure"]:
        for delta in chapter["changes"]:
            if delta["path"].endswith("/order_index"):
                delta["kind"] = "순서"
        chapter["counts"] = dict(Counter(x["kind"] for x in chapter["changes"]))
    save("english_baseline_and_compat.json", compat)
    guide = read(DEST / "neovitae_guide_sources.json")
    candidates = [
        {"file": row["member"], **value}
        for row in guide["files"]
        for value in row["visible_non_language_candidates"]
    ]
    with ZipFile(instance / "mods/neovitae-1.21.1-1.1.15.jar") as archive:
        neo_english = json.loads(archive.read("assets/neovitae/lang/en_us.json"))
        missing_guide = sorted(
            {
                x["key"]
                for row in guide["files"]
                for x in row["language_references"]
                if x["english"] is None
            }
        )
    save(
        "neovitae_guide_literal_routes.json",
        {
            "candidates": candidates,
            "candidate_count": len(candidates),
            "missing_referenced_book_keys": missing_guide,
            "raw_english_key_route": "BookTextHolder 문자열 전체 -> I18n.get; exact literal-key 추가로 처리 가능. 3053키 이외 추가키 검증 계약 필요.",
            "literal_warning": "61개가 모두 미번역 오류는 아니에요. Latin 이름은 유지 가능해요.",
            "neovitae_language_auroral_mentions": {
                k: v for k, v in neo_english.items() if "auroral" in (k + v).lower()
            },
            "game_screen_validation": "not_run",
        },
    )
    errors = []
    checks = {}
    for mod, chapter in (("auroral", "auroral"), ("neovitae", "neo_vitae")):
        source = (
            instance
            / f"config/ftbquests/quests/lang/en_us/chapters/{chapter}.snbt_merged"
        )
        target = ROOT / f"working/{mod}/quests_ko_kr.snbt"
        en, ko = parse_language_snbt(source), parse_language_snbt(target)
        SnbtReader(target.read_text(encoding="utf-8")).parse()
        if set(en) != set(ko):
            errors.append(f"{mod} 키 집합 차이")
        for key in en:
            errors.extend(validate_value(key, en[key], ko[key]))
            try:
                check_value(key, en[key], ko[key])
            except ValueError as exc:
                errors.append(str(exc))
        checks[mod] = {
            "english_keys": len(en),
            "working_keys": len(ko),
            "working_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        }
    before = read(ROOT / "temp/stage1_before.json")
    after = collect(instance)
    save(
        "final_validation.json",
        {
            "quest_checks": checks,
            "errors": errors,
            "snapshot_equal": before == after,
            "tracked_files": sum(len(rows) for rows in after["files"].values()),
            "instance_writes": 0,
            "game_screen_validation": "not_run",
        },
    )
    print(json.dumps({"errors": errors, "snapshot_equal": before == after}))


if __name__ == "__main__":
    main()
