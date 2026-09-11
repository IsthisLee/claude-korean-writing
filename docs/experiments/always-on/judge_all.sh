#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
jobs=()
for f in prompts/*.txt; do id="$(basename "$f" .txt)"; for s in 1 2; do for o in 1 2; do jobs+=("$id $s $o"); done; done; done
printf '%s\n' "${jobs[@]}" | xargs -P 3 -L 1 ./judge_one.sh
find judge -name '*.json' | wc -l
