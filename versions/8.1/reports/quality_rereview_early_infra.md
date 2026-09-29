# 품질 재검수 5순위 · 초반 기반 도구·기계·물류

기준 커밋 `6ab3127`의 8.1 산출물을 현재 JAR 영어 원문과 키 단위로 다시 대조했어요. 8.1-stable.14에
반영했어요. 분업 방식(Opus 오케스트레이터·Sonnet 워커 2개 병렬)으로 진행했어요. 관련 퀘스트인 기본
도구·전력·물류 챕터는 1순위에서 검수를 마쳤어요.

## 범위와 결과

| 네임스페이스 | 검토 키 | 수정 | 유지 |
|---|---:|---:|---:|
| quarryplus | 244 | 36 | 208 |
| xnet | 186 | 7 | 179 |
| functionalstorage | 162 | 10 | 152 |
| mob_grinding_utils | 146 | 14 | 132 |
| ironfurnaces | 143 | 7 | 136 |
| constructionstick | 142 | 4 | 138 |
| buildinggadgets2 | 112 | 8 | 104 |
| mininggadgets | 85 | 2 | 83 |
| pipez | 84 | 4 | 80 |
| generatorgalore | 75 | 2 | 73 |
| moderndynamics | 72 | 3 | 69 |
| bhc | 66 | 14 | 52 |
| energymeter | 64 | 2 | 62 |
| simplemagnets | 46 | 2 | 44 |
| ironjetpacks | 42 | 4 | 38 |
| easy_villagers, itemcollectors, toolbelt | 64 | 0 | 64 |
| pocketstorage | 28 | 4 | 24 |
| enderstorage | 8 | 3 | 5 |
| 합계 | 1,769 | 126 | 1,643 |

작업 원본은 각 네임스페이스의 `ko_kr.json`과 여러 모드가 함께 쓰는 `manual_overrides.json` 3개예요.
1순위 퀘스트 5키(Quarry 기계를 `채석장`으로 쓴 4키와 해요체 1문장)도 함께 고쳤어요.

## 주요 수정 유형

- 이름: QuarryPlus의 `쿼리`(Quarry 오역)를 `채석기`로(이름·태그·채팅·툴팁 약 27키), Void Upgrade·Void
  Module을 `제거`로, Spawner Controller를 바닐라 `몬스터 생성기 제어기`로, Baubley Heart Canisters의
  `생명력 패치`를 `체력 패치`로, Functional Storage Jade 표시 이름을 `장비 보관함`으로.
- 오역: Building Gadgets 2 레드프린트 메시지의 자리표시자 순서, Construction Sticks 내구 문장,
  QuarryPlus crash(`충돌`→`비정상 종료`), Modern Dynamics Stuffed·Hold, Pipez 방향 표시.
- 용어집: 스폰, 생물 군계, 밝기 레벨, 쿨타임, 체력, 제작법(`조리법` X), 웅크린 채 우클릭, 좌클릭,
  `mB` 단위, 마법 부여 띄어쓰기, OP(EnderStorage Operator), 켜면.
- 번역투·말투: `~된 경우`, `보유하고 있지 않습니다`, `성공적으로`, `알려지지 않은`, 해요체 농담·업적,
  명령 결과와 오류 메시지를 완결된 문장으로.

## 분업 운영 기록

| 항목 | 결과 |
|---|---|
| 워커 | Sonnet 2개(A: 도구·장비 11개 846키, B: 저장·물류·전력 9개 923키) |
| 워커 사용량 | A 약 18.4만 토큰·4.6분, B 약 18.7만 토큰·4.6분 |
| 워커 수정 | A 52키, B 72키, 모두 사유 제출, 형식 오류 0 |
| 오케스트레이터 검토 | 수정 124키 전수, 바뀐 이름의 퀘스트 사용처 확인, 유지 키 패턴 검사와 무작위 60키 |
| 되돌림·보정 | XNet `low`/`high` 단독 단어 변경 2키 되돌리고 툴팁 3키를 다른 방식으로 수정 |
| 추가 수정 | EnderStorage Operator→OP, XNet If enabled→켜면, Iron Furnaces `조리법`·`조리 시간` 5키 |

## 검증과 적용

- `quality_rereview_lang.py early_infra`, `quality_rereview_quests.py pack_progress`,
  `verify_quality_rereview.py`, 안정판 검증 통과, ZIP 두 개 생성.
- `quality_rereview_lang.py`가 여러 네임스페이스가 공유하는 작업 원본을 앞선 수정을 잃지 않고 이어서
  고치도록 고쳤어요.
- 게임 종료 상태에서 바뀐 퀘스트·언어 파일과 `pack.mcmeta`만 선택 적용했어요
  ([적용 보고](quality_rereview_early_infra_apply.json)). 실제 게임 화면은 미확인이에요.

## 남은 확인 항목

- Building Gadgets 2 Patchouli 가이드북, Energy Meter GuideME 가이드는 언어 파일이 아니라 이번 범위 밖이에요.
- QuarryPlus `청크 파괴자`(Chunk Destroyer): 기계 이름으로 `청크 파괴기`가 자연스럽지만 설정 이름 다수와
  이어져 유지했어요.
- Functional Storage `점적석 업그레이드`의 기능 일치 여부, Easy Villagers의 `주민 ~` 풀어 쓴 이름.
- 다른 계열 퀘스트(Forbidden & Arcanus, Refined Storage)의 기계 뜻 `채석장`은 해당 계열 재검수 때 고쳐요.
