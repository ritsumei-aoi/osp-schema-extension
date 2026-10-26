#!/usr/bin/env python3
"""claude_transcript.py — Readable transcript of a Claude Code session log.

Usage:
    python3 scripts/claude_transcript.py <session.jsonl> > transcript.md

Accepts both the interactive session file (~/.claude*/projects/<dir>/<id>.jsonl)
and the stream-json output of `claude -p` (one turn per file; .gz is accepted).
Writes user messages and assistant text in full, and one line per tool call
(name and arguments, truncated). Thinking is omitted. The .jsonl file itself is
the primary record; this is only a reading aid.
"""
import gzip
import json
import sys

LIMIT = 300


def short(obj):
    s = json.dumps(obj, ensure_ascii=False)
    return s if len(s) <= LIMIT else s[:LIMIT] + " …"


def main(path):
    opener = gzip.open if path.endswith(".gz") else open
    print(f"# Claude Code session transcript\n\nSource: `{path}`\n")
    with opener(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            t, ts = e.get("type"), e.get("timestamp", "")
            if t == "system" and e.get("subtype") == "init":
                print(f"- session init: model {e.get('model')}, permissionMode {e.get('permissionMode')}, "
                      f"mcp {e.get('mcp_servers')}, cwd {e.get('cwd')}")
            elif t == "system" and e.get("subtype") == "local_command":
                print(f"- {ts} local command: {e.get('content', '')[:200]}")
            elif t == "permission-mode":
                continue
            elif t == "user":
                c = e.get("message", {}).get("content")
                if isinstance(c, str):
                    tag = " (automatic)" if e.get("isMeta") else ""
                    print(f"\n## USER{tag} ({ts})\n\n```text\n{c}\n```\n")
                elif isinstance(c, list):
                    for x in c:
                        if x.get("type") == "text":
                            print(f"\n## USER ({ts})\n\n```text\n{x['text']}\n```\n")
                        elif x.get("type") == "tool_result" and x.get("is_error"):
                            print(f"  - tool error: {short(x.get('content'))}")
            elif t == "assistant":
                for c in e.get("message", {}).get("content", []):
                    if c.get("type") == "text" and c.get("text", "").strip():
                        print(f"\n### ASSISTANT ({ts})\n\n{c['text']}\n")
                    elif c.get("type") == "tool_use":
                        print(f"- {ts} tool `{c.get('name')}` {short(c.get('input'))}")
            elif t == "result":
                print(f"\n- result: {e.get('terminal_reason')} is_error={e.get('is_error')} "
                      f"num_turns={e.get('num_turns')}")


if __name__ == "__main__":
    main(sys.argv[1])
