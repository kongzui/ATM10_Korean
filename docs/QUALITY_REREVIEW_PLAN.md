# ATM10 8.1 전체 번역 품질 재검수 계획

작성일: 2026-09-28. 기준: `output/8.1` 안정판(`8.1-stable.7`)의 리소스팩 293개 네임스페이스와
FTB Quests 66챕터, 가이드·KubeJS 산출물이에요.

지금까지의 번역과 GPT 품질 검수를 거친 결과에도 구글 기계 번역의 흔적과 영어 어순을 그대로 옮긴
번역체가 남아 있어요. 이 문서는 **이미 번역된 모든 모드를 빠짐없이** 다시 검수하기 위한 순서표예요.
미번역 모드의 신규 번역은 [번역 현황](MOD_TRANSLATION_PLAN.md)과
[누적 업데이트 로드맵](ATM10_VERSION_TRANSLATION_UPGRADE_PLAN.md)을 따르고, 여기서는 다루지 않아요.

## 1. 재검수가 필요한 근거

현재 산출물에서 뽑은 대표 사례예요. 대부분 플레이어가 가장 먼저 보는 메인 퀘스트에 있어요.

| 위치 | 현재 번역 | 문제 |
|---|---|---|
| `mainquestline_part_1` | 갑옷을 입고 있어도 당신은 여전히 탈 것입니다. 시도하지 마세요. | 대명사·미래형 직역 |
| `mainquestline_part_1` | 대부분의 경우 이것이 여러분이 원하는 힘일 것입니다. | power를 `힘`으로 오역 |
| `mainquestline_part_1` | 초반 게임에 더 많은 힘을 얻으세요! | 영어 어순·오역 |
| `chapter_2_the_star` | 또는 대부분이 알고 있는 이터널 스텔라입니다. | 원문 의미 붕괴 |
| `chapter_2_the_star` | &b&l어플라이드 에너제틱스&r는 ... | 용어집의 공식 모드명 규칙 위반 |
| `chapter_2_the_star` | 당신은 당신의 흑요석 발전기를 엔더 발전기로 상위 버전으로 변환할 수 있습니다. | 대명사 반복·중복 조사 |
| `chapter.snbt` | 그리고 레이저IO / 신비농업 / 플러스 별 자동화! | 모드명 음역·뜻 번역, 직역 |
| `chapter_group.snbt` | 모던 인더스트리얼라이제이션 | 같은 목록에 영문 표기와 음역이 섞임 |

`당신|그것은|것입니다|하십시오|에 의해|를 위한` 같은 번역체 신호를 단순 검색하면 241개 파일에서
1,138회가 나와요. 오류 수가 아니라 **우선 확인할 위치를 찾는 신호**예요. 이 표현이 없는 파일에도
어순·오역·용어 문제가 있을 수 있으므로 신호가 없다고 검수를 생략하지 않아요.

신호가 많은 곳: Ice and Fire 퀘스트 50, Mekanism 퀘스트 41, PneumaticCraft 퀘스트·가이드 40여,
Occultism 언어 85, MineColonies 언어 78, Iron's Spells 언어 63, Theurgy 언어 54,
The Twilight Forest 언어 42, Neo Vitae 언어 25, Mahou Tsukai 언어 24.

모드 JAR의 내장 한국어를 대량 재사용한 모드도 위험도가 높아요. 예: Create 3,617키,
Occultism 3,587키(전량), MineColonies 3,898키(전량), FancyMenu 3,367키, Ars Nouveau 2,361키,
Mekanism 1,821키, Twilight Forest 1,764키, JourneyMap 1,371키, Mahou Tsukai 1,338키.

## 2. 순위를 정한 방법

각 계열을 두 기준으로 1~5점 평가하고, 같은 점수면 위험 신호가 큰 쪽을 앞에 둬요.

- **노출도:** 모든 플레이어가 보는 화면인지, 메인 퀘스트와 초반 진행에 나오는지, 전용 퀘스트
  챕터·가이드가 있는지, 툴팁처럼 계속 보이는 문구인지.
- **중요도:** ATM Star 제작 경로에 필요한지, 잘못 번역되면 진행이나 기계 사용을 막는지, 여러
  모드가 공유하는 용어의 기준이 되는지.
- **위험 신호:** 번역체 검색 결과, JAR 내장 한국어 대량 재사용, 퀘스트·가이드 같은 긴 문장의 양.
  GPT 품질 검수 이력은 참고만 하고 순위를 낮추는 이유로 쓰지 않아요.

키 수는 `output/8.1` 한국어 파일의 키 줄 수이고, 퀘스트는 8.1 영어 챕터의 추정 키 수예요.
작업량을 가늠하는 값이며 정확한 수정 대상 수가 아니에요.

## 3. 재검수 순서

단계는 A부터 차례로 진행해요. 한 계열이 끝날 때마다 검증·커밋·배포하고 다음 계열로 넘어가요.
표의 `GPT`는 `working/*/quality_review_completion.json`에 GPT 품질 검수 기록이 있다는 뜻이에요.

### 단계 A. 모든 플레이어가 반드시 보는 화면

| 순위 | 계열 | 언어 키 | 퀘스트 키 | 노출·중요 | 위험·비고 |
|---:|---|---:|---:|:---:|---|
| 1 | 팩 공통 진행 퀘스트 | 64 | 1,888 | 5·5 | 메인 퀘스트 번역체 다수, 모드명 표기 혼용 |
| 2 | 항상 보는 공통 UI | 4,841 | — | 5·5 | JourneyMap·Jade·JEI 내장 한국어 재사용 |
| 3 | Sophisticated 계열 | 1,137 | 퀘스트 1의 저장소 | 5·4 | GPT, 배낭 툴팁·업그레이드 설명 |
| 4 | 인벤토리·정보·가이드 UI | 2,483 | — | 4·4 | Corail Tombstone 1,253키 |
| 5 | 초반 기반 도구·기계·물류 | 1,769 | 퀘스트 1의 기본 챕터 | 4·4 | 초반 툴팁 노출이 많음 |
| 6 | Allthemodium·ATM 광물 | 2,662 | 퀘스트 1의 2장 | 4·5 | GPT, 압축 1,796키는 규칙 검사 |

### 단계 B. ATM Star 진행의 핵심 기술·자원

| 순위 | 계열 | 언어 키 | 퀘스트 키 | 노출·중요 | 위험·비고 |
|---:|---|---:|---:|:---:|---|
| 7 | Applied Energistics 2와 애드온 | 2,099 | 266 | 4·5 | GPT, GuideME 대량, 공유 용어 기준 |
| 8 | Mekanism 계열 | 5,216 | 468 | 4·5 | GPT, 퀘스트 신호 41, KubeJS 툴팁 |
| 9 | Mystical Agriculture | 849 | 278 | 4·5 | GPT, 챕터명 `신비농업` 중복 표기 |
| 10 | Apotheosis 계열·Gateways | 1,547 | 267 | 4·4 | GPT, 장비 어픽스 툴팁, 가이드 |
| 11 | Artifacts·Relics | 1,568 | 234 | 3·4 | Relics GPT, 능력 설명 문장 |
| 12 | Refined Storage 계열 | 1,490 | 126 | 3·4 | 내장 한국어 778키 재사용 |
| 13 | Create 계열 | 4,987 | 217 | 3·4 | 내장 한국어 3,617키 재사용, Ponder |
| 14 | Productive Bees·Trees | 5,326 | 749 | 3·4 | 퀘스트 양이 많음, 가이드 |
| 15 | 전력: Powah·Flux·Extreme Reactors·Ender IO | 1,540 | 110 | 3·4 | Powah·Flux·Ender IO GPT |
| 16 | Modern Industrialization 계열 | 2,230 | 183 | 3·4 | 그룹명 음역, 가이드북 |
| 17 | Draconic Evolution | 735 | 254 | 3·4 | 최종 장비·반응로 안내 |

### 단계 C. 많이 선택하는 대형 콘텐츠

| 순위 | 계열 | 언어 키 | 퀘스트 키 | 노출·중요 | 위험·비고 |
|---:|---|---:|---:|:---:|---|
| 18 | Silent Gear 계열 | 1,453 | 80 | 3·3 | GPT, 특성 설명 KubeJS 데이터 |
| 19 | Just Dire Things | 488 | 165 | 3·3 | Patchouli 가이드 |
| 20 | Ars Nouveau 계열 | 4,274 | 76 | 3·3 | GPT, 내장 한국어 2,361키 |
| 21 | Iron's Spells 계열 | 1,649 | 213 | 3·3 | 언어 신호 63 |
| 22 | The Twilight Forest | 2,061 | 123 | 3·3 | 언어 신호 42, 탐험 수첩 |
| 23 | Ice and Fire | 1,744 | 173 | 3·3 | 퀘스트 신호 50으로 최다 |
| 24 | 차원·보스 6종 | 6,621 | 1,119 | 3·3 | Aether·Bumblezone·Eternal Starlight 등 |
| 25 | Occultism | 3,588 | 164 | 2·3 | 내장 한국어 전량 재사용, 신호 85 |
| 26 | Immersive Engineering | 1,952 | 245 | 2·3 | 설명서 본문 |
| 27 | PneumaticCraft: Repressurized | 2,271 | 279 | 2·3 | 퀘스트·Patchouli 신호 많음 |
| 28 | Industrial Foregoing | 688 | 106 | 2·3 |  |
| 29 | Oritech | 1,256 | 85 | 2·3 | Oracle Index 가이드 |
| 30 | Integrated Dynamics 계열 | 2,960 | 54 | 2·3 | 논리 용어는 용어집 확정분 유지 |

### 단계 D. 중소형·전문 콘텐츠

| 순위 | 계열 | 언어 키 | 퀘스트 키 | 노출·중요 | 위험·비고 |
|---:|---|---:|---:|:---:|---|
| 31 | 소형 자동화 | 1,834 | 170 | 2·3 | HNN·Modular Routers·Pylons·LaserIO·MFFS·XyCraft |
| 32 | Theurgy·Mahou Tsukai | 4,667 | 157 | 2·2 | 신호 54·24, Mahou 내장 한국어 재사용 |
| 33 | 기타 마법 | 2,221 | 264 | 2·2 | Forbidden Arcanus·EvilCraft·Nature's Aura 등 |
| 34 | 8.1 신규 콘텐츠 | 4,717 | 151 | 2·2 | Neo Vitae·Auroral·Ad Astra·Logistics Networks |
| 35 | MineColonies 계열 | 4,356 | — | 2·2 | 내장 한국어 전량 재사용, 신호 78 |
| 36 | 음식·농업 | 4,334 | 퀘스트 1의 음식 | 2·2 | Pam's·Herbs and Harvest 문장 |
| 37 | 기타 기술 | 4,817 | 117 | 2·2 | Actually Additions·Railcraft·CC 등 |
| 38 | SecurityCraft·Supplementaries | 3,027 | — | 2·2 | 설명 툴팁과 설정 문장 |
| 39 | 생물군계·구조물·몹 | 2,947 | — | 2·2 | 이름 위주, 규칙 검사 병행 |

### 단계 E. 설정 화면과 대량 장식 블록

| 순위 | 계열 | 언어 키 | 퀘스트 키 | 노출·중요 | 위험·비고 |
|---:|---|---:|---:|:---:|---|
| 40 | 클라이언트 설정 UI | 4,235 | — | 1·2 | FancyMenu 편집기 3,368키 대부분 |
| 41 | 건축·장식 대량 변형 | 43,523 | — | 2·1 | 재료명×형태명 규칙 검사와 표본 검수 |

41번은 BiblioWoods·BiblioBiomes·Chipped처럼 `재료 + 형태` 조합 이름이 대부분이에요. 모든 키를
사람이 한 줄씩 다시 쓰는 대신, 재료명·형태명 사전을 먼저 확정하고 전체 키를 프로그램으로 대조한 뒤
규칙에서 벗어난 이름과 설명 문장만 수동으로 고쳐요. 이 방식도 전체 키를 대조하므로 생략이 아니에요.

## 4. 계열별 포함 범위

모든 `output/8.1` 네임스페이스와 퀘스트 챕터를 한 계열에 한 번씩 배정했어요.

1. **팩 공통 진행 퀘스트** — 챕터 `welcome`, `mainquestline_part_1`, `allthemodium`,
   `chapter_2_the_star`, `achapter_2r_6the_atm_star`, `tips_and_tricks`, `building_tips`,
   `bounty_board`, `basic_tools`, `basic_armor`, `basic_power`, `basic_logistics`, `storage`,
   `generators`, `food_and_farming`와 `chapter.snbt`, `chapter_group.snbt`, `file.snbt`,
   `reward_table.snbt`. 언어 `kubejs`, `atm`, `atm10_localization`, `allthetweaks`,
   `ftbquestslangsplitter`. KubeJS `tooltips.js`, `RecipeViewer.js`, `CustomAdditions.js`와
   나머지 시작 스크립트 표시 문구.
2. **항상 보는 공통 UI** — `jei`, `jade`, `ftbquests`, `ftbchunks`, `ftbteams`, `ftbultimine`,
   `ftbessentials`, `ftbfiltersystem`, `journeymap`, `curios`, `waystones`, `naturescompass`,
   `explorerscompass`.
3. **Sophisticated 계열** — `sophisticatedcore`, `sophisticatedbackpacks`,
   `sophisticatedstorage`, `sophisticatedstorageinmotion`.
4. **인벤토리·정보·가이드 UI** — `appleskin`, `enchdesc`, `moreoverlays`, `tombstone`, `lootr`,
   `polymorph`, `craftingtweaks`, `controlling`, `mousetweaks`, `invtweaks`, `trashslot`,
   `betteradvancements`, `betteradvancedtooltips`, `guideme`, `patchouli`, `modonomicon`,
   `akashictome`, `tempad`, `tempad_static`, `jearchaeology`.
5. **초반 기반 도구·기계·물류** — `ironfurnaces`, `mininggadgets`, `buildinggadgets2`,
   `constructionstick`, `simplemagnets`, `ironjetpacks`, `bhc`, `toolbelt`, `easy_villagers`,
   `itemcollectors`, `mob_grinding_utils`, `functionalstorage`, `pocketstorage`, `enderstorage`,
   `pipez`, `moderndynamics`, `xnet`, `generatorgalore`, `energymeter`, `quarryplus`.
6. **Allthemodium·ATM 광물** — `allthemodium`, `allthearcanistgear`, `allthewizardgear`,
   `alltheores`, `allthecompressed`와 Allthemodium Patchouli 가이드.
7. **Applied Energistics 2와 애드온** — `ae2`, `ae2wtlib`, `advanced_ae`, `extendedae`,
   `expandedae`, `megacells`, `appflux`, `enderdrives`, `ae2importexportcard`, `ae2netanalyser`,
   `merequester`, `arseng`, `ae2ct`, `aeinfinitybooster`, `appmek`, `immeng`,
   `soulplied_energistics`, GuideME 가이드 전체, 챕터 `applied_energistics_2`,
   `extended__advanced_ae`. 보조 코드인 EnderDrives 스크립트는 기본 배포 규칙대로 제외 상태 유지.
8. **Mekanism 계열** — `mekanism`, `mekanismgenerators`, `mekanismtools`, `mekmm`,
   `mekanismcovers`, `mekanisticrouters`, `jei_mekanism_multiblocks`, `gmut`, 챕터 `mekanism`,
   `mekanism_reactors`, KubeJS `Mekanism-Tooltips.js`.
9. **Mystical Agriculture** — `mysticalagriculture`, `mysticalagradditions`, 챕터
   `elmystical_agriculturerr`.
10. **Apotheosis 계열·Gateways** — `apotheosis`, `apothic_attributes`, `apothic_enchanting`,
    `apothic_spawners`, `gateways`, Apotheosis 가이드, 챕터 `apotheosis_2`, `apotheosis_gear`,
    `apothic_enchanting`.
11. **Artifacts·Relics** — `artifacts`, `relics`, `reliquified_artifacts`, 챕터 `artifacts`,
    `relics`.
12. **Refined Storage 계열** — `refinedstorage`, `extradisks`, `extrastorage`, `universalgrid`,
    `refinedtypes`, `cabletiers`, `interdimensionalwirelesstransmitter`, `stepcrafter`,
    `refinedstorage_curios_integration`, `refinedstorage_jei_integration`,
    `refinedstorage_mekanism_integration`, `refinedstorage_quartz_arsenal`, 챕터
    `refined_storage`.
13. **Create 계열** — `create`, `create_dragons_plus`, `createaddition`,
    `create_enchantment_industry`, `create_aquatic_ambitions`, `create_hypertube`,
    `bellsandwhistles`, 챕터 `create`.
14. **Productive Bees·Trees** — `productivebees`, `modularbees`, `productivetrees`, 가이드, 챕터
    `productive_bees`, `productive_trees`.
15. **전력** — `powah`, `lollipop`(Powah 내부 UI), `fluxnetworks`, `bigreactors`, `zerocore`,
    `enderio`, 챕터 `powah`, `extreme_reactors`.
16. **Modern Industrialization 계열** — `modern_industrialization`,
    `extended_industrialization`, `industrialization_overdrive`, 가이드북, 챕터 `mi_steam`,
    `mi_electric`, `mi_digital`, `mi_endgame`.
17. **Draconic Evolution** — `draconicevolution`, 챕터 `draconic_evolution`.
18. **Silent Gear 계열** — `silentgear`, `silentlib`, `silentgems`, `sgearmetalworks`,
    KubeJS 특성 데이터, 챕터 `silent_gear`.
19. **Just Dire Things** — `justdirethings`, Patchouli 가이드, 챕터 `justdirethings`.
20. **Ars Nouveau 계열** — `ars_nouveau`, `ars_additions`, `ars_elemancy`, `ars_elemental`,
    `ars_creo`, `ars_controle`, `ars_technica`, `ars_ocultas`, `ars_unification`,
    `not_enough_glyphs`, `starbunclemania`, 가이드, 챕터 `ars_nouveau`.
21. **Iron's Spells 계열** — `irons_spellbooks`, `irons_jewelry`, `irons_lib`,
    `irons_patreon_lib`, 챕터 `iron_spells_and_spellbooks`.
22. **The Twilight Forest** — `twilightforest`, 탐험 수첩, 챕터 `twilight_forest`.
23. **Ice and Fire** — `iceandfire`, 가이드, 챕터 `ice__fire`.
24. **차원·보스 6종** — `aether`, `the_bumblezone`, `eternal_starlight`, `deeperdarker`,
    `undergarden`, `cataclysm`, 챕터 `aether`, `bumblezone`, `eternal_starlight`,
    `deeper_and_darker`, `undergarden`, `cataclysm`.
25. **Occultism** — `occultism`, 가이드, 챕터 `occultism`.
26. **Immersive Engineering** — `immersiveengineering`, 설명서, 챕터 `immersive_engineering`.
27. **PneumaticCraft** — `pneumaticcraft`, Patchouli 가이드, 챕터 `pneumaticcraft`.
28. **Industrial Foregoing** — `industrialforegoing`, `industrialforegoingsouls`, 챕터
    `industrial_foregoing`.
29. **Oritech** — `oritech`, Oracle Index 가이드, 챕터 `oritech`.
30. **Integrated Dynamics 계열** — `integrateddynamics`, `integrateddynamicscompat`,
    `integratedterminals`, `integratedterminalscompat`, `integratedtunnels`,
    `integratedcrafting`, `integratedscripting`, 가이드, 챕터 `integrated_dynamics`.
31. **소형 자동화** — `hostilenetworks`, `modularrouters`, `pylons`, `laserio`, `mffs`,
    `xycraft_core`, `xycraft_machines`, `xycraft_world`, `xycraft_override`, 관련 가이드, 챕터
    `hostile_neural_networks`, `modular_router`, `pylons`, `xycraft`.
32. **Theurgy·Mahou Tsukai** — `theurgy`, `mahoutsukai`, 챕터 `theurgy`, `mahou_tsukai`.
33. **기타 마법** — `forbidden_arcanus`, `evilcraft`, `evilcraftcompat`, `naturesaura`,
    `rootsclassic`, `reliquary`, 관련 가이드, 챕터 `forbidden__arcanus`, `evilcraft`,
    `natures_aura`.
34. **8.1 신규 콘텐츠** — `neovitae`, `auroral`, `ad_astra`, `ad_astra_giselle_addon`,
    `logisticsnetworks`, 각 가이드, 챕터 `neo_vitae`, `auroral`.
35. **MineColonies 계열** — `minecolonies`, `structurize`, `domum_ornamentum`, `blockui`,
    내장 가이드.
36. **음식·농업** — `farmersdelight`, `cookingforblockheads`, `farmingforblockheads`,
    `pamhc2crops`, `pamhc2foodcore`, `pamhc2foodextended`, `pamhc2trees`, `herbsandharvest`,
    `merrymaking`, `aquaculture`, `sushigocrafting`, `botanypots`, 관련 책·가이드.
37. **기타 기술** — `actuallyadditions`, `railcraft`, `stevescarts`, `rftoolsbase`,
    `rftoolsbuilder`, `rftoolspower`, `rftoolsstorage`, `rftoolsutility`, `computercraft`,
    `advancedperipherals`, `morered`, `sfm`, `little_big_redstone`, `redstonepen`,
    `compactmachines`, `productivemetalworks`, 관련 가이드·도움말·SFML 예제, 챕터 `railcraft`.
38. **SecurityCraft·Supplementaries** — `securitycraft`, `supplementaries`, `amendments`.
39. **생물군계·구조물·몹** — `biomeswevegone`, `regions_unexplored`, `dungeons_arise`,
    `betterdungeons`, `bettermineshafts`, `betterdeserttemples`, `betterendisland`,
    `betterwitchhuts`, `betterfortresses`, `betterstrongholds`, `betteroceanmonuments`,
    `betterjungletemples`, `repurposed_structures`, `mvs`, `mns`, `mss`, `mes`,
    `endermanoverhaul`, `creeperoverhaul`, `livingthings`, `variantsandventures`.
40. **클라이언트 설정 UI** — `fancymenu`, `sodium-extra`, `iris`, `iris_search`, `fzzy_config`,
    `extremesoundmuffler`, `auroras`, `rainbows`, `mifa`.
41. **건축·장식 대량 변형** — `chipped`, `chisel`, `rechiseled`, `rechiseledcreate`,
    `bibliocraft`, `bibliowoods`, `bibliobiomes`, `mcwdoors`, `mcwbridges`, `mcwroofs`,
    `mcwholidays`, `mcwlights`, `mcwfences`, `mcwpaths`, `mcwwindows`, `mcwfurnitures`,
    `mcwstairs`, `mcwtrpdoors`, `handcrafted`, `refurbished_furniture`, `framedblocks`,
    `xtonesreworked`, `everythingcopper`, `dyenamics`, `dyenamicsandfriends`, `luminax`,
    `simplylight`, `additional_lights`, `glassential`, `connectedglass`, `factory_blocks`.

## 5. Claude 재검수 기준

`AGENTS.md`의 번역·검증 규칙과 [용어집](../glossary/README.md)을 그대로 따르고, 문장 품질은
아래 기준으로 다시 봐요.

### GPT 검수에서 이어받는 것

- 키·자료형·자리표시자·서식 코드·줄바꿈 보존과 자동 검증.
- 용어집 확정 용어, 공식 모드명 영문 유지, `Upgrade`→`업그레이드` 같은 이름 규칙.
- 퀘스트 제목·Task·자동 제목과 아이템 이름의 일치 검사.
- 계열마다 기록한 금지 표현 목록(`scripts/*_family.py`, `build_ae2_addon_guides.py` 등).

### 새로 적용하는 문장 기준

- **목표는 처음부터 한국어로 만든 게임처럼 읽히는 문장이에요.** 다만 과도한 의역은 하지 않고,
  원문에 없는 정보·농담·이름을 만들지 않아요(`AGENTS.md`의 목표 문체).
- **용어는 종류별 기준을 따른다.** 이름은 바닐라 공식 한국어, 시스템·동작 용어는 한국
  플레이어가 실제로 쓰는 말이에요. 음역·원문 유지·뜻 번역의 선택과 용어 적용 범위는
  [용어집](../glossary/README.md) 2·3장을 따르고, 계열마다 용어집 6장의 교체 대상(`개체`,
  `재사용 대기시간`, `재생성`, `생물군계` 등)을 찾아 문맥을 보고 바꿔요. `개체 수`처럼 다른
  뜻이거나 바닐라 이름(`생성 알`, `시련 생성기`)이면 그대로 둬요.
- **영어 구조를 버리고 뜻으로 다시 쓴다.** 원문 한 문장을 한국어 한 문장으로 맞추지 않아도 돼요.
  정보·수치·조건만 빠짐없이 옮겨요.
- **대명사를 지운다.** `당신`, `그것`, `이것은`, `여러분`은 대부분 생략하거나 대상 이름으로 바꿔요.
- **직역 어미를 피한다.** `~할 것입니다`, `~에 의해`, `~를 위한`, `~하는 것이 가능합니다`,
  `~을 가지고 있습니다`처럼 영어 문형에서 온 표현은 자연스러운 한국어로 바꿔요.
- **게임 뜻으로 옮긴다.** `power`는 문맥에 따라 전력·동력, `tier`는 등급·단계, `upgrade`는
  이름에서는 업그레이드, 동작에서는 `상위 등급으로 바꾸다`처럼 구분해요.
- **말투를 통일한다.** 게임 안 문장은 합쇼체(`~합니다·~하세요`)예요. 해요체가 섞인 문장은
  고치고, 인물 대사만 인물에 맞는 말투를 허용해요. 농담·관용구는 `AGENTS.md`의 기준을 따라요.
- **툴팁은 짧게.** 한 줄 툴팁은 명사형·간결한 문장으로 쓰고, 긴 설명만 문장으로 풀어요.
- **모드명 표기를 고친다.** 음역·뜻 번역된 공식 모드명(`어플라이드 에너제틱스`, `레이저IO`,
  `모던 인더스트리얼라이제이션`, `신비농업`)은 용어집 규칙대로 영문으로 되돌려요.
- **의심되면 원문을 다시 본다.** 모드 내장 한국어·기존 산출물은 후보일 뿐이고, 영어 원문과 실제
  게임 동작을 기준으로 판단해요. 확신할 수 없는 용어는 용어집 보류 목록에 남겨요.

### 계열 하나를 진행하는 순서

1. 현재 설치 JAR·퀘스트의 영어 원문과 `output/8.1` 한국어를 키 단위로 짝지어요.
2. 계열에 필요한 용어를 먼저 확정하고 용어집을 갱신해요.
3. 이름 → UI·툴팁 → 퀘스트 → 가이드 순으로 100~200키씩 전체를 읽고 고쳐요.
4. 바꾼 이름이 퀘스트·가이드·다른 모드에 쓰였는지 찾아 같이 고쳐요.
5. `AGENTS.md`의 문법·키·보호 문자열·표시 경로 검증을 통과시켜요.
6. 수정 수·유지 수를 `versions/8.1/reports/`에 기록하고 커밋, 적용 규칙에 따라 배포해요.

이번 작업은 사용자가 요청한 **전체 재검수**예요. 버전업 때의 "같은 영어는 재사용" 규칙과 달리,
기존 번역도 모두 다시 읽어요. 다만 문제가 없는 번역은 억지로 바꾸지 않고 유지 수로 기록해요.

### 분업 진행(오케스트레이터·워커)

2순위 2부 시험 운영(8.1-stable.11) 결과, 3순위부터는 Opus 오케스트레이터가 계획·검토를 맡고
Sonnet 워커가 키를 읽고 고치는 방식으로 진행해요. 규칙은 `AGENTS.md`의 `서브에이전트 분업`,
워커 지시문은 [REREVIEW_WORKER_BRIEF.md](REREVIEW_WORKER_BRIEF.md)예요.

**오케스트레이터 준비**

1. `working/quality_rereview/<계열>/scope.json`을 만들어요. `status`는 `in_progress`, 기준 커밋은
   현재 HEAD, 언어는 `language_namespaces`와 작업 원본 `language_sources`, 퀘스트는 `quest_files`,
   KubeJS는 `kubejs_files`예요.
2. 작업 원본을 빠짐없이 찾아요. 네임스페이스의 `ko_kr.json`만이 아니라 같은 값을 들고 있는 파일
   (예: Explorer's Compass의 `structure_overrides.json`·`structure_fallbacks.json`)도
   `language_sources`에 넣어야 수정이 함께 반영돼요. `rg -l "<키>" working scripts`로 찾아요.
3. `python scripts/rereview_worker_kit.py pairs <계열>`로 `temp/rereview/<계열>/` 대조 파일을,
   `python scripts/rereview_worker_kit.py index`로 이름 색인을 만들어요.
4. `python scripts/quality_rereview_lang.py <계열>`(또는 `quality_rereview_quests.py`)를 한 번
   돌려 수정본 없이도 오류가 없는지 확인해요.
5. 계열에 필요한 용어가 용어집에 없으면 먼저 정해 용어집에 넣거나 워커 지시에 적어요.

**워커 배정**

- 워커 하나에 약 1,200~1,500키(대조 파일 약 200KB 이하)를 맡겨요. 시험 운영에서 이 크기로 워커당
  약 21만~23만 토큰, 5분 남짓 걸렸어요.
- 서로 겹치지 않는 파일끼리만 병렬로 돌려요. 같은 이름이 퀘스트와 언어 파일에 함께 나오면 한
  워커에게 묶어요.
- 부를 때는 지시문 경로, 계열 이름, 맡은 파일, 계열 특유의 주의점(공식 모드명, 확정 용어, 원문이 없는
  키를 읽는 법)만 짧게 알려 줘요. 규칙 전문은 지시문과 `AGENTS.md`에 있으니 다시 쓰지 않아요.
- 워커는 `rereview-worker` 에이전트(`.claude/agents/rereview-worker.md`, Sonnet·medium)로 불러요.
  이 정의가 지시문을 먼저 읽게 하고 쓰기 범위를 제한해요.

**오케스트레이터 검토**

1. 워커가 고친 키를 `영어 / 전 / 후 / 사유`로 나란히 뽑아 전부 읽어요. 단순 치환(용어 교체만 한
   키)은 따로 묶어 훑고, 나머지를 한 줄씩 판단해요.
2. 유지한 키 전체에 번역투 패턴(`이는`, `이러한`, `~된 경우`, `이 옵션을`, `~을 위한`, `당신`,
   `것입니다`, `에 의해`, `옵션`)을 검사하고, 무작위로 50~60키를 직접 읽어요.
3. 틀린 수정은 되돌리고, 놓친 문제는 오케스트레이터가 수정본에 직접 추가해요.
4. 이후는 평소와 같아요: `--write-output`, `verify_quality_rereview.py`, 안정판 검증, 패키지,
   게임 적용, 보고서(분업 평가 표 포함), 진행 현황, 커밋.

**시험 운영에서 얻은 노하우**

- 워커의 수정 정확도는 높았어요(169키 중 되돌림 0, 보정 2). 약점은 번역투를 일부 놓치는 것이라
  패턴 검사와 표본 검토가 꼭 필요해요.
- 워커는 명령 결과 메시지를 `초기화: %s 님`처럼 줄여 쓰는 경향이 있어요. 완결된 문장으로 보정해요.
- 지시문의 번역투 목록(`성공적으로` 등)도 워커가 일부 놓쳐요(4순위에서 5키). 패턴 검사는 생략하지 않아요.
- 워커가 바꾼 이름은 `rg`로 퀘스트·다른 모드 사용처를 찾아요. 보정 파일(`recheck_overrides.json`)도
  작업 원본에 넣어야 해요.
- 워커가 여러 키에서 함께 쓰이는 단독 단어(예: XNet `low`/`high`)를 바꾸면 다른 화면이 깨질 수 있어요.
  단어 대신 그 단어를 쓰는 문장 쪽을 고쳐요.
- 이전 적용 뒤 커밋만 하고 적용하지 않은 변경이 있으면, 적용 대상을 마지막 적용 커밋 기준 차이로 골라요.
- 워커가 모드 안의 표기 통일(옵션→설정, 이름표→라벨 등)을 잘 찾아요. 모드 간에 걸리는 용어는
  보고의 `glossary_suggestions`를 보고 오케스트레이터가 용어집에 반영해요.
- 영어 원문 파일이 없는 키(구조물 이름 등)는 키 ID를 원문으로 보라고 지시해야 해요.
- 워커 지시에 금지를 적어도 읽기 전용 git 명령을 쓴 적이 있어요. 지시문에 "git 명령 일체 금지"를
  분명히 적었어요.
- 한 번 고친 키를 다시 고치는 경우(용어 교체 등) `quality_rereview_lang.py`는 작업 원본이 기준
  커밋 값이나 현재 산출물 값과 같으면 통과해요.
- 이름×단계처럼 규칙으로 만든 대량 키(압축 블록 등)는 워커에게 맡기지 않고, 원래 블록의 확정 이름과
  프로그램으로 대조해 불일치와 원본 없는 이름만 직접 읽어요(6순위).
- 번역 사전이 스크립트에 있는 가이드는 오케스트레이터가 사전을 고치고 생성 스크립트로 다시 만들어요.
  바뀐 가이드 파일은 범위 파일의 `guide_files`에 넣어야 누적·안정판 검증의 허용 경로가 돼요.
- 마크다운 가이드는 `guide__<네임스페이스>__<번호>.txt` 대조 파일(약 9만 바이트)로 워커 하나에 두 개쯤 맡기고,
  워커는 `{"old","new"}` 한 줄 조각만 내요. `quality_rereview_guides.py`가 검사·반영하며, 같은 조각이 여러 번
  나오는 용어 교체는 워커 대신 오케스트레이터가 `"all": true`로 일괄 처리해요(7순위).
- 워커끼리 용어 판단이 갈릴 만한 표기(`제작 격자` 등)는 부르기 전에 정해 지시에 적어요.
- 파일을 쓰는 스크립트는 LF(`newline="\n"`)로 써요. 섞인 줄바꿈 파일을 `git restore`로 되돌리면
  바이트가 달라져 단계1 해시 검증이 실패하니, 산출물 가이드 파일은 건드리지 않아요.

## 6. 진행 현황

| 단계 | 계열 순위 | 상태 |
|---|---|---|
| A | 1~6 | 1 완료(stable.8), 2 완료(1부 stable.9, 2부 stable.11), 3 완료(stable.12), 4 완료(stable.13), 5 완료(stable.14), 6 완료(stable.15) |
| 후속 | 1·2순위 용어 교체 | 완료(stable.10). `솔라리움`만 Ender IO 계열 때 교체 |
| B | 7~17 | 7 완료(stable.16), 8~17 미착수 |
| C | 18~30 | 미착수 |
| D | 31~39 | 미착수 |
| E | 40~41 | 미착수 |

### 계열별 기록

| 순위 | 계열 | 검수 범위 | 수정 | 유지 | 배포 | 보고 |
|---:|---|---|---:|---:|---|---|
| 1 | 팩 공통 진행 퀘스트 | 퀘스트 2,023키, 언어 67키, KubeJS 6파일 | 퀘스트 575, 언어 3, KubeJS 8줄 | 퀘스트 1,448, 언어 64 | 8.1-stable.8 | [보고](../versions/8.1/reports/quality_rereview_pack_progress.md) |
| 2 (1부) | 공통 UI: JEI·Jade·FTB 6종 | 언어 8개 2,197키 | 언어 142 | 언어 2,055 | 8.1-stable.9 | [보고](../versions/8.1/reports/quality_rereview_common_ui.md) |
| 1·2 후속 | 용어 기준 교체 | 범위 파일의 해당 표현 141곳 | 퀘스트 34, 언어 68, KubeJS 3줄 | 나머지 | 8.1-stable.10 | [보고](../versions/8.1/reports/quality_rereview_term_pass.md) |
| 2 (2부) | 공통 UI: 지도·장신구·웨이스톤·나침반 | 언어 5개 2,644키 | 언어 177 | 언어 2,467 | 8.1-stable.11 | [보고](../versions/8.1/reports/quality_rereview_common_ui_2.md) |
| 3 | Sophisticated 계열 | 언어 4개 1,137키 | 언어 112 | 언어 1,025 | 8.1-stable.12 | [보고](../versions/8.1/reports/quality_rereview_sophisticated.md) |
| 4 | 인벤토리·정보·가이드 UI | 언어 20개 2,443키 | 언어 210 | 언어 2,233 | 8.1-stable.13 | [보고](../versions/8.1/reports/quality_rereview_info_ui.md) |
| 5 | 초반 기반 도구·기계·물류 | 언어 20개 1,769키 | 언어 126, 퀘스트 5 | 언어 1,643 | 8.1-stable.14 | [보고](../versions/8.1/reports/quality_rereview_early_infra.md) |
| 후속 | 보류 용어 확정 | 보류 5개, 1~4순위 불확실 항목 | 언어 62 | — | 8.1-stable.14 | [보고](../versions/8.1/reports/quality_rereview_term_decisions.md) |
| 6 | Allthemodium·ATM 광물 | 언어 5개 2,662키, 안내서 47필드 | 언어 201, 안내서 4 | 언어 2,461 | 8.1-stable.15 | [보고](../versions/8.1/reports/quality_rereview_atm_ores.md) |
| 7 | Applied Energistics 2와 애드온 | 언어 17개 2,099키, 퀘스트 266키, 가이드 223파일 | 언어 42(+압축 27), 퀘스트 24, 가이드 129파일 263곳 | 언어 2,057, 퀘스트 242, 가이드 94파일 | 8.1-stable.16 | [보고](../versions/8.1/reports/quality_rereview_ae2.md) |

계열 작업 자료는 `working/quality_rereview/<계열>/`에 두고, 퀘스트 수정본은
`scripts/quality_rereview_quests.py <계열> --write-output`으로 산출물과 8.1 수동 검수 목록에
함께 반영해요. 언어 파일 수정본은 `scripts/quality_rereview_lang.py <계열> --write-output`으로
산출물과 `working/` 작업 원본에 반영해요. 배포 검증은 `scripts/verify_quality_rereview.py`가 완료된 계열을 누적 검사해요.

구 버전 배포본(`output/7.1`)은 별도 요청이 없으면 바꾸지 않아요.
