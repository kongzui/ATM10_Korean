# ATM10 7.1 번역 대상 조사 보고서

조사일: 2026-07-12  
원본 인스턴스: `C:\Users\moon9\curseforge\minecraft\Instances\All the Mods 10 - ATM10`  
프로젝트: `C:\Users\moon9\Desktop\!경제\!코딩\!github\ATM10_Korean`

## 조사 범위와 안전성

`manifest.json`에서 현재 설치된 All the Mods 10 버전과 Minecraft 1.21.1을 확인했다. `mods`, `config/ftbquests`, `kubejs`를 읽기만 했고 JAR을 추출하거나 다시 쓰지 않았다. 조사 전후 원본의 파일 경로·크기·수정 시각은 `scripts/snapshot_instance.py`로 비교한다.

아래 수치는 `scripts/discover.py`가 만든 `manifests/`를 기준으로 한다. FTB Quests 키 수와 KubeJS 표시 문구 수는 정규식 기반 추정치이므로 각각 `추정`, `후보`로 표기한다.

## 발견한 번역 관련 위치

| 종류                  | 원본 위치                                             | 조사 결과                                              | 향후 산출물                                      |
| --------------------- | ----------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------ |
| 모드 언어 파일        | `mods/*.jar` 안의 `assets/<namespace>/lang/*.json`    | JAR 480개                                              | `output/resourcepack/assets/.../lang/ko_kr.json` |
| FTB Quests            | `config/ftbquests/quests/lang/`                       | 언어·생성 보조 파일 포함 736개, 전체 퀘스트 파일 864개 | `output/overrides/config/ftbquests/...`          |
| KubeJS 언어 파일      | `kubejs/assets/*/lang/*.json`                         | 117개                                                  | 리소스팩 또는 검증된 KubeJS override             |
| KubeJS 직접 표시 문구 | `kubejs/**/*.js`                                      | 204개 JS에서 표시 가능 문구 후보 225행                 | 필요 시 `output/overrides/kubejs/...`            |
| 기타 후보             | `config/fancymenu/assets/`, `config/konkrete/locals/` | 3개                                                    | 수동 확인 후 결정                                |

기타 후보 3개는 `language_color.png`, `language_gray.png`, `config/konkrete/locals/en_us.local`이다. 앞의 두 이미지는 파일명만 언어 관련 패턴과 일치하므로 번역 대상인지는 불확실하다. `en_us.local`의 한국어 대응 방식도 아직 확인하지 않았다.

## 모드 JAR 언어 파일

- JAR 480개를 모두 ZIP으로 열어 조사했으며, JAR 열기 오류는 0개다.
- `en_us.json`이 있는 JAR은 381개다.
- 모드 자체 `ko_kr.json`이 있는 JAR은 149개이며, 이 149개는 모두 영어 파일도 함께 가진다.
- 영어는 있지만 한국어가 없는 JAR은 232개다.
- 대상 언어 파일이 없는 나머지 99개 JAR에는 라이브러리·데이터 전용 JAR 등이 섞일 수 있어 번역 불필요 모드 99개라고 단정하지 않는다.
- 언어 네임스페이스 행 기준 영어 388개/150,054키, 한국어 152개/54,749키가 파싱됐다. 여러 JAR이 같은 네임스페이스를 제공할 가능성이 있어 이 합계는 고유 번역 키 총수와 완전히 같지 않을 수 있다.

원본 오류가 1건 있다. `mcw-trapdoors-1.1.5-mc1.21.1neoforge.jar`의 `assets/mcwtrpdoors/lang/ko_kr.json`이 120행 부근에서 JSON 쉼표 오류로 파싱되지 않는다. 원본 JAR은 수정하지 않았으며 `manifests/errors.csv`에 기록했다. 따라서 “한국어 포함 JAR 149개”는 파일 존재 기준이고, 그중 최소 1개 파일은 그대로 사용할 수 없는 상태다.

## FTB Quests

- 원문: `config/ftbquests/quests/lang/en_us.snbt`
- 현재 한국어: `config/ftbquests/quests/lang/ko_kr.snbt`
- 챕터 원본: `config/ftbquests/quests/chapters/*.snbt` 64개
- 챕터별 병합 보조 파일: `config/ftbquests/quests/lang/<locale>/chapters/*.snbt_merged`

최상위 `키: 값` 행을 세는 방식으로 영어 8,436키, 한국어 6,073키를 추정했다. 공통 5,978키, 한국어에 없는 영어 키 2,458개, 한국어에만 있는 키 95개다. 이 수치는 정식 SNBT 파서 결과가 아니며, 중첩 구조나 자료형까지 검증한 값도 아니다.

`*.snbt_merged`는 챕터별 범위를 잡는 데 유용하지만 생성·갱신 주체가 확실하지 않다. 따라서 향후 편집 기준 파일을 정하기 전까지는 직접 수정하지 않고, `manifests/ftbquest_chapters.csv`의 작업량 추정에만 사용한다.

## KubeJS

KubeJS 언어 JSON은 전체 로케일 합계 117개다. 영어는 6개 파일 1,897키이고 한국어는 `kubejs/assets/atm/lang/ko_kr.json` 한 파일 5키뿐이다. 영어 파일이 있는 네임스페이스는 `atm`, `compactmachines`, `forbidden_arcanus`, `hostilenetworks`, `kubejs`, `modern_industrialization`이다.

JS 204개를 `displayName`, `Text.of`, 상태 메시지, 툴팁, Ponder 계열 패턴으로 검사해 사용자에게 표시될 가능성이 있는 225행을 찾았다. `manifests/kubejs_text_candidates.csv`는 후보 목록이며, 주석·개발용 문자열·실행되지 않는 코드가 포함될 수 있어 실제 표시 여부는 수동 확인해야 한다. 언어 키가 아닌 직접 문자열은 단순 리소스팩만으로 바뀌지 않을 수 있다.

## 리소스팩과 덮어쓰기 번역의 구분

- JAR의 `assets/<namespace>/lang/ko_kr.json`을 대체·보완하는 작업은 원본 JAR을 건드리지 않고 `output/resourcepack/`에 같은 경로로 만든다.
- FTB Quests의 `config/ftbquests/quests/lang/ko_kr.snbt`는 일반 모드 리소스팩과 별개인 인스턴스 설정 덮어쓰기 산출물로 관리한다.
- KubeJS `assets/.../lang`은 리소스팩으로 제공 가능한지 먼저 검증한다. JS에 직접 박힌 표시 문구를 바꾸려면 KubeJS 스크립트 override가 필요할 수 있다.
- 어떤 override도 사용자의 명시적 요청과 별도 적용·백업 절차 없이는 실제 인스턴스에 넣지 않는다.

## 위험과 주의점

1. 현재 ATM10의 `ko_kr.snbt`는 존재만으로 완성된 정답이라 볼 수 없으므로 영어 원문과 대조한다.
2. FTB Quests 키 수는 추정치이고 `*.snbt_merged`의 편집 권위가 불확실하다.
3. 프로젝트 리소스팩, KubeJS assets, 모드 내장 언어 파일이 같은 키를 제공하면 로딩 우선순위에 따라 결과가 달라질 수 있다.
4. KubeJS 직접 문자열은 코드 동작과 결합돼 있어 단순 치환 시 스크립트를 깨뜨릴 수 있다.
5. `%s`, `%1$s`, `%d`, `{0}`, 줄바꿈, 색상 코드, 이스케이프가 달라지면 표시 오류나 런타임 오류가 생길 수 있다.
6. 원본 `mcwtrpdoors` 한국어 JSON 문법 오류는 프로젝트 출력에서 별도로 보정할 수 있지만 JAR 자체를 고치면 안 된다.

## 권장 첫 작업

첫 실제 번역 단위로는 FTB Quests `refined_storage` 챕터를 권장한다. 챕터별 추정치가 영어 145키, 현재 한국어 0키라서 목표 범위 100~200개에 들어가고, 기존 한국어와 병합할 위험이 작으며 주요 플레이 동선과도 가깝다.

작업은 원본에서 직접 편집하지 않고 `working/ftbquests/refined_storage/` 같은 작은 작업 폴더에 영어 기준 키 목록과 빈 검토 상태를 만든 뒤 시작한다. 이번 조사 단계에서는 그 파일을 만들거나 번역하지 않았다.

## 생성된 매니페스트

- `discovery_summary.json`: 전체 요약
- `jar_inventory.csv`: 480개 JAR의 언어 파일 유무와 오류
- `jar_language_files.csv`: JAR/네임스페이스별 영어·한국어 키 수
- `ftbquest_chapters.csv`: 64개 퀘스트 챕터별 추정 키 수
- `kubejs_languages.csv`: KubeJS 언어 JSON 목록과 키 수
- `kubejs_text_candidates.csv`: KubeJS 표시 문구 후보
- `other_translation_candidates.csv`: 기타 후보
- `errors.csv`: 원본 읽기·문법 오류 목록
