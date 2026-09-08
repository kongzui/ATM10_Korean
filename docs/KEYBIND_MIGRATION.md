# 7.1 단축키를 8.1로 한 번에 옮기기

확인일: 2026-09-09. 두 인스턴스 루트의 `options.txt`에서 `key_`로 시작하는 줄이
단축키 설정인 것을 확인했어요. 기존 설정은 493개, 8.1은 544개였고 공통 491개 중
23개의 값이 달랐어요. 8.1에만 있는 53개는 현재 값을 유지하면 돼요.
이는 확인 시점의 개인 설정이며 다음 실행 후 달라질 수 있어요.

## 파일 하나를 통째로 복사하는 방법

게임을 완전히 종료하고 **8.1의 `options.txt`를 먼저 백업**한 뒤, 7.1의 같은 파일을
8.1 인스턴스 루트에 복사해서 덮어쓰면 돼요. `config/` 안의 파일이 아니에요.

- 원본: `C:/Users/moon9/curseforge/minecraft/Instances/All the Mods 10 - ATM10/options.txt`
- 대상: `C:/Users/moon9/curseforge/minecraft/Instances/All the Mods 10 - ATM10 (1)/options.txt`

이 방법은 단축키 외에도 음량·화면·언어·활성 리소스팩 목록을 함께 옮겨요.
특히 7.1 리소스팩 선택까지 가져오므로 8.1 한국어 안정판 ZIP을 다시 활성화해야 할 수 있어요.
새 모드의 키는 기존 파일에 없어서 게임이 등록하는 기본값과 충돌하는지 확인해야 해요.

## 추천: 공통 단축키만 합친 파일을 만들어 덮어쓰기

아래 명령은 **실제 게임 파일을 수정하지 않아요**. 8.1 설정을 바탕으로 두 버전에 공통인
`key_` 줄만 7.1 값으로 교체한 파일을 프로젝트의 `temp/keybind_migration/options.txt`에 만들어요.
8.1 전용 키, 리소스팩 선택, 음량·그래픽 설정은 유지해요. 없어진 키 두 개는 추가하지 않아요.

1. Minecraft를 완전히 종료해 현재 설정을 저장해요.
2. 이 저장소 루트에서 PowerShell로 다음 명령을 실행해요. PC가 다르면 원본·대상 경로를 바꿔요.
3. 8.1의 원래 `options.txt`를 별도로 백업해요.
4. 생성한 `temp/keybind_migration/options.txt`만 8.1 인스턴스 루트에 덮어써요.
5. 게임을 실행하고 설정 → 조작에서 주요 키와 새 모드의 키 충돌을 확인해요.
   문제 시 종료 후 백업 파일을 복원해요.

```powershell
$keyOldPath = 'C:/Users/moon9/curseforge/minecraft/Instances/All the Mods 10 - ATM10/options.txt'
$keyNewPath = 'C:/Users/moon9/curseforge/minecraft/Instances/All the Mods 10 - ATM10 (1)/options.txt'
$keyUtf8 = [System.Text.UTF8Encoding]::new($false)
$keyOldLines = [System.IO.File]::ReadAllLines($keyOldPath, $keyUtf8)
$keyNewLines = [System.IO.File]::ReadAllLines($keyNewPath, $keyUtf8)
$keyMap = [System.Collections.Generic.Dictionary[string,string]]::new([System.StringComparer]::Ordinal)
foreach ($keyLine in $keyOldLines) {
    if ($keyLine.StartsWith('key_') -and $keyLine.Contains(':')) {
        $keyName = $keyLine.Substring(0, $keyLine.IndexOf(':'))
        $keyMap[$keyName] = $keyLine
    }
}
$keyChanged = 0
$keyMerged = foreach ($keyLine in $keyNewLines) {
    $keyName = $keyLine.Split(':', 2)[0]
    if ($keyLine.StartsWith('key_') -and $keyMap.ContainsKey($keyName)) {
        if ($keyLine -cne $keyMap[$keyName]) { $keyChanged++ }
        $keyMap[$keyName]
    } else {
        $keyLine
    }
}
$keyOutputDir = Join-Path (Get-Location) 'temp/keybind_migration'
[System.IO.Directory]::CreateDirectory($keyOutputDir) | Out-Null
$keyOutputPath = Join-Path $keyOutputDir 'options.txt'
[System.IO.File]::WriteAllLines($keyOutputPath, [string[]]$keyMerged, $keyUtf8)
Write-Output "바뀐 단축키: $keyChanged / 수동 설치할 파일: $keyOutputPath"
```

명령은 첫 콜론 앞의 설정 이름으로 대응시키고 나머지 줄을 그대로 보존해요.
Ctrl·Shift·Alt 같은 보조키 값도 임의로 분해하거나 재작성하지 않아요.
보조키와 사용 상황에 따라 충돌 여부가 달라질 수 있으므로 실제 조작 화면에서 확인해요.
[NeoForge 1.21.1 단축키 문서](https://docs.neoforged.net/docs/1.21.1/misc/keymappings/)

이는 `options.txt`에 저장되는 키만 옮기는 방법이에요. 모드가 별도 파일에 저장하는
매크로·키 묶음·마우스 동작 설정은 포함하지 않아요. 새 버전에서 설정 이름이 바뀐 키는
같은 기능인지 수동 확인해요. `config/` 전체를 7.1 것으로 덮어쓰지 않아요.
개인 설정 파일은 Git과 공용 한국어 배포 ZIP에 넣지 않아요.
