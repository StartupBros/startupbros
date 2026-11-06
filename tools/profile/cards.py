"""Draw the profile cards. Each card gets four variants: _d (desktop light page), _dk (desktop dark page),
_m (phone light), _mk (phone dark). Pills get name.png and name_k.png. Rendered by headless Chrome at 2x
into build/out/. Usage: cards.py [name ...]   (name = a key of A, e.g. banner_d, fork_hov_mk, pill_x_k)"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

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
CHECK = ('<svg class="chk" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5 6.5 12 13 4.5" fill="none" '
         'stroke="#39ff14" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

BASE = """
html,body{margin:0;padding:0;background:transparent}
*{box-sizing:border-box}
.card{position:relative;overflow:hidden;border-radius:18px;background:#0a0a0c;color:#f4f4f5;font-family:'Inter',sans-serif}
.card::after{content:"";position:absolute;inset:0;border-radius:inherit;border:1px solid rgba(255,255,255,0.09);pointer-events:none}
.grid{position:absolute;inset:0;background-image:linear-gradient(to right,rgba(255,255,255,0.045) 1px,transparent 1px),linear-gradient(to bottom,rgba(255,255,255,0.045) 1px,transparent 1px);background-size:30px 30px}
.eyebrow{font-family:'JetBrains Mono',monospace;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:#39ff14;display:flex;align-items:center}
.hl{color:#39ff14;text-shadow:0 0 18px rgba(57,255,20,.45)}
.btn{display:inline-flex;align-items:center;border-radius:999px;background:#7ed400;color:#0f0d15;font-weight:700;letter-spacing:-.01em;white-space:nowrap;box-shadow:0 0 0 1px rgba(15,13,21,.12),0 3px 16px rgba(126,212,0,.28)}
.ghost{display:inline-flex;align-items:center;border-radius:999px;border:1.5px solid rgba(57,255,20,.7);color:#39ff14;font-weight:700;white-space:nowrap}
.ghost.w{border-color:rgba(255,255,255,.38);color:#f4f4f5}
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
     f'<div class="sub">Founder of House of Vibe · building businesses online since 2002</div>{BTN}</div></div>',
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
.sub{position:absolute;left:40px;top:290px;width:270px;font-family:'DM Sans';font-size:25px;line-height:1.3;color:#d4d4d8}
.btn{position:absolute;left:40px;bottom:40px;height:66px;padding:0 30px;gap:12px;font-size:23px;z-index:2}
.arr{width:21px;height:21px}
.fade{position:absolute;left:0;right:0;bottom:0;height:170px;background:linear-gradient(to bottom,transparent,rgba(10,10,12,.85) 70%);z-index:1}
""", f'<div class="card"><div class="grid"></div><div class="glow"></div><img class="photo" src="{PHOTO}"><div class="fade"></div>'
     f'<div class="text">{EB}<h1>{H1}</h1></div>'
     f'<div class="sub">Founder of House of Vibe. Building businesses online since 2002.</div>{BTN}</div>',
     dark_extra=BANNER_DARK)

# ---------- link pills (monochrome; House of Vibe keeps the green mark) ----------
ICON_NOTES = ('<svg class="ic" viewBox="0 0 20 20"><rect x="4" y="2.5" width="12" height="15" rx="2" fill="none" stroke="#d4d4d8" stroke-width="1.6"/>'
              '<path d="M7 7h6M7 10h6M7 13h4" stroke="#d4d4d8" stroke-width="1.6" stroke-linecap="round"/></svg>')
ICON_YT = ('<svg class="ic" viewBox="0 0 20 20"><rect x="1.5" y="4" width="17" height="12" rx="3.5" fill="none" stroke="#d4d4d8" stroke-width="1.6"/>'
           '<path d="M8.3 7.4v5.2l4.4-2.6z" fill="#d4d4d8"/></svg>')
ICON_X = ('<svg class="ic" viewBox="0 0 24 24"><path fill="#d4d4d8" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>')
ICON_IN = ('<svg class="ic" viewBox="0 0 20 20"><rect x="2.3" y="2.3" width="15.4" height="15.4" rx="3" fill="none" stroke="#d4d4d8" stroke-width="1.6"/>'
           '<path d="M6.4 8.6v5M6.4 6.2v.1" stroke="#d4d4d8" stroke-width="1.9" stroke-linecap="round"/>'
           '<path d="M9.4 13.6V8.6M9.4 10.7c0-1.3.9-2.2 2.1-2.2s2 .8 2 2.2v2.9" fill="none" stroke="#d4d4d8" stroke-width="1.7" stroke-linecap="round"/></svg>')
PILL_CSS = """
.pill{position:absolute;left:2px;top:2px;height:34px;display:inline-flex;align-items:center;gap:8px;padding:0 15px 0 12px;
border-radius:999px;background:#0a0a0c;border:1px solid #2d2940;font-family:'Inter';font-weight:600;font-size:13.5px;color:#f4f4f5;white-space:nowrap}
.pill.primary{border-color:rgba(57,255,20,.55)}
.ic,.logo{width:16px;height:16px;flex:none}
.n{color:#a1a1aa;font-weight:500}
"""
PILLS = [
    ("pill_hov", f'{LOGO}<span>houseofvibe.ai</span>', "pill primary"),
    ("pill_notes", f'{ICON_NOTES}<span>House Notes</span>', "pill"),
    ("pill_yt", f'{ICON_YT}<span>YouTube <span class="n">34K</span></span>', "pill"),
    ("pill_x", f'{ICON_X}<span>X <span class="n">16K</span></span>', "pill"),
    ("pill_in", f'{ICON_IN}<span>LinkedIn</span>', "pill"),
]
for name, inner, cls in PILLS:
    A[name] = (420, 38, page(PILL_CSS, f'<div class="{cls}">{inner}</div>'), True)
    A[name + "_k"] = (420, 38, page(PILL_CSS + DARK, f'<div class="{cls}">{inner}</div>'), True)

# ---------- fork cards: desktop pair at width=421 each with a 6px gutter baked into the inner edge ----------
FORK = {
    "hov": dict(eb="Don't code?", h='Finish your <span class="hl">first project</span> before&nbsp;dinner.',
                p="House of Vibe members build real things with AI around their day jobs, 10 to 15 hours a week.",
                b=f'<div class="ghost">Build Your First Thing {ARROW}</div>', side="left"),
    "dev": dict(eb="Write code?", h='Get the <span class="hl">Claude Code setup</span> I&nbsp;run every&nbsp;day.',
                p="hov-stack: the rules, guards and 13 plugins behind 4,302 merged PRs in 60 days. Free and MIT.",
                b=f'<div class="ghost w">Get hov-stack {ARROW}</div>', side="right"),
}
for k, f in FORK.items():
    pad = "margin-right:6px" if f["side"] == "left" else "margin-left:6px"
    glow = "left:-140px;bottom:-200px" if k == "hov" else "right:-140px;bottom:-200px"
    inner = (f'<div class="grid"></div><div class="glow"></div><div class="in">'
             f'<div class="eyebrow">{f["eb"]}</div><h2>{f["h"]}</h2><p>{f["p"]}</p>{f["b"]}</div>')
    card(f"fork_{k}_d", 421, 232, f"""
.card{{width:415px;height:232px;{pad}}}
.grid{{-webkit-mask-image:radial-gradient(ellipse 80% 80% at 20% 10%,#000 20%,transparent 80%)}}
.glow{{position:absolute;{glow};width:420px;height:380px;background:radial-gradient(closest-side,rgba(57,255,20,.16),transparent 100%)}}
.in{{position:absolute;inset:0;padding:24px 26px}}
.eyebrow{{font-size:11.5px}}
h2{{margin:11px 0 0;font-weight:800;font-size:24px;line-height:1.13;letter-spacing:-.022em;color:#fff}}
p{{margin:9px 0 0;font-family:'DM Sans';font-size:14.5px;line-height:1.42;color:#b4b4bc}}
.ghost{{margin-top:16px;height:38px;padding:0 18px;gap:9px;font-size:14px}}
.arr{{width:14px;height:14px}}
""", f'<div class="card">{inner}</div>')
    card(f"fork_{k}_m", 600, 372, f"""
.card{{width:600px;height:360px;border-radius:22px}}
.grid{{-webkit-mask-image:radial-gradient(ellipse 90% 80% at 20% 10%,#000 20%,transparent 80%)}}
.glow{{position:absolute;{glow};width:560px;height:480px;background:radial-gradient(closest-side,rgba(57,255,20,.18),transparent 100%)}}
.in{{position:absolute;inset:0;padding:34px 36px}}
.eyebrow{{font-size:17px}}
h2{{margin:16px 0 0;font-weight:800;font-size:38px;line-height:1.1;letter-spacing:-.028em;color:#fff}}
p{{margin:14px 0 0;font-family:'DM Sans';font-size:23px;line-height:1.36;color:#b4b4bc}}
.ghost{{position:absolute;left:36px;bottom:32px;height:58px;padding:0 26px;gap:11px;font-size:21px}}
.arr{{width:19px;height:19px}}
""", f'<div class="card">{inner}</div>')

# ---------- leaderboards: the author's usage, not a claim about the repo ----------
BOARDS = [("#2", "all-time", "ccrank"), ("#2", "last 30 days, of 82", "CCWarriors"),
          ("#4", "all-time, of ~1,400", "viberank"), ("Top 2%", "#40 of 2,442", "tokscale")]
tiles = "".join(f'<div class="t"><div class="r">{r}</div><div class="s">{s}</div><div class="b">{b}</div></div>' for r, s, b in BOARDS)
STACK_BODY = (f'<div class="card"><div class="grid"></div><div class="glow"></div><div class="in">'
              f'<div class="eyebrow">{LOGO}<span>Public Claude Code leaderboards</span></div>'
              f'<h2><span class="hl">520 billion tokens</span> logged in Claude&nbsp;Code.</h2>'
              f'<p>#2, #2 and #4 on three boards, and the top 2% on a fourth.</p>'
              f'<div class="tiles">{tiles}</div>'
              f'<div class="foot">Read Nov 6, 2026 · token total from viberank · each board counts only what was submitted to it</div></div></div>')
card("stack_d", 900, 300, """
.card{width:900px;height:300px}
.grid{-webkit-mask-image:radial-gradient(ellipse 70% 90% at 15% 20%,#000 25%,transparent 80%)}
.glow{position:absolute;right:-120px;top:-160px;width:560px;height:460px;background:radial-gradient(closest-side,rgba(57,255,20,.20),transparent 100%)}
.in{position:absolute;inset:0;padding:28px 34px}
.eyebrow{font-size:12px;gap:11px}.logo{width:17px;height:17px}
h2{margin:13px 0 0;font-weight:800;font-size:34px;line-height:1.08;letter-spacing:-.026em;color:#fff}
p{margin:9px 0 0;font-family:'DM Sans';font-size:17px;line-height:1.4;color:#b4b4bc}
.tiles{margin-top:20px;display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.t{background:#121118;border:1px solid #24212f;border-radius:12px;padding:13px 16px 12px}
.r{font-weight:800;font-size:28px;letter-spacing:-.02em;color:#39ff14;text-shadow:0 0 14px rgba(57,255,20,.35);line-height:1}
.s{font-family:'DM Sans';font-size:13.5px;color:#b4b4bc;margin-top:7px;white-space:nowrap}
.b{font-family:'JetBrains Mono';font-weight:600;font-size:11.5px;letter-spacing:.08em;color:#e4e4e7;margin-top:6px;text-transform:uppercase}
.foot{margin-top:14px;font-family:'JetBrains Mono';font-size:11px;color:#71717a}
""", STACK_BODY)
card("stack_m", 600, 720, """
.card{width:600px;height:720px;border-radius:22px}
.grid{-webkit-mask-image:radial-gradient(ellipse 90% 60% at 15% 15%,#000 25%,transparent 80%)}
.glow{position:absolute;right:-160px;top:-180px;width:600px;height:560px;background:radial-gradient(closest-side,rgba(57,255,20,.20),transparent 100%)}
.in{position:absolute;inset:0;padding:36px 36px}
.eyebrow{font-size:15px;gap:12px;letter-spacing:.14em}.logo{width:22px;height:22px}
h2{margin:18px 0 0;font-weight:800;font-size:46px;line-height:1.06;letter-spacing:-.03em;color:#fff}
p{margin:14px 0 0;font-family:'DM Sans';font-size:24px;line-height:1.34;color:#b4b4bc}
.tiles{margin-top:28px;display:grid;grid-template-columns:1fr 1fr;gap:16px}
.t{background:#121118;border:1px solid #24212f;border-radius:16px;padding:20px 22px 18px}
.r{font-weight:800;font-size:46px;letter-spacing:-.03em;color:#39ff14;text-shadow:0 0 16px rgba(57,255,20,.35);line-height:1}
.s{font-family:'DM Sans';font-size:20px;color:#b4b4bc;margin-top:10px}
.b{font-family:'JetBrains Mono';font-weight:600;font-size:17px;letter-spacing:.08em;color:#e4e4e7;margin-top:8px;text-transform:uppercase}
.foot{margin-top:22px;font-family:'JetBrains Mono';font-size:16px;line-height:1.45;color:#71717a}
""", STACK_BODY)

# ---------- House of Vibe pitch (the closing ask) ----------
FEATS = [("Day 1", "Watch it build something real before dinner."),
         ("Day 7", "Replace what you're paying for."),
         ("Built for day jobs", "10 to 15 hours a week, evenings and weekends."),
         ("Live every month", "Training, then Q&amp;A on every question.")]
feats = "".join(f'<div class="f">{CHECK}<div><div class="ft">{t}</div><div class="fl">{l}</div></div></div>' for t, l in FEATS)
WORD = '<div class="word">HOUSE <span class="of">of</span> <span class="vibe">VIBE</span></div>'
PITCH_BODY = (f'<div class="card"><div class="grid"></div><div class="glow"></div><div class="in">'
              f'<div class="brand">{LOGO}{WORD}<div class="tag">The window is open right now</div></div>'
              f'<h2>Most people haven\'t noticed. <span class="hl">The people in the House&nbsp;have.</span></h2>'
              f'<div class="lead">Projects you build. Not courses you watch. And you actually finish them.</div>'
              f'<div class="feats">{feats}</div>'
              f'<div class="cta">{BTN}<div class="g"><b>The Open Door Guarantee.</b> 30 days to try everything. '
              f'Full refund if it\'s not for you.<span class="once">One payment, lifetime access.</span></div></div></div></div>')
WORD_CSS = """
.brand{display:flex;align-items:center}
.word{font-weight:900;letter-spacing:.01em;color:#fff;display:flex;align-items:baseline;gap:7px}
.word .of{font-family:'Instrument Serif',serif;font-style:italic;font-weight:400;color:#8a8a93}
.word .vibe{color:#39ff14;text-shadow:0 0 12px rgba(57,255,20,.6)}
.tag{margin-left:auto;font-family:'JetBrains Mono';font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#39ff14}
.lead{font-family:'DM Sans';color:#d4d4d8}
.f{display:flex;gap:10px;align-items:flex-start}
.ft{font-weight:700;color:#fff;letter-spacing:-.01em;white-space:nowrap}
.fl{font-family:'DM Sans';color:#b4b4bc}
.g{font-family:'DM Sans';color:#e4e4e7}.g b{color:#fff;font-weight:700}
.once{display:block;color:#a1a1aa}
"""
card("pitch_d", 900, 392, WORD_CSS + """
.card{width:900px;height:392px}
.grid{-webkit-mask-image:radial-gradient(ellipse 70% 90% at 80% 30%,#000 25%,transparent 80%)}
.glow{position:absolute;right:-100px;top:-180px;width:600px;height:480px;background:radial-gradient(closest-side,rgba(57,255,20,.22),transparent 100%)}
.in{position:absolute;inset:0;padding:30px 36px}
.brand{gap:12px}.logo{width:26px;height:26px}.word{font-size:19px}.word .of{font-size:19px}.tag{font-size:11.5px}
h2{margin:20px 0 0;font-weight:800;font-size:34px;line-height:1.1;letter-spacing:-.026em;color:#fff}
.lead{margin-top:10px;font-size:17.5px}
.feats{margin-top:22px;display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.chk{width:17px;height:17px;flex:none;margin-top:2px}
.ft{font-size:15px}.fl{font-size:14px;line-height:1.4;margin-top:4px}
.cta{position:absolute;left:36px;right:36px;bottom:28px;display:flex;align-items:center;gap:22px}
.btn{height:50px;padding:0 26px;gap:10px;font-size:17px;flex:none}
.arr{width:17px;height:17px}
.g{font-size:15px;line-height:1.42}.g b{display:block}
""", PITCH_BODY)
card("pitch_m", 600, 980, WORD_CSS + """
.card{width:600px;height:980px;border-radius:22px}
.grid{-webkit-mask-image:radial-gradient(ellipse 90% 60% at 80% 15%,#000 25%,transparent 80%)}
.glow{position:absolute;right:-160px;top:-200px;width:640px;height:600px;background:radial-gradient(closest-side,rgba(57,255,20,.22),transparent 100%)}
.in{position:absolute;inset:0;padding:38px 36px}
.brand{gap:14px;flex-wrap:wrap}.logo{width:32px;height:32px}.word{font-size:25px}.word .of{font-size:25px}
.tag{margin:18px 0 0;width:100%;font-size:16px}
h2{margin:14px 0 0;font-weight:800;font-size:46px;line-height:1.07;letter-spacing:-.03em;color:#fff}
.lead{margin-top:16px;font-size:24px;line-height:1.36}
.feats{margin-top:30px;display:grid;grid-template-columns:1fr;gap:20px}
.chk{width:24px;height:24px;flex:none;margin-top:3px}
.ft{font-size:23px}.fl{font-size:20px;line-height:1.34;margin-top:6px}
.cta{position:absolute;left:36px;right:36px;bottom:36px;display:flex;flex-direction:column;gap:20px}
.btn{height:72px;justify-content:center;gap:12px;font-size:25px}
.arr{width:23px;height:23px}
.g{font-size:20px;line-height:1.4;text-align:center}
""", PITCH_BODY)


def render(name):
    w, h, html, crop = A[name]
    src = f"{SRC}/{name}.html"
    open(src, "w").write(html)
    out = f"{OUT}/{name}.png"
    if os.path.exists(out):
        os.remove(out)
    ud = f"{UD}/{name}"
    cmd = ["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
           f"--user-data-dir={ud}", "--allow-file-access-from-files", "--force-device-scale-factor=2",
           "--default-background-color=00000000", f"--window-size={w},{h}", "--virtual-time-budget=4000",
           f"--screenshot={out}", f"file://{src}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.exists(out):
        return f"{name} FAILED rc={r.returncode} {r.stderr[-300:]}"
    im = Image.open(out)
    if crop:
        im = im.crop(im.getchannel("A").getbbox())
    im.save(out, optimize=True)
    return f"{name} {im.size} {os.path.getsize(out)}"


names = sys.argv[1:] or list(A)
with ThreadPoolExecutor(max_workers=6) as ex:
    for line in ex.map(render, names):
        print(line)
