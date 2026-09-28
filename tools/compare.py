#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare a draft against the sent version and report what changed per axis.

Usage:
    compare.py BEFORE AFTER [--json] [--label NAME]

Produces the axis deltas plus the phrase-level evidence a human needs to
decide whether a rule should change: which formulations were dropped, which
were added, and which substance appeared that the draft did not have.
"""
import argparse
import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure import measure, _strip_quote, _sentences  # noqa: E402

AXIS_NAMES = {
    "W": "Wärme", "O": "Optimismus", "L": "Lastverteilung", "K": "Kompaktheit",
    "E": "Explizitheit", "S": "Struktur", "F": "Führung",
}

def _norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()

def phrase_diff(before, after):
    """Sentences dropped and added, matched loosely so rewrites show up as pairs."""
    b = _sentences(_strip_quote(before))
    a = _sentences(_strip_quote(after))
    bn, an = [_norm(x) for x in b], [_norm(x) for x in a]
    sm = difflib.SequenceMatcher(None, bn, an)
    dropped, added, rewritten = [], [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "delete":
            dropped.extend(b[i1:i2])
        elif tag == "insert":
            added.extend(a[j1:j2])
        elif tag == "replace":
            olds, news = b[i1:i2], a[j1:j2]
            for k, o in enumerate(olds):
                best, score = None, 0.0
                for n in news:
                    r = difflib.SequenceMatcher(None, _norm(o), _norm(n)).ratio()
                    if r > score:
                        best, score = n, r
                if best and score > 0.45:
                    rewritten.append((o, best, round(score, 2)))
                else:
                    dropped.append(o)
            for n in news:
                if not any(n is x[1] for x in rewritten):
                    added.append(n)
    return dropped, added, rewritten

def new_substance(before, after):
    """Concrete detail present in the sent version but not in the draft."""
    pats = [
        (r"\+\d{2}[\d /-]{6,}", "Telefonnummer"),
        (r"\b\d{1,2}\.\d{1,2}\.(\d{2,4})?\b", "Datum"),
        (r"\b\d{1,2}:\d{2}\b", "Uhrzeit"),
        (r"\(([^)]{3,40})\)", "Klammer-Präzisierung"),
        (r"\b\d+[.,]?\d*\s?(€|Euro)\b", "Betrag"),
    ]
    out = []
    for p, label in pats:
        b = set(re.findall(p, before))
        for m in re.finditer(p, after):
            tok = m.group(0)
            if tok not in before:
                out.append((label, tok.strip()))
    seen, uniq = set(), []
    for label, tok in out:
        if (label, tok) not in seen:
            seen.add((label, tok))
            uniq.append((label, tok))
    return uniq

def compare(before_raw, after_raw, label="Paar"):
    mb, ma = measure(before_raw, "vorher"), measure(after_raw, "nachher")
    dropped, added, rewritten = phrase_diff(before_raw, after_raw)
    return {
        "label": label, "before": mb, "after": ma,
        "axis_delta": {k: ma["axes"][k] - mb["axes"][k] for k in "WOLKESF"},
        "dropped": dropped, "added": added,
        "rewritten": [{"from": o, "to": n, "similarity": s} for o, n, s in rewritten],
        "new_substance": new_substance(_strip_quote(before_raw), _strip_quote(after_raw)),
    }

def render(c):
    mb, ma, d = c["before"], c["after"], c["axis_delta"]
    print("=" * 78)
    print("%s" % c["label"])
    print("=" * 78)
    print("%-14s %-22s %-22s" % ("", "vorher", "nachher"))
    print("%-14s %-22s %-22s" % ("Regler",
          " ".join("%s%d" % (k, mb["axes"][k]) for k in "WOLKESF"),
          " ".join("%s%d" % (k, ma["axes"][k]) for k in "WOLKESF")))
    moved = {k: v for k, v in d.items() if v}
    if moved:
        print("%-14s %s" % ("Bewegt", ", ".join(
            "%s %s %+d" % (k, AXIS_NAMES[k], v) for k, v in sorted(moved.items(), key=lambda x: -abs(x[1])))))
    for key, lab, fmt in (("words", "Wörter", "%d"), ("median_sentence", "Median Satz", "%d"),
                          ("bullets", "Bullets", "%d"), ("conditionals", "Konditionale", "%d"),
                          ("bring_requests", "Bring-Bitten", "%d"), ("questions", "Fragen", "%d"),
                          ("fillers", "Floskeln", "%d"), ("substance_markers", "Substanz", "%d")):
        print("%-14s %-22s %-22s" % (lab, fmt % mb[key], fmt % ma[key]))
    if c["new_substance"]:
        print("\nNeu eingesetzte Substanz (war im Draft nicht drin):")
        for lab, tok in c["new_substance"]:
            print("  + %-24s %s" % (lab, tok))
    if c["rewritten"]:
        print("\nUmformuliert:")
        for r in c["rewritten"]:
            print("  \U0001F534 %s" % r["from"])
            print("  \U0001F7E2 %s" % r["to"])
            print()
    if c["dropped"]:
        print("Ersatzlos gestrichen:")
        for s in c["dropped"]:
            print("  - %s" % s)
        print()
    if c["added"]:
        print("Neu hinzugefügt:")
        for s in c["added"]:
            print("  + %s" % s)

def main():
    ap = argparse.ArgumentParser(description="Vergleiche Draft gegen gesendete Fassung.")
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--label", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    before = open(a.before, encoding="utf-8").read()
    after = open(a.after, encoding="utf-8").read()
    label = a.label or "%s → %s" % (os.path.basename(a.before), os.path.basename(a.after))
    c = compare(before, after, label)
    if a.json:
        print(json.dumps(c, indent=2, ensure_ascii=False))
    else:
        render(c)

if __name__ == "__main__":
    main()
