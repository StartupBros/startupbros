"""Download the card fonts (latin subsets of Inter, DM Sans, JetBrains Mono, Instrument Serif) from Google Fonts
and write local.css pointing at the downloaded files. Skips the download when local.css already exists.
Usage: fonts.py OUTDIR"""
import pathlib
import re
import sys
import urllib.request

CSS = ("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900"
       "&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400"
       "&family=JetBrains+Mono:wght@400;600&family=Instrument+Serif:ital@1&display=swap")
# Google Fonts serves woff2 only to browsers it recognizes.
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()


d = pathlib.Path(sys.argv[1]).resolve()
d.mkdir(parents=True, exist_ok=True)
if (d / "local.css").exists():
    print("fonts: cached in", d)
    sys.exit(0)
css = get(CSS).decode()
faces = []
for subset, body in re.findall(r"/\*\s*([a-z-]+)\s*\*/\s*@font-face\s*\{([^}]*)\}", css):
    if subset != "latin":
        continue
    fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
    style = re.search(r"font-style:\s*(\w+)", body).group(1)
    wght = re.search(r"font-weight:\s*([\d ]+);", body).group(1).strip()
    url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
    p = d / f"{fam.replace(' ', '')}-{style}-{wght.replace(' ', '_')}.woff2"
    if not p.exists():
        p.write_bytes(get(url))
    faces.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{wght};"
                 f"src:url('{p}') format('woff2');}}")
if len(faces) < 13:
    sys.exit(f"fonts: expected 13 latin faces, got {len(faces)}; Google Fonts output changed")
(d / "local.css").write_text("\n".join(faces) + "\n")
print("fonts:", len(faces), "faces in", d)
