# ATM10 8.1 번역 업그레이드 진행 현황

기준일: 2026-09-09. 원문·키 수는 이전 호환판 감사 기록을 유지해요.

## 배포 방식

현재 배포는 Auroral·Neo Vitae·Ad Astra·Logistics Networks·Step Crafter 번역을 더하고
보조 번역 실행 코드를 제외한 `8.1-stable.6`과 `7.1-stable.1`이에요.
일반 언어·퀘스트·가이드·ATM10 원래 스크립트 번역은 유지해요. 프로젝트가 추가한 보조 파일
네 개는 주석만 있는 파일로 교체해 기존 설치의 실행 코드를 비활성화해요.
보조 제외 범위는 `docs/AUXILIARY_TRANSLATION_SCRIPTS.md`, 최초 안정판 근거는
`stable_release.md`, 현재 추가 범위는 `ad_astra_completion.md`를 확인해요.
에이전트는 이번 안정판을 실제 인스턴스에 적용하지 않았어요. 사용자가 직접 설치한 뒤
정상 작동을 확인했어요. 버전별·화면별 확인 목록은 없으며 전체 기능 검증으로 확대하지 않아요.

## 완료한 범위

- 버전별 산출물 분리, 8.1 원문 조사, FTB Quests 분할 언어 이식과 KubeJS 갱신
- 기존 MI, Sophisticated, Apotheosis, Ars Nouveau, Iron's Spells, SecurityCraft,
  CC:Tweaked, Mekanism, Herbs and Harvest, MineColonies, Waystones, EnderDrives,
  클라이언트 UI, JEI, Create, Eternal Starlight, FTB Teams, Supplementaries·Amendments 작업 유지
- 기존 모드 신규·변경분 누락 111키 번역 및 기존 값 10키 교정
- 가이드 JSON 2개 중복 닫기 제거, 빌드·검증기 재발 방지, Modern UI 전용 글꼴 제외
- Cataclysm·Relics 챕터의 낡은 구조 수정 및 챕터 6개 현재 원본 구조 대조
- PneumaticCraft 가이드의 경험치 흡수·차원 이동·새 차원 조건 위젯 반영
- 리소스팩 메타데이터를 8.1로 갱신하고 설치 가능한 ZIP 패키징 도구 추가

## 유지한 번역과 이전 원문 검증 수치

- 모드 언어 파일 286개, 전체 값 147,388개
- 7.1과 값이 같은 재사용 항목 145,208개. 이번에 새로 번역한 수가 아니라 누적 재사용 수예요.
- 기존 모드의 현재 신규·변경 영어 키 중 번역 누락 0개, 기존 유효 번역 키 손실 0개
- JSON·메타데이터 1,761개, SNBT 76개, JavaScript 27개 문법 검사 통과
- 자리표시자·서식·줄바꿈 오류 0개, Tempad 특수 텍스트 컴포넌트 10개 구조 확인
- 리소스·가이드·데이터 출처 검토 2,274개, 퀘스트 구조 6개·작물/등급 설정 13개 대조
- FTB Quests 번역 8,858키, 의도적 자동 제목 생략 64키 유지
- 글꼴 참조 3개 정상, 현재 사용하는 TTF의 한글 음절 11,172자 포함 확인

초기 보호 문자열 경고 69건 중 67건은 강조 문구 또는 `%%`와 순번 자리표시자 순서에 대한
검사 오탐이었어요. 실제 내용·줄바꿈 변경 2건은 번역을 수정했고, 오탐은 범위를 좁혀
검증기를 보완했어요. 숫자 자리표시자와 비순번 인자 순서는 계속 검사해요.

## 후속 업데이트

- 신규 11개 네임스페이스 후보, 4,779키: Neo Vitae, Ad Astra와 애드온, Logistics Network,
  Auroral, Step Crafter, Borderless, Better Advanced Tooltips, Moog's Structures,
  Common Storage Lib, Invasive Optimizations
- 기존 산출물부터 없던 영어 키 2,120개: 버전업 누락과 구분하며, 현재 모드 자체 번역이나
  다른 네임스페이스를 통한 표시를 먼저 확인해요.
- 기존 감사 밖의 별도 output 없는 98개 네임스페이스를 `additional_namespace_backlog.md`에
  추가 조사 후보로 정리했어요. 내장 번역·다른 표시 경로를 확인하기 전 미번역으로 확정하지 않아요.
- 퀘스트 제목 감사는 작업 전 1,210개, 실제 적용 후 1,098개 후보를 반환해요. 정상적인 자동
  아이템명, 공식 모드명·저작권 표기와 기존 이름 불일치가 섞여 있어 실제 오류 수가 아니에요.
  전체 번역 품질 개선을 호환판의 새 번역 누락과 혼동하지 않아요.
- 이전 수정판에서 EnderDrives Java 문자열 처리 오류가 추가로 확인돼 보조 실행 코드를 제외했어요.
  사용자가 안정판 정상 작동을 확인했으며, 각 모드·화면의 세부 검수는 후속 작업에서 기록해요.

현재 작업 순서는 [누적 업데이트 로드맵](../../../docs/ATM10_VERSION_TRANSLATION_UPGRADE_PLAN.md),
모드별 후보 수는 [번역 현황](../../../docs/MOD_TRANSLATION_PLAN.md)을 확인해요.
현재 배포 근거는 `stable_release.md`, 자동 검증은 `stable_validation.json`, ZIP 목록은
`../manifests/8.1-stable.1_packages.json`이에요. `compat_*`는 이전 배포의 이력이에요.
현재 실행 후 원문과의 대조 실패 기록은 `current_instance_compat_audit.json`에 남아 있으며,
다음 번역 변경 시 새 원문 검증을 해야 해요. 사용자 정상 작동 확인으로 이 기록을 지우지 않아요.

## 2026-09-13 · Auroral 누적 stable.2

- 일반 언어 148키: 신규 한국어 146, 공식 이름 유지 2, 기존 일반 언어 재사용 0.
- GuideME 29페이지 번역, 현재 JAR의 한국어 리소스 탐색 경로 확인.
- 기존 퀘스트 46키 검수: 용어·제목 수정 34, 그대로 재사용 12. 관련 KubeJS 표시 문구 추가 없음.
- 현재 원문·검수 기록·보호 문자열 대조 및 전체 JSON 1,762/SNBT 76/JS 27개 문법 검사 통과.
- 기존 2,633파일 해시 보존, 실제 인스턴스 변경 없음. ZIP 루트·CRC·파일 내용 검사 통과.
- 보고서: `8.1-stable.2_stable_validation.json`; ZIP 목록: `../manifests/8.1-stable.2_packages.json`.
- 사용자가 ZIP을 설치해요. 새 게임 화면 확인은 대기 중이며 Neo Vitae는 다음 누적 배포로 진행해요.

## 2026-09-13 · Neo Vitae 누적 stable.3 · 이번 작업 종료

- 현재 JAR 영어 3,053키 검수: 새 한국어 2,953키, 고유명사·단위 유지 100키.
- 책의 직접 문구 61키 추가: 한국어 49키, 이름 유지 12키. 최종 언어 파일 3,114키.
- 책 JSON 223개와 참조 언어 1,529키, 직접 문자열의 현재 Modonomicon 처리 경로 검증.
- 기존 퀘스트 105키 중 66키의 용어·제목 수정, 39키 재사용. 구조와 진행 조건 유지.
- KubeJS 추가 표시 문구 변경 없음. 보조 번역 실행 코드와 7.1 산출물은 이전 상태 유지.
- 전체 문법·보호 문자열·현재 원문·범위·ZIP 무결성 검사와 Python Ruff 검사 통과.
- 보고서: `8.1-stable.3_stable_validation.json`; ZIP 목록: `../manifests/8.1-stable.3_packages.json`.
- [Neo Vitae 완료 보고](../../../docs/archive/reports/8.1/neovitae_completion.md)에 원문 설명 차이와 처리 근거 기록.
- 실제 인스턴스에 적용하지 않았어요. 새 번역의 게임 화면 확인은 사용자 설치 후 진행해요.
- 사용자의 이번 작업 단위까지만 완료하라는 지시에 따라 단계 2 이후는 시작하지 않아요.

## 2026-09-26 · Ad Astra 계열 누적 stable.4

- 다음 계열 요청에 따라 Ad Astra와 Giselle Addon의 일반 언어 999키를 검수했어요.
  현재 JAR 후보 재사용 421·교정 155·신규 한국어 393·후보 없는 원문 표기 유지 30키예요.
- Astrodux 35파일·99페이지·165문구를 현재 영어 구조로 작성했어요.
  후보 재사용 42·교정 56·신규 한국어 65·원문 고유명사 유지 2문구예요.
- 현재 퀘스트 구조 66챕터에 관련 참조가 없고 KubeJS는 제작법·태그 참조뿐이므로 변경하지 않았어요.
- 전체 JSON 1,800/SNBT 76/JS 27개와 언어·가이드 보호 문자열, 기존 파일 해시,
  ZIP 두 개의 CRC·내용, 저장소 전체 Ruff 검사를 통과했어요.
- 커밋 단위: 언어 `2e589ee`, 가이드·관련 표시 경로 `43b5f70`, 이후 stable.4 배포·적용 기록.
- 기존 스크립트로 폴더팩의 이번 번역 37파일만 적용했고, 그 외 파일과 options.txt는 보존했어요.
  현재 활성 팩은 stable.1 ZIP이므로 누적 stable.4 ZIP을 활성화해야 해요. 게임 화면은 미검증이에요.
- [완료 보고](../../../docs/archive/reports/8.1/ad_astra_completion.md), `ad_astra_apply.json`,
  `8.1-stable.4_stable_validation.json`과 `../manifests/8.1-stable.4_packages.json`에 근거를 남겨요.
- Logistics Network 이후는 시작하지 않았어요.

## 2026-09-27 · Logistics Networks 누적 stable.5

- 이전 계획서 3개와 작업 관련 Markdown 자동 커밋 규칙을 `9228eea`로 커밋했어요.
- 현재 영어 454키 전체를 검수해 `7aac04a`로 커밋했어요. 가이드 등록 2키를 추가한 최종
  언어 파일은 456키이며 신규 한국어 436·기존 한국어 재사용 0·원문 유지 20키예요.
- GuideME 17페이지와 이름·설명, 원문 앵커·fallback 표시 경로를 `6fbd2b1`로 커밋했어요.
- FTB Quests 1,000파일·66챕터와 KubeJS 871파일에서 관련 참조는 없었어요. override는 같아요.
- 누적 JSON 1,802/SNBT 76/JS 27개 검증과 ZIP 두 개의 CRC·전체 내용 대조를 통과했어요.
- 게임 종료 상태에서 19개 파일만 `game_root`의 폴더팩에 적용했고 범위 밖 변경은 없어요.
  개인 설정은 보존했어요. 선택된 팩은 stable.1 ZIP이므로 새 팩 활성화와 실제 화면 확인이 남아 있어요.
- [완료 보고](../../../docs/archive/reports/8.1/logisticsnetworks_completion.md), [가이드 근거](../../../docs/archive/reports/8.1/logisticsnetworks_guide.md),
  [전체 검증](8.1-stable.5_stable_validation.json), [패키지 목록](../manifests/8.1-stable.5_packages.json)에 기록해요.
- 이번 작업은 여기서 종료해요. 다음 대상은 Step Crafter 79키예요.

## 2026-09-27 · Step Crafter 누적 stable.6

- 현재 0.1.8 영어 79키 전체를 번역·검수하고 `8a670aa`로 커밋했어요.
- 신규 한국어 78키·기존 한국어 재사용 0키·공식 모드명 원문 유지 1키예요.
- 별도 가이드는 없고, 색상 제작법 발전 과제 48파일에 표시 문구가 없어요.
- FTB Quests 1,000파일·66챕터와 KubeJS 871파일에 관련 참조가 없어 수정하지 않았어요.
- 전체 JSON 1,803/SNBT 76/JavaScript 27개와 기존 번역 보존 검사를 통과했어요.
- stable.6 ZIP 두 개의 루트·CRC·전체 내용 해시를 확인했어요. override는 stable.5와 같아요.
- 게임 종료 상태에서 언어 1파일만 `game_root` 폴더팩에 적용했어요. 범위 밖 변경과 개인 설정
  변경은 없어요. 현재 활성 팩은 stable.1 ZIP이므로 새 팩 활성화와 실제 화면 확인이 남아 있어요.
- [완료 보고](../../../docs/archive/reports/8.1/stepcrafter_completion.md), [전체 검증](8.1-stable.6_stable_validation.json),
  [패키지 목록](../manifests/8.1-stable.6_packages.json), [적용 기록](stepcrafter_apply.json)을 남겼어요.
- 단계 2의 파일 작업을 마쳤어요. 다음 대상은 Better Advanced Tooltips 5키예요.

## 2026-09-28 · Better Advanced Tooltips 누적 stable.7

- 현재 영어 설정 5키를 모두 신규 번역했어요. 기존 한국어 재사용은 0키예요.
- 별도 가이드와 FTB Quests·KubeJS 관련 참조는 없어요. `Fuel:`과 오류 안내는 코드 직접 표시로
  확인해 원문 유지 항목으로 기록했어요. 보조 번역 코드는 추가하지 않았어요.
- 전체 JSON 1,804/SNBT 76/JavaScript 27개, 기존 번역 보존, ZIP 두 개의 CRC·전체 내용 검사를 통과했어요.
- 원본 6,365파일의 조사 전후 상태가 같았고, 게임 종료 상태에서 새 언어 파일 1개만 적용했어요.
  범위 밖 파일과 개인 설정은 보존했어요. 선택 팩은 stable.1이므로 새 팩 활성화가 필요해요.
- [완료 보고](../../../docs/archive/reports/8.1/betteradvancedtooltips_completion.md), [배포 안내](../../../docs/archive/releases/8.1-stable.7.md),
  [패키지 목록](../manifests/8.1-stable.7_packages.json)에 근거를 남겨요.
- 실제 게임 화면은 미검증이에요. 다음 대상은 Borderless Window 21키예요.

## 2026-09-29 · 품질 재검수 1순위 누적 stable.8

- 팩 공통 진행 퀘스트 19파일 2,023키를 현재 영어와 다시 대조해 575키를 고치고 1,448키를 유지했어요.
- 언어 5개 네임스페이스 67키 중 3키, KubeJS 2파일 8줄을 고쳤어요. 신규 번역은 없어요.
- 전체 JSON 1,804/SNBT 76/JavaScript 27개, 재검수 누적 검증, ZIP 두 개의 CRC·전체 내용 검사를 통과했어요.
- 게임 종료 상태에서 23파일만 선택 적용했고 예상 밖 변경과 개인 설정 변경은 없었어요.
- [재검수 보고](quality_rereview_pack_progress.md), [배포 안내](../../../docs/archive/releases/8.1-stable.8.md),
  [패키지 목록](../manifests/8.1-stable.8_packages.json)에 근거를 남겨요.
- 실제 게임 화면은 미검증이에요. 다음은 재검수 2순위 공통 UI예요.

## 2026-09-29 · 품질 재검수 2순위 1부 누적 stable.9

- JEI·Jade·FTB Quests·Chunks·Teams·Ultimine·Essentials·Filter System 언어 2,197키를 다시 대조해
  142키를 고치고 2,055키를 유지했어요. 퀘스트·KubeJS·신규 번역 변경은 없어요.
- 재검수 누적 검증, 안정판 검증, ZIP 두 개의 CRC·전체 내용 검사를 통과했어요.
- 게임 종료 상태에서 언어 7파일과 pack.mcmeta만 선택 적용했고 예상 밖 변경은 없었어요.
- [재검수 보고](quality_rereview_common_ui.md), [배포 안내](../../../docs/archive/releases/8.1-stable.9.md),
  [패키지 목록](../manifests/8.1-stable.9_packages.json)에 근거를 남겨요.
- 실제 게임 화면은 미검증이에요. 다음은 2순위 2부(JourneyMap·Curios·Waystones·나침반)예요.

## 2026-09-29 · 1·2순위 용어 교체 누적 stable.10

- 새 용어 기준(스폰·엔티티·쿨타임·생물 군계·단축 바·키 지정)을 1순위 퀘스트 34키·KubeJS 3줄과
  2순위 1부 언어 68키에 반영했어요. 신규 번역은 없어요.
- 재검수 누적 검증, 안정판 검증, ZIP 두 개의 CRC·전체 내용 검사를 통과했어요.
- 게임 종료 상태에서 17파일만 선택 적용했고 예상 밖 변경은 없었어요. 표시 경로 감사 4개를 갱신했어요.
- [용어 교체 보고](quality_rereview_term_pass.md), [배포 안내](../../../docs/archive/releases/8.1-stable.10.md),
  [패키지 목록](../manifests/8.1-stable.10_packages.json)에 근거를 남겨요.
- 실제 게임 화면은 미검증이에요. 다음은 2순위 2부(JourneyMap·Curios·Waystones·나침반)예요.

## 2026-09-29 · 품질 재검수 2순위 2부 누적 stable.11

- JourneyMap·Curios·Waystones·Nature's Compass·Explorer's Compass 언어 2,644키를 다시 대조해 177키를
  고치고 2,467키를 유지했어요. Opus·Sonnet 분업 시험 운영으로 진행했고 신규 번역은 없어요.
- 재검수 누적 검증, 안정판 검증, ZIP 두 개의 CRC·전체 내용 검사를 통과했어요.
- 게임 종료 상태에서 언어 5파일과 pack.mcmeta만 선택 적용했고 예상 밖 변경은 없었어요.
- [재검수 보고](quality_rereview_common_ui_2.md), [배포 안내](../../../docs/archive/releases/8.1-stable.11.md),
  [패키지 목록](../manifests/8.1-stable.11_packages.json)에 근거를 남겨요.
- 실제 게임 화면은 미검증이에요. 다음은 3순위 Sophisticated 계열이에요.

## 2026-09-29 · 품질 재검수 3순위 누적 stable.12

- Sophisticated Core·Backpacks·Storage·Storage In Motion 언어 1,137키를 다시 대조해 112키를 고치고
  1,025키를 유지했어요. Sonnet 워커 분업으로 진행했고 신규 번역은 없어요.
- 재검수 누적 검증, 안정판 검증, ZIP 두 개의 CRC·전체 내용 검사를 통과했어요.
- 게임 종료 상태에서 언어 파일과 pack.mcmeta만 선택 적용했어요.
- [재검수 보고](quality_rereview_sophisticated.md), [배포 안내](../../../docs/archive/releases/8.1-stable.12.md),
  [패키지 목록](../manifests/8.1-stable.12_packages.json)에 근거를 남겨요.
- 실제 게임 화면은 미검증이에요. 다음은 4순위 인벤토리·정보·가이드 UI예요.

## 2026-09-29 · 품질 재검수 4순위 누적 stable.13

- Corail Tombstone·Lootr·Tempad·Enchantment Descriptions 등 20개 모드 언어 2,443키를 다시 대조해
  210키를 고치고 2,233키를 유지했어요. Sonnet 워커 2개 분업으로 진행했고 신규 번역은 없어요.
- 재검수 누적 검증, 안정판 검증, ZIP 두 개의 CRC·전체 내용 검사를 통과했어요.
- 게임 종료 상태에서 바뀐 언어 14파일과 pack.mcmeta만 선택 적용했어요.
- [재검수 보고](quality_rereview_info_ui.md), [배포 안내](../../../docs/releases/8.1-stable.13.md),
  [패키지 목록](../manifests/8.1-stable.13_packages.json)에 근거를 남겨요.
- 실제 게임 화면은 미검증이에요. 다음은 5순위 초반 기반 도구·기계·물류예요.
