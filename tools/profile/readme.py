"""Write the profile README. Usage: readme.py REF OUTFILE  (REF = branch whose raw assets the banner loads).
The House Notes list and the upstream line start as placeholders between markers. refresh.py fills them, and the
daily Action in .github/workflows/refresh.yml keeps them current."""
import hashlib
import os
import sys

ref, outfile = sys.argv[1], sys.argv[2]
RAW_BASE = f"https://raw.githubusercontent.com/StartupBros/startupbros/{ref}/assets/v4"
ASSETS = os.path.join(os.path.dirname(os.path.abspath(outfile)), "assets", "v4")
PLACEHOLDER = "(filled in by tools/profile/refresh.py)"


def raw(fname):
    """Raw URL with a content hash, so GitHub's image proxy refetches a card whose file name stayed the same."""
    with open(os.path.join(ASSETS, fname), "rb") as f:
        return f"{RAW_BASE}/{fname}?v={hashlib.sha1(f.read()).hexdigest()[:8]}"


def utm(url, campaign):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}utm_source=github&utm_medium=profile&utm_campaign={campaign}"


def pic(name, alt, width="100%"):
    return ('<picture>'
            f'<source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="{raw(name + "_mk.png")}">'
            f'<source media="(max-width: 600px)" srcset="{raw(name + "_m.png")}">'
            f'<source media="(prefers-color-scheme: dark)" srcset="{raw(name + "_dk.png")}">'
            f'<img src="{raw(name + "_d.png")}" width="{width}" alt="{alt}"></picture>')


HOV = "https://houseofvibe.ai/"
BLOG = "https://houseofvibe.ai/blog"
WM = "https://willmitchell.com/"
STACK = "https://github.com/StartupBros-com/hov-stack"
VIBERANK = "https://www.viberank.app/profile/StartupBros"
BANNER_ALT = ("Will Mitchell. Helping people with day jobs build real things with AI. Founder of StartupBros and "
              "House of Vibe, 9,000+ entrepreneurs served since 2012. Build Your First Thing.")
OSS = [  # pinned repos after hov-stack, in pin order
    ("StartupBros/hov-router", "use your AI accounts from one place in Claude Code, and see which account handled "
     "each request. My fork of tombii/better-ccflare, where most of the upstream pull requests below started."),
    ("StartupBros-com/synthetic-panel", "test marketing copy against AI customer personas, scored on your machine. "
     "No API key."),
    ("StartupBros-com/house-of-vibe", "scripts, checkers and tests from House Notes posts, one folder per post."),
]
oss = "\n".join(f"- [{r.split('/')[1]}](https://github.com/{r}): {d}" for r, d in OSS)

readme = f"""<p align="center"><a href="{utm(HOV, "readme-banner")}">{pic("banner", BANNER_ALT)}</a></p>

# Hi, I'm Will

I've sold things online since I was 12. I started StartupBros in 2012, and now I'm building \
[House of Vibe]({utm(HOV, "readme-intro")}), where people with day jobs learn AI by building real things. \
I work in Claude Code 8 to 10 hours a day.

I also work with a small number of funded teams as a fractional AI co-founder: \
[willmitchell.com]({utm(WM, "readme-intro")}).

## What I'm working on

- [hov-stack]({STACK}): the Claude Code setup I work in every day. Rules, guards and 13 plugins you can install \
one at a time.
- #1 on [viberank]({VIBERANK}), with 520 billion tokens in Claude Code.
- Latest from [House Notes]({utm(BLOG, "readme-notes")}), the House of Vibe blog:
  <!-- house-notes:start -->
  - {PLACEHOLDER}
  <!-- house-notes:end -->

## Open source

{oss}

<!-- upstream:start -->
{PLACEHOLDER}
<!-- upstream:end -->

## Background

- StartupBros was one of the earliest Amazon FBA education companies, with 9,000+ clients since 2012.
- An 8-figure exit: an e-commerce brand I helped buy and grow.
- Lina Khan cited my Amazon ranking guide twice before she chaired the FTC: in the \
[Yale Law Journal](https://www.yalelawjournal.org/note/amazons-antitrust-paradox) and in Oxford's Digital Dominance \
([all citations](https://willmitchell.com/citations)).
- Quoted in [The New York Times](https://willmitchell.com/media-kit).
- Co-author of Self-Made U.

[X](https://x.com/startupbros) · [YouTube](https://youtube.com/startupbros) · \
[LinkedIn](https://www.linkedin.com/in/willmitchell/) · [willmitchell.com]({utm(WM, "readme-footer")})
"""

open(outfile, "w").write(readme)
print(outfile, readme.count("\n"), "lines")
