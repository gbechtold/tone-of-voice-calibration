#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PostToolUse hook for mcp__claude_ai_Gmail__create_draft.

Gmail deletes a draft once it is sent, so the sent message can never be diffed against
what was proposed. This stores a copy of every draft, so the `tov` skill can later
compare it with what was actually sent and learn from the difference.

Reads the hook payload on stdin. Never fails the tool call: always exits 0.

Usage (hook):  python3 draft_snapshot.py
Test:          echo '{"tool_input":{...}}' | python3 draft_snapshot.py --verbose
"""
import html
import json
import os
import re
import sys
import time

SNAP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "data", "_snapshots")
RETENTION_DAYS = 90

def dig(d, *keys):
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return None
    return d

def find_any(node, names, depth=0):
    """Search the whole payload for the first of `names` that carries a value.

    The hook payload does not always nest the tool result under the key we expect:
    the first live draft on 28.09.2026 produced draft_id=None although the API had
    returned an id. Searching recursively makes the hook independent of the exact
    envelope shape.
    """
    if depth > 6 or node is None:
        return None
    if isinstance(node, dict):
        for n in names:
            v = node.get(n)
            if isinstance(v, (str, int)) and str(v).strip():
                return str(v)
        for v in node.values():
            found = find_any(v, names, depth + 1)
            if found:
                return found
    elif isinstance(node, list):
        for v in node:
            found = find_any(v, names, depth + 1)
            if found:
                return found
    return None

def html_to_text(raw_html):
    # Parameter NICHT "html" nennen: das würde das Modul html verdecken und
    # html.unescape() unten mit AttributeError sprengen — den der Hook still
    # verschluckt, sodass Snapshots dauerhaft ausbleiben.
    t = re.sub(r"<br\s*/?>", "\n", raw_html)
    t = re.sub(r"</(p|div)>", "\n", t)
    t = re.sub(r"<a [^>]*?>(.*?)</a>", r"\1", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    # html.unescape statt einer Handliste: &uuml; und &szlig; fehlten und landeten
    # roh im Snapshot, was jede spätere Messung verfälscht hätte.
    t = html.unescape(t)
    t = t.replace("\u00a0", " ")
    return re.sub(r"\n{3,}", "\n\n", t).strip()

def prune(verbose=False):
    cutoff = time.time() - RETENTION_DAYS * 86400
    for fn in os.listdir(SNAP_DIR):
        if not fn.endswith(".json"):
            continue
        full = os.path.join(SNAP_DIR, fn)
        try:
            if os.path.getmtime(full) < cutoff:
                os.remove(full)
                if verbose:
                    print("entfernt (älter als %d Tage): %s" % (RETENTION_DAYS, fn))
        except OSError:
            pass

def main():
    verbose = "--verbose" in sys.argv
    try:
        raw = sys.stdin.read()
    except Exception:
        return 0
    if not raw or not raw.strip():
        return 0
    try:
        data = json.loads(raw)
    except ValueError:
        if verbose:
            print("kein JSON auf stdin — übersprungen", file=sys.stderr)
        return 0

    inp = dig(data, "tool_input") or dig(data, "toolInput") or {}
    res = dig(data, "tool_response") or dig(data, "toolResponse") or {}
    if not isinstance(res, dict):
        res = {}
    body = inp.get("htmlBody") or inp.get("body") or ""
    snap = {
        "created": time.strftime("%Y%m%d-%H%M%S"),
        "to": inp.get("to"), "cc": inp.get("cc"),
        "subject": inp.get("subject"),
        "was_html": bool(inp.get("htmlBody")),
        "body_text": html_to_text(body) if inp.get("htmlBody") else body.strip(),
        "draft_id": res.get("id") or res.get("draftId") or find_any(data, ["draftId", "id"]),
        "thread_id": (res.get("threadId") or inp.get("threadId")
                      or find_any(data, ["threadId", "messageId"])),
        "matched": False,
    }
    # Diagnose: Wenn die IDs fehlen, halten wir die STRUKTUR der Payload fest,
    # nicht ihren Inhalt. Zwei echte Drafts am 28.09.2026 kamen ohne draft_id an,
    # obwohl die API sie zurueckgab. Vermutung: Die Payload traegt nur tool_input.
    # Nur Schluesselnamen, keine Werte - die Payload enthaelt Kundendaten.
    if not snap["draft_id"] and not snap["thread_id"]:
        def shape(node, depth=0):
            if depth > 2 or not isinstance(node, dict):
                return type(node).__name__
            return {k: shape(v, depth + 1) for k, v in sorted(node.items())}
        snap["_payload_shape"] = shape(data)

    if not snap["subject"] and not snap["body_text"]:
        if verbose:
            print("leerer Draft — nichts gespeichert", file=sys.stderr)
        return 0
    try:
        if not os.path.isdir(SNAP_DIR):
            os.makedirs(SNAP_DIR)
        out = os.path.join(SNAP_DIR, "%s.json" % snap["created"])
        n = 1
        while os.path.exists(out):
            out = os.path.join(SNAP_DIR, "%s-%d.json" % (snap["created"], n))
            n += 1
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(snap, fh, indent=1, ensure_ascii=False)
        if verbose:
            print("gespeichert: %s (%d Zeichen Text)" % (out, len(snap["body_text"])))
        prune(verbose)
    except Exception as exc:
        if verbose:
            print("Fehler beim Speichern: %s" % exc, file=sys.stderr)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)   # ein Hook darf den Tool-Call nie scheitern lassen
