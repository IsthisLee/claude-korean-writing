#!/usr/bin/env python3
"""긴 대화 판정 집계. 순서를 바꾼 두 판정이 엇갈리면 무승부."""
import json, re, sys, os, collections
base = os.path.dirname(os.path.abspath(__file__))
# tag 별로 답변1 = 앞의 것, 답변2 = 뒤의 것
LABEL = {"lateAB": ("off_late", "on_late"), "onFade": ("on_early", "on_late")}
for tag, (n1, n2) in LABEL.items():
    c = collections.Counter(); detail = []
    for pid in ("01", "05", "09", "11"):
        picks = []
        for o in ("1", "2"):
            f = f"{base}/verdict/{tag}_{pid}_o{o}.json"
            if not os.path.exists(f): picks.append("?"); continue
            t = json.load(open(f)).get("result", "")
            m = re.search(r'"winner"\s*:\s*"(1|2|tie)"', t)
            v = m.group(1) if m else "tie"
            if v == "tie": picks.append("tie")
            else: picks.append(({"1": n1, "2": n2} if o == "1" else {"1": n2, "2": n1})[v])
        win = picks[0] if picks[0] == picks[1] else "tie"
        c[win] += 1; detail.append((pid, picks[0], picks[1], win))
    print(f"[{tag}] {n1} vs {n2}: {dict(c)}")
    for d in detail: print("   ", d)
