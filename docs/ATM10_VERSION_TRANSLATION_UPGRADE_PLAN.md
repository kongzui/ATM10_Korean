# ATM10 7.1 → 8.1 번역 업그레이드 계획

작성일: 2026-08-31

현재 상태: 8.1 첫 실행·원본 조사·버전별 저장소 구조 준비 완료, 번역 재기준화 전

- 기준 버전: ATM10 7.1
- 목표 버전: ATM10 8.1

## 1. 결론

- 7.2, 7.3, 8.0을 따로 설치하지 않고 7.1과 설치된 8.1을 직접 비교한다.
- 8.1 프로필은 현재 설치한 하나만 사용한다. 8GB짜리 프로필을 두 개 만들 필요는 없다.
- 원본 조회와 시험 적용 모두 현재 8.1 프로필을 사용하되, 적용 전 백업과 파일별 선택 적용으로
  안전을 확보한다.
- 게임 인스턴스의 `mods/`, `config/`, `kubejs/`, 월드와 로그를 저장소로 복사하지 않는다.
  저장소에는 번역 작업 파일, 검증된 산출물, 작은 조사 목록과 보고서만 둔다.
- `working/`은 공용 작업 공간으로 유지하되, 완성 산출물은 `output/7.1/`과 `output/8.1/`로
  물리적으로 분리한다.
- `output/7.1/`은 검증 완료본으로 고정하고, 같은 내용에서 시작한 `output/8.1/`만 현재
  원문에 재기준화한다.
- `output/8.1/release.json`에서 전체 적용을 차단한다. 8.1 원문에 다시 맞춘 파일만 `--path`로
  선택 적용하고, 모든 재검수가 끝난 뒤에만 전체 적용을 허용한다.

현재 로컬 경로는 다음처럼 사용한다.

```json
{
  "source_root": null,
  "game_root": "C:/Users/moon9/curseforge/minecraft/Instances/All the Mods 10 - ATM10 (1)"
}
```

`source_root`는 나중에 별도의 깨끗한 기준 프로필이 정말 필요할 때만 선택적으로 설정한다.

## 2. 버전 업그레이드를 고려한 저장소 구조

```text
ATM10_Korean/
├─ version_context.json          현재 기준 버전·목표 버전·버전 작업 공간
├─ local_paths.json              이 PC의 실제 인스턴스 경로, Git 제외
├─ versions/
│  ├─ 7.1/
│  │  ├─ version.json
│  │  ├─ manifests/              당시 설치·언어·퀘스트 조사 결과
│  │  └─ reports/                당시 검증 보고서
│  └─ 8.1/
│     ├─ version.json
│     ├─ manifests/              8.1 재조사 결과
│     ├─ reports/                7.1 비교·첫 실행·검증 보고서
│     └─ conflicts/              자동 이식할 수 없는 충돌 기록
├─ working/                      현재 번역 작업 파일
├─ output/
│  ├─ 7.1/
│  │  ├─ release.json            7.1 검증 완료 상태
│  │  ├─ resourcepack/           7.1 리소스팩 완성본
│  │  └─ overrides/              7.1 덮어쓰기 완성본
│  └─ 8.1/
│     ├─ release.json            8.1 재기준화·전체 적용 차단 상태
│     ├─ resourcepack/           8.1 리소스팩 작업본
│     └─ overrides/              8.1 덮어쓰기 작업본
├─ glossary/                     공통 용어
├─ scripts/                      조사·빌드·검증·적용 도구
└─ temp/                         재생성 가능한 임시 파일과 적용 백업, Git 제외
```

이 구조에서 9.0으로 올라갈 때는 `versions/9.0/`과 `output/9.0/`을 추가한다. 새 output은 직전
검증 완료본을 복사해 시작하며, `release.json`에서 전체 적용을 막은 상태로 현재 원문에 다시
맞춘다. 조사·빌드·검증·적용 스크립트는 `version_context.json`의 활성 버전 output만 사용한다.

## 3. 실제 7.1과 8.1 비교 결과

| 항목 | 7.1 | 8.1 | 처리 |
| --- | ---: | ---: | --- |
| Minecraft | 1.21.1 | 1.21.1 | 같은 게임 세대지만 모드·로더 재검증 |
| NeoForge | 21.1.234 | 21.1.249 | 스크립트·리소스 로딩 확인 |
| 실제 JAR | 481개 | 488개 | JAR은 읽기만 함 |
| 영어 언어 네임스페이스 | 389개 | 398개 | 원문 해시와 키 재비교 |
| 모드 자체 한국어 네임스페이스 | 152개 | 154개 | 정답이 아니라 검수 후보로 사용 |
| FTB Quests 챕터 | 64개 | 66개 | 8.1 분할 언어 구조로 이식 |

CurseForge 설치 메타데이터 기준 모드는 추가 11개, 제거 4개, 업데이트 157개, 동일 323개다.
JAR 자체를 읽는 데 실패한 파일은 없지만, Macaw's Trapdoors JAR 내부
`assets/mcwtrpdoors/lang/ko_kr.json`에는 쉼표가 빠진 원본 문법 오류가 1개 있다. 프로젝트
리소스팩으로 해당 언어를 만들 때 8.1 영어 원문을 기준으로 해결하고 원본 JAR은 수정하지 않는다.

### 추가된 모드와 새 번역 후보

- Ad Astra (`ad_astra`)
- Ad Astra: Giselle Addon (`ad_astra_giselle_addon`)
- Auroral (`auroral`)
- Better Advanced Tooltips (`betteradvancedtooltips`)
- Borderless Window (`borderless`)
- Common Storage Lib (`common_storage_lib`)
- Invasive Optimizations (`invasiveopts`)
- Logistics Network (`logisticsnetworks`)
- Neo Vitae (`neovitae`)
- Step Crafter (`stepcrafter`)
- StructureOverlapless (`moogs_structures`)

### 제거된 모드

- Modern UI
- Reap Mod
- Untranslated Items
- UntranslatedItems: AlsoFluidsAndChemicals

현재 output에는 제거된 Modern UI용 글꼴 파일이 하나 남아 있다. 8.1 화면에서 필요 소비자가
없는지 확인한 뒤 8.1 재기준화 작업 단위에서 제거 여부를 결정한다.

7.1 보존본의 Herbs and Harvest 가이드 파일 `grapes.json`과 `herbs.json`에는 문서 뒤쪽에
중복 닫기 구조가 있어 일반 JSON 파서가 실패한다. 이번 구조 변경에서 새로 생긴 오류는 아니며,
8.1 복사본에도 그대로 있으므로 Herbs and Harvest 재검수 때 현재 원본에서 다시 만든다.

### 영어 원문이 바뀐 기존 번역 네임스페이스 54개

다음 네임스페이스는 기존 한국어가 있어도 8.1 영어 전체와 다시 대조한다.

`advancedperipherals`, `amendments`, `apotheosis`, `apothic_attributes`,
`apothic_enchanting`, `ars_elemancy`, `ars_nouveau`, `artifacts`,
`create_enchantment_industry`, `create_hypertube`, `createaddition`, `enderdrives`,
`eternal_starlight`, `extended_industrialization`, `fancymenu`, `ftbquests`, `ftbteams`,
`functionalstorage`, `generatorgalore`, `glassential`, `herbsandharvest`, `hostilenetworks`,
`industrialforegoing`, `integratedscripting`, `integratedterminals`, `integratedtunnels`,
`iris_search`, `irons_lib`, `irons_spellbooks`, `jei`, `jei_mekanism_multiblocks`,
`journeymap`, `lootr`, `mekmm`, `mffs`, `minecolonies`, `mininggadgets`,
`modern_industrialization`, `modularbees`, `oritech`, `pipez`, `pneumaticcraft`,
`quarryplus`, `securitycraft`, `sfm`, `sodium-extra`, `sophisticatedbackpacks`,
`sophisticatedcore`, `sophisticatedstorage`, `structurize`, `supplementaries`,
`the_bumblezone`, `tombstone`, `waystones`

영어 원문 해시가 그대로인 기존 번역은 전부 다시 번역하지 않는다. 키·용어·게임 화면의 빠른
검수만 하고 재사용한다.

## 4. 가장 큰 구조 변경: FTB Quests

7.1은 `config/ftbquests/quests/lang/en_us.snbt`와 `ko_kr.snbt`를 사용했지만, 8.1은
`lang/en_us/...`와 `lang/ko_kr/...` 아래의 여러 파일을 사용한다.

- 8.1 영어 분할 파일: 70개
- 8.1 한국어 분할 파일: 59개
- 한국어에 없는 영어 파일: 14개
- 영어에 없는 옛 한국어 파일: 3개

한국어에 없는 파일은 다음과 같다.

- `chapters/aether.snbt`
- `chapters/apotheosis_gear.snbt`
- `chapters/auroral.snbt`
- `chapters/deeper_and_darker.snbt`
- `chapters/draconic_evolution.snbt`
- `chapters/extended__advanced_ae.snbt`
- `chapters/ice__fire.snbt`
- `chapters/mi_digital.snbt`
- `chapters/mi_electric.snbt`
- `chapters/mi_endgame.snbt`
- `chapters/mi_steam.snbt`
- `chapters/neo_vitae.snbt`
- `chapters/oritech.snbt`
- `chapters/refined_storage.snbt`

영어에 없는 한국어 파일은 다음과 같다. 이름이 바뀐 챕터인지 폐기된 파일인지 먼저 확인한다.

- `chapters/rust_free_and_oiled.snbt`
- `chapters/steam_age.snbt`
- `chapters/the_electric_age.snbt`

기존 스크립트 48개가 단일 `ko_kr.snbt` 경로를 직접 사용한다. 이 48개를 한꺼번에 바꾸면
검증 범위가 너무 넓어지므로 다음 원칙을 사용한다.

1. 공용 `scripts/ftbquests_layout.py`로 병합형·분할형 경로를 판정한다.
2. 먼저 FTB Quests 공통 빌드·감사 도구를 분할형에 맞춘다.
3. 각 모드를 재번역할 때 그 모드의 가족 스크립트만 공용 도우미로 옮긴다.
4. 새 output은
   `output/8.1/overrides/config/ftbquests/quests/lang/ko_kr/<상대 경로>`에 둔다.
5. 기존 `output/7.1/.../lang/ko_kr.snbt`는 8.1에 적용하지 않는다.

## 5. 8.1 재번역 작업 순서

### 단계 0. 첫 실행 기준 만들기 — 완료

- [x] 새 8.1 프로필 설치
- [x] 번역팩 없이 한 번 실행하고 정상 종료
- [x] KubeJS 시작 스크립트 19개와 클라이언트 스크립트 15개 로드 확인
- [x] KubeJS 오류·경고 0개 확인
- [x] 실행 전후 번역 원본 중 `kubejs/config/common.json`만 바뀐 것을 확인
- [x] 종료 후 Minecraft·Java 프로세스가 없는 것을 확인

번역 적용 전부터 있던 Sodium Extra, Jupiter, JEI 설정, 설정 로딩 시점, Silent Gear 모델 경고는
`versions/8.1/reports/first_launch.md`에 기준 오류로 기록했다. 번역 후에는 새로 생긴 오류만
회귀로 판단한다.

### 단계 1. 버전별 저장소 구조와 적용 안전장치 — 완료

- [x] `version_context.json`에서 기준 7.1과 목표 8.1 지정
- [x] 7.1 조사 자료를 `versions/7.1/`로 이동
- [x] 8.1 조사·비교·첫 실행 기록을 `versions/8.1/`에 생성
- [x] 7.1 산출물을 `output/7.1/{resourcepack,overrides}`로 보존
- [x] 같은 파일을 `output/8.1/{resourcepack,overrides}` 작업본으로 복사
- [x] `output/8.1/release.json`에서 8.1 전체 적용 차단
- [x] 모든 산출물 스크립트를 활성 버전 output 경로로 전환
- [x] `local_paths.json`을 현재 8.1 프로필로 변경
- [x] 조사 결과 기본 출력 위치를 활성 버전 폴더로 변경

### 단계 2. FTB Quests 분할 구조부터 이식

- [ ] 공통 SNBT 빌드·감사·제목 fallback 검증기가 분할 파일을 읽고 쓰게 한다.
- [ ] 14개 누락 챕터를 영어 원문과 기존 검수 번역으로 대조한다.
- [ ] 3개 한국어 전용 챕터의 이름 변경·폐기 여부를 확인한다.
- [ ] `chapter/group title`, `quest title`, `subtitle`, `description`, `task title`,
  아이템 hover 이름, `custom_name`과 첫 Task fallback을 모두 확인한다.
- [ ] 단일 아이템 Task의 불필요한 중복 `task.title`을 제거한다.
- [ ] 퀘스트 제목을 프로젝트 리소스팩의 확정 아이템 이름과 일치시킨다.

이 단계를 먼저 하는 이유는 이후 모드별 번역이 퀘스트 파일을 잘못된 7.1 단일 파일에 합치는
것을 막기 위해서다.

### 단계 3. 원문과 충돌하는 override 재기준화

8.1 작업본 override 263개 중 8.1 같은 경로와 내용이 다른 파일은 43개이고, 8.1 원본에 같은
경로가 없는 파일은 220개다. `target_missing`은 곧바로 삭제한다는 뜻이 아니라 프로젝트가 새로
추가한 번역 파일인지, 7.1에만 필요한 낡은 파일인지 분류해야 한다는 뜻이다.

먼저 다음 파일을 8.1 원본에서 다시 만든다.

- FTB Quests 원본과 다른 챕터 6개: Cataclysm, Generators, Mekanism, MI Digital,
  MI Electric, Relics
- `kubejs/client_scripts/tooltips.js`
- `kubejs/server_scripts/announcements/announcements.js`
- `kubejs/startup_scripts/CustomAdditions.js`

처리 원칙은 8.1 파일을 기준으로 한국어 표시 부분만 이식하고 조합법, 태그, 등록, 밸런스와
실행 로직은 그대로 보존하는 것이다.

### 단계 4. 새 모드 번역

다음 순서로 일반 언어 파일뿐 아니라 관련 퀘스트·KubeJS·가이드도 함께 조사한다.

1. 퀘스트가 있는 Auroral, Neo Vitae
2. 콘텐츠가 큰 Ad Astra, Ad Astra: Giselle Addon
3. Logistics Network, Step Crafter
4. Better Advanced Tooltips, Borderless Window
5. Common Storage Lib, Invasive Optimizations, StructureOverlapless

라이브러리나 최적화 모드처럼 실제 사용자 표시 문자열이 거의 없으면 번역 파일을 억지로 만들지
않고 조사 완료로 기록한다.

### 단계 5. 영어가 바뀐 기존 번역 54개 재검수

한 번에 전부 섞지 않고 다음 우선순위로 모드 계열별 작업 단위를 만든다.

1. 퀘스트·진행 영향이 큰 계열: FTB Quests, Apotheosis·Artifacts, Iron's Spells,
   AE2 애드온, Modern Industrialization, Cataclysm·Relics, Hostile Neural Networks,
   Eternal Starlight
2. 자주 쓰는 콘텐츠: Sophisticated 계열, Ars Nouveau, Industrial Foregoing,
   PneumaticCraft, MineColonies·Structurize, Integrated 계열, JourneyMap·FTB Teams,
   Pipez·Functional Storage
3. UI·보조·소규모: JEI 계열, Sodium Extra, FancyMenu, Waystones, Supplementaries와 나머지

각 계열에서 다음을 반복한다.

1. 8.1 JAR의 `en_us` 전체와 기존 프로젝트 `ko_kr` 전체를 비교한다.
2. 영어가 같은 키는 검수된 기존 번역을 재사용한다.
3. 영어 값이 바뀐 키는 다시 번역하고, 새 키는 새로 번역한다.
4. 삭제된 키는 다른 소비자가 없는지 확인한 뒤 정리한다.
5. 관련 FTB Quests, KubeJS, GuideME·Patchouli·Modonomicon, 발전 과제를 함께 확인한다.
6. JSON·SNBT·자리표시자·서식과 가족별 검증을 통과한 뒤 선택 적용하고 커밋한다.

### 단계 6. 변경 없는 번역과 제거 모드 정리

- [ ] 영어 해시가 같은 기존 번역은 키·용어·게임 표시만 빠르게 확인한다.
- [ ] 제거 모드 전용 산출물이 다른 모드에서도 필요한지 확인한다.
- [ ] 필요 없는 Modern UI 전용 파일과 7.1 전용 FTB 파일을 별도 검증 단위로 정리한다.
- [ ] 새 8.1 원문에 없는 KubeJS 파일은 프로젝트 추가 파일인지 낡은 파일인지 분류한다.
- [ ] Herbs and Harvest의 `grapes.json`, `herbs.json`을 8.1 원본 기준으로 다시 만든다.

### 단계 7. 자동 검증과 파일별 시험 적용

각 모드 계열에서 다음 검사를 통과해야 한다.

- JSON·SNBT 문법, 중복 키와 자료형
- 영어·한국어 키 수와 누락·추가 키
- `%s`, `%1$s`, `%d`, `{0}` 자리표시자
- 줄바꿈, 색상 코드, URL, 숫자와 이스케이프 문자
- 퀘스트 제목·Task 제목·fallback 표시 경로
- 관련 KubeJS 직접 문자열과 가이드
- 수정한 Python 파일의 Ruff
- `git diff --check`
- 실제 인스턴스의 적용 전후 스냅샷

Minecraft와 Java가 종료된 상태에서 다음처럼 검증 완료 파일만 적용한다.

```powershell
python scripts/apply_translations.py --dry-run `
  --path "resourcepacks/ATM10_Korean/assets/<modid>/lang/ko_kr.json"

python scripts/apply_translations.py `
  --path "resourcepacks/ATM10_Korean/assets/<modid>/lang/ko_kr.json"
```

### 단계 8. 게임 화면 검증과 전체 적용 해제

- [ ] 메인 메뉴와 새 시험 월드에서 리소스팩 로딩 오류가 없는지 확인한다.
- [ ] JEI 검색, 퀘스트 화면, 가이드, 툴팁과 설정 화면을 확인한다.
- [ ] 복제 월드에서 누락 블록·아이템·엔티티와 퀘스트 진행도를 확인한다.
- [ ] 정상 저장·종료·재실행을 확인한다.
- [ ] 전체 재기준화 완료 후 `output/8.1/release.json`을 검증 완료 상태로 바꾼다.
- [ ] 마지막 전체 dry-run과 적용 후 계획 밖 변경이 없는지 확인한다.

## 6. 월드 처리

기존 7.1 월드는 저장소 구조 정리나 번역 조사와 별개다. 실제로 8.1에서 플레이할 때만 다음
순서를 사용한다.

1. Minecraft를 완전히 종료한다.
2. 7.1 월드를 별도 백업한다.
3. 백업 복사본만 8.1 `saves/`에 넣는다.
4. 첫 로딩 전 로그와 제거 모드 목록을 확인한다.
5. 복사본에서 주요 저장소, 기계, 퀘스트와 새 청크 생성을 점검한다.
6. 문제가 있으면 원본을 열지 않고 새 복사본으로 다시 시험한다.

## 7. 커밋 단위

1. 버전별 구조·조사·안전장치
2. FTB Quests 분할 구조 호환
3. 충돌 FTB Quests·KubeJS 재기준화
4. 새 모드별 번역
5. 변경된 기존 모드의 계열별 재검수
6. 제거·변경 없는 모드 정리와 최종 8.1 배포 표시

각 번역 단위는 관련 검증을 모두 통과했을 때만 커밋하고 push는 하지 않는다.

## 8. 전체 완료 조건

- [x] 설치된 8.1의 Minecraft·NeoForge·모드·언어·퀘스트 조사가 끝났다.
- [x] 7.1과 8.1의 모드·영어 원문·override 충돌 목록을 만들었다.
- [x] 8.1 첫 실행 기준 로그를 남겼다.
- [ ] FTB Quests 분할 언어 구조로 모든 필요한 번역을 이식했다.
- [ ] 새 모드의 번역 완료 또는 번역 불필요 사유를 기록했다.
- [ ] 영어가 바뀐 기존 번역 54개를 현재 원문과 대조했다.
- [ ] 모든 원문 충돌 override를 8.1 파일에서 다시 만들었다.
- [ ] JSON·SNBT·자리표시자·서식·Ruff·Git 검사가 통과했다.
- [ ] 파일별 시험 적용과 실제 화면 확인이 끝났다.
- [ ] `output/8.1/release.json`을 8.1 전체 적용 가능 상태로 전환했다.

현재는 구조 정리와 조사까지만 완료했으며, 번역 파일은 아직 8.1에 적용하지 않았다.
