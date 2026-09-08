// 게임 API는 대역을 사용하고, 번역 스크립트 자체는 설치된 실제 Rhino로 실행해요.
var callbacks = []
var translatedMessages = []
var translationsAvailable = true
var Platform = {
  isLoaded: function () { return testModsLoaded },
  isClientEnvironment: function () { return testClient }
}
// 화면·위젯·컴포넌트는 JS 객체가 아닌 Java 객체와 Rhino의 실제 래퍼를 사용해요.
var MockWidget = RealWidget
var Java = {
  loadClass: function (name) {
    if (name === "net.minecraft.client.gui.components.AbstractWidget") return MockWidget
    if (name === "yalter.mousetweaks.ConfigScreen") return RealConfigScreen
    if (name === "net.minecraft.network.chat.Component") {
      return RealComponent
    }
    if (name === "net.minecraft.client.resources.language.I18n") {
      return {
        exists: function () { return translationsAvailable },
        get: function (key) { return testTranslations[key] || key }
      }
    }
    if (name === "net.neoforged.bus.api.EventPriority") return { LOWEST: "LOWEST" }
    return name
  }
}
var NativeEvents = {
  onEvent: function (priority, type, callback) {
    if (arguments.length === 2) callbacks.push({ type: priority, callback: type })
    else {
      if (priority !== "LOWEST") throw new Error("이벤트 우선순위 변경")
      callbacks.push({ type: type, callback: callback })
    }
  }
}
var Client = { player: null }
var Text = { of: function (text) { return text } }
function check(condition, message) {
  if (!condition) throw new Error(message)
}
function list(values) {
  return {
    size: function () { return values.length },
    get: function (index) { return values[index] },
    set: function (index, value) { values[index] = value }
  }
}
function fire(suffix, event) {
  for (var index = 0; index < callbacks.length; index++) {
    if (callbacks[index].type.endsWith(suffix)) callbacks[index].callback(event)
  }
}
