# ATM10 주요 모드 번역 현황

## 문서 목적

이 문서는 ATM10에서 번역할 모드를 고르고 현재 상태를 확인하는 분류·상태 문서다.
선택한 모드의 처리 단계는 `PLAN.md`, 안전·번역·검증·적용·Git 규칙은 `AGENTS.md`, 사용자용
설명과 명령은 `README.md`를 따른다.

목록의 위아래 배치와 콘텐츠 분류는 구현 우선순위가 아니다. 사용자는 어떤 분류의 모드든
자유롭게 선택할 수 있고, 서로 다른 분류의 모드를 하나의 작업으로 묶을 수도 있다. 선택하지
않은 모드는 현재 작업이 끝난 뒤 자동으로 이어서 진행하지 않는다.

필요하면 사용자가 선택한 하나 이상의 모드 묶음을 Codex Goal로 진행할 수 있다. Goal은 그때
선택한 범위만 관리하며, 이 문서 전체를 순서대로 실행하는 장기 로드맵으로 사용하지 않는다.

## 기준 환경

- 현재 목표 모드팩: All the Mods 10 8.1
- 이전 검수 기준: All the Mods 10 7.1
- Minecraft: 1.21.1
- 설치 모드 기준: 2026-08-31 `game_root/mods`의 JAR 488개
- 8.1 조사 자료: 영어 언어 네임스페이스 398개, FTB Quests 챕터 66개
- 현재 output 상태: `output/7.1/` 검증본을 보존하고, 복사한 `output/8.1/`을 재기준화하는
  중이며 8.1 전체 적용 금지

아래 완료 목록은 7.1에서 끝낸 전체 검수 기록이다. 8.1에서 영어 원문이나 표시 경로가 바뀐
항목은 기존 한국어를 후보로 재사용하되, 새 원문과 다시 대조해 완료 상태를 갱신한다. 실제 영향
목록과 순서는 `versions/8.1/reports/pack_comparison.md`와 버전 업그레이드 계획을 따른다.

목록에는 플레이 중 표시 문구가 많거나, 독립적인 진행·UI·가이드·퀘스트가 있거나, ATM10의
대표 콘텐츠로 사용되는 모드를 우선 수록한다. 라이브러리·API·성능 최적화·로더·내부 호환
모드는 사용자 표시 문구가 주요 번역 대상이 아닌 한 독립 항목에서 제외한다. 작은 애드온은
가능한 한 관련 본체의 `함께 확인할 범위`에 묶는다.

모드팩 업데이트 뒤 작업을 시작할 때는 실제 설치 여부와 버전을 다시 확인한다. 설치 목록이
달라졌다면 기억이나 다른 ATM 시리즈 구성을 근거로 추측하지 않고 이 문서를 갱신한다.

### 상태 의미

- **완료** — 전체 검토·검증·산출물 반영을 마치고 적용 완료 또는 보류 사유를 기록한 상태다.
- **부분 완료** — 일부 언어·퀘스트·가이드 또는 공통 범위만 완료한 상태다.
- **미작업** — 프로젝트 기준의 전체 검토 완료 기록이 없는 상태다.
- **재검수 필요** — 완료 기록은 있으나 원문·버전·적용본 차이로 다시 확인해야 하는 상태다.

모드 JAR에 한국어가 포함되어 있어도 프로젝트 전체 검수를 마친 것은 아니므로 자동으로
`완료`로 표시하지 않는다.

## 이 문서의 사용 방법

다음처럼 원하는 모드나 공통 UI만 골라 요청하면 된다.

- `The Twilight Forest와 EvilCraft를 번역해줘.`
- `Relics·Artifacts 계열을 하나의 작업으로 진행해줘.`
- `Mekanism 본체와 연동 모드를 함께 번역해줘.`
- `JEI 공통 UI와 Jade만 먼저 정리해줘.`
- `탐험·차원·보스 분류에서 The Twilight Forest와 The Undergarden만 진행해줘.`

요청받은 모드와 직접 관련된 애드온·FTB Quests·KubeJS만 현재 범위로 고정한다. 작업량이 크면
내부 배치로 나눌 수 있지만, 선택한 범위를 끝낸 뒤 다른 모드로 자동 이동하지 않는다.

## 7.1에서 완료된 항목

완료 항목은 빠르게 찾아볼 수 있도록 표 대신 영역별 목록으로 정리한다. 각 항목은 모드의 핵심
기능과 함께 검수한 직접 연동 범위를 짧게 설명한다.

### 공통 문구·공통 UI

- **ATM10 공통 문구** — 팩 공통 탐색·목차·그룹·메시지다. FTB Quests, Lang Splitter,
  KubeJS와 All The Tweaks 표시 경로를 함께 검수했다.
- **Just Enough Items (JEI)** — 아이템 검색, 조합법 조회, 북마크와 설정 UI다. FTB·AE2·Refined
  Storage의 JEI 연동을 함께 확인했다.
- **Jade** — 바라보는 블록과 엔티티의 상태를 보여 주는 화면 오버레이다. 본체 설정과 실제
  문구 소유 모드까지 추적했다.
- **JourneyMap·FTB Chunks·FTB Teams** — 지도·웨이포인트·청크 소유·팀 권한을 관리하는 UI다.
- **Waystones·Nature's Compass·Explorer's Compass** — 이동 지점을 저장하고 바이옴·구조물을
  찾는 탐색 도구다.
- **Curios·효과 표시** — 추가 장비 슬롯, 마법부여 설명과 상태 오버레이다. Enchantment
  Descriptions와 More Overlays Updated를 포함한다.
- **가이드 프레임워크 UI** — GuideME, Modonomicon, Patchouli와 Akashic Tome의 검색·목차·버튼
  같은 공통 가이드 화면이다.
- **공통 편의 기능** — FTB Ultimine의 채굴, Corail Tombstone의 사망 지점, Lootr의 전리품,
  Polymorph 계열의 제작법 선택과 Crafting Tweaks UI를 다룬다.
- **인벤토리·조작 편의** — Controlling, Better Advancements, AppleSkin, Mouse Tweaks,
  Inventory Tweaks와 TrashSlot의 키 설정·정보 표시·인벤토리 조작 기능이다.
- **Tempad** — 저장한 위치 사이를 이동하는 휴대용 순간이동 도구다. 관련 퀘스트와 KubeJS도
  함께 검수했다.
- **클라이언트 메뉴·설정 UI** — 시작 메뉴, 그래픽·셰이더와 소리 차단 설정을 제공한다.
  FancyMenu, Sodium Extra, Iris, Extreme Sound Muffler와 Fzzy Config를 함께 검수했다.
- **FTB Essentials·FTB Filter System** — 순간이동 요청·홈·휴지통 명령과 스마트 필터 UI를
  제공한다. 채팅 메시지·툴팁과 다른 FTB 모드 연동을 포함한다.
- **Just Enough Archaeology** — JEI·EMI에서 고고학 솔질과 스니퍼 결과를 보여 준다. 본체의
  조합법 범주·설명과 JEI·EMI 표시 경로를 함께 검수했다.

공통 UI 완료 범위는 프레임워크와 공통 화면에 한정한다. 특정 모드의 아이템·블록 이름,
전용 조합법 문구와 가이드 본문은 해당 모드의 완료 여부를 따른다.

### 저장소·인벤토리

- **Sophisticated Backpacks·Sophisticated Storage** — 필터·자동화·업그레이드를 갖춘 배낭과
  상자·통 저장소다. Sophisticated Core와 Create 연동, Storage in Motion을 포함한다.
- **Applied Energistics 2 (AE2)와 주요 애드온** — 네트워크형 디지털 저장소와 자동 제작
  시스템이다. AE2WTLib, EnderDrives, ExtendedAE, AdvancedAE, MEGA Cells 등 주요 애드온의
  언어·GuideME 가이드·퀘스트를 함께 검수했다.
- **AE2 추가 연동 모드** — AE2 Crafting Tree, AEInfinityBooster, Applied Mekanistics,
  Immersive Energistics, PolyEng와 Soulplied Energistics처럼 AE2를 다른 기술·마법 모드와
  연결하는 기능이다.
- **Refined Storage 2 계열** — 디스크와 그리드를 이용하는 디지털 저장소다. Extra Disks,
  Extra Storage, Universal Grid, Refined Types와 Curios·Mekanism 연동을 포함한다.
- **Functional Storage·Pocket Storage·EnderStorage** — 대량 서랍 저장, 휴대 저장과 원격 공유
  저장소를 제공한다.
- **Compact Machines** — 블록 하나 안의 별도 공간에 기계실과 자동화 설비를 구성한다.

### 장비·캐릭터 성장·전투

- **Apotheosis** — 어픽스·보석·소켓·희귀도로 장비를 성장시키는 시스템이다. Apothic
  Attributes, Enchanting과 Spawners를 포함한다.
- **Relics·Artifacts** — 장착형 유물을 성장시키고 능력을 해금한다. Reliquified Artifacts까지
  함께 검수했다.
- **Silent Gear** — 재료와 부품을 조합해 도구와 방어구를 만드는 시스템이다. Silent Lib,
  Silent Gems와 Metalworks를 포함한다.
- **Allthemodium·ATM 장비** — ATM 핵심 광물, 최종 장비와 ATM Star 진행에 쓰인다. Arcanist와
  Wizard 장비, 관련 퀘스트·KubeJS를 포함한다.
- **Draconic Evolution** — 모듈식 최종 장비, 대용량 에너지 저장과 반응로를 제공한다.
- **Iron Jetpacks·장비 편의** — 제트팩 비행, 추가 체력, 도구 벨트와 자석 같은 휴대 장비
  기능이다.
- **Reliquary** — 전리품을 재료로 유물·도구·마법성 아이템을 만드는 모드다.
- **Gateways to Eternity·Hellish Trials** — 소환형 전투 도전과 단계별 보상을 제공한다.
  두 본체, Apotheosis 관련 보상과 퀘스트를 함께 검수했다.

### 전력·물류·기술 자동화

- **Mekanism 계열** — 광물 처리, 화학 물질, 발전과 대형 기계를 제공한다. Generators, Tools,
  Covers, Mekanistic Routers, MEKMM과 멀티블록 안내를 포함한다.
- **Powah!·Flux Networks** — 발전·충방전 장치와 무선 전력망을 제공한다.
- **Pipez·Modern Dynamics·XNet** — 아이템·액체·에너지 물류망과 필터·채널 제어를 제공한다.
- **Create 계열** — 회전력 기반 기계, 공정, 조립과 기차를 제공한다. Dragons Plus, Crafts &
  Additions, Enchantment Industry, Aquatic Ambitions, Hypertube와 Bells & Whistles를 포함한다.
- **Modern Industrialization 계열** — 증기 시대부터 전기·디지털 공정까지 이어지는 산업
  시스템이다. Extended Industrialization과 Industrialization Overdrive를 포함한다.
- **Ender IO** — 기계·발전기와 여러 자원을 한 블록에 운반하는 다중 채널 도관을 제공한다.
- **Immersive Engineering** — 전선·전압·컨베이어와 대형 멀티블록 산업 설비를 제공한다.
- **PneumaticCraft: Repressurized** — 압력·온도·드론 프로그래밍을 이용한 자동화 시스템이다.
- **Industrial Foregoing** — 농사·목축·몹 처리·레이저 채굴을 자동화한다. Souls 연동을 포함한다.
- **Just Dire Things** — 도구·이동·에너지와 자동화 장치를 한 계열로 제공한다.
- **Actually Additions** — 발전기, 기계, 농업과 여러 자동화 장치를 제공한다.
- **Oritech** — 광물 가공, 발전과 대형 산업 기계를 제공한다.
- **Extreme Reactors** — 대형 원자로와 터빈으로 후반 전력을 생산한다.
- **Railcraft Reborn** — 철도 물류, 증기와 대형 철도 설비를 제공한다.
- **Modular Routers** — 모듈을 조합해 아이템·블록·엔티티 작업을 자동화한다.
- **CC: Tweaked** — Lua 컴퓨터와 주변기기로 자동화 프로그램을 만든다. Advanced Peripherals와
  More Red CC 호환을 포함한다.
- **Super Factory Manager** — SFML 텍스트 규칙으로 공장 물류를 제어한다.
- **RFTools 계열** — 건축·전력·저장·유틸리티 장치를 제공한다. Base, Builder, Power,
  Storage와 Utility를 포함한다.
- **XyCraft 계열** — 자원, 기계, 저장 탱크와 기술 블록을 제공한다.
- **LaserIO·MFFS** — 레이저 물류망과 에너지 방어장·포스 필드를 제공한다.
- **Steve's Carts** — 모듈식 광산 수레를 조립해 운송·채굴·농사 작업을 자동화한다.
- **Pylons** — 일정 범위에 효과를 부여하고 수확·청크 관련 작업을 자동화한다.
- **Little Big Redstone·Redstone Pen** — 큰 레드스톤 회로를 작은 블록 안에 만들고 배선을
  편집한다. 회로 편집 UI·인게임 가이드와 발전 과제를 함께 검수했다.
- **QuarryPlus·소형 전력 도구** — 채굴기·펌프·발전기와 전력 측정 도구를 제공한다.
  QuarryPlus, Generator Galore, Energy Meter의 설정과 Jade 표시를 포함한다.

### 농업·자원 생산·몹 자동화

- **Mystical Agriculture 계열** — 작물로 광물과 각종 자원을 생산한다. Agradditions,
  Customization과 Botany Pots 연동을 포함한다.
- **Productive Bees** — 벌의 종과 유전자를 조합해 자원을 생산한다. Modular Bees와 가이드를
  포함한다.
- **Productive Trees** — 다양한 나무를 수집·교배해 자원을 생산한다. Productive Bees 연동과
  인게임 가이드를 포함한다.
- **Hostile Neural Networks** — 몹 데이터 모델을 학습해 전리품을 자동 생산한다.
- **Farmer's Delight 계열** — 조리·주방·농업과 식사 콘텐츠를 확장한다. Cooking for
  Blockheads와 Farming for Blockheads를 포함한다.
- **Pam's HarvestCraft 2** — 작물·과일나무와 대량의 음식·조리 재료를 추가한다.
- **Botany Pots·Botany Trees** — 화분에서 작물과 나무를 자동 재배한다.
- **Productive Metalworks** — 금속을 녹이고 주조해 재료를 생산하는 설비를 제공한다.
- **All The Ores·All The Compressed** — 팩 공통 광물과 단계별 대량 압축 블록을 제공한다.
- **Mama's Herbs and Harvest·Mama's MerryMaking** — 허브·치즈·음료·가공 음식과 계절
  장식·의상을 추가한다. 인게임 가이드·채팅 안내와 효과 설명을 함께 검수했다.
- **Aquaculture 2·Sushi Go Crafting** — 낚시·물고기·낚싯대와 초밥 조리·음식 효과를
  확장한다. 음식 책·효과 설명과 관련 FTB Quests를 포함한다.

### 마법·주문·의식

- **Ars Nouveau 계열** — 문양을 조합해 주문을 만들고 마법 자동화를 구성한다. 설치된 Ars
  애드온, Patchouli 가이드와 관련 퀘스트를 포함한다.
- **Iron's Spells 'n Spellbooks 계열** — 전투 주문, 마법 학파와 주문 장비를 제공한다. Iron's
  Jewelry와 관련 라이브러리를 포함한다.
- **Occultism** — 의식으로 정령과 소환수를 부리고 마법 저장소를 구성한다.
- **Mahou Tsukai** — 마법진과 마력을 사용하는 전투·의식 마법을 제공한다.
- **Forbidden and Arcanus** — 신비 재료, 의식과 마법 장비를 제공한다.
- **Theurgy** — 연성술과 의식으로 재료를 다른 자원으로 변환한다.
- **EvilCraft** — 피와 영혼을 사용하는 마법·기술 혼합 시스템이다. Origins of Darkness
  가이드북을 포함한다.
- **Nature's Aura** — 자연의 오라를 모아 의식과 장치를 작동시킨다.
- **Roots Classic** — 자연 재료로 주문과 의식을 수행한다.

### 탐험·차원·보스

- **The Twilight Forest** — 별도 차원의 던전과 보스를 순서대로 공략한다. 직접 연동,
  퀘스트·KubeJS·발전 과제와 탐험 수첩을 포함한다.
- **L_Ender's Cataclysm** — 고난도 구조물, 보스와 전용 장비를 제공한다.
- **The Undergarden** — 지하 세계를 테마로 한 별도 차원과 생태계를 제공한다.
- **The Aether** — 하늘 차원의 던전·보스·장비와 진행 체계를 제공한다.
- **The Bumblezone** — 벌집 차원에서 탐험·수집·보스 콘텐츠를 진행한다.
- **Eternal Starlight** — 별빛 테마 차원, 생물군계, 던전과 보스를 제공한다.
- **Deeper and Darker** — 딥 다크를 확장하고 다른 차원과 장비를 제공한다.
- **Ice and Fire** — 드래곤과 신화 생물, 전용 장비와 탐험 콘텐츠를 제공한다.
- **Oh The Biomes We've Gone·Regions Unexplored** — 오버월드와 여러 차원의 생물군계를
  확장한다. 두 본체의 생물군계·나무·블록 이름을 함께 검수했다.
- **구조물·던전 모음** — YUNG's Better 시리즈, When Dungeons Arise, Dungeon Crawl,
  Repurposed Structures, Structory와 Moog's Structures의 탐험 구조물 표시 경로를 검수했다.
- **생물·몹 확장 모음** — Enderman Overhaul, Variants&Ventures, Living Things와 Creeper
  Overhaul의 몹 이름·설정·자막을 함께 검수했다.

### 식민지·대형 독립 콘텐츠

- **MineColonies 계열** — 주민 직업·건설·연구를 관리하는 식민지 운영 시스템이다.
  Structurize, Domum Ornamentum, BlockUI, StyleColonies와 TownTalk 범위를 확인했다.
- **SecurityCraft** — 잠금·감시·카메라·키패드·권한 설정으로 건물과 물품을 보호한다.

### 건축·장식·생활

- **Supplementaries·Amendments** — 바닐라 분위기를 유지하면서 생활·장식·상호작용 블록과
  기능을 확장한다.
- **Chipped** — 블록마다 많은 장식 변형과 가공 작업대를 제공한다. 본체와 Rechiseled Chipped
  연동의 검색 이름·설명·표시 경로를 함께 검수했다.
- **Chisel·Rechiseled** — 건축 블록의 다양한 질감 변형을 제공한다. Chisel, Rechiseled와
  Rechiseled: Create를 함께 검수했다.
- **BiblioCraft 계열** — 가구·진열·보관과 대규모 목재 변형을 제공한다. BiblioCraft,
  BiblioWoods와 BiblioBiomes의 현재 영어 원문 전체를 함께 검수했다.
- **Macaw's 시리즈** — 문·창문·지붕·가구·다리 등 건축 부품을 제공한다. Doors, Windows,
  Roofs, Furniture, Bridges, Lights, Fences, Paths, Stairs, Trapdoors와 Holidays를 포함한다.
- **Handcrafted·Refurbished Furniture** — 가구와 실내 장식 블록을 제공한다. 두 본체와 관련
  조합법 표시를 함께 검수했다.
- **FramedBlocks** — 다른 블록의 외형을 입힐 수 있는 건축 프레임을 제공한다. 본체와 AE2·기술
  모드 연동을 함께 검수했다.
- **XTones Reworked** — 여러 색상과 무늬의 대량 장식 블록을 제공한다. 본체, KubeJS 표시
  후보와 조합법 경로를 함께 검수했다.
- **Everything is Copper·Dyenamics** — 구리 장비·건축 부품과 추가 염료 색상 블록을 제공한다.
  관련 FTB Quests와 Dyenamics and Friends 용어 연결을 포함한다.
- **조명·유리 장식 모음** — Luminax, Simply Light, Additional Lights, Glassential Renewed와
  Connected Glass의 조명·특수 유리·연결 유리를 함께 검수했다.
- **Factory Blocks·Construction Sticks** — 공장풍 장식 블록과 블록을 빠르게 놓는 건축
  도구를 제공한다. 툴팁·발전 과제와 조작 안내를 함께 검수했다.

### 복합 시스템·기타

- **Integrated Dynamics 계열** — 변수·논리·터미널·물류·자동조합·스크립트로 복잡한 자동화를
  구성한다. Dynamics, Terminals, Tunnels, Crafting과 Scripting을 포함한다.
- **초중반 기반 시설** — Iron Furnaces, Easy Villagers, Mining Gadgets, Building Gadgets,
  Mob Grinding Utils와 Item Collectors처럼 자주 쓰는 기계·주민·건축·채굴 도구 묶음이다.

## 완료된 작업 기록

완료 기록은 다음 작업을 강제하는 우선순위가 아니라 현재 진행 상태만 보여 준다.

- **Applied Energistics 2 본체:** 언어 파일, 관련 FTB Quests·KubeJS와 GuideME 가이드
  125페이지 완료
- **AE2 GuideME 애드온 11개:** AE2WTLib, EnderDrives, ExtendedAE, AdvancedAE,
  MEGA Cells, Applied Flux, ExpandedAE, AE2 Import Export Card, AE2 Network Analyser,
  ME Requester, Ars Énergistique 완료
- **AE2 추가 연동 모드 6개:** AE2 Crafting Tree, AEInfinityBooster, Applied Mekanistics,
  Immersive Energistics, PolyEng, Soulplied Energistics 언어 46키와 관련 퀘스트 검수 완료
- **Sophisticated 계열:** Core, Backpacks, Storage, Storage In Motion과 관련 퀘스트 완료
- **대형 장비 모드군 4개:** Apotheosis, Relics·Artifacts, Silent Gear,
  Allthemodium·ATM 장비의 언어·관련 퀘스트·KubeJS·가이드 검수와 적용 완료
- **Integrated Dynamics 계열:** 5개 모드와 호환 네임스페이스 2개의 언어 2,948키,
  전용·관련 퀘스트 74키, 인게임 가이드·발전 과제·KubeJS 검수와 적용 완료
- **탐험·차원·보스 모드군 7개:** The Twilight Forest, L_Ender's Cataclysm,
  The Undergarden, The Aether, The Bumblezone, Eternal Starlight, Deeper and Darker의
  본체 언어와 직접 연동 모드, 전용·관련 퀘스트, KubeJS·발전 과제·fallback 표시 경로를
  현재 설치 원문과 대조해 검수하고 적용 완료
- **순차 번역 모드군 13개:** Refined Storage 2, Functional Storage 계열,
  Pipez·Modern Dynamics·XNet, Modular Routers, Hostile Neural Networks,
  Iron Jetpacks·장비 편의, 초중반 기반 시설, Botany Pots·Botany Trees,
  All The Ores·All The Compressed, Productive Metalworks, Compact Machines, Create 계열과
  Modern Industrialization 계열을 각각 검증 가능한 커밋으로 완료하고 실제 게임 적용까지 확인
- **후속 기술·자동화 모드군 10개:** Immersive Engineering, PneumaticCraft: Repressurized,
  Industrial Foregoing, Just Dire Things, Actually Additions, Oritech, Extreme Reactors,
  Railcraft Reborn, CC: Tweaked, Super Factory Manager의 기존 한국어 전체와 새 번역을 현재
  영어 원문에 대조하고, 직접 연동 모드·FTB Quests·KubeJS·가이드·발전 과제·기타 표시 경로를
  계열별로 검수해 각각 커밋하고 실제 게임 적용까지 확인. Super Factory Manager는 새 언어
  280키와 게임 내 SFML 예제 17개를 완료
- **추가 기술·자동화 모드군 5개:** RFTools, XyCraft, LaserIO·MFFS, Pylons,
  Steve's Carts의 언어 2,369키와 FTB Quests 표시 112키를 현재 영어 원문에 대조하고,
  Patchouli 181파일의 표시 문구 772개·KubeJS·발전 과제·설정을 계열별로 검수해
  `0c06cfd`, `9523f06`, `b0dcc80`, `92ed683`, `c13fa3e`로 각각 커밋 완료. Java가
  실행 중이어서 실제 게임 적용은 안전 규칙에 따라 보류
- **마법·최종 장비 모드군 3개:** Draconic Evolution, Iron's Spells 'n Spellbooks 계열,
  Forbidden and Arcanus의 언어 2,652키와 FTB Quests 표시 661키를 현재 영어 원문에
  대조하고, KubeJS·발전 과제·fallback 표시 경로를 검수해 `41863db`, `f95f3be`,
  `f20c293`으로 각각 커밋하고 `source_root`에 적용 완료
- **후속 마법·보안 모드군 6개:** Nature's Aura, Roots Classic, Theurgy, Occultism,
  Mahou Tsukai, SecurityCraft의 기존 한국어 전체와 새 번역을 현재 설치 영어 원문에 대조하고,
  전용·관련 FTB Quests, 가이드·설명서, KubeJS와 발전 과제 표시 경로를 검수해 `e73c246`,
  `a370764`, `0334b0d`, `c1d44a4`, `bb21d20`, `9e9b5a8`로 각각 커밋하고
  `source_root`에 적용 완료
- **순차 번역 모드군 6개:** Reliquary, Farmer's Delight 계열,
  Supplementaries·Amendments, Ice and Fire, Pam's HarvestCraft 2, MineColonies 계열의
  언어 9,707키를 현재 설치 영어 원문과 대조해 검수했다. 검수 후 재사용 5,428키와
  신규·수정 4,279키, 관련 FTB Quests 표시 224키, Ice and Fire 가이드 4파일과
  MineColonies 내장 가이드 4종의 표시 경로를 검증했다. StyleColonies 구조물 팩 메타데이터와
  TownTalk 음성 리소스는 언어 파일이 없는 감사 전용 범위로 확인했다. `b8cbc0f`, `e2178b7`,
  `5bc4711`, `0fe1ff0`, `6c54cd7`, `9a6a201`로 계열별 커밋하고 `game_root`에 적용 완료
- **FTB Quests 공통 제목·탐색 기반:** 공통 범위와 완료 항목별 관련 제목·Task 제목·fallback
  표시 경로를 모두 검수했다.
- **후속 완료 모드군 21개:** 공통 UI 3개, 전투 1개, 기술 자동화 2개, 농업·음식 2개,
  탐험·생물·구조물 3개와 건축·장식 10개 항목을 27개 검증 계열로 나눠 현재 설치 영어
  원문 전체와 대조했다. 언어·FTB Quests·KubeJS·가이드·발전 과제·기타 표시 경로를 계열별로
  검증하고 `600717a`부터 `daa2474`까지 28개 독립 커밋으로 완료했다. Dungeon Crawl은 번역할
  표시 산출물이 없는 감사 전용 범위로 확인했고, 나머지 산출물은 `game_root`에 적용해 현재
  304개 배포 경로의 해시 일치를 확인했다.
