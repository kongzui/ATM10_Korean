---
navigation:
  title: 팁과 요령
  position: 20
---

# 팁과 요령

알아 두면 좋은 소소한 권장 사항 모음입니다.

* OptiFine을 제거하세요.
* 확대·축소 및 주석 표시·숨기기 버튼이 있는 가이드북 장면은 회전하고 확대하거나 축소할 수 있습니다.
* 네트워크를 나무처럼 뻗는 구조로 만들고 순환 경로를 피하세요.
* 완전한 블록 형태의 [장치](ae2-mechanics/devices.md)는 8개 이하로 묶으세요. 단,
  [채널](ae2-mechanics/channels.md)이 네트워크를 따라 어떻게 전달되는지 완전히 이해했다면 예외입니다.
* 모든 [패턴](items-blocks-machines/patterns.md)에 사용할 목재 하나를 정해 계속 사용하세요. 패턴에서
  대체 재료를 허용해도 가끔은 잘 작동하지만, 어디서나 같은 목재를 사용하면 번거로움이 크게 줄어듭니다.
* [패턴](items-blocks-machines/patterns.md)을 <ItemLink id="pattern_access_terminal" />에서 세로로 배치하거나
  여러 [패턴 공급기](items-blocks-machines/pattern_provider.md)에 나누어 넣어 조합법을 병렬로 처리하세요.
* 네트워크가 순간적인 전력 사용량 증가를 견딜 수 있도록 [에너지 셀](items-blocks-machines/energy_cells.md)을 추가하세요.
* <ItemLink id="condenser" />에는 물을 사용할 수 있습니다.
* 네트워크를 깔끔하게 유지하는 가장 좋은 방법은 검이나 방어구 같은 무작위 몹 전리품을 넣지 않는 것입니다.
  마법 부여와 내구도가 서로 다른 조합은 각각 별도의 [종류](ae2-mechanics/bytes-and-types.md)로 계산됩니다.
* [처리 패턴](items-blocks-machines/patterns.md)의 결과물을 돌려보낼 때는 "아이템이 시스템에 들어오는"
  사건이 발생해야 합니다. <ItemLink id="import_bus" />, <ItemLink id="interface" /> 또는
  <ItemLink id="pattern_provider" />의 반환 슬롯을 사용해야 하며, <ItemLink id="storage_bus" />가 붙은
  상자로 결과물을 파이프로 보내기만 해서는 안 됩니다.
* 확대·축소 및 주석 표시·숨기기 버튼이 있는 가이드북 장면은 회전하고 확대하거나 축소할 수 있다는 점을 잊지 마세요.
* <ItemLink id="pattern_provider" />는 완전한 조합법 묶음만 한쪽 면을 통해 내보냅니다. 기계에 불완전한
  재료 묶음이 들어가는 일을 막는 데 유용하지만, 때로는 재료를 여러 곳으로 보내야 합니다. 이럴 때는
  <ItemLink id="interface" />를 ["파이프" 서브네트워크](example-setups/pipe-subnet.md)로 사용하거나,
  서로 다른 아이템 스택, 유체, 화학 물질 등을 동시에 보관하는 기능을 이용해 중간 상자나 탱크처럼
  사용할 수 있습니다.
* 확대·축소 및 주석 표시·숨기기 버튼이 있는 가이드북 장면은 확대·축소하고 회전할 수 있습니다.
