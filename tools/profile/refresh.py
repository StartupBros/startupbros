"""Refresh the two generated parts of the profile README in place:
- the latest House Notes posts, read from the House of Vibe RSS feed, between the house-notes markers;
- the merged upstream pull request line, read from GitHub's search API, between the upstream markers.
A part keeps its last good text when its source can't be read, with a warning. The run fails only when a part
has never been filled. Standard library only, so the daily Action needs no install step.
Usage: refresh.py README.md   (sends GITHUB_TOKEN when it is set)"""
import collections
import email.utils
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

FEED = "https://houseofvibe.ai/blog/rss.xml"
POST = re.compile(r"https://houseofvibe\.ai/blog/[a-z0-9-]+/?")
REPO = re.compile(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+")
UA = "startupbros-profile-refresh (+https://github.com/StartupBros/startupbros)"
AUTHOR = "StartupBros"
QUERY = f"is:pr author:{AUTHOR} is:merged is:public -user:{AUTHOR} -org:StartupBros-com"
PLACEHOLDER = "filled in by tools/profile/refresh.py"
NOTES = 5
NAMED = 3
MAX_BYTES = 5_000_000


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError(f"{url} returned more than {MAX_BYTES} bytes")
    return body


def md_text(s):
    """One line of plain text, safe inside a Markdown link label. A bare $ would start GitHub math."""
    return re.sub(r"([\\`*_\[\]<>$])", r"\\\1", " ".join(s.split())[:200])


def utm(url):
    return f"{url}{'&' if '?' in url else '?'}utm_source=github&utm_medium=profile&utm_campaign=readme-notes"


def notes_lines(feed):
    """Markdown list lines for the newest posts in an RSS document (bytes)."""
    items = []
    for it in ET.fromstring(feed).iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        if not title or not POST.fullmatch(link):
            raise ValueError(f"unexpected feed item: title={title!r} link={link!r}")
        items.append((email.utils.parsedate_to_datetime((it.findtext("pubDate") or "").strip()), title, link))
    if not items:
        raise ValueError("the feed has no items")
    items.sort(key=lambda t: t[0], reverse=True)
    items = items[:NOTES]
    year = items[0][0].year
    out = []
    for date, title, link in items:
        when = f"{date:%b} {date.day}" + ("" if date.year == year else f", {date.year}")
        out.append(f"  - [{md_text(title)}]({utm(link)}) · {when}")
    return "\n".join(out)


def upstream_line(counts):
    """The one-sentence upstream summary for a Counter of merged pull requests per owner/repo."""
    total, projects = sum(counts.values()), len(counts)
    if not total:
        raise ValueError("no merged pull requests counted")
    for repo in counts:
        if not REPO.fullmatch(repo):
            raise ValueError(f"unexpected repository name {repo!r}")
    q = urllib.parse.quote_plus(f"is:pr author:{AUTHOR} is:merged")
    if projects == 1:
        (repo, n), = counts.items()
        return (f"Merged upstream: [{n} pull request{'' if n == 1 else 's'} in {md_text(repo)}]"
                f"(https://github.com/{repo}/pulls?q={q}).")
    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].lower()))[:NAMED]
    links = [f"[{n} in {md_text(r)}](https://github.com/{r}/pulls?q={q})" for r, n in top]
    named = ", ".join(links[:-1]) + " and " + links[-1]
    head = f"Merged upstream: {total} pull requests across {projects} projects"
    return f"{head}{', including' if projects > len(top) else ':'} {named}."


def upstream_counts(token):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    counts, total = collections.Counter(), None
    for page in range(1, 11):  # the search API stops at 1,000 results
        q = urllib.parse.urlencode({"q": QUERY, "per_page": 100, "page": page})
        d = json.loads(get(f"https://api.github.com/search/issues?{q}", headers))
        if d.get("incomplete_results"):
            raise ValueError("GitHub search returned incomplete results")
        total = d["total_count"]
        for item in d["items"]:
            counts[item["repository_url"].split("/repos/", 1)[1]] += 1
        if not d["items"] or sum(counts.values()) >= total:
            break
    if sum(counts.values()) != total:
        raise ValueError(f"counted {sum(counts.values())} of {total} pull requests")
    return counts


def span(text, name):
    """(start, end) of the lines between a marker pair; the markers' own lines stay put."""
    a, b = text.find(f"<!-- {name}:start -->"), text.find(f"<!-- {name}:end -->")
    if a < 0 or b < a:
        raise SystemExit(f"README is missing the {name} markers")
    start = text.index("\n", a) + 1
    end = text.rfind("\n", 0, b) + 1
    return start, end


def replace(text, name, body):
    start, end = span(text, name)
    return text[:start] + body.rstrip("\n") + "\n" + text[end:]


def refresh(text, sources):
    """Apply each (name, build) source to text. Returns (text, warnings, unfilled)."""
    warnings, unfilled = [], []
    for name, build in sources:
        start, end = span(text, name)
        try:
            text = replace(text, name, build())
        except Exception as e:  # noqa: BLE001 - any failure keeps the last good text
            warnings.append(f"{name}: {type(e).__name__}: {e}")
            if PLACEHOLDER in text[start:end]:
                unfilled.append(name)
    return text, warnings, unfilled


def main():
    path = sys.argv[1]
    old = open(path).read()
    token = os.environ.get("GITHUB_TOKEN")
    new, warnings, unfilled = refresh(old, [
        ("house-notes", lambda: notes_lines(get(FEED))),
        ("upstream", lambda: upstream_line(upstream_counts(token))),
    ])
    for w in warnings:
        print(f"::warning::{w}")
    if new != old:
        open(path, "w").write(new)
    print(path, "updated" if new != old else "unchanged")
    if unfilled:
        sys.exit(f"never filled: {', '.join(unfilled)}")


if __name__ == "__main__":
    main()
