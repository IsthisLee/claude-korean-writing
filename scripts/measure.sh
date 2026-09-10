#!/usr/bin/env bash
# 실제 문서 뭉치에 훅을 돌려 오탐률을 잰다.
#
# 사용  : scripts/measure.sh DIR...
# 대상  : DIR 아래의 .md 중 한글 20자 이상인 파일. node_modules 와 .git 은 건너뛴다.
# 출력  : 검사 대상 수, 걸린 파일 수, 코드별 파일 수, 걸린 파일 목록과 항목.
# 판단  : 걸린 파일이 사람이 쓴 글이면 오탐, Claude 가 쓴 글이면 참 양성이다. 그 구분은 사람이 한다.
#         결과와 판단을 EVALUATION.md 의 재측정 기록에 적는다.
# 종료  : 측정이므로 항상 0. 훅 실행 자체가 실패한 파일이 있으면 1.
set -uo pipefail
HOOK="$(cd "$(dirname "$0")/.." && pwd)/hooks-handlers/posttooluse.sh"
[ $# -gt 0 ] || { echo "사용: scripts/measure.sh DIR..." >&2; exit 2; }
python3 - "$HOOK" "$@" <<'PY'
import collections, json, os, re, subprocess, sys
hook, dirs = sys.argv[1], sys.argv[2:]
files = []
for d in dirs:
    for root, subdirs, names in os.walk(d):
        subdirs[:] = [s for s in subdirs if s not in ("node_modules", ".git")]
        files += [os.path.join(root, n) for n in names if n.endswith(".md")]
codes = collections.Counter(); hits = []; checked = 0; errors = 0
for f in sorted(files):
    try:
        text = open(f, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        continue
    if len(re.findall(r"[가-힣]", text)) < 20:
        continue
    checked += 1
    payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": os.path.abspath(f), "content": text}}, ensure_ascii=False)
    r = subprocess.run([hook], input=payload, capture_output=True, text=True)
    if r.returncode == 2:
        found = re.findall(r"^\s+(K\d+)\s+(.*?)\s+—", r.stderr, re.M)
        for code, _ in found:
            codes[code] += 1
        hits.append((f, found))
    elif r.returncode != 0:
        errors += 1; print(f"오류 (exit {r.returncode}): {f}", file=sys.stderr)
print(f"검사 대상 {checked} (전체 .md {len(files)}), 걸린 파일 {len(hits)}")
print("코드별 파일 수: " + ", ".join(f"{c} {n}" for c, n in codes.most_common()))
for f, found in hits:
    print(f"  {f}")
    for code, what in found:
        print(f"      {code} {what}")
sys.exit(1 if errors else 0)
PY
