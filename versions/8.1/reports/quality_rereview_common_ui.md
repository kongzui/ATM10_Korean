# 품질 재검수 2순위 1부 · 항상 보는 공통 UI(JEI·Jade·FTB 계열)

기준 커밋 `3ac673a`의 8.1 산출물을 현재 JAR 영어 원문과 키 단위로 다시 대조했어요.
사용자 요청으로 2순위를 두 부분으로 나눴고, 이번 1부는 8.1-stable.9에 반영했어요.

## 범위와 결과

| 네임스페이스 | 검토 키 | 수정 | 유지 |
|---|---:|---:|---:|
| jei | 312 | 13 | 299 |
| jade | 410 | 8 | 402 |
| ftbquests | 768 | 102 | 666 |
| ftbchunks | 346 | 4 | 342 |
| ftbteams | 113 | 9 | 104 |
| ftbultimine | 89 | 3 | 86 |
| ftbessentials | 94 | 3 | 91 |
| ftbfiltersystem | 65 | 0 | 65 |
| 합계 | 2,197 | 142 | 2,055 |

퀘스트·KubeJS 변경은 없어요. 수정 목록은 `working/quality_rereview/common_ui/lang/`,
키별 결과는 [JSON 보고](quality_rereview_common_ui_lang.json)에 있어요.

## 주요 수정 유형

- 설정 설명의 `참이면/거짓이면`을 `켜면/끄면`으로 바꾸고, 영어 어순을 따른 문장을 다시 썼어요.
- 모드명 뜻 번역·음역을 공식 이름으로 되돌렸어요(FTB Quests, CustomNPCs, BuildCraft, Botania).
- Minecraft 공식 용어에 맞췄어요: 주 손, 단축바, 생물군계, 개체(Entity), 재사용 대기시간.
- 명령어 결과 문구를 완료형으로, `~에 의해` 수동태를 능동문으로 바꿨어요.
- JEI 북마크 제작, 2x2 제작 칸, 검색창 관련 키 이름을 기능이 드러나게 정리했어요.

## 검증과 적용

- `quality_rereview_lang.py`: 자리표시자·서식 코드·`\n` 개수·빈 값 검사, 작업 원본과 산출물 일치.
- `verify_quality_rereview.py`: 기준 대비 키 목록·순서 동일, 1·2순위 누적 통과.
- `verify_stable_release.py --version 8.1` 통과, `package_compat_release.py`로 ZIP 두 개 생성.
- 게임 종료 상태에서 언어 7파일과 `pack.mcmeta`만 선택 적용했고 예상 밖 변경은 없었어요
  ([적용 보고](quality_rereview_common_ui_apply.json)). 실제 게임 화면은 미확인이에요.
- 작업 중 `quality_rereview_lang.py`가 Windows에서 CRLF로 쓰던 문제를 LF 고정으로 고쳤고,
  단계1 검증은 이번 배포가 바꿀 수 있는 경로에 한해 stable.1 기준 내용 고정 검사를 건너뛰어요.

## 남은 항목(2순위 2부)

- JourneyMap, Curios, Waystones, Nature's Compass, Explorer's Compass는 다음 작업에서 검수해요.
- 남은 문체 신호 2개(`~를 위한`)는 자연스러운 표현이라 유지했어요.
