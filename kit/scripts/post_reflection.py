#!/usr/bin/env python3
"""post_reflection.py — ask a finished Claude batch run for its missing final reflection
afterwards (design §9.38, author's decision 2026-10-09). The run itself is not changed:
it is counted and judged as it ended (final_commit); this is a separate record.

Usage:
    python3 scripts/post_reflection.py <RUN> --mode resume|new [--dry-run]
    e.g. python3 scripts/post_reflection.py thm01-R-sonnet46-b12-G --mode resume

Procedure (fixed):
  - Claude Code harness only, with the run's own settings (model, effort, Claude Code
    version, config dir, tool lists from batch_run.py).
  - resume: one message in the run's last session (--resume <session_id>).
    new: one message in a new session in the same workspace.
  - The message is fixed: G = the reflection sentence of prompts/G_prompt.txt,
    C = prompts/C_final_reflection.txt.
  - One message only, no fixed replies. Try resume first; use new only if resume did
    not commit the reflection.
  - Records go to runs/batch/<RUN>/post_reflection/ (turn log, gzip, and result.json
    with the commits added after the run's final_commit).
"""
import argparse
import gzip
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch_run as br  # noqa: E402

G_TEXT = ("When all eight issues are complete, read final_reflection_template.md and create "
          "docs/issues/final_reflection.md, then commit and push.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--mode", choices=["resume", "new"], required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    rundir = br.REV / "runs/batch" / a.run
    info = json.loads((rundir / "run.json").read_text())
    cond = a.run.rsplit("-", 1)[1]
    ws = br.WS_ROOT / a.run
    if "Claude Code" not in str(info.get("harness", "")):
        sys.exit("only Claude Code runs are supported")
    prompt_g = (br.EXP / "prompts/G_prompt.txt").read_text()
    if cond == "G":
        assert G_TEXT in " ".join(prompt_g.split()), "G reflection sentence not found in G_prompt.txt"
        text, done = G_TEXT, "docs/issues/final_reflection.md"
    else:
        text, done = (br.EXP / "prompts/C_final_reflection.txt").read_text().strip(), "final_reflection.md"
    version = str(info.get("harness", "")).split()[0]
    args = argparse.Namespace(model=info["model"], effort=info.get("effort") or "medium",
                              config_dir=Path(info.get("config_dir") or br.DEFAULT_CONFIG),
                              claude_bin=str(br.CLAUDE_VERSIONS / version))
    sid = None
    if a.mode == "resume":
        sids = [t.get("session_id") for t in info.get("turns", []) if t.get("session_id")]
        sid = sids[-1] if sids else info.get("session_id")
        if not sid:
            sys.exit("no session id in run.json")
    final = info.get("final_commit")
    head = br.git(ws, "rev-parse", "--short", "HEAD")
    print(json.dumps({"run": a.run, "mode": a.mode, "session_id": sid, "model": args.model,
                      "effort": args.effort, "claude_bin": args.claude_bin,
                      "config_dir": str(args.config_dir), "workspace": str(ws),
                      "final_commit": final, "head": head, "text": text,
                      "already_committed": br.committed(ws, done)}, indent=1))
    if a.dry_run:
        return
    if br.committed(ws, done):
        sys.exit("reflection already committed")
    logdir = rundir / "post_reflection"
    logdir.mkdir(exist_ok=True)
    n = 1 + len(list(logdir.glob("turn*.jsonl.gz")))
    t = br.run_turn_claude(ws, logdir, n, text, args, sid)
    log = logdir / t["log"]
    with open(log, "rb") as f, gzip.open(str(log) + ".gz", "wb") as g:
        shutil.copyfileobj(f, g)
    log.unlink()
    t["log"] += ".gz"
    res = {"run": a.run, "mode": a.mode, "started_session": sid, "turn": t,
           "final_commit": final, "head_before": head,
           "head_after": br.git(ws, "rev-parse", "--short", "HEAD"),
           "commits_after_final": br.git(ws, "log", "--format=%h %s", f"{final}..HEAD").splitlines() if final else [],
           "reflection_committed": br.committed(ws, done),
           "uncommitted": br.git(ws, "status", "--short").splitlines()}
    out = logdir / f"result{n}.json"
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps({k: res[k] for k in ("reflection_committed", "commits_after_final", "uncommitted")}, indent=1))


if __name__ == "__main__":
    main()
