#!/usr/bin/env bash
# fix_setup.sh — Prepare one correction trial of the fix experiment (design §9.30,
# runs/fix/PROTOCOL.md). Nothing in the original batch workspace is touched.
#
# Usage: runs/fix/scripts/fix_setup.sh <RUN> <FINAL_COMMIT>
#   e.g. runs/fix/scripts/fix_setup.sh thm01-R-gemini31p-b01-C 4335d47
# Creates:
#   <home>/notebook/git/thm01-R-fix/<RUN>/                 copy of the final commit
#       (clone of study/<RUN> from thm01-R-batch-remote.git, branch fix/<RUN>, no origin;
#        an existing copy is kept if its HEAD is FINAL_COMMIT)
#   <home>/notebook/git/thm01-R-fix/managers/<RUN>/        Manager directory (FIX_MANAGER_BRIEF.md,
#       reference/ = docs/math of the copy + the prompts the Worker received, memos/<RUN>/)
#   <home>/notebook/git/thm01-R-fix/agy-home/manager-<RUN>/  Manager HOME (login token only,
#       settings.json of the author with model Gemini 3.1 Pro (Low))
#   experiment/manifests/fix-<RUN>.txt                sha256 of the copy and of the Manager dir
set -euo pipefail
[ $# -eq 2 ] || { sed -n '2,17p' "$0"; exit 1; }
RUN="$1"; BASE="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"
FIX="$(cd "$HERE/.." && pwd)"
REV="$(cd "$FIX/../.." && pwd)"
ROOT="$HOME/notebook/git/thm01-R-fix"
WS="$ROOT/$RUN"; MGR="$ROOT/managers/$RUN"; H="$ROOT/agy-home/manager-$RUN"
REMOTE="$HOME/notebook/git/thm01-R-batch-remote.git"
RUNJSON="$REV/runs/batch/$RUN/run.json"
[ -f "$RUNJSON" ] || { echo "ERROR: $RUNJSON not found" >&2; exit 1; }
[ -e "$MGR" ] && { echo "ERROR: $MGR exists" >&2; exit 1; }
[ -e "$H" ] && { echo "ERROR: $H exists" >&2; exit 1; }
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# 1. copy of the final commit
if [ -e "$WS" ]; then
  [ "$(git -C "$WS" rev-parse --short=7 HEAD)" = "${BASE:0:7}" ] || { echo "ERROR: $WS exists with another HEAD" >&2; exit 1; }
  echo "Keeping existing copy $WS (HEAD $BASE)"
else
  mkdir -p "$ROOT"
  git clone -q --no-checkout "$REMOTE" -b "study/$RUN" "$WS"
  git -C "$WS" checkout -q -b "fix/$RUN" "$BASE"
  git -C "$WS" remote remove origin
fi
[ -z "$(git -C "$WS" status --porcelain)" ] || { echo "ERROR: $WS is not clean" >&2; exit 1; }

# 2. Manager directory
mkdir -p "$MGR/reference/docs/math" "$MGR/reference/prompts" "$MGR/memos/$RUN"
cp "$FIX/kit/FIX_MANAGER_BRIEF.md" "$MGR/MANAGER_BRIEF.md"
cp "$WS"/docs/math/*.md "$MGR/reference/docs/math/"
python3 -I - "$RUNJSON" "$MGR/reference/prompts" <<'PY'
import json, sys, pathlib
d = json.load(open(sys.argv[1])); out = pathlib.Path(sys.argv[2])
seen = []
for t in d["turns"]:
    if t["text"] not in seen:
        seen.append(t["text"])
for i, text in enumerate(seen, 1):
    (out / f"worker_prompt_{i}.txt").write_text(text)
PY
MODEL="$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["model"])' "$RUNJSON")"
COND="$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["condition"])' "$RUNJSON")"
cat > "$MGR/memos/$RUN/manager_memo.md" <<EOF
# Manager memo: $RUN (correction session)

- Run ID: $RUN
- Original condition: $COND
- Worker model: $MODEL
- Worker repository (read-only): $WS
- Base commit: $BASE
EOF
git -C "$MGR" init -q
git -C "$MGR" -c user.name=scribe -c user.email=scribe@localhost add -A
git -C "$MGR" -c user.name=scribe -c user.email=scribe@localhost commit -q -m "init: correction session for $RUN"

# 3. Manager HOME
mkdir -p "$H/.gemini/antigravity-cli"
cp "$HOME/notebook/git/thm01-R-agy-home/base/.gemini/antigravity-cli/antigravity-oauth-token" "$H/.gemini/antigravity-cli/"
python3 -I - "$HOME/.gemini/antigravity-cli/settings.json" "$H/.gemini/antigravity-cli/settings.json" <<'PY'
import json, sys
s = json.load(open(sys.argv[1])); s["model"] = "Gemini 3.1 Pro (Low)"
open(sys.argv[2], "w").write(json.dumps(s, indent=2) + "\n")
PY

# 4. manifest
MAN="$REV/experiment/manifests/fix-$RUN.txt"
{
  echo "# fix trial: $RUN"
  echo "# built: $(now)"
  echo "# base commit: $BASE (study/$RUN in $REMOTE)"
  echo "# worker copy: $WS (branch fix/$RUN, no origin)"
  echo "# manager dir: $MGR"
  echo "# manager home: $H"
  echo "# kit commit: $(git -C "$REV" rev-parse --short HEAD)"
  echo "## worker copy files"
  (cd "$WS" && git ls-files | sort | xargs shasum -a 256)
  echo "## manager dir files"
  (cd "$MGR" && find . -type f ! -path './.git/*' | sort | xargs shasum -a 256)
} > "$MAN"
echo "Worker copy:  $WS"
echo "Manager dir:  $MGR"
echo "Manager HOME: $H"
echo "Manifest:     $MAN"
echo "Start the Manager with:"
echo "  cd $MGR && HOME=$H GIT_CONFIG_GLOBAL=$HOME/.gitconfig agy"
