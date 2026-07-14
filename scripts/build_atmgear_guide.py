#!/usr/bin/env python3
"""Allthemodium Patchouli 안내서 전체를 한국어 리소스와 데이터 덮어쓰기로 만든다."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile

from atmgear_catalog import TARGETS
from local_paths import PROJECT_ROOT, resolve_source_root
from prepare_atmgear import find_jar

SOURCE_PREFIX = "assets/allthemodium/patchouli_books/allthemodium_book/en_us/"
OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output/resourcepack/ATM10_Korean/assets/allthemodium/patchouli_books/allthemodium_book/ko_kr"
)
BOOK_SOURCE = "data/allthemodium/patchouli_books/allthemodium_book/book.json"
BOOK_OUTPUT = (
    PROJECT_ROOT
    / "output/overrides/kubejs/data/allthemodium/patchouli_books/allthemodium_book/book.json"
)
REPORT_FILE = PROJECT_ROOT / "working/atmgear/guide_validation.json"
PATCHOULI_TAG = re.compile(r"\$\([^)]*\)")
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")

TRANSLATIONS = {
    "Armour": "방어구",
    "This will show you information about the different armour options": "여러 방어구 선택지에 관한 정보를 보여 줍니다",
    "Dimensions": "차원",
    "This will show you information about the different dimensions": "여러 차원에 관한 정보를 보여 줍니다",
    "Food Items": "음식",
    "The food items in Allthemodium": "Allthemodium의 음식입니다",
    "Links": "링크",
    "Several links if you need help. $(li)Github is good for pack issues.$(li)Discord is good to talk to others about the packs.$(li)Reddit is good for showing builds, and asking questions": "도움이 필요할 때 이용할 링크입니다. $(li)GitHub에서는 모드팩 문제를 확인할 수 있습니다.$(li)Discord에서는 다른 사람들과 모드팩에 관해 이야기할 수 있습니다.$(li)Reddit에서는 건축물을 공유하고 질문할 수 있습니다",
    "Miscellaneous": "기타",
    "Miscellaneous items that don't have enough info for one specific category": "별도의 범주로 묶기에는 정보가 적은 기타 항목입니다",
    "Ores": "광석",
    "This will show you where to find the Allthemodium specific ores.$(br2)Allthemodium, Vibranium, and Unobtainium are very rare ores, and can be hard to find.": "Allthemodium 고유 광석을 찾을 수 있는 장소를 보여 줍니다.$(br2)Allthemodium, Vibranium, Unobtainium은 매우 희귀하여 찾기 어려울 수 있습니다.",
    "Allthemodium Armour": "Allthemodium 방어구",
    "Allthemodium armour has several benefits other than just the armour, toughness and knockback resistance:$(li)Water Breathing$(li)No Crash Damage when Flying with Elytra$(li)Immune to Fire Damage$(li)No Fall Damage$(li)When you upgrade the armour from Netherite, it keeps the enchants": "Allthemodium 방어구는 방어력, 방어 강도, 밀치기 저항 외에도 여러 효과를 제공합니다:$(li)수중 호흡$(li)겉날개 비행 중 충돌 피해 무효$(li)화염 피해 면역$(li)낙하 피해 무효$(li)네더라이트 방어구를 업그레이드하면 마법 부여 유지",
    "The Mining Dimension": "채굴 차원",
    "The Mining Dimension is useful to set up quarries to mine in. It is also useful to use as a testing area since it is a superflat dimension. To teleport to the dimension use the $(l:dimensions/teleport_pad)Teleport Pad$(/c) in the Overworld.": "채굴 차원은 채석기를 설치해 자원을 캐기 좋습니다. 완전한 평지 차원이므로 시험 공간으로도 유용합니다. 이 차원으로 이동하려면 오버월드에서 $(l:dimensions/teleport_pad)텔레포트 패드$(/c)를 사용하세요.",
    "The Other": "디 아더",
    "The Other is a very hostile dimension. To teleport to the dimension use the $(l:dimensions/teleport_pad)Teleport Pad$(/c) in the Nether. Little is known of this place, but it seems to be where Piglins come from, huge underground cities exist in any biomes with tree cover on the surface, as well as dungeons and ancient pyramids full of monsters and loot": "디 아더는 매우 위험한 차원입니다. 이 차원으로 이동하려면 네더에서 $(l:dimensions/teleport_pad)텔레포트 패드$(/c)를 사용하세요. 알려진 정보는 적지만 피글린의 고향으로 보이며, 지표에 나무가 있는 생물 군계 아래에는 거대한 지하 도시가 있습니다. 몬스터와 전리품으로 가득한 던전과 고대 피라미드도 존재합니다.",
    "Teleport Pad": "텔레포트 패드",
    "The Teleport Pad is used to teleport to $(l:dimensions/miningdim)The Mining Dimension$(/c), and $(l:dimensions/otherdim)The Other$(/c) you need to shift right click with both an empty hand and off hand.$(br2)As a note, the $(l:dimensions/miningdim)The Mining Dimension$(/c) is disabled in the ATM6: To The Sky pack": "텔레포트 패드를 사용하면 $(l:dimensions/miningdim)채굴 차원$(/c)과 $(l:dimensions/otherdim)디 아더$(/c)로 이동할 수 있습니다. 양손을 모두 비우고 웅크린 채 우클릭하세요.$(br2)참고로 ATM6: To The Sky 모드팩에서는 $(l:dimensions/miningdim)채굴 차원$(/c)이 비활성화되어 있습니다.",
    "Allthemodium Apple": "Allthemodium 사과",
    "The Allthemodium Apple gives 20 hunger and 80 saturation. The apple has the following effects:$(li)Fast to Eat$(li)Can Always Eat$(li)Absorption X for 30 Sec$(li)Regeneration X for 30 Sec": "Allthemodium 사과는 허기 20과 포만도 80을 회복합니다. 다음 효과를 제공합니다:$(li)빠른 섭취$(li)허기가 가득 차도 섭취 가능$(li)30초 동안 흡수 X$(li)30초 동안 재생 X",
    "Allthemodium Carrot": "Allthemodium 당근",
    "The Allthemodium carrot gives 40 hunger and 320 saturation. The carrot has the following effects:$(li)Fast to Eat$(li)Can Always Eat$(li)Absorption X for 30 Sec$(li)Regeneration X for 30 Sec": "Allthemodium 당근은 허기 40과 포만도 320을 회복합니다. 다음 효과를 제공합니다:$(li)빠른 섭취$(li)허기가 가득 차도 섭취 가능$(li)30초 동안 흡수 X$(li)30초 동안 재생 X",
    "Discord": "Discord",
    "Discord Invite": "Discord 초대",
    "Our discord has chat rooms for each mod pack, For help and general discussion.": "Discord에는 각 모드팩의 도움말과 일반 대화를 위한 채팅방이 있습니다.",
    "Github": "GitHub",
    "Github Link": "GitHub 링크",
    "In Github you can see current issues, and mod pack updates.": "GitHub에서 현재 문제와 모드팩 업데이트를 확인할 수 있습니다.",
    "Reddit": "Reddit",
    "Reddit Link": "Reddit 링크",
    "Reddit is a good place to see the server lists, and also to ask for help, and show off builds.": "Reddit에서 서버 목록을 보고 도움을 요청하거나 건축물을 자랑할 수 있습니다.",
    "Allthemodium Tools": "Allthemodium 도구",
    "Allthemodium has several built in tools included, all of which are indestructible.": "Allthemodium에는 여러 도구가 포함되어 있으며 모두 파괴되지 않습니다.",
    "Allthemodium Ore": "Allthemodium 광석",
    "Allthemodium Ore spawns in the Deep Dark biome in cave walls and ceilings, you can also find it as a common spawn very high in the Mountains above 170Y, It can also be found everywhere in the mining dimension between Y -59 and Y 20. also Deepslate layer caves of the Other Dimension": "Allthemodium 광석은 딥 다크 생물 군계의 동굴 벽과 천장에 생성됩니다. Y 170보다 높은 산 정상에서도 비교적 흔하게 찾을 수 있습니다. 채굴 차원에서는 Y -59~20 전역에 생성되며, 디 아더의 심층암 지층 동굴에서도 발견됩니다.",
    "Unobtainium Ore": "Unobtainium 광석",
    "Unobtainium ore can be found in the End Highland biome.It spawns under Y 78.": "Unobtainium 광석은 엔드 고지대 생물 군계의 Y 78 아래에서 생성됩니다.",
    "Vibranium Ore": "Vibranium 광석",
    "Vibranium ore can be found in the Nether, above Y 64. It is also found in The Other dimension, deep underground in caves": "Vibranium 광석은 네더의 Y 64 위에서 찾을 수 있습니다. 디 아더의 깊은 지하 동굴에서도 발견됩니다.",
    "This Book wil give you information about the Allthemodium Mod, and the ATM Mod Packs": "이 책은 Allthemodium 모드와 ATM 모드팩에 관한 정보를 제공합니다",
}
USER_FIELDS = {"name", "description", "text", "title", "link_text", "landing_text"}


def translate_value(field: str, value: object, path: str, count: list[int]) -> object:
    """사용자 표시 필드만 재귀적으로 번역한다."""
    if isinstance(value, dict):
        return {
            key: translate_value(key, child, f"{path}.{key}", count)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [
            translate_value(field, child, f"{path}[{index}]", count)
            for index, child in enumerate(value)
        ]
    if field not in USER_FIELDS:
        return value
    if not isinstance(value, str):
        return value
    if value not in TRANSLATIONS:
        raise KeyError(f"안내서 표시 문구 번역이 없습니다: {path}={value!r}")
    translated = TRANSLATIONS[value]
    if PATCHOULI_TAG.findall(value) != PATCHOULI_TAG.findall(translated):
        raise ValueError(f"Patchouli 태그 순서가 다릅니다: {path}")
    source_numbers = NUMBER.findall(value)
    target_numbers = NUMBER.findall(translated)
    if any(
        target_numbers.count(number) < source_numbers.count(number)
        for number in set(source_numbers)
    ):
        raise ValueError(f"안내서 숫자가 누락되었습니다: {path}")
    count[0] += 1
    return translated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    jar_path = find_jar(instance, TARGETS[0])
    translated_fields = [0]
    output_files: list[str] = []
    with ZipFile(jar_path) as archive:
        sources = sorted(
            name
            for name in archive.namelist()
            if name.startswith(SOURCE_PREFIX) and name.endswith(".json")
        )
        for source in sources:
            value = json.loads(archive.read(source).decode("utf-8-sig"))
            relative = source.removeprefix(SOURCE_PREFIX)
            translated = translate_value("", value, relative, translated_fields)
            output = OUTPUT_ROOT / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(translated, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            output_files.append(output.relative_to(PROJECT_ROOT).as_posix())

        book = json.loads(archive.read(BOOK_SOURCE).decode("utf-8-sig"))
        translated_book = dict(book)
        translated_book["landing_text"] = translate_value(
            "landing_text",
            book["landing_text"],
            f"{BOOK_SOURCE}.landing_text",
            translated_fields,
        )
        BOOK_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        BOOK_OUTPUT.write_text(
            json.dumps(translated_book, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        output_files.append(BOOK_OUTPUT.relative_to(PROJECT_ROOT).as_posix())

    report = {
        "jar": jar_path.name,
        "localized_guide_json": len(sources),
        "book_metadata_overrides": 1,
        "translated_display_fields": translated_fields[0],
        "output_files": output_files,
        "remaining": 0,
        "status": "passed",
    }
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
