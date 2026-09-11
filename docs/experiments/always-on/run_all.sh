#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
jobs=()
for f in prompts/*.txt; do id="$(basename "$f" .txt)"; for c in A B; do for s in 1 2; do jobs+=("$id $c $s"); done; done; done
printf '%s\n' "${jobs[@]}" | xargs -P 3 -L 1 ./gen_one.sh
find out -name '*.json' | wc -l
