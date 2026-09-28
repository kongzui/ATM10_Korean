# 품질 재검수 1·2순위 용어 교체

2026-09-29에 정한 용어 기준([용어집](../../../glossary/README.md) 6장)을 이미 재검수를 마친
1순위(팩 공통 진행 퀘스트)와 2순위 1부(JEI·Jade·FTB 공통 UI)에 반영했어요. 8.1-stable.10에
포함했어요. 일괄 치환하지 않고 범위 파일의 해당 표현 141곳을 한 곳씩 문맥으로 판단했어요.

## 결과

| 범위 | 바꾼 키 | 파일 |
|---|---:|---|
| 1순위 퀘스트 | 34 | welcome, mainquestline_part_1, allthemodium, chapter_2_the_star, tips_and_tricks, building_tips, bounty_board, basic_armor, food_and_farming |
| 1순위 KubeJS | 3줄 | client_scripts/tooltips.js |
| 2순위 1부 언어 | 68 | jei 2, jade 16, ftbquests 21, ftbchunks 16, ftbultimine 6, ftbessentials 7 |

## 판단 기준

| 표현 | 바꾼 경우 | 그대로 둔 경우 |
|---|---|---|
| 생성 | 몹이 나타나는 뜻 → `스폰`(좀비·스켈레톤 변종, 떠돌이 상인, 몹 스폰 차단 등) | 광석·구조물·블록이 만들어지는 뜻, `생성 알`·`시련 생성기`, 파티·웨이포인트 생성 |
| 개체 | 엔티티를 가리키는 말 → `엔티티` | Jade 검색 별칭(`entity,엔티티,개체`)은 옛 말로도 찾도록 유지 |
| 재사용 대기시간 | → `쿨타임`(번식·복제 대기시간 포함) | FTB Chunks의 `유휴 지역 해제 대기 시간`(쿨타임이 아닌 대기) |
| 생물군계 | → `생물 군계` 전체 | 없음 |
| 단축바 / 키 설정 | → `단축 바` / `키 지정` | 없음 |
| 키친싱크 | → `온갖 모드를 담은 모드팩` | 없음 |
| 순간이동 | 없음 | 문장 속 동작이라 모두 유지 |

추가로 Jade의 `몹 생성기 종류`를 바닐라 블록 이름에 맞춰 `몬스터 생성기 종류`로, FTB Quests
이미지 설정의 `다른 개체`는 원문 `other objects`에 맞춰 `다른 요소`로 고쳤어요.

## 남긴 항목

- `솔라리움`(1순위 ATM의 별 챕터 1곳)은 Ender IO 아이템 이름과 함께 바꿔야 해서 Ender IO 계열
  재검수 때 고쳐요.

## 검증과 적용

- `quality_rereview_quests.py`, `quality_rereview_lang.py`, `verify_quality_rereview.py`,
  `verify_stable_release.py --version 8.1` 통과. `package_compat_release.py`로 ZIP 두 개 생성.
- `quality_rereview_lang.py`가 한 번 고친 키를 다시 고칠 때 작업 원본을 현재 산출물과도 비교하도록
  고쳤어요.
- 이전 문서 정리 때 링크 스크립트가 가이드 `.md`를 건드려 `git restore`로 되돌리면서 섞여 있던
  줄바꿈 바이트가 바뀌었어요. 내용은 같았고, stable.9·7.1-stable.1 ZIP에 남은 원래 바이트로
  8.1 16파일·7.1 12파일을 복원하고 작업 원본 가이드 18파일도 산출물·JAR 원문 바이트에 맞췄어요.
- 게임 종료 상태에서 퀘스트 9파일, KubeJS 1파일, 언어 6파일과 `pack.mcmeta`만 선택 적용했고 예상
  밖 변경은 없었어요([적용 보고](quality_rereview_term_pass_apply.json)). 표시 경로 감사 4개를
  갱신했어요. 실제 게임 화면은 미확인이에요.
