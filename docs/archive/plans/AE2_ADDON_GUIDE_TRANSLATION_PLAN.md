# AE2 연동 모드 GuideME 가이드 한국어 번역 계획

## 1. 목표

AE2 본체 가이드 125페이지 번역이 끝난 상태에서, 현재 ATM10 설치본에 포함된 AE2 연동
모드의 GuideME 가이드를 한국어로 번역한다.

이번 계획의 조사 범위는 특정 모드 이름만 고른 목록이 아니라 `source_root/mods`의 전체 JAR
480개를 읽기 전용으로 검사하여 확인한 모든 `assets/*/ae2guide/**/*.md` 영어 원문이다.
AE2 본체를 제외하면 11개 모드, 99페이지, 영어 단어 약 13,939개가 남아 있다. 이는 AE2
본체 가이드와 비교해 페이지 수로 약 79%, 영어 단어 수로 약 47%다.

99페이지의 실제 작업 구성은 다음과 같다.

- 신규 한국어 페이지: 98개
- 기존 AE2 한국어 페이지 호환성 재검토: 1개
  (`items-blocks-machines/wireless_terminals.md`)
- 현재 연동 모드 전용 GuideME 한국어 페이지: 0개

페이지별 단어 수는 Markdown 태그를 제외한 라틴 문자 토큰을 센 대략적인 작업량 지표다.
번역 문자열 수나 최종 한국어 어절 수와 같지는 않다.

## 2. 기준 환경과 조사 결과

조사 기준일은 2026-07-13이며, 경로는 Git 제외 파일 `local_paths.json`에서 읽었다.

- 원본 조회 경로: `C:/Users/moon9653nb/Desktop/ATM10_source`
- 실제 게임 경로: 미설정
- GuideME: `guideme-21.1.16.jar`
- AE2 본체: `appliedenergistics2-19.2.17.jar`
- AE2 본체 완료 상태: 125/125페이지, 게임 화면 검증은 아직 미완료

원본 JAR은 ZIP 형식으로 열어 파일명과 내용을 읽기만 했다. 추출, 수정, 재압축 또는
프로젝트 저장소로의 복사는 수행하지 않는다.

### 연동 모드별 가이드 분량

| 모드 | 설치 JAR | 영어 페이지 | 영어 단어(약) | 부속 리소스 | 기존 한국어 언어 파일 참고 자료 |
|---|---|---:|---:|---|---|
| AE2WTLib | `ae2wtlib-19.5.0.jar` | 8 | 1,044 | 없음 | 26/46키 |
| EnderDrives | `enderdrives-neoforge-1.21.1-1.4.4.jar` | 3 | 858 | PNG 3개 | 없음 |
| ExtendedAE | `ExtendedAE-1.21-2.2.33-neoforge.jar` | 46 | 2,754 | PNG 140개, SNBT 129개 | 78/253키 |
| AdvancedAE | `AdvancedAE-1.6.11-1.21.1.jar` | 13 | 3,231 | PNG 18개, SNBT 18개 | 246/246키 |
| MEGA Cells | `megacells-4.11.0.jar` | 7 | 3,783 | PNG 56개, SNBT 12개 | 없음 |
| Applied Flux | `AppliedFlux-1.21-2.1.5-neoforge.jar` | 12 | 419 | PNG 3개, SNBT 1개 | 없음 |
| ExpandedAE | `expandedae-2.1.1.jar` | 5 | 360 | PNG 12개, SNBT 7개 | 없음 |
| AE2 Import Export Card | `ae2importexportcard-1.21.1-1.5.0.jar` | 1 | 221 | PNG 2개 | 5/5키 |
| AE2 Network Analyser | `AE2NetworkAnalyzer-1.21-2.1.5-neoforge.jar` | 2 | 454 | PNG 5개 | 없음 |
| ME Requester | `merequester-neoforge-1.21.1-1.4.3.jar` | 1 | 813 | PNG 1개 | 없음 |
| Ars Énergistique | `arseng-2.1.1-beta.jar` | 1 | 2 | 없음 | 없음 |
| **합계** |  | **99** | **13,939** |  |  |

표의 기존 한국어는 각 모드 JAR에 포함된 `ko_kr.json` 키 수다. 완성된 정답이 아니라
영어 원문과 프로젝트 용어집에 대조할 참고 자료로만 사용한다. AdvancedAE, ExtendedAE,
ExpandedAE, MEGA Cells에는 다른 언어의 가이드 번역도 있지만 영어 가이드를 원문으로 삼는다.

### GuideME 가이드가 없는 AE2 연동 모드

JAR 메타데이터에서 AE2 의존성 또는 연동을 확인했지만 영어 GuideME Markdown을 제공하지 않는
모드는 이번 가이드 계획에서 제외한다.

- AE2 Crafting Tree, AE2 JEI Integration, AEInfinityBooster
- Applied Mekanistics, Immersive Energistics, PolyEng, Soulplied Energistics
- Advanced Peripherals, Ars Unification, Ender IO, FramedBlocks
- All The Tweaks, Modern Industrialization 및 기타 선택적 AE2 연동 모드

이 모드들의 일반 언어 파일, 툴팁, FTB Quests 또는 KubeJS 문구는 별도의 모드 번역 범위다.

## 3. 먼저 확인하고 해결할 사항

### 연동 모드 아이템 이름 선행 확정

현재 출력 리소스팩에는 AE2 본체 `assets/ae2/lang/ko_kr.json`만 있고, 가이드 대상 연동
모드 11개 언어 네임스페이스의 검증된 한국어 언어 파일은 없다. AE2 Import Export Card도 실제
언어 네임스페이스는 `ae2importexportcard`이므로 현재 AE2 언어 파일로 완료된 것이 아니다.

각 모드의 가이드 배치를 시작하기 전에 다음 관문을 통과해야 한다.

1. 해당 가이드가 참조하는 아이템, 블록, 기계와 UI 키를 모두 수집한다.
2. 영어 언어 파일과 프로젝트 용어집, AE2 본체 번역, 기존 FTB Quests 번역을 대조한다.
3. 프로젝트에서 사용할 한국어 이름을 확정하고 해당 모드의 검증된 `ko_kr.json`에 반영한다.
4. 가이드 제목과 본문의 명칭이 출력 리소스팩의 이름과 정확히 일치하는지 검사한다.

가이드에 필요한 이름만 임시로 정한 뒤 언어 파일 없이 완료 처리하지 않는다. 모드 전체 언어
파일 번역을 별도 작업으로 진행한다면, 해당 결과가 먼저 커밋된 뒤 가이드 배치를 시작한다.

### AE2WTLib의 동일 경로 덮어쓰기

전체 JAR을 비교한 결과 영어 GuideME 경로가 충돌하는 문서는 정확히 1개다.

`assets/ae2/ae2guide/items-blocks-machines/wireless_terminals.md`

- AE2 19.2.17 원문: 74줄, 무선 터미널과 무선 제작 터미널을 한 페이지에서 설명
- AE2WTLib 19.5.0 원문: 56줄, 무선 제작 터미널 설명을 AE2WTLib 전용 페이지 링크로 이동
- 현재 한국어 파일: 74줄, AE2 본체 원문 구조를 따름

AE2WTLib 배치에서는 두 JAR 원문을 다시 비교하고, 설치 조합에서 실제로 필요한 AE2WTLib의
교차 네임스페이스 링크를 보존하도록 기존 한국어 페이지를 갱신한다. 이 파일은 신규 페이지가
아니라 기존 AE2 본체 번역 1개의 호환성 수정으로 기록한다.

### 특수 경로와 렌더링 구문

- AE2 Import Export Card의 가이드는 자체 네임스페이스가 아니라
  `assets/ae2/ae2guide/ae2importexportcard-index.md`에 들어 있다.
- 원문에는 상대 링크 외에 `ae2:`와 `ae2wtlib:` 교차 네임스페이스 링크가 있다.
- 보호 대상 태그에는 `GameScene`, `ImportStructure`, `ItemLink`, `RecipeFor`,
  `RecipesFor`, `Recipe`, `ItemImage`, `BlockImage`, `ItemGrid`, `CategoryIndex`,
  `SubPages`, `BoxAnnotation`, `FloatingImage` 등이 있다.
- ExtendedAE는 장면과 구조 파일이 특히 많으므로 Markdown만 검사해서 완료 처리하지 않는다.
- ExpandedAE의 `cards.md`와 `exp_encoding.md`는 일반적인 H1 제목이 없으므로 제목이 없다는
  이유만으로 오류로 판단하지 않고 front matter와 실제 렌더링 구조를 확인한다.
- Ars Énergistique는 색인 1페이지와 제목 정도만 있어 작업량은 작지만, 공식 모드명과 링크
  노출 여부를 게임에서 확인해야 한다.

## 4. 프로젝트 경로

### 작업본

- 일반 연동 모드:
  `working/ae2_addons/<namespace>/ae2guide/_ko_kr/`
- AE2 Import Export Card:
  `working/ae2_addons/ae2importexportcard/ae2guide/_ko_kr/`
- AE2WTLib 충돌 페이지:
  `working/ae2/ae2guide/_ko_kr/items-blocks-machines/wireless_terminals.md`
- 통합 진행 기록:
  `working/ae2_addons/guide_progress.json`
- 전체 완료 기록:
  `working/ae2_addons/guide_completion.json`

충돌 페이지의 작업본을 두 위치에 중복 생성하지 않는다. 기존 AE2 작업본을 단일 원본으로
유지하고 연동 모드 진행 기록에서 해당 파일을 참조한다.

### 검증된 리소스팩 산출물

- 일반 형식:
  `output/resourcepack/ATM10_Korean/assets/<namespace>/ae2guide/_ko_kr/`
- AE2WTLib 충돌 페이지와 AE2 Import Export Card:
  `output/resourcepack/ATM10_Korean/assets/ae2/ae2guide/_ko_kr/`

이미지와 SNBT 구조 파일은 원본 JAR에서 그대로 제공되므로 번역 산출물에 복제하지 않는다.
한국어 Markdown이 참조하는 원본 리소스가 JAR 안에 존재하는지만 검증한다.

### 실제 인스턴스 적용 경로

검증된 결과는 다음 리소스팩 아래에 누적한다.

- `source_root/resourcepacks/ATM10_Korean/assets/...`
- `game_root/resourcepacks/ATM10_Korean/assets/...` (`game_root`가 설정된 경우만)

현재 `game_root`는 비어 있으므로 계획 시점에는 `source_root`만 적용 대상이다. 적용 전
Minecraft/Java 프로세스를 확인하며, 실행 중이면 적용과 백업을 수행하지 않고 대기 상태로 남긴다.

## 5. 번역 배치 계획

모드 경계를 우선해 배치를 나누고, 긴 모드만 기능별로 분리한다. 한 배치는 번역, 자동 검증,
수동 문서 검토, 커밋, 안전 적용까지 끝나야 다음 배치로 넘어간다. 여러 모드가 한 배치에 있는
경우에도 모드별로 독립 검증하고 독립 커밋할 수 있어야 한다.

### 1차 배치 — AE2WTLib 무선 터미널

- 8페이지, 약 1,044단어
- 신규 7페이지, 기존 AE2 페이지 수정 1개

대상:

- `assets/ae2/ae2guide/items-blocks-machines/wireless_terminals.md`
- `assets/ae2wtlib/ae2guide/ae2wtlib/ae2wtlib-index.md`
- `assets/ae2wtlib/ae2guide/ae2wtlib/magnet_card.md`
- `assets/ae2wtlib/ae2guide/ae2wtlib/quantum_bridge_card.md`
- `assets/ae2wtlib/ae2guide/ae2wtlib/restock.md`
- `assets/ae2wtlib/ae2guide/ae2wtlib/wireless_crafting_terminal.md`
- `assets/ae2wtlib/ae2guide/ae2wtlib/wireless_terminals.md`
- `assets/ae2wtlib/ae2guide/ae2wtlib/wireless_universal_terminal.md`

### 2차 배치 — EnderDrives

- 3페이지, 약 858단어

대상:

- `enderdrives_intro/enderdrives_intro-index.md`
- `enderdrives_intro/enderdrives_intro.md`
- `enderdrives_intro/tapedrive_intro.md`

Ender Drive와 Tape Disk Drive의 저장 방식, 수치, 디스크/드라이브 관계를 생략하지 않는다.

### 3차 배치 — ExtendedAE 재료·입문

- 11페이지, 약 378단어

대상:

- `epp_intro/epp_intro-index.md`
- `epp_intro/machine_frame.md`
- `epp_intro/quartz_blend.md`
- `epp_intro/silicon_block.md`
- `epp_intro/entro_block.md`
- `epp_intro/entro_budding.md`
- `epp_intro/entro_crystal.md`
- `epp_intro/entro_dust.md`
- `epp_intro/entro_ingot.md`
- `epp_intro/entro_seed.md`
- `epp_intro/entro_shard.md`

### 4차 배치 — ExtendedAE 저장·설정

- 10페이지, 약 690단어

대상:

- `epp_intro/config_modifier.md`
- `epp_intro/extended_drive.md`
- `epp_intro/infinity_cell.md`
- `epp_intro/ingredient_buffer.md`
- `epp_intro/mod_storage_bus.md`
- `epp_intro/oversize_interface.md`
- `epp_intro/packing_tape.md`
- `epp_intro/pattern_modifier.md`
- `epp_intro/precise_storage_bus.md`
- `epp_intro/void_cell.md`

### 5차 배치 — ExtendedAE 자동 제작·기계

- 13페이지, 약 870단어

대상:

- `epp_intro/assembler_matrix.md`
- `epp_intro/caner.md`
- `epp_intro/circuit_cutter.md`
- `epp_intro/concurrent_processor.md`
- `epp_intro/crystal_assembler.md`
- `epp_intro/crystal_fixer.md`
- `epp_intro/extended_charger.md`
- `epp_intro/extended_inscriber.md`
- `epp_intro/extended_interface.md`
- `epp_intro/extended_io_port.md`
- `epp_intro/extended_modecular_assembler.md`
- `epp_intro/extended_pattern_provider.md`
- `epp_intro/extended_pattern_terminal.md`

원문 파일명 `extended_modecular_assembler.md`와 `caner.md`의 철자는 수정하지 않는다.
사용자 표시 이름만 출력 언어 파일의 확정 명칭에 맞춘다.

### 6차 배치 — ExtendedAE 네트워크·입출력

- 12페이지, 약 816단어

대상:

- `epp_intro/active_formation_plane.md`
- `epp_intro/extended_io_bus.md`
- `epp_intro/mod_export_bus.md`
- `epp_intro/precise_export_bus.md`
- `epp_intro/smart_annihilation_plane.md`
- `epp_intro/tag_export_bus.md`
- `epp_intro/tag_storage_bus.md`
- `epp_intro/threshold_export_bus.md`
- `epp_intro/threshold_level_emitter.md`
- `epp_intro/upgrade_items.md`
- `epp_intro/wireless_connector.md`
- `epp_intro/wireless_hub.md`

### 7차 배치 — AdvancedAE 자동화·입출력

- 8페이지, 약 968단어

대상:

- `aae_intro/aae_intro-index.md`
- `aae_intro/advanced_io_bus.md`
- `aae_intro/advanced_pattern_encoder.md`
- `aae_intro/advanced_pattern_provider.md`
- `aae_intro/app_upgrade_items.md`
- `aae_intro/import_export_bus.md`
- `aae_intro/stock_export_bus.md`
- `aae_intro/throughput_monitor.md`

### 8차 배치 — AdvancedAE 양자 장비·기계

- 5페이지, 약 2,263단어

대상:

- `aae_intro/quantum_armor.md`
- `aae_intro/quantum_computer.md`
- `aae_intro/quantum_crafter.md`
- `aae_intro/quantum_crafter_terminal.md`
- `aae_intro/reaction_chamber.md`

페이지 수는 적지만 설명량과 장면 내부 문구가 많다. 방어구 능력, 슬롯, 에너지 소비,
처리량과 조건을 항목별로 원문과 대조한다.

### 9차 배치 — MEGA Cells 저장소

- 4페이지, 약 2,881단어

대상:

- `index.md`
- `storage.md`
- `bulk_cell.md`
- `radioactive_cell.md`

`bulk_cell.md` 한 페이지가 약 2,027단어이므로 단일 페이지라도 별도 세부 검토표를 사용한다.
바이트, 타입 수, 용량, 한계값과 방사성 화학 셀의 조건을 숫자 단위까지 대조한다.

### 10차 배치 — MEGA Cells 제작·에너지·기타

- 3페이지, 약 902단어

대상:

- `crafting.md`
- `energy.md`
- `extras.md`

### 11차 배치 — Applied Flux

- 12페이지, 약 419단어

대상:

- `appflux/appflux-index.md`
- `appflux/diamond_dust.md`
- `appflux/emerald_dust.md`
- `appflux/energy_processor.md`
- `appflux/flux_accessor.md`
- `appflux/flux_cells.md`
- `appflux/induction_card.md`
- `appflux/insulating_resin.md`
- `appflux/mark_energy.md`
- `appflux/portable_flux_cells.md`
- `appflux/redstone_crystal.md`
- `appflux/terminal_interact.md`

FE와 AE의 저장·전달·변환 관계, 단위 표기와 터미널 조작 방향을 보존한다.

### 12차 배치 — ExpandedAE

- 5페이지, 약 360단어

대상:

- `cards.md`
- `exp_encoding.md`
- `exp_pp.md`
- `expandedae-index.md`
- `qol-features.md`

### 13차 배치 — AE2 소형 유틸리티

- 2개 모드, 3페이지, 약 675단어

대상:

- AE2 Import Export Card:
  `assets/ae2/ae2guide/ae2importexportcard-index.md`
- AE2 Network Analyser:
  `assets/ae2netanalyser/ae2guide/ae2_network_analyser.md`
- AE2 Network Analyser:
  `assets/ae2netanalyser/ae2guide/ae2_tick_profiler.md`

두 모드는 산출물 네임스페이스와 언어 파일을 섞지 않고 각각 독립 검증·커밋한다.

### 14차 배치 — ME Requester

- 1페이지, 약 813단어

대상:

- `assets/merequester/ae2guide/merequester.md`

요청 수량, 유지 조건, 제작 요청 동작과 상태 표시 문구를 빠짐없이 대조한다.

### 15차 배치 — Ars Énergistique 색인

- 1페이지, 약 2단어

대상:

- `assets/arseng/ae2guide/arseng-index.md`

공식 모드명은 `Ars Énergistique`를 유지한다. 페이지가 가이드 목차에 보이는지와 빈 페이지처럼
렌더링되지 않는지는 게임 화면에서 확인한다.

## 6. 배치별 작업 절차

각 배치는 다음 순서로 처리한다.

1. `local_paths.json`에서 `source_root`를 읽고 대상 JAR 이름과 SHA-256을 기록한다.
2. JAR을 읽기 전용으로 열어 영어 Markdown과 참조 리소스 목록을 확정한다.
3. 해당 모드의 영어 언어 파일, 기존 한국어 후보, 출력 리소스팩과 용어집을 대조한다.
4. 가이드에 등장하는 아이템·블록·기계 이름을 출력 언어 파일에 먼저 확정한다.
5. 작업본의 정확한 `_ko_kr` 경로에 영어 원문과 같은 파일 구조로 번역한다.
6. 제목, 본문, 링크 문구, 이미지 대체 문구와 장면 내부 사용자 표시 문구를 번역한다.
7. 자동 검증을 통과한 배치 파일만 출력 리소스팩에 누적한다.
8. 작업본과 출력의 파일 목록과 SHA-256을 비교한다.
9. Minecraft/Java 프로세스를 확인하고 실행 중이 아니면 기존 대상 파일을 백업해 적용한다.
10. 적용 전후 스냅샷으로 지정 대상 외 인스턴스 변경이 없는지 확인한다.
11. 미확인 항목이 없을 때만 해당 배치를 독립 커밋하고 진행 기록을 갱신한다.
12. 실제 화면 검증이 필요한 항목은 완료로 꾸미지 않고 별도 목록에 남긴다.

원본 JAR, 월드, 설정, 캐시와 로그는 수정하지 않는다. `game_root`가 계속 비어 있으면
`source_root`에만 적용한다.

## 7. 번역 규칙

- 영어 원문을 기준으로 번역하고 다른 언어 가이드는 의미 확인에만 참고한다.
- 기존 모드 한국어는 프로젝트 용어집과 AE2 본체 번역에 맞는지 검토한 뒤 선택한다.
- 공식 모드명은 영어 표기를 유지한다.
- `ME`, `AE`, `FE`, `P2P`, `NBT`, `GUI` 등 기능 구분에 필요한 약어를 임의로 없애지 않는다.
- 아이템, 블록과 기계 이름은 출력 리소스팩의 해당 키 값과 정확히 일치시킨다.
- `Upgrade`는 `업그레이드`, `Advanced` 등급은 원칙적으로 `고급`을 사용한다.
- 수치, 조건, 방향, 채널, 전력, 저장 용량, 슬롯과 입출력 관계를 생략하거나 바꾸지 않는다.
- front matter의 키, ID 목록과 navigation 경로는 원문 그대로 보존한다.
- GuideME 태그명, 속성명, ID, 링크 대상, 이미지 경로, 인라인 코드와 레시피 ID는 번역하지 않는다.
- 링크 문구, 이미지 대체 문구, 제목과 장면 안의 사용자 표시용 주석만 자연스럽게 번역한다.
- 원문 자체의 오탈자는 경로나 ID에서 고치지 않는다. 의미에 영향을 주면 진행 기록의 원문
  이슈로 남기고 번역문에서만 자연스럽게 표현한다.

## 8. 자동화와 검증

AE2 본체 전용 `scripts/build_ae2_guide.py`와 `scripts/verify_ae2_guide.py`를 연동 모드
경로까지 무리하게 하드코딩하지 않는다. 기존 검증 로직을 재사용하되 다음 역할의 별도 스크립트를
추가하는 방향으로 구현한다.

- `scripts/build_ae2_addon_guides.py`
  - 모드별 JAR 파일명, 원문 guide root, 출력 namespace와 배치 목록 관리
  - JAR을 읽기 전용으로 사용
  - 검증된 현재 배치만 출력에 누적
  - AE2WTLib 충돌 페이지와 AE2 Import Export Card의 `assets/ae2` 예외 매핑 지원
- `scripts/verify_ae2_addon_guides.py`
  - 여러 guide root와 교차 네임스페이스 링크 해석
  - 원본 Markdown, PNG, SNBT 참조 존재 확인
  - 모드별 작업본·출력·적용본 비교

각 배치에서 다음 항목을 모두 검사한다.

- 대상 JAR 이름과 SHA-256, 영어 원문 경로의 일치
- 작업본과 출력의 대상 파일 목록 일치
- 모든 한국어 파일에 대응하는 영어 원문 존재
- 누락 파일, 추가 파일, 중복 소유 경로 없음
- UTF-8 BOM 없음
- front matter 키, navigation, categories, item_ids 보존
- GuideME 태그명, 속성, ID, 구조와 순서 보존
- `ImportStructure`, `Recipe`, `RecipeFor`, `RecipesFor` 보호
- 상대 링크, 앵커, `ae2:`와 `ae2wtlib:` 링크 해석 성공
- 이미지와 SNBT 구조 참조가 제공 JAR 중 하나에 존재
- 인라인 코드, 숫자, 단위, URL과 자리표시자 보존
- 영어 제목, 영어 문단과 이미지 대체 문구 잔존 후보 0개
- 작업본과 출력 파일별 SHA-256 일치
- 적용 후 출력과 대상 파일별 SHA-256 일치
- 예상 밖 인스턴스 변경 0개

영어 고유명사, 모드명, 기술 약어와 코드는 영어 잔존 검사 허용 목록에 명시한다. 단순 정규식
통과만으로 번역 완료를 판단하지 않는다.

## 9. FTB Quests와 KubeJS 연계 범위

읽기 전용 조사에서 다음 관련 파일을 확인했다.

- FTB Quests:
  `config/ftbquests/quests/chapters/applied_energistics_2.snbt`
- FTB Quests:
  `config/ftbquests/quests/chapters/extended__advanced_ae.snbt`
- KubeJS: AdvancedAE, ExtendedAE, MEGA Cells의 제작법 및 아이템 ID 참조 스크립트

FTB Quests 한국어 산출물에는 이미 AE2와 MEGA Cells 설명, `Extended AE 및 Advanced AE`
챕터 제목 등이 있다. 이번 가이드 작업에서는 가이드에 확정한 아이템 이름과 기존 퀘스트 표현을
교차 검토한다. 실제 불일치가 발견되면 가이드 배치와 섞지 않고 별도 FTB Quests 수정 단위로
기록한다.

확인된 KubeJS 관련 줄은 제작법과 아이템 ID 참조이며 새로 번역할 사용자 표시 리터럴은 발견하지
못했다. 따라서 계획 시점에는 KubeJS 수정이 없다. 이후 화면 조사에서 KubeJS가 생성한 영어 이름이
발견될 때만 출처를 확인해 별도 범위로 처리한다.

## 10. 게임 화면 검증

자동 검증 후 다음 항목은 실제 게임에서 직접 확인해야 한다.

1. GuideME 목차에 11개 연동 모드 색인이 정상적으로 보이는가
2. 각 모드 색인에서 모든 하위 페이지로 이동할 수 있는가
3. AE2WTLib의 무선 제작 터미널 링크가 새 전용 페이지로 이동하는가
4. `ae2:`와 `ae2wtlib:` 링크가 올바른 네임스페이스 페이지를 여는가
5. ExtendedAE와 AdvancedAE의 GameScene, 구조물과 장면 주석이 잘리지 않는가
6. 이미지, 아이템 격자, 레시피와 블록 미리보기가 정상 렌더링되는가
7. 출력 언어 파일의 아이템명과 페이지 제목이 JEI 및 인벤토리 표시와 같은가
8. 긴 MEGA Cells 페이지의 표, 목록, 숫자와 스크롤 위치가 정상인가
9. ExpandedAE의 H1 없는 페이지와 Ars Énergistique 색인이 빈 페이지처럼 보이지 않는가
10. 한국어 줄바꿈, 링크 글자와 이미지 대체 문구가 UI 폭을 넘지 않는가

AE2 본체 125페이지의 게임 화면 검증도 아직 남아 있다. 연동 모드 번역의 파일 작업을 시작하는
것을 막지는 않지만, 전체 AE2 계열 가이드 완료 선언 전에는 본체와 연동 모드를 함께 화면 검수한다.

## 11. 커밋과 적용 원칙

- 번역, 검증, 적용이 끝난 배치만 독립 커밋한다.
- 서로 다른 모드의 파일은 같은 커밋에 섞지 않는다.
- 계획서, `AGENTS.md`, 사용자 기존 변경과 무관한 파일은 스테이징하지 않는다.
- 커밋 메시지는 기존 형식의 짧은 한국어 현재 시제 명령형을 사용한다.
- 적용 기록 때문에 파일이 추가로 바뀌면 기존 AE2 작업처럼 번역 커밋과 적용 기록 커밋을
  분리할 수 있다.
- `git push`, `git reset`, `git rebase`, `git commit --amend`는 수행하지 않는다.

커밋 메시지 예시:

- `AE2WTLib 가이드 번역`
- `ExtendedAE 가이드 재료·입문 번역`
- `MEGA Cells 가이드 저장소 번역`
- `AE2 연동 모드 가이드 적용 기록`

## 12. 전체 완료 조건

다음 조건을 모두 만족해야 AE2 연동 모드 가이드 번역을 완료로 기록한다.

- 조사된 11개 모드 99개 원문 대응 작업 완료
- 신규 한국어 Markdown 98개와 AE2WTLib 호환성 수정 1개 검증 완료
- 대상 모드별 가이드 사용 아이템 이름이 출력 언어 파일과 정확히 일치
- 작업본, 출력과 적용본 파일 목록 및 SHA-256 일치
- front matter, GuideME 태그, ID, 링크와 리소스 참조 보존
- 영어 문단, 임시 문구와 자리표시자 오류 0개
- UTF-8 BOM 파일 0개
- 적용 전 백업과 적용 후 예상 밖 인스턴스 변경 검사 완료
- FTB Quests 용어 교차 검토 완료, KubeJS 추가 대상 유무 기록
- 본체와 연동 모드의 실제 게임 화면 검증 결과 기록
- 모드별 재사용 수, 신규 번역 수, 커밋과 적용 경로 기록

## 13. 바로 다음 작업

1차 배치인 AE2WTLib을 시작하기 전에 `ae2wtlib` 언어 파일 46키를 영어 원문과 대조해
프로젝트 한국어 이름을 확정한다. 그 다음 AE2와 AE2WTLib의 충돌 문서를 다시 비교하여 기존
`wireless_terminals.md`를 호환성 구조로 갱신하고, AE2WTLib 전용 7페이지를 번역한다.
