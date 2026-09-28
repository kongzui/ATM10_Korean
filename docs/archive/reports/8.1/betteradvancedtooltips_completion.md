# Better Advanced Tooltips 완료 보고

2026-09-28 · ATM10 8.1 · 누적 배포 `8.1-stable.7`

## 번역과 문서

- 현재 `2101.1.0-build.5`의 설정 언어 5키를 모두 새로 번역했어요. 기존 한국어 재사용은 0키예요.
- `working/betteradvancedtooltips/`에 원문·번역·검수·원본 해시·표시 경로 근거를 기록했어요.
- 완성 언어 파일은 `output/8.1/resourcepack/ATM10_Korean/assets/betteradvancedtooltips/lang/ko_kr.json`이에요.
- FTB Quests 1,000파일·66챕터와 KubeJS 871파일에 관련 참조가 없어 변경하지 않았어요.
  별도 가이드도 없어요.
- 계획서·번역 현황·용어집·보조 번역 제외 문서·배포 안내를 함께 갱신했어요.

## 검증

- 현재 JAR 해시와 영어 전체, 한국어 키·중복·자료형·보호 문자열, 검수 기록과 output 일치를 확인했어요.
- 전체 JSON 1,804개·SNBT 76개·JavaScript 27개와 기존 번역 보존 검사를 통과했어요.
- 수정한 Python 문법과 저장소 Ruff 검사, `git diff --check`를 통과했어요.
- `betteradvancedtooltips_validation.json`과 `8.1-stable.7_stable_validation.json`에 근거를 기록했어요.

## 배포와 실제 파일 적용

- `temp/releases/8.1-stable.7/`에 리소스팩·override ZIP 두 개를 생성했어요.
  리소스팩 2,389파일, override 335파일의 CRC와 전체 내용을 검증했어요.
- ZIP 해시는 `../manifests/8.1-stable.7_packages.json`에 있어요. override는 stable.6과 같아요.
- 조사·검증·패키징 전후 인스턴스 6,365파일의 경로·크기·수정 시각이 일치했어요.
- Java·Minecraft 종료 상태에서 기존 적용 스크립트의 dry-run과 실제 적용을 수행했어요.
- 적용 대상은 `C:/Users/moon9/curseforge/minecraft/Instances/All the Mods 10 - ATM10 (1)/`
  아래 `resourcepacks/ATM10_Korean/assets/betteradvancedtooltips/lang/ko_kr.json` 한 파일이에요.
  새 파일의 되돌리기 정보는 `temp/backups/20260928_215259_756127/backup_manifest.json`에 있어요.
- 계획한 파일 외의 변경은 없고 `options.txt`의 해시도 같아요. 근거는
  `betteradvancedtooltips_apply.json`에 기록했어요.
- 현재 선택된 팩은 `ATM10_Korean_8.1-stable.1_resourcepack.zip`이에요.
  새 stable.7 ZIP 또는 최신 폴더팩을 활성화해야 새 번역이 표시돼요.

## 실제 게임에서 남은 확인

설정 5키는 번역 완료지만 게임 화면은 확인하지 않았어요. 코드가 직접 표시하는 `Fuel:`과
데이터 오류 안내는 원문으로 유지해요. 보조 번역 코드는 추가하지 않았어요.
[표시 경로 조사](../../../../versions/8.1/reports/betteradvancedtooltips_translation.md)에서 구체적인 근거를 확인할 수 있어요.
다음 대상은 Borderless Window 21키예요.
