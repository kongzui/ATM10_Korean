#!/usr/bin/env python3
"""CC: Tweaked CraftOS 도움말을 코드 표기를 보존해 번역하고 검증한다."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from pathlib import Path
from zipfile import ZipFile

import actually_additions_family as candidate_helper
from local_paths import PROJECT_ROOT, resolve_source_root
from version_context import active_output_root


WORK_ROOT = PROJECT_ROOT / "working/cc_tweaked/help"
ENGLISH_ROOT = WORK_ROOT / "en_us"
KOREAN_ROOT = WORK_ROOT / "ko_kr"
OUTPUT_ROOT = active_output_root() / "overrides/kubejs/data/computercraft/lua/rom/help"
CACHE_FILE = PROJECT_ROOT / "temp/cc_tweaked_help_candidate_cache.json"
JAR_PREFIX = "cc-tweaked-1.21.1-forge-1.120.0"
SOURCE_PREFIX = "data/computercraft/lua/rom/help/"
EXCLUDED_FILES = {
    "changelog.md": "현재 기능 설명이 아닌 과거 버전 변경 기록",
    "credits.md": "번역하면 안 되는 기여자 이름과 원문 인용 중심의 크레디트",
}
TOKEN_PATTERN = re.compile(
    r"https?://[^\s),]+|`[^`]+`|\"[^\"]*\"|'[A-Za-z0-9_./:-]+'|"
    r"(?<![\w])(?:[A-Za-z_][\w]*[.:])+[A-Za-z_][\w]*(?:\([^)]*\))?|"
    r"(?<![\w])[A-Za-z_][\w]*\([^)]*\)|--[\w-]+|Ctrl\+[A-Z]|"
    r"(?<![\w])[A-Za-z_][\w]*:[A-Za-z_][\w]*(?![\w])"
)
PURE_CODE = re.compile(
    r"^(?:[A-Za-z_][\w]*(?:[.:][A-Za-z_][\w]*)+\([^)]*\)|"
    r"[A-Za-z_][\w]*(?:[.:][A-Za-z_][\w]*)+|"
    r"[A-Za-z_][\w]*\([^)]*\))$"
)
CODE_WITH_COMMENT = re.compile(
    r"^(?:[A-Za-z_][\w]*(?:[.:][A-Za-z_][\w]*)+\([^)]*\)|"
    r"[A-Za-z_][\w]*\([^)]*\))\s+--"
)
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")

TERM_REPLACEMENTS = (
    ("컴퓨터크래프트", "CC: Tweaked"),
    ("Crafty Turtles", "제작용 터틀"),
    ("Crafty Turtle", "제작용 터틀"),
    ("Turtles", "터틀"),
    ("Turtle", "터틀"),
    ("Pocket은", "pocket은"),
    ("포켓 API", "pocket API"),
    ("Rednet API", "rednet API"),
    ("Redstone API", "레드스톤 API"),
    ("거북이", "터틀"),
    ("터틀가", "터틀이"),
    ("터틀는", "터틀은"),
    ("주변기기", "주변 장치"),
    ("주변 장치 장치", "주변 장치"),
    ("주변 API", "주변 장치 API"),
    ("파일시스템", "파일 시스템"),
    ("쉘", "셸"),
    ("루아", "Lua"),
    ("메소드", "메서드"),
    ("라벨", "레이블"),
    ("에 의해 노출되는 방법:", "가 제공하는 메서드:"),
    ("에 의해 발생되는 이벤트:", "에서 발생하는 이벤트:"),
    ("에 의해 발생하는 이벤트:", "에서 발생하는 이벤트:"),
    ("모뎀가 제공하는", "모뎀이 제공하는"),
    ("API의 기능:", "API의 함수:"),
    ("프로그램이에요", "프로그램입니다"),
    ("사용하십시오", "사용하세요"),
    ("실행하십시오", "실행하세요"),
    ("주의하십시오", "주의하세요"),
    ("마우스 오른쪽 버튼", "우클릭"),
    ("마우스 왼쪽 버튼", "좌클릭"),
)

ALLOWED_PROSE_EXACT = {
    "Lua",
    "HTTP",
    "API",
    "APIs",
    "GPS",
    "WebSocket",
}

LINE_OVERRIDES = {
    "The function os.pullEvent() will yield the program until a system event occurs. The first "
    "return value is the event name, followed by any arguments.": (
        "os.pullEvent() 함수는 시스템 이벤트가 발생할 때까지 프로그램 실행을 일시 중지합니다. "
        "첫 번째 반환값은 이벤트 이름이고 그 뒤에 이벤트 인수가 옵니다."
    ),
    "Some events which can occur are:": "발생할 수 있는 주요 이벤트:",
    '"char" when text is typed on the keyboard. Argument is the character typed.': (
        '"char": 키보드로 문자를 입력할 때 발생합니다. 인수는 입력한 문자입니다.'
    ),
    '"key" when a key is pressed on the keyboard. Arguments are the keycode and whether the key is '
    "a repeat. Compare the keycode to the values in keys API to see which key was pressed.": (
        '"key": 키보드의 키를 누를 때 발생합니다. 인수는 키 코드와 반복 입력 여부입니다. '
        "keys API의 값과 비교하면 어떤 키인지 알 수 있습니다."
    ),
    '"key_up" when a key is released on the keyboard. Argument is the numerical keycode. Compare '
    "to the values in keys API to see which key was released.": (
        '"key_up": 키보드의 키를 놓을 때 발생합니다. 인수는 숫자 키 코드입니다. keys API의 '
        "값과 비교하면 어떤 키인지 알 수 있습니다."
    ),
    '"paste" when text is pasted from the users keyboard. Argument is the line of text pasted.': (
        '"paste": 사용자가 텍스트를 붙여넣을 때 발생합니다. 인수는 붙여넣은 한 줄입니다.'
    ),
    "Events only on advanced computers:": "고급 컴퓨터에서만 발생하는 이벤트:",
    '"mouse_click" when a user clicks the mouse. Arguments are button, xPos, yPos.': (
        '"mouse_click": 마우스를 클릭할 때 발생합니다. 인수는 button, xPos, yPos입니다.'
    ),
    '"mouse_drag" when a user moves the mouse when held. Arguments are button, xPos, yPos.': (
        '"mouse_drag": 버튼을 누른 채 마우스를 움직일 때 발생합니다. 인수는 button, xPos, yPos입니다.'
    ),
    '"mouse_up" when a user releases the mouse button. Arguments are button, xPos, yPos.': (
        '"mouse_up": 마우스 버튼을 놓을 때 발생합니다. 인수는 button, xPos, yPos입니다.'
    ),
    '"mouse_scroll" when a user uses the scrollwheel on the mouse. Arguments are direction, xPos, '
    "yPos.": (
        '"mouse_scroll": 마우스 휠을 돌릴 때 발생합니다. 인수는 direction, xPos, yPos입니다.'
    ),
    "Other APIs and peripherals will emit their own events. See their respective help pages for "
    "details.": "다른 API와 주변 장치도 고유한 이벤트를 냅니다. 자세한 내용은 각 도움말을 확인하세요.",
    "excavate is a program for Mining Turtles. When excavate is run, the turtle will mine a "
    "rectangular shaft into the ground, collecting blocks as it goes, and return to the surface "
    "once bedrock is hit.": (
        "excavate는 채굴 터틀용 프로그램입니다. 실행하면 터틀이 직사각형 수직 갱도를 파며 "
        "블록을 수집하고, 기반암에 닿으면 지상으로 돌아옵니다."
    ),
    "go is a program for Turtles, used to control the turtle without programming. It accepts one "
    "or more commands as a direction followed by a distance.": (
        "go는 프로그래밍 없이 터틀을 움직이는 프로그램입니다. 방향과 거리로 이루어진 명령을 "
        "하나 이상 받습니다."
    ),
    "turn is a program for Turtles, used to turn the turtle around without programming. It accepts "
    'one or more commands as a direction and a number of turns. The "go" program can also be used '
    "for turning.": (
        "turn은 프로그래밍 없이 터틀을 회전시키는 프로그램입니다. 방향과 회전 횟수로 이루어진 "
        '명령을 하나 이상 받습니다. 회전에는 "go" 프로그램도 사용할 수 있습니다.'
    ),
    "The locate function will send a signal to nearby gps servers, and wait for responses before "
    "the timeout. If it receives enough responses to determine this computers position then x, y "
    "and z co-ordinates will be returned, otherwise it will return nil. If GPS hosts do not have "
    "their positions configured correctly, results will be inaccurate.": (
        "locate 함수는 주변 GPS 서버에 신호를 보내고 제한 시간까지 응답을 기다립니다. 컴퓨터 "
        "위치를 계산할 만큼 응답을 받으면 x, y, z 좌표를 반환하고, 부족하면 nil을 반환합니다. "
        "GPS 호스트 위치가 잘못 설정되어 있으면 결과도 부정확합니다."
    ),
    'A period of time after a http.request() call is made, a "http_success" or "http_failure" event '
    "will be raised. Arguments are the url and a file handle if successful. Arguments are nil, an "
    "error message, and (optionally) a file handle if the request failed. http.get() and "
    "http.post() block until this event fires instead.": (
        'http.request()를 호출하면 잠시 뒤 "http_success" 또는 "http_failure" 이벤트가 발생합니다. '
        "성공 시 URL과 파일 핸들을, 실패 시 URL·오류 메시지와 선택적으로 파일 핸들을 인수로 "
        "받습니다. http.get()과 http.post()는 이 이벤트가 발생할 때까지 기다립니다."
    ),
    "Rednet is not the only way to use modems for networking. Interfacing with the modem directly "
    'using the peripheral API and listening for the "modem_message" event allows for lower level '
    "control, at the expense of powerful high level networking features.": (
        "rednet만이 모뎀을 이용하는 방법은 아닙니다. 주변 장치 API로 모뎀을 직접 제어하고 "
        '"modem_message" 이벤트를 받으면 고급 네트워크 기능을 포기하는 대신 더 낮은 수준까지 '
        "제어할 수 있습니다."
    ),
    '"term_resize", when the size of a terminal changes. This can happen in multitasking '
    'environments, or when the terminal out is being redirected by the "monitor" program.': (
        '"term_resize": 터미널 크기가 바뀔 때 발생합니다. 멀티태스킹 환경이나 "monitor" '
        "프로그램으로 출력을 리디렉션했을 때 발생할 수 있습니다."
    ),
    "paint is a program for creating images on Advanced Computers. Select colors from the color "
    "pallette on the right, and click on the canvas to draw. Press Ctrl to access the menu and save "
    "your pictures.": (
        "paint는 고급 컴퓨터에서 그림을 만드는 프로그램입니다. 오른쪽 팔레트에서 색을 고르고 "
        "캔버스를 클릭해 그리세요. Ctrl을 누르면 메뉴를 열어 그림을 저장할 수 있습니다."
    ),
    "When equipping upgrades, it will search your inventory for a suitable upgrade, starting in the "
    "selected slot. If one cannot be found then it will check your offhand.": (
        "업그레이드를 장착할 때 현재 선택한 슬롯부터 인벤토리에서 알맞은 업그레이드를 찾습니다. "
        "없으면 보조 손을 확인합니다."
    ),
    "If no filename is specified wget will try to determine the filename from the URL by stripping "
    "any anchors, parameters and trailing slashes and then taking everything remaining after the "
    "last slash.": (
        "파일 이름을 지정하지 않으면 wget은 URL의 앵커, 매개변수, 끝 슬래시를 제거한 뒤 마지막 "
        "슬래시 다음 부분을 파일 이름으로 사용합니다."
    ),
    "disk is an api for interacting with disk drives. The following functions are available:": (
        "disk는 디스크 드라이브와 상호 작용하는 API입니다. 사용할 수 있는 함수:"
    ),
    "Functions in the bit API:": "bit API의 함수:",
    "bit.bnot(n)       -- bitwise not (~n)": "bit.bnot(n)       -- 비트 단위 NOT(~n)",
    "bit.band(m, n)    -- bitwise and (m & n)": "bit.band(m, n)    -- 비트 단위 AND(m & n)",
    "bit.bor(m, n)     -- bitwise or (m | n)": "bit.bor(m, n)     -- 비트 단위 OR(m | n)",
    "bit.bxor(m, n)    -- bitwise xor (m ^ n)": "bit.bxor(m, n)    -- 비트 단위 XOR(m ^ n)",
    "bit.brshift(n, bits) -- right shift (n >> bits)": (
        "bit.brshift(n, bits) -- 오른쪽 시프트(n >> bits)"
    ),
    "bit.blshift(n, bits) -- left shift  (n << bits)": (
        "bit.blshift(n, bits) -- 왼쪽 시프트(n << bits)"
    ),
    '"refuel" will refuel with at most one fuel item': (
        '"refuel"은 연료 아이템을 최대 1개 사용해 연료를 보급합니다.'
    ),
    '"refuel 10" will refuel with at most 10 fuel items': (
        '"refuel 10"은 연료 아이템을 최대 10개 사용해 연료를 보급합니다.'
    ),
    '"refuel all" will refuel with as many fuel items as possible': (
        '"refuel all"은 가능한 만큼 연료 아이템을 사용해 연료를 보급합니다.'
    ),
    '"wget http://pastebin.com/raw/CxaWmPrX test" will download the file from the URL '
    'http://pastebin.com/raw/CxaWmPrX, and save it as "test".': (
        '"wget http://pastebin.com/raw/CxaWmPrX test"는 URL '
        'http://pastebin.com/raw/CxaWmPrX에서 파일을 받아 "test"로 저장합니다.'
    ),
    "alias assigns shell commands to run other programs.": (
        "alias는 다른 프로그램을 실행할 셸 명령 별칭을 지정합니다."
    ),
    "Functions in the bit manipulation API (NOTE: This API will be removed in a future version. "
    "Use bit32 instead):": (
        "비트 연산 API의 함수(참고: 이 API는 향후 버전에서 제거됩니다. 대신 bit32를 사용하세요):"
    ),
    "Functions in the disk API. These functions are for interacting with disk drives:": (
        "디스크 드라이브를 제어하는 disk API의 함수:"
    ),
    "Events fired by the disk API:": "disk API에서 발생하는 이벤트:",
    '"disk" when a disk or other item is inserted into a disk drive. Argument is the name of the '
    "drive": '"disk": 디스크나 다른 아이템을 드라이브에 넣을 때 발생합니다. 인수는 드라이브 이름입니다.',
    '"disk_eject" when a disk is removed from a disk drive. Argument is the name of the drive': (
        '"disk_eject": 드라이브에서 디스크를 꺼낼 때 발생합니다. 인수는 드라이브 이름입니다.'
    ),
    "clear clears the screen and/or resets the palette.": (
        "clear는 화면을 지우거나 팔레트를 초기화합니다."
    ),
    "craft is a program for Crafty Turtles. Craft will craft a stack of items using the current "
    "inventory.": (
        "craft는 제작용 터틀의 프로그램입니다. 현재 인벤토리의 재료로 아이템을 제작합니다."
    ),
    "adventure is a text adventure game for CraftOS. To navigate around the world of adventure, "
    'type simple instructions to the interpreter, for example: "go north", "punch tree", "craft '
    'planks", "mine coal with pickaxe", "hit creeper with sword"': (
        "adventure는 CraftOS용 텍스트 어드벤처 게임입니다. 세계를 탐험하려면 인터프리터에 "
        '"go north", "punch tree", "craft planks", "mine coal with pickaxe", "hit creeper with '
        'sword" 같은 간단한 명령을 입력하세요.'
    ),
    "dance is a program for Turtles. Turtles love to get funky.": (
        "dance는 터틀용 프로그램입니다. 터틀도 신나게 춤출 때가 있습니다."
    ),
    "Mostly harmless.": "대체로 무해합니다.",
    "eject ejects the contents of an attached disk drive.": (
        "eject는 연결된 디스크 드라이브의 디스크를 꺼냅니다."
    ),
    "equip is a program for Turtles and Pocket Computer. equip will equip an item from the Turtle's "
    "inventory for use as a tool of peripheral. On a Pocket Computer you don't need to write a side.": (
        "equip은 터틀과 포켓 컴퓨터용 프로그램입니다. 터틀에서는 인벤토리의 아이템을 도구나 "
        "주변 장치로 장착합니다. 포켓 컴퓨터에서는 장착할 면을 지정하지 않아도 됩니다."
    ),
    "exit will exit the current shell.": "exit는 현재 셸을 종료합니다.",
    '"From Russia with Fun" comes a fun, new, suspiciously-familiar falling block game for CraftOS. '
    "Only on Pocket Computers!": (
        '"From Russia with Fun"이 선보이는 익숙한 낙하 블록 게임입니다. CraftOS 포켓 컴퓨터에서만 '
        "플레이할 수 있습니다!"
    ),
    '"excavate 3" will mine a 3x3 shaft.': (
        '"excavate 3" 명령은 3×3 크기의 수직 갱도를 팝니다.'
    ),
    '"go forward" moves the turtle 1 space forward.': (
        '"go forward" 명령은 터틀을 앞으로 1블록 이동시킵니다.'
    ),
    '"go forward 3" moves the turtle 3 spaces forward.': (
        '"go forward 3" 명령은 터틀을 앞으로 3블록 이동시킵니다.'
    ),
    '"go forward 3 up left 2" moves the turtle 3 spaces forward, 1 spaces up, then left 180 '
    "degrees.": (
        '"go forward 3 up left 2" 명령은 터틀을 앞으로 3블록, 위로 1블록 이동시킨 뒤 '
        "왼쪽으로 180도 회전시킵니다."
    ),
    "gps can be used to host a GPS server, or to determine a position using trilateration.": (
        "gps는 GPS 서버를 열거나 삼변측량으로 현재 위치를 찾는 프로그램입니다."
    ),
    "Take care when manually entering host positions. If the positions entered into multiple GPS "
    "hosts": "GPS 호스트 좌표를 직접 입력할 때는 주의하세요. 여러 GPS 호스트에 입력한 좌표가",
    "are not consistent, the results of locate calls will be incorrect.": (
        "서로 일치하지 않으면 locate 호출 결과가 잘못됩니다."
    ),
    "id prints the unique identifier of this computer, or a Disk in an attached Disk Drive.": (
        "id는 이 컴퓨터 또는 연결된 디스크의 고유 ID를 출력합니다."
    ),
    'hello prints the text "Hello World!" to the screen.': (
        'hello는 화면에 "Hello World!"를 출력합니다.'
    ),
    'ls will list all the directories and files in the current location. Use "type" to find out if '
    "an item is a file or a directory.": (
        "ls는 현재 위치의 모든 디렉터리와 파일을 나열합니다. 항목이 파일인지 디렉터리인지 "
        '확인하려면 "type"을 사용하세요.'
    ),
    "lua is an interactive prompt for the lua programming language. It's a useful tool for learning "
    "the language.": (
        "lua는 Lua 프로그래밍 언어를 직접 입력해 실행하는 대화형 프롬프트입니다. 언어를 익힐 때 "
        "유용합니다."
    ),
    "math is a standard Lua5.1 API.": "math는 표준 Lua 5.1 API입니다.",
    "string is a standard Lua5.1 API.": "string은 표준 Lua 5.1 API입니다.",
    "table is a standard Lua5.1 API.": "table은 표준 Lua 5.1 API입니다.",
    "coroutine is a standard Lua5.1 API.": "coroutine은 표준 Lua 5.1 API입니다.",
    "monitor will connect to an attached Monitor peripheral, and run a program on its display.": (
        "monitor는 연결된 모니터 주변 장치의 화면에서 프로그램을 실행합니다."
    ),
    '"modem_message" when a message is received on an open channel. Arguments are name, channel, '
    "replyChannel, message, distance": (
        '"modem_message": 열린 채널에서 메시지를 받을 때 발생합니다. 인수는 name, channel, '
        "replyChannel, message, distance입니다."
    ),
    '"alarm" when a time passed to os.setAlarm() is reached. Argument is the token returned by '
    "os.setAlarm().": (
        '"alarm": os.setAlarm()에 지정한 시각이 되면 발생합니다. 인수는 os.setAlarm()이 반환한 '
        "토큰입니다."
    ),
    "Functions in the Paint Utilities API:": "paintutils API의 함수:",
    "These methods provide an easy way to run multiple lua functions simultaneously.": (
        "이 함수들은 여러 Lua 함수를 동시에 실행하는 간단한 방법을 제공합니다."
    ),
    "pastebin is a program for uploading files to and downloading files from pastebin.com. This is "
    "useful for sharing programs with other players.": (
        "pastebin은 pastebin.com에 파일을 올리거나 내려받는 프로그램입니다. 다른 플레이어와 "
        "프로그램을 공유할 때 유용합니다."
    ),
    '"pastebin get xq5gc7LB foo" will download the file from the URL '
    'http://pastebin.com/xq5gc7LB, and save it as "foo".': (
        '"pastebin get xq5gc7LB foo" 명령은 URL http://pastebin.com/xq5gc7LB에서 파일을 '
        '받아 "foo"로 저장합니다.'
    ),
    '"pastebin run CxaWmPrX" will download the file from the URL '
    "http://pastebin.com/CxaWmPrX, and immediately run it.": (
        '"pastebin run CxaWmPrX" 명령은 URL http://pastebin.com/CxaWmPrX에서 파일을 받아 '
        "즉시 실행합니다."
    ),
    "Peripherals are external devices which CraftOS Computers and Turtles can interact with using "
    "the peripheral API.": (
        "주변 장치는 CraftOS 컴퓨터와 터틀이 peripheral API로 제어할 수 있는 외부 장치입니다."
    ),
    "To learn the lua programming language, visit http://lua-users.org/wiki/TutorialDirectory.": (
        "Lua 프로그래밍 언어를 배우려면 http://lua-users.org/wiki/TutorialDirectory를 참고하세요."
    ),
    'To create programs, use "edit" to create files, then type their names in the shell to run '
    'them. If you name a program "startup" and place it in the root or on a disk drive, it will run '
    "automatically when the computer starts.": (
        '프로그램을 만들려면 "edit"로 파일을 만든 뒤 셸에 파일 이름을 입력해 실행하세요. '
        '프로그램 이름을 "startup"으로 지정하고 루트나 디스크 드라이브에 두면 컴퓨터를 켤 때 '
        "자동으로 실행됩니다."
    ),
    "programs lists all the programs on the rom of the computer.": (
        "programs는 컴퓨터 ROM에 있는 모든 프로그램을 나열합니다."
    ),
    "reboot will turn the computer off and on again.": "reboot는 컴퓨터를 껐다가 다시 켭니다.",
    "Redirection ComputerCraft Edition is the CraftOS version of a fun new puzzle game by Dan200, "
    "the author of ComputerCraft.": (
        "Redirection ComputerCraft Edition은 ComputerCraft 제작자 Dan200의 퍼즐 게임을 CraftOS로 "
        "옮긴 버전입니다."
    ),
    "refuel is a program for Turtles. Refuel will consume items from the inventory as fuel for "
    "turtle.": "refuel은 터틀용 프로그램입니다. 인벤토리의 아이템을 터틀 연료로 사용합니다.",
    "repeat is a program for repeating rednet messages across long distances. To use, connect 2 or "
    'more modems to a computer and run the "repeat" program; from then on, any rednet message sent '
    "from any computer in wireless range or connected by networking cable to either of the modems "
    "will be repeated to those on the other side.": (
        "repeat는 rednet 메시지를 장거리로 중계하는 프로그램입니다. 컴퓨터에 모뎀을 2개 이상 "
        '연결하고 "repeat"를 실행하면, 한쪽 모뎀의 무선 범위나 네트워크 케이블을 통해 들어온 '
        "rednet 메시지를 다른 쪽으로 중계합니다."
    ),
    "The set program can be used to inspect and change system settings.": (
        "set은 시스템 설정을 확인하고 변경하는 프로그램입니다."
    ),
    "shell.allow_disk_startup - if a Disk Drive with a Disk inside that has a 'startup' script is "
    "attached to a computer, this setting allows to automatically run that script when the computer "
    "starts.": (
        "shell.allow_disk_startup - 'startup' 스크립트가 든 디스크 드라이브를 컴퓨터에 연결했을 "
        "때, 컴퓨터가 시작되면 해당 스크립트를 자동으로 실행할지 설정합니다."
    ),
    "shell.allow_startup - if there is a 'startup' script in a computer's root, this setting allow "
    "to automatically run that script when the computer runs.": (
        "shell.allow_startup - 컴퓨터 루트에 'startup' 스크립트가 있을 때 컴퓨터가 시작되면 해당 "
        "스크립트를 자동으로 실행할지 설정합니다."
    ),
    "list.show_hidden - determines, whether the List program will list hidden files or not.": (
        "list.show_hidden - list 프로그램이 숨김 파일을 표시할지 설정합니다."
    ),
    "shell is the toplevel program which interprets commands and runs program.": (
        "shell은 명령을 해석하고 프로그램을 실행하는 최상위 프로그램입니다."
    ),
    "shutdown will turn off the computer.": "shutdown은 컴퓨터를 끕니다.",
    "time prints the current time of day.": "time은 현재 시각을 출력합니다.",
    "Methods exposed by the Speaker:": "스피커가 제공하는 메서드:",
    'Instruments are as follows: "harp", "bass", "snare", "hat", and "basedrum" with the '
    'addition of "flute", "bell", "chime", and "guitar" in Minecraft versions 1.12 and above.': (
        '악기 종류는 "harp", "bass", "snare", "hat", "basedrum"이며, Minecraft 1.12 이상에서는 '
        '"flute", "bell", "chime", "guitar"도 사용할 수 있습니다.'
    ),
    "tunnel is a program for Mining Turtles. Tunnel will mine a 3x2 tunnel of the depth specified.": (
        "tunnel은 채굴 터틀용 프로그램입니다. 지정한 길이만큼 3×2 크기의 터널을 팝니다."
    ),
    '"tunnel 20" will tunnel a tunnel 20 blocks long.': (
        '"tunnel 20" 명령은 20블록 길이의 터널을 팝니다.'
    ),
    "turtle is an api available on Turtles, which controls their movement.": (
        "turtle은 터틀의 동작을 제어하는 API입니다."
    ),
    '"redstone pulse front 10 1" emits 10 one second redstone pulses on the front redstone output.': (
        '"redstone pulse front 10 1" 명령은 앞쪽 레드스톤 출력으로 1초짜리 펄스를 10회 보냅니다.'
    ),
    '"turtle_inventory" when any of the items in the inventory are changed. Use comparison '
    "operations to inspect the changes.": (
        '"turtle_inventory": 인벤토리의 아이템이 바뀔 때 발생합니다. 비교 함수를 사용해 변경 '
        "사항을 확인하세요."
    ),
    "unequip is a program for Turtles and Pocket Computers. unequip will remove tools of peripherals "
    "from the specified side of the turtle. On a Pocket Computer you don't need to write a side.": (
        "unequip은 터틀과 포켓 컴퓨터용 프로그램입니다. 터틀에서는 지정한 면의 도구나 주변 "
        "장치를 해제합니다. 포켓 컴퓨터에서는 면을 지정하지 않아도 됩니다."
    ),
    "New features in CC: Tweaked 1.120.0": "CC: Tweaked 1.120.0의 새로운 기능",
    "Methods exposed by Workbenches:": "작업대가 제공하는 메서드:",
    'Workbenches are peripheral devices found on Crafty Turtles running CraftOS. Type "help '
    'peripheral" to learn about using the Peripheral API to connect with peripherals. When a '
    'workbench is attached to a turtle, peripheral.getType() will return "workbench".': (
        '작업대는 제작용 터틀에 달린 주변 장치입니다. 주변 장치 API 사용법은 "help peripheral"을 '
        '입력해 확인하세요. 터틀에 작업대가 달려 있으면 peripheral.getType()은 "workbench"를 '
        "반환합니다."
    ),
}

CODE_EXACT_LINES = {
    "c = colors.combine( colors.red, colors.blue )",
    "c = colors.combine( c, colors.green )",
    "c = colors.subtract( c, colors.blue )",
    'c = rs.getBundledInput( "right" )',
    "colors.white, colors.orange, colors.magenta, colors.lightBlue, colors.yellow, "
    "colors.lime, colors.pink, colors.gray, colors.lightGray, colors.cyan, colors.purple, "
    "colors.blue, colors.brown, colors.green, colors.red, colors.black.",
    "colours.white, colours.orange, colours.magenta, colours.lightBlue, colours.yellow, "
    "colours.lime, colours.pink, colours.grey, colours.lightGrey, colours.cyan, "
    "colours.purple, colours.blue, colours.brown, colours.green, colours.red, colours.black.",
    '"exec say Hello World"',
    '"exec setblock ~0 ~1 ~0 minecraft:dirt"',
    "vector:length()",
    "vector:normalize()",
    "vector:round()",
    "vector:tostring()",
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 최상위 값이 객체가 아닙니다: {path}")
    return value


def find_jar() -> Path:
    root = resolve_source_root()
    matches = sorted(
        path
        for path in (root / "mods").glob("*.jar")
        if path.name.lower().startswith(JAR_PREFIX.lower())
    )
    if len(matches) != 1:
        raise RuntimeError(f"CC: Tweaked JAR을 확정하지 못했습니다: {matches}")
    return matches[0]


def prepare(force: bool) -> dict[str, object]:
    jar = find_jar()
    extracted = 0
    translated = 0
    with ZipFile(jar) as archive:
        for name in sorted(archive.namelist()):
            if not name.startswith(SOURCE_PREFIX) or name.endswith("/"):
                continue
            relative = name.removeprefix(SOURCE_PREFIX)
            target = ENGLISH_ROOT / relative
            if target.exists() and not force:
                raise FileExistsError(f"기존 작업본을 덮어쓰지 않습니다: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(archive.read(name).decode("utf-8-sig"), encoding="utf-8")
            extracted += 1
            if relative not in EXCLUDED_FILES:
                translated += 1
    report = {
        "jar": jar.name,
        "help_files_found": extracted,
        "operational_help_translation_targets": translated,
        "excluded_non_operational_files": EXCLUDED_FILES,
    }
    write_json(WORK_ROOT / "scope.json", report)
    return report


def translatable_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped in ALLOWED_PROSE_EXACT:
        return False
    if stripped in CODE_EXACT_LINES:
        return False
    if stripped in {"end", "else", "do", "then", "repeat", "until"}:
        return False
    if stripped.startswith("--") or CODE_WITH_COMMENT.match(stripped):
        return False
    if re.match(r"^(?:local\s|if\s|for\s|while\s|return\s)", stripped):
        return False
    if re.match(r"^[A-Za-z_]\w*\s*=\s*", stripped):
        return False
    if PURE_CODE.fullmatch(stripped):
        return False
    return bool(LATIN_WORD.search(stripped))


def protect(line: str) -> tuple[str, list[str]]:
    tokens: list[str] = []

    def replace(match: re.Match[str]) -> str:
        tokens.append(match.group(0))
        return f"XQZ{len(tokens) - 1}ZQX"

    return TOKEN_PATTERN.sub(replace, line), tokens


def restore(value: str, tokens: list[str]) -> str:
    for index, token in enumerate(tokens):
        marker = f"XQZ{index}ZQX"
        if marker not in value:
            raise ValueError(f"도움말 코드 토큰이 사라졌습니다: {marker}: {value}")
        value = value.replace(marker, token)
    return value


def request_line(line: str) -> str:
    leading = line[: len(line) - len(line.lstrip())]
    protected, tokens = protect(line.strip())
    translated = candidate_helper.request_translation_candidate(protected)
    return leading + restore(translated, tokens)


def candidate() -> dict[str, object]:
    cache = load_json(CACHE_FILE) if CACHE_FILE.is_file() else {}
    requested = {
        line
        for path in sorted(ENGLISH_ROOT.rglob("*"))
        if path.is_file()
        and path.relative_to(ENGLISH_ROOT).as_posix() not in EXCLUDED_FILES
        for line in path.read_text(encoding="utf-8").splitlines()
        if translatable_line(line) and not isinstance(cache.get(line), str)
    }
    failures: list[str] = []
    if requested:
        completed = 0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_line, line): line for line in sorted(requested)
            }
            for future in as_completed(futures):
                line = futures[future]
                try:
                    cache[line] = future.result()
                    completed += 1
                    if completed % 25 == 0:
                        write_json(CACHE_FILE, cache)
                except Exception as exc:  # pragma: no cover - 외부 후보 서비스
                    failures.append(f"{line}: {exc}")
        write_json(CACHE_FILE, cache)
    if failures:
        raise RuntimeError("도움말 후보 생성 실패:\n" + "\n".join(failures))
    report = {
        "cached_lines": len(cache),
        "new_candidate_lines": len(requested),
        "status": "candidate_requires_full_review",
    }
    write_json(WORK_ROOT / "candidate_report.json", report)
    return report


def reviewed_line(source: str, candidate_value: str) -> str:
    value = LINE_OVERRIDES.get(source, candidate_value)
    for old, new in TERM_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("터틀를", "터틀을").replace("엔터티", "엔티티")
    value = value.replace("디렉토리", "디렉터리").replace("0로", "0으로")
    value = value.replace("터틀와", "터틀과").replace("\u200b", "")
    value = value.replace("인쇄합니다", "출력합니다").replace(
        "인쇄하세요", "출력하세요"
    )
    value = value.replace("입니다.,", "이며,").replace("합니다.,", "하며,")
    value = value.replace("됩니다.,", "되며,").replace("발생합니다.,", "발생하며,")
    value = value.replace(".를 방문", "를 방문").replace(".와 같은", "와 같은")
    return value


def normalize() -> dict[str, object]:
    cache = load_json(CACHE_FILE)
    files = 0
    lines_reviewed = 0
    code_lines_preserved = 0
    for source_path in sorted(ENGLISH_ROOT.rglob("*")):
        if not source_path.is_file():
            continue
        relative = source_path.relative_to(ENGLISH_ROOT)
        if relative.as_posix() in EXCLUDED_FILES:
            continue
        source_lines = source_path.read_text(encoding="utf-8").splitlines()
        target_lines: list[str] = []
        for line in source_lines:
            if translatable_line(line):
                candidate_value = cache.get(line)
                if not isinstance(candidate_value, str):
                    raise KeyError(f"도움말 후보가 없습니다: {relative}:{line}")
                target_lines.append(reviewed_line(line, candidate_value))
                lines_reviewed += 1
            else:
                target_lines.append(line)
                if line.strip():
                    code_lines_preserved += 1
        target = KOREAN_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        ending = "\n" if source_path.read_text(encoding="utf-8").endswith("\n") else ""
        target.write_text("\n".join(target_lines) + ending, encoding="utf-8")
        files += 1
    report = {
        "files_reviewed": files,
        "prose_lines_reviewed": lines_reviewed,
        "code_lines_preserved": code_lines_preserved,
        "existing_korean_reused_without_review": 0,
        "status": "all_operational_help_lines_reviewed",
    }
    write_json(WORK_ROOT / "normalization.json", report)
    return report


def code_tokens(line: str) -> list[str]:
    return [token.rstrip(".,;:") for token in TOKEN_PATTERN.findall(line)]


def verify() -> tuple[dict[str, object], int]:
    errors: list[str] = []
    prose_lines = 0
    code_lines = 0
    files = 0
    untranslated: list[str] = []
    for source_path in sorted(ENGLISH_ROOT.rglob("*")):
        if not source_path.is_file():
            continue
        relative = source_path.relative_to(ENGLISH_ROOT)
        if relative.as_posix() in EXCLUDED_FILES:
            continue
        target_path = KOREAN_ROOT / relative
        if not target_path.is_file():
            errors.append(f"한국어 도움말 누락: {relative}")
            continue
        source_lines = source_path.read_text(encoding="utf-8").splitlines()
        target_lines = target_path.read_text(encoding="utf-8").splitlines()
        if len(source_lines) != len(target_lines):
            errors.append(f"도움말 줄 수 불일치: {relative}")
            continue
        for index, (source, target) in enumerate(
            zip(source_lines, target_lines, strict=True), 1
        ):
            source_tokens = code_tokens(source)
            missing_tokens = sorted(
                {
                    token
                    for token in source_tokens
                    if target.count(token) != source.count(token)
                }
            )
            if missing_tokens:
                errors.append(f"코드 토큰 불일치: {relative}:{index}: {missing_tokens}")
            if translatable_line(source):
                prose_lines += 1
                if source == target:
                    untranslated.append(f"{relative}:{index}")
            elif source.strip():
                code_lines += 1
                if source != target:
                    errors.append(f"코드 전용 줄 변경: {relative}:{index}")
        files += 1
    if untranslated:
        errors.append(f"미번역 도움말 줄: {untranslated[:30]}")
    report = {
        "files": files,
        "prose_lines_reviewed": prose_lines,
        "code_lines_preserved": code_lines,
        "untranslated": len(untranslated),
        "excluded_non_operational_files": EXCLUDED_FILES,
        "errors": errors,
        "status": "complete" if not errors else "incomplete",
    }
    write_json(WORK_ROOT / "validation.json", report)
    return report, 1 if errors else 0


def build() -> dict[str, object]:
    copied = 0
    for source in sorted(KOREAN_ROOT.rglob("*")):
        if not source.is_file():
            continue
        target = OUTPUT_ROOT / source.relative_to(KOREAN_ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        copied += 1
    return {"operational_help_files": copied, "excluded": EXCLUDED_FILES}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("prepare", "candidate", "normalize", "verify", "build")
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.force)
        status = 0
    elif args.command == "candidate":
        result = candidate()
        status = 0
    elif args.command == "normalize":
        result = normalize()
        status = 0
    elif args.command == "verify":
        result, status = verify()
    else:
        result = build()
        status = 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
