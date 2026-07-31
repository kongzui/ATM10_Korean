#!/usr/bin/env python3
"""L_Ender's Cataclysm 언어와 FTB Quests 번역을 수동 재검수한다."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORK_ROOT = PROJECT_ROOT / "working/cataclysm"
LANG_ROOT = WORK_ROOT / "cataclysm"

TEXT_REPLACEMENTS = (
    ("네더라이트 괴물", "네더라이트 몬스트로시티"),
    ("현세의 잔재", "현대의 잔재"),
    ("바제트", "와제트"),
    ("로얄 드라우그", "왕실 드라우그"),
    ("이름없는", "이름 없는"),
    ("고대의 금속", "고대 금속"),
    ("괴물같은 투구", "괴물의 투구"),
    ("괴상한 뿔", "괴물의 뿔"),
    ("타오르는 잿더미", "타오르는 재"),
    ("타는 재", "타오르는 재"),
    ("흑염의 재", "타오르는 재"),
    ("이그니튬", "이그니티움"),
    ("커슘", "커스뮴"),
    ("포탈", "포털"),
    ("Yuri_0", "Yuri_O"),
    ("엔더 가디언", "엔더 수호자"),
    ("섬멸자", "절멸자"),
)

LANGUAGE_OVERRIDES: dict[str, str] = {
    "itemGroup.cataclysm.item": "L_Ender's Cataclysm: 아이템",
    "itemGroup.cataclysm.block": "L_Ender's Cataclysm: 블록",
    "item.cataclysm.monstrous_helm": "괴물의 투구",
    "item.cataclysm.monstrous_helm.desc": (
        "착용 중 체력이 절반 아래로 떨어지면 주변 개체를 밀쳐냅니다"
    ),
    "item.cataclysm.monstrous_helm2.desc": (
        "방어력, 밀치기 저항, 재생 효과가 강화됩니다"
    ),
    "item.cataclysm.monstrous_horn": "괴물의 뿔",
    "item.cataclysm.void_core.desc": "우클릭하여 공허의 룬을 소환합니다",
    "item.cataclysm.wip.desc": "개발 중",
    "item.cataclysm.ignitium_helmet.desc2": (
        "%s 키를 눌러 생명체에게 불타는 낙인 효과를 부여합니다"
    ),
    "item.cataclysm.cursium_helmet.desc2": (
        "%s 키를 눌러 범위 안에서 벽 뒤에 있는 생명체에게 발광 효과를 부여합니다"
    ),
    "item.cataclysm.cursium_chestplate.desc2": (
        "죽으면 체력 5로 부활하고 5초 동안 무적 상태가 됩니다"
    ),
    "item.cataclysm.cursium_chestplate.desc3": (
        "무적 상태가 끝나면 6분 동안 약화 효과를 받아 부활할 수 없습니다"
    ),
    "item.cataclysm.cursium_leggings.desc2": (
        "낮은 확률로 공격을 회피하며, 투사체 공격은 회피 확률이 더 높습니다"
    ),
    "item.cataclysm.cursium_boots.desc2": (
        "낙하 피해를 줄이고, %s 키를 누르면 뒤로 도약합니다"
    ),
    "item.cataclysm.soul_render2.desc": (
        "웅크린 채 사용하면 망령 도끼창을 나선형으로 소환합니다"
    ),
    "item.cataclysm.ignitium_upgrade.desc": "이그니티움 업그레이드",
    "item.cataclysm.cursium_upgrade.desc": "커스뮴 업그레이드",
    "item.cataclysm.blessed_amethyst_crab_meat.desc": (
        "축복 효과를 받습니다. 축복 중에는 어둠, 심연의 공포, "
        "심연의 화상에 면역이 됩니다"
    ),
    "item.cataclysm.ring_of_grudged": "원한의 반지",
    "item.cataclysm.ancient_metal_ingot": "고대 금속 주괴",
    "item.cataclysm.ancient_metal_nugget": "고대 금속 조각",
    "item.cataclysm.burning_ashes": "타오르는 재",
    "item.cataclysm.blessed_amethyst_crab_meat": "축복받은 자수정 게살",
    "item.cataclysm.sandstorm_in_a_bottle": "병 속의 모래폭풍",
    "item.cataclysm.sandstorm_in_a_bottle.desc": (
        "우클릭하여 주위를 도는 모래폭풍 2개를 소환합니다"
    ),
    "item.cataclysm.music_disc_the_leviathan.desc": ("Yuri_O - Predator of the Abyss"),
    "item.cataclysm.music_disc_ancient_remnant.desc": ("Yuri_O - The Dryest Beast"),
    "item.cataclysm.onyx_spawn_egg": "오닉스 생성 알",
    "block.cataclysm.obsidian_fence": "흑요석 울타리",
    "block.cataclysm.purpur_tile_pillar": "퍼퍼 타일 기둥",
    "block.cataclysm.chorus_stem": "후렴 줄기",
    "block.cataclysm.door_of_seal_part": "봉인의 문 부품",
    "block.cataclysm.cursed_tombstone.message": "힘이 아직 약하다....",
    "block.cataclysm.prismarine_brick_fence": "프리즈마린 벽돌 울타리",
    "block.cataclysm.boss_respawner": "보스 재생성기",
    "block.cataclysm.void_infused_end_stone_bricks": ("공허가 깃든 엔드 석재 벽돌"),
    "block.cataclysm.azure_seastone_mural_empty": ("청해석 벽화(억눌린 자연의 창의성)"),
    "entity.cataclysm.old_netherite_monstrosity": ("오래된 네더라이트 몬스트로시티"),
    "entity.cataclysm.netherite_monstrosity": "네더라이트 몬스트로시티",
    "entity.cataclysm.ignis.defeat_message": (
        "네더 요새에서 이그나이티드 버서커들이 깨어났습니다..."
    ),
    "entity.cataclysm.cm_falling_block": "Cataclysm 낙하 블록",
    "entity.cataclysm.the_leviathan.defeat_message": (
        "심연이 당신을 바라봅니다. 이제 바다에 코랄 골렘이 나타납니다..."
    ),
    "entity.cataclysm.abyss_blast": "심연 폭발",
    "entity.cataclysm.mini_abyss_blast": "소형 심연 폭발",
    "entity.cataclysm.porta_abyss_blast": "심연 폭발",
    "entity.cataclysm.abyss_blast_portal": "심연 폭발 포털",
    "entity.cataclysm.abyss_portal": "심연 포털",
    "entity.cataclysm.portal_abyss_blast": "포털의 심연 폭발",
    "entity.cataclysm.modern_remnant": "현대의 잔재",
    "entity.cataclysm.wadjet": "와제트",
    "entity.cataclysm.royal_draugr": "왕실 드라우그",
    "entity.cataclysm.scylla_ceraunus": "케라우노스",
    "entity.cataclysm.onyx": "오닉스",
    "effect.cataclysm.ghost_sickness": "유령 후유증",
    "effect.cataclysm.lightning_hex": "번개의 저주",
    "effect.cataclysm.over_gravity": "과중력",
    "effect.cataclysm.dragon_wound": "용의 상처",
    "flamethrower.sub": "화염방사기",
    "ministrosityhurt.sub": "네더라이트 미니스트로시티가 피해를 입음",
    "ignis_shield_break": "이그니스의 방패가 부서짐",
    "abyss_blast.sub": "레비아탄이 심연 폭발을 준비함",
    "abyss_blast_shoot.sub": "레비아탄이 심연 폭발을 발사함",
    "abyss_blast_only_charge.sub": "레비아탄이 다중 심연 폭발을 준비함",
    "abyss_blast_only_shoot.sub": "레비아탄이 심연 폭발을 발사함",
    "portal_abyss_blast.sub": "심연 폭발이 솟아오름",
    "parry.sub": "방패가 공격을 튕겨 냄",
    "scylla_music_disc.sub": "스킬라의 원곡이 재생됨",
    "scylla_roar.sub": "스킬라가 울부짖음",
    "super_lightning_strike.sub": "번개가 내리침",
    "monstrosityland.sub": "네더라이트 몬스트로시티가 쓰러짐",
    "monstrosity_music.sub": "네더라이트 몬스트로시티의 테마곡이 재생됨",
    "enderguardian_music.sub": "엔더 가디언의 테마곡이 재생됨",
    "ignis_music.sub": "이그니스의 테마곡이 재생됨",
    "harbinger_music.sub": "하빈저의 테마곡이 재생됨",
    "harbinger_prepare.sub": "하빈저가 미사일 발사를 준비함",
    "emp_activated.sub": "전기가 흐름",
    "leviathan_music.sub": "레비아탄의 원곡이 재생됨",
    "leviathan_music_1.sub": "레비아탄의 테마곡이 재생됨",
    "leviathan_music_2.sub": "레비아탄의 테마곡이 재생됨",
    "black_hole_opening.sub": "차원의 균열이 나타남",
    "koboleton_ambient.sub": "코볼레톤의 뼈가 달그락거림",
    "kobolediator_ambient.sub": "코볼레디에이터가 신음함",
    "prowler_idle.sub": "배회자가 정상 작동함",
    "prowler_death.sub": "배회자가 정상 작동하지 않음",
    "remnant_idle.sub": "고대의 잔재가 신음함",
    "remnant_stomp.sub": "지면이 무너짐",
    "maledictus_music.sub": "말레딕투스의 테마곡이 재생됨",
    "maledictus_music_disc.sub": "말레딕투스의 원곡이 재생됨",
    "maledictus_hurt.sub": "말레딕투스가 죽음",
    "maledictus_short_roar.sub": "말레딕투스가 포효함",
    "maledictus_battle_cry.sub": "말레딕투스가 함성을 지름",
    "maledictus_spear.sub": "망령 도끼창들이 나타남",
    "hippocamtus_idle.sub": "히포캄투스가 꼬르륵거림",
    "scylla_music.sub": "스킬라의 테마곡이 재생됨",
    "the_cataclysmfarer.sub": "대격변의 여행자 테마곡이 재생됨",
    "death.attack.cataclysm.flame_strike": "%s이(가) 화염에 휩싸였습니다",
    "death.attack.cataclysm.storm_bringer": "%s이(가) %s에게 사냥당했습니다",
    "death.attack.cataclysm.maledictio": "%s이(가) %s에게 저주받았습니다",
    "death.attack.cataclysm.maledictio_anima": "%s이(가) %s에게 저주받았습니다",
    "death.attack.cataclysm.penetrate": "%s이(가) %s에게 관통당했습니다",
    "death.attack.cataclysm.lightning": "%s이(가) %s에게 감전당했습니다",
    "death.attack.cataclysm.emp": "%s이(가) 전기구이 통닭이 되어 버렸습니다",
    "death.attack.cataclysm.emp.player": ("%s이(가) 전기구이 통닭이 되어 버렸습니다"),
    "curios.identifier.rings": "반지",
    "ability.cataclysm.amethyst_cluster": "자수정 군집",
    "ability.cataclysm.amethyst_cluster.desc": (
        "주변에 자수정 군집을 발사해 개체에게 피해를 줍니다."
    ),
    "item.cataclysm.shift_desc": "[SHIFT]를 눌러 자세히 보기",
    "notice.qna": "Cataclysm 이그니스 봉제 인형에 관심이 있나요?",
    "notice.yes": "예",
    "notice.link.check": "링크 확인",
    "notice.click": "MakeShip 사이트로 이동",
    "notice.no.more": "알림 다시 보지 않기",
    "notice.open.browser": "MakeShip 사이트로 이동",
    "notice.no.more.text": ("알림을 껐습니다. 설정에서 다시 켤 수 있습니다."),
    "key.categories.cataclysm": "L_Ender's Cataclysm 키",
    "key.cataclysm.ability": "L_Ender's Cataclysm 능력",
    "key.cataclysm.helmet_ability": "L_Ender's Cataclysm 투구 능력",
    "key.cataclysm.chestplate_ability": "L_Ender's Cataclysm 흉갑 능력",
    "key.cataclysm.boots_ability": "L_Ender's Cataclysm 부츠 능력",
    "advancements.cataclysm.root.title": "L_Ender's Cataclysm",
    "advancements.cataclysm.root.description": "L_Ender's Cataclysm!",
    "advancements.cataclysm.find_ruined_citadel.title": "또 다른 요새라고?!",
    "advancements.cataclysm.find_soul_black_smith.title": "괴물이 벼려지는 곳",
    "advancements.cataclysm.burning_arena.title": "거대한 투기장",
    "advancements.cataclysm.ancient_factory.title": "어울리지 않는 곳",
    "advancements.cataclysm.sunken_city.title": "바다에 가라앉다",
    "advancements.cataclysm.cursed_pyramid.title": "새롭게 바뀐 사막 피라미드",
    "advancements.cataclysm.frosted_prison.title": "얼어붙은 감옥",
    "advancements.cataclysm.acropolis.title": "왜 하늘에?",
    "advancements.cataclysm.kill_ender_guardian.title": "저거 셜커 아니었나?",
    "advancements.cataclysm.kill_revenant.description": (
        "이그나이티드 레버넌트를 처치하세요"
    ),
    "advancements.cataclysm.kill_monstrosity.description": (
        "네더라이트 몬스트로시티를 처치하세요"
    ),
    "advancements.cataclysm.kill_ignis.description": ("이그니스를 소환해 쓰러뜨리세요"),
    "advancements.cataclysm.kill_harbinger.description": ("하빈저를 깨워 쓰러뜨리세요"),
    "advancements.cataclysm.kill_leviathan.description": (
        "레비아탄을 소환해 쓰러뜨리세요"
    ),
    "advancements.cataclysm.kill_remnant.description": (
        "저주받은 피라미드 안의 수상한 모래를 발굴해 고대의 잔재를 "
        "깨우고 쓰러뜨리세요"
    ),
    "advancements.cataclysm.kill_maledictus.description": (
        "말레딕투스를 소환해 쓰러뜨리세요"
    ),
    "advancements.cataclysm.kill_clawdian.title": "이제 새우습게 볼 수 없겠군",
    "advancements.cataclysm.kill_all_bosses.title": "대격변의 여행자",
    "advancements.cataclysm.kill_all_bosses.description": (
        "L_Ender's Cataclysm의 정상에 올랐습니다!"
    ),
}

QUEST_OVERRIDES: dict[str, str] = {
    "quest.0741FABE57CA1A7D.quest_desc": (
        "&9히포캄투스&r는 &9아크로폴리스&r를 지키는 강력한 해마 전사입니다. "
        "\n\n두꺼운 갑옷을 입고 창과 방패를 듭니다. "
        "\n\n85 &4하트&r와 방어력 18을 지녔습니다. "
        "\n\n방패로 피해를 막고 창을 휘두르거나 찌릅니다. 특수 공격에 걸리면 "
        "제자리에 묶인 채 &9히포캄투스&r에게 연속으로 찔립니다. "
        "\n\n&9신다리아&r처럼 죽을 때 &9라크리마&r를 떨어뜨립니다."
    ),
    "quest.0741FABE57CA1A7D.title": "&9히포캄투스",
    "quest.13D5F689E6884281.quest_desc": (
        "&e코볼레디에이터&r는 &e저주받은 피라미드&r 안에 있는 두 미니 보스 중 "
        "하나입니다. \n\n플레이어가 가까이 다가올 때까지 잠들어 있으며, 서바이벌 모드의 "
        "플레이어가 접근하면 깨어납니다. 알아내는 데 꽤 오래 걸렸어요. "
        "\n\n540 &4하트&r를 지녔고 채굴 피로를 부여합니다. "
        "\n\n너무 가까이 다가가면 검을 휘두릅니다! 거리를 벌리면 미식축구 공을 들고 "
        "엔드 존으로 달려가듯 돌진합니다! "
        "\n\n죽으면 코볼레톤 뼈, 고대 금속 주괴, 그리고 해골을 떨어뜨립니다!"
    ),
    "quest.17CA9D80D8EC3EF7.quest_desc": (
        "&4&l하빈저&r의 모습과 능력은 동력원인 네더의 별에서 많은 영감을 "
        "받았습니다. \n\n4,680 &4하트&r를 지녔으며 &4고대 공장&r에서 생성된 존재를 "
        "제외하고 눈에 보이는 모든 몹과 플레이어를 공격합니다. "
        "\n\n날아다니며 돌진하기도 합니다. &0위더&r처럼 &l&4하빈저&r는 경로에 "
        "있는 거의 모든 블록을 부숩니다. "
        "\n\n공격할 때는 &4위더 미사일&r을 발사해 &0위더 효과&r를 부여하거나, "
        "등에서 &4위더 곡사포&r를 사방으로 발사합니다. "
        "\n\n그 밖에도 &4레이저&r, &4레이저 개틀링&r, 거대한 &4입 광선&r을 "
        "발사합니다. \n\n다른 생체 기계처럼 &4EMP&r에 매우 약합니다! EMP를 사용하면 "
        "몇 초 동안 기절해 움직이거나 싸우지 못합니다."
    ),
    "quest.1B4ED65C614B102F.quest_desc": (
        "&b이그나이티드 레버넌트&r는 &b&l이그니스&r를 처치하러 가는 길을 "
        "막습니다. \n\n&b레버넌트&r는 블레이즈와 비슷하지만 막대 대신 방패가 몸을 "
        "둘러싸고 있습니다! \n\n방패가 모든 공격을 막으므로 방패를 들어 올릴 때까지 "
        "기다렸다가 공격해야 합니다. \n\n640 &4하트&r를 지녔고 2가지 공격을 "
        "사용합니다. 공중으로 떠올라 블레이즈 막대를 사방에 던지거나, 스핀짓주를 "
        "하듯 방패를 회전시킵니다. \n\n죽으면 &b타오르는 재&r를 떨어뜨립니다."
    ),
    "quest.2011638351B67396.quest_desc": (
        "&9폭풍의 정수&r 2개와 &9라크리마&r 3개로 &9아스트라페&r를 만들 수 "
        "있습니다. \n\n&9아스트라페&r는 &9히포캄투스&r와 &9신다리아&r가 사용하는 "
        "무기를 결합한 것입니다. \n\n삼지창처럼 찌를 수 있지만 피해와 사거리가 더 "
        "큽니다. 우클릭을 길게 누르면 &9신다리아&r처럼 &9번개 창&r을 발사합니다! "
        "\n\n&9번개 창&r은 여전히 벽에 튕기지만, 이제 재사용 대기시간이 있습니다..."
    ),
    "quest.2011638351B67396.title": "&9아스트라페",
    "quest.25ACB08E4F12CE79.quest_desc": (
        "&c네더라이트 미니스트로시티&r는 &4&lL_Ender's Cataclysm&r에서 얻을 "
        "수 있는 반려동물입니다! \n\n먼저 &c네더라이트 형상&r을 제작해야 합니다. "
        "\n\n그다음 &c&l네더라이트 몬스트로시티&r를 처치해 &c용암 동력 전지&r를 "
        "얻습니다. \n\n마지막으로 &c형상&r을 놓고 &c동력 전지&r를 먹이면 길들일 수 "
        "있습니다! \n\n길들인 뒤 Shift+우클릭하면 따라오기, 대기, 돌아다니기 모드를 "
        "바꿀 수 있습니다. \n\n우클릭하면 인벤토리를 엽니다. 레고 파워 마이너의 바위 "
        "괴물처럼 머리 전체를 여는 셈이며, 인벤토리는 15칸입니다. "
        "\n\n960 &4하트&r를 지녔지만 치료하는 방법은 찾지 못했습니다..."
    ),
    "quest.2790EB2E347D28DE.quest_subtitle": (
        "L_Ender's Cataclysm의 모든 보스를 쓰러뜨리세요"
    ),
    "quest.2B115519A21F9CB7.quest_desc": (
        "&d&l엔더 가디언&r은 엔드 석재, &d퍼퍼&r, &5흑요석&r으로 이루어진 "
        "거대한 괴수로, &d공허의 제단&r에서 기다립니다. \n6,660 &4하트&r를 "
        "지녔으며 너무 가까이 다가가면 끌려갈 수 있으니 조심하세요! "
        "\n\n공격과 능력이 아주 많습니다. 가까이 있는 상대는 주먹으로 치거나 내려쳐 "
        "밀어냅니다. \n\n멀리 떨어지면 돌진해 거리를 좁히거나, 발을 굴러 "
        "&d공허의 룬&r을 만들고 &d셜커 탄환&r을 연달아 발사합니다. "
        "\n\n&d공허 태풍&r으로 플레이어를 끌어당기거나 발밑에 소환해 붙잡기도 "
        "합니다. 너무 오래 갇혀 있으면 폭발해 피해를 입습니다. "
        "\n\n&4체력&r이 절반이 되면 가면이 깨져 진짜 머리가 드러납니다! 분노한 가디언은 "
        "투기장 바닥을 부숴 둘 다 아래층으로 떨어뜨립니다. "
        "\n\n이제 더 강하게 끌어당기고 더 많은 &d공허의 룬&r을 보내며, 훨씬 빠르고 "
        "강하게 공격합니다!"
    ),
    "quest.30C5D432C810F904.quest_desc": (
        "&9폭풍의 눈&r은 &9&l스킬라&r와 싸울 수 있는 &9아크로폴리스&r로 " "안내합니다."
    ),
    "quest.30C5D432C810F904.title": "&9폭풍의 눈",
    "quest.33B1D3FD4C0B5514.quest_desc": (
        "&e&l고대의 잔재&r는 자신의 영역인 &e모래&r를 지배합니다. "
        "\n\n2,700 &4하트&r를 지녔으며 &e와제트&r와 &e코볼레디에이터&r의 "
        "도움을 받습니다. \n\n뼈로 된 꼬리를 휘두르거나 물고, 땅을 밟아 충격파를 "
        "일으킵니다. \n\n강하게 포효해 &e모래폭풍&r을 소환하고 머리 위로 "
        "&e모래 함정&r을 떨어뜨리기도 합니다. \n\n돌진할 때는 경로의 모든 블록을 "
        "부수므로 플레이어뿐 아니라 FPS에도 피해를 줍니다. "
        "\n\n약점은 자신을 부활시킨 바로 그 물건입니다! &e목걸이&r를 공격하면 잠시 "
        "쓰러지므로, 그 틈에 공격해 다시 무덤으로 돌려보내세요!"
    ),
    "quest.3459CAEB59CBD60E.quest_desc": (
        "이번에는 누군가 전원 스위치를 켠 모양이네요! \n\n&4배회자&r는 "
        "&4고대 공장&r을 지키는 미니 보스로, 640 &4하트&r를 지녔습니다. "
        "\n\n3가지 공격을 사용합니다. 가까운 적에게는 톱을, 멀리 있는 적에게는 "
        "W.A.S.W.와 비슷한 견착 미사일과 눈에서 나오는 레이저를 사용합니다. "
        "\n\n죽으면 레드스톤과 철을 떨어뜨립니다. \n(참고로 EMP 공격에도 약합니다.)"
    ),
    "quest.35E42F7925CA097A.quest_desc": (
        "&d공허 코어&r는 &d엔더 골렘&r에게서 얻을 수 있습니다! "
        "\n\n무기로 사용할 수 있으며, 우클릭하면 땅에서 &d공허의 룬&r이 솟아납니다. "
        "\n\n&d공허의 룬&r은 소환사 송곳니처럼 사용한 방향으로 약 10블록 동안 "
        "일렬로 나아갑니다. \n\n몹에게 닿을 때마다 약 3 &4하트&r 반의 피해를 주고, "
        "소환사 송곳니와 달리 몹을 밀쳐냅니다. \n\n더 많은 &4&lL_Ender's "
        "Cataclysm&r 무기를 제작하는 데도 사용할 수 있습니다!"
    ),
    "quest.3C0F8EB779E56F2A.quest_desc": (
        "몹 투표에서 원했던 게 집게발이 여기 있네요! \n\n다만 처치해야 할 게가 "
        "훨씬 크고... 훨씬 사납습니다... \n\n키틴 집게발은 클로디언이 떨어뜨립니다. "
        "\n\n착용하면 블록과 개체에 닿는 거리가 늘어나, 더 멀리 블록을 설치하고 "
        "몹을 공격할 수 있습니다!"
    ),
    "quest.3C0F8EB779E56F2A.title": "&9키틴 클로",
    "quest.45FBEABEBA7CC09E.quest_desc": (
        "무슨 일이 있어 &5도시&r가 &9물&r 아래로 가라앉았는지는 알 수 없지만, "
        "&9물&r 위로 솟은 석재 벽돌 덕분에 쉽게 찾을 수 있습니다. "
        "\n\n처음 만나는 가장 큰 방은 거대한 돔 형태의 도심이며, 여기에 "
        "&5심연의 제단&r이 있습니다. \n\n방에서 이어진 복도는 &5도시&r의 다른 "
        "건물로 연결됩니다. &5코랄서스&r가 갇힌 감옥과 귀중한 전리품이 가득한 "
        "보물 방도 있습니다! \n\n&5도시&r 곳곳에는 주민인 &5심연꾼&r이 살고 "
        "있습니다. "
    ),
    "quest.465B08461B460DAC.quest_desc": (
        "&d엔더마프테라&r는 &d폐허가 된 성채&r 주변에 삽니다. "
        "\n\n8 &4하트&r를 지녔고 물어뜯는 기본 공격만 사용합니다. "
        "\n\n너무 많이 물어뜯으면 턱이 부러지며, 그러면 죽어도 턱을 떨어뜨리지 "
        "않습니다. \n\n&d공허의 턱&r을 원한다면 빠르게 처치하세요!"
    ),
    "quest.4D644A9829C240CB.quest_desc": (
        "&b&l이그니스&r의 방패가 마음에 드나요? &b이그니티움&r으로 방패 1개를 직접 만들 수 "
        "있습니다. \n\n&b불꽃의 보루&r는 일반 방패처럼 사용할 수 있으며 특별한 효과도 "
        "있습니다. \n\nShift와 우클릭을 길게 누른 뒤 놓으면 염소처럼 정면으로 "
        "돌진합니다. \n\n부딪힌 대상은 피해를 받고, 벽에 끼이면 기절합니다. "
        "\n\n하나쯤 갖고 다니면 정말 유용합니다!"
    ),
    "quest.4D822D92492E1F53.quest_desc": (
        "&3아프트강그&r는 &3서리 감옥&r 안의 미니 보스입니다. "
        "\n\n480 &4하트&r를 지녔으며 거대한 도끼로 공격합니다. "
        "\n\n도끼를 휘두르거나 주변 땅을 내려칩니다. 땅을 내려치면 레이저가 "
        "생겨 경로에 있는 모두에게 피해를 줍니다. &e코볼레디에이터&r와 비슷한 "
        "돌진 공격도 사용합니다! \n\n죽으면 검은 강철 주괴와 조각, 썩은 살점과 "
        "뼈를 떨어뜨립니다."
    ),
    "quest.4FA156C383C9C438.quest_desc": (
        "&e코볼레톤&r은 &e&l고대의 잔재&r를 섬기는 작은 공룡 해골입니다. "
        "\n\n12 &4하트&r 반을 지녔으며 코피스로 공격합니다. "
        "\n\n죽으면 무기와 뼈, 고대 금속 조각을 떨어뜨릴 수 있습니다."
    ),
    "quest.4FA7774D89171BB3.quest_desc": (
        "&4&lL_Ender's Cataclysm&r의 반려동물을 하나 더 원하나요? 그렇다면 "
        "잔재의 해골이 필요합니다! \n\n&e고대의 잔재&r가 확정적으로 떨어뜨리며, "
        "사용하면 현대의 잔재가 생성됩니다. \n\n&e고대&r 개체보다 훨씬 작고 "
        "온순합니다. 스니퍼 알을 먹여 길들이면 늑대처럼 행동합니다. "
        "\n\n플레이어를 공격한 대상이나 플레이어가 공격한 대상을 공격합니다. 따라오기, "
        "돌아다니기, 대기의 3가지 모드도 있습니다. 따라오기는 말 그대로 플레이어를 "
        "따라오고, 돌아다니기는 일정 범위를 돌아다니며, 대기는 한곳에 눕게 합니다. "
        "\n\n1500 &4하트&r를 지녔으며 &e코볼레톤 뼈&r를 먹이면 회복합니다! "
        "\n\n새 공룡 친구와 즐거운 시간 보내세요!"
    ),
    "quest.53154550397E9704.quest_desc": (
        "&c&l네더라이트 몬스트로시티&r는 이름 그대로 &c네더라이트&f와 "
        "&c용암&r으로 이루어진 괴수입니다. \n\n최대 9,600 &4하트&r를 지닐 수 "
        "있지만 처음 만났을 때는 약 1,100 &4하트&r뿐이었습니다. 근처에 플레이어가 "
        "없으면 &4체력&r을 회복합니다.\n\n거대한 팔로 내리치거나 땅을 강타하는 "
        "근접 공격을 사용합니다. 블록을 공중으로 던져 충격파를 일으키기도 합니다. "
        "\n\n멀어지면 돌진하거나 뛰어듭니다. 100톤은 되어 보이니 어느 쪽도 맞고 "
        "싶지는 않네요! \n\n가장 위험한 것은 원거리 공격입니다. &c마그마 탄&r을 "
        "발사하며, 탄이 떨어진 곳에는 &c용암&r이 생깁니다. 손에서 &c화염구&r를 "
        "발사해 땅에서 &c화염 기둥&r이 솟게 하기도 합니다."
    ),
    "quest.55278DDC31951DA5.quest_desc": (
        "&3드라우그&r는 &3저주받은 묘비&r를 지키고 싶어서 아예 잠가 둔 모양입니다! "
        "\n\n&3봉인의 문&r이라는 아주 창의적인 이름의 문이 길을 막고 있으므로 "
        "&3기이한 열쇠&r가 필요합니다. \n\n정말 철저하게 잠그고 싶었는지 &3기이한 열쇠&r는 "
        "&3아프트강그&r에게 맡겼습니다. &3서리 감옥&r에서 아직 살아 있는 가장 "
        "강한 자에게요!"
    ),
    "quest.55278DDC31951DA5.quest_subtitle": "말레딕투스로 가는 길 열기",
    "quest.55278DDC31951DA5.title": "&3기이한 열쇠",
    "quest.573DD5834B321D0A.quest_desc": (
        "&9아크로폴리스&r는 광활한 &9바다&r 위 구름 속에 떠 있는 거대한 도시입니다. "
        "(그런데도 처음에는 못 봤네요.) \n\n&9청해석&r, &3프리즈마린&r, 그리고 "
        "&9물&r로 이루어져 있습니다! 정말 많고 많은 &9물&r이 있습니다! "
        "\n\n그리스 건축 양식을 바탕으로 여러 층과 정원, 투기장까지 갖추고 있습니다. "
        "\n\n곳곳에 &9옥토호스트&r, &9어친킨&r, &9신다리아&r, &9히포캄투스&r, "
        "&9클로디언&r이 생성됩니다! 운 나쁜 &9바다&r 몹도 조금 있고요. "
        "\n\n건축물 곳곳에는 상자와 다이아몬드 블록, 스펀지 같은 희귀 블록이 "
        "숨겨져 있습니다!"
    ),
    "quest.573DD5834B321D0A.title": "&9아크로폴리스&f: &9&l스킬라의 거처",
    "quest.5BD22081ED81BCC6.quest_desc": (
        "&9어친킨&r은 어째서인지 &9아크로폴리스&r에 사는 작은 골칫거리입니다. "
        "\n\n6 &4하트&r를 지녔고 방어력은 없어 다행히 꽤 약합니다. "
        "\n\n가까이 있으면 때리고, 거리가 있으면 굴러서 돌진합니다. 구르는 동안 "
        "수많은 &9가시&r를 발사해 맞은 대상에게 피해를 줍니다! "
        "\n\n죽어도 고유 아이템은 떨어뜨리지 않습니다. 대신 마지막까지 피해를 주는 "
        "&9가시&r를 더 남깁니다. 그게 전부입니다."
    ),
    "quest.5BD22081ED81BCC6.title": "&9어친킨",
    "quest.5D74D73092ACD2F2.quest_desc": (
        "&5코랄 골렘&r은 &5가라앉은 도시&r 안에서 생성되며, &5&l레비아탄&r을 "
        "쓰러뜨린 뒤에는 바다에서도 생성됩니다. \n\n더 큰 친척인 &5코랄서스&r와 "
        "비슷하지만 체력은 110 &4하트&r로 더 적고 &5심연꾼&r이 탈 수 없습니다. "
        "\n\n대신 공격 종류는 더 많습니다! 뛰어들거나 주변 땅을 내려치고, 직접 "
        "후려치기도 합니다. \n\n죽으면 결정화된 산호 파편을 떨어뜨리며, 파편으로 "
        "결정화된 산호를 만들 수 있습니다. 이것들은 &5심연의 제물&r을 만드는 데 "
        "사용됩니다."
    ),
    "quest.5EDB5A2D744CE415.quest_desc": (
        "&4레이저 개틀링&r은 &4위더라이트&r로 만들 수 있는 무기입니다. "
        "\n\n인벤토리의 레드스톤을 소모해 불을 붙이고 3 &4하트&r 반의 피해를 주는 "
        "레이저를 발사합니다. \n\n레드스톤 1개당 레이저 50발을 쏘니 꽤 좋은 "
        "거래라고 생각합니다."
    ),
    "quest.5FBA199E0B7F1585.quest_desc": (
        "&9옥토호스트&r는 사실 몹 2마리가 협력하는 존재입니다! 플레이어를 죽이기 "
        "위해서요! \n\n&9심비옥토&r가 &9익사한 숙주&r를 조종합니다. "
        "\n\n&9심비옥토&r는 8 &4하트&r를 지녔고 방어력은 없습니다. 혼자일 때는 "
        "&0먹물&r만 발사하며, 죽으면 &0먹물 주머니&r를 떨어뜨립니다. "
        "\n\n&9익사한 숙주&r는 일반 &9드라운드&r처럼 행동합니다. 10 &4하트&r와 "
        "방어력 2를 지녔으며, 갑옷과 무기를 들고 생성되어 이를 사용할 수 있습니다. "
        "\n\n&9옥토호스트&r로 합쳐지면 동시에 공격합니다. &9심비옥토&r는 &0먹물&r을 쏘고, "
        "&9익사한 숙주&r는 무기나 주먹으로 공격합니다."
    ),
    "quest.5FBA199E0B7F1585.title": "&9옥토호스트",
    "quest.62DF58D36B739EA0.quest_desc": (
        "&e와제트&r는 &e코볼레디에이터&r처럼 &e저주받은 피라미드&r 안에서 "
        "플레이어가 다가오기를 기다립니다. \n\n&e와제트&r는 450 &4하트&r를 지녔고 "
        "다행히 채굴 피로는 부여하지 않습니다! \n가까이 있으면 무기를 휘두르고, "
        "멀어지면 모래폭풍을 던지거나 천장에서 모래 블록을 머리 위로 떨어뜨립니다. "
        "\n\n솔직히 어느 공격이 더 나쁜지 모르겠네요! \n\n죽으면 고대 금속 주괴만 "
        "떨어뜨립니다."
    ),
    "quest.631796E7615C04FA.quest_desc": (
        "&2자수정 게&r는 아홀로틀과 함께 무성한 동굴에 삽니다. "
        "\n\n1200 &4하트&r를 지녔으며 처음에는 중립적입니다. 먼저 공격하지는 "
        "않지만 공격받으면 반격합니다. \n\n집게발로 후려치거나 자수정을 던지고, "
        "땅속으로 파고듭니다. \n\n죽으면 고기와 껍데기를 떨어뜨립니다. 고기는 자수정 "
        "제단에서 축복해 강화할 수 있습니다. 껍데기를 조합하면 네더라이트 흉갑과 "
        "비슷한 능력치와 &2게&r의 능력을 지닌 블룸 스톤 견갑을 만들 수 있습니다."
    ),
    "quest.655FF7295B688354.quest_desc": (
        "&9클로디언&r은 &9아크로폴리스&r의 미니 보스입니다. "
        "\n\n자기 몸보다도 큰 도끼를 든 거대한 바닷가재입니다! "
        "\n\n225 &4하트&r와 방어력 12를 지녔습니다. "
        "\n\n도끼와 발로 공격합니다. 도끼를 휘둘러 중간 정도의 피해를 주고, "
        "땅을 내려쳐 충격파를 일으킵니다. 발로 땅을 구르면 더 큰 충격파와 "
        "&9파도&r가 밀려옵니다! \n\n너무 멀어지면 경로의 블록을 부수며 "
        "돌진합니다! \n\n처치하면 &9집게발&r을 떨어뜨립니다. 조금 잔인해 보이지만 "
        "다행히 판타지 속 폭력일 뿐입니다!"
    ),
    "quest.655FF7295B688354.title": "&9클로디언",
    "quest.683C260C854C5AA3.quest_desc": (
        "&4기계식 융합 모루&r는 &4&lL_Ender's Cataclysm&r 아이템을 조합할 때 "
        "필요합니다. \n\n일반 모루처럼 놓을 수 있지만, 다행히 내구도가 없습니다! "
        "\n\n조합법은 JEI에서 확인하세요. 왼쪽 칸에 아이템 1개, 가운데 칸에 다른 "
        "아이템을 넣으면 오른쪽 칸에서 결과물을 얻습니다."
    ),
    "quest.696A33E7D91A487E.quest_desc": (
        "&9신다리아&r는 &9아크로폴리스&r를 지키는 해파리와 인간이 합쳐진 듯한 "
        "몹입니다. 녹색과 보라색을 띠며 반투명합니다. \n\n60 &4하트&r를 지녔고 "
        "방어력은 없습니다. \n\n우산처럼 보이지만 실제로는 치명적인 무기를 듭니다! "
        "\n\n가까이 있으면 무기를 휘두르고, 멀리 있으면 &9번개 창&r을 발사합니다. "
        "\n\n&9번개 창&r은 벽에 튕기지만, 다행히 &9아크로폴리스&r에는 벽이 많지 "
        "않습니다! \n\n죽으면 &9신다리아&r는 &9라크리마&r를 떨어뜨립니다."
    ),
    "quest.696A33E7D91A487E.title": "&9신다리아",
    "quest.6B5BC33667C782EC.quest_desc": (
        "&d엔더 골렘&r 여러 마리가 &d폐허가 된 성채&r를 지킵니다. "
        "\n\n&d엔더 가디언&r과 싸우기 위해 꼭 처치할 필요는 없지만, &d공허 코어&r를 "
        "얻으려면 처치하는 편이 좋습니다. \n\n&d엔더 골렘&r은 3000 &4하트&r를 "
        "지녔으며 내버려 두면 회복합니다. \n\n주먹으로 치거나 땅을 내려칩니다. "
        "땅을 내려치면 &d공허의 룬&r이 생성되어 닿는 플레이어나 몹에게 피해를 "
        "줍니다."
    ),
    "quest.6CB8D3919B16784B.quest_desc": (
        "&9케라우노스&r는 &9&l스킬라&r가 직접 사용하는 닻 무기입니다! "
        "\n\n&9폭풍의 정수&r 2개와 &9라크리마&r 3개로 만들 수 있습니다. "
        "&9아스트라페&r와 재료 배치 순서만 다릅니다. \n\n철퇴처럼 닻을 휘두를 "
        "수 있지만 공격 간격이 매우 깁니다. 대신 특수 공격도 사용할 수 있습니다! "
        "\n\n우클릭을 길게 눌러 정면으로 닻을 던집니다. 몹에게 맞으면 피해를 주고 "
        "밀쳐냅니다. \n\nShift+우클릭을 길게 누르면 닻 대신 정면에 &9파도&r 여러 "
        "개를 펼쳐 보냅니다!"
    ),
    "quest.6CB8D3919B16784B.title": "&9케라우노스",
    "quest.71055E7BBB337C4D.quest_desc": (
        "&3저주받은 묘비&r를 우클릭하면 &3&l말레딕투스&r를 발할라나 북유럽의 "
        "지옥에 해당하는 곳에서 불러올 수 있습니다. \n\n8,400 &4하트&r와 거대한 "
        "날개를 지녔습니다.\n\n&3섬멸자&r 2개를 휘두르며, 땅을 내리쳐 "
        "충격파를 일으키기도 합니다! \n\n날개 덕분에 민첩하게 움직이며 다양한 공격을 "
        "사용합니다. 경로의 모든 블록을 부수며 돌진하거나 공격을 피하기도 합니다! "
        "\n\n공중으로 날아오른 뒤 &3저주받은 활&r을 쏘거나 &3영혼 분쇄자&r를 들고 "
        "내려찍습니다. &3저주받은 활&r은 화살 4발을 발사하고, &3영혼 분쇄자&r는 "
        "&3망령 도끼창&r의 비를 내립니다."
    ),
    "quest.713006AB89E43C6D.quest_desc": (
        "거대한 &9아크로폴리스&r 꼭대기에 &9&l스킬라&r가 생성됩니다. "
        "&d&l엔더 가디언&r처럼 가까이 다가가기만 하면 나타납니다. "
        "\n\n&4&lL_Ender's Cataclysm&r에서 가장 작은 보스 중 하나로, 키는 약 "
        "3블록입니다. 현재 390 &4하트&r와 방어력 12를 지녔지만 곧 강화될 "
        "예정입니다! \n\n작은 몸집이나 &6&lATM10&r 강화 효과가 없다는 이유로 얕보지 "
        "마세요. 이곳의 보스 중에서도 손꼽히게 다양한 공격을 사용합니다. "
        "\n\n자신의 &9닻&r인 &9케라우노스&r로 멀리 있는 플레이어를 끌어당기거나, "
        "직접 휘둘러 큰 피해를 줍니다! \n\n등이나 구름에서 &9번개 창&r을 던지고, "
        "공중으로 뛰어올랐다가 내려찍어 착지 지점 주변에 &9낙뢰&r를 일으킵니다. "
        "\n\n그게 전부가 아닙니다! &9물&r을 다뤄 &9파도&r를 보내거나 "
        "&9물뱀&r을 소환해 물게 합니다! \n\n쓰러뜨리면 일반적인 보스 장비와 함께 "
        "&9라크리마&r와 &9폭풍의 정수&r를 떨어뜨립니다."
    ),
    "quest.713006AB89E43C6D.title": "&9&l스킬라",
    "quest.746DE905D45A396C.quest_desc": (
        "&5&l레비아탄&r은 사람들이 바다를 두려워하는 이유입니다. "
        "\n\n6,400 &4하트&r와 날카로운 이빨, 강한 촉수를 지녔으며 &9물&r 밖에서는 "
        "무적입니다. \n\n수중 &5기뢰&r를 소환하고 고질라 같은 &5원자 광선&r을 "
        "발사하며, 직접 물어뜯기도 합니다. \n\n가장 위험한 것은 &5소용돌이&r입니다! "
        "&6&lATM 개발자&r를 말하는 건 아니고요! \n\n촉수로 &5물 소용돌이&r를 "
        "열어 주변 개체를 미끼처럼 빨아들입니다. 해저의 &5소용돌이&r에서 위쪽으로 "
        "발사되는 &5레이저&r도 소환합니다. \n\n&4체력&r이 절반 아래로 떨어지면 격노합니다! "
        "격노한 뒤에는 &5레이저&r을 훨씬 자주 사용하고, 바다에 자신만 남을 때까지 "
        "쉴 새 없이 공격합니다."
    ),
    "quest.7CBEBBCB9D95D11A.quest_desc": (
        "&5심연의 알&r도 &5&l레비아탄&r이 떨어뜨립니다. 아무래도 임신한 개체를 "
        "처치한 모양이네요. \n\n&5알&r을 놓고 잠시 기다리면 아기 &5레비아탄&r이 "
        "태어납니다. \n\n부화한 뒤 열대어를 아주 많이 먹이면 길들일 수 있습니다. "
        "\n\n&5아기&r는 1200 &4하트&r를 지녔고 열대어를 먹여 회복할 수 "
        "있습니다. \n\n길들인 뒤에는 &e현대의 잔재&r처럼 Shift+우클릭으로 따라오기, "
        "대기, 돌아다니기 모드를 설정할 수 있습니다."
    ),
    "quest.7D57A14810BC0CBE.quest_desc": (
        "&b화염의 제단&r에 &b타오르는 재&r를 사용하면 &b&l이그니스&r가 "
        "나타납니다. \n7,200 &4하트&r와 거대한 &b검&f과 &b방패&r를 지녔습니다. "
        "\n\n&b방패&r는 플레이어의 공격을 막고, &b검&r으로 베거나 찌릅니다. "
        "검에 찔리면 움직일 수 없고 공격만 할 수 있습니다. \n\n도약한 뒤 &b방패&r로 "
        "땅을 내려쳐 블록과 플레이어를 공중으로 띄우는 충격파를 일으킵니다. "
        "도약하지 않고 &b검&r으로도 비슷한 공격을 할 수 있습니다. "
        "\n\n&b화염구&r 3개를 공중에 던진 뒤 플레이어를 향해 날립니다! 가스트의 "
        "화염구처럼 되받아치세요. \n\n&4체력&r을 약 7,500 &4하트&r까지 깎으면 "
        "&b밝은 파란색&r으로 변합니다. 이제 더 빠르고 강하게 공격하며 생명력을 "
        "흡수합니다. \n\n&b화염구&r도 더는 반사할 수 없고 여러 종류의 &b충격파&r를 "
        "사용합니다!"
    ),
    "task.01063DC98BCE5A91.title": "대격변의 여행자",
    "quest.2A444F4CCC72545D.quest_desc": (
        "&4&lL_Ender's Cataclysm&r에서 &6&lATM 별&r에 필요한 아이템 중 가장 "
        "얻기 쉬운 것은 &5심연의 제물&r입니다. \n\n가장 기본적인 재료는 주괴 "
        "블록과 자수정으로, 모두 &2&l바닐라&r 아이템입니다. \n\n그다음 앵무조개 "
        "껍데기와 바다의 심장이 필요합니다. 희귀한 &2&l바닐라&r 아이템이지만 "
        "&5심연꾼&r을 처치하면 얻을 수 있습니다! \n\n&5심연꾼 워록&f과 &5사제&r가 "
        "사용하며 죽을 때 떨어뜨리는 의식용 단검도 필요합니다. \n마지막 재료는 "
        "결정화된 산호와 산호 덩어리 중에서 고를 수 있습니다. 둘 다 &5코랄 골렘&r과 "
        "&5코랄서스&r가 떨어뜨립니다."
    ),
    "quest.2A444F4CCC72545D.title": "&5심연의 제물",
    "quest.4BD203AD481DDE8F.quest_desc": (
        "&4미트 슈레더&r는 &4&l하빈저&r가 떨어뜨리는 &4위더라이트&r로 "
        "만듭니다. \n\n먼저 &2&l오버월드&r 지하 깊은 곳의 &4고대 공장&r을 "
        "찾아야 합니다. \n\n그 안에서 동력이 꺼진 &4&l하빈저&r를 찾고 네더의 별을 "
        "넣어 가동하세요! \n\n어렵고 긴 보스전을 마치면 &4미트 슈레더&r를 제작할 "
        "수 있습니다!"
    ),
    "quest.4BD203AD481DDE8F.title": "&4미트 슈레더",
    "quest.5B2FD54E425D5C9D.quest_desc": (
        "이 아이템은 얻기 어렵습니다. &d공허 &c용광로&r의 모든 재료를 얻으려면 "
        "보스 2명과 미니 보스를 처치해야 합니다. \n\n먼저 &4기계식 융합 "
        "모루&r가 필요합니다. &2&l오버월드&r 지하의 &4고대 공장&r을 찾으세요. "
        "\n\n&4&l하빈저&r에게 네더의 별을 넣어 가동한 뒤 처치하세요! "
        "&4&l하빈저&r가 떨어뜨리는 &4위더라이트&r로 &4기계식 융합 모루&r를 "
        "만들 수 있습니다. \n\n다음은 &c인퍼널 포지&r입니다. &c&l네더라이트 "
        "몬스트로시티&r가 떨어뜨립니다. \n\n&c&l네더&r에서 &c영혼 대장간&r "
        "구조물을 찾고 &c&l네더라이트 몬스트로시티&r를 처치해 &c인퍼널 포지&r를 "
        "얻으세요! \n\n마지막이자 아마 가장 쉬운 재료는 &d공허 코어&r입니다. 보스가 "
        "아니라 미니 보스가 떨어뜨리니 다행이네요! \n\n&5&l엔드&r에서 &d폐허가 된 "
        "성채&r를 찾으면 그 안의 &d엔더 골렘&r에게서 &d공허 코어&r를 얻을 수 "
        "있습니다. \n\n모든 재료를 모은 뒤 &4기계식 융합 모루&r에서 &c인퍼널 "
        "포지&r와 &d공허 코어&r를 결합해 &d공허 &c용광로&r를 만드세요."
    ),
    "quest.5B2FD54E425D5C9D.title": "&d공허 &c용광로",
}

QUEST_QUALITY_OVERRIDES: dict[str, str] = {
    "quest.00307A898A639191.quest_desc": (
        "이 퀘스트는 &6AllTheMods 스태프&r 또는 AllTheMods 모드팩을 위한 "
        "&2커뮤니티 기여자&r가 작성했습니다.\n\n모든 &6AllTheMods&r 팩은 "
        "&eAll Rights Reserved&r 라이선스를 따릅니다. 따라서 &6AllTheMods 팀&r이 "
        "출시하지 않은 공개 팩에서는 명시적인 허가 없이 이 퀘스트를 사용할 수 "
        "없습니다.\n\n이 퀘스트는 의도적으로 숨겨져 있습니다. 이 문구가 보인다면 편집 "
        "모드입니다."
    ),
    "quest.0496E8E786262464.title": "&2오버월드&r: 보스 &m3 4&r 5명의 영역",
    "quest.05DE9E1CDFBC22DE.quest_desc": (
        "&d공허의 갈래 화살&r은 분광 화살과 &d공허의 턱&r으로 제작합니다. "
        "\n\n모든 활이나 쇠뇌로 발사할 수 있으며, 몹이나 블록에 맞으면 산산이 "
        "부서집니다. \n\n부서진 파편들이 주변으로 흩어져 맞은 대상에게 피해를 줍니다!"
    ),
    "quest.0853917693A259C2.quest_desc": (
        "&3섬멸자&r는 &3커스뮴&r과 검은 강철로 만든 아주 재미있는 무기입니다. "
        "\n\n하루 종일 적을 후려칠 수 있죠! 하지만 &3섬멸자&r 하나보다 더 재미있는 "
        "것이 무엇인지 아나요? \n\n&3섬멸자&r 두 개입니다! \n\n양손에 &3섬멸자&r를 하나씩 들고 "
        "우클릭을 길게 누르면 강력하게 땅을 내려쳐 주변 모두에게 피해를 줍니다!"
    ),
    "quest.0853917693A259C2.title": "&3섬멸자",
    "quest.0894EB1F3FCFCECA.quest_desc": (
        "&3드라우그&r는 &5심연꾼&r처럼 계급이 있습니다. &3드라우그&r, "
        "&3왕실 드라우그&r, &3엘리트 드라우그&r 순입니다. \n\n일반 "
        "&3드라우그&r는 14 &4하트&r를 지녔고 검은 강철 검과 도끼를 듭니다. "
        "썩은 살점과 뼈, 드물게 검은 강철 조각을 떨어뜨립니다. \n\n&3왕실 "
        "드라우그&r는 15 &4하트&r를 지녔고 검과 도끼 외에 검은 강철 타지 방패도 "
        "듭니다. 일반 &3드라우그&r와 같은 아이템을 떨어뜨립니다. \n\n마지막 "
        "&3엘리트 드라우그&r는 거리에 따라 검은 강철 검과 쇠뇌를 바꿔 듭니다. "
        "16 &4하트&r를 지녔으며, 물론 일반 &3드라우그&r와 전리품은 같습니다!"
    ),
    "quest.0B7F2B63D867D221.quest_desc": (
        "이것을 찾으려면 약간의 고고학이 필요합니다! \n\n&e&l고대의 잔재&r에게 "
        "내려가는 거대한 수직 통로 옆에는 방 3개가 있습니다. \n\n그중 방 2개에는 "
        "솔로 털어 전리품을 얻을 수 있는 수상한 모래가 있으며, &e사막의 목걸이&r도 "
        "나옵니다. \n그런 다음 &e사막의 목걸이&r를 들고 &e&l고대의 잔재&r를 "
        "우클릭해 부활시키세요!"
    ),
    "quest.0EE0946240B41A00.quest_desc": (
        "&b이그니티움&r은 네더라이트 장비의 업그레이드 재료입니다. 제작하는 "
        "&b이그니티움 업그레이드&r와 &b&l이그니스&r가 떨어뜨리는 "
        "&b이그니티움 주괴&r가 필요합니다. \n\n&b이그니티움 투구&r를 쓰면 용암 "
        "속을 선명하게 볼 수 있습니다. \n\n&b이그니티움 흉갑&r은 겉날개와 결합할 "
        "수 있습니다. \n\n&b이그니티움 레깅스&r는 화염 면역을 주지는 않지만 몸에 "
        "붙은 불을 더 빨리 꺼 줍니다. \n&b이그니티움 부츠&r를 신으면 용암 위를 "
        "걸을 수 있습니다. 가죽 부츠로 가루눈에 들어가듯 Shift를 길게 눌러 용암 "
        "아래로 내려갈 수 있습니다."
    ),
    "quest.0F8F0F7880235BA2.quest_desc": (
        "&c영혼 대장간&r은 네더&r에 있습니다. 보루 잔해로 착각하고 지나치지 "
        "마세요. 훨씬 위험합니다. \n\n여기에서 금, 흑암, 네더라이트를 찾을 수 "
        "있습니다. \n\n이곳에 생성되는 적대적인 몹은 보스인 &c&l네더라이트 "
        "몬스트로시티&r뿐입니다!"
    ),
    "quest.0F8F0F7880235BA2.title": (
        "&c영혼 대장간&f: &c&l네더라이트 몬스트로시티&r의 거처"
    ),
    "quest.1744E700CF742CE2.quest_desc": (
        "&5코랄서스&r는 &5가라앉은 도시&r의 경비병이자 탈것입니다. "
        "\n\n&5심연꾼&r이 타고 빠르게 이동하며 함께 공격할 수 있습니다! "
        "\n\n160 &4하트&r를 지녔고 때리거나 던지는 기본 공격을 사용합니다. "
        "\n\n죽으면 &5심연의 제물&r 제작에 쓰이는 산호 덩어리를 떨어뜨립니다."
    ),
    "quest.18EB86F91CBBCCC6.quest_desc": (
        "L_Ender's Cataclysm의 모든 던전이 &e저주받은 피라미드&r처럼 찾기 쉬운 "
        "것은 아닙니다. \n\n그럴 때는 전용 눈이 도움이 됩니다! \n\n각 눈은 정해진 "
        "구조물로 안내하며, 걱정하지 않아도 될 만큼 거의 깨지지 않습니다."
    ),
    "quest.1A8F438DB8508276.quest_desc": (
        "&3서리 감옥&r은 눈 덮인 산 위와 내부에 걸쳐 있는 거대한 성채입니다. "
        "\n\n안에는 수십 개의 감방과 무기고, &3저주받은 묘비&r가 놓인 큰 방이 "
        "있습니다. \n\n검은 강철을 비롯한 전리품이 든 상자와 가져갈 수 있는 장식된 "
        "도자기가 곳곳에 있습니다! \n\n물론 길을 막는 적인 &3드라우그&r와 "
        "&3아프트강그&r도 있습니다."
    ),
    "quest.1A8F438DB8508276.title": ("&3서리 감옥&r: &3&l말레딕투스의 거처"),
    "quest.1C5EA7D62BAF2108.quest_desc": (
        "&5&l레비아탄&r과 싸우려면 제물, 정확히는 &5심연의 제물&r이 필요합니다. "
        "\n\n가장 기본적인 재료는 주괴 블록과 자수정으로, 모두 &2&l바닐라&r "
        "아이템입니다. \n\n다음으로 앵무조개 껍데기와 바다의 심장이 필요합니다. "
        "희귀한 &2&l바닐라&r 아이템이지만 &5심연꾼&r을 처치하면 얻을 수 "
        "있습니다! \n\n&5심연꾼 워록&f과 &5사제&r가 사용하는 의식용 단검도 "
        "필요하며, 둘을 처치하면 얻을 수 있습니다. \n마지막 재료는 결정화된 산호와 "
        "산호 덩어리 중에서 고를 수 있습니다. 둘 다 &5코랄 골렘&r과 "
        "&5코랄서스&r가 떨어뜨립니다."
    ),
    "quest.21A0FD474FBB49F7.quest_desc": (
        "&5엔드&r의 황량함을 채우는 또 다른 구조물은 &d폐허가 된 성채&r입니다. "
        "\n\n&d폐허가 된 성채&r는 &5흑요석&r, 엔드 석재, &d퍼퍼&r로 이루어진 "
        "궁전입니다. \n\n궁전에는 상자, 셜커 상자, 셜커, 그리고 고유 블록인 "
        "&d공허석&r이 있습니다! \n\n앞서 말한 셜커와 &d엔더마프테라&r, "
        "&d엔더 골렘&r을 조심하세요."
    ),
    "quest.21A0FD474FBB49F7.title": ("&d폐허가 된 성채&r: &d&l엔더 가디언&r의 거처"),
    "quest.236EA8D18ECD5FE8.quest_desc": (
        "생성 방식이 꽤 독특합니다! &b&l이그니스&r를 처치하면 네더 요새에 "
        "&b이그나이티드 버서커&r가 생성될 수 있습니다. \n\n&b레버넌트&r와 "
        "비슷하지만 방패 대신 검을 듭니다! 검은 방패처럼 피해를 막지 못하는 대신 "
        "더 큰 피해를 줍니다. \n\n체력은 65 &4하트&r로 훨씬 낮으며, 죽을 때 "
        "꺼져 가는 불씨를 떨어뜨립니다. 꺼져 가는 불씨 4개로 &b타오르는 재&r "
        "1개를 만들 수 있습니다."
    ),
    "quest.291C76140DE97E3C.quest_desc": (
        "&b이그니티움&r은 네더라이트와 비슷하지만 얻으려면 실력이 필요합니다. "
        "\n\n&b&l이그니스&r는 1개만 떨어뜨리므로 신중히 사용하세요! "
        "\n\n네더라이트 갑옷을 업그레이드하거나 무기를 만드는 데 사용할 수 있습니다."
    ),
    "quest.291C76140DE97E3C.title": "&b이그니티움 주괴",
    "quest.2A196974431FCC42.quest_desc": (
        "&c지옥불 용광로&r는 &c&l네더라이트 몬스트로시티&r가 떨어뜨립니다. "
        "엄밀히 말하면 무기가 아니라 곡괭이입니다! \n네더라이트 등급까지 채굴할 수 "
        "있어 올더모듐 광석도 캘 수 있습니다. \n\n우클릭하면 땅을 내리쳐 주변 "
        "모두를 공격합니다. \n\n(검과 곡괭이용 마법 부여를 모두 적용할 수 있습니다!)"
    ),
    "quest.2BCB788924BBD849.quest_desc": (
        "제가 가장 좋아하면서도 가장 강력한 무기 중 하나입니다. \n\n&b소각자&r는 "
        "일반 검처럼 사용하고 마법을 부여할 수 있습니다! \n하지만 우클릭을 길게 누른 "
        "뒤 몇 초 후 놓으면 바라보는 방향의 땅에서 거대한 불길이 솟아올라 "
        "폭발합니다. \n\n크기도 거대해 멋질 뿐 아니라 공격 범위도 더 넓습니다!"
    ),
    "quest.2CD58FC229BC0C28.quest_desc": (
        "&d수호의 건틀릿&r은 &d&l엔더 가디언&r이 떨어뜨립니다. \n\n어느 손에 "
        "들든 우클릭을 길게 누르면 주변의 모든 몹을 끌어당깁니다! \n\n주로 "
        "사용하는 손에 들고 몹을 때려 피해를 줄 수도 있습니다. \n\n비행 중인 몹을 "
        "끌어당겨 떨어뜨려 보세요!"
    ),
    "quest.2CD58FC229BC0C28.title": "&d수호의 건틀릿",
    "quest.2F62C290A5CE50F8.quest_desc": (
        "잠깐, &e고대 금속&r 몇 개만으로 네더라이트 검보다 피해가 크고 사거리가 "
        "엄청나며 &e모래폭풍&r까지 날리는 무기를 얻는다고요!? \n\n네, 바로 "
        "&e고대의 창&r입니다!"
    ),
    "quest.37E4DECFB6526969.quest_desc": (
        "&3영혼 분쇄자&r는 &3커스뮴&r과 검은 강철로 제작합니다. \n\n대부분의 "
        "&4&lL_Ender's Cataclysm&r 무기처럼 거대해 사거리와 피해가 크지만, 특수 "
        "효과는 훨씬 뛰어납니다! \n\n우클릭하면 &3영혼 분쇄자&r를 들고 앞으로 "
        "돌진하며, 지나간 자리에 하늘에서 &3망령 도끼창&r이 떨어집니다! "
        "Shift+우클릭하면 주변에 &3망령 도끼창&r을 소환합니다."
    ),
    "quest.392EAE8BE71510C1.quest_desc": (
        "황량한 &5엔드&r에 주민 1명이 더 생겼습니다. \n\n다른 하나는 물론 "
        "&d엔더 드래곤&r입니다!"
    ),
    "quest.45FBEABEBA7CC09E.title": ("&5가라앉은 도시&r: &5&l레비아탄&r의 거처"),
    "quest.462D173D576A8D91.quest_desc": (
        "&e고대 금속&r은 &e저주받은 피라미드&r 안의 거의 모든 적이 떨어뜨립니다! "
        "\n\n다른 주괴처럼 조각이나 블록으로 합치고 다시 나눌 수 있습니다. "
        "\n\n&e본 렙타일 갑옷&r이나 &e고대의 창&r을 만드는 데 사용합니다."
    ),
    "quest.4CCEC13CC5A5772D.quest_desc": (
        "&4&lL_Ender's Cataclysm&r에는 반려동물 3마리가 있습니다. &e현대의 잔재&r, "
        "&5아기 레비아탄&r, &4네더라이트 미니스트로시티&r입니다! "
        "\n\n&e현대의 잔재&r와 &4네더라이트 미니스트로시티&r는 양동이에 담을 수 "
        "있습니다. \n\n&5아기 레비아탄&r은 물 양동이가 필요합니다."
    ),
    "quest.50C9CB8FB16E453D.quest_desc": (
        "&b타오르는 경기장&r은 &4네더&r에 있는 거대한 콜로세움 형태의 "
        "투기장입니다. \n평화롭지만 뜨거운 1층에 도착하며, 2층에는 &b이그나이티드 "
        "레버넌트&r가 있습니다. &b타오르는 재&r를 얻으려면 이들을 처치해야 합니다. "
        "\n\n그 재를 3층 제단에 사용해 &b&l이그니스&r를 소환할 수 있습니다! "
        "\n\n전리품을 찾는다면 3층 위쪽도 확인하세요!"
    ),
    "quest.50C9CB8FB16E453D.title": ("&b타오르는 경기장&r: &b&l이그니스&r의 거처"),
    "quest.5C6C4AD0F60BECCA.quest_desc": (
        "&e코피스&r는 &e코볼레톤&r이 사용하는 무기이자 전리품입니다. "
        "\n\n철 검과 같은 피해를 주지만 마법을 부여하거나 수리할 수 없습니다. "
        "\n\n플레이어가 오래 사용할 거라고는 생각하지 않은 모양이네요..."
    ),
    "quest.5E3263ACE170A8E3.quest_desc": (
        "&d소용돌이의 &e건틀릿&r은 &d수호의 건틀릿&r과 &e병 속의 모래폭풍&r을 "
        "&4기계식 융합 모루&r에서 합쳐 만듭니다. \n\n&4&lL_Ender's Cataclysm&r의 "
        "다른 무기와는 매우 다릅니다. \n\n우클릭을 길게 누르면 조준한 곳에 "
        "&d공허 &e소용돌이&r가 생깁니다. \n\n&d공허 &e소용돌이&r는 주변의 모든 "
        "개체를 빨아들인 뒤 몇 초 후 닫히며 폭발해 주변에 피해를 줍니다!"
    ),
    "quest.62089E9E6D596DA7.quest_desc": (
        "&3&b임모레이터&r는 &4기계식 융합 모루&r에서 &3섬멸자&r를 "
        "&b이그니티움 주괴&r로 업그레이드한 무기입니다. \n\n&b불타는 낙인&r에 "
        "걸린 몹에게 더 큰 피해를 주므로 &b타오르는 손길&r과 잘 어울립니다! "
        "\n\n양손에 &3&b임모레이터&r를 들고 우클릭을 길게 누르면 발밑에 "
        "&b화염 강타&r를 소환합니다. 범위 안의 모든 몹에게 피해를 주고 마지막에는 "
        "폭발합니다!"
    ),
    "quest.62089E9E6D596DA7.title": "&3&b임모레이터",
    "quest.689F32883C4E9502.quest_desc": (
        "&4&lL_Ender's Cataclysm&r은 새로운 보스와 던전, 그리고 전리품을 추가하는 "
        "모드입니다! \n\n정해진 보스 처치 순서는 없지만 더 강한 보스도 있고, 다른 "
        "보스를 상대하는 데 도움이 되는 전리품을 주는 보스도 있습니다. "
        "\n\n필요한 구조물은 각각의 눈을 이용해 찾으세요!"
    ),
    "quest.689F32883C4E9502.title": "&4&lL_Ender's Cataclysm",
    "quest.69439426534EBDC4.quest_desc": (
        "&b타오르는 손길&r은 &b이그니티움&r으로 만들 수 있는 또 다른 아이템입니다! "
        "\n\n손 칸에 착용하는 큐리오스 아이템입니다. \n\n착용하면 모든 공격이 일정 "
        "확률로 대상에게 &b불타는 낙인&r을 부여합니다. \n\n이 효과는 방어력과 방어 "
        "강도를 낮추며, &b&l이그니스&r에게 당하면 상당히 괴롭습니다."
    ),
    "quest.6BC3CF8937DEDE89.quest_desc": (
        "&c지옥불 용광로&r와 &d공허 코어&r를 합쳐 &d공허 &c용광로&r를 만드세요! "
        "\n\n여전히 채굴 등급과 속도가 같은 곡괭이입니다. \n\n이제 땅을 우클릭하면 "
        "&d공허의 룬&r을 부채꼴로 소환해 모든 몹에게 피해를 줄 수 있습니다. "
        "\n\n정말 곡괭이 기능에는 별로 집중하지 않는 것 같죠?"
    ),
    "quest.6ED61438A8A1EAA4.quest_desc": (
        "위더라이트는 &4하빈저&r가 떨어뜨리며, 항상 블록 1개가 나옵니다. 이 블록은 "
        "주괴 9개로 나눌 수 있습니다. \n\n위더라이트는 무기 3개와 "
        "&4기계식 융합 모루&r를 만드는 데 사용합니다. 이 모루로 "
        "&4&lL_Ender's Cataclysm&r 아이템을 조합할 수 있습니다!"
    ),
    "quest.6FC4146E534C51DA.quest_desc": (
        "네더라이트 업그레이드 형판, 네더라이트 투구, &c괴물의 뿔&r을 조합하면 "
        "&c괴물의 투구&r를 만들 수 있습니다. \n\n기본 능력치는 같지만 체력이 절반 "
        "아래로 떨어지면 주변의 모든 개체를 밀쳐내고 방어 능력치가 증가합니다."
    ),
    "quest.6FC4146E534C51DA.title": "&c괴물의 투구",
    "quest.70CDA5F1593DB4B2.quest_desc": (
        "&e저주받은 피라미드&r는 사막에 생성되며, 입구의 거대한 기둥 때문에 "
        "놓치기 어렵습니다. \n\n안에는 함정과 &e코볼레톤&r, 미니 보스가 "
        "기다립니다! \n\n상자와 장식된 도자기, 그리고 다음 단계에 필요한 수상한 "
        "모래도 있습니다..."
    ),
    "quest.70CDA5F1593DB4B2.title": ("&e저주받은 피라미드&r: &e&l고대의 잔재&r의 거처"),
    "quest.7270FA5C48AF7280.quest_desc": (
        "&3커스뮴 갑옷&r은 네더라이트 갑옷의 업그레이드입니다. 네더라이트 장비, "
        "&3커스뮴 주괴&r, &3커스뮴 업그레이드 형판&r을 조합하세요. 형판은 직접 "
        "제작할 수 있습니다! \n\n&3커스뮴 투구&r를 쓰고 C 키를 누르면 분광의 "
        "눈처럼 블록 너머의 몹을 볼 수 있습니다. \n\n&3커스뮴 흉갑&r은 내장된 "
        "불사의 토템처럼 작동해 죽을 때 한 번 살려 줍니다. 다만 재사용 대기시간은 "
        "6분입니다... \n\n&3커스뮴 레깅스&r는 확률적으로 공격을 회피합니다. "
        "&2&lMinecraft&r에서 확률이 어떻게 작동하는지는 모르겠네요! \n\n&3커스뮴 "
        "부츠&r를 신고 V 키를 누르면 뒤로 도약합니다. 낙하 피해도 크게 줄이지만 "
        "완전히 막지는 못합니다!"
    ),
    "quest.7270FA5C48AF7280.title": "&3커스뮴 갑옷",
    "quest.747B62A955D0C629.quest_desc": (
        "&4고대 공장&r은 &2오버월드&r 지하 깊은 곳에 있습니다. \n\n레버와 동력 "
        "레일, EMP 같은 레드스톤 아이템을 많이 찾을 수 있습니다. 곧 쓸모가 "
        "있을까요? \n\n&4감시자&f와 &4배회자&r 같은 레드스톤 기계가 플레이어를 "
        "공격합니다! \n\n위험하지만 훔쳐 갈 전리품과 블록도 많으며, 특히 레드스톤이 "
        "풍부합니다."
    ),
    "quest.747B62A955D0C629.title": ("&4고대 공장&r: &4&l하빈저&r의 거처"),
    "quest.74ACCEB6DC9EF6F7.quest_desc": (
        "&d공허 &4견착식 무기 &d(V.&4A.S.W.)&r는 위더 버전과 비슷하지만 더 "
        "강력합니다! \n\n이제 &d공허 &4곡사포&r만 발사하며, 더 큰 피해를 주고 "
        "&4곡사포&r가 명중한 지역의 땅에서 &d공허의 룬&r이 솟아나게 합니다. "
        "\n\n재사용 대기시간이 길지만 기다릴 시간은 충분합니다. \n\n&4기계식 융합 "
        "모루&r에서 &4W.A.S.W.&r와 &d공허 코어&r를 결합해 만들 수 있습니다."
    ),
    "quest.7AEE4BE3AB41ED3E.quest_desc": (
        "&b이그니티움 흉갑&r과 겉날개를 합치면 됩니다... 정말 간단합니다!"
    ),
    "quest.7C848C7011726470.quest_desc": (
        "&c괴물의 눈&r은 &c&l네더라이트 몬스트로시티&r와 싸울 수 있는 "
        "&c영혼 대장간&r으로 안내합니다."
    ),
    "quest.7F4963FCAE5337EC.quest_desc": (
        "&b&l이그니스&r만 상대해도 충분히 어렵지만, 먼저 "
        "&b이그나이티드 레버넌트&r를 처치해 &b타오르는 재&r를 얻어야 합니다. "
        "\n\n타오르는 재를 화염의 제단에 사용해 &b&l이그니스&r를 소환하세요."
    ),
    "quest.7F4963FCAE5337EC.title": "&b타오르는 재",
    "quest.1178E4123E8818E2.title": "&e병 속의 모래폭풍",
    "quest.462D173D576A8D91.title": "&e고대 금속 주괴",
    "quest.683C260C854C5AA3.title": "&4기계식 융합 모루",
}


def load_json(path: Path) -> dict[str, object]:
    """UTF-8 JSON 객체를 읽는다."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    """UTF-8 BOM 없이 JSON을 기록한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_text(value: str) -> str:
    """검수에서 확정한 공통 용어만 안전하게 통일한다."""
    for old, new in TEXT_REPLACEMENTS:
        value = value.replace(old, new)
    return value


def normalize_language_value(key: str, value: str) -> str:
    """언어 키의 계열별 규칙을 적용한다."""
    value = normalize_text(value)
    if key.startswith("block.cataclysm.curved_azure_seastone_"):
        value = value.replace("조각된 청해석", "곡면 청해석", 1)
    if key.startswith(
        (
            "block.cataclysm.polished_azure_seastone",
            "block.cataclysm.polished_obsidian",
        )
    ):
        value = value.replace("매끄러운", "윤나는", 1)
    return value


def review_language() -> dict[str, object]:
    """현재 설치 JAR의 735개 언어 키를 원문과 다시 대조한다."""
    english = load_json(LANG_ROOT / "en_us.json")
    korean = load_json(LANG_ROOT / "ko_kr.json")
    sources = load_json(LANG_ROOT / "candidate_sources.json")
    before = dict(korean)
    missing_overrides = sorted(set(LANGUAGE_OVERRIDES) - set(english))
    if missing_overrides:
        raise KeyError(f"현재 원문에 없는 언어 교정 키: {missing_overrides}")

    for key, source in english.items():
        original = korean[key]
        if key in LANGUAGE_OVERRIDES:
            korean[key] = LANGUAGE_OVERRIDES[key]
        if isinstance(korean[key], str):
            korean[key] = normalize_language_value(key, korean[key])
        if sources[key] == "new_translation_required":
            if key not in LANGUAGE_OVERRIDES and not family_goal.is_allowed_original(
                str(source)
            ):
                raise ValueError(f"수동 번역이 빠진 언어 키: {key}")
            sources[key] = "manual_review"
        elif korean[key] != original:
            sources[key] = "manual_quality_review"
        errors = family_goal.validate_value(key, source, korean[key])
        if errors:
            raise ValueError("; ".join(errors))

    write_json(LANG_ROOT / "ko_kr.json", korean)
    write_json(LANG_ROOT / "candidate_sources.json", sources)
    return {
        "keys_reviewed": len(english),
        "changes_this_run": sum(korean[key] != before[key] for key in korean),
        "reviewed_or_edited": sum(
            value in {"manual_review", "manual_quality_review"}
            for value in sources.values()
        ),
        "source_counts": dict(sorted(Counter(sources.values()).items())),
    }


def replace_quest_text(value: object, replacement: str) -> object:
    """퀘스트 값의 첫 표시 문구만 바꾸고 이미지 요소는 그대로 둔다."""
    replacement = replacement.replace("\n", "\\n")
    if isinstance(value, str):
        return replacement
    if isinstance(value, list) and value and isinstance(value[0], str):
        return [replacement, *value[1:]]
    raise TypeError(f"지원하지 않는 퀘스트 표시 값: {value!r}")


def normalize_quest_value(value: object) -> object:
    """문자열과 문자열 목록에 공통 용어 교정을 적용한다."""
    if isinstance(value, str):
        value = normalize_text(value)
        value = value.replace("&4&l대재앙", "&4&lL_Ender's Cataclysm")
        value = value.replace("&4&lCataclysm", "&4&lL_Ender's Cataclysm")
        return value
    if isinstance(value, list):
        return [normalize_quest_value(item) for item in value]
    return value


def review_quests() -> dict[str, object]:
    """전용 및 관련 FTB Quests 표시 키를 모두 재검수한다."""
    reviewed = 0
    changed = 0
    source_counts: Counter[str] = Counter()
    seen: set[str] = set()
    for root in sorted((WORK_ROOT / "quests").glob("*")):
        english_path = root / "en_us.json"
        korean_path = root / "ko_kr.json"
        source_path = root / "candidate_sources.json"
        if not english_path.is_file():
            continue
        english = load_json(english_path)
        korean = load_json(korean_path)
        sources = load_json(source_path)
        before = dict(korean)
        for key, source in english.items():
            if key in QUEST_OVERRIDES:
                korean[key] = replace_quest_text(korean[key], QUEST_OVERRIDES[key])
                sources[key] = "manual_review"
                seen.add(key)
            elif key in QUEST_QUALITY_OVERRIDES:
                korean[key] = replace_quest_text(
                    korean[key], QUEST_QUALITY_OVERRIDES[key]
                )
                sources[key] = "manual_quality_review"
                seen.add(key)
            korean[key] = normalize_quest_value(korean[key])
            if sources[key] == "new_translation_required":
                raise ValueError(f"수동 번역이 빠진 퀘스트 키: {key}")
            if korean[key] != before[key] and sources[key] not in {
                "manual_review",
                "manual_quality_review",
            }:
                sources[key] = "manual_quality_review"
            errors = family_goal.quest_snbt.validate_value(key, source, korean[key])
            if errors:
                raise ValueError("; ".join(errors))
        reviewed += len(english)
        changed += sum(korean[key] != before[key] for key in korean)
        source_counts.update(str(value) for value in sources.values())
        write_json(korean_path, korean)
        write_json(source_path, sources)

    unknown = sorted((set(QUEST_OVERRIDES) | set(QUEST_QUALITY_OVERRIDES)) - seen)
    if unknown:
        raise KeyError(f"현재 퀘스트 원문에 없는 교정 키: {unknown}")
    return {
        "keys_reviewed": reviewed,
        "changes_this_run": changed,
        "source_counts": dict(sorted(source_counts.items())),
    }


def review() -> dict[str, object]:
    """언어와 모든 퀘스트 표시 경로의 수동 검수 결과를 기록한다."""
    report = {
        "family": "L_Ender's Cataclysm",
        "language": review_language(),
        "ftbquests": review_quests(),
    }
    write_json(WORK_ROOT / "manual_review_report.json", report)
    return report


def refresh_sources() -> dict[str, object]:
    """현재 설치본에서 검수 기준 영어 원문만 다시 기록한다."""
    instance = resolve_source_root()
    jar = family_goal.find_jar(instance, "L_Ender's Cataclysm ")
    with ZipFile(jar) as archive:
        language = json.loads(
            archive.read("assets/cataclysm/lang/en_us.json").decode("utf-8-sig")
        )
    quest_root = instance / "config/ftbquests/quests/lang/en_us/chapters"
    dedicated = family_goal.quest_snbt.parse_language_snbt(
        quest_root / "cataclysm.snbt_merged"
    )
    related = family_goal.related_quest_keys(instance, "cataclysm")
    write_json(LANG_ROOT / "en_us.json", language)
    write_json(WORK_ROOT / "quests/cataclysm/en_us.json", dedicated)
    write_json(WORK_ROOT / "quests/related/en_us.json", related)
    inventory = family_goal.inventory(instance, "cataclysm")
    write_json(WORK_ROOT / "inventory.json", inventory)
    return {
        "jar": jar.name,
        "language_keys": len(language),
        "dedicated_quest_keys": len(dedicated),
        "related_quest_keys": len(related),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("review", "sources"))
    args = parser.parse_args()
    if args.command == "review":
        report = review()
    else:
        report = refresh_sources()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
