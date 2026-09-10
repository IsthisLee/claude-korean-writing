#!/usr/bin/env bash
# 긴 대화 실험 판정. 두 가지를 본다.
#  A) late_on vs late_off  : 30턴 뒤에도 주입이 도움이 되는가
#  B) early_on vs late_on  : 주입 조건 안에서 앞뒤가 달라지는가 (효과가 옅어지는가)
set -uo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
EXP="$(cd "$BASE/../exp" && pwd)"
mkdir -p "$BASE/verdict"
COMMON=(--no-session-persistence --strict-mcp-config --setting-sources "" --model claude-fable-5-1 --effort xhigh --tools "" --output-format json)

one() { # one <태그> <파일1> <파일2> <id> <순서>
  local tag=$1 f1=$2 f2=$3 id=$4 o=$5
  local out="$BASE/verdict/${tag}_${id}_o${o}.json"
  [ -s "$out" ] && return 0
  python3 - "$EXP/prompts/$id.txt" "$f1" "$f2" "$o" > "$out.p" <<'PY'
import json, sys
q = open(sys.argv[1]).read()
a = json.load(open(sys.argv[2]))["result"]
b = json.load(open(sys.argv[3]))["result"]
r1, r2 = (a, b) if sys.argv[4] == "1" else (b, a)
print(f"""당신은 한국어 문체 심사자다. 같은 질문에 대한 두 답변 중 어느 쪽이 더 자연스러운 한국어인지 판정한다. 내용의 옳고 그름은 기준이 아니다. 문체만 본다.

감점 패턴: 사물·개념 의인화, 영어 직역 비유, 추상 구조어(축·갈래·결·레이어), 줄표 삽입구, 첫째·둘째 병렬, 목록이 아닌 내용을 불릿으로 쪼갬, 번역투(~에 대해·~를 통해 남발, 가지고 있다, 되어진다, ~에 의해, ~할 수 있다 남발, ~것들), AI 관용구(결론적으로·요약하면·시사하는 바·혁신적·~할 때다), 문두 접속사 남발, 형식명사 남발, 문장 길이가 다 비슷함, 이모지, 굵게 남발, 한 답변 안에서 문체가 바뀜.

격식이 높거나 낮은 것 자체는 감점이 아니다. 길이도 기준이 아니다.

아래 JSON 만 출력한다.
{{"winner": "1" 또는 "2" 또는 "tie", "why": "한 문장"}}

=== 질문 ===
{q}

=== 답변 1 ===
{r1}

=== 답변 2 ===
{r2}
""")
PY
  claude -p "$(cat "$out.p")" "${COMMON[@]}" < /dev/null > "$out" 2>/dev/null
  rm -f "$out.p"
}

for id in 02 06 07 12; do
  for o in 1 2; do
    one freshAB "$BASE/off/fresh_$id.json" "$BASE/on/fresh_$id.json" "$id" "$o"
    
  done
  echo "판정 $id 완료"
done
