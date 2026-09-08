# Mouse Tweaks 시작 화면 충돌 수정

현재 배포: `8.1-compat.3` / `7.1-final.2`. 실제 인스턴스 적용은 사용자가 직접 해요.

2026-09-08 18:44:45 충돌 보고서에서 `mousetweaks_config_labels.js#35`의
`Cannot find function getClass`가 직접 원인으로 확인됐어요. 같은 실행의 KubeJS 로그는
22/22 시작 스크립트, 오류 0개였어요. 이전 const 문제를 통과한 뒤 화면 초기화 이벤트에서
새 오류가 난 것이며, 리소스팩 ZIP이나 추가 모드가 직접 원인이라는 근거는 없어요.

화면의 `getClass()` 호출을 제거하고 `Java.loadClass("yalter.mousetweaks.ConfigScreen")`과
`instanceof`로 Mouse Tweaks 설정 화면을 판별해요. 실제 Mouse Tweaks JAR에서 해당 클래스가
public인 것을 확인했어요. 다른 화면은 바로 반환하고 기존 번역·콜백·이벤트 우선순위는 유지해요.

이전 검사에서 JavaScript 대역 화면에 getClass를 만들어 실제 Java 래퍼와 다르게 동작했던
검증 결함도 수정했어요. 이제 Java로 만든 화면·위젯·컴포넌트·이벤트를 실제 Rhino로 감싸
검사해요. `3a6bf12`의 이전 배포 스크립트는 일반 화면 초기화에서 같은 getClass 오류로
실패해야 하고, 수정본은 초기화·반복 렌더·다른 화면 필터·모드 부재·서버 조건을 통과해야 해요.
7.1 Rhino build.81과 8.1 Rhino build.91에서 모두 이 재현·회귀 검사를 통과했어요.

게임 API 전체나 실제 Minecraft 화면을 실행한 검사는 아니에요. 실제 게임 재확인은 남아 있어요.
두 버전의 `startup_hotfix_validation.json`, 8.1의 `compat_validation.json`과 버전별 배포
패키지 명세에 전체 문법·번역 유지·원문 호환·ZIP CRC·내용 해시 검증 결과를 기록해요.

기존 모드 언어 값 7.1의 145,570개와 8.1의 147,388개를 유지했고 새 번역은 없어요.
FTB Quests와 다른 KubeJS 스크립트는 이번 변경에서 수정하지 않았어요.
실제 게임 폴더·JAR·월드·설정은 수정하지 않았어요. 이전 오류 수정도 모두 포함하는 전체 ZIP을
버전마다 두 개씩 제공해요. 이전 팩을 비활성화하고 새 팩과 override로 교체한 뒤 완전히 재시작해요.
