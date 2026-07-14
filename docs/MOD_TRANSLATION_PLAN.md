# ATM10 주요 모드 번역 계획

## 목적

ATM10 7.1에 설치된 주요 모드와 공통 UI를 아래 Goal 순서에 따라 한국어로 번역한다.

이 문서에는 실행 순서가 하나만 있다. `Goal 실행 순서`의 번호가 실제 작업 순위이며,
분야 이름이나 문서의 배치 순서는 별도의 우선순위를 뜻하지 않는다.

순서는 다음 요소를 함께 고려한다.

- 실제 플레이 중 문구가 노출되는 빈도
- 게임 초반부터 후반까지 사용하는 기간
- 번역 누락이 플레이 이해에 미치는 영향
- UI·설정·툴팁의 문장량
- ATM10 퀘스트 및 진행에서의 중요도
- 모드와 애드온 사이의 용어 의존성

## 기준 환경

- 기준 모드팩: All the Mods 10 7.1
- Minecraft: 1.21.1
- 설치 모드 기준: 2026-07-14 `source_root/mods`의 JAR 480개
- 원본 조회 경로: `local_paths.json`의 `source_root` 우선 사용

Goal을 시작할 때는 기준 환경을 다시 읽기 전용으로 조사한다. 모드팩 업데이트로 설치 목록이
달라졌다면 활성 Goal의 범위를 임의로 넓히지 않고, 새 모드를 별도 후보로 기록한 뒤 계획서를
갱신한다.

## Goal 실행 규칙

1. 한 번에 하나의 Goal만 활성화하고, 번호가 작은 Goal부터 완료한다.
2. Goal 시작 전에 Git 기록, `working/`의 완료 기록, `output/` 산출물과 현재
   `source_root` 적용본을 확인한다.
3. 이미 구현·검증·적용된 범위는 해시와 완료 기록만 간단히 확인하고 다시 번역하지 않는다.
   확인 결과가 일치하면 `기존 완료 확인`으로 기록하고 다음 Goal로 넘어간다.
4. 완료 기록이 없거나 현재 원문과 산출물이 다르면 해당 범위만 다시 연다.
5. Goal 시작 시 설치된 본체·애드온·FTB Quests·KubeJS 범위를 목록으로 고정한다.
6. 한 Goal이 크면 약 100~200개 언어 키, 가이드 한 묶음 또는 FTB Quests 한 챕터 단위로
   내부 배치를 나눈다.
7. 내부 배치는 순서대로 구현하고 검증하지만, Goal 전체 범위가 끝나기 전에는 다음 Goal로
   넘어가지 않는다.
8. 각 검증 가능한 내부 배치는 독립적으로 커밋할 수 있다. 계획서와 사용자의 기존 변경은
   번역 커밋에 포함하지 않는다.
9. Goal의 마지막 배치까지 검증한 뒤 Minecraft·Java 프로세스를 확인하고, 저장소의 적용
   스크립트로 `source_root`와 설정된 `game_root`에 적용한다.
10. 게임 프로세스가 실행 중이면 적용을 보류하고 Goal을 `적용 대기`로 기록한다. 프로세스가
    종료된 뒤 적용과 해시 검증까지 끝내고 Goal을 닫는다.
11. AI는 구현·커밋·적용·파일 검증까지 담당한다. 실제 게임 화면에서 문구의 잘림, 문맥과
    렌더링을 확인하는 일은 사용자가 담당하며, 발견된 문제는 후속 수정 후보로 기록한다.
12. `git push`는 사용자가 직접 요청한 경우에만 수행한다.

## Goal 실행 순서

### 공통 문구와 공통 UI

| 순위 | Goal | 포함 범위 | 핵심 확인 항목 | 상태 |
|---:|---|---|---|---|
| 0 | ATM10 공통 문구 | FTB Quests, FTB Quests Lang Splitter, KubeJS, All The Tweaks의 비모드 공통 문구 | 공통 탐색·목차·그룹·시스템 메시지 | 대기 |
| 1 | JEI 공통 UI | Just Enough Items, FTB JEI Extras, AE2 JEI Integration, Refined Storage JEI Integration | 검색·북마크·버튼·설정·공통 조합법 UI | 대기 |
| 2 | Jade | Jade | 오버레이 UI·설정·상태 표시 | 대기 |
| 3 | 지도·청크·팀 | JourneyMap, FTB Chunks, FTB Teams | 지도·웨이포인트·청크·팀·권한 | 대기 |
| 4 | 이동·탐색 도구 | Waystones, Nature's Compass, Explorer's Compass | 이동·바이옴·구조물 탐색 UI | 대기 |
| 5 | 공통 장비·효과 표시 | Curios, Enchantment Descriptions, More Overlays Updated | 장착 부위·마법부여 설명·오버레이 | 대기 |
| 6 | 가이드 프레임워크 UI | GuideME, Modonomicon, Patchouli, Akashic Tome | 버튼·탭·검색·목차·설정 | 대기 |
| 7 | 공통 편의 기능 A | FTB Ultimine, Corail Tombstone, Lootr | 키 안내·사망 지점·전리품·설정 | 대기 |
| 8 | 공통 편의 기능 B | Polymorph, Ars Polymorphia, Crafting Tweaks | 제작법 충돌 선택·제작 UI·설정 | 대기 |

0순위에서는 특정 모드에 귀속되지 않는 공통 문구만 번역한다. 모드 이름, 모드 아이템,
모드별 퀘스트 챕터·설명·Task와 모드 전용 KubeJS 문구는 건드리지 않고 해당 모드 Goal로
넘긴다. 조사 결과 번역할 비모드 공통 문구가 없다면 변경 없이 조사 결과만 기록하고
0순위를 완료한다.

JEI Goal에서는 JEI 자체의 UI, 검색, 북마크, 버튼, 설정과 공통 안내만 번역한다. 특정 모드가
제공하는 아이템·블록 이름, 툴팁과 모드 전용 조합법 문구는 해당 모드 Goal에서 번역한다.

가이드 프레임워크 Goal에서는 프레임워크 자체 UI만 번역한다. 각 가이드북의 본문은 해당
원본 모드 Goal에 포함한다.

### 저장소와 장비

| 순위 | Goal | 포함 범위 | 핵심 확인 항목 | 상태 |
|---:|---|---|---|---|
| 9 | Sophisticated 배낭 | Sophisticated Core, Sophisticated Backpacks, Backpacks Create Integration | 배낭·필터·업그레이드·확장 툴팁 | 대기 |
| 10 | Sophisticated 저장소 | Sophisticated Storage, Storage Create Integration, Storage in Motion | 저장소·제어기·업그레이드·이동 연동 | 대기 |
| 11 | Applied Energistics 2 완료 범위 | AE2 본체와 GuideME 가이드 제공 애드온 11개 | 기존 완료 기록·산출물·적용 해시 확인 | **완료 — 간단 확인만 수행** |
| 12 | AE2 추가 연동 모드 | AE2 Crafting Tree, AEInfinityBooster, Applied Mekanistics, Immersive Energistics, PolyEng, Soulplied Energistics | 일반 언어 파일·툴팁·퀘스트·KubeJS | 대기 |
| 13 | Apotheosis 기반 | Apotheosis, Apothic Attributes | 장비 어픽스·보석·소켓·속성·희귀도 | 대기 |
| 14 | Apotheosis 마법부여·스포너 | Apothic Enchanting, Apothic Spawners | 마법부여·스포너 개조·오류·설정 | 대기 |
| 15 | Relics·Artifacts | Relics, Artifacts, Reliquified Artifacts | 유물·장착 부위·레벨·능력·해금 조건 | 대기 |
| 16 | Mekanism 본체 | Mekanism | 기계 UI·광물 처리·화학 물질·멀티블록 | 대기 |
| 17 | Mekanism 연동 | Mekanism Generators, Mekanism Tools, Mekanism Covers, Just Enough Mekanism Multiblocks | 발전·장비·커버·멀티블록 안내 | 대기 |
| 18 | ATM 핵심 장비와 진행 | Allthemodium, All The Arcanist Gear, All the Wizard Gear | ATM 장비·ATM Star·관련 퀘스트·KubeJS | 대기 |
| 19 | Refined Storage 2 본체 | Refined Storage 2 | 컨트롤러·디스크·그리드·자동제작 | 대기 |
| 20 | Refined Storage 2 연동 | Curios Integration, Mekanism Integration, Quartz Arsenal | 장비·화학 물질·무기 연동과 관련 UI | 대기 |
| 21 | 단순·대량 저장소 | Functional Storage, Pocket Storage, EnderStorage | 제어기·링크·잠금·용량·공허·압축 | 대기 |

11순위 완료 범위는 AE2 본체, AE2WTLib, EnderDrives, ExtendedAE, AdvancedAE,
MEGA Cells, Applied Flux, ExpandedAE, AE2 Import Export Card, AE2 Network Analyser,
ME Requester와 Ars Énergistique다. 이 범위는 `working/ae2/`와
`working/ae2_addons/`의 완료 기록을 확인하고, 원문이나 적용본이 달라진 경우에만 영향을
받은 부분을 다시 연다.

Refined Storage 2의 JEI Integration은 1순위에서 공통 JEI UI를 확인하고, Refined Storage
전용 조합법·아이템 문구는 19~20순위에서 확인한다.

### 전력·물류·기술

| 순위 | Goal | 포함 범위 | 핵심 확인 항목 | 상태 |
|---:|---|---|---|---|
| 22 | 전력망 | Powah!, Flux Networks | 발전·충방전·전송량·네트워크·우선순위 | 대기 |
| 23 | 물류망 | Pipez, Modern Dynamics, XNet | 아이템·액체·에너지·필터·연결 방향 | 대기 |
| 24 | 초중반 기반 시설 A | Iron Furnaces, Easy Villagers | 기계 등급·주민 작업·자동화·설정 | 대기 |
| 25 | 초중반 기반 시설 B | Mining Gadgets, Building Gadgets, Mob Grinding Utils, Item Collectors | 도구 모듈·건축·몹 처리·수집 범위 | 대기 |
| 26 | Create 본체 | Create | 회전력·응력·가공·조립·기차·Ponder | 대기 |
| 27 | Create 애드온 | Create: Dragons Plus, Create Crafts & Additions, Create Enchantment Industry, Create Aquatic Ambitions, Create Hypertube, Rechiseled: Create | 본체 용어와 애드온 UI·가이드 일치 | 대기 |
| 28 | Ars Nouveau 본체 | Ars Nouveau | 주문·문양·마나·의식·가이드북 | 대기 |
| 29 | Ars Nouveau 애드온 | Ars Additions, Ars Controle, Ars Creo, Ars Elemancy, Ars Elemental, Ars Ocultas, Ars Technica, Ars Unification | 본체 용어·주문·장치·연동 일치 | 대기 |
| 30 | Mystical Agriculture 계열 | Mystical Agriculture, Mystical Agradditions, Mystical Customization, Botany Pots Mystical | 작물·정수·등급·제작·재배 조건 | 대기 |
| 31 | Industrial Foregoing | Industrial Foregoing, Industrial Foregoing Souls | 농사·목축·몹 처리·레이저·기계 UI | 대기 |
| 32 | Productive Bees | Productive Bees | 벌·유전자·생산 조건·가이드북 | 대기 |
| 33 | Iron's Spells 'n Spellbooks | Iron's Spells 'n Spellbooks | 주문·학파·등급·재사용 대기시간·장비 | 대기 |
| 34 | Silent Gear 계열 | Silent Gear, Silent Lib, Silent Gems | 재료 등급·부품·특성·시너지·능력치 | 대기 |
| 35 | Just Dire Things | Just Dire Things | 도구·모듈·이동·에너지·자동화 | 대기 |
| 36 | Modern Industrialization | Modern Industrialization, Extended Industrialization | 기계 단계·재료 가공·멀티블록·후반 진행 | 대기 |
| 37 | Ender IO | Ender IO | 기계·발전·장비·도관·필터·채널 설정 | 대기 |
| 38 | Immersive Engineering | Immersive Engineering | 전선·전압·컨베이어·공정·멀티블록 | 대기 |
| 39 | Draconic Evolution | Draconic Evolution | 장비 모듈·보호막·에너지·반응로 경고 | 대기 |

Create와 Sophisticated 사이의 연동 언어는 9~10순위에서 배낭·저장소 기능을 먼저 확정하고,
27순위에서 Create 용어와의 최종 일관성을 다시 확인한다.

### 마법·탐험·독립 콘텐츠

| 순위 | Goal | 포함 범위 | 핵심 확인 항목 | 상태 |
|---:|---|---|---|---|
| 40 | The Twilight Forest | The Twilight Forest | 차원·보스·진행 제한·구조물·장비 | 대기 |
| 41 | Occultism | Occultism, Occultism KubeJS | 의식·소환·저장소·사전·KubeJS | 대기 |
| 42 | Integrated Dynamics 기반 | Integrated Dynamics, Integrated Terminals | 변수·논리·리더·터미널·오류 메시지 | 대기 |
| 43 | Integrated 자동화 | Integrated Tunnels, Integrated Crafting, Integrated Scripting | 물류·자동조합·스크립트·조건 설정 | 대기 |
| 44 | MineColonies | MineColonies | 주민 직업·요구 사항·건설·연구·UI | 대기 |
| 45 | PneumaticCraft: Repressurized | PneumaticCraft: Repressurized | 압력·온도·드론·플라스틱·경고 | 대기 |
| 46 | Mahou Tsukai | Mahou Tsukai | 마법진·마나·주문·조건·장비 | 대기 |
| 47 | Forbidden and Arcanus | Forbidden and Arcanus | 재료·의식·장비·효과·가이드 | 대기 |
| 48 | Theurgy | Theurgy, Theurgy KubeJS | 연성·재료 변환·의식·KubeJS | 대기 |
| 49 | EvilCraft | EvilCraft | 피·영혼·기계·의식·가이드북 | 대기 |
| 50 | 탐험·전투 차원 | L_Ender's Cataclysm, The Undergarden | 보스·차원·구조물·진행·전리품 | 대기 |

## 모드별 공통 작업 범위

각 Goal에서는 포함 모드와 직접 관련된 다음 항목을 모두 조사한다.

- 아이템·블록·기계 이름
- 엔티티·효과·속성 이름
- 메뉴·버튼·탭·필터·설정 화면
- 일반 툴팁과 Shift 확장 툴팁
- 상태·오류·경고 메시지
- 키 입력 안내
- 발전 과제와 가이드북 본문
- 관련 FTB Quests의 챕터·퀘스트·Task·설명·fallback 제목
- 관련 KubeJS 표시 문구
- 설치된 본체와 애드온 사이의 용어 일치

영어 문구의 출처를 추측하지 않는다. JEI, Jade 또는 공통 라이브러리에 보이는 문구라도 실제
키의 소유 모드와 네임스페이스를 확인한 뒤 담당 Goal에서 처리한다.

## Goal 작업 단계

1. 현재 설치된 본체·애드온과 버전을 확인하고 Goal 범위를 고정한다.
2. Git 기록과 완료 JSON을 확인해 기존 완료 범위를 분리한다.
3. 영어 원문, 모드 자체 한국어, ATM10 기존 한국어와 프로젝트 용어집을 수집한다.
4. 영어 전체 키와 기존 한국어 전체를 대조해 누락·오역·용어 불일치를 조사한다.
5. 관련 FTB Quests, KubeJS, 발전 과제와 가이드 파일을 조사한다.
6. 작업량에 따라 내부 배치를 정하고 순서대로 번역한다.
7. JSON·SNBT 문법, 키, 자료형, 자리표시자, 줄바꿈, 서식 코드와 가이드 참조를 검증한다.
8. 검증된 배치를 `output/`에 반영하고 독립적인 완료 단위로 커밋한다.
9. 마지막 배치에서 용어집, 조사 보고서와 완료 기록을 갱신한다.
10. Minecraft·Java 프로세스를 확인하고 저장소 적용 스크립트로 번역 산출물을 적용한다.
11. 적용 전후 해시와 계획 밖 변경을 검사한 뒤 Goal 완료를 보고한다.

## Goal 완료 조건

다음 조건을 모두 충족해야 Goal을 완료한다.

- 고정한 본체와 애드온의 영어 원문 전체를 검토함
- 기존 한국어 전체의 의미·용어·검색성·자리표시자를 검수함
- 관련 FTB Quests와 KubeJS 조사 및 필요한 번역을 완료함
- 가이드가 있으면 본문과 참조 파일을 검증함
- 남은 미번역과 수동 검토 항목이 없거나, 불가피한 보류 사유를 명확히 기록함
- 문법·키·자리표시자·줄바꿈·서식 코드 검증을 통과함
- 완료된 내부 배치를 커밋하고 커밋 정보를 기록함
- 설정된 적용 대상에 산출물을 적용하고 해시 일치를 확인함
- 원본 JAR과 계획 밖 인스턴스 파일이 변경되지 않음

사용자의 실제 게임 화면 확인은 AI의 파일 구현 Goal 완료 조건에 포함하지 않는다. AI는 적용한
파일과 사용자가 확인할 주요 화면을 완료 보고에 적고, 사용자가 발견한 표시 문제는 해당 모드의
후속 수정으로 처리한다.

## 우선순위 변경

실제 플레이를 막는 심각한 미번역이나 오역이 발견되면 사용자가 지시한 경우에만 현재 순서를
조정한다. 순서를 바꾸면 이 문서의 Goal 번호와 변경 이유를 먼저 갱신해 실행 순서가 다시 두 개로
갈라지지 않게 한다.
