let shouldFreeze = false // set this to true if you need to debug something on your world

if (shouldFreeze) {
  ServerEvents.loaded(event => {
	  event.server.tell("서버 정지를 시작합니다...")
	  event.server.runCommandSilent("tick freeze")
  })
}
