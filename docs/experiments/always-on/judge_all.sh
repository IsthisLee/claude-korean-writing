#!/usr/bin/env bash
cd "$(dirname "$0")"
jobs=()
for id in $(ls prompts | sed 's/.txt//'); do for s in 1 2; do for o in 1 2; do jobs+=("$id $s $o"); done; done; done
printf '%s\n' "${jobs[@]}" | xargs -P 3 -L 1 ./judge_one.sh
ls judge/*.json | wc -l
