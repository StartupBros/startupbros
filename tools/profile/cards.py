"""Draw the profile banner in four variants: _d (desktop light page), _dk (desktop dark page), _m (phone light),
_mk (phone dark). Rendered by headless Chrome at 2x into build/out/. Usage: cards.py [name ...]
(name = a key of A, e.g. banner_d or banner_mk)"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SRC = os.path.join(BUILD, "src")
OUT = os.path.join(BUILD, "out")
UD = os.path.join(BUILD, "chrome")
FONTS = os.path.join(BUILD, "fonts", "local.css")  # written by fonts.py
PHOTO = os.path.join(HERE, "will_arms.png")
os.makedirs(SRC, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

LOGO = ('<svg class="logo" viewBox="0 0 512 512" aria-hidden="true"><path fill="none" stroke="#39ff14" '
        'stroke-width="64" stroke-linejoin="miter" stroke-miterlimit="10" d="M108 404 V238 L256 90 L404 238 V404"/>'
        '<path fill="#39ff14" d="M176 262 H238 L256 316 L274 262 H336 L256 392 Z"/></svg>')
ARROW = ('<svg class="arr" viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" fill="none" '
         'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')

BASE = """
html,body{margin:0;padding:0;background:transparent}
*{box-sizing:border-box}
.card{position:relative;overflow:hidden;border-radius:18px;background:#0a0a0c;color:#f4f4f5;font-family:'Inter',sans-serif}
.card::after{content:"";position:absolute;inset:0;border-radius:inherit;border:1px solid rgba(255,255,255,0.09);pointer-events:none}
.grid{position:absolute;inset:0;background-image:linear-gradient(to right,rgba(255,255,255,0.045) 1px,transparent 1px),linear-gradient(to bottom,rgba(255,255,255,0.045) 1px,transparent 1px);background-size:30px 30px}
.eyebrow{font-family:'JetBrains Mono',monospace;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:#39ff14;display:flex;align-items:center}
.hl{color:#39ff14;text-shadow:0 0 18px rgba(57,255,20,.45)}
.btn{display:inline-flex;align-items:center;border-radius:999px;background:#7ed400;color:#0f0d15;font-weight:700;letter-spacing:-.01em;white-space:nowrap;box-shadow:0 0 0 1px rgba(15,13,21,.12),0 3px 16px rgba(126,212,0,.28)}
.arr{flex:none}
"""
# Dark-page variant: lift the card off GitHub's #0d1117 canvas the way GitHub's own boxes do.
DARK = """
.card{background:#161b22}
.card::after{border-color:#30363d}
.t{background:#0d1117!important;border-color:#30363d!important}
.pill{background:#161b22!important;border-color:#30363d!important}
.pill.primary{border-color:rgba(57,255,20,.6)!important}
"""


def page(css, body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTS}">'
            f'<style>{BASE}{css}</style></head><body>{body}</body></html>')


A = {}  # name -> (w, h, html, crop)


def card(name, w, h, css, body, crop=False, dark_extra=""):
    """Register the light variant as name and the dark variant as name + 'k'."""
    A[name] = (w, h, page(css, body), crop)
    A[name + "k"] = (w, h, page(css + DARK + dark_extra, body), crop)


# ---------- banner (carries the first Build Your First Thing button) ----------
EB = f'<div class="eyebrow">{LOGO}<span>Will Mitchell</span></div>'
H1 = 'Helping people with day jobs <br>build <span class="hl">real things</span> with AI.'
BTN = f'<div class="btn">Build Your First Thing {ARROW}</div>'
BANNER_DARK = ".card{background:#0a0a0c}"
card("banner_d", 900, 300, """
.card{width:900px;height:300px}
.grid{-webkit-mask-image:radial-gradient(ellipse 75% 90% at 30% 40%,#000 30%,transparent 85%)}
.glow{position:absolute;right:-60px;top:-40px;width:470px;height:440px;background:radial-gradient(closest-side,rgba(57,255,20,.30),rgba(57,255,20,.10) 55%,transparent 100%)}
.photo{position:absolute;right:54px;top:20px;height:560px;filter:drop-shadow(0 0 1px rgba(57,255,20,.55)) drop-shadow(0 0 22px rgba(57,255,20,.22))}
.text{position:absolute;left:48px;top:38px;width:640px}
.eyebrow{font-size:13px;letter-spacing:.22em;gap:12px}.logo{width:20px;height:20px}
h1{margin:14px 0 0;font-weight:800;font-size:41px;line-height:1.06;letter-spacing:-.025em;color:#fff}
.sub{margin-top:14px;font-family:'DM Sans';font-size:18.5px;line-height:1.35;color:#d4d4d8}
.btn{margin-top:22px;height:46px;padding:0 24px;gap:10px;font-size:16px}
.arr{width:16px;height:16px}
""", f'<div class="card"><div class="grid"></div><div class="glow"></div><img class="photo" src="{PHOTO}">'
     f'<div class="text">{EB}<h1>{H1}</h1>'
     f'<div class="sub">Founder of StartupBros and House of Vibe.<br>9,000+ entrepreneurs served since 2012.</div>{BTN}</div></div>',
     dark_extra=BANNER_DARK)

card("banner_m", 600, 640, """
.card{width:600px;height:640px}
.grid{-webkit-mask-image:radial-gradient(ellipse 90% 70% at 30% 25%,#000 30%,transparent 85%)}
.glow{position:absolute;right:-140px;bottom:-120px;width:600px;height:560px;background:radial-gradient(closest-side,rgba(57,255,20,.32),rgba(57,255,20,.10) 55%,transparent 100%)}
.photo{position:absolute;right:0;top:262px;height:720px;filter:drop-shadow(0 0 1px rgba(57,255,20,.55)) drop-shadow(0 0 26px rgba(57,255,20,.22))}
.text{position:absolute;left:40px;top:40px;width:530px}
.eyebrow{font-size:19px;letter-spacing:.22em;gap:14px}.logo{width:28px;height:28px}
h1{margin:20px 0 0;font-weight:800;font-size:49px;line-height:1.06;letter-spacing:-.03em;color:#fff}
h1 br{display:none}
.sub{position:absolute;left:40px;top:290px;width:255px;font-family:'DM Sans';font-size:23px;line-height:1.32;color:#d4d4d8}
.btn{position:absolute;left:40px;bottom:40px;height:66px;padding:0 30px;gap:12px;font-size:23px;z-index:2}
.arr{width:21px;height:21px}
.fade{position:absolute;left:0;right:0;bottom:0;height:170px;background:linear-gradient(to bottom,transparent,rgba(10,10,12,.85) 70%);z-index:1}
""", f'<div class="card"><div class="grid"></div><div class="glow"></div><img class="photo" src="{PHOTO}"><div class="fade"></div>'
     f'<div class="text">{EB}<h1>{H1}</h1></div>'
     f'<div class="sub">Founder of StartupBros and House of Vibe. 9,000+ entrepreneurs since 2012.</div>{BTN}</div>',
     dark_extra=BANNER_DARK)



def holes(im, crop):
    """Pixels inside the card's rounded outline that are not fully opaque, so the page would show through.
    Chrome sometimes screenshots before a tile is painted: banner_dk merged in #12 had a 37,893-pixel
    see-through strip under the photo. The mask is drawn inside the card's visible box, since the fork
    cards carry a deliberate transparent gutter, 3px in and with a radius at least the card's own
    (18px or 22px, so 36 or 44 at 2x), so antialiased edges and corners never count."""
    alpha = im.convert("RGBA").getchannel("A")
    x0, y0, x1, y1 = alpha.getbbox()
    mask = Image.new("L", alpha.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((x0 + 3, y0 + 3, x1 - 4, y1 - 4),
                                           radius=(y1 - y0) // 2 if crop else 48, fill=255)
    clear = alpha.point(lambda v: 255 if v < 255 else 0)
    return ImageChops.multiply(mask, clear).histogram()[255]


def render(name, tries=3):
    w, h, html, crop = A[name]
    src = f"{SRC}/{name}.html"
    open(src, "w").write(html)
    out = f"{OUT}/{name}.png"
    ud = f"{UD}/{name}"
    cmd = ["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
           f"--user-data-dir={ud}", "--allow-file-access-from-files", "--force-device-scale-factor=2",
           "--default-background-color=00000000", f"--window-size={w},{h}", "--virtual-time-budget=4000",
           f"--screenshot={out}", f"file://{src}"]
    for attempt in range(1, tries + 1):
        if os.path.exists(out):
            os.remove(out)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if not os.path.exists(out):
            return f"{name} FAILED rc={r.returncode} {r.stderr[-300:]}"
        im = Image.open(out)
        if crop:
            im = im.crop(im.getchannel("A").getbbox())
        n = holes(im, crop)
        if not n:
            im.save(out, optimize=True)
            return f"{name} {im.size} {os.path.getsize(out)}" + (f" (render {attempt})" if attempt > 1 else "")
    os.remove(out)
    return f"{name} FAILED {n} see-through pixels inside the card after {tries} renders"


if __name__ == "__main__":
    names = sys.argv[1:] or list(A)
    with ThreadPoolExecutor(max_workers=6) as ex:
        lines = list(ex.map(render, names))
    print("\n".join(lines))
    if any(" FAILED " in line for line in lines):
        sys.exit(1)
