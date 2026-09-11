#!/usr/bin/env python3
"""코드 과제를 채점한다. 모델이 쓴 함수를 실제로 돌려 숨은 테스트에 넣는다.

읽고 판단하는 것이 아니라 실행한다. 경계 조건을 챙겼는지가 여기서 갈린다.
모델이 쓴 코드를 이 프로세스 안에서 exec 하므로 실험 결과에만 쓴다.

실행: ./grade_code.py
"""
import json
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import code_tests  # noqa: E402

# 기본은 실제로 쓰는 모델이다. 인자로 다른 모델을 주면 그쪽 결과를 채점한다.
# 큰 모델은 대개 만점이라 저하가 있어도 안 보인다. 여유가 있는 모델을 같이 봐야 한다.
MODEL = sys.argv[1] if len(sys.argv) > 1 else "claude-opus-5"
OUT = HERE / "out" / MODEL
FENCE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.S)


def extract(text):
    blocks = FENCE.findall(text)
    if not blocks:
        return None
    # 가장 긴 블록을 쓴다. 설명용 짧은 조각이 앞에 붙는 경우가 있다.
    return max(blocks, key=len)


def load_func(code, name):
    ns = {}
    exec(compile(code, "<model>", "exec"), ns)  # noqa: S102 - 실험용
    fn = ns.get(name)
    return fn if callable(fn) else None


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def diff_ci(k1, n1, k2, n2):
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    p1, p2 = k1 / n1, k2 / n2
    lo = (p2 - p1) - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = (p2 - p1) + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return lo, hi


print("=" * 78)
print(f"코드 품질 — {MODEL}. 모델이 쓴 함수를 실제로 돌려 숨은 테스트에 넣는다")
print("A 주입 없음 / B 주입 있음. 경계 조건을 챙겼는지가 갈리는 지점이다")
print("=" * 78)

tot = {"A": [0, 0], "B": [0, 0]}      # 통과한 테스트 수
full = {"A": [0, 0], "B": [0, 0]}     # 만점을 받은 표본 수
missed = {"A": {}, "B": {}}

print(f"\n  {'과제':<26} {'A 주입없음':<20} {'B 주입있음':<20}")
print("  " + "-" * 70)
for task, fname in sorted(code_tests.TASK_FUNC.items()):
    cells = []
    for c in "AB":
        marks, per = [], []
        for f in sorted(OUT.glob(f"{task}_{c}_*.json")):
            text = (json.loads(f.read_text(encoding="utf-8")).get("result") or "")
            code = extract(text)
            if not code:
                marks.append("-")
                per.append((0, len(code_tests.CASES[fname])))
                continue
            try:
                fn = load_func(code, fname)
            except Exception:
                fn = None
            if fn is None:
                marks.append("-")
                per.append((0, len(code_tests.CASES[fname])))
                continue
            ok, total, failed = code_tests.run(fname, fn)
            per.append((ok, total))
            marks.append("o" if ok == total else str(total - ok))
            for name in failed:
                missed[c][f"{task} {name}"] = missed[c].get(f"{task} {name}", 0) + 1
        tot[c][0] += sum(o for o, _ in per)
        tot[c][1] += sum(t for _, t in per)
        full[c][0] += sum(1 for o, t in per if o == t and t)
        full[c][1] += len(per)
        cells.append(f"{sum(o for o,_ in per)}/{sum(t for _,t in per)} [{''.join(marks)}]")
    print(f"  {task} {fname:<21} {cells[0]:<20} {cells[1]:<20}")

print("  " + "-" * 70)
print("  괄호 안은 표본별 결과다. o 는 만점, 숫자는 틀린 테스트 수, - 는 코드를 못 뽑았다는 뜻이다.\n")

for label, d in (("테스트 단위", tot), ("표본 단위 만점", full)):
    a, b = d["A"], d["B"]
    lo, hi = diff_ci(a[0], a[1], b[0], b[1])
    print(f"  {label}:  A {a[0]}/{a[1]} ({a[0]/a[1]*100:.0f}%)   "
          f"B {b[0]}/{b[1]} ({b[0]/b[1]*100:.0f}%)   "
          f"차이 95% CI [{lo*100:+.1f}, {hi*100:+.1f}]%p")

print("\n  놓친 경계 조건 (조건별 횟수)")
keys = sorted(set(missed["A"]) | set(missed["B"]))
if not keys:
    print("    없음")
for k in keys:
    print(f"    {k:<44} A {missed['A'].get(k,0)}  B {missed['B'].get(k,0)}")
