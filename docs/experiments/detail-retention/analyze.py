#!/usr/bin/env python3
"""첫 Write(교정 전)와 최종 doc.md(교정 후)를 견준다. 훅이 걸려 고친 표본만 판정자에게 보낸다.

stream-json 에는 훅 알림이 남지 않는다. 걸렸는지는 첫 Write 의 내용에 훅을 다시 돌려 본다.
판정 캐시는 실행 폴더마다 따로 둔다. 이름만으로 두었더니 같은 이름의 다른 모델 표본이 앞 판정을 받아 왔다.

usage: analyze.py <실행 폴더> [--no-judge]    실행 폴더는 이 파일 기준 경로(예: out/run-20260911-170000)
종료  : 사라진 정보가 하나라도 있으면 1
"""
import concurrent.futures as cf
import json
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
HOOK = REPO / "plugin/hooks-handlers/posttooluse.sh"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
if not ARGS:
    sys.exit(__doc__)
RUNS = ARGS[0]


def hangul(t):
    return len(re.findall(r"[가-힣]", t))


def first_write(stream):
    """첫 Write 의 내용과 그 뒤 편집 횟수."""
    v0, edits = None, 0
    for line in stream.read_text(encoding="utf-8").splitlines():
        try:
            ev = json.loads(line)
        except Exception:
            continue
        msg = ev.get("message")
        if not isinstance(msg, dict) or not isinstance(msg.get("content"), list):
            continue
        for b in msg["content"]:
            if not isinstance(b, dict) or b.get("type") != "tool_use":
                continue
            if b.get("name") not in ("Write", "Edit", "MultiEdit"):
                continue
            inp = b.get("input") or {}
            if not str(inp.get("file_path", "")).endswith("doc.md"):
                continue
            if v0 is None and b["name"] == "Write":
                v0 = inp.get("content", "")
            else:
                edits += 1
    return v0, edits


def flags(text):
    """첫 Write 에 저장소의 훅을 다시 돌려 걸린 코드를 얻는다. 걸리는지는 안내 문구와 관계없다."""
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "doc.md"
        p.write_text(text, encoding="utf-8")
        payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(p), "content": text}})
        r = subprocess.run([str(HOOK)], input=payload, capture_output=True, text=True,
                           env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"})
    return re.findall(r"^\s+(K\d+)\s+(.*?) —", r.stderr, re.M)


PROMPT = """아래 [원본]과 [수정본]은 같은 글이다. 수정본은 문체만 고치라는 지적을 받고 고친 판이다. 도구는 없다. 두 글만 보고 답하라.
원본에 담긴 정보 가운데 수정본에서 사라진 것을 모두 찾아라. 정보란 사실·수치·날짜·대상·조건·예외·이유·예시·절차 단계·주의사항·대비(무엇이 아닌지)다.
표현이나 어순만 바뀌고 뜻이 남아 있으면 사라진 것이 아니다. 뜻은 남았지만 강조나 뉘앙스가 약해진 것은 weakened 에 따로 적는다. 원본에 없던 정보가 생겼으면 added 에 적는다.
JSON 객체 하나만 출력한다:
{{"missing":[{{"원본":"원본의 해당 구절 그대로","무엇":"사라진 정보 한 줄"}}],"weakened":[{{"원본":"...","무엇":"..."}}],"added":["..."]}}

[원본]
{a}

[수정본]
{b}
"""


def judge(name, a, b):
    cache = HERE / "judge" / RUNS / f"{name}.json"
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        return json.loads(cache.read_text())
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(["claude", "-p", PROMPT.format(a=a, b=b), "--no-session-persistence", "--tools", "",
                            "--strict-mcp-config", "--setting-sources", "", "--model", "claude-opus-5",
                            "--output-format", "json"],
                           cwd=d, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=600)
    try:
        res = json.loads(r.stdout).get("result", "")
    except Exception:
        res = r.stdout
    m = re.search(r"\{.*\}", res, re.S)
    if not m:
        # 계정 사용량이 떨어지면 판정 자리에 안내 문구가 들어온다. 0 건으로 세지 않고 이름을 찍는다.
        print(f"파싱 실패 {name}: {res[:200]!r}")
        return None
    v = json.loads(m.group(0))
    cache.write_text(json.dumps(v, ensure_ascii=False, indent=1))
    return v


rows = []
for o in sorted((HERE / RUNS).iterdir()):
    st = o / "stream.jsonl"
    if not st.exists():
        continue
    v0, edits = first_write(st)
    fin = (o / "final.md").read_text(encoding="utf-8") if (o / "final.md").exists() else None
    if v0 is None or fin is None:
        print(f"{o.name}: 첫 Write 또는 최종 파일 없음")
        continue
    (o / "v0.md").write_text(v0, encoding="utf-8")
    rows.append(dict(name=o.name, v0=v0, fin=fin, edits=edits, flags=flags(v0)))

todo = [r for r in rows if r["flags"] and r["v0"] != r["fin"]]
if "--no-judge" not in sys.argv:
    with cf.ThreadPoolExecutor(4) as ex:
        for r, v in zip(todo, ex.map(lambda r: judge(r["name"], r["v0"], r["fin"]), todo)):
            r["judge"] = v

for r in rows:
    j = r.get("judge") or {}
    ks = ",".join(k for k, _ in r["flags"]) or "-"
    line = f"{r['name']:28} 훅 {ks:16} 교정편집 {r['edits']}  한글 {hangul(r['v0'])}→{hangul(r['fin'])}"
    if j:
        line += f"  사라짐 {len(j.get('missing', []))} 약해짐 {len(j.get('weakened', []))} 생김 {len(j.get('added', []))}"
    print(line)
    for m in j.get("missing", []):
        print(f"        - 사라짐: {m.get('무엇')}  ⟵ 「{m.get('원본')}」")
    for m in j.get("weakened", []):
        print(f"        · 약해짐: {m.get('무엇')}  ⟵ 「{m.get('원본')}」")

lost = sum(len((r.get("judge") or {}).get("missing", [])) for r in todo)
unjudged = [r["name"] for r in todo if r.get("judge") is None]
print(f"\n표본 {len(rows)}  훅 걸림 {sum(1 for r in rows if r['flags'])}  교정된 것 {len(todo)}  사라진 정보 합계 {lost}")
if unjudged and "--no-judge" not in sys.argv:
    print("판정 못 한 표본: " + ", ".join(unjudged))
sys.exit(1 if lost or (unjudged and "--no-judge" not in sys.argv) else 0)
