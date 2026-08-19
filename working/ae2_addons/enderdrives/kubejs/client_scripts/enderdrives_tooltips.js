const ENDERDRIVES_TRANSLATED_TOOLTIP_ITEMS = [
    'enderdrives:ender_disk_1k',
    'enderdrives:ender_disk_4k',
    'enderdrives:ender_disk_16k',
    'enderdrives:ender_disk_64k',
    'enderdrives:ender_disk_256k',
    'enderdrives:ender_disk_creative',
    'enderdrives:tape_disk'
]

ItemEvents.modifyTooltips(event => {
    if (Platform.isLoaded('enderdrives')) {
        event.modify(ENDERDRIVES_TRANSLATED_TOOLTIP_ITEMS, tooltip => {
            tooltip.dynamic('enderdrives_korean')
        })
    }
})

ItemEvents.dynamicTooltips('enderdrives_korean', event => {
    for (let index = 0; index < event.lines.size(); index++) {
        const plain = event.lines.get(index).getString()
            .replace(/§[0-9A-FK-OR]/gi, '')
            .trim()

        if (plain === 'This item is disabled on the server.') {
            event.lines.set(index, Text.of('§c이 서버에서는 이 아이템을 사용할 수 없습니다.'))
            continue
        }
        if (plain === 'Ideal for tools, armor, and NBT-heavy items.') {
            event.lines.set(
                index,
                Text.of('§7도구, 방어구와 NBT 데이터가 많은 아이템에 적합합니다.')
            )
            continue
        }

        let match = plain.match(/^Tape ID: (.+)$/)
        if (match) {
            event.lines.set(index, Text.of(`§7테이프 ID: §f${match[1]}`))
            continue
        }

        match = plain.match(/^(?:Partitioned: ([\d,]+) items?|파티션 (?:설정됨|항목): ([\d,]+)개s?)$/)
        if (match) {
            const count = match[1] || match[2]
            event.lines.set(index, Text.of(`§7파티션 항목: §f${count}개`))
        }
    }
})
