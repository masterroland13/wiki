#!/usr/bin/env bash
# Verify Markdown image references resolve to existing files.
# Usage: scripts/wiki_verify_images.sh [file.md ...]
# Exit 0 if all OK; exit 1 if any missing.

set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 path/to/file.md [more.md ...]" >&2
  exit 2
fi

fail=0

for md in "$@"; do
  if [[ ! -f "$md" ]]; then
    echo "MISSING FILE: $md" >&2
    fail=1
    continue
  fi
  dir=$(dirname "$md")
  while IFS= read -r line; do
    ref=$(printf '%s\n' "$line" | sed -n 's/.*!\[[^]]*\](\([^)]*\)).*/\1/p')
    [[ -z "$ref" ]] && continue
    ref="${ref#\"}"; ref="${ref%\"}"
    ref="${ref#\'}"; ref="${ref%\'}"
    case "$ref" in
      http://*|https://*) continue ;;
    esac
    path="${ref%% *}"
    target="$dir/$path"
    if [[ ! -f "$target" ]]; then
      echo "BROKEN: $md -> $path (resolved: $target)" >&2
      fail=1
    else
      echo "OK: $md -> $path"
    fi
  done <<EOF
$(grep -E '\!\[[^]]*\]\([^)]+\)' "$md" 2>/dev/null || true)
EOF
done

exit "$fail"
