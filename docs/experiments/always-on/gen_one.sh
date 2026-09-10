#!/usr/bin/env bash
# usage: gen_one.sh <prompt_id> <cond A|B> <sample>
set -u
cd "$(dirname "$0")"
id=$1; cond=$2; s=$3
out="out/${id}_${cond}_${s}.json"
[ -s "$out" ] && exit 0
if [ "$cond" = "B" ]; then
  claude -p "$(cat "prompts/$id.txt")" --no-session-persistence --tools "" --strict-mcp-config --setting-sources "" --model claude-fable-5-1 --effort xhigh --append-system-prompt "$(cat combined-system.txt)" --output-format json --settings settings-B.json < /dev/null > "$out.tmp" 2> "$out.err" && mv "$out.tmp" "$out" || echo "FAIL $id $cond $s"
else
  claude -p "$(cat "prompts/$id.txt")" --no-session-persistence --tools "" --strict-mcp-config --setting-sources "" --model claude-fable-5-1 --effort xhigh --append-system-prompt "$(cat combined-system.txt)" --output-format json < /dev/null > "$out.tmp" 2> "$out.err" && mv "$out.tmp" "$out" || echo "FAIL $id $cond $s"
fi
