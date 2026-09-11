#!/usr/bin/env python3
"""스킬 적용(S)과 미적용(A)의 세부 항목 보존을 조건을 모르는 판정자로 센다 (EVALUATION.md J3).

실행: gen.sh 로 답을 만든 뒤 python3 judge.py

확정 기준(측정 전): 과제별로 표본 합계 순열검정 p<0.05 로 S 가 낮거나,
항목 하나라도 Fisher p<0.05 로 S 에서 줄면 '빠진다'. 둘 다 아니면 '증거 없음'.
"""
import concurrent.futures as cf, itertools, json, math, pathlib, random, re, statistics, subprocess, tempfile

HERE = pathlib.Path(__file__).resolve().parent
# 산출물은 커밋하지 않는 폴더(docs/experiments/*/out/, */judge/)에 둔다.
OUT, JUDGE = HERE.parent / "out" / "skill", HERE.parent / "judge" / "skill"
JUDGE.mkdir(parents=True, exist_ok=True)
ITEMS = json.load(open(HERE / "items.json"))
PROMPT = """아래 [글]이 [항목] 각각을 실제로 담고 있는지 true/false 로 판정하라. 도구는 없다. 글만 보고 판정한다.
표현이 달라도 뜻이 같으면 true, 빠졌거나 암시만 했으면 false. 수치·날짜·이름은 값이 맞아야 true 다.
글의 문체나 품질은 판정하지 않는다.

항목:
{items}

JSON 객체 하나만 출력한다. 키는 위 항목 id, 값은 true/false.

[글]
{text}
"""

def hangul(t): return len(re.findall(r"[가-힣]", t))

def judge(name, task, text):
    cache = JUDGE / f"{name}.json"
    if cache.exists(): return name, json.loads(cache.read_text())
    items = "\n".join(f"- {k}: {v}" for k, v in ITEMS[task].items())
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(["claude", "-p", PROMPT.format(items=items, text=text), "--no-session-persistence", "--tools", "",
                            "--strict-mcp-config", "--setting-sources", "", "--model", "claude-opus-5", "--output-format", "json"],
                           cwd=d, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=300)
    try: res = json.loads(r.stdout).get("result", "")
    except Exception: res = r.stdout
    m = re.search(r"\{.*\}", res, re.S)
    if not m: print(f"파싱 실패 {name}: {res[:150]!r}"); return name, None
    v = json.loads(m.group(0))
    if set(v) != set(ITEMS[task]): print(f"키 불일치 {name}"); return name, None
    cache.write_text(json.dumps(v, ensure_ascii=False)); return name, v

def perm_p_lower(a, b):
    """S(b) 합계 평균이 A(a) 보다 낮은 쪽 단측이 아니라 확정 기준대로 양측 p 를 내고, 방향은 따로 본다."""
    pool, na = a + b, len(a); obs = abs(sum(a) / len(a) - sum(b) / len(b)); tot = sum(pool)
    n = hit = 0
    for idx in itertools.combinations(range(len(pool)), na):
        sa = sum(pool[i] for i in idx); n += 1
        hit += abs(sa / na - (tot - sa) / (len(pool) - na)) >= obs - 1e-12
    return hit / n

def fisher_p(a, b, c, d):
    n, r1, c1 = a + b + c + d, a + b, a + c
    pr = lambda x: math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if pr(x) <= p0 + 1e-12)

texts = {}
for p in sorted(OUT.glob("*.json")):
    t = json.loads(p.read_text()).get("result") or ""
    if hangul(t) < 100: print(f"답이 아닌 표본: {p.name}"); continue
    texts[p.stem] = t
jobs = [(n, n.split("_")[0], t) for n, t in texts.items()]
with cf.ThreadPoolExecutor(4) as ex:
    got = {n: v for n, v in ex.map(lambda j: judge(*j), jobs) if v is not None}

# 중립 대조군(N): 스킬과 같은 길이의 무관한 문서를 붙였다. A 와 견줘 같은 항목이 빠지는지 본다.
for task in ITEMS:
    na = sorted(n for n in got if n.startswith(f"{task}_A_"))
    nn = sorted(n for n in got if n.startswith(f"{task}_N_"))
    if not na or not nn: continue
    ta = [sum(got[n].values()) for n in na]; tn = [sum(got[n].values()) for n in nn]
    print(f"\n[{task} 중립 대조군] A {sum(ta)} {ta}  N {sum(tn)} {tn}  한글 중앙값 N {statistics.median(hangul(texts[n]) for n in nn):.0f}  순열검정 p={perm_p_lower(ta, tn):.3f}")
    for it in ITEMS[task]:
        a = sum(got[n][it] for n in na); x = sum(got[n][it] for n in nn)
        print(f"    {it:20} A {a}/{len(na)}  N {x}/{len(nn)}  Fisher p={fisher_p(a, len(na) - a, x, len(nn) - x):.3f}")

verdict = {}
for task in ITEMS:
    ns = {c: sorted(n for n in got if n.startswith(f"{task}_{c}_")) for c in "AS"}
    if not ns["A"] or not ns["S"]: continue
    tot = {c: [sum(got[n].values()) for n in ns[c]] for c in "AS"}
    ln = {c: statistics.median(hangul(texts[n]) for n in ns[c]) for c in "AS"}
    k = len(ITEMS[task])
    p = perm_p_lower(tot["A"], tot["S"])
    lower = sum(tot["S"]) / len(tot["S"]) < sum(tot["A"]) / len(tot["A"])
    print(f"\n[{task}] 항목 {k}개  A {sum(tot['A'])}/{k*len(ns['A'])} {tot['A']}  S {sum(tot['S'])}/{k*len(ns['S'])} {tot['S']}")
    print(f"    한글 중앙값 A {ln['A']:.0f}  S {ln['S']:.0f}   합계 순열검정 p={p:.3f} (S 가 {'낮음' if lower else '같거나 높음'})")
    drops = []
    for it in ITEMS[task]:
        a = sum(got[n][it] for n in ns["A"]); s = sum(got[n][it] for n in ns["S"])
        fp = fisher_p(a, len(ns["A"]) - a, s, len(ns["S"]) - s)
        mark = "  <- S 에서 줄어듦(p<0.05)" if s < a and fp < 0.05 else ""
        if mark: drops.append(it)
        print(f"    {it:20} A {a}/{len(ns['A'])}  S {s}/{len(ns['S'])}  Fisher p={fp:.3f}{mark}")
    verdict[task] = "빠진다" if (lower and p < 0.05) or drops else "증거 없음"
    print(f"    판정: {verdict[task]}" + (f" (항목: {', '.join(drops)})" if drops else ""))
print("\n종합:", verdict)
