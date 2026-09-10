#!/usr/bin/env bash
# 긴 대화에서 상시 규칙 효과가 유지되는지. 한 세션 안에서 앞(early)과 뒤(late)를 잰다.
# resume 은 SessionStart matcher 가 startup 뿐이라 재주입하지 않는다. 주입은 맨 앞에 한 번만 놓인다.
set -uo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
EXP="$(cd "$BASE/../exp" && pwd)"
cond=$1; fill=${2:-30}
COMMON=(--strict-mcp-config --setting-sources "" --model claude-fable-5-1 --effort xhigh --tools "" --output-format json)
SYS="$(cat "$EXP/combined-system.txt")"
out="$BASE/$cond"; mkdir -p "$out"

if [ "$cond" = "on" ]; then
  first=$(claude -p '준비됐으면 READY 라고만 답하라.' --append-system-prompt "$SYS" "${COMMON[@]}" --settings "$BASE/settings-on.json" < /dev/null)
else
  first=$(claude -p '준비됐으면 READY 라고만 답하라.' --append-system-prompt "$SYS" "${COMMON[@]}" < /dev/null)
fi
sid=$(printf '%s' "$first" | python3 -c 'import sys,json;print(json.load(sys.stdin)["session_id"])') || { echo "세션 시작 실패"; printf '%s' "$first" | head -c 300; exit 1; }
echo "$sid" > "$out/session_id"
echo "[$cond] session=$sid"

ask() {
  claude --resume "$sid" -p "$2" --append-system-prompt "$SYS" "${COMMON[@]}" < /dev/null > "$out/$1" 2>"$out/$1.err"
}

for id in 01 05 09 11; do ask "early_$id.json" "$(cat "$EXP/prompts/$id.txt")"; done
echo "[$cond] early 4건"
for i in $(seq 1 "$fill"); do ask "fill_$i.json" "숫자 하나만 답하라. $i 더하기 7은?"; done
echo "[$cond] 채움 $fill 턴"
for id in 01 05 09 11; do ask "late_$id.json" "$(cat "$EXP/prompts/$id.txt")"; done
ask "probe.json" '컨텍스트에 "[korean-writing]" 으로 시작하는 규칙 줄이 아직 보이면 그 줄만 그대로, 없으면 NONE 이라고만 답하라.'
echo "[$cond] late 4건 + probe 완료"
