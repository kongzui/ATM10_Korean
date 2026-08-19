// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.

KubeJSTweaks.checkCompatibility(event => {
  event.checkModVersion("jei", "19.22.0.316", "이 버전은 도구 내구도 문제를 일으킵니다")
  event.checkModVersion("uranus", "[2.3.1-bugfix,2.3.1-bugfix2]", "This version is causing TPS and memory leak issues")
  event.checkModVersion("octolib", "0.6.0.2", "This version is causing high CPU usage issues")
  event.checkModVersion("utilitarian", "1.21.1-0.15.0", "This version is crashing when bonemealing small flowers")
  event.checkModVersion("amendments", "1.21-2.0.4", "This version is crashing when opening lecterns")

  event.checkModLoaded("accessories_compat_layer", "이 모드는 다른 모드와 Curios 호환성 문제를 일으킬 수 있습니다")
  event.checkModLoaded("letmedespawn", "This mod can cause same items to not stack due to NBT issues")

})

// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.
