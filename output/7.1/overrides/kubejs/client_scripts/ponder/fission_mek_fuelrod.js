// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.

Ponder.registry((allthemods) => {
    allthemods.create([
		'mekanismgenerators:fission_fuel_assembly',
		'mekanismgenerators:control_rod_assembly'
		])
	.scene('fission_mek_fuelrod','Mekanism 핵분열로: 연료 집합체', 'kubejs:fission_mek',

	(scene, util) => {


			scene.world.showSection([0, 0, 0, 4, 4, 4], Facing.down);
			scene.idle(20);
			scene.world.hideSection([0, 1, 0, 3, 4, 3], Facing.up);
            scene.idle(20);

			scene.text(80, '내부에 핵분열 연료 집합체를 배치해 연료봉을 만드세요.', [2.5, 2.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.world.setBlock([2, 1, 2], 'mekanismgenerators:fission_fuel_assembly', true);
            scene.world.showSection([2, 1, 2], Facing.down)
            scene.idle(10);
			scene.world.setBlock([2, 2, 2], 'mekanismgenerators:fission_fuel_assembly', true);
            scene.world.showSection([2, 2, 2], Facing.down)
            scene.idle(80);

			scene.text(120, '핵분열 연료 집합체를 여러 개 쌓고 맨 위에 제어봉 집합체를 놓으면 연료봉이 됩니다.', [1.5, 2.5, 2.5]).placeNearTarget();
			scene.idle(40);
			scene.addKeyframe();
			scene.world.setBlock([2, 3, 2], 'mekanismgenerators:control_rod_assembly', true);
			scene.world.showSection([2, 3, 2], Facing.down)
			scene.idle(80);

			scene.text(80, '각 연료봉 위에 제어봉 집합체를 배치하세요.', [1.5, 3.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(90);

			scene.text(80, '제어봉 집합체는 천장에서 한 블록 아래에 배치하세요.', [1.5, 3.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(90);

			scene.text(60, '연료봉끼리는 맞닿을 수 없습니다.', [1.5, 1.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.world.setBlock([1, 1, 2], 'mekanismgenerators:fission_fuel_assembly', true);
			scene.world.setBlock([3, 1, 2], 'mekanismgenerators:fission_fuel_assembly', true);
            scene.world.showSection([1, 1, 2], Facing.down)
			scene.world.showSection([3, 1, 2], Facing.down)
			scene.idle(60)
			scene.world.setBlock([1, 1, 2], 'air', true);
			scene.world.setBlock([3, 1, 2], 'air', true);
			scene.idle(40);

			scene.world.hideSection([1, 1, 1, 3, 3, 3], Facing.up);
			scene.idle(40);
			scene.world.setBlock([1, 1, 1], 'mekanismgenerators:fission_fuel_assembly', true);
			scene.world.setBlock([1, 2, 1], 'mekanismgenerators:fission_fuel_assembly', true);
			scene.world.setBlock([1, 3, 1], 'mekanismgenerators:control_rod_assembly', true);
			scene.world.setBlock([1, 1, 3], 'mekanismgenerators:fission_fuel_assembly', true);
			scene.world.setBlock([1, 2, 3], 'mekanismgenerators:fission_fuel_assembly', true);
			scene.world.setBlock([1, 3, 3], 'mekanismgenerators:control_rod_assembly', true);
			scene.world.setBlock([3, 1, 1], 'mekanismgenerators:fission_fuel_assembly', true);
			scene.world.setBlock([3, 2, 1], 'mekanismgenerators:fission_fuel_assembly', true);
			scene.world.setBlock([3, 3, 1], 'mekanismgenerators:control_rod_assembly', true);
			scene.world.setBlock([3, 1, 3], 'mekanismgenerators:fission_fuel_assembly', true);
			scene.world.setBlock([3, 2, 3], 'mekanismgenerators:fission_fuel_assembly', true);
			scene.world.setBlock([3, 3, 3], 'mekanismgenerators:control_rod_assembly', true);
			scene.world.showSection([1, 1, 1, 3, 3, 3], Facing.down);

			scene.text(80, '연료봉이 여러 개라면 바둑판 모양으로 배치하는 것이 좋습니다.', [1.5, 1.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(100);

			scene.world.showSection([0, 1, 0, 3, 4, 0], Facing.down)
			scene.idle(5);
			scene.world.showSection([0, 1, 1, 0, 4, 3], Facing.down)
			scene.idle(5);
			scene.world.showSection([1, 4, 1, 3, 4, 3], Facing.down);
			scene.idle(20);


    });
});

// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.
