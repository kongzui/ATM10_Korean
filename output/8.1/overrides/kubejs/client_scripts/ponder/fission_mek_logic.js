// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.

Ponder.registry((allthemods) => {
    allthemods.create('mekanismgenerators:fission_reactor_logic_adapter')
	.scene('fission_mek_logic','Mekanism 핵분열로: 로직 어댑터', 'kubejs:fission_logic_example',

	(scene, util) => {


			scene.world.showSection([0, 0, 2, 4, 4, 6], Facing.down);
			scene.world.setBlock([2, 3, 2], 'mekanismgenerators:reactor_glass', false);
            scene.idle(20);

			scene.text(60, '로직 어댑터를 사용하면 레드스톤으로 반응기를 제어할 수 있습니다.', [2.5, 1.5, 2]).placeNearTarget().attachKeyFrame();
			scene.idle(80)


			scene.text(60, '우클릭해 설정 화면을 여세요.', [2.5, 1.5, 2]).placeNearTarget().attachKeyFrame();
			scene.showControls(60, [2.5, 2.5, 2], 'down').rightClick();
			scene.idle(70);


			scene.text(80, '두 개를 사용하면 특정 조건에서 반응기를 정지하는 안전장치를 구성할 수 있습니다.', [2.5, 3.5, 2]).placeNearTarget().attachKeyFrame();
			scene.world.setBlock([2, 3, 2], 'mekanismgenerators:fission_reactor_logic_adapter', true);
            scene.idle(90);

			scene.text(60, '이 어댑터는 가동으로 설정하세요.', [2.5, 3.5, 2]).placeNearTarget().attachKeyFrame();
			scene.idle(60);
			scene.text(60, '이 어댑터는 심각한 피해로 설정하세요.', [2.5, 1.5, 2]).placeNearTarget().attachKeyFrame();
			scene.idle(70);

			scene.world.showSection([2, 0, 0], Facing.down);
			scene.idle(5);
			scene.world.showSection([2, 0, 1], Facing.down);
			scene.idle(5);
			scene.world.showSection([2, 1, 1], Facing.down);
			scene.idle(5);

			scene.text(60, '반응기가 심각한 피해를 입으면 레드스톤 신호를 출력합니다.', [2.5, 1.5, 2]).placeNearTarget().attachKeyFrame();
			scene.idle(10);
			scene.idle(60);

			scene.world.setBlock([2, 2, 0], 'minecraft:gravel', false);
			//scene.world.modifyBlock([2, 3, 1], () => Block.id("minecraft:observer").with("facing", "north"), false);
			scene.world.showSection([2, 1, 0, 2, 3, 0], Facing.down);
			scene.world.showSection([2, 3, 1], Facing.down);
			scene.idle(20);

			scene.text(80, '이 신호로 자갈이나 모래를 받친 피스톤을 움직여 관측기를 작동시킬 수 있습니다.', [2.5, 1.5, 1]).placeNearTarget().attachKeyFrame();
			scene.idle(5);

			scene.world.modifyBlock([2, 1, 1], (curState) => curState.with("power", "15"), false);
			scene.world.modifyBlock([2, 1, 0], (curState) => curState.with("extended", "true"), false);
			scene.world.setBlock([2, 3, 0], 'minecraft:gravel', false);
			scene.world.setBlock([2, 2, 0], 'minecraft:piston_head', false);
			scene.world.modifyBlock([2, 2, 0], (curState) => curState.with("facing", "up"), false);
			scene.idle(90);

			scene.text(120, '관측기가 자갈을 향하도록 배치하세요. 자갈이 관측기를 작동시켜 반응기를 끕니다.', [2.5, 3.5, 2]).placeNearTarget().attachKeyFrame();
			scene.idle(60);






    });
});

// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.
