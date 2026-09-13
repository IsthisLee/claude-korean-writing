#!/usr/bin/env python3
"""AI 판정 여러 벌과 사람 블라인드 평가를 모아 결과를 낸다.

사용: python3 analyze.py <run.sh 출력 폴더> [사람 평가 폴더]
      run 폴더 안의 judge-<기준서>-<판정 모델>/ 을 모두 읽는다.
      사람 평가 폴더는 평가 페이지의 db 를 파일로 받은 것이다(ratings/<문서>.json, 문서마다 rater·pair·choice).
      글 A·B 가 어느 쪽인지는 이 파일 옆 mapping.json 으로 되돌린다.

판정 한 쌍은 순서를 바꿔 두 번 물어 두 번 같은 답일 때만 승패로 센다. 다르면 「갈림」 이다.
부호 검정은 승패만 놓고 양측으로 계산한다. 비김과 갈림은 뺀다.
"""
import collections
import json
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent


def verdicts(jdir):
    out = {}
    for f in sorted(jdir.glob("*_o1.json")):
        i = f.name[:-len("_o1.json")]
        got = {}
        for o in ("1", "2"):
            p = jdir / f"{i}_o{o}.json"
            m = re.search(r"\{.*\}", p.read_text(encoding="utf-8") if p.exists() else "", re.S)
            try:
                w = json.loads(m.group(0)).get("winner") if m else None
            except Exception:
                w = None
            if w not in ("1", "2", "tie"):
                continue
            # 순서1: 글 1 = 스킬, 순서2: 글 1 = im-not-ai
            got[o] = "tie" if w == "tie" else (("skill" if w == "1" else "imnotai") if o == "1" else ("imnotai" if w == "1" else "skill"))
        out[i] = "fail" if len(got) < 2 else (got["1"] if got["1"] == got["2"] else "split")
    return out


def sign_p(w, l):
    n = w + l
    if n == 0:
        return 1.0
    k = min(w, l)
    return min(1.0, 2 * sum(math.comb(n, x) for x in range(k + 1)) / 2 ** n)


def summary(name, v):
    c = collections.Counter(v.values())
    print(f"{name:<42} 스킬 {c['skill']:>2} · im-not-ai {c['imnotai']:>2} · 비김 {c['tie']:>2} · 갈림 {c['split']:>2}"
          f" · 실패 {c['fail']:>2} · 부호 검정 p={sign_p(c['skill'], c['imnotai']):.3f}")


def agree(a, b):
    both = [i for i in a if i in b and a[i] in ("skill", "imnotai", "tie") and b[i] in ("skill", "imnotai", "tie")]
    same = sum(a[i] == b[i] for i in both)
    return same, len(both)


def humans(folder):
    mapping = json.loads((HERE / "mapping.json").read_text(encoding="utf-8"))["pairs"]
    by_rater = collections.defaultdict(dict)
    for f in pathlib.Path(folder).rglob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        d = d.get("data", d)
        pair, choice, rater = d.get("pair"), d.get("choice"), d.get("rater")
        if pair not in mapping or choice not in ("A", "B", "tie") or not rater:
            continue
        by_rater[rater][pair] = "tie" if choice == "tie" else mapping[pair][choice]
    return by_rater


def main():
    run = pathlib.Path(sys.argv[1])
    judges = {d.name[len("judge-"):]: verdicts(d) for d in sorted(run.glob("judge-*")) if d.is_dir()}
    print("== AI 판정")
    for name, v in judges.items():
        summary(name, v)
    names = list(judges)
    if len(names) > 1:
        print("\n== AI 판정끼리 같은 답을 낸 쌍 (둘 다 확정한 쌍 가운데)")
        for x in range(len(names)):
            for y in range(x + 1, len(names)):
                s, n = agree(judges[names[x]], judges[names[y]])
                print(f"{names[x]} ↔ {names[y]}: {s}/{n}")
    if len(sys.argv) > 2:
        raters = humans(sys.argv[2])
        print(f"\n== 사람 평가 (평가자 {len(raters)}명)")
        for r, v in raters.items():
            summary(f"평가자 {r} ({len(v)}쌍)", v)
        votes = collections.defaultdict(collections.Counter)
        for v in raters.values():
            for i, c in v.items():
                votes[i][c] += 1
        majority = {}
        for i, cnt in votes.items():
            top = cnt.most_common()
            majority[i] = top[0][0] if len(top) == 1 or top[0][1] > top[1][1] else "split"
        summary("사람 다수 의견", majority)
        print("\n== 사람 다수 의견과 AI 판정의 일치 (둘 다 확정한 쌍 가운데)")
        for name, v in judges.items():
            s, n = agree(majority, v)
            print(f"{name}: {s}/{n}")


if __name__ == "__main__":
    main()
