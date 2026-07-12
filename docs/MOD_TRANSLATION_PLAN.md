# ATM10 주요 모드 번역 계획

## 개요

ATM10 7.1에 포함된 주요 모드와 공통 UI를 순차적으로 번역한다.

번역 순서는 단순한 모드 인기도나 콘텐츠 규모보다 다음 요소를 우선하여 정한다.

* 실제 플레이 중 문구가 노출되는 빈도
* 게임 초반부터 후반까지 사용하는 기간
* 번역 누락이 플레이 이해에 미치는 영향
* UI·설정·툴팁의 문장량
* ATM10 퀘스트 및 진행에서의 중요도
* 개별 모드의 인지도와 콘텐츠 규모

모든 플레이에 공통으로 노출되는 UI 계층을 먼저 정리한 뒤, 저장소·장비·기술·마법 등 주요 모드 계열을 순서대로 진행한다.

번역 중 자주 보이는 미번역 문구가 발견되면 아래 순위와 관계없이 먼저 수정할 수 있다.

---

## 0순위: ATM10 공통 문구

개별 모드 번역보다 먼저 확인하거나, 다른 작업과 병행하여 계속 관리한다.

### ATM10 전용 문구

* FTB Quests
* FTB Quests Lang Splitter
* KubeJS
* All The Tweaks
* ATM10 전용 아이템·조합법·시스템 메시지
* ATM Star 및 팩 전용 진행 문구
* 관련 데이터팩과 리소스팩 문구

퀘스트 제목, 설명, 작업 조건, 보상, 챕터 이름과 KubeJS 표시 문구를 우선한다.

모드 번역을 완료할 때마다 해당 모드와 관련된 FTB Quests 및 KubeJS 문구도 함께 확인한다.

---

## 1순위: 공통 UI 및 정보 표시

이 계열은 특정 모드를 진행하지 않아도 게임 전체에서 계속 노출되므로 가장 먼저 정리한다.

### 1. JEI 계열

* Just Enough Items
* AE2 JEI Integration
* FTB JEI Extras
* 각 모드의 JEI 연동 플러그인
* 현재 설치된 기타 JEI 애드온

우선 확인할 항목:

* 조합법 분류 이름
* 검색 도움말
* 제작·가공 화면
* 에너지 및 처리 시간 표시
* 아이템 사용처와 생성법
* 즐겨찾기 및 북마크 관련 문구

단순 아이템 이름은 해당 아이템의 원본 모드 번역을 우선하고, JEI 자체 UI와 조합법 분류를 중심으로 작업한다.

### 2. Jade 계열

* Jade
* Jade Addons
* 현재 설치된 Jade 연동 모드

우선 확인할 항목:

* 블록 및 엔티티 정보
* 기계 상태
* 저장된 아이템과 액체
* 에너지 및 진행률
* 수확 가능 여부
* 도구 요구 조건
* 소유자 및 보호 정보

Jade에 표시되는 문구가 실제 원본 모드에서 오는지 Jade 연동 모드에서 오는지 구분하여 처리한다.

### 3. 지도·청크·이동 계열

* JourneyMap
* JourneyMap Integration
* FTB Chunks
* FTB Teams
* Waystones
* Nature's Compass
* Explorer's Compass
* Structure Compass
* 현재 설치된 관련 애드온

우선 확인할 항목:

* 지도와 웨이포인트
* 청크 소유 및 강제 로딩
* 팀 설정과 권한
* 차원 이동
* 구조물 및 바이옴 검색
* 사망 지점과 위치 안내

### 4. 공통 장비·효과 표시

* Curios 및 장비 슬롯 관련 모드
* Equipment Compare
* Enchantment Descriptions
* More Overlays Updated
* 속성 및 효과 표시 관련 모드
* 현재 설치된 장비 비교 애드온

우선 확인할 항목:

* 장착 부위
* 장비 비교 문구
* 속성 증가·감소
* 마법부여 설명
* 조건부 효과
* 키 입력 안내
* Shift 확장 툴팁

### 5. 가이드북 계열

* GuideME
* Modonomicon
* Patchouli
* Akashic Tome
* 각 모드의 전용 가이드북
* 현재 설치된 기타 안내서 프레임워크

가이드 프레임워크 자체의 버튼·탭·검색·목차 문구를 먼저 번역한다.

각 가이드북의 본문은 해당 원본 모드 번역 작업에 포함한다.

### 6. 공통 편의 기능

* FTB Ultimine
* Corail Tombstone
* Lootr
* Polymorph
* Carry On
* Crafting Tweaks 계열
* 인벤토리 정렬 및 검색 관련 모드
* 제작법 충돌 선택 UI
* 현재 설치된 기타 편의 모드

번역량이 적더라도 플레이 중 자주 표시되는 설정, 키 안내와 시스템 메시지는 우선 처리한다.

---

## 2순위: 저장소 및 인벤토리

### 1. Sophisticated 계열

* Sophisticated Core
* Sophisticated Backpacks
* Sophisticated Storage
* Sophisticated Backpacks Create Integration
* Sophisticated Storage Create Integration
* Sophisticated Storage in Motion
* 현재 설치된 기타 애드온

초반부터 후반까지 계속 사용하는 배낭과 저장소 계열이므로 가장 먼저 작업한다.

중점 항목:

* 업그레이드 이름
* 필터 및 설정 화면
* 슬롯·스택 관련 문구
* 줍기·공급·압축·제작·자동 급식 기능
* 일반 및 고급 업그레이드
* Shift 확장 툴팁
* 배낭과 저장소의 공통 용어

### 2. Applied Energistics 2 계열

* Applied Energistics 2
* AdvancedAE
* ExtendedAE
* AE2 Import Export Card
* AE2 Network Analyser
* AE2 Crafting Tree
* AEInfinityBooster
* AE2 JEI Integration
* 현재 설치된 기타 AE2 애드온

중점 항목:

* 저장소 및 터미널
* 셀과 드라이브
* 채널과 네트워크
* 패턴 및 자동조합
* 입출력 버스
* 서브네트워크와 P2P
* 네트워크 오류 및 상태 메시지

### 3. Refined Storage 2 계열

* Refined Storage 2
* 현재 설치된 관련 애드온과 연동 모드

AE2와 용어가 비슷하지만 서로 다른 시스템이므로 무리하게 같은 번역을 적용하지 않는다.

컨트롤러, 디스크, 그리드, 자동제작, 외부 저장소와 무선 접속 관련 용어를 중점적으로 확인한다.

### 4. 단순·대량 저장소 계열

* Functional Storage
* Storage Drawers
* Pocket Storage
* EnderChests 및 EnderTanks 계열
* 현재 설치된 기타 저장소 모드

서랍, 제어기, 링크, 잠금, 용량·공허·압축 업그레이드 등의 공통 용어를 통일한다.

### 5. Integrated 계열

* Integrated Dynamics
* Integrated Tunnels
* Integrated Terminals
* Integrated Crafting
* Integrated Scripting
* 현재 설치된 관련 애드온

저장소뿐 아니라 변수·논리·물류와 자동조합을 포함하므로 별도 대형 작업으로 진행한다.

---

## 3순위: 장비 및 캐릭터 성장

### 1. Apotheosis 계열

* Apotheosis
* Apothic Attributes
* Apothic Enchanting
* Apothic Spawners
* Apothic Compats
* Iron's Apothic
* 현재 설치된 관련 애드온

중점 항목:

* 장비 어픽스
* 보석과 소켓
* 속성과 능력치
* 희귀도와 품질
* 마법부여
* 스포너 개조
* 보스 및 전리품 툴팁

무작위 장비마다 반복 노출되므로 아이템 이름보다 효과 설명과 수치 표현을 우선한다.

### 2. Relics·Artifacts 계열

* Relics
* Artifacts
* Reliquified Artifacts
* Reliquified 계열 애드온
* 현재 설치된 관련 호환 모드

중점 항목:

* 유물 이름
* 장착 부위
* 기본 능력
* 경험치 및 레벨
* 진화 조건
* 능력 잠금 해제
* 세부 능력치
* 키 입력 및 활성화 조건

Relics와 Artifacts를 별도 작업으로 나누지 않고 하나의 작업 단위로 처리한다.

### 3. Silent Gear 계열

* Silent Gear
* Silent Lib
* 현재 설치된 관련 애드온

재료 등급, 도구 부품, 특성, 시너지와 장비 능력치 표현을 통일한다.

### 4. Allthemodium 및 ATM 장비

* Allthemodium
* All The Arcanist Gear
* All the Wizard Gear
* ATM 전용 방어구와 도구
* ATM Star 관련 아이템

ATM10의 핵심 진행 아이템이므로 관련 퀘스트와 KubeJS 문구를 반드시 함께 확인한다.

---

## 4순위: 기술 및 기반 시설

### 1. Mekanism 계열

* Mekanism
* Mekanism Generators
* Mekanism Tools
* 현재 설치된 관련 애드온

기계 UI, 광물 처리, 가스·화학 물질, 멀티블록, 핵분열·핵융합과 경고 메시지를 함께 번역한다.

### 2. 전력·물류 계열

* Powah!
* Flux Networks
* Pipez
* Modern Dynamics
* XNet
* 현재 설치된 에너지·아이템·액체 운송 모드

이 계열은 여러 모드와 함께 사용되므로 에너지 입력·출력, 전송량, 우선순위, 필터와 연결 방향 표현을 통일한다.

### 3. 초중반 기반 모드

* Iron Furnaces
* Easy Villagers
* Mining Gadgets
* Building Gadgets
* Mob Grinding Utils
* Item Collectors
* 현재 설치된 관련 편의·자동화 모드

개별 번역량은 크지 않지만 초중반 사용 빈도가 높으므로 대형 후반 모드보다 먼저 처리한다.

### 4. Create 계열

* Create
* Create: Dragons Plus
* 현재 설치된 Create 애드온과 연동 모드

기계 부품, 회전력, 응력, 조립, 가공법과 기차 관련 용어를 본체와 애드온 전체에서 통일한다.

### 5. Just Dire Things

도구, 장비, 이동, 에너지와 자동화가 함께 포함되어 있으며 실제 활용 범위가 넓다.

아이템 이름뿐 아니라 설정 화면, 모듈과 능력 설명을 함께 확인한다.

### 6. Industrial Foregoing

농사, 목축, 몹 처리, 인챈트, 레이저 채굴과 다양한 자동화 기계를 함께 번역한다.

### 7. Modern Industrialization

기계 단계, 재료 가공, 멀티블록과 후반 ATM 진행 문구를 중점적으로 확인한다.

번역량이 많으므로 별도의 장기 작업으로 진행할 수 있다.

### 8. Ender IO

기계, 발전, 장비와 아이템·액체·에너지·레드스톤 도관의 설정 화면을 중점적으로 번역한다.

### 9. Immersive Engineering

전선, 전압, 컨베이어, 공정과 멀티블록 기계 관련 용어를 통일한다.

### 10. Draconic Evolution

장비 모듈, 보호막, 에너지 저장고, 반응로 상태와 위험 경고를 정확하게 번역한다.

### 11. PneumaticCraft: Repressurized

압력, 온도, 드론 프로그래밍, 플라스틱 생산과 경고 메시지를 중점적으로 번역한다.

---

## 5순위: 마법·농업·자원 생산

1. Ars Nouveau 계열
2. Mystical Agriculture 계열
3. Productive Bees
4. Iron's Spells 'n Spellbooks 계열
5. Occultism
6. Mahou Tsukai
7. Forbidden and Arcanus
8. Theurgy
9. EvilCraft
10. 현재 설치된 기타 마법 모드

### 공통 확인 항목

* 주문과 의식
* 마법 학파
* 등급과 재사용 대기시간
* 피해 및 효과 유형
* 소환 조건
* 자원 생산 조건
* 작물·벌·정수·유전자
* 가이드북과 진행 설명

본체와 애드온이 같은 용어를 사용하도록 가능한 한 하나의 작업 단위로 묶는다.

---

## 6순위: 탐험·전투·독립 콘텐츠

1. The Twilight Forest
2. L_Ender's Cataclysm
3. The Undergarden
4. MineColonies
5. 현재 설치된 기타 차원·보스·구조물 모드

보스 이름과 구조물 이름만 번역하지 않고 다음 문구도 함께 확인한다.

* 진행 제한과 해금 조건
* 보스 능력과 전투 안내
* 구조물 및 차원 설명
* 발전 과제
* 전리품과 장비 설명
* 주민 직업과 요구 사항
* 관련 FTB Quests 문구

MineColonies처럼 번역량이 매우 많고 독립성이 높은 모드는 별도의 장기 작업으로 관리한다.

---

## 전체 우선순위 요약

1. ATM10 전용 FTB Quests 및 KubeJS
2. JEI
3. Jade
4. JourneyMap·FTB Chunks·FTB Teams·Waystones
5. 공통 장비·효과·가이드 UI
6. Sophisticated 계열
7. Applied Energistics 2 계열
8. Apotheosis 계열
9. Relics·Artifacts 계열
10. Mekanism 계열
11. Allthemodium 및 ATM 전용 진행
12. Refined Storage 2 및 기타 저장소
13. 전력·물류·초중반 편의 모드
14. Create 계열
15. Ars Nouveau 계열
16. Mystical Agriculture 계열
17. Industrial Foregoing
18. Productive Bees
19. Iron's Spells 'n Spellbooks
20. Silent Gear
21. Just Dire Things
22. Modern Industrialization
23. Ender IO
24. Immersive Engineering
25. Draconic Evolution
26. The Twilight Forest
27. Occultism
28. Integrated Dynamics 계열
29. MineColonies
30. PneumaticCraft 및 나머지 대형 모드

---

## 기본 작업 범위

각 작업 단위에서 가능한 범위까지 다음 항목을 확인한다.

* 아이템 및 블록 이름
* 엔티티 및 효과 이름
* 메뉴와 설정 화면
* 버튼, 탭 및 필터
* 일반 툴팁
* Shift 등으로 표시되는 확장 툴팁
* 상태 및 오류 메시지
* 키 입력 안내
* 책과 가이드
* 발전 과제
* 관련 FTB Quests 문구
* 관련 KubeJS 표시 문구
* 현재 설치된 애드온 및 연동 모드

---

## 작업 원칙

* 실제 플레이에서 자주 보이는 문구를 먼저 번역한다.
* 본체와 애드온은 가능한 한 하나의 작업 단위로 묶는다.
* 공통 라이브러리의 문구가 여러 모드에서 사용되는지 확인한다.
* 기존 한국어 번역은 누락·오역·용어 불일치를 먼저 조사한다.
* 아이템명과 기계명처럼 검색에 사용되는 용어는 일관성을 우선한다.
* 기능을 확인할 수 없는 문구는 추측해서 번역하지 않는다.
* 변수, 자리표시자, 서식 코드와 키 구조는 원본 형식을 유지한다.
* 한 모드를 완료할 때 관련 퀘스트와 KubeJS 문구도 함께 처리한다.
* 새 공통 용어와 예외는 프로젝트 용어집에 반영한다.
* 실제 게임에서 주요 UI와 툴팁을 확인한 뒤 작업을 완료한다.

---

## 진행 방식

1. ATM10에 설치된 본체와 애드온을 확인한다.
2. 영어 원본과 기존 한국어 파일을 수집한다.
3. 누락 키와 기존 번역 상태를 조사한다.
4. 공통 용어와 번역 기준을 정한다.
5. 본체와 애드온을 번역한다.
6. 관련 FTB Quests와 KubeJS 문구를 번역한다.
7. 자리표시자, 서식 코드와 키 구조를 검증한다.
8. 실제 게임에서 주요 화면과 툴팁을 확인한다.
9. 용어집과 진행 기록을 갱신한다.

---

## 참고

이 문서는 전체 번역 작업의 대략적인 순서를 관리하기 위한 개요다.

공통 UI 모드는 독립적인 콘텐츠 규모가 작더라도 플레이 전반에 노출되므로 최우선으로 관리한다.

각 모드의 세부 작업 범위와 완료 조건은 해당 작업을 시작할 때 별도로 정한다. 실제 게임에서 번역 누락이 자주 보이거나 다른 모드 진행을 방해하는 경우에는 우선순위를 앞당긴다.
