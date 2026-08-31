if (Platform.isLoaded("appleskin") && Platform.isClientEnvironment()) {
  const $EventPriority = Java.loadClass("net.neoforged.bus.api.EventPriority")
  const $DebugTextEvent = Java.loadClass(
    "net.neoforged.neoforge.client.event.CustomizeGuiOverlayEvent$DebugText"
  )

  NativeEvents.onEvent($EventPriority.LOWEST, $DebugTextEvent, event => {
    const lines = event.getLeft()

    for (let index = 0; index < lines.size(); index++) {
      const line = String(lines.get(index))
      const match = /^hunger: ([^,]+), sat: ([^,]+), exh: (.+)$/.exec(line)

      if (match !== null) {
        lines.set(
          index,
          `허기: ${match[1]}, 포만도: ${match[2]}, 허기 소모도: ${match[3]}`
        )
      }
    }
  })
}
