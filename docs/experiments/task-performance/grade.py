#!/usr/bin/env python3
"""상시 규칙 주입이 과제 수행에 영향을 주는지 채점한다.

A 는 주입 없음, B 는 주입 있음. 문체는 보지 않는다. 이 실험이 묻는 것은
"규칙을 넣으면 모델이 일을 덜 잘하는가" 하나다.

정확도(T)는 답이 하나로 떨어지므로 문자열 비교다.
지시 준수(C)는 사용자가 명시로 요청한 것을 실제로 냈는지만 본다.
서브에이전트(S)는 조사 결과의 정확도와 답변 언어를 본다.
스킬 오발동(K)은 코드 작업에서 글 작성 스킬이 떴는지 센다. POS 는 양성 대조다.

실행: ./grade.py   (run_all.sh 가 마지막에 부른다)
"""
import json
import math
import pathlib
import re
import statistics

HERE = pathlib.Path(__file__).resolve().parent

TRUTH = {
    "T01": "[1, 2, 3]", "T02": "0", "T03": "NO", "T04": "YES", "T05": "3,3,3",
    "T06": "3", "T07": "[[1, 0], [1, 0], [1, 0]]", "T08": "1,10,2",
    "T09": "False", "T10": "-4",
}
ASK = {"C1": "불릿 5개", "C2": "이모지 필수", "C3": "영어로 답",
       "C4": "첫째·둘째·셋째", "C5": "영어 질문"}
SUB_TRUTH = {"S1": "6,30", "S2": "10"}

EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF⭐✅❌✨🎉🚀]")


def answer(text):
    m = re.findall(r"ANSWER\s*=\s*(.+)", text)
    return m[-1].strip().rstrip(".").strip("`") if m else None


def norm(s):
    return re.sub(r"\s+", " ", s).strip() if s else s


def hangul_ratio(text):
    letters = re.findall(r"[가-힣A-Za-z]", text)
    return len(re.findall(r"[가-힣]", text)) / len(letters) if letters else 0.0


def grade_conflict(pid, text):
    if pid == "C1":
        n = len([l for l in text.split("\n") if re.match(r"^\s*[-*•]\s+\S", l)])
        return n == 5, f"불릿 {n}"
    if pid == "C2":
        n = len(EMOJI.findall(text))
        return n > 0, f"이모지 {n}"
    if pid in ("C3", "C5"):
        r = hangul_ratio(text)
        return r < 0.10, f"한글 {r*100:.0f}%"
    if pid == "C4":
        got = [w for w in ("첫째", "둘째", "셋째") if w in text]
        return len(got) == 3, f"{got}"
    return None, ""


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def diff_ci(k1, n1, k2, n2):
    """두 비율 차이의 95% 구간 (Newcombe). 작은 표본에서 정규 근사보다 낫다."""
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    p1, p2 = k1 / n1, k2 / n2
    lo = (p2 - p1) - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = (p2 - p1) + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return lo, hi


def load(dirname, pattern="*.json"):
    d = HERE / dirname
    rows = []
    if not d.exists():
        return rows
    for f in sorted(d.glob(pattern)):
        pid, cond, s = f.stem.split("_")
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        u = j.get("usage", {}) or {}
        rows.append({
            "pid": pid, "cond": cond, "text": j.get("result", "") or "",
            "cost": j.get("total_cost_usd", 0.0), "ms": j.get("duration_ms", 0),
            "turns": j.get("num_turns", 0),
            "tok": (u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                    + u.get("cache_read_input_tokens", 0)),
            "out": u.get("output_tokens", 0),
        })
    return rows


def table(rows, keys, grader, labeler):
    if not rows:
        return None
    tot = {"A": [0, 0], "B": [0, 0]}
    print(f"\n  {'문항':<22} {'A 주입없음':<15} {'B 주입있음':<15}  어긋난 것")
    print("  " + "-" * 70)
    for pid in sorted(keys):
        cells, bad_all = [], []
        for c in "AB":
            sel = [r for r in rows if r["pid"] == pid and r["cond"] == c]
            res = [grader(pid, r["text"]) for r in sel]
            ok = [x[0] for x in res]
            tot[c][0] += sum(ok)
            tot[c][1] += len(ok)
            cells.append(f"{sum(ok)}/{len(ok)} " + "".join("o" if x else "X" for x in ok))
            bad_all += [f"{c}:{d}" for x, d in res if not x]
        print(f"  {labeler(pid):<22} {cells[0]:<15} {cells[1]:<15}  {', '.join(bad_all)[:34]}")
    print("  " + "-" * 70)
    a, b = tot["A"], tot["B"]
    if a[1] and b[1]:
        lo, hi = diff_ci(a[0], a[1], b[0], b[1])
        print(f"  {'합계':<22} {a[0]}/{a[1]} ({a[0]/a[1]*100:.0f}%){'':<5} "
              f"{b[0]}/{b[1]} ({b[0]/b[1]*100:.0f}%){'':<5}  차이 95% CI "
              f"[{lo*100:+.1f}, {hi*100:+.1f}]%p")
    return tot


def truth_grader(truth):
    def g(pid, text):
        got = answer(text)
        return norm(got) == norm(truth[pid]), str(got)
    return g


print("=" * 78)
print("주입이 과제 수행에 영향을 주는가 — A 주입 없음 / B 주입 있음")
print("=" * 78)

for model, note in (("claude-haiku-4-5-20251001", "여유가 있어 저하가 드러나는 조건"),
                    ("claude-opus-5", "실제로 쓰는 모델")):
    rows = [r for r in load(f"out/{model}") if r["pid"] in TRUTH]
    if rows:
        print(f"\n■ 정확도 — {model} ({note})")
        table(rows, set(TRUTH), truth_grader(TRUTH), lambda p: f"{p} (정답 {TRUTH[p][:14]})")

rows = [r for r in load("out/claude-opus-5") if r["pid"] in ASK]
if rows:
    print("\n■ 사용자 지시 준수 — 규칙과 반대되는 것을 명시로 요청했다")
    table(rows, set(ASK), grade_conflict, lambda p: f"{p} {ASK[p]}")

rows = load("subout")
if rows:
    print("\n■ 서브에이전트 — A 는 주입 끔, B 는 켬")
    table(rows, set(SUB_TRUTH), truth_grader(SUB_TRUTH), lambda p: f"{p} (정답 {SUB_TRUTH[p]})")
    print("\n  S2 는 영어로 답하라고 했다. 한글이 섞이면 주입이 언어를 끌어당긴 것이다.")
    for c in "AB":
        sel = [r for r in rows if r["pid"] == "S2" and r["cond"] == c]
        if sel:
            print(f"    {c}: 한글 비중 " + ", ".join(f"{hangul_ratio(r['text'])*100:.0f}%" for r in sel))

sk = HERE / "skillout"
if sk.exists():
    print("\n■ 스킬 오발동 — 코드 작업에서 글 작성 스킬이 뜨는가")
    counts = {"A": [0, 0], "B": [0, 0]}
    pos = None
    for f in sorted(sk.glob("*.jsonl")):
        pid, cond, _ = f.stem.split("_")
        n = len(re.findall(r'"name":"Skill"', f.read_text(encoding="utf-8", errors="ignore")))
        if pid == "POS":
            pos = n
            continue
        counts[cond][0] += n
        counts[cond][1] += 1
    for c in "AB":
        if counts[c][1]:
            print(f"    {c}: 코드 작업 {counts[c][1]}건에서 스킬 호출 {counts[c][0]}건")
    if pos is not None:
        mark = "검출기가 돈다" if pos >= 1 else "검출기가 죽었다. 위 0 건은 근거가 아니다"
        print(f"    양성 대조(진짜 글 작성 요청): 스킬 호출 {pos}건 — {mark}")

print("\n" + "=" * 78)
print("비용과 시간")
print("=" * 78)
for name, dirname in (("정확도·지시 준수 (haiku)", "out/claude-haiku-4-5-20251001"),
                      ("정확도·지시 준수 (opus)", "out/claude-opus-5"),
                      ("서브에이전트 (opus)", "subout")):
    rows = load(dirname)
    if not rows:
        continue
    print(f"  {name}")
    for c in "AB":
        sel = [r for r in rows if r["cond"] == c]
        if not sel:
            continue
        print(f"    {c}: 총입력 중앙값 {statistics.median(r['tok'] for r in sel):>7.0f}"
              f"  출력 중앙값 {statistics.median(r['out'] for r in sel):>5.0f}"
              f"  시간 중앙값 {statistics.median(r['ms'] for r in sel)/1000:>5.1f}초"
              f"  비용 합 ${sum(r['cost'] for r in sel):.2f}")
