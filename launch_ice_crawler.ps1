$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Exe = Join-Path $Root "IceCrawler.exe"
$Ui = Join-Path $Root "ui\ice_ui.py"

if (Test-Path $Exe) {
    & $Exe
} else {
    python $Ui
}
