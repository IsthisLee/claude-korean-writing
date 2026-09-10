#!/usr/bin/env python3
"""종결어미 분포. 코드블록·표·인라인코드를 뺀 산문에서 문장 끝을 분류한다.
hap: ~습니다/~ㅂ니다/~입니다/~니까 (합쇼체)  yo: ~요 (해요체)  da: ~다 (해라체/평서)  other"""
import json, glob, os, re, collections, sys
d = sys.argv[1] if len(sys.argv) > 1 else "out"
def prose(t):
    t = re.sub(r"```.*?```", "", t, flags=re.S); t = re.sub(r"`[^`\n]+`", "", t)
    t = re.sub(r"^\s*\|.*$", "", t, flags=re.M); t = re.sub(r"^#+ .*$", "", t, flags=re.M)
    return t
def classify(t):
    c = collections.Counter()
    for s in re.split(r"(?<=[.!?])\s+|\n+", prose(t)):
        s = s.strip().rstrip(".!?)*」”\"' ")
        if len(re.findall(r"[가-힣]", s)) < 4: continue
        if re.search(r"(습니다|ㅂ니다|입니다|니까|십시오|시죠)$", s): c["hap"] += 1
        elif re.search(r"요$", s): c["yo"] += 1
        elif re.search(r"다$", s): c["da"] += 1
        else: c["other"] += 1
    return c
rows = []
for f in sorted(glob.glob(os.path.join(d, "*.json"))):
    n = os.path.basename(f)[:-5]; pid, cond, s = n.split("_")
    c = classify(json.load(open(f)).get("result") or "")
    tot = c["hap"] + c["yo"] + c["da"]
    dom = max(("hap","yo","da"), key=lambda k: c[k]) if tot else "-"
    mixed = tot and (c["hap"] + c["yo"]) > 0 and c["da"] > 0 and min(c["hap"] + c["yo"], c["da"]) / tot >= 0.2
    rows.append((pid, cond, s, c["hap"], c["yo"], c["da"], dom, "MIXED" if mixed else ""))
print(f"{'id':3}{'c':2}{'s':2}{'hap':>5}{'yo':>5}{'da':>5}  dom  mixed")
for r in rows: print(f"{r[0]:3}{r[1]:2}{r[2]:2}{r[3]:5d}{r[4]:5d}{r[5]:5d}  {r[6]:4} {r[7]}")
for cond in ("A","B"):
    sub = [r for r in rows if r[1] == cond]
    dom = collections.Counter(r[6] for r in sub); mixed = sum(1 for r in sub if r[7])
    print(f"{cond}: dominant {dict(dom)}  mixed(>=20% minority)={mixed}/{len(sub)}")
# 같은 프롬프트·표본 쌍에서 A 는 존댓말(hap/yo) 인데 B 는 해라체(da) 로 바뀐 수
A = {(r[0], r[2]): r for r in rows if r[1] == "A"}; B = {(r[0], r[2]): r for r in rows if r[1] == "B"}
down = [(k) for k in A if k in B and A[k][6] in ("hap","yo") and B[k][6] == "da"]
up = [(k) for k in A if k in B and A[k][6] == "da" and B[k][6] in ("hap","yo")]
print("pairs A polite -> B plain(da):", len(down), down)
print("pairs A plain(da) -> B polite:", len(up), up)
