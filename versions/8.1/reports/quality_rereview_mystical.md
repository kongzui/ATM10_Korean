# 품질 재검수 9순위 · Mystical Agriculture

기준 커밋 `63aa605`의 8.1 산출물을 현재 JAR 영어 원문과 키 단위로 다시 대조했어요. 8.1-stable.18에
반영했어요. 분업 방식(Opus 오케스트레이터·Sonnet 워커 2개 병렬)으로 진행했어요.

## 범위와 결과

| 대상 | 검토 | 수정 | 유지 |
|---|---:|---:|---:|
| mysticalagriculture 언어(Patchouli 책 157키 포함) | 745키 | 59 | 686 |
| mysticalagradditions 언어 | 104키 | 1 | 103 |
| 언어 합계 | 849키 | 60 | 789 |
| 퀘스트 `elmystical_agriculturerr` | 277키 | 140 | 137 |
| MysticalCustomization 작물 설정 `name` | 13파일 | 3 | 10 |
| 연동: 퀘스트 `achapter_2r_6the_atm_star`(1순위 계열) | 1키 | 1 | — |

작업 원본은 `working/mystical/<모드>/ko_kr.json`이고, 수정본은 `working/quality_rereview/mystical/`에 있어요.
퀘스트 수정 140키 중 127키는 작물 부제 `Tier:`의 `티어`→`등급`, 1키는 자동 처리하는 숨김 라이선스 문구예요.
영어에만 있는 1키(`quest.47A91A89E9879863.quest_desc`)는 빈 설명이라 번역할 문장이 없어요.

작물 설정 3파일은 범위 파일의 `guide_files`에 넣어 누적 검증이 구조(`name` 밖 값 불변)를 확인해요.
`scripts/mystical_family.py`의 `CUSTOM_NAMES`도 같은 이름으로 고쳤어요. 이 스크립트의 `build`는 7.1 시절
단일 퀘스트 파일 구조를 쓰고 언어를 JAR와 내부 사전으로 다시 만들므로, 8.1 산출물에는 실행하지 않아요.

## 주요 수정 유형

- 용어: `티어`→`등급`(툴팁·퀘스트 부제·책), `%s의 에센스`→`%s 에센스`, `인챈터`→`마법 부여기`,
  `기계 틀`→`기계 프레임`, `소환 반경`·동작 `소환`→`스폰`, `생물군계`→`생물 군계`, `조합`→`제작`,
  `오른쪽 클릭`→`우클릭`, `조리 속도`→`처리 속도`.
- 바닐라 이름: 효과 `신속`→`속도 증가`, `구속`→`속도 감소`, `경험치 구슬`→`경험 구슬`, `흙길`→`흙 길`.
- 다른 모드 확정 이름과 맞춘 작물 재료: `소울라리움`, `생동 합금`(용어집), `시그널륨`(All The Ores),
  `아이언우드`·`파이어리 주괴`(Twilight Forest), `석영 농축 철`(Refined Storage), `대지 응집체`.
- 오역: `드래곤 알 청크`→`드래곤 알 덩어리`, 부서지지 않는 주입 수정을 `내구도 무한`으로 옮긴 문장,
  `추락 피해 무효`(Fall Damage Resistance)→`추락 피해 저항`, `인퍼륨 출력`→`인퍼륨 생산량`.
- 퀘스트: `당신은 마법사입니다`, 해요체 부제, `해당 모드`, 항아리 중복 문장, `이러한 ~에 사용됩니다`,
  마법 부여 이름 `신비로운 깨달음`→`신비한 깨달음`.
- 작물 설정: `스카이 스틸`→`천령 강철`, `어둠돌`→Forbidden Arcanus의 `다크스톤`,
  `미탐사 목재`→`Regions Unexplored 목재`. 원래 이름 `Unexplored Wood`는 모드명 Regions Unexplored의
  원목(`regions_unexplored:logs`)을 뜻해 공식 모드명을 뜻으로 옮기지 않았어요(ATM10 공개 저장소에서 확인).

## 챕터명 `신비농업`

계획표의 `신비농업` 중복 표기는 ATM10 원본 한국어가 두 챕터 제목 키에 `Mystical Agriculture`와 `신비농업`을
섞어 둔 문제였어요. 1순위에서 `chapter.snbt`의 두 키(`0F96DC3563DA78EF`, `5C764279146E5E66`)를 모두
`Mystical Agriculture`로 고쳤고, 이번에 산출물 전체에서 `신비농업`·`신비 농업`이 0곳인 것을 다시 확인했어요.
`5C764279146E5E66`은 챕터 파일이 없는 키라 화면에 나오지 않아요. 인스턴스의 옛 병합 파일
`lang/ko_kr.snbt`(2026-09-08)에는 `신비농업`이 남아 있지만, 우리가 적용하는 분할 파일이 같은 키를 덮어요.

## 새로 정한 용어

용어집 `품질 재검수 9순위 · Mystical Agriculture`에 8개를 추가했어요: 공식 모드명 3종, Essence `에센스`,
Tier `등급`, Enchanter `마법 부여기`, Machine Frame `기계 프레임`, Soulium Spawner `소울륨 소환기`,
Crux `크룩스`, 효과 Speed `속도 증가`. 워커 사이에 판단이 갈릴 만한 이 표기는 워커를 부르기 전에 정해 지시했어요.

## 분업 운영 기록

| 항목 | 결과 |
|---|---|
| 워커 | Sonnet 2개 병렬(mysticalagriculture, Agradditions+퀘스트) |
| 워커 사용량 | 14.6만 토큰(2.8분), 9.9만 토큰(2.4분) |
| 워커 수정 | 언어 56키, 퀘스트 139키, 형식 오류 0(퀘스트 워커가 자가 점검에서 `\n` 1곳을 스스로 고침) |
| 오케스트레이터 검토 | 수정 전수, 바뀐 이름의 사용처 검색, 유지 키 패턴 검사와 무작위 언어 60키·퀘스트 26키 |
| 되돌림 | 퀘스트 2키(말하는 양·소 농담은 인물 대사라 원래 반말 유지) |
| 보정 | 퀘스트 1키(`씨앗 기반재` 말장난 부제를 명사구로) |
| 추가 수정 | 언어 4키(책의 `소환`→`스폰` 2, `생성됩니다`, `인퍼륨 출력`), 퀘스트 2키 |

용어를 미리 정해 두어 워커 사이 판단 차이가 없었어요. 워커는 지시한 `소울륨 소환기` 이름 유지를 동작
`소환`까지 유지로 넓혀 읽었어요. 이름과 동작 용어를 따로 적어도 이런 경우가 생기니 패턴 검사로 확인해요.

## 검증과 적용

- `quality_rereview_lang.py mystical`, `quality_rereview_quests.py mystical`(`pack_progress` 재반영 포함),
  `verify_quality_rereview.py`, `verify_stable_release.py --version 8.1`(JSON 1,804·SNBT 76·JavaScript 27개,
  언어 값 152,189개), ZIP 두 개 생성과 CRC·내용 검사 통과.
- 바꾼 Python 파일만 `ruff format --check`·`ruff check` 통과.
- Java 프로세스가 없는 상태에서 stable.17 이후 바뀐 8파일을 `game_root`에 선택 적용했고 예상 밖 변경은 0개예요.
  [적용 보고](quality_rereview_mystical_apply.json)에 백업 위치가 있어요. 표시 경로 감사 4개의 해시를 갱신했어요.
  실제 게임 화면은 미확인이에요.

## 남은 확인 항목

- 원문 오류: `quest.67DBE6C59C0D9D1B`는 부제가 5등급인데 설명이 `Tier 4 Essence`라고 적혀 있어 원문대로 뒀어요.
  책 `slow_falling_augment.page.1`은 영어가 Slowness를 막는다고 잘못 적었지만 한국어는 실제 효과(느린 낙하)예요.
- 이름 후보: `퀸즈 슬라임`(Queen's Slime, 설치된 Tinkers' 확정 이름 없음), 마법 부여 `영혼 흡수`(Soul Siphoner).
- 다른 계열로 넘긴 항목: Refined Storage 퀘스트의 `석탄 정수`(12순위), Productive Bees 퀘스트의 `시그날룸`·
  `활기찬 합금`(14순위), Ender IO·압축 블록의 `활기찬 합금`(15순위), XyCraft 퀘스트의 `기계 틀`(31순위),
  MI·Oritech·Iron's Spells의 `인챈터`(해당 계열).
