# 진행 작업: ATM10 8.1 전체 번역 품질 재검수

순서와 기준은 [재검수 계획](docs/QUALITY_REREVIEW_PLAN.md), 규칙은 `AGENTS.md`를 따라요.
이번 요청은 계획의 순서대로 이미 번역된 계열을 다시 검수하는 작업이에요. 계열 하나가 끝날 때마다
검증·커밋·적용하고 계획의 진행 현황을 갱신해요. 신규 번역과 보조 번역 코드는 범위 밖이에요.

3순위부터는 Opus 오케스트레이터와 Sonnet 워커 분업으로 진행해요. 준비·배정·검토 순서와 노하우는
[재검수 계획의 분업 진행](docs/QUALITY_REREVIEW_PLAN.md), 워커 지시문은
[REREVIEW_WORKER_BRIEF.md](docs/REREVIEW_WORKER_BRIEF.md), 대조 자료 도구는
`scripts/rereview_worker_kit.py`예요.

## 재검수 9순위 · Mystical Agriculture · 8.1-stable.18

- [x] Sonnet 워커 2개 병렬(mysticalagriculture, Agradditions+퀘스트)로 언어 849키, 퀘스트 277키, 작물 설정 13파일 검토.
- [x] 언어 60키, 퀘스트 140키, 작물 설정 3파일 수정. ATM의 별 퀘스트의 `경험치 정수`를 `경험치 에센스`로 연동.
- [x] 워커를 부르기 전에 에센스·등급·마법 부여기·기계 프레임 등 표기를 정하고 용어집에 8개 기록.
- [x] 챕터명 `신비농업`은 1순위에서 해결된 것을 확인(산출물 0곳, 옛 병합 파일만 남음).
- [x] 재검수·누적 전체 검증, stable.18 ZIP 두 개 생성, 게임 종료 상태에서 8파일 선택 적용.
- [ ] 보고서의 남은 확인 항목(원문 오류 2, 이름 후보 2, 다른 계열로 넘긴 표기), 게임 화면 확인.

[재검수 보고](versions/8.1/reports/quality_rereview_mystical.md). 다음 계열은 10순위 Apotheosis 계열·Gateways예요.

## 재검수 8순위 · Mekanism 계열 · 8.1-stable.17

- [x] Sonnet 워커 7개 병렬(mekanism 3분할, generators+tools, 애드온 5개, 퀘스트 2)로 8개 모드 언어 5,216키, 퀘스트 468키, KubeJS 툴팁 검토.
- [x] 언어 1,398키, 퀘스트 296키, KubeJS 1줄 수정. 기초 전력 퀘스트의 `에틸렌`을 `에텐`으로 연동.
- [x] 워커끼리 갈린 용어(Fluid·모듈 이름·Injection 등)를 오케스트레이터가 정해 용어집에 16개 기록.
- [x] 재검수·누적 전체 검증, stable.17 ZIP 두 개 생성, 게임 종료 상태에서 12파일 선택 적용.
- [ ] Mekanism Ponder 스크립트 표기 정리, 보고서의 남은 확인 항목, 게임 화면 확인.

[재검수 보고](versions/8.1/reports/quality_rereview_mekanism.md). 다음 계열은 9순위 Mystical Agriculture였어요.

## 재검수 7순위 · Applied Energistics 2와 애드온 · 8.1-stable.16

- [x] Sonnet 워커 8개 병렬(언어·퀘스트 2, GuideME 가이드 6)로 17개 모드 언어 2,099키, 퀘스트 266키, 가이드 223파일 검토.
- [x] 언어 42키, 퀘스트 24키, 가이드 129파일 263곳 수정. 압축 블록 천령 금속 27키 연동.
- [x] 가이드 조각 교체 도구(`quality_rereview_guides.py`)와 가이드 대조 파일 생성, 누적 검증의 마크다운 검사 추가.
- [x] 재검수·누적 전체 검증, stable.16 ZIP 두 개 생성, 게임 종료 상태에서 140파일 선택 적용.
- [ ] 기존 AE2 전용 검증기 8.1 기준 갱신, 보고서의 남은 확인 항목, 게임 화면 확인.

[재검수 보고](versions/8.1/reports/quality_rereview_ae2.md). 다음 계열은 8순위 Mekanism 계열이었어요.

## 재검수 6순위 · Allthemodium·ATM 광물 · 8.1-stable.15

- [x] Sonnet 워커 1개로 4개 모드 866키 검토, 29키 수정. 오케스트레이터 보정 9키.
- [x] All The Compressed 1,796키를 원래 블록 이름과 규칙 대조, 163키 수정.
- [x] Allthemodium Patchouli 안내서 47필드 직접 검수, 4필드 수정 후 생성 스크립트로 재생성.
- [x] Rod·Gear·광물·차원·바닐라 생물 군계 이름 용어집 기록.
- [x] 재검수·누적 전체 검증, stable.15 ZIP 두 개 생성, 게임 종료 상태에서 9파일 선택 적용.
- [ ] `The Beyond` 표기 결정, 게임 화면 확인.

[재검수 보고](versions/8.1/reports/quality_rereview_atm_ores.md). 다음 계열은 7순위 Applied Energistics 2와 애드온이었어요.

## 재검수 5순위 · 초반 기반 도구·기계·물류 · 8.1-stable.14

- [x] 보류 용어 5개와 1~4순위 불확실 항목 확정, 앞선 계열 62키 반영([결정 보고](versions/8.1/reports/quality_rereview_term_decisions.md)).
- [x] Sonnet 워커 2개로 20개 모드 1,769키 검토, 126키 수정. 1순위 퀘스트 5키 보정.
- [x] 재검수·누적 전체 검증, stable.14 ZIP 두 개 생성, 게임 종료 상태에서 29파일 선택 적용.
- [ ] Building Gadgets 2·Energy Meter 가이드 재검수, 게임 화면 확인.

[재검수 보고](versions/8.1/reports/quality_rereview_early_infra.md). 다음 계열은 6순위 Allthemodium·ATM 광물이었어요.

## 재검수 4순위 · 인벤토리·정보·가이드 UI · 8.1-stable.13

- [x] Sonnet 워커 2개 병렬로 20개 모드 2,443키 검토, 210키 수정(오케스트레이터 보정·추가 9키 포함).
- [x] 바뀐 이름의 퀘스트·다른 모드 사용처 없음 확인, 작업 원본 보정 파일까지 반영.
- [x] 재검수·누적 전체 검증, stable.13 ZIP 두 개 생성, 게임 종료 상태에서 15파일 선택 적용.
- [ ] 보고서의 남은 확인 항목과 게임 화면 확인.

[재검수 보고](versions/8.1/reports/quality_rereview_info_ui.md). 다음 계열은 5순위 초반 기반 도구·기계·물류였어요.

## 재검수 3순위 · Sophisticated 계열 · 8.1-stable.12

- [x] Sonnet 워커 1개로 언어 4개 1,137키 검토, 112키 수정(오케스트레이터 보정 1키 포함).
- [x] Chipped 연동 업그레이드 이름·제한된 통 설정 이름 통일, 이름을 쓰는 퀘스트 없음 확인.
- [x] 재검수·누적 전체 검증, stable.12 ZIP 두 개 생성, 게임 종료 상태에서 선택 적용.
- [ ] Admin(관리자/OP)·Void(제거/공허) 표기 결정, 게임 화면 확인.

[재검수 보고](versions/8.1/reports/quality_rereview_sophisticated.md). 다음 계열은 4순위 인벤토리·정보·가이드 UI였어요.

## 재검수 2순위 2부 · 지도·장신구·웨이스톤·나침반 · 8.1-stable.11

- [x] Opus 오케스트레이터·Sonnet 워커 2개 분업 시험 운영으로 언어 5개 2,644키 검토, 177키 수정.
- [x] 워커 수정 전수 검토, 유지 키 표본 검토, 누락 번역투 8키 보정.
- [x] 재검수·누적 전체 검증, stable.11 ZIP 두 개 생성, 게임 종료 상태에서 6파일 선택 적용.
- [ ] 실제 게임에서 JourneyMap·Waystones·나침반 화면 확인.

[재검수 보고](versions/8.1/reports/quality_rereview_common_ui_2.md)에 분업 평가를 기록해요. 다음 계열은 3순위 Sophisticated였어요.

## 1·2순위 용어 교체 · 8.1-stable.10

- [x] 용어집 6장 기준으로 퀘스트 34키·언어 68키·KubeJS 3줄 교체(141곳 문맥 판단).
- [x] 재검수·누적 전체 검증, stable.10 ZIP 두 개 생성, 게임 종료 상태에서 17파일 선택 적용.
- [ ] `솔라리움`은 Ender IO 계열 재검수 때 아이템 이름과 함께 교체.

[용어 교체 보고](versions/8.1/reports/quality_rereview_term_pass.md)를 참고해요.

## 재검수 2순위 1부 · 공통 UI(JEI·Jade·FTB) · 8.1-stable.9

- [x] 언어 8개 네임스페이스 2,197키를 현재 JAR 영어와 대조, 142키 수정·2,055키 유지.
- [x] 재검수·누적 전체 검증, stable.9 ZIP 두 개 생성, 게임 종료 상태에서 8파일 선택 적용.
- [ ] 2부: JourneyMap·Curios·Waystones·Nature's Compass·Explorer's Compass 검수.
- [ ] 실제 게임에서 JEI·Jade·FTB 설정 화면 확인.

[재검수 보고](versions/8.1/reports/quality_rereview_common_ui.md)를 참고해요.

## 재검수 1순위 · 팩 공통 진행 퀘스트 · 8.1-stable.8

- [x] 퀘스트 19파일 2,023키를 현재 분할 영어와 대조, 575키 수정·1,448키 유지.
- [x] 언어 5개 네임스페이스 67키 검토(3키 수정), KubeJS 6파일 검토(2파일 8줄 수정).
- [x] 모드명 음역·번역체·오역·깨진 문장·서식 코드 위치와 아이템 이름 일치 교정.
- [x] 재검수·누적 전체 검증, stable.8 ZIP 두 개 생성, 게임 종료 상태에서 23파일 선택 적용.
- [ ] 실제 게임에서 메인 퀘스트·2장·3장·건축 팁 화면 확인.

[재검수 보고](versions/8.1/reports/quality_rereview_pack_progress.md)에 수정 유형과 다른 계열로
넘긴 아이템 이름을 기록해요. 다음 계열은 2순위 2부예요.

## Better Advanced Tooltips · 8.1-stable.7

- [x] 현재 2101.1.0-build.5 JAR의 영어 5키·내장 한국어 없음 확인.
- [x] 설정 5키 전체 신규 번역과 키·보호 문자열 검증.
- [x] FTB Quests 1,000파일·66챕터와 KubeJS 871파일 조사; 관련 참조 없음.
- [x] 별도 가이드 없음, 직접 표시 `Fuel:`·오류 안내는 원문 유지로 분류.
- [x] 누적 전체 검증, stable.7 ZIP 두 개 생성, 게임 종료 상태에서 언어 1파일 선택 적용.
- [ ] 실제 게임에서 설정 화면과 툴팁 확인.

[표시 경로 근거](versions/8.1/reports/betteradvancedtooltips_translation.md)와
[완료 보고](docs/archive/reports/8.1/betteradvancedtooltips_completion.md)에 기록해요.
선택된 팩은 stable.1 ZIP이므로 stable.7 팩 활성화와 실제 화면 확인이 필요해요.
다음 대상은 Borderless Window 21키예요.

## Step Crafter · 8.1-stable.6

- [x] 현재 0.1.8 JAR의 영어 79키·내장 한국어 없음 확인.
- [x] 이름·UI·툴팁·설정 79키 전체 번역과 보호 문자열 검증.
- [x] FTB Quests 1,000파일·66챕터와 KubeJS 871파일 조사; 관련 참조 없음.
- [x] 별도 가이드 없음. 제작법 해금용 발전 과제 48파일에 표시 문구 없음 확인.
- [x] 누적 전체 검증, stable.6 ZIP 두 개 생성, 게임 종료 상태에서 언어 1파일 적용.
- [ ] 실제 게임에서 제작기·요청기·관리자·모니터 화면 확인.

언어·표시 경로는 `8a670aa`로 커밋했어요. [완료 보고](docs/archive/reports/8.1/stepcrafter_completion.md)에
배포·적용 근거를 기록해요. 현재 선택된 팩은 stable.1 ZIP이므로 새 stable.6 팩 활성화가 필요해요.
Step Crafter 작업은 여기서 마치며 다음 대상은 Better Advanced Tooltips 5키예요.

## Logistics Networks · 8.1-stable.5

- [x] 현재 JAR 1.13.0의 일반 언어 454키 대조; 내장 한국어 없음.
- [x] 150·150·154개 내부 단위로 이름·UI·필터·툴팁·설정 전체 번역 검수.
- [x] GuideME 17페이지와 가이드 이름·설명 2키, 앵커·등록 컴포넌트 검수.
- [x] FTB Quests 1,000파일·66챕터와 KubeJS 871파일 조사; 관련 참조 없음.
- [x] 전체 누적 검증, stable.5 ZIP 두 개 생성, 종료 상태 확인 후 선택 파일 19개 적용.
- [ ] 실제 게임에서 노드·필터·렌치·컴퓨터 화면과 가이드 확인.

언어 `7aac04a`, 가이드·표시 경로 `6fbd2b1`로 커밋했어요.
[완료 보고](docs/archive/reports/8.1/logisticsnetworks_completion.md)에 적용 경로와 검증 근거를 기록해요.
현재 선택된 번역 팩은 stable.1 ZIP이에요. 새 stable.5 ZIP 활성화 후 화면 확인이 남아 있어요.
Logistics Networks 작업은 당시 여기서 종료했고, 다음 Step Crafter 진행 결과는 위에 기록해요.

## Ad Astra·Giselle Addon · 8.1-stable.4

- [x] 현재 JAR과 일반 언어 831·168키, 내장 한국어 후보 전체 대조.
- [x] 이름·UI·툴팁·발전 과제·소리 자막·마법부여 검수, 언어 단위 커밋 `2e589ee`.
- [x] Astrodux 35파일·165문구, 99페이지의 현재 영어 구조와 보호 문자열 검증.
- [x] 퀘스트 66챕터와 KubeJS 관련 참조 조사, 가이드 단위 커밋 `43b5f70`.
- [x] 누적 전체 JSON 1,800/SNBT 76/JS 27개 문법·기존 파일 보존 검사.
- [x] 누적 ZIP 두 개 검증과 선택 파일 37개 적용 결과 기록.
- [ ] 실제 게임에서 JEI·기계 UI·가이드·애드온 화면 확인.

세부 근거는 [완료 보고](docs/archive/reports/8.1/ad_astra_completion.md)에 기록해요.

## 현재 기준

- [x] 7.1·8.1 보조 코드 제외 안정판 ZIP 네 개 생성·검증.
- [x] 사용자 안정판 정상 작동 확인을 기록. 버전별·화면별 세부 확인은 별도예요.
- [x] 신규 모드·기존 누락·보조 번역 우선순위와 낡은 문서 정리.
- [x] 단축키 이전 방법 안내. 실제 설정 적용은 사용자가 직접 해요.

## 원문 기준 확인 → Auroral 전체

- [x] 현재 설치 목록과 8.1 기준 목록의 차이 및 개인 추가 모드 구분.
- [x] 실행 후 퀘스트와 기준 원문 차이 확인; 수정 대상의 새 원문 검증 기준 확정.
- [x] 새 번역에 맞는 검증·패키징 조건 준비. 과거 해시 검증을 무조건 우회하지 않기.
- [x] Auroral 영어 148키와 현재 한국어 후보·관련 퀘스트·가이드·KubeJS 조사.
- [x] 일반 언어 전체 검수, 퀘스트 제목과 확정 아이템 이름 연결 확인.
- [x] 변경분 문법·보호 문자열·표시 경로 검증 후 계열 커밋.
- [x] 8.1 누적 ZIP 두 개 생성·검증, 배포 문서와 현황 갱신 후 문서 커밋.
- [ ] 사용자 설치 후 해당 모드의 게임 확인 결과 기록.

## Neo Vitae 전체 · 8.1-stable.3

언어 3,053키와 직접 표시 문구 61키, 퀘스트 105키 검수를 마쳤어요.
세부 수치와 원문 차이는 [완료 보고](docs/archive/reports/8.1/neovitae_completion.md)에 있어요.

- [x] 현재 JAR 영어 3,053키·한국어 후보 유무와 가이드·퀘스트 조사.
- [x] 일반 이름·UI·툴팁·가이드 언어 전체 검수와 용어 통일.
- [x] 관련 퀘스트 제목·Task·자동 제목을 확정 아이템 이름과 대조.
- [x] 문법·보호 문자열·가이드 표시 경로 검증 후 계열 커밋.
- [x] 다음 누적 ZIP 두 개 생성·검증과 배포 문서·현황 갱신.
- [ ] 사용자 설치 후 해당 모드의 게임 확인 결과 기록.

원문 기준의 상세 근거는 [단계 0 보완 보고](docs/archive/reports/8.1/stage1_source_baseline.md)에 있어요.
사용자 설치 후 화면 확인은 파일·정적 검증과 구분해 대기 항목으로 남겨요.
단계 1 당시에는 실제 인스턴스를 수정하지 않았어요. 이번 적용은 현재 `AGENTS.md`를 따르며,
7.1 안정판과 보조 코드 제외 방침을 유지해요.
