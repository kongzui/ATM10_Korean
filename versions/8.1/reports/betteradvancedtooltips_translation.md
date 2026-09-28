# Better Advanced Tooltips 번역·표시 경로 검수

2026-09-28, ATM10 8.1의 `better-advanced-tooltips-2101.1.0-build.5.jar`를 읽기 전용으로 확인했어요.
원본 JAR 해시와 멤버 목록은 `working/betteradvancedtooltips/`에 기록했어요.

## 일반 언어와 관련 데이터

- 현재 영어 5키 전체를 새로 번역했어요. 내장 한국어와 기존 한국어 재사용은 0키예요.
- 크리에이티브 탭 툴팁 제거, 구성 요소 개수 툴팁 제거, 연료·태그·구성 요소 툴팁이에요.
- `BATConfig`의 다섯 Boolean 설정 이름이 영어 언어 키의 마지막 부분과 일치해요.
- `ItemStackMixin`은 구성 요소 개수를, `CreativeModeInventoryScreenMixin`은 크리에이티브
  탭 목록을 숨기는 설정을 사용해요. 구성 요소는 아이템 데이터이며 제작 부품을 뜻하지 않아요.
- JAR의 별도 책·가이드·발전 과제는 없어요. 폰트 JSON 두 개는 아이콘 매핑이에요.
- FTB Quests 1,000파일·66챕터와 KubeJS 871파일에서 모드 이름·네임스페이스 참조는 없어요.
  관련 override 변경은 없어요. 조사 파일 해시는 `display_audit.json`에 있어요.

## 언어 파일로 바뀌지 않는 표시

현재 JAR의 클래스를 `javap -p -c -constants`로, 문자열 결합 상수는 `javap -p -v`로 확인했어요.

- `BATClientEventHandler`: 연료 줄은 `MutableComponent.append(String)`으로 `Fuel:`을
  직접 붙여요. `t`, `s`, `x` 단위도 문자열 결합 상수예요.
- 같은 클래스의 데이터 표시 오류 문구는 `<식별자> errored, see log`를 만든 뒤
  `Component.literal`로 표시해요. 한국어 언어 키를 새로 추가해도 연결되지 않아요.
- 태그·구성 요소 ID와 값은 레지스트리에서 가져오는 진단 데이터로 유지해요.
- `BATIcons`와 `TooltipTagType`의 문자들은 전용 폰트의 아이콘이에요. 번역하지 않아요.

위 직접 표시 문구는 기본 안정판의 보조 코드 제외 방침에 따라 원문으로 유지해요.
설정 언어 5키 완료와 전체 툴팁 한국어화를 구분해요. 실제 게임 화면은 미검증이에요.

## 재검증

`python scripts/verify_betteradvancedtooltips_translation.py`로 현재 JAR 해시, 영어 5키,
검수 기록, 한국어 키·순서·자료형·중복·보호 문자열과 output 일치, 관련 파일 해시를 검사해요.
검증 전후 실제 인스턴스의 파일 목록·크기·수정 시각을 비교해요.
