#!/usr/bin/env bash
# 파일을 통째로 훅에 넣어 검사한다.
#
# 훅은 Claude Code 가 방금 편집한 부분만 본다. 이미 써 둔 문서를 점검하거나 CI·pre-commit 에서
# 돌릴 때는 파일 전체를 편집분으로 넣는다. 판정 기준과 메시지는 훅과 같다.
#
# 사용  : scripts/check.sh FILE...
# 종료  : 걸린 파일이 하나라도 있으면 1, 없으면 0. 인자가 없으면 2. .md 가 아닌 파일은 건너뛴다.
# 끄기  : 파일 머리에 <!-- korean-writing: ignore --> 가 있으면 그 파일은 통과한다.
set -uo pipefail
HOOK="$(cd "$(dirname "$0")/.." && pwd)/hooks-handlers/posttooluse.sh"
[ $# -gt 0 ] || { echo "사용: scripts/check.sh FILE..." >&2; exit 2; }

bad=0
for f in "$@"; do
  if [ ! -f "$f" ]; then echo "없음: $f" >&2; bad=1; continue; fi
  case "$f" in *.md) ;; *) echo "건너뜀 (.md 아님): $f"; continue ;; esac
  abs="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
  out=$(python3 -c 'import json, sys
p = sys.argv[1]
print(json.dumps({"tool_name": "Write", "tool_input": {"file_path": p, "content": open(p, encoding="utf-8").read()}}, ensure_ascii=False))' "$abs" | "$HOOK" 2>&1 >/dev/null)
  rc=$?
  case "$rc" in
    0) echo "통과: $f" ;;
    2) echo "$out"; bad=1 ;;
    *) echo "오류 (exit $rc): $f"; echo "$out"; bad=1 ;;
  esac
done
exit $bad
