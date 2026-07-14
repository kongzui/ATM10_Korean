# AE2 내장 가이드북 한국어 번역 계획

## 1. 목표

ATM10 7.1에 설치된 Applied Energistics 2의 GuideME 내장 가이드북을 한국어로
완성한다. 영어 원본과 같은 문서 구조를 유지하고, 기존 `ATM10_Korean` 누적
리소스팩을 통해 적용한다.

이 계획의 1차 범위는 AE2 본체 가이드 125페이지다. AE2WTLib, ExtendedAE,
EnderDrives 등 연동 모드의 가이드는 AE2 본체 완료 후 별도 계획으로 진행한다.

## 2. 기준 환경

- 모드팩: All the Mods 10 7.1
- Minecraft: 1.21.1
- NeoForge: 21.1.234
- AE2: `appliedenergistics2-19.2.17.jar`
- GuideME: `guideme-21.1.16.jar`
- 영어 원본: `assets/ae2/ae2guide/`
- 한국어 경로: `assets/ae2/ae2guide/_ko_kr/`
- 영어 원본 문서: 125페이지
- 번역 대상 분량: 영어 약 30,534단어
- 그림: PNG 40개
- 구조물·장면 데이터: SNBT 123개

원본 JAR은 읽기 전용으로 취급하며 추출, 수정, 재압축하지 않는다.

## 3. 프로젝트 경로

### 작업본

```text
working/ae2/ae2guide/_ko_kr/
```

### 검증된 리소스팩 산출물

```text
output/resourcepack/ATM10_Korean/assets/ae2/ae2guide/_ko_kr/
```

### 실제 인스턴스 적용 경로

```text
C:\Users\moon9\curseforge\minecraft\Instances\All the Mods 10 - ATM10\
resourcepacks\ATM10_Korean\assets\ae2\ae2guide\_ko_kr\
```

그림과 SNBT는 영어 기본 리소스를 사용한다. 한국어 문서에 별도의 현지화 이미지가
필요한 경우가 아니라면 `_ko_kr/assets/`로 복제하지 않는다.

## 4. 현재 진행 상태

### 완료: 1차 배치 — 시작·월드

- 페이지: 5개
- 영어 단어: 1,976개
- 신규 번역: 5개
- 기존 한국어 재사용: 0개
- 실제 인스턴스 적용: 완료
- 예상 밖 인스턴스 변경: 0개
- 남은 AE2 본체 문서: 120페이지

완료 파일:

```text
index.md
getting-started.md
tips-and-tricks.md
ae2-mechanics/meteorites.md
ae2-mechanics/certus-growth.md
```

관련 커밋:

- `6fbc23e` — `AE2 가이드 첫 배치 번역`
- `6df557a` — `AE2 가이드 안전 적용 도구 추가`
- `48f5d67` — `AE2 가이드 첫 배치 적용 기록`

게임을 직접 실행한 화면 검증은 아직 하지 않았다. 2차 배치 시작 전에 목차, 한글
본문, 장면, 링크와 조합법 표시를 확인한다.

## 5. 번역 배치 계획

각 배치는 번역, 자동 검증, 리소스팩 생성, 커밋, 실제 적용, 적용 기록 순서로
완료한다. 분량이 큰 배치는 문맥을 유지할 수 있는 범위에서 둘로 나눌 수 있다.

### 2차 배치 — AE2 핵심 원리

- 7페이지
- 약 2,104단어
- 선행 작업: 1차 배치 게임 화면 확인

```text
ae2-mechanics/ae2-mechanics-index.md
ae2-mechanics/bytes-and-types.md
ae2-mechanics/devices.md
ae2-mechanics/energy.md
ae2-mechanics/import-export-storage.md
ae2-mechanics/me-network-connections.md
ae2-mechanics/cable-subparts.md
```

바이트, 종류, 에너지, 장치, 네트워크 연결, 반입·반출·저장 용어를 확정한다.
이 배치의 용어는 저장 셀, 채널과 자동 제작 문서의 기준으로 사용한다.

### 3차 배치 — 네트워크 심화

- 5페이지
- 약 2,245단어

```text
ae2-mechanics/channels.md
ae2-mechanics/subnetworks.md
ae2-mechanics/p2p-tunnels.md
ae2-mechanics/quantum-bridge.md
ae2-mechanics/spatial-io.md
```

표, 채널 수, P2P 입력·출력 관계, 서브네트워크와 공간 저장소 설명을 집중 검수한다.

### 4차 배치 — 자동 제작 원리

- 1페이지
- 약 1,781단어
- 복잡도가 높으므로 단독 처리

```text
ae2-mechanics/autocrafting.md
```

패턴, 제작 CPU, 보조 처리 장치, 제작 저장소와 처리 패턴의 역할을 현재 AE2
리소스팩 용어와 일치시킨다.

### 5차 배치 — 수정 농장 예제

- 4페이지
- 약 1,810단어

```text
example-setups/advanced-certus-farm.md
example-setups/semiauto-certus-farm.md
example-setups/simple-certus-farm.md
example-setups/amethyst-farm.md
```

구조물 단계, 방향, 블록 배치와 자동 수확 과정을 게임 장면과 함께 검증한다.

### 6차 배치 — 저장·물류 예제

- 8페이지
- 약 3,387단어

```text
example-setups/bucket-emptier.md
example-setups/bucket-filler.md
example-setups/cell-dumper-filler.md
example-setups/interface-autostocking.md
example-setups/level-emitter-autostocking.md
example-setups/pipe-subnet.md
example-setups/specialized-local-storage.md
example-setups/storage-types.md
```

분량과 장면 수가 많으므로 필요하면 `bucket/cell/autostocking`과
`pipe/local storage/storage types` 두 작업으로 나눈다.

### 7차 배치 — 자동화·제작 예제

- 9페이지
- 약 3,053단어

```text
example-setups/example-setups-index.md
example-setups/charger-automation.md
example-setups/furnace-automation.md
example-setups/main-network.md
example-setups/ore-fortuner.md
example-setups/processor-automation.md
example-setups/recursive-crafting-setup.md
example-setups/regulated-cobble-gen.md
example-setups/throw-in-water-automation.md
```

자동 제작 원리 배치를 완료한 뒤 진행한다. 조합법의 입력·출력과 장면의 진행 순서를
원문대로 보존한다.

### 8차 배치 — 재료·장식 블록

- 27페이지
- 약 1,212단어
- 짧은 아이템·블록 문서 중심

`items-blocks-machines/items-blocks-machines-index.md`와 Certus, Fluix,
Sky Stone, 프레스, 프로세서, 특이점, 장식 블록 문서를 포함한다.

아이템명과 블록명은 현재 프로젝트의 `assets/ae2/lang/ko_kr.json`과 정확히
일치시킨다.

### 9차 배치 — 도구·셀·업그레이드

- 21페이지
- 약 3,004단어

절단 칼, 렌치, 색상 도포기, 엔트로피 조작기, 물질 대포, 저장 셀, 공간 셀,
패턴, 업그레이드 카드, 무선 터미널 등을 포함한다.

AE2WTLib이 `items-blocks-machines/wireless_terminals.md`와 같은 리소스 경로를
제공하므로 이 문서는 두 JAR의 원문을 비교한 뒤 처리한다.

### 10차 배치 — 네트워크 인프라

- 15페이지
- 약 2,113단어

케이블, ME 제어기, 에너지 수용기·셀, 덮개, 양자 연결기, 석영 섬유,
공간 고정기, 토글 버스, 진동실, 공간 I/O 장치와 무선 액세스 포인트를 포함한다.

케이블 종류, 채널 전달, 전력 전달과 장면 구조를 2·3차 배치의 용어에 맞춘다.

### 11차 배치 — 기계

- 8페이지
- 약 1,220단어

셀 작업대, 충전기, 물질 응축기, 나무 손잡이, 수정 성장 가속기, 회로 인쇄기,
분자 조립기와 하늘 돌 탱크를 포함한다.

`Recipe`, `RecipeFor`와 `ae2:ConfigValue` 태그를 별도로 검사한다.

### 12차 배치 — 저장·입출력 장치

- 9페이지
- 약 2,467단어

형성·소멸 평면, ME 상자·드라이브, 반입·반출 버스, ME I/O 포트, 모니터와
ME 저장 버스를 포함한다.

반입과 반출의 방향, 필터, 우선순위와 연결 대상이 뒤바뀌지 않게 검수한다.

### 13차 배치 — 자동 제작 장치

- 3페이지
- 약 2,134단어

```text
items-blocks-machines/crafting_cpu_multiblock.md
items-blocks-machines/interface.md
items-blocks-machines/pattern_provider.md
```

4차 배치의 자동 제작 용어를 그대로 사용한다. 장면 내부 주석과 장치 연결 방향을
함께 확인한다.

### 14차 배치 — 접근·제어 장치

- 3페이지
- 약 2,009단어

```text
items-blocks-machines/level_emitter.md
items-blocks-machines/p2p_tunnels.md
items-blocks-machines/terminals.md
```

긴 GUI 이름, 임계값 조건, P2P 터널 종류와 터미널 기능을 검수한다.

## 6. 배치별 작업 절차

각 배치는 다음 순서를 지킨다.

1. 현재 AE2 JAR 버전과 영어 원문 파일을 확인한다.
2. 실제 인스턴스의 번역 관련 경로 스냅샷을 만든다.
3. 해당 배치에 필요한 기존 AE2 리소스팩 용어를 추출한다.
4. `working/ae2/ae2guide/_ko_kr/`에서 번역한다.
5. 빌드·검증 도구의 배치 파일 목록을 안전하게 확장한다.
6. 자동 검증이 통과하면 `output/`으로 승격한다.
7. 번역과 검증 도구 변경을 독립 커밋한다.
8. Java 또는 Minecraft 프로세스가 없는지 확인한다.
9. 기존 실제 대상 파일을 백업한 뒤 리소스팩에 적용한다.
10. 적용 파일 해시와 인스턴스 전체 변경 범위를 검증한다.
11. 적용 상태를 기록하고 별도 커밋한다.

Java 또는 Minecraft가 실행 중이면 1~7단계까지만 완료하고 실제 적용은 보류한다.

## 7. 번역 규칙

- AE2 아이템·블록·메뉴 이름은 현재 프로젝트의 AE2 리소스팩과 일치시킨다.
- 프로젝트 glossary와 `AGENTS.md`를 우선한다.
- `navigation.title`과 화면에 표시되는 본문만 번역한다.
- 공식 모드명 `Applied Energistics 2`와 `AE2`는 유지한다.
- 링크 문구는 번역하되 링크 대상은 변경하지 않는다.
- 장면 주석의 표시 문구는 번역하되 좌표와 색상은 변경하지 않는다.
- 숫자, 조건, 방향, 수량, 확률과 기능 차이를 생략하지 않는다.
- 원문에 없는 공략이나 설명을 추가하지 않는다.
- 일본어·중국어 문서는 모호한 의미를 확인하는 참고 자료로만 사용한다.

다음 항목은 번역하지 않는다.

- 리소스 ID와 namespace
- Markdown 링크 주소와 앵커
- 이미지·구조물 경로
- 태그 이름과 속성 이름
- `id`, `src`, `name` 속성값
- 카메라 좌표, 회전값, 색상, 축척과 `{true}` 값
- 명령어와 인라인 코드

## 8. 자동 검증

현재 도구:

```text
scripts/build_ae2_guide.py
scripts/verify_ae2_guide.py
scripts/apply_ae2_guide.py
```

각 배치에서 다음 항목을 검사한다.

- 영어 원본과 한국어 파일 목록
- 누락·불필요 파일
- YAML front matter와 `navigation.title` 외 메타데이터 보존
- GuideME와 HTML 태그의 이름, 순서, 속성값
- 인라인 코드와 명령어
- Markdown 링크와 이미지 대상
- 구조물 SNBT 참조
- 제목 단계와 수평선
- 한국어 본문 존재 여부
- 영어 문단 잔존 후보
- UTF-8 BOM
- 작업본과 `output/` 파일 내용·해시

전체 완료 전에는 추가로 다음 검증을 구현하거나 확장한다.

- 125개 영어·한국어 파일의 전체 목록 비교
- 페이지 앵커 존재 여부
- 태그 열기·닫기 중첩 검사
- ItemLink 아이템 ID와 Recipe ID 확인
- AE2 업데이트 전후 파일별 원문 해시 비교

## 9. 게임 검증

각 배치 적용 후 최소한 다음을 확인한다.

1. G 키를 길게 눌러 가이드가 정상적으로 열리는지 확인한다.
2. 왼쪽 목차 제목이 한국어로 표시되는지 확인한다.
3. 이전·다음 페이지와 본문 링크가 이동하는지 확인한다.
4. ItemLink의 아이템 이름과 툴팁이 표시되는지 확인한다.
5. Recipe와 RecipeFor가 정상 렌더링되는지 확인한다.
6. 이미지와 GameScene이 표시되는지 확인한다.
7. 장면 회전, 확대·축소와 주석 표시가 작동하는지 확인한다.
8. 한국어 파일이 아직 없는 페이지가 영어로 fallback되는지 확인한다.
9. 긴 한국어 문장이 잘리거나 겹치지 않는지 확인한다.

게임에서 발견한 문제는 바로 원본 의미, 태그 구조와 실제 표시 결과를 대조한 뒤 해당
배치 안에서 수정한다.

## 10. 커밋과 적용 원칙

- 검증 가능한 번역 배치마다 독립 커밋한다.
- 안전 적용 도구의 기능 변경은 번역 커밋과 분리한다.
- 실제 적용 완료 기록은 필요할 때 별도 커밋한다.
- `AGENTS.md`, `PLAN.md`와 사용자의 기존 변경은 스테이징하지 않는다.
- `git push`, `git reset`, `git rebase`, `git commit --amend`는 수행하지 않는다.
- 실제 적용 전 백업과 되돌릴 방법을 마련한다.
- 원본 JAR과 월드 세이브는 수정하지 않는다.

## 11. 전체 완료 조건

다음 조건을 모두 만족해야 AE2 본체 가이드 번역을 완료로 판정한다.

- AE2 본체 영어 문서 125개에 대응하는 한국어 문서가 모두 존재한다.
- 미번역 페이지와 불필요한 한국어 페이지가 0개다.
- front matter, 태그, 링크, 이미지, 구조물과 조합법 검증 오류가 0개다.
- 영어 문단 잔존 후보를 모두 검토했다.
- 프로젝트 AE2 리소스팩과 가이드의 아이템·기술 용어가 일치한다.
- 전체 가이드를 게임에서 순회하며 목차와 주요 렌더링 기능을 확인했다.
- 실제 인스턴스에 백업 후 적용했다.
- 적용 파일 해시가 프로젝트 산출물과 일치한다.
- 원본 JAR과 번역 범위 밖의 인스턴스 파일 변경이 0개다.
- 완료 상태와 남은 연동 모드 후속 범위를 기록했다.

## 12. 바로 다음 작업

1. 게임에서 1차 배치 5페이지를 확인한다.
2. 문제가 없으면 2차 배치 7페이지의 영어 원문과 기존 AE2 용어를 대조한다.
3. `Bytes and Types`부터 번역해 바이트와 종류 용어를 먼저 확정한다.
4. 2차 배치 전체를 검증·커밋·적용한다.
