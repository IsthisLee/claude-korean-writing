#!/usr/bin/env python3
import json, glob, re, os, collections
by = collections.defaultdict(lambda: {"n":0,"errors":0,"minor":0,"major":0,"none":0,"samples_with_err":0})
cost = 0; rows = []
for f in sorted(glob.glob("factcheck/*.json")):
    d = json.load(open(f)); cost += d.get("total_cost_usd",0)
    n = os.path.basename(f)[:-5]; pid, c, s = n.split("_")
    m = re.search(r"\{.*\}", d["result"], flags=re.S)
    try: j = json.loads(m.group(0))
    except Exception: print("UNPARSED", n); continue
    e = len(j.get("errors", [])); sev = j.get("severity","?")
    b = by[c]; b["n"] += 1; b["errors"] += e; b[sev] = b.get(sev,0)+1; b["samples_with_err"] += (1 if e else 0)
    rows.append((pid, c, s, sev, e, [x.get("quote","")[:70].replace("\n"," ") for x in j.get("errors",[])]))
for c in ("A","B"):
    b = by[c]; print(f"{c}: n={b['n']} samples_with_errors={b['samples_with_err']} total_errors={b['errors']} severity none={b['none']} minor={b['minor']} major={b['major']}")
print("factcheck cost usd:", round(cost,2))
print("\nmajor items:")
for r in rows:
    if r[3] == "major": print("  ", r)
print("\nper sample:")
for r in rows: print(f"  {r[0]}_{r[1]}_{r[2]} {r[3]:5} {r[4]}  {r[5]}")
