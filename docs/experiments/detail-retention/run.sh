#!/usr/bin/env bash
# 검사 훅의 안내대로 고친 글에서 원문의 정보가 사라지는지 잰다 (EVALUATION.md I1).
#
# 왜 : 모델은 훅이 알린 대로 고친다. 안내가 규칙집 처방을 한 줄로 줄이면서 보존 조건을 떨어뜨리면
#      고치는 동안 정보가 지워진다. 옛 K9 안내 「A가 아니라 B다 → B다」 가 실제로 그렇게 했다.
# 무엇: 대조군 초안을 모델에게 doc.md 로 저장하게 하고 PostToolUse 검사 훅만 켠다. 훅이 걸리면
#      모델이 알림을 받고 고친다. 처음 저장한 글과 고친 글을 조건을 모르는 판정자에게 주고
#      사라진 정보를 세게 한다.
#
# 사용  : run.sh [훅 경로] [표본 수]
#         훅을 안 주면 저장소의 plugin/hooks-handlers/posttooluse.sh 다. 안내를 고친 사본을 주면 그것을 잰다.
# 종료  : 사라진 정보가 하나라도 있으면 1.
# 비용  : 표본 3 이면 Sonnet 5 와 Opus 5 로 생성 6회, 판정 6회. LLM 을 부르므로 CI 에 넣지 않는다.
set -uo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$BASE/../../.." && pwd)"
HOOK="${1:-$REPO/plugin/hooks-handlers/posttooluse.sh}"
N="${2:-3}"
command -v claude >/dev/null 2>&1 || { echo "claude 가 없다" >&2; exit 2; }
[ -x "$HOOK" ] || { echo "훅을 실행할 수 없다: $HOOK" >&2; exit 2; }

RUN="out/run-$(date +%Y%m%d-%H%M%S)"
echo "훅: $HOOK"
echo "출력: $BASE/$RUN"
# 병렬로 돌릴 때 claude 가 작업 목록 stdin 을 물지 않도록 hook_fix.sh 안에서 < /dev/null 로 끊는다.
for m in claude-sonnet-5 claude-opus-5; do
  for s in $(seq 1 "$N"); do echo "$BASE/drafts/control.txt $s $m"; done
done | HOOK="$HOOK" RUNS="$RUN" xargs -P 3 -n 3 "$BASE/hook_fix.sh"
python3 "$BASE/analyze.py" "$RUN"
