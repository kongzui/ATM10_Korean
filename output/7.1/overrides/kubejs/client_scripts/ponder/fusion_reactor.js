// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.

Ponder.registry((allthemods) => {
    allthemods.create([
	'mekanismgenerators:fusion_reactor_frame',
	'mekanismgenerators:fusion_reactor_port',
	'mekanismgenerators:fusion_reactor_controller',
	'mekanismgenerators:fusion_reactor_logic_adapter'
	])
	.scene('fusion_reactor','Mekanism 핵융합로', 'kubejs:fusion_mek',

	(scene, util) => {


			scene.world.showSection([0, 0, 0, 4, 4, 4], Facing.down);
            scene.idle(10);

			scene.text(60, '핵융합로는 틱당 수백만 RF를 생산할 수 있습니다.', [0, 2.5, 4.5]).placeNearTarget().attachKeyFrame();
			scene.idle(80)

			scene.text(60, '설정 장치로 포트의 모드를 변경할 수 있습니다.', [1.5, 2.5, 0]).placeNearTarget().attachKeyFrame();
			scene.showControls(60, [1.5, 3.5, 0], 'down').rightClick().withItem('mekanism:configurator').whileSneaking();
			scene.idle(10);
			scene.world.modifyBlock([1, 2, 0], (curState) => curState.with("active", "true"), true);
			scene.idle(20);
			scene.world.modifyBlock([1, 2, 0], (curState) => curState.with("active", "false"), true);
			scene.idle(40);

			//hide front
			scene.world.hideSection([0, 0, 0, 4, 4, 3], Facing.up);
			scene.idle(10);

			scene.text(80, '핵융합로의 각 면을 이 형태로 만드세요.', [2.5, 2, 4.5]).attachKeyFrame();
			scene.idle(90);

			//east face
			scene.world.showSection([4, 0, 0, 4, 4, 3], Facing.down);
			scene.idle(10);

			//power port
			scene.text(60, '에너지를 출력할 포트가 필요합니다.', [4, 2.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(70);

			//west face
			scene.world.showSection([0, 0, 0, 0, 4, 3], Facing.down);
			scene.idle(30);

			//Laser
			scene.text(60, '레이저 초점 매트릭스로 반응기를 가동합니다.', [0, 2.5, 2.5]).placeNearTarget().attachKeyFrame();
			scene.idle(70);

			//bottom face
			scene.world.showSection([1, 0, 0, 3, 0, 3], Facing.down);
			scene.idle(30);

			//top face
			scene.world.showSection([0, 4, 0, 3, 4, 3], Facing.down);
			scene.idle(30);

			//controller
			scene.text(60, '핵융합로 제어기는 윗면 중앙에 배치해야 합니다.', [2.5, 4.5, 3.5]).placeNearTarget().attachKeyFrame();
			scene.idle(70);

			//north face
			scene.world.showSection([1, 1, 0, 3, 3, 0], Facing.down);
			scene.idle(30);

			//fuel input

			scene.text(30, '중수소를 입력할 포트 두 개가 필요하고', [3.5, 2.5, 0]).placeNearTarget().attachKeyFrame();
			scene.idle(40);
			scene.text(40, '삼중수소도 입력해야 합니다.', [1.5, 2.5, 0]).placeNearTarget().attachKeyFrame();
			scene.idle(50);





    });
});

// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.
