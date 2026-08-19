let enderDrivesMessageContext = ''
let enderDrivesMessageContextExpiresAt = 0

const ENDERDRIVES_EXACT_MESSAGES = {
    'This EnderDisk is disabled on the server.':
        '§c이 서버에서는 엔더 아이템 저장 셀을 사용할 수 없습니다.',
    '[EnderDrives] Transfer blocked: Infinite loop detected between linked drives.':
        '§c[EnderDrives] 연결된 드라이브 사이에 무한 전송 고리가 감지되어 전송을 차단했습니다.',
    '[EnderDrives Tape Stats]': '§b[EnderDrives 테이프 통계]',
    'No saved tape drives to verify.': '§7검증할 저장된 테이프 드라이브가 없습니다.',
    'Oldest Tape Drives:': '§b가장 오래된 테이프 드라이브:',
    'No saved tape drives found.': '§7저장된 테이프 드라이브가 없습니다.',
    'Failed to import. File missing or invalid format.':
        '§c가져오지 못했습니다. 파일이 없거나 형식이 올바르지 않습니다.',
    'Failed to export. Tape might not exist or is corrupted.':
        '§c내보내지 못했습니다. 테이프가 없거나 손상되었을 수 있습니다.',
    'Cached Tape Drives:': '§bRAM에 캐시된 테이프 드라이브:',
    'No tape drives are currently cached in RAM.':
        '§7현재 RAM에 캐시된 테이프 드라이브가 없습니다.',
    'You must be a server operator to dump global channels.':
        '§c전체 공개 채널을 덤프하려면 서버 관리자 권한이 필요합니다.',
    "Invalid channel type. Use 'private', 'team', or 'global'.":
        "§c채널 유형이 올바르지 않습니다. 'private', 'team' 또는 'global'을 사용하세요.",
    'Failed to access 256k storage cell.':
        '§c256k 아이템 저장 셀에 접근하지 못했습니다.',
    'If drive creation was successful, you can run clear on that frequency now.':
        '§a드라이브 생성에 성공했다면 이제 해당 주파수에 clear 명령을 실행할 수 있습니다.',
    'Stress test complete on your private channel:':
        '§b비공개 채널의 부하 시험이 완료되었습니다:',
    'Frequency mismatch. Use the same frequency you confirmed.':
        '§c주파수가 일치하지 않습니다. 확인할 때 사용한 주파수와 같아야 합니다.',
    'You must be a server operator to clear general channels.':
        '§c공용 채널을 비우려면 서버 관리자 권한이 필요합니다.',
    'Hold an EnderDisk in your hand.':
        '§c엔더 아이템 저장 셀을 손에 들어 주세요.'
}

function stripEnderDrivesFormatting(text) {
    return text.replace(/§[0-9A-FK-OR]/gi, '').trim()
}

function stripEnderDrivesStatusIcon(text) {
    return text.replace(/^[✔✓✅⚠✖]\s*/, '')
}

function translateEnderDrivesScope(scope) {
    const normalized = scope.toLowerCase()
    if (normalized === 'private') return '비공개'
    if (normalized === 'team') return '팀'
    if (normalized === 'global') return '전체 공개'
    return scope
}

function translateEnderDrivesBoolean(value) {
    if (value === 'Yes') return '§a예'
    if (value === 'No') return '§c아니요'
    if (value === '(Not in RAM)') return '§7(RAM에 없음)'
    return value
}

function setEnderDrivesMessageContext(context) {
    enderDrivesMessageContext = context
    enderDrivesMessageContextExpiresAt = Date.now() + 5000
}

function hasEnderDrivesMessageContext(context) {
    if (Date.now() > enderDrivesMessageContextExpiresAt) {
        enderDrivesMessageContext = ''
    }
    return enderDrivesMessageContext === context
}

function translateEnderDrivesSystemMessage(rawText) {
    const plain = stripEnderDrivesFormatting(rawText)
    const message = stripEnderDrivesStatusIcon(plain)
    const exact = ENDERDRIVES_EXACT_MESSAGES[message]
    if (exact) {
        if (message === '[EnderDrives Tape Stats]') setEnderDrivesMessageContext('stats')
        if (message === 'Stress test complete on your private channel:') {
            setEnderDrivesMessageContext('stress')
        }
        return exact
    }

    let match = message.match(/^Frequency must be between (.+) and (.+)\.$/)
    if (match) return `§c주파수는 §e${match[1]}§c에서 §e${match[2]}§c 사이여야 합니다.`

    match = message.match(/^\[Info for Tape (.+)]$/)
    if (match) {
        setEnderDrivesMessageContext('info')
        return `§b[테이프 ${match[1]} 정보]`
    }
    if (hasEnderDrivesMessageContext('info')) {
        match = message.match(/^Last Accessed: (.+)$/)
        if (match) return ` §7마지막 접근: §f${match[1]}`
        match = message.match(/^Bytes: (.+)$/)
        if (match) return ` §7바이트: §d${match[1]}`
        match = message.match(/^Types: (.+)$/)
        if (match) return ` §7종류: §e${match[1]}`
        match = message.match(/^Pinned: (.+)$/)
        if (match) return ` §7RAM 고정: ${translateEnderDrivesBoolean(match[1])}`
        match = message.match(/^In RAM: (.+)$/)
        if (match) return ` §7RAM 상주: ${translateEnderDrivesBoolean(match[1])}`
    }

    match = message.match(/^Tape (.+) unpinned\.$/)
    if (match) return `§e✔ 테이프의 RAM 고정을 해제했습니다: ${match[1]}`
    match = message.match(/^Tape (.+) pinned to RAM\.$/)
    if (match) return `§a✔ 테이프를 RAM에 고정했습니다: ${match[1]}`
    match = message.match(/^Failed to read tape (.+): (.+)$/)
    if (match) return `§c테이프를 읽지 못했습니다: ${match[1]} / ${match[2]}`
    match = message.match(/^Removed (.+) empty tape\(s\)\.$/)
    if (match) return `§a✔ 빈 테이프 ${match[1]}개를 제거했습니다.`

    if (hasEnderDrivesMessageContext('stats')) {
        match = message.match(/^Disk Usage: (.+) bytes$/)
        if (match) return ` §7디스크 사용량: §6${match[1]}바이트`
        match = message.match(/^Stored \.bin Files: (.+)$/)
        if (match) return ` §7저장된 .bin 파일: §b${match[1]}개`
        match = message.match(/^RAM Usage \(Est\.\): (.+) bytes$/)
        if (match) return ` §7예상 RAM 사용량: §d${match[1]}바이트`
        match = message.match(/^Total Types Cached: (.+)$/)
        if (match) return ` §7캐시된 전체 종류: §e${match[1]}종`
        match = message.match(/^Cached Drives: (.+)$/)
        if (match) return ` §7캐시된 드라이브: §a${match[1]}개`
    }

    match = message.match(/^Error verifying tape (.+): (.+)$/)
    if (match) return `§c테이프 ${match[1]} 검증 오류: ${match[2]}`
    match = message.match(/^Finished verifying (.+) tape\(s\)\. Bad tapes: (.+)$/)
    if (match) return `§b✔ 테이프 ${match[1]}개 검증 완료. 불량 테이프: §c${match[2]}개`
    match = message.match(/^(.+) — OK \((.+) entries\)$/)
    if (match) return `§a${match[1]} — 정상 (${match[2]}개 항목)`
    match = message.match(/^(.+) — (.+)\/(.+) entries failed$/)
    if (match) return `§c${match[1]} — ${match[2]}/${match[3]}개 항목 실패`
    match = message.match(/^No \.bin file exists for tape (.+)$/)
    if (match) return `§c테이프 ${match[1]}의 .bin 파일이 없습니다.`
    match = message.match(/^Error while scanning tape file: (.+)$/)
    if (match) return `§c테이프 파일 검사 중 오류가 발생했습니다: ${match[1]}`
    match = message.match(/^Invalid UUID format: (.+)$/)
    if (match) return `§cUUID 형식이 올바르지 않습니다: ${match[1]}`
    match = message.match(/^Suggest exporting backup with \/enderdrives tape export (.+)$/)
    if (match) return `§e⚠ /enderdrives tape export ${match[1]} 명령으로 백업을 내보내세요.`

    match = message.match(/^\[Diagnosis for (.+)]$/)
    if (match) {
        setEnderDrivesMessageContext('diagnosis')
        return `§b[${match[1]} 진단 결과]`
    }
    if (hasEnderDrivesMessageContext('diagnosis')) {
        match = message.match(/^Size: (.+) bytes$/)
        if (match) return ` §7크기: §e${match[1]}바이트`
        match = message.match(/^Malformed: (.+)$/)
        if (match) return ` §7손상 항목: §c${match[1]}개`
        match = message.match(/^Total entries: (.+)$/)
        if (match) return ` §7전체 항목: §a${match[1]}개`
    }

    match = message.match(/^Failed to delete tape (.+)\. File may not exist\.$/)
    if (match) return `§c테이프를 삭제하지 못했습니다: ${match[1]}. 파일이 없을 수 있습니다.`
    match = message.match(/^Invalid UUID: (.+)$/)
    if (match) return `§c올바르지 않은 UUID: ${match[1]}`
    match = message.match(/^Deleted tape (.+) from disk\.$/)
    if (match) return `§a✔ 디스크에서 테이프를 삭제했습니다: ${match[1]}`
    match = message.match(/^Tape (.+) was cached in RAM and has been released\.$/)
    if (match) return `§eRAM에 캐시된 테이프도 함께 해제했습니다: ${match[1]}`
    match = message.match(/^- (.+?) \| Modified: (.+?) \| Size: (.+) bytes$/)
    if (match) return ` §8- §f${match[1]} §7| 수정: §6${match[2]} §7| 크기: §e${match[3]}바이트`
    match = message.match(/^Imported tape (.+) from JSON\.$/)
    if (match) return `§a✔ JSON에서 테이프를 가져왔습니다: ${match[1]}`
    match = message.match(/^Exported tape (.+) to JSON\.$/)
    if (match) return `§a✔ 테이프를 JSON으로 내보냈습니다: ${match[1]}`
    match = message.match(/^- (.+?) \| Types: (.+)$/)
    if (match) return ` §8- §f${match[1]} §7| 종류: §a${match[2]}종`
    match = message.match(/^Tape (.+) is not currently cached in RAM\.$/)
    if (match) return `§c해당 테이프는 현재 RAM에 캐시되어 있지 않습니다: ${match[1]}`
    match = message.match(/^Released tape (.+) from RAM\.$/)
    if (match) return `§a✔ RAM에서 테이프를 해제했습니다: ${match[1]}`

    match = message.match(/^No items found in frequency (.+)\.$/)
    if (match) return `§c해당 주파수에 아이템이 없습니다: ${match[1]}`
    match = message.match(/^EnderDrives ([^:]+):([^ ]+) Drive:(.+)$/)
    if (match) {
        return `EnderDrives ${translateEnderDrivesScope(match[1])}:${match[2]} 드라이브:${match[3]}`
    }
    match = message.match(/^Dumped (.+) items into (.+) 256k drive\(s\)\.$/)
    if (match) return `§a✔ 아이템 §e${match[1]}개§a를 256k 드라이브 §b${match[2]}개§a에 덤프했습니다.`

    if (hasEnderDrivesMessageContext('stress')) {
        match = message.match(/^Duplicates: (.+)$/)
        if (match) return `중복: ${match[1]}개`
        match = message.match(/^Unique types: (.+)$/)
        if (match) return `고유 종류: ${match[1]}종`
        match = message.match(/^Inserted (.+) items in (.+) ms\.$/)
        if (match) return `아이템 ${match[1]}개를 ${match[2]}ms에 삽입했습니다.`
        match = message.match(/^Duplicate detected for: (.+)$/)
        if (match) return `중복 감지: ${match[1]}`
    }

    match = message.match(/^Frequency (.+) is not empty\. Autobenchmark requires a completely empty frequency\.$/)
    if (match) return `§c해당 주파수에 아이템이 남아 있습니다: ${match[1]}. 자동 벤치마크에는 완전히 빈 주파수가 필요합니다.`
    match = message.match(/^Best stable entry count: (.+) types$/)
    if (match) return `§a✔ 안정적으로 처리한 최대 항목 수: §b${match[1]}종`
    match = message.match(/^TPS dropped below (.+) in at least one dimension\. Stopping\.$/)
    if (match) return `§c⚠ 차원 하나 이상에서 TPS가 ${match[1]} 아래로 떨어져 중지합니다.`

    match = message.match(/^\[AutoBenchmark]\nTested Size: (.+) types\nInsert: (.+)ms\nQuery: (.+)ms\nTypes: (.+)\nMemory: (.+)MB\nTPS: (.+) \(worst: (.+)\) \| Tick: (.+)ms$/)
    if (match) {
        return `§b[자동 벤치마크]\n§7시험 규모: §a${match[1]}종\n§7삽입: §e${match[2]}ms\n§7조회: §e${match[3]}ms\n§7종류: §a${match[4]}종\n§7메모리: §b${match[5]}MB\n§7TPS: §a${match[6]} §7(최저: §f${match[7]}§7) §7| 틱: §a${match[8]}ms`
    }

    match = message.match(/^\[EnderDrives Autobenchmark]\nThis command will insert items until 2,000,000 types are added to the database\.\nIt will automatically stop if server TPS drops below 18\.\n\nOnce the test starts, open an AE2 terminal with an EnderDrive installed at frequency (.+) and scope Private\.\n\nRe-run \/enderdrives autobenchmark (.+) to confirm and begin the test\.$/)
    if (match) {
        return `§b[EnderDrives 자동 벤치마크]\n§7데이터베이스에 §f2,000,000§7종이 추가될 때까지 아이템을 삽입합니다.\n§7서버 TPS가 §c18§7 아래로 떨어지면 자동으로 중지합니다.\n\n§f시험을 시작한 뒤, 엔더 드라이브의 주파수는 §a${match[1]}§f, 공유 범위는 §a비공개§f로 설정하고 AE2 터미널을 열어 두세요.\n\n§e확인하고 시험을 시작하려면 §6/enderdrives autobenchmark ${match[2]}§e 명령을 다시 실행하세요.`
    }

    match = message.match(/^EnderDB Stats:\n - DB Entries: (.+)\n - Items Written: (.+)\n - Commits: (.+)\n - DB File Size: (.+) bytes$/)
    if (match) {
        return `EnderDB 통계:\n - DB 항목: ${match[1]}개\n - 기록한 아이템: ${match[2]}개\n - 커밋: ${match[3]}회\n - DB 파일 크기: ${match[4]}바이트`
    }

    match = message.match(/^Cleared frequency (.+) for scope (.+)$/)
    if (match) return `§a✔ ${translateEnderDrivesScope(match[2])} 범위의 주파수를 비웠습니다: §b${match[1]}`
    match = message.match(/^This will permanently delete all items stored in frequency (.+) under the (.+) scope\.\nIf you are sure, run the same command again to confirm\.$/)
    if (match) {
        return `§c⚠ ${translateEnderDrivesScope(match[2])} 범위에서 다음 주파수에 저장된 모든 아이템을 영구 삭제합니다: §e${match[1]}\n§7계속하려면 같은 명령을 다시 실행해 확인하세요.`
    }
    match = message.match(/^Frequency set to (.+)$/)
    if (match) return `주파수 설정 완료: ${match[1]}`

    return null
}

if (Platform.isClientEnvironment()) {
    const $EnderDrivesSystemChatEvent = Java.loadClass(
        'net.neoforged.neoforge.client.event.ClientChatReceivedEvent$System'
    )

    NativeEvents.onEvent($EnderDrivesSystemChatEvent, event => {
        const source = stripEnderDrivesFormatting(event.getMessage().getString())
        if (source.startsWith('Frequency set to ') && Client.player !== null) {
            const heldItemId = String(Client.player.mainHandItem.id)
            if (!heldItemId.startsWith('enderdrives:ender_disk_')) return
        }
        const translated = translateEnderDrivesSystemMessage(source)
        if (translated !== null) {
            event.setMessage(Text.of(translated))
        }
    })
}
