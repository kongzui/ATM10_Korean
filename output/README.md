# ATM10 버전별 번역 산출물

각 ATM10 버전의 실제 배포 파일을 독립적으로 보관한다.

```text
output/
├─ 7.1/
│  ├─ release.json
│  ├─ resourcepack/
│  └─ overrides/
└─ 8.1/
   ├─ release.json
   ├─ resourcepack/
   └─ overrides/
```

- `resourcepack/`에는 해당 버전의 `ATM10_Korean` 리소스팩을 둔다.
- `overrides/`에는 해당 버전의 FTB Quests, KubeJS 등 덮어쓰기 파일을 둔다.
- `release.json`에는 검증 상태와 전체 적용 허용 여부를 기록한다.
- 조사·빌드·검증·적용 스크립트는 `version_context.json`의 활성 버전 폴더만 사용한다.
- 검증을 마친 이전 버전 폴더는 수정하지 않는다.

새 버전은 직전 검증 완료본을 새 버전 폴더로 복사해 시작한다. 곧바로 전체 적용하지 않고,
현재 설치본의 영어 원문과 충돌 경로를 재검수한 파일부터 선택 적용한다.
