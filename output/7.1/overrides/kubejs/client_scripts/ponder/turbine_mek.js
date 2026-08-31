// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.

Ponder.registry((allthemods) => {
    allthemods.create([
	'mekanismgenerators:turbine_casing',
	'mekanismgenerators:turbine_valve',
	'mekanismgenerators:turbine_vent',
	'mekanismgenerators:turbine_rotor',
	'mekanismgenerators:turbine_blade',
	'mekanismgenerators:rotational_complex',
	'mekanismgenerators:saturating_condenser',
	'mekanism:pressure_disperser',
	'mekanismgenerators:electromagnetic_coil',
	])
	.scene('turbine_mek','Mekanism: 산업용 터빈', 'kubejs:turbine_mek',

	(scene, util) => {


			scene.showStructure();
            scene.idle(5);

			scene.text(60, '산업용 터빈은 가열된 냉각재로 에너지를 생산합니다.', [0, 4.5, 4.5]).placeNearTarget().attachKeyFrame();
			scene.idle(65);

			scene.text(60, '모서리는 터빈 케이싱으로 만드세요.', [0, 4.5, 4.5]).placeNearTarget().attachKeyFrame();
			scene.idle(65);

			scene.text(60, '면에는 터빈 케이싱, 구조용 유리, 터빈 밸브, 증기 배출구를 사용할 수 있습니다.', [0, 2.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(65);

			scene.text(60, '터빈 밸브로 증기를 입력하거나 에너지를 출력합니다.', [0, 1.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(65);

			//hide top
			scene.world.hideSection([0, 4, 0, 4, 6, 4], Facing.up);
			scene.idle(5);

			//hide walls
			scene.world.hideSection([0, 4, 0, 4, 6, 4], Facing.up);
			scene.world.hideSection([0, 1, 0, 3, 6, 0], Facing.up);
			scene.world.hideSection([0, 1, 0, 0, 6, 3], Facing.up);
			scene.idle(10);

			//Turbine Rotor

			scene.text(80, '터빈 로터는 중앙에 배치하세요. 로터 하나마다 터빈 블레이드 2개를 장착합니다.', [2, 3.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(85);

			//show next layer
			scene.world.showSection([2, 4, 2], Facing.up);
			scene.idle(10);

			scene.text(80, '터빈 로터 위에 회전 기구를 배치하세요.', [2, 4.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(85);

			scene.world.showSection([1, 4, 1, 3, 4, 1], Facing.up);
			scene.world.showSection([3, 4, 2], Facing.up);
			scene.world.showSection([1, 4, 2], Facing.up);
			scene.world.showSection([1, 4, 3, 3, 4, 3], Facing.up);
			scene.idle(10);

			scene.text(80, '회전 기구 주변 층을 압력 분산기로 채우세요.', [1, 4.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(85);

			//Show Layer Vents

			scene.world.showSection([0, 4, 0, 4, 4, 0], Facing.up);
			scene.world.showSection([0, 4, 4, 4, 4, 4], Facing.up);
			scene.world.showSection([0, 4, 1, 0, 4, 3], Facing.up);
			scene.world.showSection([4, 4, 0, 4, 4, 4], Facing.up);

			scene.world.showSection([0, 1, 0, 3, 3, 0], Facing.up);
			scene.world.showSection([0, 1, 1, 0, 3, 3], Facing.up);

			scene.text(120, '이 층부터 바깥 면에 증기 배출구를 사용할 수 있습니다. 증기 배출구는 터빈에서 물도 출력합니다.', [0, 4.5, 3.5]).placeNearTarget().attachKeyFrame();
			scene.idle(125);

			//Show Electromagnetic Coil

			scene.world.showSection([2, 5, 2], Facing.up);
			scene.idle(5);

			scene.text(60, '회전 기구 위에 전자기 코일을 배치하세요.', [2, 5.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(65);

			scene.world.setBlock([2, 5, 1], 'mekanismgenerators:electromagnetic_coil', true);
			scene.world.setBlock([1, 5, 2], 'mekanismgenerators:electromagnetic_coil', true);
			scene.world.setBlock([2, 5, 3], 'mekanismgenerators:electromagnetic_coil', true);
			scene.world.setBlock([3, 5, 2], 'mekanismgenerators:electromagnetic_coil', true);
			scene.world.showSection([2, 5, 1], Facing.up);
			scene.world.showSection([1, 5, 2], Facing.up);
			scene.world.showSection([2, 5, 3], Facing.up);
			scene.world.showSection([3, 5, 2], Facing.up);
			scene.idle(10);

			scene.text(100, '전자기 코일은 최대 5개까지 배치할 수 있으며, 서로 연결되거나 회전 기구에 닿아야 합니다.', [2, 5.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(105);

			//Saturating Condensers

			scene.world.showSection([3, 5, 3], Facing.up);
			scene.world.showSection([1, 5, 1], Facing.up);
			scene.world.showSection([1, 5, 3], Facing.up);
			scene.world.showSection([3, 5, 1], Facing.up);

			scene.text(120, '포화 응축기는 증기를 다시 물로 바꿉니다. 필수 부품은 아니지만 코일 층이나 그 위에 배치해야 합니다.', [1, 5.5, 1.5]).placeNearTarget().attachKeyFrame();
			scene.idle(130);

			//Show other layers

			scene.world.showSection([0, 5, 0, 4, 5, 0], Facing.up);
			scene.world.showSection([0, 5, 4, 4, 5, 4], Facing.up);
			scene.world.showSection([0, 5, 1, 0, 5, 3], Facing.up);
			scene.world.showSection([4, 5, 0, 4, 5, 3], Facing.up);
			scene.idle(5);

			scene.world.showSection([0, 6, 0, 4, 6, 4], Facing.up);
			scene.idle(20);

			scene.world.hideSection([1, 6, 1, 3, 6, 3], Facing.up);
			scene.idle(15);
			scene.world.setBlock([1, 6, 1], 'mekanismgenerators:turbine_vent', false);
			scene.world.setBlock([2, 6, 1], 'mekanismgenerators:turbine_vent', false);
			scene.world.setBlock([3, 6, 1], 'mekanismgenerators:turbine_vent', false);
			scene.world.setBlock([1, 6, 2], 'mekanismgenerators:turbine_vent', false);
			scene.world.setBlock([2, 6, 2], 'mekanismgenerators:turbine_vent', false);
			scene.world.setBlock([3, 6, 2], 'mekanismgenerators:turbine_vent', false);
			scene.world.setBlock([1, 6, 3], 'mekanismgenerators:turbine_vent', false);
			scene.world.setBlock([2, 6, 3], 'mekanismgenerators:turbine_vent', false);
			scene.world.setBlock([3, 6, 3], 'mekanismgenerators:turbine_vent', false);
			scene.idle(10);

			scene.world.showSection([1, 6, 1, 3, 6, 3], Facing.down);
			scene.idle(10);

			scene.text(80, '필요하면 윗면을 증기 배출구로 채울 수 있습니다.', [2.5, 6.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(85);


    });
});

// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.
