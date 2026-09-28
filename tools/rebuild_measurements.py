#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild data/measurements.csv from the pairs on disk.

The CSV is derived data: never edit it by hand. Run this after adding a pair so the
numbers always match what measure.py currently computes — otherwise a change to a
counting rule silently invalidates the whole series.

Usage: rebuild_measurements.py [--root DIR]
"""
import argparse, io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure import measure  # noqa: E402

AXES = "WOLKESF"

def profile_of(slug, mapping):
    return mapping.get(slug, "standard")

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(here), os.pardir, "data"))
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    pairs = os.path.join(root, "pairs")
    if not os.path.isdir(pairs):
        print("Kein pairs/-Verzeichnis unter %s" % root, file=sys.stderr)
        return 2
    # Profilzuordnung steht in jedem Paar-README als "Profil: <name>"
    rows = []
    for d in sorted(os.listdir(pairs)):
        p = os.path.join(pairs, d)
        if not os.path.isdir(p):
            continue
        prof = "standard"
        rm = os.path.join(p, "README.md")
        if os.path.exists(rm):
            for line in io.open(rm, encoding="utf-8"):
                if line.strip().lower().startswith("profil:"):
                    prof = line.split(":", 1)[1].split("·")[0].strip()
                    break
        b = measure(io.open(os.path.join(p, "before.txt"), encoding="utf-8").read())
        a2 = measure(io.open(os.path.join(p, "after.txt"), encoding="utf-8").read())
        if not b or not a2:
            print("übersprungen (nicht messbar): %s" % d, file=sys.stderr)
            continue
        rows.append([d[:10], d[11:], prof]
                    + [str(b["axes"][k]) for k in AXES] + [str(a2["axes"][k]) for k in AXES]
                    + [str(b["words"]), str(a2["words"]),
                       str(b["median_sentence"]), str(a2["median_sentence"]), "auto"])
    hdr = ("datum,paar,profil," + ",".join("%s_vor" % k for k in AXES) + ","
           + ",".join("%s_nach" % k for k in AXES)
           + ",woerter_vor,woerter_nach,median_vor,median_nach,quelle")
    out = os.path.join(root, "measurements.csv")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write("# generiert von tools/rebuild_measurements.py — nicht von Hand pflegen\n")
        f.write(hdr + "\n")
        for r in rows:
            f.write(",".join(r) + "\n")
    print("%d Paare geschrieben: %s" % (len(rows), out))
    return 0

if __name__ == "__main__":
    sys.exit(main())
