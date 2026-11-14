#!/usr/bin/env bash
# Apply patches/*.patch in order to the go2rtc checkout in the current directory.
# The patches come from stacked upstream PRs, so upstream merges them in order:
# skip the longest leading run that upstream already contains, apply the rest.
# A patch that neither applies nor is already upstream fails the build.
set -euo pipefail
dir=$(cd "$(dirname "$0")" && pwd)/patches
patches=("$dir"/*.patch)
n=${#patches[@]}

# Do patches 1..k all reverse-apply as a stack? Tried in the index only.
upstream_prefix() {
  local k=$1 i ok=0
  for ((i = k - 1; i >= 0; i--)); do
    git apply --cached -R "${patches[i]}" 2>/dev/null || { ok=1; break; }
  done
  git reset -q
  return $ok
}

skip=0
for ((k = n; k > 0; k--)); do
  if upstream_prefix "$k"; then skip=$k; break; fi
done

for ((i = 0; i < n; i++)); do
  name=$(basename "${patches[i]}")
  if ((i < skip)); then
    echo "upstream $name (already applied, skipped)"
  elif git apply --index "${patches[i]}"; then
    echo "applied  $name"
  else
    echo "FAILED   $name does not apply to this release" >&2
    exit 1
  fi
done