#!/usr/bin/env bash
# 주입 규칙을 고쳤을 때 답변이 나빠지지 않았는지 본다.
#
# 왜 : 훅의 정규식은 평소 답변에서 표본당 0.21 건만 잡아 회귀 감시에 못 쓴다(EVALUATION.md C5).
#      답변 품질은 블라인드 쌍대 판정으로만 잡힌다.
# 무엇: 옛 규칙과 새 규칙으로 같은 프롬프트를 각각 생성하고, 어느 쪽이 새 규칙인지 모르는
#      판정자에게 순서를 바꿔 두 번 물어 이긴 쪽을 센다.
# 왜 규칙끼리 비교하나: 채택 시점의 답변을 얼려 두고 대조하면 모델이 바뀔 때 그 차이까지
#      회귀로 잡힌다. 두 규칙을 같은 시각 같은 모델로 돌리면 규칙 차이만 남는다.
#
# 사용  : regress.sh 옛규칙.md 새규칙.md [프롬프트ID...]
#         ID 를 안 주면 01 05 09 11 을 쓴다. 네 개가 기본인 이유는 비용이다.
# 종료  : 새 규칙이 진 쌍이 이긴 쌍보다 많으면 1, 아니면 0.
# 비용  : 프롬프트 4개 기준 생성 8회와 판정 8회로 3~4달러. LLM 을 부르므로 CI 에는 넣지 않는다.
#         릴리스 전에 사람이 한 번 돌리는 자리다.
set -uo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"

[ $# -ge 2 ] || { echo "사용: regress.sh 옛규칙.md 새규칙.md [프롬프트ID...]" >&2; exit 2; }
OLD=$1; NEW=$2; shift 2
IDS=("$@"); [ ${#IDS[@]} -gt 0 ] || IDS=(01 05 09 11)
for f in "$OLD" "$NEW"; do [ -r "$f" ] || { echo "못 읽음: $f" >&2; exit 2; }; done
command -v claude >/dev/null 2>&1 || { echo "claude 가 없다" >&2; exit 2; }

WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
# 전역 지침은 저장소에 두지 않는다. 사용자 것을 그때그때 읽어 붙인다.
# --setting-sources "" 로 사용자 설정을 뺐으므로 이렇게 되살려야 C5 와 조건이 같다.
SYS="$WORK/sys.txt"
{ echo "이 세션에는 도구와 스킬이 없다. 도구 호출을 흉내 내지 말고 지금 아는 것으로 바로 답한다."
  [ -r "$HOME/.claude/CLAUDE.md" ] && { echo; cat "$HOME/.claude/CLAUDE.md"; }
} > "$SYS"

# 함정 둘을 여기서 막는다. README 의 「먼저 읽을 것」 참고.
#
# 모델은 KW_REGRESS_MODEL 로 바꿀 수 있다. 기본은 claude-fable-5-1 이고 지난 판정도 그것으로 냈다.
# 그 모델의 사용량이 떨어지면 생성물 자리에 안내 문구가 들어와 여덟 건이 통째로 무효가 된다.
# 실제로 2026-09-11 에 그렇게 멈췄다. 모델을 바꿔 돌린 결과는 지난 판정과 곧바로 견주지 않는다.
MODEL="${KW_REGRESS_MODEL:-claude-fable-5-1}"
COMMON=(--no-session-persistence --strict-mcp-config --setting-sources ""
        --model "$MODEL" --effort xhigh --tools "" --output-format json)

settings_for() { # settings_for <규칙파일> <출력경로>
  python3 - "$1" "$2" <<'PY'
import json, sys, os
rules, out = os.path.abspath(sys.argv[1]), sys.argv[2]
cmd = "sed '/korean-writing: ignore/d' " + json.dumps(rules)
json.dump({"hooks": {"SessionStart": [{"matcher": "startup",
          "hooks": [{"type": "command", "command": cmd, "timeout": 10}]}]}},
          open(out, "w"), ensure_ascii=False)
PY
}
mkdir -p "$WORK/cfg"   # 설정을 생성물과 같은 자리에 두면 validate.py 가 생성물로 오인한다
settings_for "$OLD" "$WORK/cfg/old.json"
settings_for "$NEW" "$WORK/cfg/new.json"

echo "옛 규칙: $OLD"
echo "새 규칙: $NEW"
echo "프롬프트: ${IDS[*]}"
echo "모델: $MODEL"

for id in "${IDS[@]}"; do
  p="$BASE/prompts/$id.txt"
  [ -r "$p" ] || { echo "프롬프트 없음: $p" >&2; exit 2; }
  for side in old new; do
    claude -p "$(cat "$p")" --append-system-prompt "$(cat "$SYS")" \
      "${COMMON[@]}" --settings "$WORK/cfg/$side.json" < /dev/null > "$WORK/${id}_${side}.json" 2>/dev/null
  done
  echo "  생성 $id"
done

# 생성물이 실제 답변인지 먼저 본다. 이 검사를 건너뛰어 1차 실험을 통째로 버린 적이 있다.
python3 "$BASE/validate.py" "$WORK" || true
bad=$(python3 - "$WORK" <<'PY'
import glob, json, os, re, sys
n = 0
for f in glob.glob(os.path.join(sys.argv[1], "*_*.json")):
    t = (json.load(open(f)).get("result") or "")
    if len(re.findall(r"[가-힣]", t)) < 150 or re.search(r"antml:|<invoke|function_results", t):
        n += 1
print(n)
PY
)
[ "$bad" = "0" ] || { echo "무효 생성물 ${bad}건. 판정하지 않는다." >&2; exit 2; }

judge() { # judge <id> <순서 1|2>
  local id=$1 o=$2
  python3 - "$BASE" "$WORK" "$id" "$o" > "$WORK/j_${id}_$o.txt" <<'PY'
import json, sys
base, w, id, o = sys.argv[1:5]
q = open(f"{base}/prompts/{id}.txt").read()
a = json.load(open(f"{w}/{id}_old.json"))["result"]
b = json.load(open(f"{w}/{id}_new.json"))["result"]
r1, r2 = (a, b) if o == "1" else (b, a)
print(f"""당신은 한국어 문체 심사자다. 같은 질문에 대한 두 답변 중 어느 쪽이 더 자연스러운 한국어인지 판정한다. 내용의 옳고 그름은 기준이 아니다. 문체만 본다.

감점 패턴: 사물·개념 의인화, 영어 직역 비유, 추상 구조어(축·갈래·결·레이어), 줄표 삽입구, 첫째·둘째 병렬, 목록이 아닌 내용을 불릿으로 쪼갬, 번역투, AI 관용구(결론적으로·요약하면·시사하는 바·혁신적·~할 때다), 문두 접속사 남발, 형식명사 남발, 문장 길이가 다 비슷함, 이모지, 굵게 남발, 한 답변 안에서 문체가 바뀜.

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
  claude -p "$(cat "$WORK/j_${id}_$o.txt")" "${COMMON[@]}" < /dev/null > "$WORK/v_${id}_$o.json" 2>/dev/null
}

win_new=0; win_old=0; tie=0
for id in "${IDS[@]}"; do
  judge "$id" 1; judge "$id" 2
  r=$(python3 - "$WORK" "$id" <<'PY'
import json, re, sys
w, id = sys.argv[1:3]
def pick(o):
    t = json.load(open(f"{w}/v_{id}_{o}.json"))["result"]
    m = re.search(r'"winner"\s*:\s*"(1|2|tie)"', t)
    if not m: return "tie"
    v = m.group(1)
    if v == "tie": return "tie"
    return ({"1": "old", "2": "new"} if o == "1" else {"1": "new", "2": "old"})[v]
a, b = pick("1"), pick("2")
print(a if a == b else "tie")
PY
)
  case "$r" in new) win_new=$((win_new+1));; old) win_old=$((win_old+1));; *) tie=$((tie+1));; esac
  echo "  판정 $id -> $r"
done

echo
echo "새 규칙 승 $win_new / 옛 규칙 승 $win_old / 무승부 $tie"
if [ "$win_old" -gt "$win_new" ]; then
  echo "회귀 의심. 새 규칙이 진 쌍이 더 많다. 바꾼 줄을 다시 보라."
  exit 1
fi
echo "회귀 없음."
exit 0
