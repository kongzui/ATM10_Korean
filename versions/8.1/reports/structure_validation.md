# ATM10 8.1 버전별 구조 검증

검증일: 2026-08-31

## 결과

- `output/7.1/`과 `output/8.1/`에 각각 `resourcepack/`, `overrides/`, `release.json`이 있다.
- 각 버전은 리소스팩 2,301개, override 264개, `release.json`을 포함해 총 2,566개 파일이다.
- 복사 직후 `release.json`을 제외한 7.1과 8.1의 시작 파일 2,565개를 SHA-256으로 비교했으며
  차이는 0개였다.
- 새 파일에 대한 `git diff --check`를 통과시키기 위해 8.1 작업본 13개의 줄 끝 공백·혼합
  들여쓰기·마지막 빈 줄만 정리했다. 7.1 보존본은 바꾸지 않았다.
- `version_context.json`의 활성 버전 8.1을 기준으로 산출물 경로가 `output/8.1/`로 결정된다.
- Python 스크립트 225개의 바이트코드 컴파일과 전체 Ruff 검사가 통과했다.
- `PROJECT_ROOT / "output/resourcepack"` 또는 `output/overrides`를 직접 사용하는 표현은 0개다.
- 8.1 전체 적용은 `output/8.1/release.json`에 의해 차단된다.
- 파일 하나를 고른 dry-run은 `output/8.1/`을 읽고 8.1 `game_root`를 대상으로 정상 완료됐다.
- 저장소 작업 뒤 실제 8.1 인스턴스 3,687개 파일의 경로·크기·수정 시각은 기준 스냅샷과 같다.
- Minecraft와 Java 프로세스는 실행 중이지 않다.

## 기존 산출물에서 확인된 별도 검토 항목

- Herbs and Harvest의 `grapes.json`, `herbs.json`은 뒤쪽 중복 닫기 구조 때문에 일반 JSON
  파서가 실패한다. 7.1에서 이어받은 문제이며 8.1 재검수 때 현재 원본에서 다시 만든다.
- 8.1 Macaw's Trapdoors JAR 내부 `ko_kr.json`에는 쉼표 누락 문법 오류가 있다. 원본 JAR은
  수정하지 않고 프로젝트 리소스팩에서 현재 영어 원문을 기준으로 처리한다.
- 8.1 FTB Quests는 분할 언어 구조이므로 기존 단일 `ko_kr.snbt`는 적용하지 않는다.

이번 구조 정리에서는 실제 게임에 번역 파일을 적용하지 않았다.
