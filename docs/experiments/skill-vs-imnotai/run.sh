#!/usr/bin/env bash
# korean-writing 스킬로 처음부터 쓴 글과 im-not-ai 로 사후 윤문한 글을 블라인드로 붙인다.
#
# 왜 : 이 플러그인의 목표가 "스킬 품질이 im-not-ai 수준이 되거나 그보다 높은 것" 이다.
#      정규식으로 센 표지 개수는 그 답이 되지 못한다. 2026-09-10 실측에서 표지를 1.95 에서
#      0.25 로 줄인 판이 블라인드 판정에서는 옛 판을 이기지 못했다(EVALUATION.md C7).
# 무엇: 프롬프트마다 두 글을 만든다. 하나는 스킬을 시스템 프롬프트로 붙여 처음부터 쓴 것,
#      다른 하나는 규칙 없이 쓴 뒤 im-not-ai 파이프라인으로 윤문한 것이다. 어느 쪽이
#      어느 조건인지 모르는 판정자에게 순서를 바꿔 두 번 묻는다.
# 경로: 단문(01~08)은 Fast Path 한 콜, 장문(L1~L6)은 정밀 3콜(진단·윤문·마무리)로 윤문한다.
#      결합 입력은 저장소의 scripts/prepare_monolith_input.py 가 만든다.
#
# 사용  : run.sh [출력디렉터리] [프롬프트ID...]
#         ID 를 안 주면 01 05 L1 L4 를 쓴다. 넷이 기본인 이유는 비용이다.
# 종료  : 스킬이 진 쌍이 이긴 쌍보다 많으면 1, 아니면 0.
# 비용  : 프롬프트 4개 기준 생성 8회, 윤문 최대 14회, 판정 8회. LLM 을 부르므로 CI 에 넣지 않는다.
#         릴리스 전에 사람이 한 번 돌리는 자리다.
# 주의  : 병렬로 돌릴 때 claude 호출에 `< /dev/null` 을 붙인다. 붙이지 않으면 작업 목록 stdin 을
#         물어 마지막 묶음이 통째로 빈 출력을 낸다(실측: 24건 중 4건이 그렇게 죽었다).
set -uo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$BASE/../../.." && pwd)"
OUT=${1:-"$BASE/run-$(date +%Y%m%d-%H%M%S)"}; shift 2>/dev/null || true
IDS=("$@"); [ ${#IDS[@]} -gt 0 ] || IDS=(01 05 L1 L4)
command -v claude >/dev/null 2>&1 || { echo "claude 가 없다" >&2; exit 2; }
mkdir -p "$OUT/gen" "$OUT/work" "$OUT/judge"

MODEL=${KW_MODEL:-claude-opus-5}
JUDGE=${KW_JUDGE:-claude-opus-5}
COMMON=(--strict-mcp-config --setting-sources "" --max-turns 1)
NOTOOL=$'\n\n## 이 실행의 예외\n이 세션에는 도구가 없다. 파일을 읽거나 쓰지 말고 요구한 산출물의 본문만 그대로 출력한다. 설명·머리말·코드펜스를 붙이지 않는다.'

sys_of() { # sys_of <에이전트파일> <규칙집파일>
  cat "$REPO/agents/$1"; echo; echo "## 규칙집"; echo; cat "$REPO/skills/humanize-korean/references/$2"; printf '%s' "$NOTOOL"
}

for id in "${IDS[@]}"; do
  q="$BASE/prompts/$id.txt"
  [ -r "$q" ] || { echo "프롬프트 없음: $id" >&2; exit 2; }
  echo "  생성 $id"
  claude -p "$(cat "$q")" --append-system-prompt "$(cat "$REPO/SKILL.md")" --model "$MODEL" "${COMMON[@]}" \
    > "$OUT/gen/skill_$id.md" 2>/dev/null < /dev/null
  claude -p "$(cat "$q")" --model "$MODEL" "${COMMON[@]}" \
    > "$OUT/gen/plain_$id.md" 2>/dev/null < /dev/null
  [ -s "$OUT/gen/skill_$id.md" ] && [ -s "$OUT/gen/plain_$id.md" ] || { echo "생성 실패: $id" >&2; exit 1; }

  echo "  윤문 $id"
  run="$OUT/work/$id"; mkdir -p "$run"; cp "$OUT/gen/plain_$id.md" "$run/01_input.txt"
  python3 "$REPO/scripts/prepare_monolith_input.py" --run-dir "$run" --genre column >/dev/null 2>&1 || exit 1
  case "$id" in
    L*)  # 정밀 3콜
      claude -p "다음 결합 입력을 진단하라. 진단 본문만 출력한다.

$(cat "$run/01_input_with_metrics.txt")" \
        --append-system-prompt "$(sys_of humanize-diagnostician.md ai-tell-taxonomy.md)" \
        --model "$MODEL" "${COMMON[@]}" > "$run/02_diagnosis.md" 2>/dev/null < /dev/null
      python3 "$REPO/scripts/prepare_monolith_input.py" --run-dir "$run" --genre column \
        --diagnosis "$run/02_diagnosis.md" >/dev/null 2>&1 || exit 1 ;;
  esac
  claude -p "다음 결합 입력을 윤문하라. 본문만 출력한다. HUMANIZE-SUMMARY 블록은 붙이지 않는다.

$(cat "$run/01_input_with_metrics.txt")" \
    --append-system-prompt "$(sys_of humanize-monolith.md quick-rules.md)" \
    --model "$MODEL" "${COMMON[@]}" > "$run/05_rewritten.md" 2>/dev/null < /dev/null
  case "$id" in
    L*)
      claude -p "원문과 윤문본을 대조해 의미 보존과 자연성을 판정하고 문제 구간만 국소 보정하라. 최종 본문만 출력한다.

## 원문
$(cat "$run/01_input.txt")

## 윤문본
$(cat "$run/05_rewritten.md")" \
        --append-system-prompt "$(sys_of humanize-finalizer.md quick-rules.md)" \
        --model "$MODEL" "${COMMON[@]}" > "$OUT/gen/imnotai_$id.md" 2>/dev/null < /dev/null ;;
  esac
  [ -s "$OUT/gen/imnotai_$id.md" ] || cp "$run/05_rewritten.md" "$OUT/gen/imnotai_$id.md"
  python3 - "$run/01_input.txt" "$OUT/gen/imnotai_$id.md" <<'PY'
import sys, os
sys.path.insert(0, os.path.join(os.environ["KW_REPO"], "skills/humanize-korean/references"))
import metrics_v2
a = open(sys.argv[1], encoding="utf-8").read()
b = open(sys.argv[2], encoding="utf-8").read()
print(f"    변경률 {metrics_v2.change_rate(a, b, ignore_markup=True) * 100:.1f}%")
PY
done

echo
for id in "${IDS[@]}"; do
  for o in 1 2; do
    if [ "$o" = 1 ]; then r1="$OUT/gen/skill_$id.md"; r2="$OUT/gen/imnotai_$id.md"
    else r1="$OUT/gen/imnotai_$id.md"; r2="$OUT/gen/skill_$id.md"; fi
    {
      cat "$BASE/judge-rubric.md"; echo
      echo "## 요청"; cat "$BASE/prompts/$id.txt"; echo
      echo "## 글 1"; cat "$r1"; echo
      echo "## 글 2"; cat "$r2"
    } > "$OUT/judge/${id}_o$o.prompt"
    claude -p "$(cat "$OUT/judge/${id}_o$o.prompt")" --model "$JUDGE" "${COMMON[@]}" \
      > "$OUT/judge/${id}_o$o.json" 2>/dev/null < /dev/null
  done
done

python3 - "$OUT" "${IDS[@]}" <<'PY'
import json, re, sys, os, collections
out, ids = sys.argv[1], sys.argv[2:]
win = collections.Counter(); split = 0; bad = 0
for i in ids:
    got = {}
    for o in ("1", "2"):
        raw = open(f"{out}/judge/{i}_o{o}.json", encoding="utf-8").read()
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            bad += 1
            print(f"  판정 실패 {i} 순서{o}: {raw.strip()[:90]}")
            continue
        try:
            w = json.loads(m.group(0)).get("winner")
        except Exception:
            bad += 1
            continue
        got[o] = "tie" if w == "tie" else (("skill" if w == "1" else "imnotai") if o == "1"
                                           else ("imnotai" if w == "1" else "skill"))
    if len(got) < 2:
        continue
    if got["1"] == got["2"]:
        win[got["1"]] += 1
        print(f"  판정 {i} -> {got['1']}")
    else:
        split += 1
        print(f"  판정 {i} -> 순서에 따라 갈림")
print(f"\n스킬 승 {win['skill']} / im-not-ai 승 {win['imnotai']} / 무 {win['tie']} / 갈림 {split} / 판정 실패 {bad}")
if bad:
    print("판정이 실패했다. 계정 사용량이 남아 있는지 확인하라 (실측: 소진 메시지가 JSON 자리에 들어온다).")
print("스킬이 졌다." if win["imnotai"] > win["skill"] else "회귀 없음.")
sys.exit(1 if win["imnotai"] > win["skill"] else 0)
PY
