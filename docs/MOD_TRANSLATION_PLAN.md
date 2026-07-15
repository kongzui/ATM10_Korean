# ATM10 주요 모드 번역 안내

## 문서 목적

이 문서는 ATM10 7.1에서 번역할 모드를 고르고 현재 상태를 확인하는 분류·상태 문서다.
선택한 모드의 처리 단계는 `PLAN.md`, 안전·번역·검증·적용·Git 규칙은 `AGENTS.md`, 사용자용
설명과 명령은 `README.md`를 따른다.

표의 위아래 배치와 콘텐츠 분류는 구현 우선순위가 아니다. 사용자는 어떤 분류의 모드든
자유롭게 선택할 수 있고, 서로 다른 분류의 모드를 하나의 작업으로 묶을 수도 있다. 선택하지
않은 모드는 현재 작업이 끝난 뒤 자동으로 이어서 진행하지 않는다.

필요하면 사용자가 선택한 하나 이상의 모드 묶음을 Codex Goal로 진행할 수 있다. Goal은 그때
선택한 범위만 관리하며, 이 문서 전체를 순서대로 실행하는 장기 로드맵으로 사용하지 않는다.

## 기준 환경

- 기준 모드팩: All the Mods 10 7.1
- Minecraft: 1.21.1
- 설치 모드 기준: 2026-07-14 `source_root/mods`의 JAR 480개
- 조사 자료: 설치 JAR, 388개 영어 언어 네임스페이스, FTB Quests 챕터 64개

목록에는 플레이 중 표시 문구가 많거나, 독립적인 진행·UI·가이드·퀘스트가 있거나, ATM10의
대표 콘텐츠로 사용되는 모드를 우선 수록한다. 라이브러리·API·성능 최적화·로더·내부 호환
모드는 사용자 표시 문구가 주요 번역 대상이 아닌 한 독립 항목에서 제외한다. 작은 애드온은
가능한 한 관련 본체의 `함께 확인할 범위`에 묶는다.

모드팩 업데이트 뒤 작업을 시작할 때는 실제 설치 여부와 버전을 다시 확인한다. 설치 목록이
달라졌다면 기억이나 다른 ATM 시리즈 구성을 근거로 추측하지 않고 이 문서를 갱신한다.

표의 `한글 표기`는 사용자가 모드 성격을 쉽게 찾기 위한 안내용 이름이다. 실제 게임 번역에서는
프로젝트 용어집과 공식 모드명 유지 규칙을 다시 적용하며, 이 표의 음역을 자동으로 확정 명칭으로
사용하지 않는다.

### 상태 의미

| 상태 | 의미 |
|---|---|
| 완료 | 전체 검토·검증·산출물 반영을 마치고 적용 완료 또는 보류 사유를 기록함 |
| 부분 완료 | 일부 언어·퀘스트·가이드 또는 공통 범위만 완료됨 |
| 미작업 | 프로젝트 기준의 전체 검토 완료 기록이 없음 |
| 재검수 필요 | 완료 기록은 있으나 원문·버전·적용본 차이로 다시 확인해야 함 |

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

## 공통 문구와 공통 UI

공통 UI는 개별 모드보다 반드시 먼저 해야 하는 선행 작업이 아니다. 독립적으로 선택하거나
다른 모드 작업과 함께 선택할 수 있다.

| 모드·항목 | 한글 표기 | 어떤 모드인가 | 함께 확인할 범위 | 상태 | 선정 근거 |
|---|---|---|---|---|---|
| ATM10 공통 문구 | ATM10 공통 문구 | 특정 모드에 속하지 않는 팩 공통 탐색·목차·그룹·메시지 | FTB Quests, FTB Quests Lang Splitter, KubeJS, All The Tweaks | 완료 | 공통 제목·탐색 전체 검수 완료 |
| Just Enough Items | JEI | 조합법 조회와 아이템 검색 UI | FTB JEI Extras, AE2 JEI Integration, Refined Storage JEI Integration | 완료 | 플레이 전반에서 반복 노출 |
| Jade | 제이드 | 바라보는 블록·엔티티 상태를 보여 주는 오버레이 | 본체 UI, 설정, 상태 표시와 실제 문구 소유 모드 | 완료 | 플레이 전반에서 반복 노출 |
| JourneyMap·FTB Chunks·FTB Teams | 저니맵·FTB 청크·FTB 팀 | 지도, 웨이포인트, 청크 소유와 팀 권한 UI | 세 본체와 관련 키 안내 | 완료 | 초반부터 계속 사용하는 공통 UI |
| Waystones·Compass 계열 | 웨이스톤·탐색 나침반 | 이동 지점과 바이옴·구조물 탐색 도구 | Waystones, Nature's Compass, Explorer's Compass | 완료 | 자주 사용하는 탐색 편의 기능 |
| Curios·효과 표시 | 큐리오·효과 표시 | 장착 슬롯, 마법부여 설명과 추가 오버레이 | Curios, Enchantment Descriptions, More Overlays Updated | 완료 | 장비와 툴팁 전반에 노출 |
| 가이드 프레임워크 UI | 가이드 UI | 여러 모드 가이드북의 검색·목차·버튼을 제공 | GuideME, Modonomicon, Patchouli, Akashic Tome | 완료 | 여러 모드 가이드의 공통 기반 |
| 공통 편의 기능 | 공통 편의 기능 | 채굴, 사망 지점, 전리품과 제작법 충돌을 다루는 UI | FTB Ultimine, Corail Tombstone, Lootr, Polymorph, Ars Polymorphia, Crafting Tweaks | 완료 | 사용 빈도가 높은 편의 기능 |
| 인벤토리·조작 편의 | 인벤토리·조작 편의 | 키 설정, 인벤토리 조작과 정보 표시를 개선 | Controlling, Better Advancements, AppleSkin, Mouse Tweaks, Inventory Tweaks, TrashSlot | 완료 | 신규: 초반부터 계속 노출되는 UI |
| Tempad | 템패드 | 저장한 위치 사이를 이동하는 휴대용 순간이동 도구 | 본체, 관련 퀘스트와 KubeJS | 완료 | 신규: 대표 이동 편의 아이템 |

ATM10 공통 문구 작업에서는 모드 이름·아이템·모드별 퀘스트·모드 전용 KubeJS 문구를
건드리지 않는다. 조사 결과 비모드 공통 문구가 없다면 조사 기록만 남긴다.

JEI 작업에서는 JEI 자체 검색·북마크·버튼·설정·공통 안내를 다룬다. 특정 모드의 아이템·블록
이름, 툴팁과 모드 전용 조합법 문구는 그 모드 작업에서 처리한다. 가이드 프레임워크 작업도
프레임워크 UI만 다루고 각 가이드 본문은 원본 모드 작업에 포함한다.

## 콘텐츠 성격별 모드 목록

분류는 모드를 찾기 쉽게 하기 위한 대표 위치일 뿐 작업 순위가 아니다. 여러 성격을 가진 모드는
가장 대표적인 분류 한 곳에만 두고 다른 성격은 설명과 `함께 확인할 범위`에 적는다.

### 저장소·인벤토리

| 모드 | 한글 표기 | 어떤 모드인가 | 함께 확인할 범위 | 상태 | 선정 근거 |
|---|---|---|---|---|---|
| Sophisticated Backpacks | 소피스티케이티드 백팩 | 필터·자동화·업그레이드를 갖춘 배낭 모드 | Sophisticated Core, Backpacks Create Integration | 완료 | 기존 계획·전 구간 사용 |
| Sophisticated Storage | 소피스티케이티드 스토리지 | 상자·통과 다양한 저장소 업그레이드를 제공 | Sophisticated Core, Storage Create Integration, Storage in Motion | 완료 | 기존 계획·전 구간 사용 |
| Applied Energistics 2 | Applied Energistics 2 (AE2) | 네트워크 기반 디지털 저장소와 자동 제작 시스템 | AE2WTLib, EnderDrives, ExtendedAE, AdvancedAE, MEGA Cells, Applied Flux, ExpandedAE, AE2 Import Export Card, AE2 Network Analyser, ME Requester, Ars Énergistique | 완료 | 기존 완료 기록과 적용본 확인 |
| AE2 추가 연동 모드 | AE2 추가 연동 모드 | AE2 기능을 다른 기술·마법 시스템과 연결 | AE2 Crafting Tree, AEInfinityBooster, Applied Mekanistics, Immersive Energistics, PolyEng, Soulplied Energistics | 미작업 | 기존 계획·설치된 연동 모드 |
| Refined Storage 2 | Refined Storage 2 | 디스크와 그리드를 이용하는 디지털 저장소 시스템 | Extra Disks, Extra Storage, Universal Grid, Refined Types, Curios·Mekanism Integration, Quartz Arsenal | 미작업 | 기존 계획·전용 퀘스트 챕터 |
| Functional Storage·Pocket Storage·EnderStorage | 펑셔널 스토리지·포켓 스토리지·엔더 스토리지 | 대량 저장, 휴대 저장과 원격 공유 저장소를 제공 | 세 본체와 관련 퀘스트·KubeJS | 미작업 | 기존 계획·초중반 저장소 |
| Compact Machines | 컴팩트 머신 | 작은 기계실 차원을 블록 하나에 구성 | 본체, 관련 퀘스트와 연동 | 미작업 | 신규: 독립적인 공간·자동화 시스템 |

### 장비·캐릭터 성장·전투

| 모드 | 한글 표기 | 어떤 모드인가 | 함께 확인할 범위 | 상태 | 선정 근거 |
|---|---|---|---|---|---|
| Apotheosis | 아포테오시스 | 어픽스·보석·소켓·희귀도 기반 장비 성장을 제공 | Apothic Attributes, Apothic Enchanting, Apothic Spawners | 완료 | 기존 계획·전용 퀘스트 다수 |
| Relics·Artifacts | 렐릭·아티팩트 | 장착형 유물과 성장·능력 해금 시스템을 제공 | Relics, Artifacts, Reliquified Artifacts | 완료 | 기존 계획·전용 퀘스트 챕터 |
| Silent Gear | Silent Gear | 재료와 부품을 조합해 장비를 제작하는 시스템 | Silent Lib, Silent Gems, Silent Gear Metalworks | 완료 | 기존 계획·전용 퀘스트 챕터 |
| Allthemodium·ATM 장비 | 올더모디움·ATM 장비 | ATM 핵심 광물, 최종 장비와 ATM Star 진행을 담당 | All The Arcanist Gear, All the Wizard Gear, ATM Star 퀘스트와 KubeJS | 완료 | 기존 계획·팩 핵심 진행 |
| Draconic Evolution | 드라코닉 에볼루션 | 모듈식 최종 장비, 에너지 저장과 반응로를 제공 | Brandon's Core는 의존성으로만 확인, 관련 퀘스트 | 미작업 | 기존 계획·전용 퀘스트 챕터 |
| Iron Jetpacks·장비 편의 | 아이언 제트팩·장비 편의 | 비행, 체력 확장과 휴대 장비 슬롯을 제공 | Iron Jetpacks, Baubley Heart Canisters, Tool Belt, Simple Magnets | 미작업 | 신규: 자주 사용하는 성장·편의 장비 |
| Gateways to Eternity·Hellish Trials | 영원의 관문·지옥의 시련 | 소환형 전투 도전과 단계별 보상을 제공 | 두 본체, Apotheosis 관련 보상과 퀘스트 | 미작업 | 신규: 독립 전투 콘텐츠 |
| Reliquary | 렐리쿼리 | 전리품 기반 유물, 도구와 마법성 아이템을 제공 | 본체, 관련 조합법과 퀘스트 | 미작업 | 신규: 독립 장비·유물 콘텐츠 |

### 전력·물류·기술 자동화

| 모드 | 한글 표기 | 어떤 모드인가 | 함께 확인할 범위 | 상태 | 선정 근거 |
|---|---|---|---|---|---|
| Mekanism | 메카니즘 | 광물 처리, 화학 물질, 발전과 대형 기계를 제공 | Mekanism Generators, Mekanism Tools, Mekanism Covers, Mekanistic Routers, MEKMM, Just Enough Mekanism Multiblocks | 완료 | 기존 계획·대형 퀘스트 챕터 |
| Powah!·Flux Networks | 파와·플럭스 네트워크 | 발전·충방전과 무선 전력망을 제공 | Powah!, Lollipop, Flux Networks, 관련 퀘스트·GuideME·KubeJS·발전 과제 | 완료 | 기존 계획·공통 전력 기반 |
| Pipez·Modern Dynamics·XNet | 파이프즈·모던 다이내믹스·엑스넷 | 아이템·액체·에너지 물류망과 필터를 제공 | 세 본체와 관련 연동 | 미작업 | 기존 계획·공통 물류 기반 |
| Create | Create | 회전력 기반 기계, 공정, 조립과 기차를 제공 | Create: Dragons Plus, Create Crafts & Additions, Create Enchantment Industry, Create Aquatic Ambitions, Create Hypertube, Create: Bells & Whistles | 미작업 | 기존 계획·대형 기술 모드 |
| Modern Industrialization | 모던 인더스트리얼라이제이션 | 증기부터 전기·디지털 공정까지 이어지는 산업 시스템 | Extended Industrialization, Industrialization Overdrive | 미작업 | 기존 계획·전용 퀘스트 4개 |
| Ender IO | Ender IO | 기계, 발전과 다중 채널 도관을 제공 | 본체, 관련 퀘스트와 다른 모드 연동 | 완료 | 기존 계획·대형 기술 모드 |
| Immersive Engineering | 이머시브 엔지니어링 | 전선·전압·컨베이어와 멀티블록 공정을 제공 | 본체, 관련 퀘스트와 가이드 | 미작업 | 기존 계획·대형 퀘스트 챕터 |
| PneumaticCraft: Repressurized | 뉴매틱크래프트: 리프레셔라이즈드 | 압력·온도·드론 프로그래밍 자동화를 제공 | 본체, 관련 퀘스트와 가이드 | 미작업 | 기존 계획·대형 퀘스트 챕터 |
| Industrial Foregoing | 인더스트리얼 포고잉 | 농사·목축·몹 처리·레이저 자동화 기계를 제공 | Industrial Foregoing Souls | 미작업 | 기존 계획·전용 퀘스트 챕터 |
| Just Dire Things | 저스트 다이어 씽즈 | 도구·이동·에너지와 자동화 장치를 함께 제공 | 본체, 관련 퀘스트와 KubeJS | 미작업 | 기존 계획·전용 퀘스트 챕터 |
| Actually Additions | 액추얼리 애디션즈 | 발전, 기계, 농업과 다양한 자동화 장치를 제공 | 본체, 관련 조합법·발전 과제·퀘스트 | 미작업 | 신규: 영어 1,026키의 대표 기술 모드 |
| Oritech | 오리테크 | 광물 가공, 발전과 대형 산업 기계를 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 신규: 전용 퀘스트·영어 1,255키 |
| Extreme Reactors | 익스트림 리액터 | 대형 원자로와 터빈으로 전력을 생산 | 본체, 전용 퀘스트 챕터; ZeroCore는 의존성 | 미작업 | 신규: ATM 후반 발전 콘텐츠 |
| Railcraft Reborn | 레일크래프트 리본 | 철도 물류, 증기와 대형 철도 설비를 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 신규: 전용 퀘스트·영어 1,075키 |
| Modular Routers | 모듈러 라우터 | 모듈을 조합해 아이템·블록·엔티티 작업을 자동화 | 본체, 전용 퀘스트 챕터 | 미작업 | 신규: 자주 쓰는 범용 자동화 |
| CC: Tweaked | CC: 트위크드 | Lua 컴퓨터와 주변기기로 자동화를 프로그래밍 | Advanced Peripherals, More Red CC 호환 | 미작업 | 신규: 독립 프로그래밍 시스템 |
| Super Factory Manager | 슈퍼 팩토리 매니저 | 텍스트 기반 규칙으로 공장 물류를 제어 | 본체, 가이드와 관련 퀘스트 | 미작업 | 신규: 독립 물류 프로그래밍 UI |
| RFTools | 알에프툴즈 | 건축·전력·유틸리티·저장 장치를 제공하는 기술 모음 | Base, Builder, Power, Storage, Utility | 미작업 | 신규: 설치된 주요 기술 모음 |
| XyCraft | 자이크래프트 | 자원, 기계, 저장 탱크와 기술 블록을 제공 | Core, Machines, World, Override | 미작업 | 신규: 전용 퀘스트 챕터 |
| LaserIO·MFFS | 레이저 IO·MFFS | 레이저 물류망과 에너지 방어장·포스 필드를 제공 | 두 본체와 관련 연동 | 미작업 | 신규: 독립 기술 UI와 설정 다수 |
| Steve's Carts | 스티브 카트 | 모듈식 광산 수레를 조립해 운송과 작업을 자동화 | 본체, 관련 조합법과 가이드 | 미작업 | 신규: 영어 709키의 독립 자동화 |
| Pylons | 파일런 | 범위형 효과·수확·청크 관련 자동화 장치를 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 신규: ATM 퀘스트에 포함 |

### 농업·자원 생산·몹 자동화

| 모드 | 한글 표기 | 어떤 모드인가 | 함께 확인할 범위 | 상태 | 선정 근거 |
|---|---|---|---|---|---|
| Mystical Agriculture | 미스티컬 애그리컬처 | 작물로 광물과 각종 자원을 생산 | Mystical Agradditions, Mystical Customization, Botany Pots Mystical, 관련 퀘스트·KubeJS·발전 과제·가이드 | 완료 | 기존 계획·대형 퀘스트 챕터 |
| Productive Bees | 프로덕티브 비즈 | 벌과 유전자를 이용해 자원을 생산 | Modular Bees, 관련 퀘스트·KubeJS·발전 과제·가이드 | 완료 | 기존 계획·가장 큰 퀘스트 챕터 |
| Productive Trees | 프로덕티브 트리즈 | 다양한 나무를 수집·교배해 자원을 생산 | Productive Bees 직접 연동, 전용 퀘스트·KubeJS·발전 과제·가이드 | 완료 | 신규: 전용 퀘스트·영어 4,149키 |
| Hostile Neural Networks | 적대적 신경망 | 몹 데이터 모델을 학습해 전리품을 자동 생산 | 본체, 전용 퀘스트 챕터 | 미작업 | 신규: 대표 몹 자동화 모드 |
| Farmer's Delight 계열 | 파머스 딜라이트 계열 | 조리·주방·농업과 식사 콘텐츠를 확장 | Farmer's Delight, Cooking for Blockheads, Farming for Blockheads | 미작업 | 신규: 음식·농업 퀘스트의 중심 |
| Pam's HarvestCraft 2 | 팸의 하베스트크래프트 2 | 작물·과일나무와 대량의 요리를 추가 | Crops, Food Core, Food Extended, Trees | 미작업 | 신규: 영어 문구와 음식 항목이 많음 |
| Botany Pots·Botany Trees | 보타니 포츠·보타니 트리즈 | 화분에서 작물과 나무를 자동 재배 | 두 본체와 Mystical 연동 | 미작업 | 신규: 초중반 자원 자동화 |
| Productive Metalworks | 프로덕티브 메탈웍스 | 금속 용해·주조와 재료 생산 설비를 제공 | 본체와 다른 자원 모드 연동 | 미작업 | 신규: 영어 376키의 생산 시스템 |
| All The Ores·All The Compressed | 올 더 오어스·올 더 컴프레스드 | 팩 공통 광물과 대량 압축 블록을 제공 | Allthemodium·ATM Star·관련 퀘스트 | 미작업 | 신규: ATM 공통 자원·영어 항목 다수 |

### 마법·주문·의식

| 모드 | 한글 표기 | 어떤 모드인가 | 함께 확인할 범위 | 상태 | 선정 근거 |
|---|---|---|---|---|---|
| Ars Nouveau | 아르스 누보 | 문양을 조합해 주문을 만들고 자동화하는 마법 모드 | Ars Additions, Ars Controle, Ars Creo, Ars Elemancy, Ars Elemental, Ars Ocultas, Ars Technica, Ars Unification, Not Enough Glyphs, Starbuncle Mania, Ars Énergistique, All the Arcanist Gear, 관련 퀘스트·Patchouli·KubeJS·발전 과제 | 완료 | 기존 계획·전용 퀘스트 챕터 |
| Iron's Spells 'n Spellbooks | 아이언의 주문과 마법책 | 전투 주문, 마법 학파와 장비를 제공 | Iron's Jewelry, Iron's Lib는 의존성으로 확인 | 미작업 | 기존 계획·대형 퀘스트 챕터 |
| Occultism | 오컬티즘 | 의식·소환수·정령과 마법 저장소를 제공 | Occultism KubeJS, 사전과 전용 퀘스트 | 미작업 | 기존 계획·대형 퀘스트 챕터 |
| Mahou Tsukai | 마호우 츠카이 | 마법진과 마나를 이용하는 전투·의식 마법 | 본체, 관련 퀘스트 | 미작업 | 기존 계획·전용 퀘스트 챕터 |
| Forbidden and Arcanus | 포비든 앤 아르카누스 | 신비 재료, 의식과 마법 장비를 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 기존 계획·전용 퀘스트 챕터 |
| Theurgy | 테우르기 | 연성술과 재료 변환 의식을 제공 | Theurgy KubeJS, 전용 퀘스트와 가이드 | 미작업 | 기존 계획·전용 퀘스트 챕터 |
| EvilCraft | 이블크래프트 | 피와 영혼을 이용하는 마법·기술 혼합 모드 | 본체, EvilCraft Compat, Origins of Darkness 가이드북, 전용 퀘스트·KubeJS·발전 과제 | 완료 | 기존 계획·전용 퀘스트 챕터 |
| Nature's Aura | 네이처스 오라 | 자연의 오라를 모아 의식과 장치를 작동 | 본체, 전용 퀘스트와 가이드 | 미작업 | 신규: 전용 퀘스트 챕터 |
| Roots Classic | 루츠 클래식 | 자연 재료를 이용한 주문과 의식을 제공 | 본체, 관련 발전 과제와 가이드 | 미작업 | 신규: 영어 483키의 독립 마법 모드 |

### 탐험·차원·보스

| 모드 | 한글 표기 | 어떤 모드인가 | 함께 확인할 범위 | 상태 | 선정 근거 |
|---|---|---|---|---|---|
| The Twilight Forest | 황혼의 숲 | 별도 차원의 던전과 보스를 순서대로 공략 | 본체, Bibliowoods 직접 연동, 전용·관련 퀘스트·KubeJS·발전 과제·탐험 수첩 | 완료 | 기존 계획·대표 차원 모드 |
| L_Ender's Cataclysm | 카타클리즘 | 고난도 구조물, 보스와 전용 장비를 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 기존 계획·보스 콘텐츠 |
| The Undergarden | 언더가든 | 지하 세계를 테마로 한 별도 차원과 생태계를 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 기존 계획·차원 콘텐츠 |
| The Aether | 에테르 | 하늘 차원의 던전·보스·장비와 진행을 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 신규: 전용 퀘스트·영어 1,238키 |
| The Bumblezone | 범블존 | 벌집 차원에서 탐험·수집·보스 콘텐츠를 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 신규: 전용 퀘스트·영어 1,788키 |
| Eternal Starlight | 이터널 스타라이트 | 별빛 테마 차원, 생물군계, 던전과 보스를 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 신규: 전용 퀘스트·영어 1,788키 |
| Deeper and Darker | 디퍼 앤 다커 | 딥 다크를 확장하고 다른 차원과 장비를 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 신규: 전용 퀘스트 챕터 |
| Ice and Fire | 아이스 앤 파이어 | 드래곤과 신화 생물, 장비와 탐험 콘텐츠를 제공 | 본체, 전용 퀘스트 챕터 | 미작업 | 신규: 전용 퀘스트·영어 1,744키 |
| Oh The Biomes We've Gone·Regions Unexplored | 오 더 바이옴즈 위브 곤·리전스 언익스플로어드 | 오버월드와 여러 차원의 생물군계를 확장 | 두 본체와 나무·블록 이름 | 미작업 | 신규: 대규모 생물군계·영어 항목 다수 |
| 구조물·던전 모음 | 구조물·던전 모음 | 월드 곳곳에 던전과 탐험 구조물을 추가 | YUNG's Better 시리즈, When Dungeons Arise, Dungeon Crawl, Repurposed Structures, Structory, Moog's Structures | 미작업 | 신규: 설치된 대표 구조물 모드 묶음 |

### 식민지·대형 독립 콘텐츠

| 모드 | 한글 표기 | 어떤 모드인가 | 함께 확인할 범위 | 상태 | 선정 근거 |
|---|---|---|---|---|---|
| MineColonies | 마인콜로니 | 주민 직업·건설·연구를 관리하는 식민지 운영 모드 | Structurize, Domum Ornamentum, BlockUI, StyleColonies, TownTalk | 미작업 | 기존 계획·영어 3,817키의 대형 콘텐츠 |
| SecurityCraft | 시큐리티크래프트 | 잠금·감시·보호 블록과 보안 설정을 제공 | 본체, 카메라·키패드·권한 UI | 미작업 | 신규: 영어 1,521키·높은 UI 비중 |

### 건축·장식·생활

| 모드 | 한글 표기 | 어떤 모드인가 | 함께 확인할 범위 | 상태 | 선정 근거 |
|---|---|---|---|---|---|
| Chipped | 칩드 | 블록마다 많은 장식 변형과 가공 작업대를 제공 | 본체, Rechiseled Chipped 연동 | 미작업 | 신규: 영어 7,265키의 대형 장식 모드 |
| Chisel·Rechiseled | 치즐·리치즐드 | 건축 블록의 다양한 질감 변형을 제공 | Chisel, Rechiseled, Rechiseled: Create | 미작업 | 신규: 영어 블록 이름이 매우 많음 |
| BiblioCraft 계열 | 비블리오크래프트 계열 | 가구·진열·보관과 대규모 목재 변형을 제공 | BiblioCraft, BiblioWoods, BiblioBiomes | 미작업 | 신규: 설치 목록 최대 규모의 언어 항목 |
| Macaw's 시리즈 | 마코 시리즈 | 문·창문·지붕·가구·다리 등 건축 부품을 제공 | 설치된 Macaw's Doors, Windows, Roofs, Furniture, Bridges, Lights, Fences, Paths, Stairs, Trapdoors, Holidays | 미작업 | 신규: 여러 건축 애드온이 함께 설치됨 |
| Supplementaries·Amendments | 서플리멘터리즈·어멘드먼츠 | 바닐라풍 생활·장식·상호작용 요소를 확장 | 두 본체와 관련 퀘스트·설정 | 미작업 | 신규: 널리 쓰이는 생활 확장 모드 |
| Handcrafted·Refurbished Furniture | 핸드크래프티드·리퍼비시드 퍼니처 | 가구와 실내 장식 블록을 제공 | 두 본체와 관련 조합법 | 미작업 | 신규: 영어 장식 항목이 많음 |
| FramedBlocks | 프레임드 블록 | 다른 블록의 외형을 입힐 수 있는 건축 프레임을 제공 | 본체, AE2·기술 모드 연동 | 미작업 | 신규: 범용 건축·위장 블록 |

### 복합 시스템·기타

| 모드 | 한글 표기 | 어떤 모드인가 | 함께 확인할 범위 | 상태 | 선정 근거 |
|---|---|---|---|---|---|
| Integrated Dynamics 계열 | 인티그레이티드 다이내믹스 계열 | 변수·논리·터미널·물류·자동조합·스크립트를 제공 | Integrated Dynamics, Integrated Terminals, Integrated Tunnels, Integrated Crafting, Integrated Scripting, 호환 네임스페이스·관련 퀘스트·가이드 | 완료 | 기존 계획·전용 퀘스트 챕터 |
| 초중반 기반 시설 | 초중반 기반 시설 | 자주 쓰는 기계·주민·건축·채굴·몹 처리 도구 묶음 | Iron Furnaces, Easy Villagers, Mining Gadgets, Building Gadgets, Mob Grinding Utils, Item Collectors | 미작업 | 기존 계획·작은 독립 모드 묶음 |

## 완료된 작업 기록

완료 기록은 다음 작업을 강제하는 우선순위가 아니라 현재 진행 상태만 보여 준다.

- **Applied Energistics 2 본체:** 언어 파일, 관련 FTB Quests·KubeJS와 GuideME 가이드
  125페이지 완료
- **AE2 GuideME 애드온 11개:** AE2WTLib, EnderDrives, ExtendedAE, AdvancedAE,
  MEGA Cells, Applied Flux, ExpandedAE, AE2 Import Export Card, AE2 Network Analyser,
  ME Requester, Ars Énergistique 완료
- **Sophisticated 계열:** Core, Backpacks, Storage, Storage In Motion과 관련 퀘스트 완료
- **대형 장비 모드군 4개:** Apotheosis, Relics·Artifacts, Silent Gear,
  Allthemodium·ATM 장비의 언어·관련 퀘스트·KubeJS·가이드 검수와 적용 완료
- **Integrated Dynamics 계열:** 5개 모드와 호환 네임스페이스 2개의 언어 2,948키,
  전용·관련 퀘스트 74키, 인게임 가이드·발전 과제·KubeJS 검수와 적용 완료
- **FTB Quests 공통 제목·탐색 기반:** 일부 완료. 다른 모드의 미완성 제목과 fallback은
  해당 모드를 선택했을 때 함께 검토
