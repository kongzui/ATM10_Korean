# ATM10 8.1 번역 업그레이드 진행 현황

기준 시각: 2026-09-01

## 지금 상태

- 7.1 검증본은 `output/7.1/`에 그대로 보존되어 있다.
- 8.1 작업본은 `output/8.1/`에서 재기준화 중이다.
- 완료·검증된 모드별 파일은 현재 8.1 게임 프로필에 선택 적용되어 바로 시험할 수 있다.
- 아직 전체 파일 적용은 금지되어 있다. `output/8.1/release.json`의
  `full_apply_allowed`는 모든 남은 작업과 게임 화면 검증이 끝날 때까지 `false`로 유지한다.

## 완료한 작업

1. 8.1 첫 실행, 원본 JAR·퀘스트·KubeJS 조사와 7.1 비교를 마쳤다.
2. 버전별 `output/7.1/`, `output/8.1/` 구조와 파일별 선택 적용 안전장치를 만들었다.
3. FTB Quests의 8.1 분할 언어 구조 이식과 추가 UI 번역을 마쳤다.
4. KubeJS를 8.1 원본 코드에 맞춰 재기준화했다.
5. 다음 기존 모드 계열을 8.1 원문에 맞춰 갱신하고 검증했다.
   - Modern Industrialization, Sophisticated 계열, Apotheosis, Ars Nouveau
   - Iron's Spells, SecurityCraft, CC:Tweaked, Mekanism
   - Herbs and Harvest, MineColonies, Waystones, EnderDrives
   - 클라이언트 UI, JEI, Create, Eternal Starlight, FTB Teams
   - Supplementaries, Amendments

## 이번 Supplementaries·Amendments 작업

- 현재 원문: Supplementaries 1,355키, Amendments 108키
- 기존 번역 재사용: 784키
  - 현재 JAR 한국어와 대조 후 재사용 617키
  - 기존 프로젝트 검수본 재사용 167키
- 8.1 신규·변경 번역: 679키
- 수동 교정이 기록된 키: Supplementaries 334키, Amendments 1키
- 미번역, 중복 키, 자리표시자·숫자·줄바꿈 오류와 번역으로 생긴 이름 충돌: 모두 0개
- 관련 FTB Quests와 KubeJS 직접 표시 문구: 없음
- JAR 내부 발전 과제와 제작법은 언어 키 사용 여부까지 확인했으며 원본 JAR은 수정하지 않았다.
- 현재 8.1 게임 프로필에 다음 두 파일만 선택 적용했다.
  - `resourcepacks/ATM10_Korean/assets/supplementaries/lang/ko_kr.json`
  - `resourcepacks/ATM10_Korean/assets/amendments/lang/ko_kr.json`

## 남은 작업

### 1. 기존 번역의 8.1 변경분 마무리

현재 감사 기준으로 변경된 기존 원문 중 산출물에 없는 키는 18개 네임스페이스의 111개다.

- Tombstone 20, JourneyMap 23, Artifacts 6
- Hostile Neural Networks 8, Integrated Tunnels 8, MFFS 7
- Functional Storage 5, Generator Galore 5, Industrial Foregoing 5, Modular Bees 5
- Lootr 4, PneumaticCraft 3, QuarryPlus 4, Integrated Terminals 3
- The Bumblezone 2, Integrated Scripting 1, Oritech 1, SFM 1

보호 문자열·자료형 검증 오류 69개도 함께 해결해야 한다.

- Industrial Foregoing 57
- Reliquified Artifacts 8
- Relics 2
- PneumaticCraft 1
- The Bumblezone 1

### 2. 8.1 신규 네임스페이스 분류와 번역

신규 후보는 11개 네임스페이스, 영어 원문 4,779키다. 설정·라이브러리 내부 문자열은 무조건
번역하지 않고 실제 사용자 표시 경로를 먼저 확인한다.

1. 퀘스트 영향이 있는 Auroral, Neo Vitae
2. Ad Astra, Ad Astra: Giselle Addon
3. Logistics Network, Step Crafter
4. Borderless, Better Advanced Tooltips
5. Moog's Structures, Common Storage Lib, Invasive Optimizations

### 3. 정리와 최종 검증

1. 8.1에서 사라진 키와 모드 전용 파일의 실제 소비자를 확인해 낡은 파일만 정리한다.
2. 전체 JSON·SNBT·자리표시자·서식·중복 키 검사를 다시 실행한다.
3. 새 시험 월드에서 리소스팩 로딩, JEI, 퀘스트, 설정 화면과 툴팁을 확인한다.
4. 문제가 없으면 `output/8.1/release.json`을 전체 적용 가능 상태로 바꾸고 마지막 전체 적용을
   검증한다.

## 언제 사용할 수 있나

- 현재 설치된 8.1 프로필에서는 지금까지 완료해 선택 적용한 번역을 바로 시험할 수 있다.
- 다만 이것은 전체 릴리스가 아니라 검증 완료 파일을 차례로 얹은 작업 중 버전이다.
- 8.1 전체 한글패치 완성까지는 기존 변경분 111키와 검증 오류 69개, 신규 네임스페이스
  4,779키의 표시 범위 분류·번역, 마지막 게임 화면 검증이 남아 있다.
- 따라서 “게임에 넣어 시험하기”는 지금 가능하지만, “8.1 전체를 빠짐없이 번역한 정식본”은
  아직 여러 작업 단위가 더 필요하다.
