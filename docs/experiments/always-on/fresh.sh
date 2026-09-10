#!/usr/bin/env bash
# 같은 세션을 이어 받아, 그 대화에서 한 번도 안 나온 프롬프트를 묻는다.
# 앞서 물었던 질문을 다시 물으면 모델이 앞 답변을 그대로 되풀이해 비교가 성립하지 않는다.
set -uo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
EXP="$(cd "$BASE/../exp" && pwd)"
cond=$1
sid=$(cat "$BASE/$cond/session_id")
COMMON=(--strict-mcp-config --setting-sources "" --model claude-fable-5-1 --effort xhigh --tools "" --output-format json)
SYS="$(cat "$EXP/combined-system.txt")"
for id in 02 06 07 12; do
  claude --resume "$sid" -p "$(cat "$EXP/prompts/$id.txt")" --append-system-prompt "$SYS" "${COMMON[@]}" < /dev/null > "$BASE/$cond/fresh_$id.json" 2>/dev/null
  echo "[$cond] fresh $id"
done
