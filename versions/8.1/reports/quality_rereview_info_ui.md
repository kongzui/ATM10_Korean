# 품질 재검수 4순위 · 인벤토리·정보·가이드 UI

기준 커밋 `14a51ca`의 8.1 산출물을 현재 JAR 영어 원문과 키 단위로 다시 대조했어요. 8.1-stable.13에
반영했어요. 분업 방식(Opus 오케스트레이터·Sonnet 워커 2개 병렬)으로 진행했어요.

## 범위와 결과

| 네임스페이스 | 검토 키 | 수정 | 유지 |
|---|---:|---:|---:|
| tombstone | 1,253 | 85 | 1,168 |
| lootr | 221 | 25 | 196 |
| enchdesc | 182 | 10 | 172 |
| tempad | 164 | 46 | 118 |
| jearchaeology | 156 | 0 | 156 |
| tempad_static | 84 | 6 | 78 |
| modonomicon | 81 | 3 | 78 |
| patchouli | 79 | 3 | 76 |
| guideme | 42 | 1 | 41 |
| moreoverlays | 40 | 9 | 31 |
| craftingtweaks | 40 | 2 | 38 |
| trashslot | 24 | 7 | 17 |
| appleskin | 22 | 9 | 13 |
| mousetweaks | 18 | 3 | 15 |
| controlling | 12 | 0 | 12 |
| akashictome | 11 | 1 | 10 |
| invtweaks, betteradvancedtooltips, polymorph, betteradvancements | 14 | 0 | 14 |
| 합계 | 2,443 | 210 | 2,233 |

작업 원본은 각 네임스페이스의 `ko_kr.json`과 보정 파일 `recheck_overrides.json`(enchdesc, lootr,
polymorph, controlling, guideme)이에요.

## 주요 수정 유형

- 용어집: `재생성`→`리스폰`, `개체`→`엔티티`, `재사용 대기시간`→`쿨타임`, `생물군계`→`생물 군계`,
  `핫바`→`단축 바`, 설정 설명의 `활성화하면`→`켜면`, `옵션`→`설정`, `마법 부여된`→`마법이 부여된`,
  몹 스폰 밝기 오버레이, 우클릭·좌클릭.
- 바닐라 이름: 팬텀(`망령` 오역), 차광 유리, 네더 석영, 네더라이트 파편, 철 원석, 레드스톤 조명,
  속도 감소, 입자, 장식된 도자기.
- 이름 일치: Tombstone `무덤 가루`·`사역마의 그릇`·`거인의 힘 물약`·`침묵의 결속`·`주술사`(Witch
  Doctor 오역), Tempad 공식 표기와 `텔레포트` 앱·업그레이드 이름, TrashSlot의 `삭제 슬롯`.
- 오역: Tempad의 `so long as` 조건, Lootr `Block Entity Age`, Patchouli 색인 안내, 원문에 없던 예시·
  횟수 삭제, 순간이동 허용 메시지의 주어.
- 번역투·말투: `당신`, `그것`, `이러한`, `~에 의한`, `~하십시오`, `성공적으로 ~되었습니다`, 해요체 혼용,
  명령 결과의 완결 문장.

## 분업 운영 기록

| 항목 | 결과 |
|---|---|
| 워커 | Sonnet 2개(A: Tombstone 1,253키, B: 나머지 19개 모드 1,190키) |
| 워커 사용량 | A 약 24.7만 토큰·5.4분, B 약 26.4만 토큰·9.7분 |
| 워커 수정 | A 82키, B 128키, 모두 사유 제출, 형식 오류 0 |
| 오케스트레이터 검토 | 수정 210키 전수, 바뀐 이름의 퀘스트·다른 모드 사용처 확인, 유지 키 패턴 검사와 무작위 60키 |
| 되돌림·보정 | 0키 되돌림, 워커 수정 4키 보정(목록 문형, `자신` 주어, `설정을 설정` 중복 2) |
| 워커가 놓친 항목 | 5키(`성공적으로` 3, `자신을 동족으로` 1, 어색한 안내 1)를 오케스트레이터가 추가 수정 |

지시문에 넣은 번역투 목록(`성공적으로`)을 워커가 일부 놓쳤어요. 오케스트레이터 패턴 검사는 계속
필요해요.

## 검증과 적용

- `quality_rereview_lang.py info_ui`, `verify_quality_rereview.py`, 안정판 검증 통과, ZIP 두 개 생성.
- `verify_quality_rereview.py`는 텍스트 컴포넌트 목록처럼 문자열이 아닌 기존 값(`tempad_static`의
  `location.tempad.saved`)을 기준과 같을 때만 허용하도록 고쳤어요.
- 게임 종료 상태에서 언어 파일과 `pack.mcmeta`만 선택 적용했어요([적용 보고](quality_rereview_info_ui_apply.json)).
  실제 게임 화면은 미확인이에요.

## 남은 확인 항목

- Tombstone: `무덤 영혼 귀속`(Soulbound) 이름이 무덤 영혼과 헷갈릴 수 있음, `휴식의 종`의 `종` 뜻,
  Raider 바닐라 표기(습격자·약탈자), stealth speed(`잠행 속도`).
- Tempad: `block.tempad.workstation_child`가 tempad와 tempad_static에서 원문·번역이 다름,
  `spatial anchor`가 AE2 공간 정박기인지 불명.
- Controlling `Confirm?`이 긴 문장으로 풀려 버튼 폭을 넘을 수 있음(화면 확인 필요).
- 용어집 보류: Hunger(허기/배고픔), Trail Ruins.
