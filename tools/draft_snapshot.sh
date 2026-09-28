#!/usr/bin/env bash
# PostToolUse hook for mcp__claude_ai_Gmail__create_draft.
#
# Gmail deletes a draft once it is sent, so the sent version can never be compared
# against what was proposed. This stores a copy of every draft Claude creates, so the
# tov skill can later diff it against what Guntram actually sent.
#
# Reads the hook payload on stdin, writes one JSON file per draft. Never fails the
# tool call: always exits 0.
set -uo pipefail

SNAP_DIR="/Users/guntrambechtold/Documents/Projects/260928-ToneOfVoice/data/_snapshots"
RETENTION_DAYS=90

payload=$(cat 2>/dev/null || true)
[ -z "$payload" ] && exit 0
mkdir -p "$SNAP_DIR" 2>/dev/null || exit 0

STAMP=$(date +%Y%m%d-%H%M%S)
OUT="$SNAP_DIR/$STAMP.json"

python3 - "$OUT" <<'PY' <<<"$payload" 2>/dev/null || exit 0
import json, sys, os, re
out = sys.argv[1]
try:
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip().startswith("{") else {}
except Exception:
    data = {}

def dig(d, *keys):
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return None
    return d

inp = dig(data, "tool_input") or dig(data, "toolInput") or {}
res = dig(data, "tool_response") or dig(data, "toolResponse") or {}
body = inp.get("htmlBody") or inp.get("body") or ""
# htmlBody -> plain text, so compare.py sees the same shape as a sent message
text = re.sub(r"<br\s*/?>", "\n", body)
text = re.sub(r"</?(p|div)[^>]*>", "\n", text)
text = re.sub(r"<a [^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", r"\2", text, flags=re.S)
text = re.sub(r"<[^>]+>", "", text)
text = re.sub(r"\n{3,}", "\n\n", text).strip()

snap = {
    "created": os.path.basename(out).replace(".json", ""),
    "to": inp.get("to"), "cc": inp.get("cc"),
    "subject": inp.get("subject"),
    "body_text": text,
    "draft_id": (res or {}).get("id") or (res or {}).get("draftId"),
    "thread_id": (res or {}).get("threadId") or inp.get("threadId"),
    "matched": False,
}
if not snap["subject"] and not snap["body_text"]:
    sys.exit(0)
with open(out, "w", encoding="utf-8") as fh:
    json.dump(snap, fh, indent=1, ensure_ascii=False)
PY

# Kundendaten nicht endlos liegen lassen
find "$SNAP_DIR" -name '*.json' -type f -mtime "+$RETENTION_DAYS" -delete 2>/dev/null || true
exit 0
