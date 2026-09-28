# Neo Vitae 전체 번역 완료 · 8.1-stable.3

2026-09-13. 이번 작업 단위는 Neo Vitae예요. Auroral stable.2 이후 이 모드까지 마치며,
단계 2 이후는 시작하지 않아요. 실제 인스턴스는 읽기 전용으로 조사하고 설치는 사용자가 해요.

## 번역과 표시 범위

현재 원본은 `neovitae-1.21.1-1.1.15.jar`예요.
SHA-256: `2f69f1eb3cbdce545c80939e40dbc243029073baf4f17ad457debb665c2a285c`.

| 항목 | 완료 수 |
|---|---:|
| 현재 JAR 일반 언어 전체 검수 | 3,053키 |
| 신규 한국어 / 고유명사·단위 표기 유지 | 2,953 / 100키 |
| 이전 배포의 일반 언어 재사용 / JAR 한국어 후보 | 0 / 0키 |
| 일반 언어에 포함된 book 키 | 1,531키 |
| 책 JSON / JSON에서 참조하는 고유 book 키 | 223파일 / 1,529키 |
| 직접 표시 문구: 한국어 / 원문 이름 유지 | 49 / 12키 |
| 최종 Neo Vitae 한국어 파일 | 3,114키 |
| 기존 퀘스트: 용어·제목 수정 / 그대로 재사용 | 66 / 39키 |

같은 모드에서 영어가 같은 문구를 재사용한 것은 이전 배포 번역 재사용 수에 넣지 않아요.
일반 언어와 book 키, 직접 문구의 등장 횟수와 고유 문구 수도 중복 합산하지 않아요.

`working/neovitae/review.json`은 원문 전체와 검수한 번역을 키별로 연결해요.
직접 문구는 `guide_literal_sources.json`의 JAR 멤버·JSON 포인터,
`guide_literals.review.json`의 원문·번역·검수 기록에 연결돼요.
`BookTextHolder.getString`이 직접 문자열을 `I18n.get`으로 조회하는 현재 클래스의 해시도
검증해요. 원본 책 JSON이나 JAR, 보조 실행 코드는 수정하지 않아요.

FTB Quests는 전용 챕터 49퀘스트와 ATM Star 챕터의 Teleposer 퀘스트 1개,
관련 Task 81개를 조사했어요. 기존 명시적 제목과 아이템 fallback을 구분하며,
단순 아이템 Task에 중복 제목을 추가하지 않아요. 숨겨진 저작권 Task의
`AllRightsReserved` 두 개와 공식 모드 이름은 유지해요.
KubeJS `modpack/att_items.js`의 Teleposer 아이템 ID 참조 외에 관련 표시 문구는 없었어요.

## 원문에서 발견한 차이와 처리

- 중급 절삭유: `book...dungeons.tau_fruit.tau_oil_uses.text`는 속도 25%%,
  `book...spiritus.ore_processing.intermediate_cutting.text`는 50%%라고 적혀 있어요.
  각각 현재 영어의 숫자와 퍼센트 이스케이프를 보존해요. 실제 수치를 임의로 확정하지 않아요.
- 가이드의 Hellforged Sand와 아이템 이름 Hellforged Dust가 달라요.
  원문의 모래/가루 구분을 보존하고 서로 같은 이름이라고 추정하지 않아요.
- 퀘스트 원문의 Ritual Diviner [Dusk]와 현재 아이템 [Tenebrae]가 달라요.
  설명의 Dusk는 보존하고 아이템 표시에는 현재 JAR 이름을 사용해요.
- 퀘스트 `419DB4A2A5A5FC58`의 설명은 Mine Entrance Key지만 Task의 `mine_key`는
  Mine Dungeon Key예요. 설명은 광산 입구 열쇠, 실제 Task 아이템은 광산 던전 열쇠로
  각각의 원문을 유지해요. Task 구조나 요구 아이템을 고치지 않아요.
- 같은 책의 이전 촉매 명칭 Small/Standard/Simple은 해당 초급/중급/순환 촉매의
  설명 문맥에 맞춰 현재 아이템 이름과 통일해요. 숫자·조건은 그대로예요.

## 검증과 남은 확인

전체 배포 검증과 패키징 결과는 `8.1-stable.3_stable_validation.json`,
`../manifests/8.1-stable.3_packages.json`에 기록해요.
JSON/SNBT/JS 문법, 중복 키·자료형, 보호 문자열, 현재 JAR·책·퀘스트 근거,
고정 기준 이후 변경 범위, 기존 보조 코드 비활성화와 ZIP 내용을 검사해요.
수정한 Python의 Ruff 형식·정적 검사도 수행해요.

현재 원문 기준으로 이번 모드의 번역 키 누락은 없어요. 라틴어 고유명사는 의도적으로 유지해요.
게임 화면 검증은 미실행이며, 원문의 서로 다른 설명이 실제 플레이에서 어떤 동작과 맞는지는
사용자 설치 후 확인할 수 있어요. 이 상태를 다른 모드의 번역 완료나 전체 게임 검수로 확대하지 않아요.

최종 확인 결과: JSON 1,763개·SNBT 76개·JavaScript 27개 검사 통과,
stable.1 이후 변경 없는 산출물 2,632개 해시 일치, 실제 원본 6,308개 파일의
경로·크기·수정 시각이 작업 전 스냅샷과 같아요. 책 추가 키 누락·근거 없는 추가 키·숫자 변조를
메모리에서 각각 넣었을 때 모두 검증이 실패하는 것도 확인했어요.
리소스팩 ZIP 2,331파일과 override ZIP 335파일의 CRC·내용 대조를 통과했어요.

번역·검증 커밋: `4fa4189` — Neo Vitae 전체 번역과 8.1-stable.3 누적 배포 검증.
