#!/usr/bin/env bash
# 초안 하나를 doc.md 로 저장하게 하고 PostToolUse 검사 훅만 켠다. 훅이 걸리면 모델이 알림을 받고 고친다.
# run.sh 가 부른다. 상시 규칙도 스킬도 없다. 훅이 시키는 교정만 떼어 보려는 것이다.
#
# 사용  : hook_fix.sh <초안> <표본 번호> [모델]
# 환경  : HOOK 는 훅 경로(기본은 저장소의 훅), RUNS 는 이 폴더 기준 출력 위치(기본 out/runs)
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$BASE/../../.." && pwd)"
src=$1; s=$2; model=${3:-claude-sonnet-5}
hook="${HOOK:-$REPO/plugin/hooks-handlers/posttooluse.sh}"
name="$(basename "$src")"; name="${name%.*}"
o="$BASE/${RUNS:-out/runs}/${name}_${model#claude-}_${s}"
[ -s "$o/stream.jsonl" ] && exit 0
mkdir -p "$o"

python3 - "$hook" "$o/settings.json" <<'PY'
import json, sys
json.dump({"hooks": {"PostToolUse": [{"matcher": "Edit|Write|MultiEdit",
          "hooks": [{"type": "command", "command": sys.argv[1], "timeout": 10}]}]}}, open(sys.argv[2], "w"))
PY

W="$(mktemp -d -t kw-hookfix)" || exit 1
trap 'rm -rf "$W"' EXIT
p="아래 초안을 현재 디렉터리의 doc.md 파일로 저장해라. 채팅에는 저장했다고만 한 줄로 답한다.

$(cat "$src")"

# 빈 임시 폴더에서 돌린다. 저장소 안에서 돌리면 모델이 초안 대신 저장소를 뒤진다.
# --setting-sources "" 로 사용자 설정과 훅을, --strict-mcp-config 로 MCP 도구 정의를 뺀다.
if (cd "$W" && env -u KOREAN_WRITING_HOOK_DISABLED claude -p "$p" --no-session-persistence --strict-mcp-config \
    --setting-sources "" --settings "$o/settings.json" --tools "Read,Write,Edit" --permission-mode acceptEdits \
    --max-turns 12 --model "$model" --output-format stream-json --verbose < /dev/null) > "$o/stream.jsonl" 2> "$o/err.txt"; then
  if [ -f "$W/doc.md" ]; then cp "$W/doc.md" "$o/final.md"; fi
else
  echo "FAIL $src $s $model"
fi
exit 0
