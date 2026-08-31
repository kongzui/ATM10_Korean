NativeEvents.onEvent("net.neoforged.neoforge.event.entity.player.PlayerEvent$PlayerChangedDimensionEvent", event => {
    if (event.to.location().getNamespace().equals("hyperbox")){
        event.entity.tell("Hyperbox는 6.0 이상 버전에서 제거됩니다. Compact Machines로 옮겨 주세요.")
        if (Platform.clientEnvironment) {
            Client["submit(java.lang.Runnable)"](() => {
                Client.gui.setTitle(Text.blue("Hyperbox").append(Text.red("가 제거될 예정입니다!")))
                Client.gui.setSubtitle(Text.white("새 모드로 물건을 옮겨 주세요: ").append(Text.blue("Compact Machines")))
            })
        }
    }
})
