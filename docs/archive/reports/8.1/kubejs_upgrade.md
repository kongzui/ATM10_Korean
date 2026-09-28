# ATM10 8.1 KubeJS 번역 업그레이드

- 현재 8.1 KubeJS에서 찾은 사용자 표시 문구 후보: 20개 파일, 217개
- 번역 산출물로 덮는 후보 파일: 20개(100%)
- 표시 문자열을 제외한 코드 구조가 그대로인 파일: 17개
- 8.1 구조 변경을 수동 반영한 파일: 3개
- 새로 번역한 현재 원본 파일: 3개
- 프로젝트가 추가하는 호환 번역 스크립트 유지: 4개
- 다시 생성한 Silent Gear 특성 데이터: 4개 파일, 9개 문구
- ATM KubeJS 언어 키: 영어 8개, 한국어 8개, 누락 0개
- JavaScript 문법 검사: 27개 파일, 오류 0개
- JSON 문법 검사: 35개 파일, 오류 0개

## 수동 구조 반영

- `client_scripts/tooltips.js`: 8.1 원본에서 사라진 Expanded AE 툴팁 조작을 제거했다.
- `server_scripts/announcements/announcements.js`: 8.1에서 삭제된 4.0~4.2 공지를 제거하고 5.3의 Hyperbox 안내를 현재 원문에 맞췄다.
- `server_scripts/banlist_script.js`: 현재 8.1 코드를 기준으로 금지 엔티티, 블록 엔티티, 아이템 안내와 표지판 문구를 번역했다.

## 다음 단계로 넘긴 범위

`kubejs/data/` 아래의 구조물 NBT와 일부 데이터 JSON은 KubeJS 자체 문구가 아니라 모드 원본의 `custom_name` 등을 번역한 덮어쓰기다. 각 모드 계열 검토 단계에서 현재 8.1 JAR 원본과 다시 대조한다.
