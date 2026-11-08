#!/usr/bin/env bash
# Rebuild the profile: draw the banner, palette-quantize it into assets/v4/, write README.md, then refresh the
# House Notes list and the upstream count (the same step the daily Action runs).
# Usage: bash tools/profile/build.sh [REF]   REF = the branch the README's image URLs load from (default main).
# Needs google-chrome and python3 with Pillow built with libimagequant (check: python3 -c
# 'from PIL import features; print(features.check("libimagequant"))').
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../.." && pwd)
ref=${1:-main}
build="$here/build"

python3 -I "$here/fonts.py" "$build/fonts"
python3 -I "$here/cards.py"

rm -rf "$build/stage"
mkdir -p "$build/stage"
for v in d dk m mk; do cp "$build/out/banner_${v}.png" "$build/stage/"; done

python3 -I "$here/quant.py" "$repo/assets/v4" "$build/stage"/*.png
python3 -I "$here/readme.py" "$ref" "$repo/README.md"
python3 -I "$here/refresh.py" "$repo/README.md"
