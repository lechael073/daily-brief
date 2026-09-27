#!/usr/bin/env python3
"""Build widget.json for the KWGT home-screen widget from a brief JSON file.

Usage: python3 build_widget.py <brief.json>   (writes widget.json next to this script)

The widget has a single text item reading the "w" key, so everything shown on
the home screen is decided here. Change the layout below instead of editing
the widget on the phone. Older keys are kept so existing formulas keep working.
"""
import json
import os
import sys

LINK = "https://claude.ai/artifact/7Mi1uSSsgmThYHHEqMzhD7"
ARROW = {"up": "▲", "down": "▼", "flat": "–"}
# KWGT BBCode colours (Korean convention: up = red, down = blue)
COLOR = {"up": "#FF6B61", "down": "#6EA4FF", "flat": "#AAAAAA"}

# ---- layout settings: edit these to change what the widget shows ----
N_STORIES = 4          # how many issues to list
SHOW_SUMMARY = False   # add the one-line summary under each issue
MARKETS = [0, 1, 2, 3, 4, 5]  # which market rows to show (index into markets)


def main(path):
    b = json.load(open(path, encoding="utf-8"))
    markets = b.get("markets", [])
    stories = b.get("stories", [])

    def mline(m, color=True):
        d = m.get("dir", "flat")
        arrow = ARROW.get(d, "–")
        if color:
            arrow = f"[c={COLOR.get(d, '#AAAAAA')}]{arrow}[/c]"
        return f'{m.get("label", "")} {m.get("value", "")} {arrow}'

    w = {
        "date": b.get("date", ""),
        "updated": b.get("updatedLabel", ""),
        "headline": b.get("headline", ""),
        "sub": b.get("subhead", ""),
        "asof": b.get("marketsAsOf", ""),
        "link": LINK,
    }
    for i, m in enumerate(markets[:6], 1):
        w[f"m{i}_label"] = m.get("label", "")
        w[f"m{i}_value"] = m.get("value", "")
        w[f"m{i}_dir"] = m.get("dir", "flat")
        w[f"m{i}_arrow"] = ARROW.get(m.get("dir", "flat"), "–")
    for i, s in enumerate(stories[:3], 1):
        w[f"s{i}"] = s.get("title", "")
    if len(markets) >= 6:
        w["mk"] = mline(markets[0], False) + "\n" + mline(markets[5], False)
    w["mk_all"] = "\n".join(mline(m, False) for m in markets[:6])
    w["st"] = "\n".join(f'• [{s.get("tagLabel", "")}] {s.get("title", "")}' for s in stories[:4])
    w["st_sum"] = "\n\n".join(
        f'[{s.get("tagLabel", "")}] {s.get("title", "")}\n{s.get("summary", "")}' for s in stories[:3]
    )

    # ---- the single combined text the widget shows ----
    kicker = b.get("kicker", "")
    top = f'[c=#AAAAAA][s=0.8]{"속보 · " if kicker == "속보" else ""}갱신 {w["updated"]}[/s][/c]'
    head = f'[b][s=1.3]{w["headline"]}[/s][/b]'
    mk = "\n".join(mline(markets[i]) for i in MARKETS if i < len(markets))
    asof = f'[c=#AAAAAA][s=0.8]{w["asof"]}[/s][/c]'
    issues = []
    for s in stories[:N_STORIES]:
        line = f'• [b]{s.get("tagLabel", "")}[/b] {s.get("title", "")}'
        if SHOW_SUMMARY and s.get("summary"):
            line += f'\n   [c=#BBBBBB][s=0.85]{s["summary"]}[/s][/c]'
        issues.append(line)
    w["w"] = "\n".join([top, head, "", mk, asof, "", *issues])

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "widget.json")
    json.dump(w, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(w["w"])


if __name__ == "__main__":
    main(sys.argv[1])
