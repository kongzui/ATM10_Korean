# ATM10 8.1 첫 실행 기준 기록

확인일: 2026-08-31

## 결과

- 번역팩을 적용하지 않은 8.1 프로필이 메인 메뉴 자원 로딩까지 완료되고 정상 종료됐다.
- KubeJS 시작 스크립트 19개와 클라이언트 스크립트 15개가 오류·경고 없이 로드됐다.
- 실행 전후 번역 관련 원본 스냅샷에서 바뀐 파일은 `kubejs/config/common.json` 하나였다.
- 종료 후 Minecraft와 Java 프로세스가 남아 있지 않았다.

## 번역 검증에서 기준으로 삼을 기존 로그

다음 메시지는 한국어 번역을 적용하기 전부터 발생했으므로 번역 회귀로 바로 판단하지 않는다.

- Sodium Extra의 누락된 access transformer 경고
- 첫 실행 시 `config/jupiter.json`이 없다는 메시지
- JEI 설정의 오래된 `buttonNavigationVisibility` 키 오류
- 자원 로딩 중 반복된 `Cannot get config value before config is loaded` 예외
- Silent Gear의 `trident_icon` 모델 누락 경고

번역 적용 뒤에는 이 기준 로그와 비교해 새 JSON·SNBT·KubeJS·리소스팩 오류만 분리한다.
