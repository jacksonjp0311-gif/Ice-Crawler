$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
python (Join-Path $Root "icecrawler.py") $args
