# ATM10 버전 및 한국어 번역 업그레이드 계획

작성일: 2026-08-31

현재 상태: 사전 검토 완료, 본PC 실행 보류

현재 기준 버전: ATM10 7.1

현재 목표 버전: ATM10 8.1

## 1. 결론

- 게임팩은 `7.2`, `7.3`, `8.0`을 차례대로 설치할 필요 없이, 별도의 새 `8.1` 인스턴스를
  만들어 직접 옮긴다.
- 기존 `7.1` 인스턴스와 월드는 그대로 보존한다. `8.1`에서 열 때는 반드시 복사한 월드를
  사용한다.
- 한국어 번역은 중간 버전별 산출물을 따로 만들지 않고 `7.1`과 최종 `8.1` 원문을 직접
  비교해 누적 차이를 반영한다. 다만 중간 버전 변경 기록은 삭제·이름 변경·퀘스트 개편을
  빠뜨리지 않기 위한 참고 자료로 사용한다.
- 현재 `output/` 전체를 `8.1`에 바로 적용하면 안 된다. 기존 적용 스크립트는 파일을 통째로
  복사하므로, 일부 FTB Quests와 KubeJS 파일을 `7.1` 상태로 되돌릴 수 있다.
- 실제 실행 직전에 최신 정식판을 다시 확인한다. 그때 `8.2` 또는 `8.1.x`가 나왔다면 이
  문서의 목표 버전과 차이 조사를 최신판 기준으로 갱신한다.

## 2. 사전 검토에서 확인한 사실

| 항목 | 현재 7.1 기준 | 최신 8.1 기준 | 판단 |
| --- | --- | --- | --- |
| 배포일 | 2026-06-26 | 2026-08-29 | 네 번의 정식판 차이가 있음 |
| Minecraft | 1.21.1 | 1.21.1 | 월드 형식의 큰 세대 변경은 아님 |
| NeoForge | 21.1.234 | 21.1.249 | 로더와 모드 호환성 재검증 필요 |
| 모드 JAR | 480개 | 새 인스턴스에서 재조사 필요 | 기존 목록을 그대로 믿지 않음 |
| 건너뛴 정식판 | 없음 | 7.2, 7.3, 8.0, 8.1 | 누적 차이로 처리 |

공식 네 번의 변경 기록을 합치면 다음과 같다.

- 모드 추가 14건
- 모드 업데이트 280건, 고유 모드 164개
- 모드 제거 1건: Reap Mod
- 현재 프로젝트가 번역한 네임스페이스와 자동으로 연결되는 업데이트 대상은 최소 90개다.
  이름이 다른 모드를 보수적으로 제외한 수치이므로 실제 재검수 대상은 더 많다.
- 현재 누적 산출물은 리소스팩 파일 2,291개와 실제 override 파일 263개다.
- override 263개 중 243개가 KubeJS 아래에 있으므로 전체 복사 전에 원문 충돌 검사가
  필요하다.

### 새로 추가된 모드

- 7.2: CodecUI, Invasive Optimizations
- 8.0: Auroral, Borderless Window, Neo Vitae, Overlapless
- 8.1: Ad Astra, Ad Astra: Giselle Addon, Apollib, Common Storage Lib 3종,
  LogisticsNetworks, Step Crafter

`8.1` 배포 설명에는 Ad Astra가 우선 추가됐고 전용 퀘스트와 팩 조정은 이후에 들어올
예정이라고 적혀 있다. 따라서 이번 번역 갱신에서는 Ad Astra 본체 언어를 먼저 확인하고,
퀘스트는 실제 `8.1` 인스턴스에 있는 것만 처리한다.

### 이미 확인된 원문 충돌 경로

공식 GitHub의 `8.1` 변경 기록 생성 시점과 현재 `7.1` 원본을 대조했을 때 다음 파일은
최신 원문에서 실제 구조나 내용이 바뀌었다.

| 경로 | 확인된 차이 | 처리 원칙 |
| --- | ---: | --- |
| `config/ftbquests/quests/chapters/cataclysm.snbt` | 약 396개 줄 단위 변경 | 8.1 원본에서 한국어 변경만 다시 적용 |
| `config/ftbquests/quests/chapters/relics.snbt` | 약 176개 줄 단위 변경 | 8.1 원본에서 한국어 변경만 다시 적용 |
| `kubejs/client_scripts/tooltips.js` | 약 61개 줄 단위 변경 | 8.1 스크립트 기준으로 번역 부분만 이식 |
| `kubejs/server_scripts/announcements/announcements.js` | 약 21개 줄 단위 변경 | 최신 공지 구조를 보존해 재번역 |
| `kubejs/startup_scripts/CustomAdditions.js` | 소규모 원문 변경 | 새 아이템·등록 구조를 보존해 재번역 |

다음 세 파일은 공식 GitHub의 같은 시점에 동일 경로가 없었다. 프로젝트 전용 파일일 수
있으므로 새 CurseForge `8.1` 인스턴스에서 실제 존재 여부를 다시 확인한다.

- `config/ftbquests/quests/lang/ko_kr.snbt`
- `kubejs/startup_scripts/appleskin_debug_labels.js`
- `kubejs/startup_scripts/mousetweaks_config_labels.js`

`ko_kr.snbt`가 새 인스턴스에 있든 없든, 기존 7.1 파일을 그대로 복사하지 않는다. 최신
`en_us.snbt`, 챕터 구조, Task와 fallback 표시 경로를 기준으로 키를 다시 맞춘다.

## 3. 절대 지킬 안전 경계

1. 기존 `7.1` 인스턴스는 업데이트 대상으로 쓰지 않고 읽기 전용 보관본으로 둔다.
2. 기존 월드를 `8.1`로 직접 열지 않는다. 백업 후 복제한 월드만 시험한다.
3. `mods/`, `config/`, `kubejs/`를 예전 인스턴스에서 새 인스턴스로 통째로 복사하지 않는다.
4. 원본 JAR은 읽기만 하고 수정·재압축·교체하지 않는다.
5. `local_paths.json`을 새 경로로 바꾸기 전에 경로가 정확한 새 인스턴스인지 확인한다.
6. 재기준화가 끝나기 전에는 `python scripts/apply_translations.py` 전체 적용을 실행하지 않는다.
7. Minecraft 또는 Java가 실행 중이면 적용을 중단한다.
8. 실제 게임 적용 전에는 반드시 dry-run, 백업, 대상 경로 확인을 수행한다.
9. Git에는 월드, JAR, 로그, 캐시, 다운로드한 모드팩 ZIP을 넣지 않는다.

## 4. 작업 범위

### 포함

- ATM10 `7.1`에서 최종 정식판으로 게임 인스턴스 이동
- 설치 모드와 버전 차이 조사
- 기존 리소스팩 언어 파일의 전체 재검수
- 새 모드의 사용자 표시 언어 조사와 번역
- FTB Quests의 챕터·퀘스트·Task·설명·fallback 제목 재검수
- KubeJS의 언어 파일과 직접 표시 문자열 재검수
- GuideME, Patchouli, Modonomicon 등 가이드 표시 경로 재검수
- 기존 검증 스크립트의 버전 가정 갱신
- 새 테스트 인스턴스 적용과 게임 실행 확인

### 제외

- 기존 `7.1` 원본 인스턴스 수정
- 원본 월드 덮어쓰기
- 원본 모드 JAR 수정
- 번역과 관계없는 게임 밸런스·조합법·설정 변경
- 아직 실제 `8.1`에 없는 미래 Ad Astra 퀘스트의 추측 번역
- 사용자 확인 없는 Git push

## 5. 실행 단계

### 단계 0. 실행 직전 목표 버전 재확인

- [ ] CurseForge 정식 파일 목록에서 최신 Release 버전을 확인한다.
- [ ] 공식 GitHub 변경 기록과 최신 공개 이슈를 확인한다.
- [ ] 최신판이 `8.1`이면 이 계획을 그대로 사용한다.
- [ ] 더 새 정식판이 있으면 새 버전까지의 변경 기록을 추가하고 목표 버전을 바꾼다.
- [ ] 새 버전이 막 배포됐고 치명적 문제가 보고됐다면 한 번의 수정판을 기다릴지 결정한다.

현재 `8.1`은 조사일 기준 이틀 전에 나온 정식판이다. 공식 이슈에는 Ad Astra: Giselle Addon과
중첩 Sophisticated Backpack의 작은 성능 상호작용이 보고됐고, 애드온 `8.3`에서 수정됐다는
후속 설명이 있다. 본PC 작업 시점에 이 수정이 ATM10에 포함됐는지 다시 확인한다.

### 단계 1. 7.1 기준 보존

- [ ] `local_paths.json`이 가리키는 기존 원본의 `manifest.json` 버전이 7.1인지 확인한다.
- [ ] 기존 인스턴스의 `saves/`, `resourcepacks/`, 사용자 지도·설정 자료를 별도 백업한다.
- [ ] 월드 폴더의 파일 수, 크기, 수정 시각과 해시 기록을 남긴다.
- [ ] 저장소가 깨끗한지 확인하고 현재 번역 기준 커밋을 기록한다.
- [ ] 기존 7.1 인스턴스 이름에 `보관` 또는 `읽기 전용` 표시를 붙인다.

현재 노트북 검토 기준은 다음과 같다.

- `manifest.json`: ATM10 7.1, Minecraft 1.21.1, NeoForge 21.1.234
- JAR: 480개, 총 1,386,726,155바이트
- JAR 이름 목록 SHA-256:
  `ae90640a6df38a9ad1e25bd771cf45430618f702f773fe2f1bfe70e223eee37a`
- 저장소 기준 커밋: `5011ad5 Inventory Tweaks 번역 전수 재검수`

### 단계 2. 새 8.1 인스턴스 준비

- [ ] CurseForge에서 기존 프로필을 직접 갱신하지 않고 새 `8.1` 프로필을 만든다.
- [ ] 새 인스턴스를 번역팩 없이 한 번 실행해 기본 파일 생성을 확인한다.
- [ ] 메인 메뉴까지 정상 진입하고 종료한다.
- [ ] `latest.log`에서 모드 로딩 실패, 누락 레지스트리, 데이터팩 오류를 확인한다.
- [ ] 새 인스턴스를 복제해 하나는 깨끗한 기준본, 하나는 번역 시험본으로 둔다.
- [ ] `source_root`는 깨끗한 기준본, `game_root`는 번역 시험본으로 설정한다.
- [ ] 경로 설정 후 두 인스턴스의 `manifest.json`이 모두 목표 버전인지 확인한다.

월드를 옮길 때는 다음 순서를 사용한다.

1. 기존 월드를 닫은 상태에서 백업한다.
2. 백업본을 새 시험 인스턴스의 `saves/`로 복사한다.
3. 원본 월드는 그대로 남긴다.
4. 복사본을 열기 전에 로그와 누락 모드 목록을 확인한다.
5. 첫 실행 후 청크, 퀘스트, 아이템, 저장소와 주요 자동화 설비를 점검한다.
6. 문제가 있으면 새 복사본에서 다시 시험하고 원본을 열지 않는다.

### 단계 3. 7.1과 8.1 원문 차이 조사

- [ ] 새 `source_root`에서 `python scripts/discover.py`를 실행한다.
- [ ] 기존 Git 커밋의 7.1 매니페스트와 새 조사 결과를 비교한다.
- [ ] 추가·제거·업데이트된 JAR을 확정한다.
- [ ] 각 JAR의 영어·한국어 언어 파일 위치, 네임스페이스와 키 수를 다시 센다.
- [ ] 영어 키의 추가·삭제·이름 변경·자료형 변경을 구분한다.
- [ ] 자리표시자, 줄바꿈과 서식 코드 변경을 별도 목록으로 만든다.
- [ ] FTB Quests의 챕터 수, 영어 키, 자동 제목과 fallback 표시 경로를 다시 조사한다.
- [ ] KubeJS의 언어 JSON과 직접 표시 문자열 후보를 다시 조사한다.
- [ ] GuideME·Patchouli·Modonomicon 페이지 변경과 같은 경로 충돌을 조사한다.
- [ ] 조사 결과를 `reports/`와 `manifests/`에 저장하되 JAR이나 대용량 원본은 저장하지 않는다.

이 단계의 완료 산출물은 최소한 다음 내용을 포함한다.

- 버전과 로더 정보
- 추가·제거·업데이트 모드 목록
- 번역된 네임스페이스별 영어 키 차이
- FTB Quests 챕터·키·fallback 차이
- KubeJS와 가이드 변경 경로
- 기존 output과 새 원문이 충돌하는 파일 목록
- 처리하지 못한 파일과 오류 목록

### 단계 4. 적용 스크립트와 검증기의 버전 가정 점검

- [ ] 정확한 JAR 이름을 상수로 고정한 검증기를 찾는다.
- [ ] 새 버전에서도 파일명 패턴으로 안전하게 하나의 JAR만 찾는지 확인한다.
- [ ] 버전 자체가 검증 목적이면 새 버전으로 명시적으로 갱신한다.
- [ ] 단순히 파일을 찾기 위한 정확한 버전 고정은 안전한 패턴 탐색으로 바꾼다.
- [ ] 여러 JAR이 잡히면 임의 선택하지 않고 오류로 중단한다.
- [ ] 수정한 Python 파일만 Ruff와 관련 검증을 실행한다.

현재 확인된 버전 고정 예시는 다음과 같다.

- `scripts/verify_appleskin.py`
- `scripts/verify_betteradvancements.py`
- `scripts/verify_bumblezone_family.py`
- `scripts/verify_akashictome.py`
- `scripts/verify_ae2_translation.py`

모든 스크립트를 한꺼번에 리팩터링하지 않는다. 실제 변경 모드의 검증을 막는 항목만 해당
작업 단위에서 수정한다.

### 단계 5. 리소스팩 번역 재기준화

모드별 작업은 기존 규칙대로 약 100~200개 키 또는 하나의 독립 모드 계열로 나눈다.

- [ ] 새 `en_us` 전체와 기존 프로젝트 `ko_kr` 전체를 키별로 비교한다.
- [ ] 변경되지 않은 영어 키는 기존 검수 번역을 재사용한다.
- [ ] 영어 값이 바뀐 키는 기존 한국어가 자연스러워 보여도 다시 검토한다.
- [ ] 새 키는 원문·용어집·게임 표시 경로를 확인해 새로 번역한다.
- [ ] 삭제된 키는 다른 소비자와 호환성 필요 여부를 확인한 뒤 처리한다.
- [ ] 자리표시자, 줄바꿈, 색상 코드와 자료형을 원문과 대조한다.
- [ ] 한 모드의 일반 언어, 퀘스트, KubeJS와 가이드를 한 작업 범위에서 함께 확인한다.
- [ ] 검증 가능한 모드 또는 계열마다 독립 커밋한다.

우선순위는 다음과 같다.

1. 새 콘텐츠: Neo Vitae, Ad Astra, LogisticsNetworks, Step Crafter, Auroral
2. 퀘스트가 크게 바뀐 계열: Cataclysm, Relics, Apotheosis, Hostile Neural Networks,
   Eternal Starlight, Iron's Spells, Occultism, Pylons
3. 여러 번 업데이트된 완료 계열: Sophisticated 계열, Supplementaries, Waystones, Ars Nouveau,
   Occultism, JourneyMap, MineColonies, Modern Industrialization
4. AE2 애드온: AE2WTLib, ExtendedAE, Advanced AE, EnderDrives, AE2 Import Export Card
5. UI·라이브러리·소규모 모드

### 단계 6. FTB Quests 재기준화

- [ ] 새 8.1 챕터와 `en_us.snbt`를 권위 원본으로 사용한다.
- [ ] 기존 7.1 챕터 전체를 8.1 위에 덮어쓰지 않는다.
- [ ] 기존 한국어를 ID와 키 기준으로 이식한다.
- [ ] 새 퀘스트, 삭제된 퀘스트, 바뀐 Task와 의존 관계를 따로 확인한다.
- [ ] `chapter/group title`, `quest title`, `subtitle`, `description`, `task title`,
  아이템 hover 이름, `custom_name`과 첫 Task fallback을 모두 확인한다.
- [ ] 단일 아이템 Task의 중복 `task.title`은 최신 정책에 맞게 제거한다.
- [ ] 퀘스트 제목과 리소스팩의 확정 아이템 이름을 일치시킨다.
- [ ] Cataclysm과 Relics 챕터는 가장 먼저 8.1 원본 기반으로 다시 만든다.

중간 버전 변경 기록에서 확인된 주요 퀘스트 범위는 다음과 같다.

- 7.2: Cataclysm, Occultism, Pylons, Relics, Undergarden, Apotheosis Gem Case,
  Draconic Evolution, Hostile Neural Networks, AE2 Meteorite
- 7.3: Hostile Neural Networks, Eternal Starlight, Apotheosis 대규모 역이식
- 8.0: Neo Vitae 신규 퀘스트, Relics 형식 변경, Iron's Spells 퀘스트 변경
- 8.1: Auroral, Glowing Hellshelf, Tome of Extraction, Hellfire Forge 관련 변경

### 단계 7. KubeJS와 기타 override 재기준화

- [ ] 8.1 원본과 동일 경로인 파일은 반드시 8.1 파일에서 시작한다.
- [ ] 한국어 표시 문구만 다시 이식하고 조합법·태그·등록·밸런스 로직은 보존한다.
- [ ] `tooltips.js`, `announcements.js`, `CustomAdditions.js`를 우선 처리한다.
- [ ] 프로젝트 전용 AppleSkin·Mouse Tweaks 라벨 스크립트는 새 KubeJS에서 다시 실행 검증한다.
- [ ] 리소스팩 언어 파일로 옮길 수 있는 문구는 가능한 한 override 전체 복사를 줄인다.
- [ ] 바이너리 NBT와 번역과 무관한 데이터 파일은 변경이 없으면 다시 만들지 않는다.
- [ ] 최신 원문에 없는 파일은 필요한 프로젝트 추가 파일인지, 제거된 옛 파일인지 구분한다.

### 단계 8. 자동 검증

각 작업 단위에서 다음 검증을 모두 통과해야 한다.

- [ ] JSON 문법, 중복 키와 최상위 자료형 검사
- [ ] SNBT 문법과 구조 검사
- [ ] 영어·한국어 키 수와 누락·추가 키 검사
- [ ] `%s`, `%1$s`, `%d`, `{0}` 같은 자리표시자 보존 검사
- [ ] 줄바꿈, 색상 코드, URL, 숫자와 이스케이프 문자 보존 검사
- [ ] 퀘스트 제목·Task 제목·fallback 표시 경로 검사
- [ ] 관련 가이드와 KubeJS 직접 문자열 검사
- [ ] 수정한 Python 파일의 `ruff format .`과 `ruff check .`
- [ ] `git diff --check`
- [ ] 원본 JAR과 기준 인스턴스의 작업 전후 스냅샷 비교

### 단계 9. 시험 적용

- [ ] Java와 Minecraft가 종료됐는지 확인한다.
- [ ] 처음에는 `--path`로 재기준화가 끝난 파일만 선택해 dry-run한다.
- [ ] 예상 변경 경로가 선택 범위와 정확히 같은지 확인한다.
- [ ] 시험 인스턴스에만 적용하고 백업 매니페스트를 남긴다.
- [ ] 적용 후 같은 dry-run을 다시 실행해 `expected_changes: []`를 확인한다.
- [ ] 메인 메뉴, 새 시험 월드와 복제 월드에서 한국어 표시를 확인한다.
- [ ] 로그의 JSON, SNBT, KubeJS, 리소스팩 로딩 오류를 확인한다.
- [ ] 주요 JEI 검색, 퀘스트 화면, 가이드, 툴팁과 설정 화면을 확인한다.

다음 조건 전에는 전체 적용을 허용하지 않는다.

- Cataclysm·Relics 최신 챕터 재기준화 완료
- 최신 `ko_kr.snbt` 키·fallback 검사 완료
- `tooltips.js`, `announcements.js`, `CustomAdditions.js` 재기준화 완료
- 변경된 번역 네임스페이스 전체 검수 완료 또는 보류 목록 확정
- 새 모드의 번역 필요 여부 조사 완료
- 모든 자동 검증 통과

### 단계 10. 월드 복제본 검증과 최종 적용

- [ ] 복제 월드 로딩 전 마지막 백업을 만든다.
- [ ] 누락 블록·아이템·엔티티 경고를 확인한다.
- [ ] AE2, Sophisticated Storage, Create, Mekanism과 주요 자동화 설비를 확인한다.
- [ ] FTB Quests 진행도, 완료 표시와 보상 상태를 확인한다.
- [ ] 새 차원·구조물은 기존 청크가 아닌 새 청크에서 생성되는지 확인한다.
- [ ] 최소 한 번의 정상 저장·종료·재실행을 확인한다.
- [ ] 문제가 없을 때만 실제 플레이 인스턴스에 같은 검증 산출물을 적용한다.
- [ ] 적용 경로, 변경 파일 수, 백업 경로와 최종 해시를 기록한다.

## 6. 커밋 단위

작업은 다음처럼 독립적으로 되돌릴 수 있게 나눈다.

1. 8.1 원본 조사와 버전 검증기 호환성
2. FTB Quests·KubeJS 충돌 파일 재기준화
3. 새 모드 번역
4. 변경된 기존 모드의 계열별 재검수
5. 퀘스트·가이드·fallback 후속 검수
6. README와 버전·진행 문서 갱신

각 번역 커밋은 관련 검증을 통과한 뒤에만 만들고 push는 하지 않는다. 계획서나 진행 문서는
해당 문서 변경을 명시적으로 포함한 커밋에서만 스테이징한다.

## 7. 완료 조건

- [ ] 목표 ATM10 정식판과 Minecraft·NeoForge 버전이 문서와 일치한다.
- [ ] 기존 7.1 인스턴스와 원본 월드가 변경되지 않았다.
- [ ] 새 인스턴스의 전체 모드·언어·퀘스트·KubeJS 조사가 완료됐다.
- [ ] 업데이트된 번역 모드 전체를 새 영어 원문과 대조했다.
- [ ] 새 모드의 번역 완료 또는 명시적 보류 사유가 기록됐다.
- [ ] Cataclysm·Relics와 모든 원문 충돌 override를 최신 파일 기반으로 다시 만들었다.
- [ ] FTB Quests의 명시적 키와 자동 fallback 표시를 모두 검증했다.
- [ ] JSON·SNBT·자리표시자·서식·Ruff·Git 검사가 모두 통과했다.
- [ ] 시험 인스턴스 적용 후 계획 밖 변경이 없었다.
- [ ] 복제 월드가 정상 로딩·저장·재실행됐다.
- [ ] 실제 적용 경로, 백업, 파일 수, 커밋과 남은 검토 항목을 보고했다.

## 8. 현재 보류 사항

- 노트북에는 실제 `8.1` CurseForge 인스턴스가 없으므로 정확한 8.1 JAR·퀘스트·KubeJS
  파일 비교는 본PC에서 새 인스턴스를 만든 뒤 확정한다.
- 현재 `game_root`가 설정되지 않아 실제 게임 적용은 하지 않는다.
- 최신판이 배포된 지 얼마 되지 않았으므로 본PC 작업 시작 시 수정판 유무를 다시 확인한다.
- 이번 작업에서는 계획서만 만들며 번역 파일, 실제 인스턴스와 원본 JAR은 수정하지 않는다.

## 9. 공식 참고 자료

- [ATM10 CurseForge 정식 파일 목록](https://www.curseforge.com/minecraft/modpacks/all-the-mods-10/files/all)
- [ATM10 8.1 파일](https://www.curseforge.com/minecraft/modpacks/all-the-mods-10/files/8764211)
- [공식 전체 변경 기록](https://github.com/AllTheMods/ATM-10/blob/main/CHANGELOG.md)
- [7.1 → 7.2 변경 기록](https://github.com/AllTheMods/ATM-10/blob/main/changelogs/CHANGELOG-ATM10-7.1-7.2.md)
- [7.2 → 7.3 변경 기록](https://github.com/AllTheMods/ATM-10/blob/main/changelogs/CHANGELOG-ATM10-7.2-7.3.md)
- [7.3 → 8.0 변경 기록](https://github.com/AllTheMods/ATM-10/blob/main/changelogs/CHANGELOG-ATM10-7.3-8.0.md)
- [8.0 → 8.1 변경 기록](https://github.com/AllTheMods/ATM-10/blob/main/changelogs/CHANGELOG-ATM10-8.0-8.1.md)
- [8.1 Giselle Addon 성능 상호작용 보고](https://github.com/AllTheMods/ATM-10/issues/4364)
