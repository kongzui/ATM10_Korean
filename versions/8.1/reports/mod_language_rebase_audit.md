# ATM10 8.1 모드 언어 재검토 감사

- 기존 번역 네임스페이스: 286개
- 변경 영향 네임스페이스: 55개
- 변경·신규 원문 검토 키: 2,141개
- 검토 키 중 현재 산출물에 없는 키: 860개
- 현재 영어 원문 전체에서 산출물에 없는 키: 2,980개
- 검토 키 중 영어 원문과 같은 산출물: 16개
- 현재 키 구조와 보호 문자열 검사가 끝난 영향 네임스페이스: 20개
- 그대로 재사용 가능한 키: 35,319개
- 현재 원문에서 제거된 키: 255개
- 자리표시자·서식 오류: 72개
- 신규 네임스페이스 후보: 11개 (4,779키)

## 변경 영향 네임스페이스

| 네임스페이스 | 검토 키 | 전체 누락 | 검토분 누락 | 영어 동일 | 변경 | 신규 | 제거 | 구조 준비 |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| supplementaries | 684 | 683 | 683 | 0 | 1 | 683 | 11 | 아니요 |
| mekmm | 144 | 0 | 0 | 0 | 0 | 144 | 0 | 예 |
| ftbquests | 135 | 0 | 0 | 3 | 0 | 135 | 23 | 예 |
| herbsandharvest | 112 | 0 | 0 | 0 | 7 | 105 | 92 | 예 |
| ars_nouveau | 103 | 0 | 0 | 2 | 0 | 103 | 0 | 아니요 |
| enderdrives | 99 | 0 | 0 | 0 | 0 | 99 | 1 | 예 |
| waystones | 99 | 0 | 0 | 4 | 4 | 95 | 0 | 예 |
| minecolonies | 81 | 0 | 0 | 0 | 0 | 81 | 0 | 예 |
| modern_industrialization | 76 | 0 | 0 | 0 | 0 | 76 | 0 | 아니요 |
| advancedperipherals | 73 | 0 | 0 | 0 | 11 | 62 | 18 | 예 |
| securitycraft | 67 | 0 | 0 | 0 | 13 | 54 | 11 | 예 |
| apotheosis | 48 | 1 | 0 | 0 | 3 | 45 | 6 | 아니요 |
| fancymenu | 44 | 0 | 0 | 1 | 23 | 21 | 20 | 예 |
| sodium-extra | 43 | 0 | 0 | 0 | 5 | 38 | 2 | 예 |
| jei | 40 | 0 | 0 | 0 | 7 | 33 | 26 | 예 |
| create_enchantment_industry | 27 | 27 | 27 | 0 | 0 | 27 | 0 | 아니요 |
| irons_spellbooks | 25 | 0 | 0 | 5 | 8 | 17 | 0 | 예 |
| eternal_starlight | 24 | 23 | 23 | 0 | 1 | 23 | 1 | 아니요 |
| tombstone | 24 | 20 | 20 | 0 | 4 | 20 | 13 | 아니요 |
| journeymap | 23 | 23 | 23 | 0 | 0 | 23 | 4 | 아니요 |
| sophisticatedstorage | 17 | 0 | 0 | 0 | 1 | 16 | 0 | 예 |
| ars_elemancy | 15 | 0 | 0 | 0 | 0 | 15 | 15 | 아니요 |
| apothic_enchanting | 10 | 0 | 0 | 1 | 0 | 10 | 0 | 예 |
| artifacts | 10 | 6 | 6 | 0 | 4 | 6 | 1 | 아니요 |
| sophisticatedbackpacks | 10 | 0 | 0 | 0 | 0 | 10 | 0 | 예 |
| create_hypertube | 9 | 9 | 9 | 0 | 0 | 9 | 0 | 아니요 |
| hostilenetworks | 8 | 8 | 8 | 0 | 0 | 8 | 0 | 아니요 |
| integratedtunnels | 8 | 8 | 8 | 0 | 0 | 8 | 0 | 아니요 |
| mffs | 8 | 7 | 7 | 0 | 1 | 7 | 2 | 아니요 |
| jei_mekanism_multiblocks | 7 | 0 | 0 | 0 | 0 | 7 | 0 | 예 |
| ftbteams | 6 | 5 | 5 | 0 | 1 | 5 | 0 | 아니요 |
| extended_industrialization | 5 | 0 | 0 | 0 | 0 | 5 | 0 | 예 |
| functionalstorage | 5 | 5 | 5 | 0 | 0 | 5 | 0 | 아니요 |
| generatorgalore | 5 | 5 | 5 | 0 | 0 | 5 | 0 | 아니요 |
| industrialforegoing | 5 | 5 | 5 | 0 | 0 | 5 | 0 | 아니요 |
| iris_search | 5 | 0 | 0 | 0 | 0 | 5 | 1 | 예 |
| modularbees | 5 | 5 | 5 | 0 | 0 | 5 | 0 | 아니요 |
| lootr | 4 | 4 | 4 | 0 | 0 | 4 | 0 | 아니요 |
| pneumaticcraft | 4 | 3 | 3 | 0 | 1 | 3 | 0 | 아니요 |
| quarryplus | 4 | 4 | 4 | 0 | 0 | 4 | 3 | 아니요 |
| sophisticatedcore | 4 | 0 | 0 | 0 | 1 | 3 | 0 | 예 |
| integratedterminals | 3 | 3 | 3 | 0 | 0 | 3 | 0 | 아니요 |
| irons_lib | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 예 |
| the_bumblezone | 3 | 2 | 2 | 0 | 1 | 2 | 0 | 아니요 |
| apothic_attributes | 2 | 1 | 0 | 0 | 0 | 2 | 0 | 아니요 |
| amendments | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 아니요 |
| createaddition | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 아니요 |
| integratedscripting | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 아니요 |
| oritech | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 아니요 |
| sfm | 1 | 1 | 1 | 0 | 0 | 1 | 4 | 아니요 |
| allthetweaks | 0 | 24 | 0 | 0 | 0 | 0 | 0 | 아니요 |
| dyenamicsandfriends | 0 | 1944 | 0 | 0 | 0 | 0 | 0 | 아니요 |
| modonomicon | 0 | 137 | 0 | 0 | 0 | 0 | 0 | 아니요 |
| patchouli | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 아니요 |
| pipez | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 아니요 |

## 신규 네임스페이스 후보

| 네임스페이스 | 영어 키 | 설치본 한국어 후보 |
|---|---:|---:|
| neovitae | 3053 | 0 |
| ad_astra | 831 | 414 |
| logisticsnetworks | 454 | 0 |
| ad_astra_giselle_addon | 168 | 162 |
| auroral | 148 | 0 |
| stepcrafter | 79 | 0 |
| borderless | 21 | 0 |
| moogs_structures | 14 | 0 |
| betteradvancedtooltips | 5 | 0 |
| common_storage_lib | 3 | 0 |
| invasiveopts | 3 | 0 |

## 자동 검사 주의 사항

- 현재 JAR 중복 원문 충돌 기록: 0개
- 기준 JAR 중복 원문 충돌 기록: 0개
- 실행 로그에서 로드된 버전과 다른 현재 CC:Tweaked JAR 제외: 1개
- 실행 로그에서 로드된 버전과 다른 기준 CC:Tweaked JAR 제외: 1개
- 현재 JAR 언어 파일 읽기 오류: 1개
- 기준 JAR 언어 파일 읽기 오류: 1개
- 자세한 키와 파일 경로는 같은 이름의 JSON 보고서에 기록했습니다.
