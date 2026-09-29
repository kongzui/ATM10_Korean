# 보류 용어와 재검수 불확실 항목 확정 · 2026-09-29

용어집 보류 용어 5개와 1~4순위 재검수 보고의 불확실 항목을 확인해 정했어요. 결정 표는
[용어집](../../../glossary/README.md)의 `보류 해소 · 2026-09-29`에 있어요. 이 반영분은 5순위와 함께
8.1-stable.14에 배포해요.

## 확인한 근거

| 항목 | 근거 | 결정 |
|---|---|---|
| Hunger | 바닐라 난이도 설명·생존 모드 설명의 `배고픔 바`, 효과 `effect.minecraft.hunger`=`허기` | 음식 수치 `배고픔`, 효과 `허기` |
| Raider | 바닐라 `event.minecraft.raid.raiders_remaining`=`남은 습격자 수` | `습격자` |
| Compression Upgrade | Sophisticated Storage JAR 내장 한국어 `자동 압축 기능` | `자동 압축 업그레이드` 유지 |
| Void Upgrade | Sophisticated 내장 `제거 기능`, Functional Storage 내장 `공허 업그레이드` | 기능이 분명한 `제거`로 통일 |
| Admin | Sophisticated 내장 `무한 기능(Admin)` | 역할은 `관리자`, 권한 등급은 `OP` |
| Trail Ruins | 나무위키·한국어 Minecraft 위키 | `흔적 폐허` 유지 |
| Vibrant Alloy | 한국 강좌 글은 영문 그대로, 정착 번역 없음 | 같은 계열 명사형 `생동 합금`(Ender IO 계열 때 교체) |
| Towns and Towers mimic | 모드 설명: 사막 피라미드를 흉내 낸 함정 구조물 | `가짜 사막 피라미드` |
| Structory quarter outpost 등 | 공개 자료에 설명 없음 | 새 이름을 짓지 않고 현재 이름 유지 |

## 반영한 키

| 계열 | 네임스페이스 | 키 수 | 내용 |
|---|---|---:|---|
| 2순위 1부 | ftbultimine, ftbfiltersystem | 4 | 음식 수치 `배고픔` |
| 2순위 2부 | explorerscompass | 36 | 구조물 크기 표기 통일 29, Nether Stronghold·mimic·bog trial·Dungeons Arise 고유명 7 |
| 4순위 | appleskin | 13 | 음식 수치 `배고픔`, `배고픔 소모도` |
| 4순위 | enchdesc, tombstone | 7 | `배고픔`, `Tombstone 영혼 귀속`, `안식의 종복`, `습격자` |
| 4순위 | tempad, controlling | 2 | `작업대 터미널`(tempad·tempad_static 같은 키 통일), `확실합니까?` |

## 검증

- `quality_rereview_lang.py`로 common_ui·common_ui_2·info_ui 수정본을 반영했고 오류가 없어요.
- `verify_quality_rereview.py` 누적 검증을 통과했어요.
- 용어집에 3순위 때 잘못 들어간 보류 줄 3개가 확정 표 안에 있던 것을 함께 정리했어요.
