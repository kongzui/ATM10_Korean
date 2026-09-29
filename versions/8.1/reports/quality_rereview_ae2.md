# 품질 재검수 7순위 · Applied Energistics 2와 애드온

기준 커밋 `74e79a8`의 8.1 산출물을 현재 JAR 영어 원문과 키·문단 단위로 다시 대조했어요. 8.1-stable.16에
반영했어요. 분업 방식(Opus 오케스트레이터·Sonnet 워커 8개 병렬)으로 진행했고, 이번 계열부터 GuideME
가이드도 워커가 재검수했어요.

## 범위와 결과

| 대상 | 검토 | 수정 | 유지 |
|---|---:|---:|---:|
| ae2 언어 | 1,021키 | 26 | 995 |
| megacells 언어 | 134키 | 6 | 128 |
| advanced_ae · expandedae · enderdrives · extendedae · immeng 언어 | 712키 | 10 | 702 |
| 나머지 애드온 11개 언어 | 232키 | 0 | 232 |
| 언어 합계 | 2,099키 | 42 | 2,057 |
| 퀘스트 `applied_energistics_2` | 175키 | 15 | 160 |
| 퀘스트 `extended__advanced_ae` | 91키 | 9 | 82 |
| GuideME 가이드 11개 모드 | 223파일 | 129파일, 263곳 | 94파일 |
| 연동: allthecompressed 천령 금속 | 27키 | 27 | — |

가이드 교체 263곳은 워커 241곳과 오케스트레이터 22곳(일괄 용어 교체 20, 문장 보정)이에요. AE2 가이드
126파일 중 99파일, Extended AE 46파일 중 12파일, MEGA Cells 7파일 중 6파일을 고쳤어요.

작업 원본은 애드온별 `working/ae2_addons/<모드>/lang/ko_kr.json`, 공유 파일(`curios_effects`,
`ars_nouveau/arseng`, `mekanism/appmek`, `industrial_foregoing/soulplied_energistics`)과 가이드
`working/ae2/ae2guide/_ko_kr`, `working/ae2_addons/<모드>/ae2guide/_ko_kr`이에요. AE2 본체 언어는 작업
원본이 없어 산출물만 고쳤어요.

## 주요 수정 유형

- 용어집: `조합법`·`레시피`→`제작법`(가이드 제목 `## 제작법` 포함), `세계`→`월드`, `분할`→`파티션`,
  화이트·블랙리스트→`허용 목록`·`차단 목록`, `공허·초과분 파괴 업그레이드`→`제거 업그레이드`,
  `창의적 비행`→`크리에이티브 비행`, `오른쪽·왼쪽 클릭`→`우클릭`·`좌클릭`, `단축바`→`단축 바`,
  `청크 로딩`→`청크 로드`, `허기`(음식 수치)→`배고픔`, `Inventory Tweaks` 모드명.
- 이름: MEGA Cells `하늘 강철·청동·오스뮴`→`천령 ~`(압축 블록 27키 연동), `ME 초대형 인터페이스`,
  `조밀한 ME 전선 코일`, 가이드의 `조밀 케이블`·`양자 네트워크 연결기`·`제작기`·`토글 버스`·`저장 모니터`를
  확정 이름(`조밀한 케이블`, `양자 네트워크 브리지`, `조립기`, `ME 토글 버스`, `ME 저장소 모니터`)으로,
  Ars Nouveau `수맥봉`, 바닐라 거래 단계 `초심자`, AE2 Bud `봉오리`.
- 오역: `Deletion via Shift / Space Clicking`, Circuit Slicer `최대 9배`, P2P `quirks`, Matter Cannon 피해
  비교, Fuzzy Card `내구도 수준`, 원문에 없던 `셀 하우징으로 만드는` 삭제, 툴바를 `들고 있을 때`로 옮긴 오역.
- 조사: `<ItemLink>`가 보여 주는 실제 이름과 `(1)`·`(4)` 같은 번호 읽기에 맞춘 은/는·이/가·을/를·으로.
- 번역투·말투: `당신`, `여러분`, `이는`, `이러한`, `~에 의해`, 추측형 `~했을 것입니다`, 해요체 농담·질문.

## 새로 정한 용어

- Crafting Grid는 `제작 칸`으로 정했어요(Crafting Tweaks·JEI·Sophisticated 등 다수 표기). 다른 계열에 남은
  `제작 격자`(EvilCraft, Integrated Dynamics, Refined Storage, Twilight Forest 퀘스트)는 해당 계열에서 고쳐요.
- Sky Bronze·Sky Osmium은 Sky Steel(`천령 강철`)에 맞춰 `천령 청동`·`천령 오스뮴`이에요.

## 가이드 재검수 방식

- `rereview_worker_kit.py pairs`가 가이드 영어·한국어 전문을 파일 단위로 이어 붙인 대조 파일을 약 9만 바이트씩
  만들어요(이번 20개).
- 워커는 파일을 다시 쓰지 않고 `{"old": 한 줄 조각, "new": 새 조각}` 목록만 내요. 새
  `quality_rereview_guides.py`가 조각이 정확히 한 번 나오는지, 태그·인라인 코드·링크·이미지·제목 단계·숫자·
  front matter가 기준 커밋과 같은지 검사한 뒤 산출물과 작업 원본에 줄바꿈 바이트를 보존하며 반영해요.
  용어 일괄 교체는 `"all": true`로 해요.
- `verify_quality_rereview.py`가 범위 파일의 `guide_files`를 허용 경로로 받고 같은 마크다운 검사를 누적
  검증에서도 해요.

## 분업 운영 기록

| 항목 | 결과 |
|---|---|
| 워커 | Sonnet 8개 병렬(언어·퀘스트 2, 가이드 6) |
| 워커 사용량 | 언어·퀘스트 약 18.1만·17.1만 토큰, 가이드 약 14.5만~18.7만 토큰, 각 2~5분 |
| 워커 수정 | 언어 41키, 퀘스트 19키, 가이드 241곳, 형식 오류 0 |
| 오케스트레이터 검토 | 수정 전수, 바뀐 이름의 사용처 검색, 유지 키 패턴 검사와 무작위 약 70키, 가이드 잔여 용어 검사 |
| 되돌림·보정 | 되돌림 0. 조사 1(`수맥봉을`), 부제 2(`특히 Mekanism 말입니다`, `주문 들어갑니다!`), 문장 3 |
| 추가 수정 | 언어 1(툴바 오역), 퀘스트 2(`이는`, 해요체 농담), 가이드 22곳, 압축 블록 27키 |

워커 간에 `제작 격자` 판단이 갈리고, 한 파일에 같은 제목(`## 조합법`)이 여러 번 있으면 한 번만 나오는
조각 규칙 때문에 고치지 못했어요. 오케스트레이터가 용어를 정해 일괄 교체로 마무리했어요.

## 검증과 적용

- `quality_rereview_lang.py ae2`, `quality_rereview_quests.py ae2`, `quality_rereview_guides.py ae2`,
  `verify_quality_rereview.py`, 안정판 검증, ZIP 두 개 생성.
- 가이드 교체는 파일마다 추가·삭제 줄 수가 같아(267/267) 바뀐 줄만 교체됐어요.
- 적용 결과는 [적용 보고](quality_rereview_ae2_apply.json)에 있어요. 실제 게임 화면은 미확인이에요.

## 남은 확인 항목

- 기존 AE2 전용 검증기(`verify_ae2_guide.py`, `verify_ae2_addon_guides.py`, `verify_ae2_translation.py`)는
  이번 수정 전부터 실패해요. 7.1 시절 JAR 기록, ExtendedAE 숫자 표기, ExpandedAE KubeJS 범위 기록이 8.1과
  어긋난 문제라 이번 범위에서 고치지 않았어요. `energy_acceptor.md`, `spatial_io_port.md`는 작업 원본과
  산출물이 원래 달라요.
- AE2 `gui.ae2.Types`(`유형`/`종류` 혼용), `block.ae2.matrix_frame`(`행렬 프레임`), `chipped_budding_quartz`
  수식어, `quartz_vibrant_glass`, `PatternAccessTerminalShort` 약어형은 이름 파급이 커서 유지했어요.
- AE2WTLib `gui.ae2wtlib.trash`(`아이템 파괴`), MEGA Cells Source 셀 `소스` 표기, Advanced AE
  `UpgradeNot*Message`의 `업그레이드` 덧붙임, `advanced_pattern_provider.md` 제목 층위.
- 가이드 `energy_cells.md`의 `UNLIMITED POWAHHHH` 농담 누락, `facades.md` 이미지 설명, `fluix_researcher.md`의
  `작업소 블록`, `extended_inscriber.md`의 `중첩 수`, 문장 속 `ME` 없이 줄여 부르는 버스 이름.
