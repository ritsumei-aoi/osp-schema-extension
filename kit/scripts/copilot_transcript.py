#!/usr/bin/env python3
"""copilot_transcript.py — Readable transcript of a GitHub Copilot CLI session.

Usage:
    python3 scripts/copilot_transcript.py <events.jsonl> > transcript.md

Writes user messages and assistant replies in full, and one line per tool
call (name and arguments, truncated). Opaque reasoning is omitted. The
events.jsonl file itself is the primary record; this is only a reading aid.
"""
import json
import sys

LIMIT = 300


def short(obj):
    s = json.dumps(obj, ensure_ascii=False)
    return s if len(s) <= LIMIT else s[:LIMIT] + " …"


def main(path):
    events = [json.loads(line) for line in open(path, encoding="utf-8")]
    results = {}
    for e in events:
        if e["type"] == "tool.execution_complete":
            results[e["data"].get("toolCallId")] = e["data"]
    print(f"# Copilot CLI session transcript\n\nSource: `{path}`\n")
    for e in events:
        t, d, ts = e["type"], e.get("data", {}), e.get("timestamp", "")
        if t == "session.start":
            print(f"- {ts} session.start (Copilot {d.get('copilotVersion')}, cwd {d.get('context', {}).get('cwd')})")
        elif t == "session.model_change":
            print(f"- {ts} model: {d.get('previousModel')} -> {d.get('newModel')} ({d.get('reasoningEffort')})")
        elif t == "user.message":
            print(f"\n## USER ({ts})\n\n```text\n{d.get('content', '')}\n```\n")
        elif t == "assistant.message" and d.get("content", "").strip():
            print(f"\n### ASSISTANT ({ts})\n\n{d['content']}\n")
        elif t == "tool.execution_start":
            name = d.get("toolName")
            print(f"- {ts} tool `{name}` {short(d.get('arguments'))}")
            if name == "ask_user":
                r = results.get(d.get("toolCallId"))
                print(f"  - ask_user result: {short(r.get('result') if r else None)}")
        elif t in ("permission.requested", "session.shutdown", "abort"):
            print(f"- {ts} {t} {short(d)}")


if __name__ == "__main__":
    main(sys.argv[1])
