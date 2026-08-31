// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.

ItemEvents.modifyTooltips(allthemods => {

    // ##### Gear #####

    //Mekasuit
    allthemods.add(/mekanism:mekasuit_/, [
        Text.red('에너지 소모량 증가!'),
        Text.green('에너지 용량 증가')
    ])
    //Meka Tool
    allthemods.add('mekanism:meka_tool', [
        Text.red('에너지 소모량 증가!'),
        Text.green('에너지 용량 증가!'),
        Text.green('공격 속도와 피해 증가!')
    ])

    // ##### Generators #####

    //Solar Generator
    allthemods.add('mekanismgenerators:solar_generator', [
        Text.green('에너지 용량과 생산량 증가!')
    ])
    //Advanced Solar Generator
    allthemods.add('mekanismgenerators:advanced_solar_generator', [
        Text.green('에너지 용량과 생산량 증가!')
    ])
    //Wind Generator
    allthemods.add('mekanismgenerators:wind_generator', [
        Text.green('에너지 용량과 생산량 증가!')
    ])
    //Heat Generator
    allthemods.add('mekanismgenerators:heat_generator', [
        Text.green('에너지 용량과 생산량 증가!')
    ])
    //Gas Burning Generator
    allthemods.add('mekanismgenerators:gas_burning_generator', [
        Text.red('에너지 생산량 감소!'),
        Text.red('연료 소모량 증가!')
    ])
    //Fission Generator
    allthemods.add(/mekanismgenerators:fission_/, [
        Text.red('에너지 생산량 감소!'),
    ])
    //Fusion Generator
    allthemods.add(/mekanismgenerators:fusion_/, [
        Text.red('에너지 생산량 감소!'),
        Text.green('연료 소모량 감소!'),
    ])
    //Turbine
    allthemods.add(/mekanismgenerators:turbine_/, [
        Text.green('생산 속도 증가!'),
    ])
    //Boiler
    allthemods.add(/mekanism:boiler_/, [
        Text.green('생산 속도 증가!'),
    ])

    // ##### Machines #####

    //Upgrades
    allthemods.add(/mekanism:upgrade_/, [
        Text.green('기계 성능 향상!')
    ])
    //Waste Barrel
    allthemods.add('mekanism:radioactive_waste_barrel', [
        Text.green('붕괴 속도 증가!')
    ])
    //Thermal Evaporation Tower
    allthemods.add(/mekanism:thermal_evaporation_/, [
        Text.green('생산 속도 증가!')
    ])
    //Solar Neutron Activator
    allthemods.add('mekanism:solar_neutron_activator', [
        Text.green('생산 속도 증가!'),
        Text.green('핵폐기물 → 폴로늄 생산량 증가!')
    ])
    //Isotopic Centrifuge
    allthemods.add('mekanism:isotopic_centrifuge', [
        Text.green('핵폐기물 → 플루토늄 생산량 증가!')
    ])
    //Electric Pump
    allthemods.add('mekanism:electric_pump', [
        Text.green('생산 속도 증가!')
    ])
    //SPS
    allthemods.add(/mekanism:sps_/, [
        Text.green('에너지 소모량 감소!')
    ])
})

// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.