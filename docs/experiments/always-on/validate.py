#!/usr/bin/env python3
"""출력이 실제 답변인지 검사한다. 가짜 도구 호출 흔적이나 한글 150자 미만이면 무효."""
import json, glob, os, re, sys
d = sys.argv[1] if len(sys.argv) > 1 else "out"
BAD = re.compile(r"antml:|<invoke|function_results|Skill\(|skill_tool|⎿ Skill loaded|AskUserQuestion|\"command\"\s*:\s*\"(?:korean-writing|superpowers)")
bad = []
for f in sorted(glob.glob(os.path.join(d, "*.json"))):
    t = (json.load(open(f)).get("result") or "")
    h = len(re.findall(r"[가-힣]", t))
    why = []
    if h < 150: why.append(f"hangul={h}")
    m = BAD.search(t)
    if m: why.append(f"marker={m.group(0)!r}")
    if why: bad.append((os.path.basename(f)[:-5], ", ".join(why)))
print(f"{d}: {len(glob.glob(os.path.join(d,'*.json')))} files, invalid={len(bad)}")
for n, w in bad: print("  ", n, w)
