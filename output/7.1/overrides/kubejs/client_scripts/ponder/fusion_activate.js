// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.

Ponder.registry((allthemods) => {
    allthemods.create([
		'mekanismgenerators:hohlraum',
		'mekanismgenerators:hohlraum[mekanism:chemicals={chemical_tanks:[{amount:10L,id:"mekanismgenerators:fusion_fuel"}]}]',
		'mekanismgenerators:laser_focus_matrix'
	])
	.scene('fusion_activation','Mekanism 핵융합로: 가동', 'kubejs:fusion_activation',

	(scene, util) => {
			scene.world.showSection([2, 0, 0, 6, 4, 6], Facing.down);
			//scene.world.hideSection([3, 0, 0, 5, 2, 0], Facing.up);
            scene.idle(10);

			scene.text(60, '핵융합로를 가동하려면 몇 가지가 필요합니다.', [2, 2.5, 4.5]).placeNearTarget().attachKeyFrame();
			scene.idle(80)

			scene.text(100, '제어기에 D-T 연료로 채운 홀로륨을 넣으세요.', [4.5, 5, 3.5]).attachKeyFrame();
			scene.showControls(100, [4.5, 5.5, 3.5], 'down').withItem('mekanismgenerators:hohlraum');
			scene.idle(110);


			//show lasers
			scene.world.showSection([0, 0, 0, 1, 4, 6], Facing.down);
			scene.idle(10);

			//Laser
			scene.text(100, '레이저 초점 매트릭스에 레이저로 400MRF를 발사해야 합니다.', [0, 2.5, 3.5]).placeNearTarget().attachKeyFrame();
			scene.idle(110);

			//show laser
			scene.world.hideSection([1, 0, 0, 6, 4, 6], Facing.down);
			scene.idle(10)
			scene.rotateCameraY(90);
			scene.idle(5)

			scene.text(100, '레이저 증폭기의 빨간 면이 매트릭스를 향하게 하세요.', [1, 2.5, 3]).placeNearTarget().attachKeyFrame();
			scene.idle(110);

			scene.rotateCameraY(-90);
			scene.idle(5)

			//show everything
			scene.world.showSection([1, 0, 0, 6, 4, 6], Facing.down);
			scene.idle(10)


			//hide lasers
			scene.world.hideSection([0, 0, 0, 1, 4, 6], Facing.down);
			scene.idle(10);

			//fuel input

			scene.overlay.showText(100).text("반응기에 연료도 공급해야 합니다.").independent(-50);
			scene.text(50, '중수소 입력', [5.5, 2.5, 1]).placeNearTarget().attachKeyFrame();
			scene.idle(60);
			scene.text(50, '삼중수소 입력', [3.5, 2.5, 1]).placeNearTarget().attachKeyFrame();
			scene.idle(60);

			scene.text(80, '중수소와 삼중수소를 따로 주입하면 반응기가 설정된 속도로 D-T 연료를 혼합합니다.', [4.5, 2.5, 1]).placeNearTarget().attachKeyFrame();
			scene.idle(80);

    });
});

// This File has been authored by AllTheMods Staff, or a Community contributor for use in AllTheMods - AllTheMods 10.
// As all AllTheMods packs are licensed under All Rights Reserved, this file is not allowed to be used in any public packs not released by the AllTheMods Team, without explicit permission.
