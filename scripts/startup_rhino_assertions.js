check(callbacks.length === (testClient ? (testModsLoaded ? 4 : 1) : 0), "이벤트 수 오류")
if (testClient) {
  var message = "Frequency set to 42"
  var chat = {
    getMessage: function () { return { getString: function () { return message } } },
    setMessage: function (value) { translatedMessages.push(value) }
  }
  fire("ClientChatReceivedEvent$System", chat)
  fire("ClientChatReceivedEvent$System", chat)
  check(translatedMessages.length === 2, "채팅 반복 처리 실패")
  check(translatedMessages[0] === "주파수 설정 완료: 42", "채팅 번역 오류")
  message = "unrelated message"
  fire("ClientChatReceivedEvent$System", chat)
  check(translatedMessages.length === 2, "무관한 채팅 변경")
  message = "Frequency set to 42"
  Client.player = { mainHandItem: { id: "minecraft:stone" } }
  fire("ClientChatReceivedEvent$System", chat)
  check(translatedMessages.length === 2, "다른 모드 주파수 채팅 변경")
  Client.player = { mainHandItem: { id: "enderdrives:ender_disk_1k" } }
  fire("ClientChatReceivedEvent$System", chat)
  check(translatedMessages.length === 3, "엔더 드라이브 채팅 누락")
}
if (testClient && testModsLoaded) {
  var lines = ["hunger: 20, sat: 5.0, exh: 0.25", "unrelated"]
  var debug = { getLeft: function () { return list(lines) } }
  fire("CustomizeGuiOverlayEvent$DebugText", debug)
  fire("CustomizeGuiOverlayEvent$DebugText", debug)
  check(lines[0] === "허기: 20, 포만도: 5.0, 허기 소모도: 0.25", "F3 번역 오류")
  check(lines[1] === "unrelated", "F3 무관한 줄 변경")
  var widgets = [new MockWidget("Mouse Tweaks Options"), new MockWidget("Always Move One Item (macOS Compatibility)"), new MockWidget("unrelated")]
  var screen = new RealConfigScreen()
  for (var wi = 0; wi < widgets.length; wi++) screen.addWidget(widgets[wi])
  var event = new RealScreenEvent(screen)
  fire("ScreenEvent$Init$Post", event)
  fire("ScreenEvent$Render$Pre", event)
  fire("ScreenEvent$Render$Pre", event)
  check(widgets[0].text === testTranslations["mousetweaks.configuration.title"], "설정 제목 번역 오류")
  check(widgets[1].text === testTranslations["mousetweaks.configuration.value.always_one"], "설정 선택지 번역 오류")
  check(widgets[2].text === "unrelated", "무관한 위젯 변경")
  widgets[0].text = "Mouse Tweaks Options"
  translationsAvailable = false
  fire("ScreenEvent$Render$Pre", event)
  check(widgets[0].text === "Mouse Tweaks Options", "리소스팩 미사용 조건 오류")
  translationsAvailable = true
  var other = new RealScreen()
  other.addWidget(widgets[0])
  event = new RealScreenEvent(other)
  fire("ScreenEvent$Init$Post", event)
  fire("ScreenEvent$Render$Pre", event)
  check(widgets[0].text === "Mouse Tweaks Options", "다른 화면 변경")
}
