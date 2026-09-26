# Step Crafter · 8.1-stable.6 완료 보고

1. **번역 범위:** 현재 Step Crafter 0.1.8의 블록 이름, 툴팁, 제작·요청·관리자·모니터 UI,
   설정 설명까지 영어 79키 전체를 검수했어요. 다음 UI 모드에는 착수하지 않았어요.
2. **파일:** `working/stepcrafter/`에 현재 영어·한국어·검수 근거를 저장했어요.
   완성본은 `output/8.1/resourcepack/ATM10_Korean/assets/stepcrafter/lang/ko_kr.json`이에요.
   검증 스크립트·용어집·계획서·현황·배포 안내도 함께 갱신했어요.
3. **재사용과 신규 번역:** 내장 한국어가 없어 재사용 0개, 신규 한국어 78개예요.
   공식 모드명 `Step Crafter` 1개는 원문을 유지해요. 나머지 텍스트 미번역은 없어요.
4. **관련 콘텐츠:** 별도 가이드가 없고, 제작법 해금용 발전 과제 48파일에 표시 문구가 없어요.
   FTB Quests 1,000파일·66챕터와 KubeJS 871파일에서도 관련 참조가 없어 수정하지 않았어요.
5. **검증:** 새 모드의 영어 전체·JAR 해시·검수 기록·키 순서·중복·자료형·자리표시자·숫자·
   개행·서식·이스케이프 검사를 통과했어요. 계산식과 별표 주석도 보존했어요.
   누적 JSON 1,803/SNBT 76/JavaScript 27개를 검증했고 오류는 없어요.
   `ruff check .`, 변경 Python 포맷·컴파일, `git diff --check`를 통과했어요.
   조사 전후 실제 인스턴스 6,364파일의 경로·크기·수정 시각이 같았어요.
6. **적용:** Java·Minecraft 프로세스가 없는 상태에서 모의 적용 후 언어 1파일을 적용했어요.
   설정된 `game_root`만 대상이며 `source_root`는 없어요. 적용한 내용의 해시를 대조하고
   범위 밖 변경 0개와 `options.txt` 해시 보존을 확인했어요. 정확한 경로·백업은 아래에 있어요.
7. **남은 확인:** 이번 범위의 수동 번역 검토 항목은 없어요. 실제 게임 화면의 폭·툴팁·
   수량 설정·관리자 검색·제작 상태는 아직 실행해서 확인하지 않았어요.
   현재 선택된 번역 팩은 stable.1 ZIP이므로 새 stable.6 ZIP 또는 최신 폴더팩 활성화가 필요해요.
   다음 대상은 Better Advanced Tooltips 5키예요.

## 적용과 배포 경로

- 실제 적용 파일:
  `C:/Users/moon9/curseforge/minecraft/Instances/All the Mods 10 - ATM10 (1)/resourcepacks/ATM10_Korean/assets/stepcrafter/lang/ko_kr.json`.
- 백업·복구 목록: `temp/backups/20260927_022645_133721/backup_manifest.json`.
- [적용 결과·보존한 활성 팩 설정](stepcrafter_apply.json).
- `temp/releases/8.1-stable.6/ATM10_Korean_8.1-stable.6_resourcepack.zip`:
  2,388파일, 5,169,120바이트.
- `temp/releases/8.1-stable.6/ATM10_Korean_8.1-stable.6_overrides.zip`:
  335파일, 6,456,261바이트. 내용과 해시는 stable.5와 같아요.
- 두 ZIP의 CRC·루트·파일 목록·전체 내용 해시를 검증했어요. ZIP과 백업은 Git에서 제외해요.

## 검증·배포 근거

- [언어·표시 경로 검수](stepcrafter_translation.md)
- [모드 검증](stepcrafter_validation.json)
- [누적 stable.6 검증](8.1-stable.6_stable_validation.json)
- [ZIP 파일 목록·SHA256](../manifests/8.1-stable.6_packages.json)
- [배포·설치 안내](../../../docs/releases/8.1-stable.6.md)

ZIP 두 개는 `temp/releases/8.1-stable.6/`에 생성했어요. 원본 JAR·월드·7.1 산출물은 보존하고
보조 번역 실행 코드는 추가하지 않아요. 언어와 표시 경로 검수는
`8a670aa` — `Step Crafter 언어 79키 번역과 표시 경로 검수 추가`로 커밋했어요.
누적 배포·검증·적용 기록과 관련 Markdown은 다음 독립 커밋으로 정리해요.
