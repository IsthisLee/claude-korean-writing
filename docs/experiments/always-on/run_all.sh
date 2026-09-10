#!/usr/bin/env bash
cd "$(dirname "$0")"
jobs=()
for id in $(ls prompts | sed 's/.txt//'); do for c in A B; do for s in 1 2; do jobs+=("$id $c $s"); done; done; done
printf '%s\n' "${jobs[@]}" | xargs -P 3 -L 1 ./gen_one.sh
ls out/*.json | wc -l
