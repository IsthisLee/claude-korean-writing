#!/usr/bin/env bash
# 규칙 파일을 SessionStart 훅으로 주입해 디바운스 질문에 답하게 한다 (EVALUATION.md H13).
# 주입 방식은 docs/experiments/always-on/regress.sh 와 같다.
#
# 사용  : gen_rule.sh <조건이름> <규칙파일> <표본 번호>
#         조건이름 A 는 judge.py 가 기준으로 쓴다. 주입 없음은 rules/none.md 를 준다.
# 환경  : KW_MODEL 로 생성 모델을 바꾼다(기본 claude-sonnet-5)
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$BASE/../../../.." && pwd)"
cond=$1; rules="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"; s=$3; model=${KW_MODEL:-claude-sonnet-5}
mkdir -p "$BASE/out"
out="$BASE/out/${cond}_${s}.json"
[ -s "$out" ] && exit 0

cfg="$(mktemp -t kw-settings)" || exit 1
NEUTRAL="$(mktemp -d -t kw-neutral)" || exit 1
trap 'rm -f "$cfg"; rm -rf "$NEUTRAL"' EXIT
# 제외 표시는 저장소 검사용이라 주입문에서 뺀다.
python3 - "$rules" "$cfg" <<'PY'
import json, sys
cmd = "sed '/korean-writing: ignore/d' " + json.dumps(sys.argv[1])
json.dump({"hooks": {"SessionStart": [{"matcher": "startup",
          "hooks": [{"type": "command", "command": cmd, "timeout": 10}]}]}},
          open(sys.argv[2], "w"), ensure_ascii=False)
PY

if (cd "$NEUTRAL" && claude -p "$(cat "$REPO/docs/experiments/always-on/prompts/01.txt")" --no-session-persistence --tools "" \
    --strict-mcp-config --setting-sources "" --model "$model" --output-format json --settings "$cfg" < /dev/null) \
    > "$out.tmp" 2> "$out.err"; then
  mv "$out.tmp" "$out"
else
  echo "FAIL $cond $s"
fi
