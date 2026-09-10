#!/usr/bin/env python3
"""정규식 채점. 훅 검사기(posttooluse.sh)를 그대로 돌린 결과와, 임계 없는 원시 패턴 횟수를 같이 낸다."""
import json, re, subprocess, sys, glob, os, csv
HOOK = "/Users/isthis/Documents/personal/claude-plugins/korean-writing/hooks-handlers/posttooluse.sh"
THING = r"(?:화면|서버|장비|시스템|페이지|프로세스|코드|스크립트|훅|모듈|테스트|빌드)"
def strip(raw):
    b = re.sub(r"```.*?```", "", raw, flags=re.S)
    b = re.sub(r"`[^`\n]+`", "", b)
    b = re.sub(r"https?://\S+", "", b)
    b = re.sub(r"^\s*\|.*$", "", b, flags=re.M)
    return b
def raw_counts(text):
    b = strip(text)
    return {
        "dash": len(re.findall(r"[^|\s]\s[—–]\s[^|\s]", b)),
        "struct": len(re.findall(r"(?<![가-힣])축(?:이|은|을|으로)|갈래|결(?:이|은)\s*다르|레이어", b)),
        "geot": len(re.findall(r"것들이[었다]|것들을|하는 것이 가능", b)),
        "idiom": len(re.findall(r"결론적으로|종합하면|요약하자면|중요한 점은|시사하는 바가 크|주목할 만하|혁신적|획기적|압도적|라고 할 수 있(?:습니다|다)", b)),
        "ordinal": 1 if (re.search(r"첫째[,.]", b) and re.search(r"둘째[,.]", b)) else 0,
        "winlose": len(re.findall(r"(?:가|이)\s*이(?:긴다|깁니다|겼다|겼습니다|기고|기는|길\s)", b)),
        "person": len(re.findall(THING + r"(?:이|가)\s*(?:굳|쓰러지|쓰러졌|넘어지|일어서|잠들)", b)) + len(re.findall(r"(?:넘어뜨리|일으켜\s*세우|쓰러뜨리)", b)),
        "trans": len(re.findall(r"가지고\s*있", b)) + len(re.findall(r"되어지|지게\s*된다|되어진다", b)) + len(re.findall(r"에\s*의해", b)),
        # 보조 지표 (훅에 없음): 문두 접속사, ~에 대해/~를 통해, ~할 수 있, 이모지, 굵게, 불릿 줄 수
        "conj": len(re.findall(r"(?m)^(?:또한|따라서|즉|나아가|아울러|게다가|더욱이)[,\s]", b)),
        "edaehae": len(re.findall(r"에\s*대해|를\s*통해|을\s*통해", b)),
        "halsu": len(re.findall(r"[ㄹ을할될]\s*수\s*있", b)),
        "emoji": len(re.findall(r"[\U0001F300-\U0001FAFF☀-➿]", text)),
        "bold": len(re.findall(r"\*\*[^*]+\*\*", text)),
        "bullets": len(re.findall(r"(?m)^\s*[-*]\s", text)),
        "hangul": len(re.findall(r"[가-힣]", text)),
    }
def hook_hits(text):
    payload = json.dumps({"tool_name":"Write","tool_input":{"file_path":"/tmp/x.md","content":text}}, ensure_ascii=False)
    p = subprocess.run([HOOK], input=payload, capture_output=True, text=True)
    return re.findall(r"^\s+(K\d)\s", p.stdout + p.stderr, flags=re.M)
rows = []
for f in sorted(glob.glob(os.path.join(os.path.dirname(__file__) or ".", "out", "*.json"))):
    d = json.load(open(f))
    text = d.get("result") or ""
    name = os.path.basename(f)[:-5]
    pid, cond, s = name.split("_")
    rc = raw_counts(text)
    hk = hook_hits(text)
    u = d.get("usage", {})
    rows.append({"id":pid,"cond":cond,"s":s,"hook":"|".join(hk),"hook_n":len(hk),
                 "raw_sum": sum(rc[k] for k in ("dash","struct","geot","idiom","ordinal","winlose","person","trans")),
                 **rc, "out_tokens": u.get("output_tokens"), "cost": round(d.get("total_cost_usd",0),4)})
w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
w.writeheader(); w.writerows(rows)
