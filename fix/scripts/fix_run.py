#!/usr/bin/env python3
"""fix_run.py — Send one correction message to the Worker of a fix trial (design §9.30,
runs/fix/PROTOCOL.md §5) and record the turn.

Usage:
    python3 runs/fix/scripts/fix_run.py <RUN> <STAGE> <MESSAGE_FILE>
      STAGE 1: starts a NEW Worker session in <home>/notebook/git/thm01-R-fix/<RUN>.
      STAGE 2: resumes the stage-1 session (session id from runs/fix/<RUN>/fix_run.json).
    The message file is sent byte-for-byte as the only prompt of the turn.

The Worker is started exactly as in batch_run.py (same model, effort, tool lists,
Claude Code binary 2.1.288 or agy), using batch_run.run_turn_claude / run_turn_agy.
No fixed replies and no automatic resumes: one message per stage.
Claude Code: config dir <home>/notebook/git/thm01-R-claude-config/fix (logged in once by the author).
agy: a new HOME per trial, <home>/notebook/git/thm01-R-fix/agy-home/worker-<RUN> (login token only,
the same settings as batch_run.AGY_SETTINGS).
Logs: runs/fix/<RUN>/worker/turn<STAGE>.jsonl and runs/fix/<RUN>/fix_run.json.
"""
import json
import shutil
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE.parent
REV = FIX.parent.parent
sys.path.insert(0, str(REV / "experiment/scripts"))
import batch_run as br  # noqa: E402

ROOT = br.HOME / "notebook/git/thm01-R-fix"
CLAUDE_CONFIG = br.HOME / "notebook/git/thm01-R-claude-config/fix"


def main():
    if len(sys.argv) != 4 or sys.argv[2] not in ("1", "2"):
        print(__doc__)
        sys.exit(1)
    run, stage, msg_file = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    text = msg_file.read_text()
    orig = json.loads((REV / "runs/batch" / run / "run.json").read_text())
    ws = ROOT / run
    out = FIX / run
    logdir = out / "worker"
    logdir.mkdir(parents=True, exist_ok=True)
    state_file = out / "fix_run.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {
        "run": run, "model": orig["model"], "effort": orig.get("effort"),
        "original_harness": orig["harness"], "workspace": str(ws),
        "base_commit": br.git(ws, "rev-parse", "--short", "HEAD"), "turns": []}
    if any(t["turn"] == stage for t in state["turns"]):
        sys.exit(f"ERROR: stage {stage} already recorded in {state_file}")
    if stage == 2 and not state["turns"]:
        sys.exit("ERROR: no stage-1 session to resume")
    if br.git(ws, "status", "--porcelain"):
        print("WARNING: workspace not clean before the turn:\n" + br.git(ws, "status", "--porcelain"))
    session = state["turns"][-1]["session_id"] if stage == 2 else None
    head_before = br.git(ws, "rev-parse", "--short", "HEAD")

    if orig["harness"].startswith("agy"):
        h = ROOT / "agy-home" / f"worker-{run}"
        if stage == 1:
            (h / br.AGY_TOKEN).parent.mkdir(parents=True)
            shutil.copy2(br.AGY_BASE_HOME / br.AGY_TOKEN, h / br.AGY_TOKEN)
            (h / ".gemini/antigravity-cli/settings.json").write_text(json.dumps(br.AGY_SETTINGS, indent=1))
        args = Namespace(model=orig["model"], agy_home=h)
        state["harness"] = "agy " + subprocess.run([br.AGY_BIN, "--version"], capture_output=True,
                                                   text=True).stdout.strip()
        state["agy_home"] = str(h)
        rec = br.run_turn_agy(ws, logdir, stage, text, args, session)
        tools = br.agy_tool_calls(logdir)
    elif orig["harness"].startswith("2.1."):
        ver = orig["harness"].split()[0]
        args = Namespace(model=orig["model"], effort=orig.get("effort") or "medium",
                         config_dir=CLAUDE_CONFIG, claude_bin=str(br.CLAUDE_VERSIONS / ver))
        state["harness"] = f"{ver} (Claude Code)"
        state["config_dir"] = str(CLAUDE_CONFIG)
        rec = br.run_turn_claude(ws, logdir, stage, text, args, session)
        tools = None
    else:
        sys.exit(f"ERROR: harness {orig['harness']} not supported")

    rec.update({"stage": stage, "message_file": str(msg_file),
                "message_sha256": __import__("hashlib").sha256(text.encode()).hexdigest(),
                "started_head": head_before, "ended_head": br.git(ws, "rev-parse", "--short", "HEAD"),
                "commits": br.git(ws, "log", "--format=%h %s", f"{head_before}..HEAD").splitlines(),
                "diff_stat": br.git(ws, "diff", "--shortstat", f"{state['base_commit']}..HEAD"),
                "uncommitted": br.git(ws, "status", "--porcelain").splitlines(),
                "ended": br.now()})
    if tools is not None:
        rec["tool_calls"] = len(tools)
        rec["tool_errors"] = [t for t in tools if t["state"] == "ERROR"]
    rec["outside_refs"] = br.outside_refs(logdir, ws)
    state["turns"].append(rec)
    state_file.write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n")
    subprocess.run(["gzip", "-f", str(logdir / f"turn{stage}.jsonl")])
    print(json.dumps({k: rec.get(k) for k in ("stage", "seconds", "timed_out", "is_error", "terminal_reason",
                                              "commits", "diff_stat", "uncommitted")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
