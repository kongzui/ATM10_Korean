# 기존 조사에서 별도 한국어 산출물이 없는 추가 후보

정리일: 2026-09-09. 원본은 보존된 `../manifests/jar_language_files.csv`예요.
기준은 8.1 최초 설치 조사이며 현재 설치 전체를 다시 읽은 결과가 아니에요.
현재 `output/8.1/resourcepack/ATM10_Korean/assets/*/lang/ko_kr.json`과 비교해,
영어 키가 있는 네임스페이스 중 별도 output과 신규 11개 후보에 속하지 않는 98개를 추렸어요.
이 목록은 **영어로 남는 98개 모드**라는 뜻이 아니에요. 네임스페이스와 모드는 1:1이 아니며
다른 네임스페이스·override의 번역, 내장 한국어, 사용하지 않는 설정·예제가 포함될 수 있어요.
이름과 키 수만 보고 신규 번역 파일을 만들지 않아요. 계열 작업 시작 때 현재 JAR과 소비 경로를 확인해요.

## 처리 순서

1. 콘텐츠·조작 후보: 실제 사용 중인 아이템·기계·블록의 표시와 기존 계열 검수 기록부터 확인해요.
2. UI 후보: 공통 화면에서 자주 보이는 영어를 먼저 확인해요.
3. 나머지: 라이브러리·설정·내부 표시 여부를 분류하고 필요한 것만 번역해요.
아래 분류는 조사 우선순위이며 확정된 기능 분류나 미번역 판정이 아니에요.
키 수는 조사 CSV 값이고, 한국어 키가 있어도 프로젝트 검수 완료로 표시하지 않아요.

| 조사 순위 | 네임스페이스 | 영어 키 | JAR 한국어 후보 |
|---|---|---:|---:|
| 1 콘텐츠·조작 | `storagedelight` | 178 | 91 |
| 1 콘텐츠·조작 | `utilitarian` | 111 | 0 |
| 1 콘텐츠·조작 | `bridgingmod` | 96 | 0 |
| 1 콘텐츠·조작 | `comforts` | 83 | 83 |
| 1 콘텐츠·조작 | `chromacarvings` | 65 | 0 |
| 1 콘텐츠·조작 | `solcarrot` | 60 | 60 |
| 1 콘텐츠·조작 | `crystalix` | 59 | 0 |
| 1 콘텐츠·조작 | `dimstorage` | 36 | 34 |
| 1 콘텐츠·조작 | `utilityvest` | 36 | 0 |
| 1 콘텐츠·조작 | `dysoncubeproject` | 34 | 0 |
| 1 콘텐츠·조작 | `trashcans` | 34 | 32 |
| 1 콘텐츠·조작 | `torchmaster` | 32 | 12 |
| 1 콘텐츠·조작 | `elevatorid` | 29 | 24 |
| 1 콘텐츠·조작 | `entangled` | 24 | 21 |
| 1 콘텐츠·조작 | `wirelesschargers` | 23 | 23 |
| 1 콘텐츠·조작 | `potionsmaster` | 15 | 0 |
| 1 콘텐츠·조작 | `crafting_on_a_stick` | 14 | 13 |
| 1 콘텐츠·조작 | `shrink` | 12 | 0 |
| 1 콘텐츠·조작 | `cobblegengalore` | 10 | 0 |
| 1 콘텐츠·조작 | `laserbridges` | 9 | 0 |
| 1 콘텐츠·조작 | `rangedpumps` | 9 | 9 |
| 1 콘텐츠·조작 | `sawmill` | 8 | 0 |
| 1 콘텐츠·조작 | `treetap` | 8 | 0 |
| 1 콘텐츠·조작 | `charginggadgets` | 5 | 5 |
| 1 콘텐츠·조작 | `cosmeticarmorreworked` | 5 | 5 |
| 1 콘텐츠·조작 | `fireproofboats` | 4 | 0 |
| 1 콘텐츠·조작 | `tiab` | 4 | 0 |
| 1 콘텐츠·조작 | `disenchanting_table` | 2 | 0 |
| 1 콘텐츠·조작 | `multipiston` | 2 | 0 |
| 2 UI | `ftblibrary` | 113 | 0 |
| 2 UI | `notenoughanimations` | 107 | 0 |
| 2 UI | `drippyloadingscreen` | 46 | 0 |
| 2 UI | `justzoom` | 29 | 0 |
| 2 UI | `keybindbundles` | 26 | 0 |
| 2 UI | `darkmodeeverywhere` | 24 | 0 |
| 2 UI | `justenoughbreeding` | 22 | 0 |
| 2 UI | `simple_weather` | 19 | 0 |
| 2 UI | `measurements` | 15 | 0 |
| 2 UI | `colorfulhearts` | 14 | 0 |
| 2 UI | `memorysettings` | 8 | 0 |
| 2 UI | `crashutilities` | 4 | 0 |
| 2 UI | `keybindspurger` | 4 | 0 |
| 2 UI | `bcc` | 2 | 0 |
| 2 UI | `toastcontrol` | 2 | 0 |
| 2 UI | `justenoughprofessions` | 1 | 0 |
| 2 UI | `smithingtemplateviewer` | 1 | 0 |
| 3 표시 경로 분류 | `bookshelf` | 208 | 0 |
| 3 표시 경로 분류 | `modernfix` | 155 | 0 |
| 3 표시 경로 분류 | `shiny` | 137 | 0 |
| 3 표시 경로 분류 | `moonlight` | 136 | 0 |
| 3 표시 경로 분류 | `nochatreports` | 129 | 129 |
| 3 표시 경로 분류 | `brandonscore` | 102 | 0 |
| 3 표시 경로 분류 | `ctov` | 74 | 74 |
| 3 표시 경로 분류 | `titanium` | 53 | 0 |
| 3 표시 경로 분류 | `cloth-config2` | 49 | 49 |
| 3 표시 경로 분류 | `jupiter` | 45 | 0 |
| 3 표시 경로 분류 | `neo_auth` | 45 | 0 |
| 3 표시 경로 분류 | `cyclopscore` | 42 | 0 |
| 3 표시 경로 분류 | `simplebackups` | 40 | 0 |
| 3 표시 경로 분류 | `balm` | 36 | 0 |
| 3 표시 경로 분류 | `formations` | 35 | 0 |
| 3 표시 경로 분류 | `observable` | 34 | 0 |
| 3 표시 경로 분류 | `resourcefulconfig` | 28 | 0 |
| 3 표시 경로 분류 | `mostructures` | 27 | 0 |
| 3 표시 경로 분류 | `yet_another_config_lib_v3` | 26 | 0 |
| 3 표시 경로 분류 | `owo` | 25 | 0 |
| 3 표시 경로 분류 | `colorwheel` | 22 | 0 |
| 3 표시 경로 분류 | `transfer_labels` | 21 | 0 |
| 3 표시 경로 분류 | `bwncr` | 18 | 0 |
| 3 표시 경로 분류 | `codechickenlib` | 18 | 0 |
| 3 표시 경로 분류 | `cloudglass` | 17 | 0 |
| 3 표시 경로 분류 | `oracle_index` | 17 | 0 |
| 3 표시 경로 분류 | `cucumber` | 16 | 12 |
| 3 표시 경로 분류 | `polylib` | 13 | 0 |
| 3 표시 경로 분류 | `trophymanager` | 13 | 0 |
| 3 표시 경로 분류 | `restrictions` | 12 | 0 |
| 3 표시 경로 분류 | `camol` | 10 | 0 |
| 3 표시 경로 분류 | `commoncapabilities` | 10 | 0 |
| 3 표시 경로 분류 | `fusion` | 8 | 0 |
| 3 표시 경로 분류 | `ctm` | 7 | 0 |
| 3 표시 경로 분류 | `dummmmmmy` | 7 | 7 |
| 3 표시 경로 분류 | `fastbench` | 7 | 0 |
| 3 표시 경로 분류 | `almostunified` | 6 | 0 |
| 3 표시 경로 분류 | `placebo` | 6 | 6 |
| 3 표시 경로 분류 | `cristellib` | 4 | 0 |
| 3 표시 경로 분류 | `getittogetherdrops` | 4 | 0 |
| 3 표시 경로 분류 | `kubejstweaks` | 4 | 0 |
| 3 표시 경로 분류 | `lionfishapi` | 4 | 0 |
| 3 표시 경로 분류 | `tesseract_api` | 4 | 0 |
| 3 표시 경로 분류 | `imfast` | 3 | 0 |
| 3 표시 경로 분류 | `mcjtylib` | 3 | 0 |
| 3 표시 경로 분류 | `caelus` | 2 | 1 |
| 3 표시 경로 분류 | `terrablender` | 2 | 0 |
| 3 표시 경로 분류 | `wstweaks` | 2 | 2 |
| 3 표시 경로 분류 | `hardenedarmadillos` | 1 | 0 |
| 3 표시 경로 분류 | `repeatable_trial_vaults` | 1 | 0 |
| 3 표시 경로 분류 | `searchables` | 1 | 1 |
| 3 표시 경로 분류 | `supermartijn642corelib` | 1 | 0 |

기존 완료 계열의 이름이 이 표에 다시 나타나면 해당 검수 보고서와 다른 언어 파일 제공 여부를
먼저 확인해요. 단순 파일 부재를 번역 손실로 판단하지 않아요. 전체 진행 순서는
[누적 업데이트 로드맵](../../../docs/ATM10_VERSION_TRANSLATION_UPGRADE_PLAN.md)을 따라요.
