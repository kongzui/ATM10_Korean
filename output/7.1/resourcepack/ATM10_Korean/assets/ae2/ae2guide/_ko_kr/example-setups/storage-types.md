---
navigation:
  parent: example-setups/example-setups-index.md
  title: 저장소 종류와 네트워크 정리
  icon: drive
---

# 다양한 저장소와 네트워크 정리

필터, [파티션](../items-blocks-machines/cell_workbench.md)과
[저장소 우선순위](../ae2-mechanics/import-export-storage.md#storage-priority)를 이용해 내용물 종류에 따른 여러
단계의 저장소를 만들 수 있습니다.

저장소는 대체로 다음과 같이 나뉩니다.
* 일반 저장소는 몇 개에서 몇천 개 정도 가진 잡다한 물건을 보관합니다. 4k나 16k 같은 작은
  [셀](../items-blocks-machines/storage_cells.md)을 사용합니다.
* 대량 저장소는 조약돌이나 철처럼 몇천 개보다 많이 가진 물건을 보관합니다. 256k 같은 큰 셀이나 MEGA
  애드온의 셀을 사용합니다.
* 농장의 지역 저장소는 [전용 지역 저장소](specialized-local-storage.md)와
  [다양한](simple-certus-farm.md) [서투스](semiauto-certus-farm.md) [농장](advanced-certus-farm.md)에서
  설명한 형태입니다.

아이템을 주 네트워크에 넣으면 전용 대량·지역 저장소를 먼저 시도하고, 필터와 파티션 때문에 들어갈 수
없으면 일반 저장소에 넣도록 우선순위를 설정합니다. 아이템이 한 저장소에서 다른 저장소로 **능동적으로
이동하지는 않지만**, 네트워크에 들어오고 나갈 때 점차 "이주"합니다. 능동적으로 옮기려면
<ItemLink id="io_port" />를 사용하세요.

<GameScene zoom="3" interactive={true}>
  <ImportStructure src="../assets/assemblies/network_storage_types.snbt" />

    <BoxAnnotation color="#33dd33" min="11 0 1" max="12 1.3 2" thickness="0.05">
        대량 저장소입니다. 이 예에서는 서랍 같은 대용량 저장소에 필터가 설정된 저장 버스를 붙였습니다.
        석탄으로 필터링하고 높은 우선순위를 설정하여 석탄이 네트워크에 들어오면 이곳으로 향하고, 꺼낼
        때는 *이곳을 제외한 모든 곳*에서 먼저 가져오므로 석탄이 서랍으로 "이주"합니다.

        중요: 서랍처럼 최적화된 대형 인벤토리는 괜찮지만 거대 상자처럼 슬롯이 많고 최적화되지 않은
        인벤토리에 저장 버스를 붙이면 성능이 매우 나빠집니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dd33" min="11 0 3" max="12 1 4" thickness="0.05">
        대량 저장소입니다. 이 예에서는 높은 우선순위의 ME 드라이브에 조약돌과 철로 파티션을 설정한
        256k 셀을 넣었습니다. 균등 분배 카드가 있어 조약돌만으로 가득 차 철을 넣지 못하는 일을 막습니다.
        조약돌이나 철이 네트워크에 들어오면 이 셀로 향하고, 꺼낼 때는 *이곳을 제외한 모든 곳*에서 먼저
        가져오므로 두 아이템이 셀로 "이주"합니다.
    </BoxAnnotation>

    <BoxAnnotation color="#33dddd" min="11 0 5" max="12 1 6" thickness="0.05">
        일반 저장소입니다. 이 예에서는 16k 셀로 가득 찬 ME 드라이브를 사용하며 파티션을 설정하지
        않았습니다. 중립 우선순위 0을 사용해 아이템이 들어오면 전용 대량·지역 저장소를 먼저 선택하고,
        꺼낼 때는 이곳에서 먼저 가져옵니다. 전용 저장소가 있는 아이템은 일반 저장소에서 자연스럽게
        "이주"합니다.
    </BoxAnnotation>

    <BoxAnnotation color="#88ff88" min="11 0 8" max="12 1 9" thickness="0.05">
        이 I/O 포트는 네트워크 정리에 중요한 역할을 합니다. 저장소 우선순위는 아이템을 *능동적으로*
        옮기지 않으므로 일반 저장소의 셀을 주기적으로 I/O 포트로 "섞어" 전용 저장소가 있는 아이템을
        그곳으로 옮겨야 합니다. 저장 위치를 조각 모음하여 같은 물건이 여러 곳에 나뉘어 저장되지 않게 합니다.
    </BoxAnnotation>

    <BoxAnnotation color="#dd3333" min="14 0 11" max="15 1 12" thickness="0.05">
        몹 농장의 지역 저장소입니다. ME 드라이브의 셀에는 뼈와 화살처럼 보관할 전리품으로 파티션을
        설정합니다. 우선순위는 ME 드라이브가 아니라 주 네트워크에서 서브네트워크에 접근하는 저장 버스가
        결정합니다. 셀에는 균등 분배 카드와 초과분 파괴 카드를 설치합니다.
    </BoxAnnotation>

    <BoxAnnotation color="#dd3333" min="14 1 10" max="15 2.3 11" thickness="0.05">
        몹 농장의 지역 저장소입니다. 저장 버스와 인터페이스 구성이 주 네트워크에서 서브네트워크 저장소에
        접근하게 합니다. 저장 버스는 높은 우선순위를 사용하며 서브네트워크 셀에 저장할 항목으로 필터링합니다.

        중요: 서브네트워크에 폐기 장치가 있으므로 저장 버스를 반드시 필터링하세요. 그렇지 않으면
        네트워크에 들어오는 *모든 아이템과 유체 등*을 버리기 시작합니다!
    </BoxAnnotation>

    <BoxAnnotation color="#dd3333" min="14 0 9" max="15 1.3 10" thickness="0.05">
        몹 농장의 지역 저장소입니다. 물질 응축기의 저장 버스는 ME 드라이브보다 낮은 우선순위를
        사용합니다. 드라이브의 셀에 들어갈 수 없는 몹 전리품은 이곳으로 넘쳐 폐기됩니다. 거의 부서진
        활 같은 잡동사니가 서브네트워크를 막지 않게 하는 데 중요합니다.
    </BoxAnnotation>

    <BoxAnnotation color="#dd33dd" min="8 1 11.7" max="9 2.3 13" thickness="0.05">
        수박 농장의 지역 저장소입니다. 여러 서투스 농장 예제와 비슷한 방법을 사용합니다. 서브네트워크의
        저장 버스가 수확물을 통에 넣고, 수박 조각으로 필터링된 높은 우선순위의 주 네트워크 저장 버스가
        수확물에 접근하게 합니다.
    </BoxAnnotation>

  <IsometricCamera yaw="270" pitch="30" />
</GameScene>
