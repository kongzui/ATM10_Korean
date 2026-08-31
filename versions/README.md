# ATM10 버전별 작업 공간

`versions/`에는 버전별 원본 조사와 차이·검증 기록만 남긴다. 실제 완성 산출물은 저장소 루트의
`output/<ATM10 버전>/{resourcepack,overrides}`에 버전별로 분리한다.

## 구성

- `<버전>/version.json`: 게임팩·Minecraft·NeoForge와 조사 상태
- `<버전>/manifests/`: 설치 JAR, 언어 네임스페이스, FTB Quests와 KubeJS 조사 결과
- `<버전>/reports/`: 이전 버전과의 차이, 충돌 경로와 검증 보고서
- `<버전>/conflicts/`: 자동 병합할 수 없는 번역 충돌의 수동 검토 기록

활성 버전과 기준 버전은 저장소 루트의 `version_context.json`에서 선택한다. 각 output의 전체
적용 가능 여부는 `output/<ATM10 버전>/release.json`으로 관리한다.

## 버전 갱신 순서

1. 새 ATM10 프로필을 설치하고 `local_paths.json`의 `game_root`를 새 경로로 바꾼다.
2. `version_context.json`에 기준 버전, 목표 버전과 목표 작업 공간을 적는다.
3. `output/<이전 버전>/`을 `output/<새 버전>/`으로 복사하고 새 버전 `release.json`에서 전체
   적용을 차단한다.
4. `python scripts/discover.py`로 목표 버전 매니페스트를 만든다.
5. `python scripts/compare_pack_versions.py --base-instance <이전> --target-instance <새 버전>`으로
   실제 원문과 override 충돌을 비교한다.
6. 영향받은 모드 계열만 현재 영어 원문에 다시 대조한다.
7. 작업 단위별 검증 후 `--path`로 선택 적용한다.
8. 전체 재기준화가 끝나면 `output/<새 버전>/release.json`을 검증 완료 상태로 바꾼다.

JAR, 월드, 로그와 모드팩 ZIP은 이 디렉터리에 복사하지 않는다.
