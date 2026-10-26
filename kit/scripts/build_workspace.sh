#!/usr/bin/env bash
# build_workspace.sh — Assemble a clean Worker workspace for one R1 run.
#
# Usage:
#   scripts/build_workspace.sh <COND> <MODEL_TAG> <MODEL_NAME> <DEST_DIR> [--with-remote]
#
#   COND        A | A1 | A2 | G | F | C   (A1 / A2: same distributed files as A;
#               only the run / branch name differs, design §9.17)
#   MODEL_TAG   short tag used in the branch name (e.g. luna, sonnet46, flash38)
#   MODEL_NAME  full model name written into issue headers (e.g. "GPT-6 Luna")
#   DEST_DIR    new directory to create (must not exist)
#   --with-remote  add origin = git@github.com:ritsumei-aoi/osp-schema-extension
#                  (needed for A, because close_issue.sh pushes; the Worker's
#                  pushes then go to the public repository)
#
# The workspace is built only from files under kit/ (no bulk copy from other
# directories). A sha256 manifest of every distributed file is written to
# manifests/<branch-name>.txt, outside the workspace.
#
# Branch: study/thm01-R-<MODEL_TAG>-<COND>  (orphan, single init commit)
# F has no Git repository: the Worker must not see any version control.

set -euo pipefail

if [ $# -lt 4 ]; then
  sed -n '2,20p' "$0"; exit 1
fi
COND="$1"; TAG="$2"; MODEL="$3"; DEST="$4"; REMOTE="${5:-}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
KIT="$HERE/kit"
BRANCH="study/thm01-R-${TAG}-${COND}"
MANIFEST="${MANIFEST_DIR:-$HERE/manifests}/thm01-R-${TAG}-${COND}.txt"

[ -e "$DEST" ] && { echo "ERROR: $DEST already exists" >&2; exit 1; }
[ -e "$MANIFEST" ] && { echo "ERROR: manifest already exists: $MANIFEST" >&2; exit 1; }
case "$COND" in A|A1|A2|G|F|C) ;; *) echo "ERROR: COND must be A, A1, A2, G, F or C" >&2; exit 1;; esac
KCOND="${COND%[12]}"   # kit condition (A1 / A2 -> A)

mkdir -p "$DEST"
put() { # put <src-relative-to-kit> <dest-relative-to-workspace>
  mkdir -p "$DEST/$(dirname "$2")"
  cp "$KIT/$1" "$DEST/$2"
}
fill() { # fill placeholders in a distributed file
  sed -i.bak -e "s/{Model Name}/${MODEL}/g" -e "s#study/thm{XX}-{YY}#${BRANCH}#g" "$DEST/$1" && rm "$DEST/$1.bak"
}

math_full() {
  for f in Cn1_definition.md C_inhomogeneous_definition.md C_coboundary_definition.md; do put "math_core/$f" "docs/math/$f"; done
  for f in B0n_definition.md B0n_schema_v5.md README.md; do put "workflow_docs/$f" "docs/math/$f"; done
}
repo_skel() {
  for f in requirements.txt pytest.ini .gitignore; do put "repo_files/$f" "$f"; done
  mkdir -p "$DEST/data" "$DEST/src" "$DEST/tests"
  touch "$DEST/data/.gitkeep" "$DEST/src/.gitkeep" "$DEST/tests/.gitkeep"
}
templates() {
  put templates/final_reflection_template.md final_reflection_template.md
  put templates/supplementary_metrics_template.md supplementary_metrics_template.md
}

case "$KCOND" in
  A)
    math_full; repo_skel; templates
    for f in README.md workflow.md ai_trust_policy.md notation.md handover_memo_latest.md \
             next_session/README.md next_session/prompt_pack_finish.md next_session/prompt_pack_issue.md \
             next_session/prompt_pack_start.md next_session/template.md \
             scripts/close_issue.sh scripts/submit_correction.sh; do
      put "handover/$f" "handover/$f"
    done
    put templates/template_issue_open.md docs/issues/template_issue_open.md
    put issues_A/I01_issue_open.md docs/issues/issue_open.md; fill docs/issues/issue_open.md
    mkdir -p "$DEST/docs/issues/done"; touch "$DEST/docs/issues/done/.gitkeep"
    ;;
  G)
    math_full; repo_skel; templates
    for f in ai_trust_policy.md notation.md handover_memo_latest.md; do put "handover/$f" "handover/$f"; done
    put handover_G/README.md handover/README.md
    put handover_G/workflow.md handover/workflow.md
    # No-gate variant of the boundary rule (no human is available during the run)
    sed -i.bak -e 's#decision not covered by `issue_open.md`#decision not covered by the issues#' -e 's#halt and ask for clarification via `docs/issues/issue_needs_clarification.md`.#record the ambiguity, the assumption you adopt, and your reason in the Response section of the current issue, and continue.#' \
      "$DEST/handover/ai_trust_policy.md" && rm "$DEST/handover/ai_trust_policy.md.bak"
    for i in 1 2 3 4 5 6 7 8; do put "issues_G/I0$i.md" "docs/issues/I0$i.md"; fill "docs/issues/I0$i.md"; done
    ;;
  F)
    math_full; templates
    mkdir -p "$DEST/data" "$DEST/src" "$DEST/tests"
    put repo_files/requirements.txt requirements.txt
    ;;
  C)
    # Identical to study/thm01-X-base (used by the existing One-Shot runs)
    (cd "$KIT/c_condition" && find . -type f -not -path '*/.ipynb_checkpoints/*' | sed 's#^\./##') | while read -r f; do put "c_condition/$f" "$f"; done
    ;;
esac

# Manifest (outside the workspace)
mkdir -p "$(dirname "$MANIFEST")"
{
  echo "# run: thm01-R-${TAG}-${COND}"
  echo "# model: ${MODEL}"
  echo "# built: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# kit commit: $(git -C "$HERE" rev-parse --short HEAD 2>/dev/null || echo unknown)"
  (cd "$DEST" && find . -type f ! -path './.git/*' | sort | xargs shasum -a 256)
} > "$MANIFEST"

if [ "$COND" != "F" ]; then
  git -C "$DEST" init -q
  git -C "$DEST" checkout -q --orphan "$BRANCH"
  git -C "$DEST" add -A
  git -C "$DEST" commit -q -m "init: R1 clean base (condition ${COND}, ${MODEL})"
  if [ "$REMOTE" = "--with-remote" ]; then
    git -C "$DEST" remote add origin git@github.com:ritsumei-aoi/osp-schema-extension
  fi
fi

echo "Built $DEST  (condition $COND, branch ${BRANCH})"
echo "Manifest: $MANIFEST"
