// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.

ItemEvents.modifyTooltips(allthemods => {

    //AllTheModium

    allthemods.add(['allthemodium:allthemodium_ore', 'allthemodium:allthemodium_slate_ore'],[
        Text.of('§7채굴하려면 네더라이트 등급 이상이 필요합니다'),
        Text.of('§6딥 다크 생물 군계에서 공기에 노출된 상태로 생성됩니다'),
        Text.of('§6채굴 차원의 심층암 지층에서도 발견됩니다')
    ])
    allthemods.add(['allthemodium:vibranium_ore', 'allthemodium:other_vibranium_ore'],[
        Text.of('§7채굴하려면 Allthemodium 등급 이상이 필요합니다'),
        Text.of('§b모든 네더 생물 군계에서 발견됩니다'),
        Text.of('§b디 아더에서도 발견됩니다')
    ])
    allthemods.add('allthemodium:unobtainium_ore',[
        Text.of('§7채굴하려면 Vibranium 등급 이상이 필요합니다'),
        Text.of('§d엔드 고지대에서 발견됩니다')
    ])

    allthemods.add('kubejs:silent_allthemodium_plate',[
        Text.of("§7§o이제 덜... 시끄럽네요")
    ])
    allthemods.add('kubejs:silent_vibranium_plate',[
        Text.of("§7§o이제 덜... 시끄럽네요")
    ])
    allthemods.add('kubejs:silent_unobtainium_plate',[
        Text.of("§7§o이제 덜... 시끄럽네요")
    ])

    allthemods.add('allthemodium:allthemodium_ingot',[
        Text.of("§7§o찾으시는 주괴가 아닙니다"),
        Text.of("§6[고요한 Allthemodium 판]을 찾아보세요")
    ])
    allthemods.add('allthemodium:vibranium_ingot',[
        Text.of("§7§o찾으시는 주괴가 아닙니다"),
        Text.of("§6[고요한 Vibranium 판]을 찾아보세요")
    ])
    allthemods.add('allthemodium:unobtainium_ingot',[
        Text.of("§7§o찾으시는 주괴가 아닙니다"),
        Text.of("§6[고요한 Unobtainium 판]을 찾아보세요")
    ])


    allthemods.add('allthemodium:allthemodium_upgrade_smithing_template',[
        Text.of('§6고대 도시의 수상한 점토에서 발견됩니다')
    ])
    allthemods.add('allthemodium:vibranium_upgrade_smithing_template',[
        Text.of('§b보루 잔해의 수상한 영혼 모래에서 발견됩니다')
    ])
    allthemods.add('allthemodium:unobtainium_upgrade_smithing_template',[
        Text.of('§d디 아더 던전의 도서관에 있는 시험 생성기에서 나옵니다')
    ])

    //Forbidden Arcanus
    allthemods.add('forbidden_arcanus:hephaestus_forge_tier_1',[
        Text.of("§c§lShift-Right-Click§r§c the §c§lSmithing Table§r§c with §lMundabitur Dust"),
        Text.of("§c█ = Gilded Chiseled Polished Darkstone with Smithing Table on top"),
        Text.of("§7█ = Polished Darkstone"),
        Text.of("§5█§7 = Gilded Chiseled Polished Darkstone"),
        Text.of("§6█§7 = Chiseled Arcane Polished Darkstone"),
        Text.of("§0███§7███§0███"),
        Text.of("§0█§7███§5█§7███§0█"),
        Text.of("§0█§7█§5█§7███§5█§7█§0█"),
        Text.of("§7████§6█§7████"),
        Text.of("§7█§5█§7█§6█§c█§6█§7█§5█§7█"),
        Text.of("§7████§6█§7████"),
        Text.of("§0█§7█§5█§7███§5█§7█§0█"),
        Text.of("§0█§7███§5█§7███§0█"),
        Text.of("§0███§7███§0███")

    ])
    allthemods.add('forbidden_arcanus:clibano_core',[
        Text.of("§c§lShift-Right-Click§r§c the §c§lClibano Core§r§c with §c§lMundabitur Dust"),
        Text.of("§5█§7 = Polished Darkstone"),
        Text.of("§7█ = Polished Darkstone Bricks"),
        Text.of("§6█§7 = Clibano Core"),
        Text.of("§7Right to Left -> Bottom to Top"),
        Text.of("§5█§7█§5█§0█§7███§0█§5█§7█§5█"),
        Text.of("§7███§0█§7█§0█§7█§0█§7███"),
        Text.of("§5█§7█§5█§0█§7█§6█§7█§0█§5█§7█§5█"),
    ])
    allthemods.add('forbidden_arcanus:growing_edelwood',[
        Text.of("§4Obtainable from the Wandering Trader"),
        Text.of("§4Or by using a Corrupt Soul on an Oak Sapling"),
    ])
    allthemods.add('forbidden_arcanus:magnetized_darkstone_pedestal',[
        Text.of("§7Use Ferrognetic Mixture on the Darkstone Pedestal"),
    ])
    allthemods.add('forbidden_arcanus:soul',[
        Text.of("§7Use a Soul Extractor on Soul Sand"),
        Text.of("§7Rarely spawns in world"),
    ])
    allthemods.add('forbidden_arcanus:enchanted_soul',[
        Text.of("§7Use a Splash Aureal Bottle on a normal soul")
    ])
    allthemods.add('forbidden_arcanus:corrupt_soul',[
        Text.of("§7Rarely spawns when killing mobs")
    ])
    allthemods.add('forbidden_arcanus:blood_test_tube',[
        Text.of("§7Hold a test tube in your off-hand and then kill mobs")
    ])
    allthemods.add('forbidden_arcanus:xpetrified_orb',[
        Text.of("§7Only obtainable via the Black Hole"),
        Text.of("§7To make a Black Hole throw Dark Matter together with Corrupti Dust on the ground"),
        Text.of("§7Feed it enough xp to make it spit out an Xpetrified Orb")
    ])
    allthemods.add('forbidden_arcanus:dragon_scale',[
        Text.of("§7Dropped by the Ender Dragon")
    ])
    allthemods.add('forbidden_arcanus:stella_arcanum',[
        Text.of("§7Very rarely spawns between Y -44 and Y 42"),
        Text.of("§cWill explode when you mine it!")
    ])
    allthemods.add(/forbidden_arcanus:runic_[sd]/,[
        Text.of("§7Spawns at the bottom of the world up to Y 2"),
    ])
    allthemods.add(['forbidden_arcanus:arcane_crystal_ore', 'forbidden_arcanus:deepslate_arcane_crystal_ore'],[
        Text.of("§7Very rarely spawns between Y -40 and Y 14"),
        Text.of("§7Most common at Y -13")
    ])
    allthemods.add('forbidden_arcanus:artisan_relic',[
        Text.of("§aFound in the Armorer, Toolsmith, or Weaponsmith villager buildings"),
    ])
    allthemods.add('forbidden_arcanus:crescent_moon',[
        Text.of("§cUnobtainable"),
    ])
    allthemods.add('forbidden_arcanus:crimson_stone',[
        Text.of("§aFound in Pillager Outposts"),
    ])
    allthemods.add('forbidden_arcanus:soul_crimson_stone',[
        Text.of("§cWill turn into a Crimson Stone after 1 use"),
    ])
    allthemods.add('forbidden_arcanus:elementarium',[
        Text.of("§aFound in Jungle Temples, Desert Pyramids, and Underwater Ruins"),
    ])
    allthemods.add('forbidden_arcanus:divine_pact',[
        Text.of("§aFound in the Village and Pyramid in The Other"),
    ])
    allthemods.add('forbidden_arcanus:maledictus_pact',[
        Text.of("§aFound in Treasure Bastions"),
    ])

    //Mystical Agriculture
    allthemods.add(/mysticalagriculture:.*watering_can/,[
        Text.of("§c가짜 플레이어로 사용할 수 없습니다"),
        Text.of("§c(Modular Routers, Clickers 같은 블록 포함)")
    ])

    allthemods.add('toolbelt:belt', [
        Text.of("§7Has it's own slot to be placed in"),
        Text.of("§7Check your Keybinds for \"Open Belt Slot Inventory\"")
    ])

	//Easy Villagers
    allthemods.add(['easy_villagers:trader', 'easy_villagers:auto_trader'], [
        Text.of("§aRight click with job site block to put it inside and allow trade restocking")
    ])

	//Hyperbox
    if (Platform.isLoaded("hyperbox")) {
        allthemods.add('hyperbox:hyperbox', [
            Text.of("§aThis mod will be removed on version 6.0+")
        ])
    }

    //Eternal Starlight
    if (Platform.isLoaded("eternal_starlight")) {
        allthemods.add('eternal_starlight:loot_bag[eternal_starlight:loot_table="eternal_starlight:bosses/lunar_monstrosity"]', [
            Text.of('이 전리품 가방은 \"달빛 괴수\"에게서 나옵니다.')
        ])
    }

    if (Platform.isLoaded('modular_machinery_reborn')) {
        allthemods.add('modular_machinery_reborn:controller[modular_machinery_reborn:machine="atm:runic_crucible"]', [
            Text.of('§cWARNING, this machine has be depreciated.'),
            Text.of('Use crafting table to convert to the new version.')
        ])
        allthemods.add('modular_machinery_reborn:controller[modular_machinery_reborn:machine="atm:runic_star_altar"]', [
            Text.of('§cWARNING, this machine has be depreciated.'),
            Text.of('Use crafting table to convert to the new version.')
        ])
        allthemods.add('modular_machinery_reborn:controller[modular_machinery_reborn:machine="atm:runic_enchanter"]', [
            Text.of('§cWARNING, this machine has be depreciated.'),
            Text.of('Use crafting table to convert to the new version.')
        ])
        allthemods.add('modular_machinery_reborn:controller[modular_machinery_reborn:machine="atm:auto_hepheastus_forge"]', [
            Text.of('§cWARNING, this machine has be depreciated.'),
            Text.of('Use crafting table to convert to the new version.')
        ])
    }
	// Apotheosis Gateway Warning
	allthemods.add([
	'gateways:gate_pearl[gateways:gateway="apotheosis:tiered/frontier"]',
	'gateways:gate_pearl[gateways:gateway="apotheosis:tiered/ascent"]',
	'gateways:gate_pearl[gateways:gateway="apotheosis:tiered/summit"]',
	'gateways:gate_pearl[gateways:gateway="apotheosis:tiered/pinnacle"]'],
	[
		Text.of("§cWARNING: Will implode at wave 3 outside of the following dimensions:"),
		Text.of("§cOverworld, The Nether, The End, The Twilight Forest")
	])
	// Botany Pot Sculk
	allthemods.add([
	"minecraft:sculk",
	"minecraft:sculk_sensor",
	"minecraft:sculk_catalyst",
	"minecraft:sculk_vein",
	"minecraft:sculk_shrieker",
	"deeperdarker:gloomy_sculk",
	"deeperdarker:gloomy_grass",
	"deeperdarker:glowing_flowers",
	"deeperdarker:sculk_vines",
	"deeperdarker:glowing_roots",
	"deeperdarker:bloom_berries",
	"deeperdarker:glowing_grass",
	"deeperdarker:sculk_tendrils"],
	[
		Text.of("§9식물 화분에서 수확하려면 섬세한 손길이 부여된 괭이가 필요합니다")
	])
})


// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.
