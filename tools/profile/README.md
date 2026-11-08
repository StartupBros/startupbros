# Profile build

The README on github.com/StartupBros is plain Markdown under one banner image. The banner is an HTML page that
headless Chrome draws at 2x, then a palette-quantized PNG in four versions (desktop light, desktop dark, phone
light, phone dark); the README picks one with a `<picture>` element.

```sh
bash tools/profile/build.sh        # redraws assets/v4/banner_*.png, rewrites README.md, then runs refresh.py
```

Needs `google-chrome` and Python 3 with Pillow built with libimagequant. Fonts download from Google Fonts on the
first run into `tools/profile/build/`, which git ignores.

| File | What it holds |
|---|---|
| `readme.py` | The README's text: intro, sections, links and the UTM tags |
| `refresh.py` | Fills the two generated parts: the latest House Notes posts (RSS) and the merged upstream pull request line (GitHub search) |
| `test_refresh.py` | Tests for refresh.py: `python3 -I -m unittest discover -s tools/profile -p 'test_*.py'` |
| `cards.py` | The banner's copy and layout |
| `fonts.py` | Downloads Inter, DM Sans, JetBrains Mono and Instrument Serif |
| `quant.py` | Palette-quantizes the PNGs to 256 colors, keeping transparency |
| `will_arms.png` | The cut-out photo on the banner |

`.github/workflows/refresh.yml` runs `refresh.py` every day at 13:17 UTC and commits the README only when the text
changed. It also runs the tests on pull requests that touch `tools/profile/`. GitHub pauses a scheduled workflow
after 60 days with no activity in the repo; "Run workflow" on the Actions tab turns it back on.
