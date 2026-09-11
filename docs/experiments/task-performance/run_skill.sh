#!/usr/bin/env bash
# 스킬 오발동 한 건. usage: run_skill.sh <id|POS> <cond A|B> <sample>
# 주입문이 "글 작성 요청은 스킬을 먼저 로드한다"고 지시한다. 코드 작업에서 그것이 뜨면 본문 몫이 든다.
# POS 는 양성 대조다. 진짜 글 작성 요청이므로 스킬이 떠야 한다. 검출기가 도는지 여기서 본다.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$here/../../.." && pwd)"
id=$1; cond=$2; s=$3
mkdir -p "$here/skillout"
out="$here/skillout/${id}_${cond}_${s}.jsonl"
[ -s "$out" ] && exit 0
if [ "$cond" = "A" ]; then export KOREAN_WRITING_ALWAYS_ON_DISABLED=1; else unset KOREAN_WRITING_ALWAYS_ON_DISABLED; fi
if [ "$id" = "POS" ]; then p="팀 슬랙에 올릴 배포 완료 공지를 한국어로 써줘."; else p="$(cat "$here/prompts-skill/$id.txt")"; fi
cd "$REPO" || exit 1
claude -p "$p" \
  --plugin-dir "$REPO" --strict-mcp-config --setting-sources "" \
  --dangerously-skip-permissions --max-turns 10 --model claude-opus-5 \
  --verbose --output-format stream-json < /dev/null > "$out.tmp" 2> "$out.err"
# 턴 제한에 걸려도 스트림은 남는다. 스킬 호출은 첫 턴에 일어나므로 잘린 것으로도 판정된다.
mv "$out.tmp" "$out"
