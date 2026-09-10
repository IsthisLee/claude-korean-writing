#!/usr/bin/env bash
# usage: judge_one.sh <prompt_id> <sample> <order 1|2>   order1 = A first, order2 = B first
set -u
cd "$(dirname "$0")"
id=$1; s=$2; o=$3
out="judge_v5/${id}_${s}_o${o}.json"
[ -s "$out" ] && exit 0
python3 - "$id" "$s" "$o" > "$out.prompt" <<'PY'
import sys, json
id, s, o = sys.argv[1:4]
q = open(f"prompts/{id}.txt").read()
a = json.load(open(f"out/{id}_A_{s}.json"))["result"]
b = json.load(open(f"out_v5/{id}_B_{s}.json"))["result"]
r1, r2 = (a, b) if o == "1" else (b, a)
print(f"""당신은 한국어 문체 심사자다. 같은 질문에 대한 두 답변을 비교해 어느 쪽이 더 자연스러운 한국어인지 판정한다. 내용의 옳고 그름은 판정 기준이 아니다. 문체만 본다.

"자연스러운 한국어" 의 기준:
- 사람이 말하듯 쓴 글. 영어 문장을 옮긴 티가 없는 글.
- 감점 패턴: 사물·개념 의인화(화면이 굳다, A가 B를 이긴다), 영어 직역 비유, 추상 구조어(축·갈래·결·레이어), 줄표(—) 삽입구, 첫째·둘째 기계적 병렬, 목록이 아닌 내용을 불릿으로 쪼갬, 번역투(~에 대해·~를 통해 남발, 가지고 있다, 되어진다, ~에 의해, ~할 수 있다 남발, ~것들), AI 관용구(결론적으로·요약하면·시사하는 바·혁신적·획기적·압도적·~할 때다), 문두 접속사 남발(또한·따라서·즉), 형식명사 남발(것·점·수·바), 문장 길이가 다 비슷함, 이모지, 굵게 남발.
- 격식이 낮거나 높은 것은 감점이 아니다. 딱딱한 글과 AI 티는 다르다.
- 길이는 판정 기준이 아니다.

아래 JSON 만 출력한다. 다른 말은 쓰지 않는다.
{{"winner": "1" 또는 "2" 또는 "tie",
 "why": "한두 문장",
 "issues_1": ["답변1에서 본 감점 패턴을 짧게"],
 "issues_2": ["답변2에서 본 감점 패턴을 짧게"],
 "fact_problem_1": true/false, "fact_problem_2": true/false,
 "register_drop_1": true/false, "register_drop_2": true/false,
 "code_damage_1": true/false, "code_damage_2": true/false}}

fact_problem: 그 답변에 기술적으로 틀린 내용이 있거나, 상대 답변에는 있는 핵심 정보가 빠졌으면 true.
register_drop: 반말이나 구어체가 섞이거나 한 답변 안에서 문체가 오락가락하면 true.
code_damage: 코드·명령어·에러 문자열을 잘못 옮기거나 깨뜨렸으면 true.

=== 질문 ===
{q}

=== 답변 1 ===
{r1}

=== 답변 2 ===
{r2}
""")
PY
claude -p "$(cat "$out.prompt")" --no-session-persistence --tools "" --strict-mcp-config --setting-sources "" --model claude-fable-5-1 --effort xhigh --append-system-prompt "$(cat control.txt)" --output-format json < /dev/null > "$out.tmp" 2> "$out.err" && mv "$out.tmp" "$out" || echo "FAIL judge $id $s $o"
