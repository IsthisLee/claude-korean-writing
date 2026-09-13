#!/usr/bin/env bash
# 스킬 적용 여부에 따라 세부 항목이 빠지는지 잴 답을 만든다 (EVALUATION.md J3).
#
# 사용  : gen.sh <과제> <A|S|N|M> <표본 번호>
#         A 는 스킬 없음, S 는 plugin/SKILL.md 를 시스템 프롬프트에 붙임, N 은 같은 글자 수의 무관한 문서를 붙임
#         M 은 스킬에 「설명은 넉넉히」 지시를 더한 것이다. 확인 창의 둘째 선택지가 실제로 설명을 되살리는지 잰다.
#         M 에 붙이는 문구는 plugin/hooks-handlers/pretooluse-skill.sh 가 그 선택지에 지시하는 말과 같아야 한다.
#         과제는 prompts/ 의 파일 이름(notice·incident·debounce)이다. N 을 쓰기 전에 make_neutral.py 를 돌린다.
# 출력  : ../out/skill/<과제>_<조건>_<표본>.json  (docs/experiments/*/out/ 은 커밋하지 않는다)
# 환경  : KW_MODEL 로 생성 모델을 바꾼다(기본 claude-sonnet-5)
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$BASE/../../../.." && pwd)"
OUT="$BASE/../out/skill"
task=$1; cond=$2; s=$3; model=${KW_MODEL:-claude-sonnet-5}
mkdir -p "$OUT"
out="$OUT/${task}_${cond}_${s}.json"
[ -s "$out" ] && exit 0

# 두 조건 모두 같은 안내를 받는다. 조건 사이의 차이는 스킬 본문 하나뿐이다.
NOTOOL=$'\n\n## 이 실행의 예외\n이 세션에는 도구가 없다. 파일을 읽거나 쓰지 말고 요청한 글의 본문만 출력한다.'
MORE=$'\n\n## 이 요청의 예외\n규칙을 지키면서 요청에 없던 곁가지 설명(기본값, 동작 원리 같은 것)을 평소만큼 덧붙여 쓴다. 설명을 줄이지 않는다.'
case "$cond" in
  S) sys="$(cat "$REPO/plugin/SKILL.md")$NOTOOL" ;;
  M) sys="$(cat "$REPO/plugin/SKILL.md")$MORE$NOTOOL" ;;
  N) [ -r "$OUT/neutral.md" ] || { echo "먼저 make_neutral.py 를 돌린다" >&2; exit 2; }
     sys="$(cat "$OUT/neutral.md")$NOTOOL" ;;
  *) sys="${NOTOOL#$'\n\n'}" ;;
esac

W="$(mktemp -d -t kw-sd)" || exit 1
trap 'rm -rf "$W"' EXIT
# 빈 임시 폴더에서 돌린다. --setting-sources "" 로 사용자 설정과 훅을, --strict-mcp-config 로 MCP 도구 정의를 뺀다.
if (cd "$W" && claude -p "$(cat "$BASE/prompts/$task.txt")" --append-system-prompt "$sys" --no-session-persistence --tools "" \
    --strict-mcp-config --setting-sources "" --max-turns 1 --model "$model" --output-format json < /dev/null) > "$out.tmp" 2> "$out.err"; then
  mv "$out.tmp" "$out"
else
  echo "FAIL $task $cond $s"
fi
