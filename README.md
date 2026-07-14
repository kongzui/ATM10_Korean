# ATM10 7.1 한국어 번역

이 문서는 사용자를 위한 프로젝트 소개, 사용법, 경로 설정과 주요 명령을 안내해요. 작업 규칙은
`AGENTS.md`, 선택한 모드의 처리 순서는 `PLAN.md`, 번역 대상 분류와 상태는
`docs/MOD_TRANSLATION_PLAN.md`에서 관리합니다.

All the Mods 10 7.1을 모드별로 완성도 있게 한글화하기 위한 작업 저장소예요. 모드 언어 파일뿐
아니라 관련 FTB Quests와 KubeJS 표시 문구도 함께 다루며, 원본 모드 JAR은 수정하지 않아요.

## 사용법

원하는 모드 이름이나 `docs/MOD_TRANSLATION_PLAN.md`의 항목을 골라 요청하면 돼요.

> Applied Energistics 2 전체 한글화해 줘.

작업 결과는 하나의 누적형 `ATM10_Korean` 리소스팩과 필요한 override에 계속 더해집니다. 완성하고
검증한 번역 또는 기능 산출물은 Minecraft와 Java가 실행 중이지 않을 때 설정된 대상에 자동으로
적용해요. 조사나 문서 수정만 요청한 작업은 실제 경로에 적용하지 않습니다.

## 디렉터리

- `glossary/`: 확정한 용어와 보류 중인 용어
- `reports/`: 조사 결과, 진행 상황과 검수 기록
- `manifests/`: 다시 만들 수 있는 파일·키 개수 목록
- `working/`: 번역 작업 중인 파일
- `output/resourcepack/`: 검수를 마친 누적형 `ATM10_Korean` 리소스팩
- `output/overrides/`: FTB Quests와 KubeJS 등의 검수 완료본
- `scripts/`: 조사, 검증과 적용 도구
- `temp/`: Git에서 제외하는 재생성 가능 임시 자료와 적용 백업

## 기기별 경로 설정

저장소 루트의 `local_paths.example.json`을 `local_paths.json`으로 복사한 뒤 현재 기기의 절대
경로를 `/` 형식으로 적습니다. `local_paths.json`은 Git에서 제외되므로 기기마다 다른 설정을
안전하게 유지할 수 있어요.

```json
{
  "source_root": "C:/Users/your-name/Desktop/ATM10_source",
  "game_root": null
}
```

- 원본 조회에는 `source_root`가 있으면 우선 사용하고, 없으면 `game_root`를 사용합니다.
- 적용할 때는 설정된 각 경로를 대상으로 하며, 둘 다 설정되어 있으면 둘 다 사용합니다.
- `game_root`가 `null`이면 `source_root`에만 적용합니다.
- `--instance`를 지원하는 기존 명령에 단일 경로를 지정하면 로컬 설정 대신 그 경로를 사용합니다.

## 주요 명령

PowerShell에서 저장소 루트를 현재 폴더로 두고 실행합니다.

설치 모드와 번역 원본을 다시 조사하려면 다음 명령을 사용해요.

```powershell
python scripts/discover.py
```

실제 경로의 작업 전후 상태를 기록하고 비교할 수 있어요.

```powershell
python scripts/snapshot_instance.py create
python scripts/snapshot_instance.py compare
```

검증된 누적 산출물의 적용 대상을 먼저 확인하고 적용하려면 다음 명령을 사용합니다.

```powershell
python scripts/apply_translations.py --dry-run
python scripts/apply_translations.py
```

전체 조사 결과는 `reports/discovery.md`에서 확인할 수 있어요.
