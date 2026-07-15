// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.

Ponder.registry((allthemods) => {
    allthemods.create([
	'mekanism:sps_casing',
	'mekanism:sps_port',
	'mekanism:supercharged_coil'])
	.scene('sps','Mekanism: 초임계 위상 변환기(SPS)', 'kubejs:sps',

	(scene, util) => {


			scene.world.showSection([0, 0, 0, 6, 7, 6], Facing.down);
			scene.setSceneOffsetY(-1);
            scene.idle(20);

			scene.text(60, 'SPS는 막대한 에너지를 사용해 폴로늄을 반물질로 변환합니다.', [0, 3.5, 6.5]).placeNearTarget();
			scene.addKeyframe();
			scene.idle(80)

			scene.addKeyframe()

			scene.text(60, '설정 장치로 포트의 모드를 변경할 수 있습니다.', [2.5, 1.5, 0]).placeNearTarget();
			scene.showControls(60, [2.5, 2.5, 0], 'down').rightClick().withItem('mekanism:configurator').whileSneaking();
			scene.idle(10);
			scene.world.modifyBlock([2, 1, 0], (curState) => curState.with("active", "true"), false);
			scene.idle(20);
			scene.world.modifyBlock([2, 1, 0], (curState) => curState.with("active", "false"), false);
			scene.idle(40);

			scene.world.hideSection([0, 0, 0, 6, 6, 5], Facing.up);
			scene.idle(10);

			scene.text(60, 'SPS의 각 면을 이 형태로 만드세요.', [2.5, 4, 5]).placeNearTarget().attachKeyFrame();
			scene.idle(60);

			//east face
			scene.world.showSection([6, 0, 0, 6, 7, 5], Facing.down);
			scene.idle(10);

			scene.text(60, '한쪽 면 중앙에는 에너지를 입력할 포트가 필요합니다.', [5.5, 4, 3]).placeNearTarget().attachKeyFrame();
			scene.idle(70);

			scene.world.showSection([5, 3, 3], Facing.down);
			scene.text(60, '내부에서는 포트에 과충전 코일을 붙여 배치하세요.', [5, 4, 3]).placeNearTarget().attachKeyFrame();
			scene.idle(80);

			//west face
			scene.world.showSection([0, 0, 0, 0, 6, 5], Facing.down);
			scene.idle(30);

			scene.world.showSection([1, 3, 3], Facing.down);
			scene.text(60, '과충전 코일을 두 개 사용하면 최대 속도로 에너지를 투입할 수 있습니다.', [0, 4, 3]).placeNearTarget().attachKeyFrame();
			scene.idle(80);

			//bottom face
			scene.world.showSection([1, 0, 0, 5, 0, 5], Facing.down);
			scene.idle(30);

			//top face
			scene.world.showSection([1, 6, 0, 5, 6, 5], Facing.down);
			scene.idle(30);

			//north face
			scene.world.showSection([1, 1, 0, 5, 5, 0], Facing.down);
			scene.idle(30);


			scene.text(60, '폴로늄 입력용 포트가 하나 필요합니다.', [4.5, 1.5, 0]).placeNearTarget().attachKeyFrame();
			scene.idle(70);

			scene.world.modifyBlock([2, 1, 0], (curState) => curState.with("active", "true"), true);
			scene.text(60, '다른 포트로 반물질을 출력하세요.', [2.5, 1.5, 0]).placeNearTarget().attachKeyFrame();
			scene.idle(70);


    });
});

// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.
