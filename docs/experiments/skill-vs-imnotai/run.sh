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
#      결합 입력은 저장소의 plugin/scripts/prepare_monolith_input.py 가 만든다.
#
# 사용  : run.sh [출력디렉터리] [프롬프트ID...]
#         ID 를 안 주면 01 05 L1 L4 를 쓴다. 넷이 기본인 이유는 비용이다.
#         출력디렉터리를 안 주면 이 폴더의 out/run-<시각> 이다. out/ 은 커밋하지 않는다.
# 환경  : KW_MODEL 생성 모델(기본 claude-opus-5), KW_JUDGE 판정 모델(기본 claude-opus-5)
#         KW_RUBRIC 판정 기준서(기본 judge-rubric.md. judge-rubric-neutral.md 는 감점 목록 없는 중립 기준)
#         KW_REJUDGE=1 이면 생성을 건너뛰고 출력디렉터리의 글로 판정만 다시 한다
# 본문  : 판정 전에 양쪽 모두 HUMANIZE-SUMMARY 블록과, 마지막 --- 줄이 글의 뒤쪽 절반에 있으면 그 뒤 안내를 걷어낸다.
#         파이프라인 부산물과 어시스턴트 안내는 실제로 받는 본문이 아니어서다. 걷어낸 글은 body/ 에 남는다.
#         판정 결과는 judge-<기준서>-<판정 모델>/ 에 따로 쌓인다.
# 종료  : 스킬이 진 쌍이 이긴 쌍보다 많으면 1, 아니면 0. 필요한 파일이 없으면 2.
# 비용  : 프롬프트 4개 기준 생성 8회, 윤문 최대 14회, 판정 8회. LLM 을 부르므로 CI 에 넣지 않는다.
#         릴리스 전에 사람이 한 번 돌리는 자리다.
# 주의  : 병렬로 돌릴 때 claude 호출에 `< /dev/null` 을 붙인다. 붙이지 않으면 작업 목록 stdin 을
#         물어 마지막 묶음이 통째로 빈 출력을 낸다(실측: 24건 중 4건이 그렇게 죽었다).
#         스킬과 규칙집을 읽지 못하면 판정이 규칙 없는 글끼리 붙어도 끝까지 돈다. 그래서 먼저 확인하고 멈춘다.
#         설치본을 plugin/ 으로 나눈 뒤 2026-09-11 까지 이 스크립트가 옛 경로를 읽어 실제로 그렇게 돌았다.
set -uo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$BASE/../../.." && pwd)"
PLUGIN="$REPO/plugin"
export KW_REPO="$REPO"
OUT=${1:-"$BASE/out/run-$(date +%Y%m%d-%H%M%S)"}; shift 2>/dev/null || true
IDS=("$@"); [ ${#IDS[@]} -gt 0 ] || IDS=(01 05 L1 L4)
command -v claude >/dev/null 2>&1 || { echo "claude 가 없다" >&2; exit 2; }
for f in SKILL.md agents/humanize-monolith.md agents/humanize-diagnostician.md agents/humanize-finalizer.md \
         skills/humanize-korean/references/quick-rules.md skills/humanize-korean/references/ai-tell-taxonomy.md \
         scripts/prepare_monolith_input.py; do
  [ -r "$PLUGIN/$f" ] || { echo "필요한 파일이 없다: plugin/$f. 경로가 바뀌었으면 이 스크립트를 고친다" >&2; exit 2; }
done
mkdir -p "$OUT/gen" "$OUT/work"
echo "출력: $OUT"

MODEL=${KW_MODEL:-claude-opus-5}
JUDGE=${KW_JUDGE:-claude-opus-5}
RUBRIC=${KW_RUBRIC:-"$BASE/judge-rubric.md"}
case "$RUBRIC" in /*) ;; *) RUBRIC="$BASE/$RUBRIC" ;; esac
[ -r "$RUBRIC" ] || { echo "판정 기준서가 없다: $RUBRIC" >&2; exit 2; }
JDIR="$OUT/judge-$(basename "$RUBRIC" .md)-${JUDGE#claude-}"
mkdir -p "$JDIR" "$OUT/body"
echo "판정: $JUDGE · 기준서 $(basename "$RUBRIC")"
COMMON=(--strict-mcp-config --setting-sources "" --max-turns 1)
NOTOOL=$'\n\n## 이 실행의 예외\n이 세션에는 도구가 없다. 파일을 읽거나 쓰지 말고 요구한 산출물의 본문만 그대로 출력한다. 설명·머리말·코드펜스를 붙이지 않는다.'

# 계정 한도에 걸리면 claude 가 안내 문구를 본문 자리에 내놓는다. 그것을 글로 저장하면 측정이 통째로 거짓이 된다.
# 실측: 2026-09-11 판정 중 한도에 걸려 「You've hit your weekly limit」 64자가 글 열 개 자리에 들어갔다.
check_text() {
  local f=$1
  if [ ! -s "$f" ]; then echo "생성 실패(빈 파일): $f" >&2; return 1; fi
  if grep -q -E "hit your (weekly|usage) limit|usage limit reached|Credit balance is too low" "$f"; then
    echo "계정 한도에 걸렸다. 한도가 풀린 뒤 다시 돌린다: $f" >&2; return 1
  fi
  if [ "$(wc -m < "$f" | tr -d ' ')" -lt 120 ]; then echo "생성이 너무 짧다(120자 미만): $f" >&2; return 1; fi
  return 0
}

# 한 글을 만든다. 실패가 두 가지라 대응도 두 가지다.
# 계정 한도는 기다리는 것 말고 할 일이 없으므로 그 자리에서 멈춘다.
# 턴 한도(`Error: Reached max turns (1)`)와 빈 출력이 나오면 세 번까지 다시 만든다. 한 쌍이 죽으면
# 뒤의 판정 84건까지 통째로 못 도는 것이 더 비싸서다. 되풀이해 죽으면 원인이 따로 있다는 뜻이다.
# 실측 2026-09-13: L3 이 세 번 내리 죽었고 원인은 아래 생성 호출에 도구 안내가 빠진 것이었다.
gen_to() { # gen_to <출력파일> <프롬프트파일> [claude 에 넘길 인자...]
  local out=$1 q=$2 try
  shift 2
  for try in 1 2 3; do
    claude -p "$(cat "$q")" "$@" --model "$MODEL" "${COMMON[@]}" > "$out" 2>/dev/null < /dev/null
    if grep -q -E "hit your (weekly|usage) limit|usage limit reached|Credit balance is too low" "$out"; then
      echo "계정 한도에 걸렸다. 한도가 풀린 뒤 다시 돌린다: $out" >&2
      return 1
    fi
    check_text "$out" 2>/dev/null && return 0
    echo "    다시 생성 $try/3: $(basename "$out")" >&2
    sleep 20   # 실패가 잇따르면 잠깐 기다렸다 부른다
  done
  check_text "$out"
}

sys_of() { # sys_of <에이전트파일> <규칙집파일>
  cat "$PLUGIN/agents/$1"; echo; echo "## 규칙집"; echo; cat "$PLUGIN/skills/humanize-korean/references/$2"; printf '%s' "$NOTOOL"
}

for id in "${IDS[@]}"; do
  q="$BASE/prompts/$id.txt"
  [ -r "$q" ] || { echo "프롬프트 없음: $id" >&2; exit 2; }
  if [ -n "${KW_REJUDGE:-}" ]; then
    if [ ! -s "$OUT/gen/skill_$id.md" ] || [ ! -s "$OUT/gen/imnotai_$id.md" ]; then
      echo "판정만 다시 하려는데 생성물이 없다: $id" >&2
      exit 2
    fi
    continue
  fi
  echo "  생성 $id"
  # 도구가 없다는 말을 안 하면 모델이 첫 턴에 도구를 부르려다 턴을 다 써서 본문 없이 끝난다.
  # 실측 2026-09-13: 이 안내 없이 부른 L1 과 L3 이 `Error: Reached max turns (1)` 로 죽었고,
  # 같은 프롬프트와 같은 턴 한도에 이 안내만 붙여 따로 다섯 번 부르니 모두 본문이 나왔다.
  # 두 쪽에 똑같은 문구를 붙여 쌍 안의 조건을 맞춘다.
  gen_to "$OUT/gen/skill_$id.md" "$q" --append-system-prompt "$(cat "$PLUGIN/SKILL.md")$NOTOOL" || exit 1
  gen_to "$OUT/gen/plain_$id.md" "$q" --append-system-prompt "$NOTOOL" || exit 1

  echo "  윤문 $id"
  run="$OUT/work/$id"; mkdir -p "$run"; cp "$OUT/gen/plain_$id.md" "$run/01_input.txt"
  python3 "$PLUGIN/scripts/prepare_monolith_input.py" --run-dir "$run" --genre column >/dev/null 2>&1 || exit 1
  case "$id" in
    L*)  # 정밀 3콜
      claude -p "다음 결합 입력을 진단하라. 진단 본문만 출력한다.

$(cat "$run/01_input_with_metrics.txt")" \
        --append-system-prompt "$(sys_of humanize-diagnostician.md ai-tell-taxonomy.md)" \
        --model "$MODEL" "${COMMON[@]}" > "$run/02_diagnosis.md" 2>/dev/null < /dev/null
      python3 "$PLUGIN/scripts/prepare_monolith_input.py" --run-dir "$run" --genre column \
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
  check_text "$OUT/gen/imnotai_$id.md" || exit 1
  python3 - "$run/01_input.txt" "$OUT/gen/imnotai_$id.md" <<'PY'
import sys, os
sys.path.insert(0, os.path.join(os.environ["KW_REPO"], "plugin/skills/humanize-korean/references"))
import metrics_v2
a = open(sys.argv[1], encoding="utf-8").read()
b = open(sys.argv[2], encoding="utf-8").read()
print(f"    변경률 {metrics_v2.change_rate(a, b, ignore_markup=True) * 100:.1f}%")
PY
done

# 본문만 남긴다. 양쪽에 같은 규칙을 쓴다.
python3 - "$OUT" "${IDS[@]}" <<'PY'
import re, sys
out, ids = sys.argv[1], sys.argv[2:]
for i in ids:
    for side in ("skill", "imnotai"):
        t = open(f"{out}/gen/{side}_{i}.md", encoding="utf-8").read()
        t = re.sub(r"<!--\s*HUMANIZE-SUMMARY\s*-->.*?(<!--\s*/HUMANIZE-SUMMARY\s*-->|\Z)", "", t, flags=re.S).rstrip()
        lines = t.split("\n")
        cut = max((k for k, l in enumerate(lines) if l.strip() == "---"), default=-1)
        if cut > 0 and len("\n".join(lines[:cut])) >= 0.5 * len(t):
            t = "\n".join(lines[:cut]).rstrip()
        open(f"{out}/body/{side}_{i}.md", "w", encoding="utf-8").write(t + "\n")
PY

echo
for id in "${IDS[@]}"; do
  for o in 1 2; do
    if [ "$o" = 1 ]; then r1="$OUT/body/skill_$id.md"; r2="$OUT/body/imnotai_$id.md"
    else r1="$OUT/body/imnotai_$id.md"; r2="$OUT/body/skill_$id.md"; fi
    {
      cat "$RUBRIC"; echo
      echo "## 요청"; cat "$BASE/prompts/$id.txt"; echo
      echo "## 글 1"; cat "$r1"; echo
      echo "## 글 2"; cat "$r2"
    } > "$JDIR/${id}_o$o.prompt"
    claude -p "$(cat "$JDIR/${id}_o$o.prompt")" --model "$JUDGE" "${COMMON[@]}" \
      > "$JDIR/${id}_o$o.json" 2>/dev/null < /dev/null
  done
done

python3 - "$JDIR" "${IDS[@]}" <<'PY'
import json, re, sys, os, collections
out, ids = sys.argv[1], sys.argv[2:]
win = collections.Counter(); split = 0; bad = 0
for i in ids:
    got = {}
    for o in ("1", "2"):
        raw = open(f"{out}/{i}_o{o}.json", encoding="utf-8").read()
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
decided = win["skill"] + win["imnotai"] + win["tie"] + split
if bad:
    print("판정이 실패했다. 계정 사용량이 남아 있는지 확인하라 (실측: 소진 메시지가 JSON 자리에 들어온다).")
if decided == 0:
    # 판정이 하나도 서지 않았다. 「회귀 없음」 으로 끝내면 돌리지도 못한 판을 통과로 읽게 된다.
    print("판정 불가. 결과로 쓰지 않는다.")
    sys.exit(2)
print("스킬이 졌다." if win["imnotai"] > win["skill"] else "회귀 없음.")
sys.exit(1 if win["imnotai"] > win["skill"] else 0)
PY
