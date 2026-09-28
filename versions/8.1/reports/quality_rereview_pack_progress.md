# 8.1 품질 재검수 1순위 · 팩 공통 진행 퀘스트

작업일: 2026-09-29. 기준 커밋 `9cd1e3b`, 배포 `8.1-stable.8`.
[재검수 계획](../../../docs/QUALITY_REREVIEW_PLAN.md)의 계열 1이에요.

## 결과

FTB Quests는 현재 인스턴스의 분할 영어(`lang/en_us/**/*.snbt_merged`)와 키 단위로 전부 다시 읽었어요.
문제가 없는 번역은 바꾸지 않고 유지 수로 셌어요. 숨김 라이선스 퀘스트 13개는 한 문장으로 통일했어요.

| 파일 | 번역 키 | 수정 | 유지 |
|---|---:|---:|---:|
| `chapter.snbt` | 73 | 8 | 65 |
| `chapter_group.snbt` | 13 | 2 | 11 |
| `file.snbt` | 1 | 1 | 0 |
| `reward_table.snbt` | 51 | 32 | 19 |
| `chapters/welcome.snbt` | 13 | 3 | 10 |
| `chapters/mainquestline_part_1.snbt` | 87 | 34 | 53 |
| `chapters/allthemodium.snbt` | 116 | 17 | 99 |
| `chapters/chapter_2_the_star.snbt` | 245 | 96 | 149 |
| `chapters/achapter_2r_6the_atm_star.snbt` | 76 | 38 | 38 |
| `chapters/tips_and_tricks.snbt` | 62 | 23 | 39 |
| `chapters/building_tips.snbt` | 254 | 95 | 159 |
| `chapters/bounty_board.snbt` | 54 | 23 | 31 |
| `chapters/basic_tools.snbt` | 109 | 44 | 65 |
| `chapters/basic_armor.snbt` | 347 | 33 | 314 |
| `chapters/basic_power.snbt` | 95 | 23 | 72 |
| `chapters/basic_logistics.snbt` | 76 | 16 | 60 |
| `chapters/storage.snbt` | 164 | 17 | 147 |
| `chapters/generators.snbt` | 95 | 28 | 67 |
| `chapters/food_and_farming.snbt` | 92 | 42 | 50 |
| **합계** | **2,023** | **575** | **1,448** |

영어 2,029키 중 6키는 자동 제목을 쓰도록 기존처럼 비워 둔 fallback 키예요.

언어·KubeJS:

- `ftbquestslangsplitter` 13키 중 3키 수정, 10키 유지.
- `kubejs` 38키, `atm` 8키, `atm10_localization` 6키, `allthetweaks` 2키는 모두 유지.
- `client_scripts/tooltips.js` 7줄, `startup_scripts/CustomAdditions.js` 1줄 수정.
  `RecipeViewer.js`, `Universal_Press.js`, `update_checker.js`, `hyperbox/hyperbox.js`는 유지.
- 같은 문구를 만드는 `build_atmgear_kubejs.py`, `mystical_family.py`의 대응표도 함께 고쳐
  다시 생성해도 되돌아가지 않게 했어요.

## 주요 수정 유형

- **깨진 문장:** `[Game] [block]`, `[fuel]`, `pairs...`, `about...`, `pollinate... before...`,
  `best`·`chance`, `학교들`처럼 영어 조각이나 엉뚱한 단어가 남은 문장을 다시 번역했어요.
- **서식 코드 뭉치:** 문장을 요약한 뒤 남는 색상 코드를 문장 끝에 몰아 둔 3개 설명을 원문 구조대로
  다시 번역했어요. 제목·설명에서 색이 뒤바뀐 재료 이름도 원문 위치로 되돌렸어요.
- **모드명:** `어플라이드 에너제틱스`, `레이저IO`, `모던 인더스트리얼라이제이션`, `신비농업`,
  `프로덕티브 비`, `이터널 스타라이트`, `아르스 누보`, `지하정원`, `아이언의 마법`, `파와`,
  `금 간/살짝 깨진`(Chipped), `저장의 기쁨`, `크리스탈릭스`, `다이나믹스`, `올 더 모드 10`을
  공식 영문 이름으로 되돌렸어요. `Generator Galore`는 JAR 표시 이름을 따랐어요.
- **오역·직역:** power→힘, `바람의 힘`, `폭발 레시피`, `라텍스`(Essence), `티어/계층/등급` 혼용,
  `당신은 여전히 탈 것입니다` 같은 대명사·미래형 직역, `상위 버전으로 변환`(Upgrade)을 고쳤어요.
- **이름 일치:** 증강(Augment), 광석 망치, 마그마 발전기, 폭발 균사 발전기, 공중 인터페이스,
  마이크로미사일, 통달한 시야의 지옥 책장, 엔드 책장, 영혼에 닿은 스컬크 책장, 소코트라 용혈수,
  웬지, 짙은 참나무, 달빛 괴수, 잊힌 수호자, 우두머리 예티, 범용 전선, 물류 수송기, 고압 튜브,
  기계 파이프, 물약 발전기, 구취 발전기, 조각된 비전 광택 다크스톤 등 현재 아이템 이름에 맞췄어요.
- **Minecraft 공식 표현:** 설치된 Minecraft 한국어 파일과 대조한 스컬크 감지체, 어색한 물약, 불길한 병,
  덫 상자, 생성 알, 짙은 참나무, 시련의 회당·시련 생성기, 삼림 대저택, 엔드 고지, 깊은 어둠, 생물군계, 월드.
- **숫자 단위:** `1 Billion`→`10억`, `2 Billion`→`20억`, `85 Million`→`8500만`은 숫자 검사
  예외로 `rebase_ftbquests.py`에 근거와 함께 등록했어요.

## 검증

- `scripts/quality_rereview_quests.py pack_progress`: 영어 원문 대비 자료형·문단 수·색상 코드·
  자리표시자·숫자·`\n` 개수 검사, 오류 0개. 수정본은 8.1 수동 검수 목록에도 기록.
- `scripts/verify_quality_rereview.py`: 기준 커밋 대비 키 추가·삭제 없음, 실제 줄바꿈 없음,
  수정본·산출물·수동 검수 목록 일치, 언어 파일 자리표시자·서식 보존, KubeJS 문자열 밖 코드 동일과
  `node --check` 통과, 검증 전후 인스턴스 변화 없음.
- `scripts/verify_stable_release.py --version 8.1`: JSON 1,804·SNBT 76·JavaScript 27개,
  언어 값 152,189개 검사 통과. ZIP 두 개의 CRC·전체 내용 검사 통과.
- 변경한 Python 파일만 `ruff format`·`ruff check` 통과. 저장소 전체 포맷은 범위 밖 파일을
  건드릴 수 있어 실행하지 않았어요.

## 게임 적용

Java 프로세스가 없는 상태에서 퀘스트 19파일, KubeJS 2파일, 언어 1파일, 폴더팩 `pack.mcmeta`
1파일을 `game_root`에 선택 적용했어요. 그 뒤 Minecraft 공식 한국어 파일과 대조해 고친 3파일을
다시 적용했어요. 두 실행 모두 예상 밖 변경 0개, `options.txt` 변경 없음.
[적용 기록](quality_rereview_pack_progress_apply.json)에 백업 위치를 남겼어요.

적용으로 인스턴스의 퀘스트·KubeJS 해시가 바뀌므로, Ad Astra·Logistics Networks·Step Crafter·
Better Advanced Tooltips의 표시 경로 감사에서 적용한 21파일의 해시만 `refresh_route_audits.py`로
갱신했어요. 참조 조사 결과와 파일 수는 그대로예요.
게임 내 퀘스트 화면은 아직 확인하지 않았어요.

## 다른 계열로 넘긴 항목

퀘스트는 올바른 이름으로 고쳤지만, 아이템 이름 자체의 수정은 해당 계열 재검수에서 처리해요.

| 현재 아이템 이름 | 제안 | 계열 |
|---|---|---|
| `Allthemodium 합금 칼날`(Sword) | 합금 검 | 6 Allthemodium |
| `크리에이티브 유리 단지`(Creative Source Jar) | 크리에이티브 마나 단지 | 20 Ars Nouveau |
| `창의적인 기관차`(Creative Locomotive) | 크리에이티브 기관차 | 37 Railcraft |
| `룬 인챈터`(Runic Enchanter) | 룬 마법 부여기 | 16 Modern Industrialization |
| `Quantum 주입기`(Quantum Injector) | 양자 주입기 | 33 Forbidden & Arcanus |
| `안정한 웜홀`(Stable Wormhole) | 안정된 웜홀 | 25 Occultism |
| `강화된 반전된 포텐시아` | 강화된 반전 포텐시아 | 33 EvilCraft |
| `압력 기계`·`광산 수레맨`·`선로맨`(주민 직업) | 압력 정비공·수레 기술자·선로 기술자 | 27·37 |
| `소울 라바(Soul Lava) 벌` 생성 알 제목 | 퀘스트 제목과 이름 규칙 통일 | 14 Productive Bees |

## 남은 원문과 확인 항목

- 영어로 남은 KubeJS 문구: `tooltips.js`의 구버전 기계 경고 4쌍·Hyperbox 제거 안내,
  `RecipeViewer.js`의 Just Dire Things 촉매 안내 4줄, `CustomAdditions.js`의 블록 2개 이름과 드래곤
  안내 1줄. 기존에 번역되지 않은 신규 번역 대상이라 이번 범위에서 바꾸지 않았어요.
- 쓰이지 않는 챕터 제목 `chapter.48DB721214AA88E0`(Implosion Power)의 `폭발력`은 연결된 챕터가
  없어 표시 경로를 확인한 뒤 고쳐요.
- 게임 화면 확인: 메인 퀘스트, 2·3장, 건축 팁 챕터의 줄바꿈·색상 표시.
