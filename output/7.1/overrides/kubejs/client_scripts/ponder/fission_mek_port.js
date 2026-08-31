// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.

Ponder.registry((allthemods) => {
    allthemods.create('mekanismgenerators:fission_reactor_port')
	.scene('fission_mek_port','Mekanism 핵분열로: 포트', 'kubejs:fission_mek',

	(scene, util) => {


			scene.showStructure();
            scene.idle(20);

			scene.world.setBlock([0, 1, 1], 'mekanismgenerators:fission_reactor_port', true);
			scene.world.setBlock([0, 1, 3], 'mekanismgenerators:fission_reactor_port', true);
			scene.world.modifyBlock([0, 1, 1], (curState) => curState.with("mode", "output_waste"), false);
			scene.world.modifyBlock([0, 1, 3], (curState) => curState.with("mode", "output_coolant"), false);

			scene.text(60, '반응기에는 포트가 최소 4개 필요합니다.', [0, 1.5, 3.5]).placeNearTarget();
			scene.addKeyframe();
			scene.idle(80)

			scene.addKeyframe()

			scene.text(60, '설정 장치로 포트의 모드를 변경할 수 있습니다.', [0, 1.5, 3.5]).placeNearTarget();
			scene.showControls(60, [0.5, 2, 3.5], 'down').rightClick().withItem('mekanism:configurator').whileSneaking();
			scene.idle(80);

			scene.addKeyframe();

			scene.text(160, '필요한 포트:', [-1, 4, 4]).placeNearTarget();

			scene.text(40, '냉각재 입력', [3.5, 1.5, 0]).placeNearTarget();
			scene.idle(40);
			scene.text(40, '연료 입력', [1.5, 1.5, 0]).placeNearTarget();
			scene.idle(40);
			scene.text(40, '핵폐기물 출력', [0, 1.5, 1.5]).placeNearTarget();
			scene.idle(40);
			scene.text(40, '가열된 냉각재 출력', [0, 1.5, 3.5]).placeNearTarget();
			scene.idle(40);
			scene.addKeyframe();
			scene.idle(10);


    });
});

// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.
