#!/usr/bin/env python3
"""CC: Tweaked 계열 언어 파일을 현재 영어 원문 기준으로 번역하고 전수 검증한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path

import actually_additions_family as candidate_helper
import five_family_goal as family_goal
from local_paths import PROJECT_ROOT, resolve_source_root


FAMILY = "cc_tweaked"
WORK_ROOT = PROJECT_ROOT / "working/cc_tweaked"
CACHE_FILE = PROJECT_ROOT / "temp/cc_tweaked_language_candidate_cache.json"
CANDIDATE_FILE = WORK_ROOT / "auto_candidates.json"
NAMESPACES = ("computercraft", "advancedperipherals", "morered")

SOURCE_OVERRIDES = {
    "CC: Tweaked": "CC: Tweaked",
    "ComputerCraft": "CC: Tweaked",
    "Advanced Peripherals": "Advanced Peripherals",
    "More Red": "More Red",
    "HTTP": "HTTP",
    "Proxy": "프록시",
    "Redstone": "레드스톤",
    "Computer": "컴퓨터",
    "Computers": "컴퓨터",
    "Monitor": "모니터",
    "Monitors": "모니터",
    "Turtle": "터틀",
    "Turtles": "터틀",
    "Peripheral": "주변 장치",
    "Peripherals": "주변 장치",
    "Filesystem operations": "파일 시스템 작업",
    "Server tasks": "서버 작업",
    "Tasks": "작업",
}

TERM_REPLACEMENTS = (
    ("컴퓨터크래프트", "CC: Tweaked"),
    ("고급 주변장치", "Advanced Peripherals"),
    ("주변기기", "주변 장치"),
    ("주변 장치 장치", "주변 장치"),
    ("거북이", "터틀"),
    ("플로피 디스크", "플로피 디스크"),
    ("웹소켓", "WebSocket"),
    ("웹 소켓", "WebSocket"),
    ("스레드", "스레드"),
    ("쓰레드", "스레드"),
    ("블랙리스트", "차단 목록"),
    ("화이트리스트", "허용 목록"),
    ("인벤토리 매니저", "인벤토리 관리자"),
    ("지리 스캐너", "지질 스캐너"),
    ("에너지 탐지기", "에너지 감지기"),
    ("환경 탐지기", "환경 감지기"),
    ("플레이어 탐지기", "플레이어 감지기"),
    ("브릿지", "브리지"),
    ("NBT 스토리지", "NBT 저장소"),
    ("채팅 박스", "채팅 상자"),
    ("콜로니 인테그레이터", "식민지 연동기"),
    ("레드스톤 인테그레이터", "레드스톤 연동기"),
    ("인게임", "게임 내"),
)

KEY_OVERRIDES: dict[str, str] = {
    "argument.computercraft.argument_expected": "인수가 필요합니다.",
    "argument.computercraft.computer.distance": "엔티티까지 거리",
    "argument.computercraft.computer.family": "컴퓨터 계열",
    "argument.computercraft.computer.instance": "고유 인스턴스 ID",
    "argument.computercraft.computer.label": "컴퓨터 이름표",
    "argument.computercraft.computer.many_matching": (
        "'%s'와 일치하는 컴퓨터가 여러 대입니다(인스턴스 %s)."
    ),
    "argument.computercraft.tracking_field.no_field": "알 수 없는 필드 '%s'입니다.",
    "argument.computercraft.unknown_computer_family": "알 수 없는 컴퓨터 계열 '%s'입니다.",
    "itemGroup.computercraft": "CC: Tweaked",
    "block.computercraft.cable": "네트워크 케이블",
    "block.computercraft.redstone_relay": "레드스톤 중계기",
    "block.computercraft.printer": "프린터",
    "chat.computercraft.wired_modem.peripheral_connected": (
        "주변 장치 '%s'이(가) 네트워크에 연결되었습니다."
    ),
    "chat.computercraft.wired_modem.peripheral_disconnected": (
        "주변 장치 '%s'의 네트워크 연결이 끊겼습니다."
    ),
    "commands.computercraft.dump.desc": (
        "모든 컴퓨터의 상태나 특정 컴퓨터의 상세 정보를 표시합니다. 인스턴스 ID(예: 123), "
        '컴퓨터 ID(예: #123), 이름표(예: "@My Computer")를 지정할 수 있습니다.'
    ),
    "commands.computercraft.queue.desc": (
        "추가 인수와 함께 computer_command 이벤트를 명령 컴퓨터로 보냅니다. 주로 지도 제작자를 "
        "위한 기능으로, /trigger를 컴퓨터에서 쓰기 편하게 만든 형태입니다. 모든 플레이어가 실행할 "
        "수 있으며 보통 텍스트 구성 요소의 클릭 이벤트에서 사용합니다."
    ),
    "commands.computercraft.queue.synopsis": "명령 컴퓨터로 computer_command 이벤트 보내기",
    "commands.computercraft.shutdown.desc": (
        "지정한 컴퓨터를 종료하며, 지정하지 않으면 모두 종료합니다. 인스턴스 ID(예: 123), "
        '컴퓨터 ID(예: #123), 이름표(예: "@My Computer")를 사용할 수 있습니다.'
    ),
    "commands.computercraft.shutdown.synopsis": "컴퓨터 원격 종료",
    "commands.computercraft.synopsis": "컴퓨터를 제어하는 여러 명령",
    "commands.computercraft.track.desc": (
        "컴퓨터의 실행 시간과 처리한 이벤트 수를 추적합니다. /forge track과 비슷한 방식으로 "
        "정보를 표시해 지연 원인을 찾는 데 도움이 됩니다."
    ),
    "commands.computercraft.track.dump.no_timings": "측정 결과가 없습니다.",
    "commands.computercraft.track.dump.synopsis": "최근 추적 결과 출력",
    "commands.computercraft.track.stop.not_enabled": "현재 추적 중인 컴퓨터가 없습니다.",
    "commands.computercraft.turn_on.desc": (
        "지정한 컴퓨터를 켭니다. 인스턴스 ID(예: 123), 컴퓨터 ID(예: #123), 이름표"
        '(예: "@My Computer")를 사용할 수 있습니다.'
    ),
    "commands.computercraft.turn_on.synopsis": "컴퓨터 원격 켜기",
    "commands.computercraft.view.desc": (
        "컴퓨터 터미널을 열어 원격으로 제어합니다. 터틀 인벤토리에는 접근할 수 없습니다. "
        "인스턴스 ID(예: 123) 또는 컴퓨터 ID(예: #123)를 지정할 수 있습니다."
    ),
    "commands.computercraft.view.not_player": "플레이어만 터미널을 열 수 있습니다.",
    "commands.computercraft.view.synopsis": "컴퓨터 터미널 보기",
    "gui.computercraft.terminal": "컴퓨터 터미널",
    "gui.computercraft.pocket_computer_overlay": (
        "포켓 컴퓨터가 열려 있습니다. ESC를 눌러 닫으세요."
    ),
    "gui.computercraft.config.command_require_creative": (
        "명령 컴퓨터에 크리에이티브 모드 필요"
    ),
    "gui.computercraft.config.command_require_creative.tooltip": (
        "명령 컴퓨터와 상호 작용하려면 크리에이티브 모드이면서 관리자 권한이 있어야 합니다.\n"
        "바닐라 명령 블록의 기본 동작과 같습니다."
    ),
    "gui.computercraft.config.computer_space_limit": "컴퓨터 저장 공간 제한(바이트)",
    "gui.computercraft.config.computer_space_limit.tooltip": (
        "컴퓨터와 터틀의 디스크 저장 공간 제한을 바이트 단위로 설정합니다."
    ),
    "gui.computercraft.config.default_computer_settings.tooltip": (
        "새 컴퓨터에 적용할 기본 시스템 설정을 쉼표로 구분한 목록입니다.\n"
        '예: "shell.autocomplete=false,lua.autocomplete=false,edit.autocomplete=false"\n'
        "를 지정하면 모든 자동 완성이 꺼집니다."
    ),
    "gui.computercraft.config.disabled_generic_methods": "비활성화할 공통 메서드",
    "gui.computercraft.config.disabled_generic_methods.tooltip": (
        "비활성화할 공통 메서드나 메서드 제공자 목록입니다. 공통 메서드는 명시적인 주변 장치\n"
        "제공자가 없을 때 블록이나 블록 엔티티에 추가되는 메서드입니다. 여기에는 인벤토리\n"
        "메서드(예: inventory.getItemDetail,\n"
        "inventory.pushItems)와 Forge의 fluid_storage 및 energy_storage\n"
        "메서드가 포함됩니다.\n"
        "목록에는 메서드 그룹 전체(computercraft:inventory)\n"
        "또는 단일 메서드(computercraft:inventory#pushItems)를 지정할 수 있습니다.\n"
    ),
    "gui.computercraft.config.execution.computer_threads.tooltip": (
        "컴퓨터가 사용할 실행 스레드 수를 정합니다. 수가 많으면 더 많은\n"
        "컴퓨터를 동시에 실행할 수 있지만 지연이 생길 수 있습니다. 일부 모드는\n"
        "스레드가 1개보다 많으면 작동하지 않을 수 있으므로 주의하세요."
    ),
    "gui.computercraft.config.execution.max_main_computer_time.tooltip": (
        "컴퓨터 하나가 한 틱에 실행될 이상적인 최대 시간을 밀리초 단위로 정합니다.\n"
        "작업 시간을 미리 알 수 없어 이 제한을 넘을 수도 있으며,\n"
        "평균 실행 시간의 상한을 정하는 값입니다."
    ),
    "gui.computercraft.config.execution.max_main_global_time": "서버 틱 전체 실행 시간 제한",
    "gui.computercraft.config.execution.max_main_global_time.tooltip": (
        "한 틱에 모든 작업 실행에 사용할 수 있는 최대 시간을\n"
        "밀리초 단위로 정합니다.\n"
        "작업 시간을 미리 알 수 없어 이 제한을 넘을 수도 있으며,\n"
        "평균 실행 시간의 상한을 정하는 값입니다."
    ),
    "gui.computercraft.config.execution.tooltip": (
        "컴퓨터의 실행 방식을 제어합니다. 주로 서버를 세밀하게 조정하는\n"
        "옵션이므로 일반적으로 바꿀 필요가 없습니다."
    ),
    "gui.computercraft.config.floppy_space_limit": "플로피 디스크 저장 공간 제한(바이트)",
    "gui.computercraft.config.floppy_space_limit.tooltip": (
        "플로피 디스크의 저장 공간 제한을 바이트 단위로 설정합니다."
    ),
    "gui.computercraft.config.http.bandwidth.global_download": "전체 다운로드 제한",
    "gui.computercraft.config.http.bandwidth.global_download.tooltip": (
        "모든 컴퓨터가 공유하는 초당 다운로드 제한입니다(바이트/초)."
    ),
    "gui.computercraft.config.http.bandwidth.global_upload": "전체 업로드 제한",
    "gui.computercraft.config.http.bandwidth.global_upload.tooltip": (
        "모든 컴퓨터가 공유하는 초당 업로드 제한입니다(바이트/초)."
    ),
    "gui.computercraft.config.http.enabled.tooltip": (
        '컴퓨터에서 "http" API를 켭니다. 끄면 많은 사용자가 이용하는 "pastebin"과\n'
        '"wget" 프로그램도 작동하지 않습니다. 이 옵션은 켜 두고\n'
        '"rules" 설정으로 세부 접근을 제어하는 것을 권장합니다.'
    ),
    "gui.computercraft.config.http.max_requests.tooltip": (
        "컴퓨터 하나가 동시에 보낼 수 있는 http 요청 수입니다. 초과한 요청은\n"
        "대기열에 들어갔다가 실행 중인 요청이 끝나면 전송됩니다.\n"
        "0으로 설정하면 제한하지 않습니다."
    ),
    "gui.computercraft.config.http.proxy.tooltip": (
        'HTTP와 WebSocket 요청을 프록시 서버를 통해 보냅니다. "use_proxy"가 true인 HTTP\n'
        "규칙에만 적용되며 기본값은 꺼짐입니다.\n"
        '프록시 인증이 필요하면 "computercraft-server.toml"과 같은 폴더에\n'
        '"computercraft-proxy.pw" 파일을 만들고 콜론으로 구분한\n'
        '사용자 이름과 비밀번호(예: "myuser:mypassword")를 적으세요.\n'
        "SOCKS4 프록시는 사용자 이름만 필요합니다."
    ),
    "gui.computercraft.config.http.websocket_enabled": "WebSocket 활성화",
    "gui.computercraft.config.http.websocket_enabled.tooltip": (
        'http WebSocket을 사용합니다. "http_enable" 옵션도 true여야 합니다.'
    ),
    "gui.computercraft.config.log_computer_errors.tooltip": (
        "주변 장치와 다른 Lua 객체에서 발생한 예외를 기록합니다. 모드 개발자가\n"
        "문제를 디버그하기 쉬워지지만, 오류가 있는 메서드를 사용하면\n"
        "로그가 지나치게 많이 쌓일 수 있습니다."
    ),
    "gui.computercraft.config.maximum_open_files": "컴퓨터당 최대 동시 열기 파일 수",
    "gui.computercraft.config.maximum_open_files.tooltip": (
        "컴퓨터 하나가 동시에 열 수 있는 파일 수입니다. 0으로 설정하면 제한하지 않습니다."
    ),
    "gui.computercraft.config.monitor_distance": "모니터 표시 거리",
    "gui.computercraft.config.monitor_distance.tooltip": (
        "모니터를 렌더링하는 최대 거리입니다. 기본값은 일반 블록 엔티티\n"
        "표시 제한이지만 더 큰 모니터를 만들 때 늘릴 수 있습니다."
    ),
    "gui.computercraft.config.monitor_renderer.tooltip": (
        '모니터에 사용할 렌더러입니다. 일반적으로 "best"를 유지하세요.\n'
        "모니터 성능 문제가 있으면 다른\n"
        "렌더러를 시험해 볼 수 있습니다."
    ),
    "gui.computercraft.config.peripheral.max_notes_per_tick.tooltip": (
        "스피커가 한 번에 연주할 수 있는 최대 음표 수입니다."
    ),
    "gui.computercraft.config.peripheral.modem_high_altitude_range": (
        "모뎀 범위(고고도)"
    ),
    "gui.computercraft.config.peripheral.modem_high_altitude_range_during_storm": (
        "모뎀 범위(고고도, 악천후)"
    ),
    "gui.computercraft.config.peripheral.monitor_bandwidth": "모니터 대역폭",
    "gui.computercraft.config.peripheral.monitor_bandwidth.tooltip": (
        "틱마다 전송할 수 있는 모니터 데이터의 양을 제한합니다. 참고:\n"
        " - 대역폭은 압축 전에 측정하므로 클라이언트에 실제로 전송되는 데이터는\n"
        "   더 작습니다.\n"
        " - 패킷을 받는 플레이어 수는 계산하지 않습니다. 플레이어 한 명에게\n"
        "   보내든 20명에게 보내든 같은 대역폭을 소비합니다.\n"
        " - 최대 크기 모니터는 약 25KB를 전송하므로 기본값(1MB)이면 한 틱에 약 40개\n"
        "   모니터를 갱신할 수 있습니다.\n"
        "0으로 설정하면 제한을 끕니다."
    ),
    "gui.computercraft.config.term_sizes": "터미널 크기",
    "gui.computercraft.config.term_sizes.computer.height": "터미널 높이",
    "gui.computercraft.config.term_sizes.computer.height.tooltip": "컴퓨터 터미널 높이",
    "gui.computercraft.config.term_sizes.computer.tooltip": "컴퓨터 터미널 크기입니다.",
    "gui.computercraft.config.term_sizes.computer.width": "터미널 너비",
    "gui.computercraft.config.term_sizes.pocket_computer.height": "터미널 높이",
    "gui.computercraft.config.term_sizes.pocket_computer.height.tooltip": (
        "포켓 컴퓨터 터미널 높이"
    ),
    "gui.computercraft.config.term_sizes.pocket_computer.tooltip": (
        "포켓 컴퓨터 터미널 크기입니다."
    ),
    "gui.computercraft.config.term_sizes.pocket_computer.width": "터미널 너비",
    "gui.computercraft.config.term_sizes.tooltip": (
        "여러 컴퓨터의 터미널 크기를 설정합니다.\n"
        "터미널이 클수록 대역폭을 더 사용하므로 주의하세요."
    ),
    "gui.computercraft.config.turtle.can_push": "터틀이 엔티티 밀기",
    "gui.computercraft.config.turtle.can_push.tooltip": (
        "true이면 공간이 있을 때 터틀이 멈추지 않고\n" "앞을 막는 엔티티를 밀어냅니다."
    ),
    "gui.computercraft.config.turtle.need_fuel": "터틀 연료 사용",
    "gui.computercraft.config.turtle.need_fuel.tooltip": (
        "터틀이 이동할 때 연료가 필요한지 설정합니다."
    ),
    "gui.computercraft.config.turtle.normal_fuel_limit.tooltip": "터틀의 연료 한도입니다.",
    "gui.computercraft.config.turtle.tooltip": "터틀 관련 옵션입니다.",
    "gui.computercraft.config.upload_max_size.tooltip": (
        "파일 업로드 크기 제한을 바이트 단위로 설정하며 1KiB에서 16MiB 사이여야 합니다.\n"
        "업로드는 한 틱 안에 처리되므로 큰 파일이나 느린 네트워크는\n"
        "네트워크 스레드를 멈추게 할 수 있습니다. 디스크 공간도 확인하세요!"
    ),
    "gui.computercraft.config.upload_nag_delay": "미처리 업로드 알림 지연",
    "gui.computercraft.config.upload_nag_delay.tooltip": (
        "전송한 파일을 처리하지 않았다는 알림을 띄우기까지의 시간(초)입니다. 0이면 끕니다."
    ),
    "item.computercraft.printed_pages": "인쇄된 여러 페이지",
    "tag.item.computercraft.dyeable": "염색 가능한 아이템",
    "tag.item.computercraft.turtle_can_place": "터틀이 설치할 수 있는 아이템",
    "tracking_field.computercraft.peripheral.name": "주변 장치 호출",
    "tracking_field.computercraft.websocket_outgoing.name": "WebSocket 송신",
    "upgrade.computercraft.wireless_modem_normal.adjective": "무선",
    "upgrade.minecraft.crafting_table.adjective": "제작",
    "upgrade.minecraft.diamond_pickaxe.adjective": "채굴",
    "upgrade.minecraft.diamond_shovel.adjective": "굴착",
    "upgrade.minecraft.diamond_sword.adjective": "근접 전투",
    "gui.computercraft.config.http.rules.tooltip": (
        '특정 도메인이나 IP에서 "http" API의 동작을 제어하는 규칙 목록입니다.\n'
        "각 규칙은 호스트 이름과 선택적 포트에 일치한 뒤 요청의 여러 속성을\n"
        "설정합니다. 규칙은 앞에서부터 평가하므로 앞선 규칙이 뒤의 규칙보다\n"
        "우선합니다.\n\n"
        "사용할 수 있는 속성:\n"
        ' - "host"(필수): 이 규칙과 일치할 도메인 또는 IP 주소입니다. 도메인 이름\n'
        '("pastebin.com"), 와일드카드("*.pastebin.com") 또는 CIDR 표기'
        '("127.0.0.0/8")를 사용할 수 있습니다.\n'
        ' - "port"(선택): 80이나 443처럼 특정 포트의 요청에만 일치합니다.\n\n'
        ' - "action"(선택): 요청을 허용할지 거부할지 정합니다.\n'
        ' - "max_download"(선택): 한 요청에서 컴퓨터가 다운로드할 수 있는 최대 크기\n'
        "(바이트)입니다.\n"
        ' - "max_upload"(선택): 한 요청에서 컴퓨터가 업로드할 수 있는 최대 크기(바이트)입니다.\n'
        ' - "max_websocket_message"(선택): 컴퓨터가 WebSocket 패킷 하나로 보내거나 받을 수\n'
        "있는 최대 크기(바이트)입니다.\n"
        ' - "use_proxy"(선택): HTTP/SOCKS 프록시가 설정되어 있으면 사용합니다.'
    ),
    "itemGroup.advancedperipheralstab": "Advanced Peripherals",
    "keybind.advancedperipherals.category": "Advanced Peripherals",
    "advancedperipherals.name": "Advanced Peripherals",
    "advancements.advancedperipherals.base_toolkit": "신사의 장비",
    "advancements.advancedperipherals.base_toolkit.description": (
        "레드스톤 연동기, 인벤토리 관리자, 에너지 감지기를 모으세요. 이것들 없이 어떻게 "
        "플레이했을까요?"
    ),
    "advancements.advancedperipherals.end_automata_core": "엔드 오토마타 코어",
    "advancements.advancedperipherals.end_automata_core.description": (
        "이것으로 GPS 없이 위치를 찾는 코드를 짤 수 있다면 대단한 사람입니다."
    ),
    "advancements.advancedperipherals.husbandry_automata_core": "축산 오토마타 코어",
    "advancements.advancedperipherals.husbandry_automata_core.description": (
        "이 코어는 글루텐 무첨가일까요?"
    ),
    "advancements.advancedperipherals.nbt_toolkit": "숨길 수 없는 비밀",
    "advancements.advancedperipherals.nbt_toolkit.description": (
        "NBT 저장소와 블록 리더를 모으세요. 이제 세상의 모든 비밀이 열립니다!"
    ),
    "advancements.advancedperipherals.overpowered_automata_core": "초강력 오토마타 코어",
    "advancements.advancedperipherals.overpowered_automata_core.description": (
        "이토록 강한 힘을 감당할 수 있나요?"
    ),
    "advancements.advancedperipherals.root": "Advanced Peripherals",
    "advancements.advancedperipherals.root.description": "모든 여정은 첫 블록에서 시작됩니다.",
    "advancements.advancedperipherals.sense_toolkit": "진실은 영원히 숨을 수 없다",
    "advancements.advancedperipherals.sense_toolkit.description": (
        "지질 스캐너와 환경 감지기를 모으세요. 관찰에 한계란 없습니다!"
    ),
    "advancements.advancedperipherals.weak_automata_core": "첫 오토마타 코어",
    "advancements.advancedperipherals.weak_automata_core.description": (
        "Minecraft에도 사후 세계가 있을까요?"
    ),
    "block.advancedperipherals.block_reader": "블록 리더",
    "block.advancedperipherals.chat_box": "채팅 상자",
    "block.advancedperipherals.colony_integrator": "식민지 연동기",
    "block.advancedperipherals.energy_detector": "에너지 감지기",
    "block.advancedperipherals.environment_detector": "환경 감지기",
    "block.advancedperipherals.geo_scanner": "지질 스캐너",
    "block.advancedperipherals.inventory_manager": "인벤토리 관리자",
    "block.advancedperipherals.me_bridge": "ME 브리지",
    "block.advancedperipherals.nbt_storage": "NBT 저장소",
    "block.advancedperipherals.peripheral_casing": "주변 장치 케이스",
    "block.advancedperipherals.player_detector": "플레이어 감지기",
    "block.advancedperipherals.rs_bridge": "RS 브리지",
    "item.advancedperipherals.chunk_controller": "청크 제어기",
    "item.advancedperipherals.computer_tool": "컴퓨터 조정 도구",
    "item.advancedperipherals.end_automata_core": "엔드 오토마타 코어",
    "item.advancedperipherals.husbandry_automata_core": "축산 오토마타 코어",
    "item.advancedperipherals.overpowered_end_automata_core": "초강력 엔드 오토마타 코어",
    "item.advancedperipherals.overpowered_husbandry_automata_core": (
        "초강력 축산 오토마타 코어"
    ),
    "item.advancedperipherals.overpowered_weak_automata_core": "초강력 약한 오토마타 코어",
    "item.advancedperipherals.weak_automata_core": "약한 오토마타 코어",
    "item.advancedperipherals.tooltip.block_reader": (
        "&7블록의 NBT 데이터를 읽어 컴퓨터를 지원하지 않는 블록과도 상호 작용합니다."
    ),
    "item.advancedperipherals.tooltip.chat_box": (
        "&7게임 내 채팅을 읽고 메시지를 보낼 수 있습니다."
    ),
    "item.advancedperipherals.tooltip.chunk_controller": "&7청키 터틀의 제작 재료입니다.",
    "item.advancedperipherals.tooltip.colony_integrator": (
        "&7MineColonies와 연동해 식민지와 주민 데이터를 읽습니다."
    ),
    "item.advancedperipherals.tooltip.computer_tool": (
        "&7이 모드의 블록을 조정하려고 만든 도구입니다. 지금은 쓸모없는 파란 렌치일 뿐입니다."
    ),
    "item.advancedperipherals.tooltip.disabled": (
        "&c설정에서 비활성화된 아이템입니다. 제작할 수는 있지만 아무 기능도 하지 않습니다."
    ),
    "item.advancedperipherals.tooltip.end_automata_core": (
        "&7터틀이 월드와 기본적으로 상호 작용하고 같은 차원 안에서 순간이동하게 하는 업그레이드입니다."
    ),
    "item.advancedperipherals.tooltip.energy_detector": (
        "&7에너지 흐름을 감지하며 저항기 역할도 합니다."
    ),
    "item.advancedperipherals.tooltip.environment_detector": (
        "&7Minecraft 월드의 환경 정보를 감지하는 주변 장치입니다."
    ),
    "item.advancedperipherals.tooltip.geo_scanner": (
        "&7주변 지역을 스캔해 광석을 찾습니다."
    ),
    "item.advancedperipherals.tooltip.husbandry_automata_core": (
        "&7터틀이 동물과 기본·고급 상호 작용을 하게 하는 업그레이드입니다."
    ),
    "item.advancedperipherals.tooltip.inventory_manager": (
        "&7플레이어 인벤토리에서 지정한 아이템을 넣거나 꺼낼 수 있습니다."
    ),
    "item.advancedperipherals.tooltip.me_bridge": (
        "&7ME 브리지는 Applied Energistics 2와 연동해 아이템을 관리합니다."
    ),
    "item.advancedperipherals.tooltip.memory_card": (
        "&7인벤토리 관리자에서 사용할 플레이어 권한을 저장합니다."
    ),
    "item.advancedperipherals.tooltip.memory_card.bound": "&7연결된 플레이어: &b%s&7",
    "item.advancedperipherals.tooltip.nbt_storage": (
        "&7저장 디스크처럼 작동하며 NBT 기반 데이터를 저장합니다."
    ),
    "item.advancedperipherals.tooltip.overpowered_end_automata_core": (
        "&7엔드 오토마타 코어의 초강력 개량형입니다! 업그레이드가 매우 약하니 조심하세요."
    ),
    "item.advancedperipherals.tooltip.overpowered_husbandry_automata_core": (
        "&7축산 오토마타 코어의 초강력 개량형입니다! 업그레이드가 매우 약하니 조심하세요."
    ),
    "item.advancedperipherals.tooltip.overpowered_weak_automata_core": (
        "&7약한 오토마타 코어의 초강력 개량형입니다! 업그레이드가 매우 약하니 조심하세요."
    ),
    "item.advancedperipherals.tooltip.peripheral_casing": (
        "&7사랑받지 못한 빈 껍데기입니다. 제작 재료로 사용합니다."
    ),
    "item.advancedperipherals.tooltip.player_detector": (
        "&7플레이어와 상호 작용하는 주변 장치입니다. 스토커처럼 쓰지는 마세요."
    ),
    "item.advancedperipherals.tooltip.rs_bridge": (
        "&7RS 브리지는 Refined Storage와 연동해 아이템을 관리합니다."
    ),
    "item.advancedperipherals.tooltip.show_desc": "&b[&7%s&b] &7설명 보기",
    "item.advancedperipherals.tooltip.weak_automata_core": (
        "&7터틀을 더 유용하게 만드는 업그레이드입니다."
    ),
    "pocket.advancedperipherals.chatty_pocket": "수다쟁이",
    "pocket.advancedperipherals.colony_pocket": "식민지",
    "pocket.advancedperipherals.environment_pocket": "환경",
    "pocket.advancedperipherals.geoscanner_pocket": "지질 탐사",
    "pocket.advancedperipherals.player_pocket": "플레이어 감지",
    "text.advancedperipherals.added_player": "메모리 카드에 사용자를 등록했습니다.",
    "text.advancedperipherals.automata_core_feed_by_player": (
        "영혼에게 엔티티를 먹이려 하지만 맨몸으로는 할 수 없습니다. 더 기계적인 무언가라면 "
        "가능하지 않을까요?"
    ),
    "text.advancedperipherals.removed_player": "메모리 카드의 사용자 정보를 지웠습니다.",
    "turtle.advancedperipherals.chatty_turtle": "수다쟁이",
    "turtle.advancedperipherals.chunky_turtle": "청크",
    "turtle.advancedperipherals.compass_turtle": "나침반",
    "turtle.advancedperipherals.end_automata": "엔드 오토마타",
    "turtle.advancedperipherals.environment_turtle": "환경",
    "turtle.advancedperipherals.geoscanner_turtle": "지질 탐사",
    "turtle.advancedperipherals.husbandry_automata": "축산 오토마타",
    "turtle.advancedperipherals.overpowered_end_automata": "초강력 엔드 오토마타",
    "turtle.advancedperipherals.overpowered_husbandry_automata": "초강력 축산 오토마타",
    "turtle.advancedperipherals.overpowered_weak_automata": "초강력 약한 오토마타",
    "turtle.advancedperipherals.player_turtle": "플레이어 감지",
    "turtle.advancedperipherals.weak_automata": "약한 오토마타",
    "itemGroup.morered": "More Red",
}

COLORS = {
    "black": "검은색",
    "blue": "파란색",
    "brown": "갈색",
    "cyan": "청록색",
    "gray": "회색",
    "green": "초록색",
    "light_blue": "하늘색",
    "light_gray": "밝은 회색",
    "lime": "라임색",
    "magenta": "자홍색",
    "orange": "주황색",
    "pink": "분홍색",
    "purple": "보라색",
    "red": "빨간색",
    "white": "흰색",
    "yellow": "노란색",
}

MORE_RED_NAMES = {
    "and_2_gate": "2입력 AND 게이트",
    "and_gate": "AND 게이트",
    "bitwise_and_gate": "비트 단위 AND 게이트",
    "bitwise_diode": "비트 단위 다이오드",
    "bitwise_not_gate": "비트 단위 NOT 게이트",
    "bitwise_or_gate": "비트 단위 OR 게이트",
    "bitwise_xnor_gate": "비트 단위 XNOR 게이트",
    "bitwise_xor_gate": "비트 단위 XOR 게이트",
    "bundled_cable_post": "묶음 케이블 기둥",
    "bundled_cable_relay_plate": "묶음 케이블 중계판",
    "bundled_network_cable": "묶음 네트워크 케이블",
    "diode": "다이오드",
    "hexidecrubrometer": "헥시데크루브로미터",
    "latch": "래치",
    "multiplexer": "멀티플렉서",
    "nand_2_gate": "2입력 NAND 게이트",
    "nand_gate": "NAND 게이트",
    "nor_gate": "NOR 게이트",
    "not_gate": "NOT 게이트",
    "or_gate": "OR 게이트",
    "pulse_gate": "펄스 게이트",
    "red_alloy_wire": "적색 합금 와이어",
    "redwire_post": "레드와이어 기둥",
    "redwire_post_plate": "레드와이어 기둥판",
    "redwire_post_relay_plate": "레드와이어 기둥 중계판",
    "soldering_table": "납땜 작업대",
    "stone_plate": "석재판",
    "xnor_gate": "XNOR 게이트",
    "xor_gate": "XOR 게이트",
}

ALLOWED_EXACT_VALUES = {
    "HTTP",
    "CC: Tweaked",
    "Advanced Peripherals",
    "More Red",
    "N",
    "Y",
}

FORBIDDEN_ARTIFACTS = (
    "고급 주변장치",
    "주변기기",
    "주변 호출",
    "쓰레드",
    "거북이",
    "블랙리스트",
    "화이트리스트",
    "인게임",
    "브릿지",
)


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def request_candidate(source: str) -> str:
    return candidate_helper.request_translation_candidate(source)


def candidate() -> dict[str, object]:
    sources: dict[str, dict[str, object]] = {
        namespace: load_json(WORK_ROOT / namespace / "en_us.json")
        for namespace in NAMESPACES
    }
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requests = {
        source
        for english in sources.values()
        for key, source in english.items()
        if isinstance(source, str)
        and key not in KEY_OVERRIDES
        and source not in SOURCE_OVERRIDES
        and not family_goal.is_allowed_original(source)
        and not isinstance(cache.get(source), str)
    }
    failures: list[str] = []
    if requests:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_candidate, source): source
                for source in sorted(requests)
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    cache[source] = future.result()
                    completed += 1
                    if completed % 25 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{source}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("자동 번역 후보 생성 실패:\n" + "\n".join(failures))

    translated: dict[str, dict[str, str]] = {}
    for namespace, english in sources.items():
        translated[namespace] = {}
        for key, source in english.items():
            if not isinstance(source, str):
                raise TypeError(f"문자열이 아닌 언어 값: {namespace}:{key}")
            if key in KEY_OVERRIDES:
                value = KEY_OVERRIDES[key]
            elif source in SOURCE_OVERRIDES:
                value = SOURCE_OVERRIDES[source]
            elif family_goal.is_allowed_original(source):
                value = source
            else:
                value = str(cache[source])
            translated[namespace][key] = value
    write_json(CANDIDATE_FILE, translated)
    report = {
        "keys": sum(len(english) for english in sources.values()),
        "candidate_keys": sum(len(values) for values in translated.values()),
        "review_scope": "all_current_english_keys_including_bundled_korean",
        "review_status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "auto_candidate_report.json", report)
    return report


def structured_name(namespace: str, key: str, value: str) -> str:
    if namespace != "morered":
        return value
    path = key.removeprefix("block.morered.").removeprefix("item.morered.")
    if path.endswith("_network_cable"):
        color = path.removesuffix("_network_cable")
        if color in COLORS:
            return f"{COLORS[color]} 네트워크 케이블"
    if path in MORE_RED_NAMES:
        return MORE_RED_NAMES[path]
    if path == "bundled_cable_spool":
        return "묶음 케이블 두루마리"
    if path == "red_alloy_ingot":
        return "적색 합금 주괴"
    if path == "redwire_spool":
        return "레드와이어 두루마리"
    if key in {"emi.category.morered.soldering", "gui.morered.category.soldering"}:
        return "납땜"
    return value


def reviewed_value(namespace: str, key: str, source: str, candidate_value: str) -> str:
    value = SOURCE_OVERRIDES.get(source, candidate_value)
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    value = KEY_OVERRIDES.get(key, value)
    value = structured_name(namespace, key, value)
    value = re.sub(r"[ \t]+([,.!?])", r"\1", value)
    value = re.sub(r" {2,}", " ", value)
    if key.startswith(("item.", "block.", "entity.")):
        value = value.rstrip(".")
    return value


def normalize() -> dict[str, object]:
    candidates = load_json(CANDIDATE_FILE)
    changed = 0
    unresolved: list[str] = []
    reviewed = 0
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        namespace_candidates = candidates.get(namespace)
        if not isinstance(namespace_candidates, dict):
            raise TypeError(f"후보 네임스페이스가 없습니다: {namespace}")
        rebuilt: dict[str, str] = {}
        for key, source in english.items():
            candidate_value = namespace_candidates.get(key)
            if not isinstance(source, str) or not isinstance(candidate_value, str):
                raise TypeError(f"문자열이 아닌 언어 값: {namespace}:{key}")
            translated = reviewed_value(namespace, key, source, candidate_value)
            errors = family_goal.validate_family_value(FAMILY, key, source, translated)
            if errors:
                raise ValueError("; ".join(errors))
            rebuilt[key] = translated
            reviewed += 1
            if korean.get(key) != translated:
                changed += 1
            if (
                source == translated
                and source not in ALLOWED_EXACT_VALUES
                and not family_goal.is_allowed_original(source)
            ):
                unresolved.append(f"{namespace}:{key}")
        write_json(WORK_ROOT / namespace / "ko_kr.json", rebuilt)
    report = {
        "keys_reviewed": reviewed,
        "bundled_korean_reused_without_review": 0,
        "changed": changed,
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved[:30],
        "review_status": "all_current_english_keys_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    untranslated: list[str] = []
    reviewed = 0
    for namespace in NAMESPACES:
        english = load_json(WORK_ROOT / namespace / "en_us.json")
        korean = load_json(WORK_ROOT / namespace / "ko_kr.json")
        if list(english) != list(korean):
            errors.append(f"영어와 한국어의 키 또는 순서가 다릅니다: {namespace}")
        for key, source in english.items():
            target = korean.get(key)
            reviewed += 1
            if not isinstance(source, str) or not isinstance(target, str):
                errors.append(f"문자열이 아닌 값: {namespace}:{key}")
                continue
            errors.extend(
                family_goal.validate_family_value(FAMILY, key, source, target)
            )
            artifacts = [word for word in FORBIDDEN_ARTIFACTS if word in target]
            if artifacts:
                errors.append(f"용어 미정리: {namespace}:{key}: {', '.join(artifacts)}")
            if (
                source == target
                and source not in ALLOWED_EXACT_VALUES
                and not family_goal.is_allowed_original(source)
            ):
                untranslated.append(f"{namespace}:{key}")
    if untranslated:
        errors.append(f"미번역 키: {untranslated[:30]}")
    report = {
        "keys_reviewed": reviewed,
        "bundled_korean_reused_without_review": 0,
        "untranslated": len(untranslated),
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "specialized_validation.json", report)
    return report, 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("candidate", "normalize", "verify"))
    args = parser.parse_args()
    resolve_source_root()
    if args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "normalize":
        result = normalize()
        status = 0
    else:
        result, status = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
