# ATM10 8.1 번역 업그레이드 진행 현황

기준일: 2026-09-08

## 배포 방식

첫 배포는 `8.1-compat.1` 호환판이에요. 7.1 검수 번역을 보존하고 현재 버전의 변경분만
검토해 누적했어요. 신규 모드 전체 번역은 후속 업데이트로 분리했어요.
7.1 보존본과 실제 7.1 인스턴스는 수정하지 않았어요.

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

## 검증 수치

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
- 퀘스트 제목 감사는 작업 전 1,210개, 실제 적용 후 1,098개 후보를 반환해요. 정상적인 자동
  아이템명, 공식 모드명·저작권 표기와 기존 이름 불일치가 섞여 있어 실제 오류 수가 아니에요.
  전체 번역 품질 개선을 호환판의 새 번역 누락과 혼동하지 않아요.
- 게임 화면 확인은 사용자가 후속 확인으로 미뤘어요. 정적 검증 통과를 실제 게임 확인으로
  표현하지 않아요.

구체적인 적용·백업·배포 파일 결과는 `compat_release.md`, 자동 검증은
`compat_validation.json`, 출처와 ZIP 무결성 기록은 `../manifests/compat_*.json`에서 확인해요.
