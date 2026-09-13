"""기존 Neo Vitae 퀘스트에 확정 용어만 반영한 작업본과 검수 근거를 만들어요."""

import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_ae2_quests import ENTRY_RE, parse_language_snbt, validate_value  # noqa: E402
from local_paths import resolve_source_root  # noqa: E402
from rebase_ftbquests import value_hash  # noqa: E402
from verify_compat_release import SnbtReader  # noqa: E402
from verify_stage1_translation import check_value, git_bytes  # noqa: E402


def main():
    instance = resolve_source_root(None)
    english_path = "config/ftbquests/quests/lang/en_us/chapters/neo_vitae.snbt_merged"
    structure_path = "config/ftbquests/quests/chapters/neo_vitae.snbt"
    output_path = "overrides/config/ftbquests/quests/lang/ko_kr/chapters/neo_vitae.snbt"
    folder = ROOT / "working/neovitae"
    english = parse_language_snbt(instance / english_path)
    original_text = git_bytes(f"output/8.1/{output_path}").decode("utf-8")
    original = SnbtReader(original_text).parse()
    names = json.loads((folder / "names.ko.json").read_text(encoding="utf-8"))
    hashes = json.loads(
        (ROOT / "versions/8.1/manifests/ftbquests_english_hashes.json").read_text(
            encoding="utf-8"
        )
    )["keys"]
    replacements = {
        "의식 있는": "지각 있는",
        "의식이 깃든 껍질": "지각 있는 껍질",
        "비전 서기 도구": names["item.neovitae.arcane_scribe_tool"],
        "Vitae의 오브": "Vitae 구슬",
        "Novicius Orb of Vitae": names["item.neovitae.blood_orb_weak"],
        "Discipulus Orb of Vitae": names["item.neovitae.blood_orb_apprentice"],
        "Veneficus Orb of Vitae": names["item.neovitae.blood_orb_magician"],
        "Magus Orb of Vitae": names["item.neovitae.blood_orb_master"],
        "Dominus Orb of Vitae": names["item.neovitae.blood_orb_archmage"],
        "Divinus Orb of Vitae": names["item.neovitae.blood_orb_transcendent"],
        "Novicius 오브": names["item.neovitae.blood_orb_weak"],
        "오브": "구슬",
        "연금술 마법진": "연금술진",
        "결속 마법진": "결속 연금술진",
        "소용돌이 마법진": "소용돌이 연금술진",
        "수집 마법진": "수집 연금술진",
        "윤이 나는 혈석": names["block.neovitae.bloodstone"],
        "피로 물든 유리": names["block.neovitae.blood_stained_glass"],
        "약한 피의 파편": names["item.neovitae.weak_blood_shard"],
        "마스터 의식석": names["block.neovitae.master_ritual_stone"],
        "Ritual Diviner [Dusk]": "의식 점술 도구 [Dusk]",
        "Ritual Diviner": names["item.neovitae.ritual_diviner"],
        "Ritual Configurator": names["item.neovitae.ritual_reader"],
        "마스터 라우팅 노드": names["block.neovitae.master_routing_node"],
        "라우팅 노드": "운송 노드",
        "노드 라우터": names["item.neovitae.node_router"],
        "타우 오일": names["item.neovitae.tau_oil"],
        "강한 타우": names["block.neovitae.strong_tau"],
        "약한 타우": names["block.neovitae.weak_tau"],
        "타우": "Tau",
        "데모나이트": "Demonite",
        "지옥벼림": "지옥불 단조",
        "선견자의 인장": names["item.neovitae.sigil_seer"],
        "업그레이드 서": names["item.neovitae.upgrade_tome"],
        "효과가 묻은 투척 단검": names["item.neovitae.tipped_throwing_dagger"],
        "광산 입구 열쇠": names["item.neovitae.mine_entrance_key"],
        "광산 열쇠": names["item.neovitae.mine_key"],
        "Raw Spiritus": names["item.neovitae.raw_spiritus"],
        "Raw": "미가공",
        "Aspect": "속성",
        "Animus Mote": names["item.neovitae.animus_mote"],
        "Vitaemancer": "Vitaemancy 시전자",
        "potioncrafting": "물약 제작",
        "Breaching the Edge of Demon Realm": "악마 영역의 경계를 넘어서",
        "Highway to Hell": "지옥으로 가는 길",
        "중심 운송 노드 코어": names["item.neovitae.master_core"],
        "속도 코어": names["item.neovitae.master_core_speed"],
        "Body Builder": "근육 단련",
        "Fierce Strike": "맹렬한 일격",
        "Dwarven Might": "드워프의 힘",
        "Repair": "수리",
        "티어": "등급",
        "피를": "혈액을",
        "피는": "혈액은",
        "피가": "혈액이",
        "피로": "혈액으로",
        "피 자동화": "혈액 자동화",
        "구슬&r를": "구슬&r을",
        "구슬&r와": "구슬&r과",
        "구슬&r가": "구슬&r이",
        "구슬를": "구슬을",
        "구슬가": "구슬이",
        "등급를": "등급을",
        "노드 연결 도구&r 도구로": "노드 연결 도구&r로",
        "가까운 마스터": "가까운 중심 노드",
    }
    # 아이템 자체를 소개하는 제목은 실제 작업 아이템 이름과 맞춰요.
    titles = {
        "quest.0BA0AA8A6F07D383.title": names["item.neovitae.arcane_scribe_tool"],
        "quest.56F4E4845B8F12BB.title": names["item.neovitae.tabula_rasa"],
        "quest.7AFEB7A91DC8F413.title": names["item.neovitae.blood_orb_apprentice"],
        "quest.1B6642BBDAEB2BD5.title": "등급 II: "
        + names["item.neovitae.blood_orb_magician"],
        "quest.11F6669733F1420B.title": "등급 III: "
        + names["item.neovitae.blood_orb_master"],
        "quest.7731623EA92027D9.title": "등급 IV: "
        + names["item.neovitae.blood_orb_archmage"],
        "quest.3CA324BE8531F253.title": names["item.neovitae.weak_blood_shard"],
        "quest.4EE580588CC10C4E.title": names["item.neovitae.raw_demonite"],
        "quest.7C7C061FC04B89FB.title": names["item.neovitae.ingot_hellforged"],
    }

    def transform(value):
        if isinstance(value, list):
            return [transform(text) for text in value]
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value

    result = {key: titles.get(key, transform(value)) for key, value in original.items()}
    # 치환으로 달라지는 받침·조사는 해당 문장에서만 자연스럽게 맞춰요.
    fixes = {
        "quest.0BA0AA8A6F07D383.quest_desc": [("Vitae 구슬를", "Vitae 구슬을")],
    }
    for key, pairs in fixes.items():
        for old, new in pairs:
            result[key] = [line.replace(old, new) for line in result[key]]
    errors = []
    for key, source in english.items():
        if value_hash(source) != hashes[key]["sha256"]:
            errors.append(f"기존 영어 해시 변경: {key}")
        errors.extend(validate_value(key, source, result[key]))
        try:
            check_value(key, source, result[key])
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        raise ValueError("\n".join(errors))
    # 값의 따옴표 토큰만 교체해 기존 들여쓰기·배열 배치를 그대로 보존해요.
    serialized = original_text
    matches = list(ENTRY_RE.finditer(original_text))
    for index in range(len(matches) - 1, -1, -1):
        match = matches[index]
        key = match.group(1)
        if result[key] == original[key]:
            continue
        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else original_text.rfind("}")
        )
        section = original_text[match.end() : end]
        tokens = list(re.finditer(r'"(?:\\.|[^"\\])*"', section))
        before = original[key] if isinstance(original[key], list) else [original[key]]
        after = result[key] if isinstance(result[key], list) else [result[key]]
        if [json.loads(token[0]) for token in tokens] != before or len(before) != len(
            after
        ):
            raise ValueError(f"기존 퀘스트의 문자열 배치가 달라요: {key}")
        for token, value in reversed(list(zip(tokens, after))):
            section = (
                section[: token.start()]
                + json.dumps(value, ensure_ascii=False)
                + section[token.end() :]
            )
        serialized = serialized[: match.end()] + section + serialized[end:]
    SnbtReader(serialized).parse()
    target = folder / "quests_ko_kr.snbt"
    target.write_text(serialized, encoding="utf-8")
    assert parse_language_snbt(target) == result
    changed = {key: value for key, value in result.items() if value != original[key]}
    audit = {
        "schema_version": 1,
        "mod": "neovitae",
        "source_layout": "split_snbt_merged",
        "english_path": english_path,
        "english_sha256": hashlib.sha256(
            (instance / english_path).read_bytes()
        ).hexdigest(),
        "structure_path": structure_path,
        "structure_sha256": hashlib.sha256(
            (instance / structure_path).read_bytes()
        ).hexdigest(),
        "output_path": output_path,
        "output_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "baseline_value_sha256": {key: hashes[key]["sha256"] for key in english},
        "entries": [
            {"key": key, "english": value, "translation": result[key], "reviewed": True}
            for key, value in english.items()
        ],
        "validation": {
            "validate_value_errors": [],
            "check_value_errors": [],
            "game_screen_validation": "not_run",
        },
    }
    log = {
        "english_keys": len(english),
        "unchanged_reused": len(result) - len(changed),
        "term_corrected": len(changed),
        "new_keys": 0,
        "replacement_rules": replacements,
        "changes": [
            {
                "key": key,
                "english": english.get(key),
                "before": original[key],
                "after": value,
            }
            for key, value in changed.items()
        ],
        "notes": [
            "숨겨진 저작권 Task AllRightsReserved 2개는 원문 그대로 유지해요.",
            "향 제단은 전용 챕터 원문에 등장하지 않아 문구를 추가하지 않아요.",
            "원문 Ritual Diviner [Dusk]와 현재 아이템 [Tenebrae] 불일치는 원문의 Dusk를 보존하고 보고해요.",
            "419DB4A2A5A5FC58의 설명은 Mine Entrance Key, Task는 mine_key(Mine Dungeon Key)예요. 설명의 원문 이름과 실제 Task 아이템 이름을 각각 보존해요.",
            "전용 챕터 밖 chapter_2_the_star의 6FC55CF56BE22866은 Teleposer 아이템 fallback을 사용해요.",
        ],
    }
    for filename, value in (
        ("quest_audit.json", audit),
        ("quest_term_replacements.json", log),
    ):
        (folder / filename).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps({"keys": len(english), "changed": len(changed), "errors": errors}))


if __name__ == "__main__":
    main()
