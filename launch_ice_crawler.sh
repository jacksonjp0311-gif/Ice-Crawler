#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(uname -s)" == MINGW* || "$(uname -s)" == MSYS* || "$(uname -s)" == CYGWIN* ]] && [[ -f "$ROOT/IceCrawler.exe" ]]; then
  "$ROOT/IceCrawler.exe"
else
  python "$ROOT/ui/ice_ui.py"
fi
