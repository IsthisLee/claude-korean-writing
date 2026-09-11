#!/usr/bin/env bash
set -u; cd "$(dirname "$0")" || exit 1
id=$1; cond=$2; s=$3; out="factcheck/${id}_${cond}_${s}.json"; [ -s "$out" ] && exit 0
python3 - "$id" "$cond" "$s" > "$out.prompt" <<'PY'
import sys, json
id, cond, s = sys.argv[1:4]
q = open(f"prompts/{id}.txt").read(); a = json.load(open(f"out/{id}_{cond}_{s}.json"))["result"]
print(f"""당신은 시니어 개발자다. 아래 질문에 대한 답변에서 기술적으로 틀린 문장이 있으면 그 문장을 그대로 인용하고 왜 틀렸는지 한 줄로 적는다. 문체·형식·누락은 보지 않는다. 오직 틀린 주장만 본다. 없으면 아래 JSON 의 errors 를 빈 배열로 둔다.

아래 JSON 만 출력한다.
{{"errors": [{{"quote": "틀린 문장 인용", "why": "왜 틀렸는지"}}], "severity": "none|minor|major"}}

=== 질문 ===
{q}

=== 답변 ===
{a}
""")
PY
claude -p "$(cat "$out.prompt")" --no-session-persistence --tools "" --strict-mcp-config --setting-sources "" --model claude-fable-5-1 --effort xhigh --append-system-prompt "$(cat control.txt)" --output-format json < /dev/null > "$out.tmp" 2> "$out.err" && mv "$out.tmp" "$out" || echo "FAIL $id $cond $s"
