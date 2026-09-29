# 품질 재검수 6순위 · Allthemodium·ATM 광물

기준 커밋 `adb58be`의 8.1 산출물을 현재 JAR 영어 원문과 키 단위로 다시 대조했어요. 8.1-stable.15에
반영했어요. 일반 언어는 분업 방식(Opus 오케스트레이터·Sonnet 워커 1개)으로, All The Compressed
압축 블록은 오케스트레이터가 규칙 검사로, Allthemodium Patchouli 안내서는 오케스트레이터가 직접
검수했어요. 관련 퀘스트인 `allthemodium` 챕터는 1순위에서 검수를 마쳤어요.

## 범위와 결과

| 네임스페이스 | 검토 키 | 수정 | 유지 | 방식 |
|---|---:|---:|---:|---|
| allthecompressed | 1,796 | 163 | 1,633 | 규칙 검사 |
| alltheores | 516 | 17 | 499 | 워커 |
| allthemodium | 306 | 20 | 286 | 워커·보정 |
| allthearcanistgear | 28 | 0 | 28 | 워커 |
| allthewizardgear | 16 | 1 | 15 | 워커·보정 |
| 합계 | 2,662 | 201 | 2,461 | |
| Allthemodium 안내서 | 표시 필드 47 | 4 | 43 | 직접 검수 |

작업 원본은 각 네임스페이스의 `ko_kr.json`과 같은 키를 가진 `working/ars_nouveau/allthearcanistgear`,
`working/ae2/compat/allthecompressed`예요. 안내서는 `scripts/build_atmgear_guide.py`의 번역 사전을 고친
뒤 같은 스크립트로 다시 만들었어요(바뀐 파일 4개, `book.json` 덮어쓰기는 변화 없음).

## 압축 블록 규칙 검사

압축 블록 1,796키는 기본 이름 199개 × `1x`~`9x`와 단독 키 5개예요. 프로그램으로 다음을 확인했어요.

1. 9단계 이름이 모두 같은 기본 이름에 `n x` 접미사만 붙는지: 불일치 0.
2. 기본 이름이 원래 블록(바닐라 공식 한국어, 같은 ID나 같은 영어 이름을 가진 모드 블록의 프로젝트
   확정 이름)과 같은지: 일치 162, 불일치 19, 원래 블록 없음 18.
3. 불일치 19개 중 17개를 원래 이름으로 맞췄어요. `소울라리움 블록`은 용어집 확정 표기라 유지하고
   Ender IO 쪽을 해당 계열에서 고쳐요. `부서진 엔드 돌`도 Occultism 쪽 `부셔진`이 맞춤법 오류라 유지해요.
4. 원래 블록이 설치되지 않은 18개(Precasian, Stranglewood, 반물질 블록 등)는 이름을 직접 읽어 확인했어요.
   그중 `블레이즈 막대 블록`은 바닐라 `블레이즈 막대기`에 맞춰 고쳤어요.

고친 기본 이름: 벌집 조각 블록, 단단한 진흙, 블레이즈 막대기 블록, 충전된 레드스톤 결정 블록, 바오밥
원목·판자, 키비, Greg의 별 블록, 왁스 블록, 자이코륨 보석 블록 5색, Powah 결정 블록 3종과 에너지화 강철
블록. Powah·Productive Bees·XyCraft 이름은 현재 산출물 이름을 따랐으므로, 해당 계열에서 원래 이름이
바뀌면 압축 블록 9단계도 함께 고쳐요(용어집에 규칙 기록).

## 주요 수정 유형

- 오역: All The Ores `Other ~ Ore` 17개를 `기타 ~ 광석`에서 차원 이름 `디 아더 ~ 광석`으로.
- 용어집·바닐라 이름: Mekanism 확정 표기 `순수한`·`불순물이 섞인` 슬러리·가루 9키, 생물 군계
  `깊은 어둠`·`엔드 고지`(툴팁 2키, 안내서 2문장), 음식 수치 `배고픔`(안내서 2문장).
- 표기 통일: Rod `막대`→`막대기`(Allthemodium 3키, 압축 10키), Gear `톱니바퀴`→`기어`(3키),
  `디 아더: ` 생물 군계 접두 3키, 탭 이름 대소문자 1키.
- 안내서 문장: `허기가 가득 차도 섭취 가능`→`배부를 때도 섭취 가능`, `산 정상`처럼 원문에 없던 표현 정리.

## 새로 정한 용어

바닐라 공식 한국어(`블레이즈 막대기`, `엔드 막대기`, `깊은 어둠`, `엔드 고지`)와 프로젝트 다수 표기를
확인해 용어집 6순위 표에 기록했어요. Rod는 `막대기`, Gear는 `기어`, 광물 3종은 원문 유지, The Other는
`디 아더`, 압축 블록은 원래 블록 이름을 따라요. 다른 계열에 남은 재료 뜻의 `막대`(Modern
Industrialization 19, Immersive Engineering 4, Silent Gear 3 등)와 `딥 다크`·`엔드 고지대`는 용어집 6장
교체 대상에 넣어 해당 계열 재검수 때 고쳐요.

## 분업 운영 기록

| 항목 | 결과 |
|---|---|
| 워커 | Sonnet 1개(allthemodium·alltheores·arcanist·wizard 4개 866키) |
| 워커 사용량 | 약 12.7만 토큰·2.1분 |
| 워커 수정 | 29키, 모두 사유 제출, 형식 오류 0 |
| 오케스트레이터 검토 | 수정 29키 전수, 퀘스트·KubeJS 사용처 확인, 유지 837키 패턴 검사(0건)와 무작위 45키·전체 이름 목록 |
| 되돌림·보정 | 되돌림 0. 워커가 보류한 Rod·Gear·탭 이름 7키 보정 |
| 추가 수정 | 바닐라 생물 군계 이름 2키, 압축 블록 163키, 안내서 4필드 |

## 검증과 적용

- `quality_rereview_lang.py atm_ores`, `build_atmgear_guide.py`, `verify_atmgear_guide.py`,
  `verify_quality_rereview.py`, 안정판 검증 통과, ZIP 두 개 생성.
- `verify_quality_rereview.py`가 범위 파일의 `guide_files`를 허용 경로로 받고, 기준 커밋 대비 JSON 구조·
  문자열 밖의 값·Patchouli 태그가 그대로인지 검사하도록 넓혔어요.
- 게임 종료 상태에서 바뀐 언어 4파일, 안내서 4파일과 `pack.mcmeta`만 선택 적용했어요
  ([적용 보고](quality_rereview_atm_ores_apply.json)). 실제 게임 화면은 미확인이에요.
- 게임 설정의 활성 리소스팩은 여전히 `ATM10_Korean_8.1-stable.7_resourcepack.zip`이에요. 적용한 폴더팩을
  보려면 게임에서 폴더팩 `ATM10_Korean`을 활성화해야 해요.

## 남은 확인 항목

- `block.allthemodium.allthemodium_source_jar`의 영어 원문이 `Unobtainium Source Jar`예요. 원문 오류로
  보고 키 ID대로 `Allthemodium 마나 단지`를 유지했어요.
- `The Beyond` 차원·생물 군계 이름은 영문 그대로예요. `디 아더`와 맞춘 음역(`디 비욘드`)을 쓸지는 퀘스트
  사용처와 함께 정해야 해요.
- 다른 계열 표기: 퀘스트의 `블레이즈 막대`(Apotheosis·Cataclysm·Immersive Engineering·Iron's Spells),
  Deeper and Darker 퀘스트의 `딥 다크`, Occultism `부셔진 엔드 돌`, AppleSkin 설정 설명의 `배고픔와` 조사.
- `mcw-trapdoors` JAR 내장 `ko_kr.json`이 JSON 오류라 이름 색인에서 빠져요(원본 JAR 문제).
