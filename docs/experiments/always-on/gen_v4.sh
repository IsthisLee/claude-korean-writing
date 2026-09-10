#!/usr/bin/env bash
set -u; cd "$(dirname "$0")"
id=$1; s=$2; out="out_v4/${id}_B_${s}.json"; [ -s "$out" ] && exit 0
claude -p "$(cat "prompts/$id.txt")" --no-session-persistence --tools "" --strict-mcp-config --setting-sources "" --model claude-fable-5-1 --effort xhigh --append-system-prompt "$(cat combined-system.txt)" --output-format json --settings settings-B.json < /dev/null > "$out.tmp" 2> "$out.err" && mv "$out.tmp" "$out" || echo "FAIL $id $s"
