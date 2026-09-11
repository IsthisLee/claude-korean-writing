#!/usr/bin/env bash
# 편집 검사 훅이 짚은 자리가 같은 턴에 Claude 에게 돌아가 고쳐지는가.
#
# AI 티가 든 초안을 notice.md 로 저장해 달라고 부탁하고, 플러그인을 켠 쪽과 끈 쪽을 N 회씩 돌린다.
# 켠 쪽은 저장 직후 PostToolUse 훅이 걸린 항목을 stderr 로 내고 종료 코드 2 로 끝난다.
# Claude Code 는 그 stderr 를 system reminder 로 Claude 에게 보여 준다.
# 그 알림은 stream-json 에 찍히지 않으므로 판정은 마지막 파일을 같은 검사기에 다시 넣어서 한다.
#
# 사용: docs/experiments/hook-loop/run.sh [회수=3] [모델=claude-sonnet-5]
# 비용: 2026-09-11 에 claude-sonnet-5 로 켠 쪽 약 0.10달러, 끈 쪽 약 0.06달러였다(1회당).
set -euo pipefail
cd "$(dirname "$0")"
N="${1:-3}"; MODEL="${2:-claude-sonnet-5}"
REPO="$(cd ../../.. && pwd)"; PLUGIN="$REPO/plugin"; CHECK="$PLUGIN/scripts/check.sh"
OUT="out/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
unset KOREAN_WRITING_HOOK_DISABLED

run() {
  local arm="$1" i="$2" dir
  dir="$(mktemp -d -t kw-hookloop)"
  # 개인 설정·MCP 는 불러오지 않는다. 불러오면 도구 정의가 입력을 부풀리고 개인 훅이 끼어든다.
  local args=(-p "$(cat prompt.txt)" --model "$MODEL" --output-format stream-json --verbose
              --max-turns 10 --strict-mcp-config --setting-sources "" --no-session-persistence
              --allowedTools "Write,Edit,Read" --permission-mode acceptEdits)
  if [ "$arm" = with ]; then args+=(--plugin-dir "$PLUGIN"); fi
  # A && B || C 는 if-then-else 가 아니다. cd 가 실패하면 C 가 돈다(shellcheck SC2015).
  (
    cd "$dir" || exit 1
    claude "${args[@]}" < /dev/null > "$OLDPWD/$OUT/$arm-$i.jsonl" 2> "$OLDPWD/$OUT/$arm-$i.err" || true
    if [ -f notice.md ]; then cp notice.md "$OLDPWD/$OUT/$arm-$i.notice.md"; fi
  )
  rm -rf "$dir"
}

for i in $(seq 1 "$N"); do run with "$i" & run without "$i" & done
wait

python3 - "$OUT" "$CHECK" "$N" <<'PY'
import json, pathlib, re, subprocess, sys
out, check, n = pathlib.Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
def codes(text):
    p = out / "_probe.md"; p.write_text(text, encoding="utf-8")
    r = subprocess.run([check, str(p)], capture_output=True, text=True)
    return sorted(set(re.findall(r"^\s+(K\d+)", r.stdout + r.stderr, re.M)))
fixed = {"with": 0, "without": 0}
for arm in ("with", "without"):
    for i in range(1, n + 1):
        ev = [json.loads(l) for l in (out / f"{arm}-{i}.jsonl").read_text().splitlines() if l.startswith("{")]
        tools = [c["name"] for e in ev if e.get("type") == "assistant"
                 for c in e["message"].get("content", []) if c.get("type") == "tool_use"]
        first = next((c["input"]["content"] for e in ev if e.get("type") == "assistant"
                      for c in e["message"].get("content", []) if c.get("type") == "tool_use" and c["name"] == "Write"), "")
        final = out / f"{arm}-{i}.notice.md"
        last = codes(final.read_text(encoding="utf-8")) if final.exists() else ["파일 없음"]
        cost = next((e.get("total_cost_usd") for e in ev if e.get("type") == "result"), None)
        if not last: fixed[arm] += 1
        print(f"{arm}-{i}: 도구 {tools} · 첫 저장 {codes(first) if first else '-'} · 마지막 파일 {last or '걸림 없음'} · ${cost}")
print(f"\n마지막 파일에 걸림이 없던 실행: 켠 쪽 {fixed['with']}/{n}, 끈 쪽 {fixed['without']}/{n}")
PY
