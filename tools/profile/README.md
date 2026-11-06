# Profile build

The cards on github.com/StartupBros are HTML pages that headless Chrome draws at 2x, then palette-quantized PNGs.
Each card comes in four versions (desktop light, desktop dark, phone light, phone dark), and the README picks one
with a `<picture>` element.

```sh
bash tools/profile/build.sh        # redraws assets/v4/*.png and rewrites README.md
```

Needs `google-chrome` and Python 3 with Pillow built with libimagequant. Fonts download from Google Fonts on the
first run into `tools/profile/build/`, which git ignores.

| File | What it holds |
|---|---|
| `cards.py` | Every card's copy and layout: banner, the two fork cards, the leaderboard card, the pitch card, and the pills |
| `readme.py` | The README: section order, plugin and repo tables, House Notes, the sources block, and the UTM tags |
| `fonts.py` | Downloads Inter, DM Sans, JetBrains Mono and Instrument Serif |
| `quant.py` | Palette-quantizes the PNGs to 256 colors, keeping transparency |
| `will_arms.png` | The cut-out photo on the banner |

To refresh the leaderboard numbers, edit the `stack` card in `cards.py` (the numbers and the "Read" date) and the
matching alt text and sources block in `readme.py`, then run `build.sh` and commit `README.md` and `assets/v4/`.
