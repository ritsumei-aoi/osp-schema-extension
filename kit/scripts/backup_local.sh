#!/usr/bin/env bash
# backup_local.sh — copy the records that exist only on this machine into the evaluation
# repository (author's decision 2026-10-09, plan B), so that pushing the private
# evaluation repository backs them up:
#   - the automatic runs' push target (bare repo)  -> runs/backup/thm01-R-batch-remote.bundle
#   - each Manager directory (with its .git)       -> runs/backup/manager_dirs/<name>.tar.gz
#   - automatic-run workspaces not fully pushed, and their uncommitted files
#                                                  -> runs/backup/workspaces/
# The agy HOMEs (thm01-R-agy-home, with login data) are NOT copied.
# Overwrites the previous copies (git keeps the history), then commits only this script
# and runs/backup/ if they changed (author's decision 2026-10-09). Push afterwards with
# `git push origin feature/t1-true-template` from the repository root.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../../runs/backup"
mkdir -p "$OUT/manager_dirs"
# Re-create a copy only when its content changed (a bundle or gzip made again from the
# same data differs byte for byte, which would add a new copy to the history each time).
B="$OUT/thm01-R-batch-remote.bundle"
REMOTE="$HOME/notebook/git/thm01-R-batch-remote.git"
if [ -f "$B" ] && [ "$(git bundle list-heads "$B" | sort)" = "$(git -C "$REMOTE" show-ref | sort)" ]; then
  echo "bundle unchanged"
else
  git -C "$REMOTE" bundle create "$B" --all 2>/dev/null
  git bundle verify "$B" >/dev/null 2>&1
  echo "bundle ok: $(git bundle list-heads "$B" | wc -l | tr -d ' ') refs"
fi
TMP=$(mktemp -d)
for d in "$HOME/notebook/git/thm01-R-manager" "$HOME"/notebook/git/thm01-R-managers/*; do
  [ -d "$d" ] || continue
  n=$(basename "$d"); [ "$n" = thm01-R-manager ] && n=thm01-R-manager-shared
  tar -cf "$TMP/$n.tar" -C "$(dirname "$d")" "$(basename "$d")"
  if [ -f "$OUT/manager_dirs/$n.tar.gz" ] && gzip -dc "$OUT/manager_dirs/$n.tar.gz" | cmp -s - "$TMP/$n.tar"; then
    echo "manager dir unchanged: $n"
  else
    gzip -n -c "$TMP/$n.tar" > "$OUT/manager_dirs/$n.tar.gz"
    echo "manager dir: $n"
  fi
done
# Automatic-run workspaces (added 2026-10-09, author's decision): a workspace whose
# commits are not all in the push target (the Worker did not push, or the run stopped)
# -> runs/backup/workspaces/<run>.bundle; files left uncommitted or untracked in any
# workspace (not __pycache__) -> runs/backup/workspaces/<run>.uncommitted.tar.gz.
mkdir -p "$OUT/workspaces"
for w in "$HOME"/notebook/git/thm01-R-batch/thm01-R-*; do
  [ -d "$w/.git" ] || continue
  n=$(basename "$w")
  local_refs=$(git -C "$w" for-each-ref --format='%(objectname) %(refname)' refs/heads | sort)
  missing=0
  while read -r sha ref; do
    [ -n "$sha" ] || continue
    git -C "$REMOTE" merge-base --is-ancestor "$sha" "$ref" 2>/dev/null || missing=1
  done <<< "$local_refs"
  WB="$OUT/workspaces/$n.bundle"
  if [ "$missing" = 1 ]; then
    if [ -f "$WB" ] && [ "$(git bundle list-heads "$WB" | grep ' refs/heads/' | sort)" = "$local_refs" ]; then
      :
    else
      git -C "$w" bundle create "$WB" --branches 2>/dev/null && git -C "$w" bundle verify "$WB" >/dev/null 2>&1
      echo "workspace bundle: $n"
    fi
  fi
  files=$(git -C "$w" ls-files -z -o -m --exclude-standard | tr '\0' '\n' | grep -v '__pycache__' || true)
  WT="$OUT/workspaces/$n.uncommitted.tar.gz"
  if [ -n "$files" ]; then
    (cd "$w" && echo "$files" | tr '\n' '\0' | xargs -0 tar -cf "$TMP/$n.u.tar" 2>/dev/null)
    if [ -f "$WT" ] && gzip -dc "$WT" | cmp -s - "$TMP/$n.u.tar"; then
      :
    else
      gzip -n -c "$TMP/$n.u.tar" > "$WT"
      echo "workspace uncommitted files: $n ($(echo "$files" | wc -l | tr -d ' '))"
    fi
  fi
done
rm -r "$TMP"
cd "$HERE/../.."
git add -- experiment/scripts/backup_local.sh runs/backup
if git diff --cached --quiet -- experiment/scripts/backup_local.sh runs/backup; then
  echo "no change to commit"
else
  git commit -q -m "backup: batch remote bundle and Manager dirs ($(date '+%Y-%m-%d %H:%M'))" \
    -- experiment/scripts/backup_local.sh runs/backup
  echo "committed $(git log -1 --format=%h)"
fi
