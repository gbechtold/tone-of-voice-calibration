#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guard the public repo against private data leaking in.

The blocklist itself lives in the PRIVATE repo (data/private-terms.txt) — putting
the names into the public repo to check for them would defeat the purpose.

Exit code 0 = clean, 1 = findings, 2 = blocklist missing.

Usage:
    check_public.py [--root DIR] [--terms FILE]
"""
import argparse
import os
import re
import sys

# Structural patterns — always checked, no blocklist needed.
STRUCTURAL = [
    (r"\+\d{2}[\s/-]?\d{3}[\s/-]?\d{2}[\s\d/-]{4,}", "Telefonnummer"),
    (r"\b[A-Za-z0-9._%+-]+@(?!example\.(com|org)\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "E-Mail-Adresse"),
    (r"\bAT\d{2}\s?\d{4}[\s\d]{8,}", "IBAN"),
    (r"\b(gho_|ghp_|sk-|cw_)[A-Za-z0-9_-]{10,}", "Token"),
]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "data"}
TEXT_EXT = {".md", ".py", ".sh", ".txt", ".yaml", ".yml", ".json", ".csv", ".html"}

def load_terms(path):
    if not os.path.exists(path):
        return None
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out

def scan(root, terms):
    findings = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            try:
                with open(full, encoding="utf-8") as fh:
                    lines = fh.readlines()
            except (UnicodeDecodeError, IOError):
                continue
            for n, line in enumerate(lines, 1):
                for pat, label in STRUCTURAL:
                    for m in re.finditer(pat, line):
                        findings.append((rel, n, label, m.group(0)[:48]))
                for term in terms:
                    if re.search(r"\b%s\b" % re.escape(term), line, re.I):
                        findings.append((rel, n, "Blockliste", term))
    return findings

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_root = os.path.dirname(here)
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=default_root, help="öffentliches Repo (Default: dieses)")
    ap.add_argument("--terms", default=os.path.join(default_root, os.pardir, "data", "private-terms.txt"))
    a = ap.parse_args()

    terms = load_terms(a.terms)
    if terms is None:
        print("FEHLER: Blockliste nicht gefunden: %s" % a.terms, file=sys.stderr)
        print("Das private Submodul ist nicht ausgecheckt. Ohne Blockliste keine Prüfung.",
              file=sys.stderr)
        return 2

    findings = scan(a.root, terms)
    if not findings:
        print("Sauber: %d Begriffe und %d Strukturmuster geprüft, kein Treffer in %s"
              % (len(terms), len(STRUCTURAL), os.path.relpath(a.root)))
        return 0
    print("%d Treffer — NICHT committen:\n" % len(findings))
    for rel, n, label, tok in findings:
        print("  %s:%d  [%s]  %s" % (rel, n, label, tok))
    print("\nAnonymisieren, dann erneut prüfen.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
