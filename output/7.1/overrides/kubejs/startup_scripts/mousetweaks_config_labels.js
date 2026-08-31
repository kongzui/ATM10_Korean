if (Platform.isLoaded("mousetweaks") && Platform.isClientEnvironment()) {
  const $AbstractWidget = Java.loadClass("net.minecraft.client.gui.components.AbstractWidget")
  const $Component = Java.loadClass("net.minecraft.network.chat.Component")
  const $EventPriority = Java.loadClass("net.neoforged.bus.api.EventPriority")
  const $I18n = Java.loadClass("net.minecraft.client.resources.language.I18n")
  const $InitPost = Java.loadClass(
    "net.neoforged.neoforge.client.event.ScreenEvent$Init$Post"
  )
  const $RenderPre = Java.loadClass(
    "net.neoforged.neoforge.client.event.ScreenEvent$Render$Pre"
  )

  const SCREEN_CLASS = "yalter.mousetweaks.ConfigScreen"
  const TRANSLATIONS = [
    ["Multiple Wheel Clicks Move Multiple Items", "mousetweaks.configuration.value.proportional"],
    ["Always Move One Item (macOS Compatibility)", "mousetweaks.configuration.value.always_one"],
    ["Inventory Position Aware, Inverted", "mousetweaks.configuration.value.inventory_position_aware_inverted"],
    ["Inventory Position Aware", "mousetweaks.configuration.value.inventory_position_aware"],
    ["Down to Push, Up to Pull", "mousetweaks.configuration.value.down_to_push_up_to_pull"],
    ["Up to Push, Down to Pull", "mousetweaks.configuration.value.up_to_push_down_to_pull"],
    ["LMB Tweak Without Item", "mousetweaks.configuration.lmb_without_item"],
    ["LMB Tweak With Item", "mousetweaks.configuration.lmb_with_item"],
    ["Wheel Tweak Search Order", "mousetweaks.configuration.wheel_search_order"],
    ["Mouse Tweaks Options", "mousetweaks.configuration.title"],
    ["Scroll Direction", "mousetweaks.configuration.scroll_direction"],
    ["Scroll Scaling", "mousetweaks.configuration.scroll_scaling"],
    ["First to Last", "mousetweaks.configuration.value.first_to_last"],
    ["Last to First", "mousetweaks.configuration.value.last_to_first"],
    ["RMB Tweak", "mousetweaks.configuration.rmb_tweak"],
    ["Wheel Tweak", "mousetweaks.configuration.wheel_tweak"],
    ["Debug Mode", "mousetweaks.configuration.debug_mode"]
  ]

  function translateWidgets(screen, widgets) {
    if (String(screen.getClass().getName()) !== SCREEN_CLASS) {
      return
    }

    if (!$I18n.exists("mousetweaks.configuration.title")) {
      return
    }

    for (let index = 0; index < widgets.size(); index++) {
      const widget = widgets.get(index)

      if (!(widget instanceof $AbstractWidget)) {
        continue
      }

      const original = String(widget.getMessage().getString())
      let translated = original

      for (const [source, key] of TRANSLATIONS) {
        translated = translated.replace(source, String($I18n.get(key)))
      }

      if (translated !== original) {
        widget.setMessage($Component.literal(translated))
      }
    }
  }

  NativeEvents.onEvent($EventPriority.LOWEST, $InitPost, event => {
    translateWidgets(event.getScreen(), event.getListenersList())
  })

  NativeEvents.onEvent($EventPriority.LOWEST, $RenderPre, event => {
    translateWidgets(event.getScreen(), event.getScreen().children())
  })
}
