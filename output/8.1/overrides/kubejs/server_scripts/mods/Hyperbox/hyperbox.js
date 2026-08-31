if (Platform.isLoaded("hyperbox")) {
    BlockEvents.rightClicked("hyperbox:hyperbox",event => {
        event.server.tell(Text.red('Hyperbox는 6.0 이상 버전에서 제거됩니다. Compact Machines로 옮겨 주세요.'))
    })
}
