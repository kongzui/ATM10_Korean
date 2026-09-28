# Logistics Networks · 8.1-stable.5 완료 보고

1. **번역 범위:** 현재 설치된 Logistics Networks 1.13.0의 일반 언어 454키와 가이드
   이름·설명 2키, GuideME 17페이지를 검수했어요. 언어는 150·150·154개씩 나누고 가이드는
   노드·렌치·필터·컴퓨터별로 대조했어요. Step Crafter는 시작하지 않았어요.
2. **파일:** `working/logisticsnetworks/`에 현재 영어·한국어·검수 근거를 저장하고,
   `output/8.1/resourcepack/ATM10_Korean/assets/logisticsnetworks/`에 언어 1파일,
   GuideME 등록 1파일, 한국어 가이드 17파일을 추가했어요. 검증 스크립트·배포 안내·계획서·현황도
   갱신했어요. 이전 계획서와 작업 관련 Markdown 자동 커밋 규칙은 `9228eea`에 반영했어요.
3. **재사용과 새 번역:** 현재 JAR에 한국어가 없어 재사용 0개예요. 언어 456키 중 신규 한국어
   436개, 공식 모드명·단위·입력 예시 등의 원문 유지 20개예요. 가이드 17페이지도 새로 번역했어요.
4. **FTB Quests·KubeJS:** 퀘스트 1,000파일·현재 구조 66챕터와 KubeJS 871파일을 읽었어요.
   관련 참조가 없어 퀘스트 제목·Task·fallback·직접 표시 문구의 수정 대상은 없었어요.
   override 내용은 stable.4와 같아요.
5. **검증:** 전체 JSON 1,802개, SNBT 76개, JavaScript 27개의 문법·자료형·중복 키 검사와
   누적 번역 152,105개 값의 검증을 통과했어요. 새 모드의 모든 원문·검수 해시, 키·자리표시자·
   숫자·개행·서식과 GuideME YAML·태그·이미지·링크·앵커·인라인 코드를 대조했어요.
   발전 과제 JSON의 번역 키 참조 2개도 모두 언어 파일에 있어요. `ruff check .`, 변경한 Python
   파일의 포맷·컴파일 검사와 `git diff --check`를 통과했어요. 조사 전후 인스턴스 6,345파일의
   경로·크기·수정 시각이 같았어요. 원문의 오래된 설명을 교정한 근거는
   [가이드 검수 기록](logisticsnetworks_guide.md)에 있어요.
6. **실제 적용:** Java·Minecraft 프로세스가 없는 상태에서 저장소 적용 스크립트의 모의 적용 후
   19개 파일을 적용했어요. 대상은 아래 `game_root`이며 `source_root`는 설정되지 않았어요.
   백업·복구 목록을 만들고 적용 해시와 범위 밖 변경 0개를 확인했어요. `options.txt` 해시도 같아요.
7. **남은 확인:** 이번 범위의 텍스트 미번역·수동 번역 검토 항목은 없어요. 원본 그림 속 영어는
   그대로예요. 현재 활성 팩은 stable.1 ZIP이므로 새 stable.5 ZIP을 넣고 활성화한 뒤
   노드·필터·렌치·컴퓨터의 화면 폭, 가이드 링크 이동을 게임에서 확인해야 해요.
   실제 게임 화면 검증은 실행하지 않았어요. 다음 번역 대상은 Step Crafter 79키예요.

## 적용과 배포 경로

- 실제 적용 폴더:
  `C:/Users/moon9/curseforge/minecraft/Instances/All the Mods 10 - ATM10 (1)/resourcepacks/ATM10_Korean/assets/logisticsnetworks/`
- 적용 파일: `lang/ko_kr.json`, `guideme_guides/guide.json`,
  `guides/logisticsnetworks/guide/_ko_kr/` 아래의 17개 Markdown 페이지.
- 백업·복구 목록: `temp/backups/20260927_020750_565040/backup_manifest.json`.
- 정확한 파일 목록과 적용 검증: [적용 기록](../../../../versions/8.1/reports/logisticsnetworks_apply.json).
- 누적 리소스팩: `temp/releases/8.1-stable.5/ATM10_Korean_8.1-stable.5_resourcepack.zip`
  (2,387파일, 5,167,234바이트).
- 누적 overrides: `temp/releases/8.1-stable.5/ATM10_Korean_8.1-stable.5_overrides.zip`
  (335파일, 6,456,261바이트).
- 두 ZIP 모두 CRC·루트·전체 내용 해시를 검증했어요. ZIP과 백업은 Git에 넣지 않아요.
- 상세 SHA256: [패키지 목록](../../../../versions/8.1/manifests/8.1-stable.5_packages.json).
- 전체 검증: [stable.5 검증](../../../../versions/8.1/reports/8.1-stable.5_stable_validation.json).

## 작업 단위 커밋

- `9228eea` — Ad Astra 완료 계획과 작업 문서 자동 커밋 규칙 갱신.
- `7aac04a` — Logistics Networks 일반 언어 454키 번역과 검수 추가.
- `6fbd2b1` — Logistics Networks 가이드 17페이지와 표시 경로 번역 추가.
- 이후 stable.5 배포·계획서·검증·적용 결과를 독립된 마지막 커밋으로 정리해요.

원본 JAR, 월드, 7.1 산출물과 개인 설정은 수정하지 않았어요. 보조 번역 실행 코드도 추가하지 않았어요.
