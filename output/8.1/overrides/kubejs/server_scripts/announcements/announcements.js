let $TreeMap = Java.loadClass("java.util.TreeMap")
/** @type {import("org.apache.maven.artifact.versioning.DefaultArtifactVersion").$DefaultArtifactVersion$$Type} */
let $DefaultArtifactVersion = Java.loadClass("org.apache.maven.artifact.versioning.DefaultArtifactVersion")
/** @type {import("java.util.TreeMap").$TreeMap$$Type<(import("org.apache.maven.artifact.versioning.DefaultArtifactVersion").$DefaultArtifactVersion$$Original), (import("java.util.List").$List$$Type<(import("net.minecraft.network.chat.MutableComponent").$MutableComponent$$Original) >) >} */
let announcements = new $TreeMap()
/** @type {import("org.apache.maven.artifact.versioning.DefaultArtifactVersion").$DefaultArtifactVersion$$Original} */
let currentVersion = null

// files related:
// kubejs/assets/atm/lang/en_us.json

// Add your announcements here
function initAnnouncements(){
  addAnnouncement("4.0", "추가된 모드: Ars Creo, Ice and Fire, Oritech")
  addAnnouncement("4.1", "추가된 모드: Oritech Things")
  addAnnouncement("4.2", "제거된 모드: Oritech Things")
  addAnnouncement("4.3", "추가된 모드: Ars Controle, Create Aquatic Ambitions, Create Hypertube, Mekanism More Machines")
  addAnnouncement("4.5", "추가된 모드: Expanded AE, Industrialization Overdrive, RFTools Storage")
  addAnnouncement("4.6", "추가된 모드: The Aether, BotanyPots, BotanyTrees, RefinedTypes")
  addAnnouncement("4.6", "제거된 모드: Harvest with ease, 이제 FTB Ultimine이 같은 기능을 제공합니다")
  addAnnouncement("4.7", "추가된 모드: Draconic Evolution, BotanyPots-Mystical")
  addAnnouncement("4.12", "추가된 모드: ModularBees")
  addAnnouncement("4.13", "추가된 모드: Dyson Cube Project")
  addAnnouncement("5.0", "제거된 모드: Modular Machinery Reborn, 대신 Modern Industrialization을 사용하세요")
  addAnnouncement("5.3", Text.of("버전 6.0 이상으로 업데이트할 때를 대비해 ").append(Text.blue("Eternal Starlight")).append("와 ").append(Text.blue("Hyperbox")).append(" 모드를 ").append(Text.red("제거")).append("할 준비를 하고 있습니다"))
  addAnnouncement("5.5", Text.of("공개 베타 테스트용으로 ").append(Text.green("All The Mons (ATM10 + Cobblemon)").clickOpenUrl("https://www.curseforge.com/minecraft/modpacks/all-the-mons").hover(Text.translatable("mco.notification.visitUrl.buttonText.default"))).append("을 출시했습니다!"))
}

ServerEvents.loaded(event => {
  if (!Platform.isLoaded("bcc")) return
  announcements.clear()
  /** @type {import("dev.wuffs.bcc.BetterCompatibilityChecker").$BetterCompatibilityChecker$$Original} */
  let $BccInstance = Java.loadClass("dev.wuffs.bcc.BetterCompatibilityChecker")
  currentVersion = new $DefaultArtifactVersion($BccInstance.betterStatus.version())
  initAnnouncements()
})

function addAnnouncement(/** @type {string} */version, /** @type {import("net.minecraft.network.chat.MutableComponent").$MutableComponent$$Original} */ component) {
  announcements.computeIfAbsent(new $DefaultArtifactVersion(version), (key) => Utils.newList()).addLast(typeof component == "string" ? Text.of(component) : component)
}

PlayerEvents.loggedIn(event => {
  if (currentVersion == null) return
  let currentDismissed = event.player.persistentData.getString("LastDismissedAnnouncementVersion")
  if (currentDismissed == null) {
    currentDismissed = new $DefaultArtifactVersion("0.0.0")
  } else {
    currentDismissed = new $DefaultArtifactVersion(currentDismissed)
  }
  let ableToDismiss = false
  let printHeader = true
  announcements.forEach((key, listComponents) => {
    if (currentDismissed.compareTo(key) < 0 && currentVersion.compareTo(key) >= 0) {
      ableToDismiss = true
      if (printHeader) {
        event.player.tell(Text.translatable("=====[  %s  ]=====", Text.yellow("All The Mods 공지").bold()).gold().bold())
        printHeader = false
      }
      for (let component of listComponents) {
        let message = Text.translatable("[%s] - %s", Text.gold(key.toString()), component.yellow()).yellow()
        event.player.tell(message)
      }
    }
  })

  if (ableToDismiss) {
    let message = Text.translatable("announcements.atm.dismiss_up_to_version", Text.blue(currentVersion.toString()))
      .green()
      .hover(Text.translatable("kubejs.atm.click_here"))
      .clickRunCommand("/dismiss_announcements")

    event.player.tell(message)
  }
})

ServerEvents.basicPublicCommand("dismiss_announcements", event => {
  let player = event.player
  if (player == null) {
    event.cancel("플레이어를 찾을 수 없습니다!")
  } else {
    let pData = player.getPersistentData()
    if (event.input == "clear") {
      pData.putString("LastDismissedAnnouncementVersion", "0.0.0")
      event.respond(Text.yellow("닫은 공지의 버전 기록을 지웠습니다!"))
    } else {
      if (currentVersion == null) {
        event.cancel("현재 모드팩 버전이 비어 있습니다. BetterCompatibilityCheck가 설치되어 있나요?")
      } else {
        pData.putString("LastDismissedAnnouncementVersion", currentVersion.toString())
        event.respond(Text.translatable("announcements.atm.dismissed_up_to_version", currentVersion.toString()).yellow())
      }
    }
  }
})
