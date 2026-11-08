"""Tests for refresh.py. Run: python3 -I -m unittest discover -s tools/profile -p 'test_*.py'"""
import collections
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refresh  # noqa: E402

FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>House Notes | House of Vibe</title><link>https://houseofvibe.ai/blog</link>
<item><title>Older post</title><link>https://houseofvibe.ai/blog/older</link><pubDate>Sat, 03 Oct 2026 00:00:00 GMT</pubDate></item>
<item><title>ChatGPT Plus vs Claude Pro: which $20 plan to keep if you don't code</title>
<link>https://houseofvibe.ai/blog/chatgpt-plus-vs-claude-pro</link><pubDate>Sun, 25 Oct 2026 00:00:00 GMT</pubDate></item>
<item><title>Last year's post</title><link>https://houseofvibe.ai/blog/last-year</link><pubDate>Wed, 31 Dec 2025 00:00:00 GMT</pubDate></item>
<item><title>Plant a decoy AWS key, not a flag.txt</title><link>https://houseofvibe.ai/blog/aws-decoy-key-alert</link><pubDate>Fri, 06 Nov 2026 00:00:00 GMT</pubDate></item>
</channel></rss>"""

README = """intro
  <!-- house-notes:start -->
  - (filled in by tools/profile/refresh.py)
  <!-- house-notes:end -->

<!-- upstream:start -->
(filled in by tools/profile/refresh.py)
<!-- upstream:end -->
tail
"""


def boom():
    raise OSError("network down")


class NotesTest(unittest.TestCase):
    def test_newest_first_with_dates_and_tracking(self):
        lines = refresh.notes_lines(FEED).split("\n")
        self.assertEqual(len(lines), 4)
        self.assertTrue(lines[0].startswith("  - [Plant a decoy AWS key, not a flag.txt](https://houseofvibe.ai/blog/aws-decoy-key-alert?utm_source=github"))
        self.assertTrue(lines[0].endswith(" · Nov 6"))
        self.assertIn("which \\$20 plan", lines[1])
        self.assertTrue(lines[2].endswith(" · Oct 3"))
        self.assertTrue(lines[3].endswith(" · Dec 31, 2025"))

    def test_keeps_only_five(self):
        items = "".join(f"<item><title>P{i}</title><link>https://houseofvibe.ai/blog/p{i}</link>"
                        f"<pubDate>Mon, {i:02d} Nov 2026 00:00:00 GMT</pubDate></item>" for i in range(1, 9))
        lines = refresh.notes_lines(f"<rss><channel>{items}</channel></rss>".encode()).split("\n")
        self.assertEqual([l.split("]")[0][5:] for l in lines], ["P8", "P7", "P6", "P5", "P4"])

    def test_refuses_foreign_links_and_empty_feeds(self):
        bad = b"<rss><channel><item><title>x</title><link>https://evil.example/blog/x</link><pubDate>Fri, 06 Nov 2026 00:00:00 GMT</pubDate></item></channel></rss>"
        self.assertRaises(ValueError, refresh.notes_lines, bad)
        self.assertRaises(ValueError, refresh.notes_lines, b"<rss><channel></channel></rss>")

    def test_markdown_in_titles_is_escaped(self):
        self.assertEqual(refresh.md_text("a [b](c) *d* <e>"), "a \\[b\\](c) \\*d\\* \\<e\\>")


class UpstreamTest(unittest.TestCase):
    def test_line_matches_the_approved_wording(self):
        c = collections.Counter({"tombii/better-ccflare": 27, "steipete/oracle": 5, "jundot/omlx": 3,
                                 "EveryInc/compound-engineering-plugin": 1, "apmantza/pi-lens": 1,
                                 "davebcn87/pi-autoresearch": 1, "chrisdoc/hevy-mcp": 1})
        q = "is%3Apr+author%3AStartupBros+is%3Amerged"
        self.assertEqual(refresh.upstream_line(c),
                         "Merged upstream: 39 pull requests across 7 projects, including "
                         f"[27 in tombii/better-ccflare](https://github.com/tombii/better-ccflare/pulls?q={q}), "
                         f"[5 in steipete/oracle](https://github.com/steipete/oracle/pulls?q={q}) and "
                         f"[3 in jundot/omlx](https://github.com/jundot/omlx/pulls?q={q}).")

    def test_small_counts_read_naturally(self):
        self.assertEqual(refresh.upstream_line(collections.Counter({"a/b": 1})),
                         "Merged upstream: [1 pull request in a/b]"
                         "(https://github.com/a/b/pulls?q=is%3Apr+author%3AStartupBros+is%3Amerged).")
        self.assertTrue(refresh.upstream_line(collections.Counter({"a/b": 2, "c/d": 1})).startswith(
            "Merged upstream: 3 pull requests across 2 projects: [2 in a/b]"))

    def test_refuses_zero_and_odd_names(self):
        self.assertRaises(ValueError, refresh.upstream_line, collections.Counter())
        self.assertRaises(ValueError, refresh.upstream_line, collections.Counter({"a/b) [x](y": 1}))


class RefreshTest(unittest.TestCase):
    def test_fills_both_parts_and_leaves_the_rest(self):
        text, warnings, unfilled = refresh.refresh(README, [("house-notes", lambda: "  - one\n  - two"),
                                                            ("upstream", lambda: "Merged upstream: x.")])
        self.assertEqual((warnings, unfilled), ([], []))
        self.assertEqual(text, README.replace("  - (filled in by tools/profile/refresh.py)", "  - one\n  - two")
                         .replace("\n(filled in by tools/profile/refresh.py)\n", "\nMerged upstream: x.\n"))
        again, _, _ = refresh.refresh(text, [("house-notes", lambda: "  - one\n  - two"),
                                             ("upstream", lambda: "Merged upstream: x.")])
        self.assertEqual(again, text)

    def test_a_failed_source_keeps_the_last_good_text(self):
        filled, _, _ = refresh.refresh(README, [("house-notes", lambda: "  - one"), ("upstream", lambda: "line")])
        text, warnings, unfilled = refresh.refresh(filled, [("house-notes", boom), ("upstream", lambda: "line 2")])
        self.assertIn("  - one\n", text)
        self.assertIn("\nline 2\n", text)
        self.assertEqual(unfilled, [])
        self.assertEqual(len(warnings), 1)
        self.assertTrue(warnings[0].startswith("house-notes: OSError"))

    def test_a_part_never_filled_is_reported(self):
        _, warnings, unfilled = refresh.refresh(README, [("house-notes", boom), ("upstream", lambda: "x")])
        self.assertEqual(unfilled, ["house-notes"])

    def test_missing_markers_stop_the_run(self):
        self.assertRaises(SystemExit, refresh.refresh, "no markers\n", [("upstream", lambda: "x")])


if __name__ == "__main__":
    unittest.main()
