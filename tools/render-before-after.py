#!/usr/bin/env python3
"""README 의 전후 비교 그림(docs/before-after-column.svg)을 실제 생성물에서 뽑은 문장으로 그린다.

재료는 docs/samples/before-after/ 에 있다. 블라인드 판정 스크립트(docs/experiments/skill-vs-imnotai/run.sh)가
2026-09-11 에 칼럼 프롬프트 L1 로 만든 글을 글자 하나 바꾸지 않고 옮겼다.

  prompt.txt    요청
  plain.txt     규칙 없이 쓴 칼럼(claude-opus-5)
  imnotai.txt   그 칼럼을 im-not-ai 파이프라인으로 윤문한 글
  skill.txt     korean-writing 스킬을 붙여 처음부터 쓴 칼럼
  judge.json    조건을 모르는 판정자(claude-opus-5)의 두 판정
  excerpts.json 그림에 싣는 대목. 글에서 같은 자리를 맡는 대목끼리 짝지었다

칼럼 전문은 그림에 담기에 길어서 짝지은 대목만 크게 싣는다. 짝을 짓는 기준은 자리다.
여는 대목은 여는 대목과, 마지막 문장은 마지막 문장과 붙여야 같은 것을 견줄 수 있다.

두 가지를 확인하고 어긋나면 멈춘다. 뽑은 문장이 원문에 그대로 있는가, 판정자가 짚었다고
표시한 표현이 judge.json 의 판정문에 그대로 있는가.

사용: python3 tools/render-before-after.py
"""
import json
import pathlib
import sys
import unicodedata
from xml.sax.saxutils import escape

REPO = pathlib.Path(__file__).resolve().parent.parent
SRC = REPO / "docs" / "samples" / "before-after"
OUT = REPO / "docs" / "before-after-column.svg"

W, M, GAP = 1280, 56, 40
COL = (W - 2 * M - GAP) // 2
FONT = "'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif"
C = {"bg": "#1e2229", "card": "#262b33", "text": "#e6eaf0", "dim": "#9aa4b2", "bad": "#ff8fa3", "good": "#7ee0a3",
     "chip": "#2d333d", "title": "#f2f4f7", "rule": "#39404b"}
BODY, LH, PAD, CITE = 21, 32, 20, 32
SIDES = (("left", M, "bad"), ("right", M + COL + GAP, "good"))


def em(ch):
    return 1.0 if unicodedata.east_asian_width(ch) in "WF" else 0.55


def width(s, size):
    # 대략의 글자 폭. 한글은 1em, 로마자와 빈칸은 0.55em 으로 잡는다.
    return sum(em(c) for c in s) * size


def wrap(s, px, size):
    # 폭(px)에 맞춰 빈칸에서 끊는다.
    rows, cur, w = [], "", 0.0
    for word in s.split(" "):
        ww = width(word, size)
        sp = 0.55 * size if cur else 0
        if cur and w + sp + ww > px:
            rows.append(cur)
            cur, w = word, ww
        else:
            cur, w = (cur + " " + word) if cur else word, w + sp + ww
    if cur:
        rows.append(cur)
    return rows


def t(x, y, s, size, fill, weight=400, anchor="start"):
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')


def card(x, y, h):
    return f'<rect x="{x}" y="{y:.0f}" width="{COL}" height="{h:.0f}" rx="12" fill="{C["card"]}"/>'


def lines_of(side, src, name, judge):
    for p in side["parts"]:
        if p not in src:
            sys.exit(f"「{p}」 가 {name} 에 없다. 뽑은 문장을 원문과 맞춘다")
    cite = side.get("cite")
    if cite and cite not in judge:
        sys.exit(f"「{cite}」 가 judge.json 의 판정문에 없다. 짚었다는 표시를 지우거나 표현을 맞춘다")
    text = " … ".join(side["parts"]) + (" …" if len(side["parts"]) > 1 else "")
    return wrap(text, COL - 44, BODY)


def main():
    spec = json.loads((SRC / "excerpts.json").read_text(encoding="utf-8"))
    prompt = (SRC / "prompt.txt").read_text(encoding="utf-8").strip()
    judge = (SRC / "judge.json").read_text(encoding="utf-8")
    src = {k: (SRC / spec[k]["file"]).read_text(encoding="utf-8") for k, _x, _c in SIDES}

    o, y = [], 40
    o.append(t(M, y + 28, "같은 요청, 두 결과", 28, C["title"], 700))
    o.append(t(M, y + 60, f"요청: {prompt}", 17, C["dim"]))
    y += 94
    for k, x, color in SIDES:
        o.append(card(x, y, 76))
        o.append(t(x + 22, y + 33, spec[k]["title"], 21, C["title"], 700))
        o.append(t(x + 22, y + 60, spec[k]["sub"], 15, C[color]))
    y += 76 + 30

    for row in spec["rows"]:
        rows = {k: lines_of(row[k], src[k], spec[k]["file"], judge) for k, _x, _c in SIDES}
        cited = any(row[k].get("cite") for k, _x, _c in SIDES)
        o.append(t(M, y, row["role"], 15, C["dim"], 700))
        rx = M + width(row["role"], 15) + 14
        if rx < W - M - 40:
            o.append(f'<line x1="{rx:.0f}" y1="{y - 5}" x2="{W - M}" y2="{y - 5}" stroke="{C["rule"]}"/>')
        y += 14
        h = PAD + max(len(v) for v in rows.values()) * LH + (CITE if cited else 0) + 14
        for k, x, color in SIDES:
            o.append(card(x, y, h))
            yy = y + PAD + BODY
            for ln in rows[k]:
                o.append(t(x + 22, yy, ln, BODY, C["text"]))
                yy += LH
            cite = row[k].get("cite")
            if cite:
                label = f"판정자가 짚은 곳: {cite}"
                o.append(f'<rect x="{x + 22}" y="{yy - BODY - 2:.0f}" width="{width(label, 13) + 24:.0f}" '
                         f'height="26" rx="13" fill="{C["chip"]}"/>')
                o.append(t(x + 34, yy + 1, label, 13, C[color], 700))
        y += h + 26

    y += 8
    o.append(t(M, y, "어느 글인지 알리지 않고 AI 판정자에게 두 번 물었더니(두 번째는 순서를 바꿔서) 두 번 다 오른쪽을 골랐습니다.", 17, C["text"]))
    o.append(t(M, y + 30, "글에서 같은 자리를 맡는 대목끼리 짝지었습니다. 전문은 docs/samples/before-after/ · 생성과 판정 claude-opus-5 · 2026-09-11", 15, C["dim"]))
    H = y + 64
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}">',
           f'<rect width="{W}" height="{H:.0f}" rx="16" fill="{C["bg"]}"/>'] + o + ["</svg>"]
    OUT.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(REPO)} 를 그렸다. 높이 {H:.0f}px")


if __name__ == "__main__":
    main()
