"""Write the profile README. Usage: readme.py REF OUTFILE  (REF = branch whose raw assets the <picture> sources load).
Cards carry four sources: phone+dark, phone, dark, and the light desktop default."""
import hashlib
import os
import sys

ref, outfile = sys.argv[1], sys.argv[2]
RAW_BASE = f"https://raw.githubusercontent.com/StartupBros/startupbros/{ref}/assets/v4"
ASSETS = os.path.join(os.path.dirname(os.path.abspath(outfile)), "assets", "v4")


def raw(fname):
    """Raw URL with a content hash, so GitHub's image proxy refetches a card whose file name stayed the same."""
    with open(os.path.join(ASSETS, fname), "rb") as f:
        return f"{RAW_BASE}/{fname}?v={hashlib.sha1(f.read()).hexdigest()[:8]}"


def utm(url, campaign):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}utm_source=github&utm_medium=profile&utm_campaign={campaign}"


HOV = "https://houseofvibe.ai/"
BLOG = "https://houseofvibe.ai/blog"
ORG = "https://github.com/StartupBros-com"
STACK = f"{ORG}/hov-stack"
PLUGS = f"{STACK}/tree/main/plugins"
VIBERANK = "https://www.viberank.app/profile/StartupBros"


def pic(name, alt, width="100%"):
    return ('<picture>'
            f'<source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="{raw(name + "_mk.png")}">'
            f'<source media="(max-width: 600px)" srcset="{raw(name + "_m.png")}">'
            f'<source media="(prefers-color-scheme: dark)" srcset="{raw(name + "_dk.png")}">'
            f'<img src="{raw(name + "_d.png")}" width="{width}" alt="{alt}"></picture>')


def block(href, name, alt):
    return f'<p align="center"><a href="{href}">{pic(name, alt)}</a></p>'


def pill(href, name, alt):
    return (f'<a href="{href}"><picture><source media="(prefers-color-scheme: dark)" srcset="{raw(name + "_k.png")}">'
            f'<img src="{raw(name + ".png")}" height="34" alt="{alt}"></picture></a>')


def plug(name):
    return f'<a href="{PLUGS}/{name}"><b>{name}</b></a>'


FEATURED = [
    ("memory-dream", "A sleep cycle for Claude Code's auto-memory. Finds stale, superseded and oversized notes, and writes only the changes you approve."),
    ("papercut", "Logs every hard tool failure your agents route around, then ranks them into fixes it won't call verified on silence alone."),
    ("skill-tuner", "Tells you whether an edit to a SKILL.md, AGENTS.md or CLAUDE.md actually worked, with a paired comparison."),
    ("token-eater", "Spends AI credits that are about to expire on isolated, verified cleanup. Opens a draft PR and never merges."),
    ("design-rails", "Derives a DESIGN.md from the code you already have and keeps agents on it, with drift budgets that only move down."),
    ("wsl-cdp", "Lets Claude Code inside WSL2 drive your real, logged-in Windows browser, to read dashboards and take real screenshots."),
]
MORE = [
    ("rent-check", "Audits CLAUDE.md, AGENTS.md and rules files. Every always-loaded line pays rent or gets cut."),
    ("harness-vet", "An adoption gate for outside skills, plugins and MCP servers, judged against your own setup."),
    ("harness-optimizer", "Investigates recurring setup problems, then challenges its own diagnosis before it changes anything."),
    ("pro-gate", "A final pull request review by the Pro model on your ChatGPT account. No automatic merge."),
    ("sign-it", "Type /sign-it with a PDF and get it back signed with your stored signature. Never a counterparty's."),
    ("product-video", "Records a real browser tour of your product and renders it as a walkthrough video."),
    ("hov-stack", "The whole skill pack as one plugin."),
]
OSS = [  # (owner/repo, what it does); archived repos stay off this list
    ("StartupBros/hov-router", "Use all your AI accounts from one place, and see which account handled each request, with usage, costs and errors in a dashboard."),
    ("StartupBros-com/renpho-mcp-server", "Ask Claude, Cursor or any MCP client about your weight, body fat and muscle mass from a Renpho smart scale."),
    ("StartupBros-com/hass-renpho-health", "The same Renpho scale data inside Home Assistant, as an integration you add through HACS."),
    ("StartupBros-com/synthetic-panel", "Test marketing copy against AI customer personas, scored locally. No API key needed."),
]
NOTES = [
    ("20 vs 17", "checks passed<br>first time", "ChatGPT Plus vs Claude Pro: which plan to keep if you don't code", f"{BLOG}/chatgpt-plus-vs-claude-pro",
     "Both finished our four everyday jobs. ChatGPT passed 20 of 20 checks first time, Claude 17, then 20 after two follow-ups.", "Oct 25"),
    ("24 vs 20", "jobs done,<br>curl vs CLI", "Cloudflare's new CLI or plain curl for your coding agent", f"{BLOG}/cloudflare-cli-or-curl-for-coding-agents",
     "Plain curl went 24 of 24. The new CLI went 20 of 24 and called its help flag 76 times.", "Oct 5"),
    ("5 → 14", "right answers,<br>of 16", "Find the Claude Code memories your MEMORY.md no longer reaches", f"{BLOG}/claude-code-auto-memory",
     "The agent reached for 11 memory files that don't exist. One archive file and one pointer line took it from 5 answers to 14.", "Oct 4"),
]


def table(head, rows, first_attrs="nowrap"):
    """HTML table: the first column never wraps, so hyphenated names stay whole on every width."""
    out = ["<table>", f"<tr><th>{head[0]}</th><th>{head[1]}</th></tr>"]
    out += [f"<tr><td {first_attrs}>{a}</td><td>{b}</td></tr>" for a, b in rows]
    return "\n".join(out + ["</table>"])


parts = []
parts.append(block(utm(HOV, "readme-banner"), "banner",
                   "Will Mitchell. Helping people with day jobs build real things with AI. Founder of StartupBros and House of Vibe, 9,000+ entrepreneurs served since 2012. Build Your First Thing."))
parts.append('<p align="center">\n' + "&nbsp;\n".join([
    pill(utm(HOV, "readme-links"), "pill_hov", "houseofvibe.ai"),
    pill(utm(BLOG, "readme-links"), "pill_notes", "House Notes"),
    pill("https://youtube.com/startupbros", "pill_yt", "YouTube, 34K subscribers"),
    pill("https://x.com/startupbros", "pill_x", "X, 16K followers"),
]) + "\n</p>")
parts.append('<p align="center">I\'ve sold online since 2002. In 2012 I started StartupBros, one of the earliest Amazon FBA education companies, '
             'and 9,000+ entrepreneurs have come through it. I\'ve built with AI full time since 2022. '
             f'Today I run <a href="{utm(HOV, "readme-intro")}">House of Vibe</a>, where members with day jobs build real things with AI.</p>')
parts.append(block(utm(HOV, "readme-proof"), "proof",
                   "Track record: 20+ years building internet businesses. Co-author of Self-Made U. Spoke at Techstars Startup Week and "
                   "Global Sources Summit Hong Kong. 9,000+ entrepreneurs served through StartupBros. Helped grow Simply Organic to an "
                   "8-figure company, per an SEC filing. My Amazon ranking guide is footnote 353 in Lina Khan's Amazon's Antitrust Paradox, "
                   "in the Yale Law Journal. Quoted in The New York Times and Reuters."))
parts.append('<p align="center">'
             f'<a href="{utm(HOV, "readme-fork")}">{pic("fork_hov", "Do not code? Finish your first project before dinner. House of Vibe members build real things with AI around their day jobs, 10 to 15 hours a week. Build Your First Thing.", "421")}</a>'
             f'<a href="{STACK}">{pic("fork_dev", "Write code? Get the Claude Code setup I run every day. hov-stack: the rules, guards and 13 plugins behind 4,302 merged PRs in 60 days. Free and MIT. Get hov-stack.", "421")}</a>'
             '</p>')
parts.append(block(VIBERANK, "stack",
                   "Public Claude Code leaderboards: #1 all-time on viberank, with 520 billion tokens logged in Claude Code. #2 all-time on ccrank, "
                   "#2 over the last 30 days on CCWarriors, and the top 2% all-time on tokscale. Read Nov 6, 2026."))
parts.append('<p align="center"><sub>Check each board yourself: '
             f'<a href="{VIBERANK}">viberank</a> · <a href="https://ccrank.dev/leaderboard">ccrank</a> · '
             '<a href="https://ccwarriors.xyz/StartupBros">CCWarriors</a> · <a href="https://tokscale.ai/u/startupbros">tokscale</a>. '
             'Each counts only what was submitted to it, so totals differ.'
             '<br>Plus 30,000+ GitHub contributions in the last year, on the graph below.</sub></p>')
parts.append("<br>")
parts.append('<h2 align="center">hov-stack</h2>')
parts.append('<p align="center">The setup behind those numbers: the rules, guards and plugins I run every day.</p>')
parts.append('<p align="center"><sub>MIT · 13 plugins · 4,302 pull requests merged across 17 repos in the 60 days to Oct 19, 2026'
             '<br>292 allow, 75 ask and 70 deny permission rules, grown from real refusals</sub></p>')
parts.append("Add the marketplace once, then install any plugin by name:")
parts.append("```sh\nclaude plugin marketplace add \\\n  StartupBros-com/hov-stack\nclaude plugin install papercut@hov\n```")
parts.append("Or from inside Claude Code: `/plugin marketplace add StartupBros-com/hov-stack`. If one saves you a mistake, a star on "
             f"[hov-stack]({STACK}) helps the next person find it.")
parts.append(table(("Plugin", "What it does"), [(plug(n), d) for n, d in FEATURED]))
parts.append("<details>\n<summary><b>7 more plugins</b></summary>\n\n"
             + table(("Plugin", "What it does"), [(plug(n), d) for n, d in MORE]) + "\n\n</details>")
parts.append('<h2 align="center">More open source</h2>')
parts.append(table(("Repo", "What it does"),
                   [(f'<a href="https://github.com/{r}"><b>{r.split("/")[1]}</b></a>', d) for r, d in OSS]))
parts.append('<h2 align="center">From House Notes</h2>')
parts.append(f'<p align="center">How-tos from the House of Vibe blog, each one measured before it goes up. <a href="{utm(BLOG, "readme-notes")}">Read them all</a>.</p>')
parts.append(table(("Result", "Note"),
                   [(f"<b>{st}</b><br><sub>{sl}</sub>", f'<a href="{utm(u, "readme-notes")}"><b>{t}</b></a><br>{r} <sub>{d}</sub>')
                    for st, sl, t, u, r, d in NOTES], first_attrs='align="center" nowrap'))
parts.append("<br>")
parts.append(block(utm(HOV, "readme-cta"), "pitch",
                   "House of Vibe. The window is open right now. Most people haven't noticed. The people in the House have. Projects you build. Not courses you watch. And you actually finish them. Day 1: watch it build something real before dinner. Day 7: replace what you're paying for. Built for day jobs: 10 to 15 hours a week, evenings and weekends. Live every month: training, then Q&A on every question. Build Your First Thing. The Open Door Guarantee: 30 days to try everything. Full refund if it's not for you. One payment, lifetime access."))
parts.append("""<details>
<summary><sub>Sources and read dates</sub></summary>

<br>

- Track record
  - 9,000+ entrepreneurs through StartupBros since 2012, by my own count. [willmitchell.com](""" + utm("https://willmitchell.com/", "readme-sources") + """) shows "9K+ Entrepreneurs Served".
  - Simply Organic: Yepp Enterprises' [SEC Form C](https://www.sec.gov/Archives/edgar/data/1884322/000167025421001082/document_2.pdf) (2021) lists me on its advisory team, as having "Helped acquire & grow e-commerce brand Simply Organic to an 8-figure company".
  - Footnote 353 of Lina Khan's [Amazon's Antitrust Paradox](https://www.yalelawjournal.org/note/amazons-antitrust-paradox), 126 Yale L.J. 710 (2017), cites my Amazon ranking guide, and so does Oxford's Digital Dominance (2018). All 11 citations: [willmitchell.com/citations](https://willmitchell.com/citations).
  - Quoted in The New York Times (2012) and Reuters (2013): [media kit](https://willmitchell.com/media-kit).
  - Co-author of Self-Made U (2013), with Kyle Eschenroeder.
  - Speaker at [Techstars Startup Week Tampa Bay](https://techstarsstartupweektampabay2018.sched.com/list/descriptions) (2018) and Global Sources Summit Hong Kong (2018 and 2019).
  - Selling online since 2002 and building with AI full time since 2022: [about](https://willmitchell.com/about).
- Leaderboards, read Nov 6, 2026. Each board counts only what was submitted to it, so totals differ.
  - [viberank](""" + VIBERANK + """): #1 all-time, with 520.0B Claude Code tokens logged, 93% of them cache reads.
  - [ccrank](https://ccrank.dev/leaderboard): #2 all-time, 295.1B tokens across Claude Code, Codex and other tools.
  - [CCWarriors](https://ccwarriors.xyz/StartupBros): #2 of 82 on the 30-day board.
  - [tokscale](https://tokscale.ai/u/startupbros): #40 of 2,442 all-time by tokens (479.8B), the top 2%.
- The pitch card quotes [houseofvibe.ai](""" + utm(HOV, "readme-sources") + """).
- Audience: 34.8K YouTube subscribers (Nov 6, 2026) and 16,293 followers on X (Nov 5, 2026).
- GitHub: 30,214 contributions in the last year (Nov 6, 2026), private ones included, as the profile's public graph counts them.
- hov-stack: 13 plugins in its marketplace, MIT licensed. Its [README](""" + STACK + """) reports 4,302 pull requests merged across 17 repos in the 60 days to Oct 19, 2026, and 292 allow, 75 ask and 70 deny permission entries.
- House Notes results are quoted from each post.

</details>""")
parts.append("---")
parts.append('<p align="center"><sub>Will Mitchell · '
             f'<a href="{utm(HOV, "readme-footer")}">houseofvibe.ai</a> · '
             '<a href="https://www.linkedin.com/in/willmitchell/">LinkedIn</a><br>'
             'I also embed with a small number of funded teams as a fractional AI co-founder: '
             f'<a href="{utm("https://willmitchell.com/", "readme-footer")}">willmitchell.com</a></sub></p>')

open(outfile, "w").write("\n\n".join(parts) + "\n")
print(outfile, sum(1 for _ in open(outfile)), "lines")
