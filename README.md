# ATM10 7.1 한국어 번역

All the Mods 10 7.1을 모드별로 완성도 있게 한글화하기 위한 작업 저장소예요. 특정 모드 번역은 리소스팩 언어 파일만 뜻하지 않아요. 그 모드와 관련된 FTB Quests와 KubeJS 표시 문구까지 함께 조사하고, 검증 후 실제 게임에 적용하는 것이 한 작업입니다. 원본 모드 JAR은 항상 수정하지 않아요.

## 사용자가 기억할 것

원하는 모드 이름만 알려 주면 돼요.

> Applied Energistics 2 전체 한글화해 줘.

그러면 다음을 한꺼번에 처리합니다.

1. 모드의 아이템·블록·기계·버튼·툴팁을 번역합니다.
2. ATM10 FTB Quests에서 그 모드와 관련된 챕터·퀘스트를 찾아 제목과 설명을 번역합니다.
3. KubeJS에 관련 표시 문구가 있는지 찾아 함께 번역합니다.
4. 리소스팩용인지 덮어쓰기용인지 구분해 프로젝트에 저장합니다.
5. JSON/SNBT 문법, 키, 자리표시자와 서식 코드를 검사합니다.
6. 기존 퀘스트·KubeJS 파일을 덮어써야 하면 먼저 프로젝트에 백업합니다.
7. 검증된 결과를 실제 ATM10 인스턴스에 적용하고 변경 수를 짧게 보고합니다.

모드 번역은 하나의 누적형 `ATM10_Korean` 리소스팩에 계속 더합니다. 모드마다 리소스팩을 따로 만들지 않아요. 게임 안에서 리소스팩을 켜는 설정까지 자동 변경하는 것은 별도 요청이 있을 때만 수행합니다.

## 디렉터리

- `glossary/`: 확정한 용어와 보류 중인 용어
- `reports/`: 조사 결과, 진행 상황, 검수 기록
- `manifests/`: 스크립트로 다시 만들 수 있는 파일·키 개수 목록
- `working/`: 번역 작업 중인 작은 단위의 파일
- `output/resourcepack/`: 검수를 마친 누적형 `ATM10_Korean` 리소스팩
- `output/overrides/`: FTB Quests, KubeJS 등 덮어쓰기용 검수 완료본
- `scripts/`: 읽기 전용 조사와 검증 도구
- `temp/`: Git에서 제외하는 재생성 가능 임시 자료

## 기기별 경로 설정

저장소 루트의 `local_paths.example.json`을 `local_paths.json`으로 복사한 뒤 현재
기기의 절대 경로를 `/` 형식으로 적습니다. `local_paths.json`은 Git에서 제외되므로
PC와 노트북이 서로 다른 설정을 안전하게 유지합니다.

```json
{
  "source_root": "C:/Users/your-name/Desktop/ATM10_source",
  "game_root": null
}
```

- 원본 조회·빌드·검증은 `source_root`가 있으면 우선 사용하고, 없으면 `game_root`를
  사용합니다.
- 번역 적용은 설정된 `source_root`와 `game_root` 모두를 대상으로 합니다.
- `game_root`가 `null`이면 실제 게임 적용만 건너뛰며 `source_root`에는 적용합니다.
- 기존 명령처럼 `--instance`를 지정하면 로컬 설정 대신 그 단일 경로를 사용합니다.

## 조사 다시 실행하기

PowerShell에서 저장소 루트를 현재 폴더로 두고 실행합니다.

```powershell
python scripts/discover.py
```

조사 스크립트는 인스턴스에서 파일을 읽고 `manifests/`에 CSV와 JSON만 씁니다. JAR을 추출하거나 수정하지 않습니다. 번역 적용은 조사 스크립트와 별도의 검증·백업 절차로 수행해요.

작업 전 상태 기록과 변경 범위 확인에는 다음 스냅샷 도구를 사용합니다.

```powershell
python scripts/snapshot_instance.py create
python scripts/snapshot_instance.py compare
```

검증된 누적 산출물 전체를 현재 기기에 설정된 모든 대상에 적용하려면 다음 명령을
사용합니다. 먼저 `--dry-run`으로 대상과 변경 파일을 확인할 수 있으며, 실제 적용은
기존 파일을 `temp/backups/`에 백업한 뒤 파일 해시와 계획 밖 변경 여부까지 검사합니다.

```powershell
python scripts/apply_translations.py --dry-run
python scripts/apply_translations.py
```

사용자는 문서를 전부 읽지 않아도 괜찮아요. 전체 조사 결과가 궁금할 때만 `reports/discovery.md`를 보면 됩니다.
