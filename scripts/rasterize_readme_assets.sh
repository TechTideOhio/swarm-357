#!/usr/bin/env bash
# file: scripts/rasterize_readme_assets.sh
# description: Rasterize docs/assets SVGs to PNGs for GitHub README rendering
# reference: docs/assets/, README.md

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ASSETS="$ROOT/docs/assets"
HS="${CHROME_HEADLESS_SHELL:-$HOME/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe}"

if [[ ! -x "$HS" && ! -f "$HS" ]]; then
  echo "chrome-headless-shell not found at $HS" >&2
  exit 1
fi

python - <<'PY' "$ASSETS"
from pathlib import Path
import sys
assets = Path(sys.argv[1])
jobs = [
    ("banner.svg", "banner.png", 1280, 320, "#0a0a0a"),
    ("architecture.svg", "architecture.png", 960, 540, "#fafafa"),
    ("eval-results.svg", "eval-results.png", 960, 420, "#fafafa"),
    ("request-lifecycle.svg", "request-lifecycle.png", 960, 420, "#fafafa"),
    ("logo-mark.svg", "logo-mark.png", 256, 256, "#ffffff"),
    ("logo-wordmark.svg", "logo-wordmark.png", 640, 128, "#ffffff"),
]
for svg_name, png_name, w, h, bg in jobs:
    svg = (assets / svg_name).read_text(encoding="utf-8")
    if svg.startswith("<?xml"):
        svg = svg.split("?>", 1)[1].lstrip()
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
html, body {{ margin:0; padding:0; width:{w}px; height:{h}px; background:{bg}; overflow:hidden; }}
svg {{ width:{w}px; height:{h}px; display:block; }}
</style></head><body>
{svg}
</body></html>"""
    (assets / f"_render_{png_name}.html").write_text(html, encoding="utf-8")
    print(png_name, w, h)
PY

render() {
  local png="$1" size="$2"
  "$HS" --screenshot="$ASSETS/$png" --window-size="$size" --hide-scrollbars --force-device-scale-factor=1 \
    "file:///${ASSETS}/_render_${png}.html"
}

render banner.png 1280,320
render architecture.png 960,540
render eval-results.png 960,420
render request-lifecycle.png 960,420
render logo-mark.png 256,256
render logo-wordmark.png 640,128

rm -f "$ASSETS"/_render_*.html
echo "done"
