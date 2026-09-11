#!/usr/bin/env bash
# 서브에이전트 주입 한 건. usage: run_sub.sh <id> <cond A|B> <sample>
# A 는 서브에이전트 주입 끔, B 는 켬. 플러그인을 통째로 얹고 도구를 켠다.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$here/../../.." && pwd)"
id=$1; cond=$2; s=$3
mkdir -p "$here/subout"
out="$here/subout/${id}_${cond}_${s}.json"
[ -s "$out" ] && exit 0
if [ "$cond" = "A" ]; then export KOREAN_WRITING_SUBAGENT_DISABLED=1; else unset KOREAN_WRITING_SUBAGENT_DISABLED; fi
cd "$REPO" || exit 1
claude -p "$(cat "$here/prompts-sub/$id.txt")" \
  --plugin-dir "$REPO" --strict-mcp-config --setting-sources "" \
  --dangerously-skip-permissions --max-turns 20 --model claude-opus-5 \
  --output-format json < /dev/null > "$out.tmp" 2> "$out.err" \
  && mv "$out.tmp" "$out" || echo "FAIL $id $cond $s"
