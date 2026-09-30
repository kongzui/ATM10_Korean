# 품질 재검수 8순위 · Mekanism 계열

기준 커밋 `ec448a7`의 8.1 산출물을 현재 JAR 영어 원문과 키·문단 단위로 다시 대조했어요. 8.1-stable.17에
반영했어요. 분업 방식(Opus 오케스트레이터·Sonnet 워커 7개 병렬)으로 진행했어요.

## 범위와 결과

| 대상 | 검토 | 수정 | 유지 |
|---|---:|---:|---:|
| mekanism 언어 | 3,239키 | 723 | 2,516 |
| mekanismgenerators 언어 | 364키 | 92 | 272 |
| mekanismtools 언어 | 800키 | 239 | 561 |
| mekmm(Mekanism: MoreMachine) 언어 | 702키 | 332 | 370 |
| mekanisticrouters · jei_mekanism_multiblocks · gmut · mekanismcovers 언어 | 111키 | 12 | 99 |
| 언어 합계 | 5,216키 | 1,398 | 3,818 |
| 퀘스트 `mekanism` | 235키 | 130 | 105 |
| 퀘스트 `mekanism_reactors` | 233키 | 166 | 67 |
| KubeJS `client_scripts/Mekanism-Tooltips.js` | 14줄 | 1 | 13 |
| 연동: 퀘스트 `basic_power`(1순위 계열) | 1키 | 1 | — |

작업 원본은 `working/mekanism/<모드>/ko_kr.json`이고, 수정본은 `working/quality_rereview/mekanism/`에 있어요.
KubeJS 툴팁은 `scripts/build_mekanism_extras.py`의 대응표도 함께 고쳐 다시 만들어도 되돌아가지 않아요.
`tag.*` 공유 키는 Mekanism 이름을 따르는 양동이·유체·재료 태그 7개만 고쳤어요.

## 주요 수정 유형

- 설정 화면: `~을 구성하기 위한 설정`, `true인 경우`, `이는`, `~하십시오`, `닻`(anchor), `세계 생성` 같은 기계
  번역을 `~ 설정입니다.`, `켜면`, `앵커`, `월드 생성`으로 고쳤어요. mekanism 설정 설명이 수정의 절반 가까이예요.
- 이름: MoreMachine `공장`·`오버클럭된`·`다차원` → `시스템`·`오버클럭`·`다중 우주`(약 260키), `액체 에테인`
  → `액체 에텐`, `염산` → `액체 염화 수소`, `가열된 나트륨` → `과열된 나트륨`, 안료 `색소`·`염료` → `안료`와
  바닐라 염료 색, `각반` → `레깅스`, `메카슈트 하의`, `정제된 흑요석·발광석` 도구 16종, `HDPE 시트`(용지),
  `HDPE 막대기`, `화학적 투입 장치`, `유체 탱크`·`유체 방출기`·`유체 복제기`, `스쿠버 마스크`, `장갑 프리 러너`,
  `차가운 걸음 기구`, `중력 조절 기구`, `방호복 부츠`, `메카슈트 투구`, `열전 보일러`, `텔레포트 코어`.
- 핵분열: `연료 구성기`·`제어 축` → `핵분열 연료 집합체`·`제어봉 집합체`, `융합 속도` → `주입 속도`,
  `가열 효율` → `비등 효율`.
- 명령·결과 메시지를 `~했습니다`로, 사망 메시지의 영어 `Oblivion`을 한국어로 바꿨어요.
- 퀘스트: `반응기` 29곳을 `핵분열로`·`핵융합로`·`원자로`로, 모듈 퀘스트 제목·본문의 `~ 유닛`을 게임 속
  `~ 기구` 이름으로(조사 포함), `2빌리언 mB`를 `20억 mB`로, 핵분열로 최소 크기 `3x4x3` 오기를 `3x3x4`로,
  해요체·반말·`당신`·`마우스 오른쪽 버튼`·`엔터티`를 고쳤어요.

## 새로 정한 용어

용어집 `품질 재검수 8순위 · Mekanism 계열`에 16개를 추가했어요. 핵심은 다음과 같아요.

- Factory `시스템`(본체 JAR 공식), Gas `기체`, Fluid `유체`·Liquid `액체`, Pigment `안료`, Transmitter `전송기`.
- Reactor 단독 표기, Radiation `방사선`·Radioactive `방사성`·Radioactivity `방사능`.
- Chemical Injection Chamber `화학적 투입 장치`(Infuse `주입`과 구분), Leggings `레깅스`(전체 프로젝트).

## 분업 운영 기록

| 항목 | 결과 |
|---|---|
| 워커 | Sonnet 7개 병렬(mekanism 3분할, generators+tools, 애드온 5개, 퀘스트 2) |
| 워커 사용량 | 언어 12.4만~20.2만 토큰(2.5~6분), 퀘스트 31.5만·32.7만 토큰(16~18분) |
| 워커 수정 | 언어 1,262키, 퀘스트 270키, 형식 오류 0 |
| 오케스트레이터 검토 | 수정 전수, 바뀐 이름의 사용처 검색, 유지 키 패턴 검사와 무작위 언어 60키·퀘스트 24키 |
| 되돌림 | 언어 8키(`QIO 드라이브 어레이`, `융합 속도`, 유체 탱크 `액체` 4키 등), 퀘스트 0 |
| 보정 | 언어 53키, 퀘스트 67키(대부분 모듈 이름·조사 전파) |
| 추가 수정 | 언어 144키(워커가 놓친 설정·번역투·이름 전파), 퀘스트 26키 |

워커 사이에 `Fluid`를 `액체`와 `유체`로 판단이 갈렸어요. 영어가 Fluid와 Liquid를 구분하고 다른 모드도
`유체 탱크`를 쓰므로 `유체`로 정하고 영어에 Fluid만 있는 키를 일괄 정리했어요. mekanism 한 네임스페이스를
세 워커가 나눠 맡을 때는 분할 수정본(`mekanism__NN.json`)과 전용 검사(`temp/rereview/mekanism/check_part.py`)를
쓰고 오케스트레이터가 합쳤어요. 합치기·용어 통일은 다시 실행해도 같은 결과가 나오는 임시 스크립트
(`temp/rereview/mekanism/orchestrate.py`, `orchestrate_quests.py`)로 했어요.

## 검증과 적용

- `quality_rereview_lang.py mekanism`, `quality_rereview_quests.py mekanism`(`pack_progress` 재반영 포함),
  `verify_quality_rereview.py`, `verify_stable_release.py --version 8.1`(JSON 1,804·SNBT 76·JavaScript 27개,
  언어 값 152,189개), ZIP 두 개 생성과 CRC·내용 검사 통과.
- `2 Billion`을 `20억`으로 옮긴 퀘스트 1키는 기존 선례대로 `VALIDATION_ERROR_EXCEPTIONS`에 숫자 예외로 등록했어요.
- 바꾼 Python 파일만 `ruff format --check`·`ruff check` 통과.
- Java 프로세스가 없는 상태에서 stable.16 이후 바뀐 12파일을 `game_root`에 선택 적용했고 예상 밖 변경은 0개예요.
  [적용 보고](quality_rereview_mekanism_apply.json)에 백업 위치가 있어요. 적용 뒤 `build_mekanism_extras.py`를 다시
  돌려 산출물이 바뀌지 않는 것을 확인했고, 표시 경로 감사 4개의 해시를 갱신했어요. 실제 게임 화면은 미확인이에요.

## 남은 확인 항목

- KubeJS Ponder 9파일(`fission_mek.js` 등)은 이번 범위 밖이라 두었어요. `반응기`, `초임계 위상 변환기`
  (언어 파일은 `초임계 상전이 장치`)처럼 이번 용어와 다른 표기가 남아 있어요.
- Color Modulation 퀘스트는 원문의 글자별 색 코드 때문에 제목·본문에 영문 `Color Modulation`을 남겼어요.
- 이름 후보: `우라늄염`(Yellow Cake Uranium), `재가공된 핵연료 결정`(Reprocessed Fissile Fragment),
  모듈 `에너지 가위 기구`·`레이저 굴절 기구`·`선량 기구`, `개인용 통`/`개인 상자` 접두 차이.
- 퀘스트 원문 확인: `quest.603BEDD49070ECAD`(콘덴서 응축 방향), `Wasted/Lithium Comb` 이름.
- 다른 계열로 넘긴 항목: Aether `흑요석 각반`(24순위), PneumaticCraft·XyCraft의 모드명 음역 `메카니즘`(27·31순위).
