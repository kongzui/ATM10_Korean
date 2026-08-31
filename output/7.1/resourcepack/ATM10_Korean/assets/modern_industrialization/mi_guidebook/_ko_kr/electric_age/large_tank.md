---
navigation:
  title: "대형 탱크"
  icon: "modern_industrialization:large_tank"
  position: 101
  parent: modern_industrialization:electric_age.md
item_ids:
  - modern_industrialization:large_tank
  - modern_industrialization:large_tank_hatch
---

# 대형 탱크

<GameScene zoom="1" interactive={true} fullWidth={true}>
    <MultiblockShape controller="large_tank" />
    <MultiblockShape controller="large_tank" useBigShape={true} x="-8" z="-2" />
</GameScene>

대형 탱크는 대량의 액체를 저장하기에 적합한 멀티블록입니다. 대형 탱크는 멀티블록 구조 내의 블록 수마다 64B 의 액체를 저장 가능합니다.

<Recipe id="modern_industrialization:electric_age/machine/large_tank_asbl" />

대형 탱크는 필요한 용량에 따라 여러 크기로 만들 수 있습니다. 제어기의 버튼을 눌러 크기 설정 패널을 여세요.

제어기 또는 대형 탱크 해치를 통해 연결한 파이프만 탱크에 접근할 수 있습니다.

컨트롤러를 부수면 저장된 액체의 정보를 모두 잃어버리니 주의하세요.

대형 탱크 해치는 대형 탱크 블록의 연장 장치입니다. 우클릭하여 대형 탱크 메뉴를 열 수 있고, 연결한 파이프는 탱크 저장소에 직접 접근합니다.

<Recipe id="modern_industrialization:electric_age/machine/large_tank_hatch_asbl" />
