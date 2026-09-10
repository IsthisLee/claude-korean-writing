#!/usr/bin/env python3
"""판정 결과 집계. judge/{id}_{s}_o{1,2}.json 을 읽어 쌍별 승자를 낸다.
o1: 답변1=A, 답변2=B. o2: 답변1=B, 답변2=A. 두 순서의 판정이 엇갈리면 무승부."""
import json, glob, os, re, sys, collections
base = os.path.dirname(__file__) or "."
def parse(f):
    d = json.load(open(f))
    txt = d.get("result") or ""
    m = re.search(r"\{.*\}", txt, flags=re.S)
    if not m: return None, d
    try: return json.loads(m.group(0)), d
    except Exception: return None, d
def to_AB(j, order):
    # 판정 JSON 의 1/2 를 A/B 로 되돌린다
    if order == "1": mp = {"1":"A","2":"B"}
    else: mp = {"1":"B","2":"A"}
    w = j.get("winner","tie")
    win = mp.get(str(w), "tie")
    flags = {}
    for k in ("fact_problem","register_drop","code_damage"):
        for n in ("1","2"):
            flags[(k, mp[n])] = bool(j.get(f"{k}_{n}", False))
    issues = {mp["1"]: j.get("issues_1", []), mp["2"]: j.get("issues_2", [])}
    return win, flags, issues, j.get("why","")
pairs = collections.defaultdict(dict)
cost = 0.0; unparsed = []
for f in sorted(glob.glob(os.path.join(base, "judge", "*.json"))):
    name = os.path.basename(f)[:-5]
    pid, s, o = name.split("_"); o = o[1:]
    j, d = parse(f)
    cost += d.get("total_cost_usd", 0)
    if j is None: unparsed.append(name); continue
    pairs[(pid, s)][o] = to_AB(j, o)
final = []
flagsB = collections.Counter(); flagsA = collections.Counter()
per_prompt = collections.defaultdict(lambda: collections.Counter())
for (pid, s), d in sorted(pairs.items()):
    if "1" not in d or "2" not in d: continue
    w1, f1, i1, why1 = d["1"]; w2, f2, i2, why2 = d["2"]
    win = w1 if w1 == w2 else "tie"
    consistent = (w1 == w2)
    for (k, side), v in list(f1.items()) + list(f2.items()):
        if v: (flagsB if side == "B" else flagsA)[k] += 1
    per_prompt[pid][win] += 1
    final.append((pid, s, w1, w2, win, consistent, i1.get("A"), i1.get("B"), why1))
print("pairs judged:", len(final), " unparsed:", unparsed)
c = collections.Counter(x[4] for x in final)
print("final winners:", dict(c))
dec = c["A"] + c["B"]
print(f"B win rate excl. ties: {c['B']}/{dec} = {c['B']/dec*100:.0f}%" if dec else "no decisive pairs")
print("order-consistent pairs:", sum(1 for x in final if x[5]), "/", len(final))
print("prompts where A>B:", [p for p, v in per_prompt.items() if v["A"] > v["B"]])
print("per prompt:", {p: dict(v) for p, v in sorted(per_prompt.items())})
print("flags on B (out of", len(final)*2, "judgments):", dict(flagsB))
print("flags on A:", dict(flagsA))
print("judge cost usd:", round(cost, 2))
print()
for pid, s, w1, w2, win, cons, iA, iB, why in final:
    print(f"[{pid}-{s}] o1={w1} o2={w2} => {win}")
    print(f"   A issues: {iA}")
    print(f"   B issues: {iB}")
    print(f"   why(o1): {why}")
