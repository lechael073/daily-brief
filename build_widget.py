#!/usr/bin/env python3
"""Build widget.json for the KWGT home-screen widget from a brief JSON file.

Usage: python3 build_widget.py <brief.json>   (writes widget.json next to this script)

The widget has a single text item reading the "w" key, so everything shown on
the home screen is decided here. Change the layout below instead of editing
the widget on the phone. Older keys are kept so existing formulas keep working.
"""
import json
import re
import os
import sys

LINK = "https://claude.ai/artifact/7Mi1uSSsgmThYHHEqMzhD7"
ARROW = {"up": "▲", "down": "▼", "flat": "–"}
# KWGT BBCode colours (Korean convention: up = red, down = blue)
COLOR = {"up": "#FF6B61", "down": "#6EA4FF", "flat": "#AAAAAA"}

# ---- layout settings: edit these to change what the widget shows ----
N_STORIES = 8          # how many issues to list
SHOW_SUMMARY = False   # add the one-line summary under each issue
MARKETS = [0, 1, 2, 3, 4, 5]  # which markets to show (index into markets)
PAIR_MARKETS = True    # two markets per line, right column roughly aligned
SHORT = {"미 10년물": "미 10년물", "미 2년물": "미 2년물", "미 기준금리": "미 금리",
         "한은 기준금리": "한은 금리", "S&P 500": "S&P500", "코스피": "코스피"}


def em_width(text):
    """Rough rendered width in em (Hangul ~1em, digits/latin ~0.56em)."""
    w = 0.0
    for ch in re.sub(r"\[/?[a-z]+(=[^\]]*)?\]", "", text):
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F:
            w += 0.95
        elif ch in "▲▼":
            w += 0.8
        elif ch in " ":
            w += 0.25
        elif ch in ".,:·'":
            w += 0.27
        elif ch in "%&–":
            w += 0.65
        else:
            w += 0.56
    return w


def pad_to(text, target):
    """Pad with ideographic (1em), en (0.5em) and thin (~0.2em) spaces."""
    gap = max(target - em_width(text), 0.5)
    out = "\u3000" * int(gap)
    gap -= int(gap)
    if gap >= 0.5:
        out += "\u2002"
        gap -= 0.5
    out += "\u2009" * round(gap / 0.2)
    return text + out


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
    rows = [markets[i] for i in MARKETS if i < len(markets)]
    if PAIR_MARKETS:
        def cell(m, color=True):
            m2 = dict(m, label=SHORT.get(m.get("label", ""), m.get("label", "")))
            return mline(m2, color)
        left = [cell(m) for m in rows[0::2]]
        right = [cell(m) for m in rows[1::2]]
        col = max(em_width(c) for c in left) + 1.2
        mk = "\n".join(pad_to(l, col) + r for l, r in zip(left, right + [""] * len(left)))
    else:
        mk = "\n".join(mline(m) for m in rows)
    asof = f'[c=#AAAAAA][s=0.8]{w["asof"]}[/s][/c]'
    issues = []
    for s in stories[:N_STORIES]:
        tag = s.get("tagLabel", "")
        if s.get("breaking") or "속보" in tag:
            tag = f"[c=#FF6B61]{tag}[/c]"
        line = f'• [b]{tag}[/b] {s.get("title", "")}'
        if SHOW_SUMMARY and s.get("summary"):
            line += f'\n   [c=#BBBBBB][s=0.85]{s["summary"]}[/s][/c]'
        issues.append(line)
    w["w"] = "\n".join([top, head, "", mk, asof, "", *issues])

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "widget.json")
    json.dump(w, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(w["w"])


if __name__ == "__main__":
    main(sys.argv[1])
