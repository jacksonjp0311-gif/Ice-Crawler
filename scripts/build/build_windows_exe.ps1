$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

python -m pip install --upgrade pyinstaller

$icon = Join-Path $Root "ui\assets\snowflake.ico"
if (Test-Path $icon) {
    pyinstaller --noconfirm --onefile --windowed --name IceCrawler --icon $icon ui\ice_ui.py
} else {
    pyinstaller --noconfirm --onefile --windowed --name IceCrawler ui\ice_ui.py
}

Write-Host "Built: dist\IceCrawler.exe"
