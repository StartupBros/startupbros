#!/usr/bin/env bash
# Rebuild the profile: draw every card, palette-quantize them into assets/v4/, write README.md.
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
for n in banner fork_hov fork_dev stack pitch; do
  for v in d dk m mk; do cp "$build/out/${n}_${v}.png" "$build/stage/"; done
done
for n in pill_hov pill_notes pill_yt pill_x; do
  cp "$build/out/$n.png" "$build/out/${n}_k.png" "$build/stage/"
done

python3 -I "$here/quant.py" "$repo/assets/v4" "$build/stage"/*.png
python3 -I "$here/readme.py" "$ref" "$repo/README.md"
