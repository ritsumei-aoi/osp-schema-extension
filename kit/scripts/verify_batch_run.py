#!/usr/bin/env python3
"""verify_batch_run.py — Check that an automatic run was carried out correctly.

Usage:
    python3 scripts/verify_batch_run.py runs/batch/<run> [...]

This checks the procedure, not the mathematics (no judgement):
  - the model in the log is the requested one, and the first prompt sent is the
    fixed prompt file of the condition;
  - which tools were used, and whether any tool needs an answer nobody gives
    in headless mode (ask_question / ask_permission), or reaches outside
    (search_web, read_url_content, browser_*, send_message, subagents);
  - tool calls denied by the allow-list, and other tool errors;
  - the completion files are committed (G: final_reflection; C: proof, then
    final_reflection and supplementary_metrics), nothing is left uncommitted,
    and the branch was pushed to the local remote at the final commit;
  - check_artifacts.py on the workspace (structure of the JSON artifacts; the
    four-layer data/ check applies to G only).
"""
import gzip
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REMOTE = Path.home() / "notebook/git/thm01-R-batch-remote.git"
OUTSIDE = ("search_web", "read_url_content", "send_message", "invoke_subagent", "define_subagent",
           "manage_subagents", "browser_subagent", "call_mcp_tool", "generate_image")
UNANSWERED = ("ask_question", "ask_permission", "ask_custom_permission", "ask_user")
OUTSIDE = OUTSIDE + ("web_fetch", "task", "search_code_subagent", "run_dynamic_workflow", "write_agent")


def events(logdir):
    for f in sorted(logdir.glob("turn*.jsonl*"), key=lambda p: int(p.name[4:].split(".")[0])):
        op = gzip.open if f.name.endswith(".gz") else open
        with op(f, "rt") as fh:
            for line in fh:
                try:
                    yield f.name, json.loads(line)
                except ValueError:
                    pass


def git(ws, *a, cwd_git=True):
    return subprocess.run(["git", "-C", str(ws), *a], capture_output=True, text=True).stdout.strip()


def verify(logdir):
    s = json.loads((logdir / "run.json").read_text())
    ws = Path(s["workspace"])
    agy = s["harness"].startswith("agy")
    copilot = s["harness"].startswith("GitHub Copilot")
    out = {"run": s["run"], "status": s["status"], "fixed_replies": s["fixed_replies"],
           "denial_replies": s.get("denial_replies")}
    models, first_prompt, tools, denied, errors = set(), None, {}, [], []
    texts_sent = []
    for name, e in events(logdir):
        if copilot:
            d = e.get("data") or {}
            if e.get("type") == "session.tools_updated" and d.get("model"):
                models.add(d["model"])
            if e.get("type") == "user.message":
                texts_sent.append(d.get("content", ""))
            if e.get("type") == "tool.execution_start":
                tools[d.get("toolName")] = tools.get(d.get("toolName"), 0) + 1
            if e.get("type") == "tool.execution_complete" and not d.get("success"):
                err = d.get("error") or {}
                rec = (name, "", "", str(err.get("message", ""))[:160])
                (denied if err.get("code") == "denied" else errors).append(rec)
        elif agy:
            if e.get("event") == "init":
                models.add(e["init"].get("model"))
            su = e.get("step_update") or {}
            if su.get("step_type") == "user_input" and first_prompt is None:
                first_prompt = json.dumps(su, ensure_ascii=False)
            if su.get("step_type") == "tool" and su.get("state") in ("DONE", "ERROR"):
                t = su.get("tool_name")
                tools[t] = tools.get(t, 0) + 1
                info = su.get("tool_info", {})
                if su["state"] == "ERROR":
                    msg = (info.get("error") or {}).get("message", "")
                    rec = (name, t, json.dumps(info.get("parameters"), ensure_ascii=False)[:160])
                    (denied if "permission check failed" in msg else errors).append(rec + (msg[:160],))
        else:
            if e.get("type") == "system" and e.get("subtype") == "init":
                models.add(e.get("model"))
            if e.get("type") == "assistant":
                for c in e.get("message", {}).get("content", []):
                    if c.get("type") == "tool_use":
                        tools[c["name"]] = tools.get(c["name"], 0) + 1
            if e.get("type") == "user":
                for c in e.get("message", {}).get("content", []) if isinstance(e.get("message", {}).get("content"), list) else []:
                    if c.get("type") == "tool_result" and c.get("is_error"):
                        txt = json.dumps(c.get("content"), ensure_ascii=False)
                        (denied if any(w in txt.lower() for w in ("permission", "denied", "requires approval")) else errors).append((name, "", "", txt[:160]))
    prompt = (EXP / f"prompts/{s['condition']}_prompt.txt").read_text().strip()
    out["model_ok"] = bool(models) and (models == {s["model"]} or (not agy and all(s["model"] in (m or "") for m in models)))
    out["models"] = sorted(m for m in models if m)
    out["first_prompt_ok"] = s["turns"][0]["text"] == prompt
    if copilot:
        out["texts_in_log"] = [t["text"] in texts_sent for t in s["turns"]]
    if agy:
        # stream-json does not carry the user text; look for every text sent, in
        # full, in the conversation store of the run's own HOME.
        blob = b"".join(f.read_bytes() for f in Path(s["home"]).glob(".gemini/antigravity-cli/conversations/*.db*"))
        out["texts_in_conversation_store"] = [t["text"].encode() in blob for t in s["turns"]]
    out["tools"] = tools
    out["outside_tools"] = {t: n for t, n in tools.items() if t in OUTSIDE or t.startswith("browser_") or t == "open_browser_url"}
    out["unanswered_tools"] = {t: n for t, n in tools.items() if t in UNANSWERED}
    out["denied"] = denied
    out["tool_errors"] = len(errors)
    need = ["docs/issues/final_reflection.md"] if s["condition"] == "G" else \
        ["docs/issues/mathematical_proof.md", "final_reflection.md", "supplementary_metrics.md"]
    out["committed"] = {p: bool(git(ws, "log", "--format=%h", "--", p)) for p in need}
    out["uncommitted"] = git(ws, "status", "--short").splitlines()
    branch = git(ws, "rev-parse", "--abbrev-ref", "HEAD")
    out["pushed_at_final"] = git(REMOTE, "rev-parse", "--short", branch) == git(ws, "rev-parse", "--short", "HEAD")
    tmp = Path("/tmp") / f"verify_{s['run']}.json"
    subprocess.run([sys.executable, str(HERE / "check_artifacts.py"), str(ws), "--json", str(tmp)],
                   capture_output=True, text=True)
    ca = json.loads(tmp.read_text())
    tmp.unlink()
    out["check_artifacts"] = {"four_layers_complete (G: data/)": ca["four_layers_complete"],
                              "json_files": len(ca["json_files"]), "json_parse_errors": ca["json_parse_errors"],
                              "layer1_failures": {n: [k for k, v in (r.get("structure_check") or {}).items() if v is False]
                                                  for n, r in ca["layers"].items()}}
    out["last_response"] = (s["turns"][-1].get("result") or "")[:300]
    return out


if __name__ == "__main__":
    for d in sys.argv[1:]:
        print(json.dumps(verify(Path(d)), ensure_ascii=False, indent=1))
