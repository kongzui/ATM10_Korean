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
        Text.of("§c§lShift+우클릭§r§c으로 §c§l대장장이 작업대§r§c에 §l문다비투르 가루§r§c를 사용하세요"),
        Text.of("§c█ = 금박 조각된 광택 다크스톤 위에 대장장이 작업대"),
        Text.of("§7█ = 광택 다크스톤"),
        Text.of("§5█§7 = 금박 조각된 광택 다크스톤"),
        Text.of("§6█§7 = 조각된 비전 광택 다크스톤"),
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
        Text.of("§c§lShift+우클릭§r§c으로 §c§l클리바노 코어§r§c에 §c§l문다비투르 가루§r§c를 사용하세요"),
        Text.of("§5█§7 = 광택 다크스톤"),
        Text.of("§7█ = 광택 다크스톤 벽돌"),
        Text.of("§6█§7 = 클리바노 코어"),
        Text.of("§7오른쪽에서 왼쪽 -> 아래에서 위"),
        Text.of("§5█§7█§5█§0█§7███§0█§5█§7█§5█"),
        Text.of("§7███§0█§7█§0█§7█§0█§7███"),
        Text.of("§5█§7█§5█§0█§7█§6█§7█§0█§5█§7█§5█"),
    ])
    allthemods.add('forbidden_arcanus:growing_edelwood',[
        Text.of("§4떠돌이 상인에게서 얻을 수 있습니다"),
        Text.of("§4참나무 묘목에 타락한 영혼을 사용해도 됩니다"),
    ])
    allthemods.add('forbidden_arcanus:magnetized_darkstone_pedestal',[
        Text.of("§7다크스톤 받침대에 페로마그네틱 혼합물을 사용하세요"),
    ])
    allthemods.add('forbidden_arcanus:soul',[
        Text.of("§7영혼 모래에 영혼 추출기를 사용하세요"),
        Text.of("§7월드에 드물게 나타납니다"),
    ])
    allthemods.add('forbidden_arcanus:enchanted_soul',[
        Text.of("§7일반 영혼에 투척용 아우레알 병을 사용하세요")
    ])
    allthemods.add('forbidden_arcanus:corrupt_soul',[
        Text.of("§7몹을 처치할 때 드물게 나타납니다")
    ])
    allthemods.add('forbidden_arcanus:blood_test_tube',[
        Text.of("§7시험관을 보조 손에 들고 몹을 처치하세요")
    ])
    allthemods.add('forbidden_arcanus:xpetrified_orb',[
        Text.of("§7블랙홀에서만 얻을 수 있습니다"),
        Text.of("§7어둠의 물질과 코럽티 가루를 바닥에 함께 던지면 블랙홀이 생깁니다"),
        Text.of("§7블랙홀에 경험치를 충분히 주면 엑스페트리파이드 구슬이 나옵니다")
    ])
    allthemods.add('forbidden_arcanus:dragon_scale',[
        Text.of("§7엔더 드래곤이 떨어뜨립니다")
    ])
    allthemods.add('forbidden_arcanus:stella_arcanum',[
        Text.of("§7Y -44에서 Y 42 사이에 매우 드물게 생성됩니다"),
        Text.of("§c채굴하면 폭발합니다!")
    ])
    allthemods.add(/forbidden_arcanus:runic_[sd]/,[
        Text.of("§7월드 바닥부터 Y 2 사이에 생성됩니다"),
    ])
    allthemods.add(['forbidden_arcanus:arcane_crystal_ore', 'forbidden_arcanus:deepslate_arcane_crystal_ore'],[
        Text.of("§7Y -40에서 Y 14 사이에 매우 드물게 생성됩니다"),
        Text.of("§7Y -13에서 가장 흔합니다")
    ])
    allthemods.add('forbidden_arcanus:artisan_relic',[
        Text.of("§a갑옷 제조인, 도구 대장장이 또는 무기 대장장이 주민 건물에서 찾을 수 있습니다"),
    ])
    allthemods.add('forbidden_arcanus:crescent_moon',[
        Text.of("§c획득할 수 없습니다"),
    ])
    allthemods.add('forbidden_arcanus:crimson_stone',[
        Text.of("§a약탈자 전초기지에서 찾을 수 있습니다"),
    ])
    allthemods.add('forbidden_arcanus:soul_crimson_stone',[
        Text.of("§c한 번 사용하면 크림슨 스톤으로 바뀝니다"),
    ])
    allthemods.add('forbidden_arcanus:elementarium',[
        Text.of("§a정글 사원, 사막 피라미드, 해저 폐허에서 찾을 수 있습니다"),
    ])
    allthemods.add('forbidden_arcanus:divine_pact',[
        Text.of("§a디 아더의 마을과 피라미드에서 찾을 수 있습니다"),
    ])
    allthemods.add('forbidden_arcanus:maledictus_pact',[
        Text.of("§a보물 보루 잔해에서 찾을 수 있습니다"),
    ])

    //Mystical Agriculture
    allthemods.add(/mysticalagriculture:.*watering_can/,[
        Text.of("§c가짜 플레이어로 사용할 수 없습니다"),
        Text.of("§c(Modular Routers, Clickers 같은 블록 포함)")
    ])

    allthemods.add('toolbelt:belt', [
        Text.of("§7전용 장착 슬롯이 있습니다"),
        Text.of("§7키 설정에서 \"허리띠 슬롯 인벤토리 열기\"를 확인하세요")
    ])

	//Easy Villagers
    allthemods.add(['easy_villagers:trader', 'easy_villagers:auto_trader'], [
        Text.of("§a직업 블록을 들고 우클릭하면 안에 넣어 거래를 다시 채울 수 있습니다")
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
