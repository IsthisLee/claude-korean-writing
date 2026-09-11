#!/usr/bin/env python3
"""README 의 전후 비교 그림(docs/before-after.svg)을 실제 생성물에서 뽑은 문장으로 그린다.

재료는 docs/samples/before-after/ 에 있다. 블라인드 판정 스크립트(docs/experiments/skill-vs-imnotai/run.sh)가
2026-09-11 에 칼럼 프롬프트 L1 로 만든 글을 글자 하나 바꾸지 않고 옮겼다.

  prompt.txt    요청
  plain.txt     규칙 없이 쓴 칼럼(claude-opus-5)
  imnotai.txt   그 칼럼을 im-not-ai 파이프라인으로 윤문한 글
  skill.txt     korean-writing 스킬을 붙여 처음부터 쓴 칼럼
  judge.json    조건을 모르는 판정자(claude-opus-5)의 두 판정
  excerpts.json 그림에 싣는 문장. 판정자가 짚은 곳을 뽑았다

칼럼 전문은 그림에 담기에 길어서 판정자가 짚은 문장만 크게 싣는다. 뽑은 문장이 원문에 그대로 없으면 멈춘다.

사용: python3 tools/render-before-after.py
"""
import json
import pathlib
import sys
import unicodedata
from xml.sax.saxutils import escape

REPO = pathlib.Path(__file__).resolve().parent.parent
SRC = REPO / "docs" / "samples" / "before-after"
OUT = REPO / "docs" / "before-after.svg"

W, M, GAP = 1280, 56, 32
COL = (W - 2 * M - GAP) // 2
FONT = "'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif"
C = {"bg": "#1e2229", "card": "#262b33", "text": "#e6eaf0", "dim": "#9aa4b2", "bad": "#ff8fa3", "good": "#7ee0a3",
     "chip": "#2d333d", "title": "#f2f4f7", "rule": "#39404b"}
BODY, LH = 20, 30


def em(ch):
    return 1.0 if unicodedata.east_asian_width(ch) in "WF" else 0.55


def wrap(s, px, size):
    # 폭(px)에 맞춰 빈칸에서 끊는다. 한글은 1em, 로마자와 빈칸은 0.55em 으로 잡는다.
    rows, cur, w = [], "", 0.0
    for word in s.split(" "):
        ww = sum(em(c) for c in word) * size
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
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>'


def column(x, y, side, spec, color):
    src = (SRC / spec["file"]).read_text(encoding="utf-8")
    body, yy = [], y + 116
    for it in spec["items"]:
        for p in it["parts"]:
            if p not in src:
                sys.exit(f"「{p}」 가 {spec['file']} 에 없다. 뽑은 문장을 원문과 맞춘다")
        text = " … ".join(it["parts"]) + (" …" if len(it["parts"]) > 1 else "")
        cw = sum(em(c) for c in it["tag"]) * 14 + 24
        body.append(f'<rect x="{x + 24}" y="{yy - 17}" width="{cw:.0f}" height="24" rx="12" fill="{C["chip"]}"/>')
        body.append(t(x + 36, yy, it["tag"], 14, color, 700))
        yy += 34
        for row in wrap(text, COL - 48, BODY):
            body.append(t(x + 24, yy, row, BODY, C["text"]))
            yy += LH
        yy += 18
    h = yy - y + 4
    head = [f'<rect x="{x}" y="{y}" width="{COL}" height="{h}" rx="12" fill="{C["card"]}"/>',
            t(x + 24, y + 38, spec["title"], 20, C["title"], 700),
            t(x + 24, y + 64, spec["sub"], 15, color),
            f'<line x1="{x + 24}" y1="{y + 78}" x2="{x + COL - 24}" y2="{y + 78}" stroke="{C["rule"]}"/>']
    return head + body, h


def main():
    spec = json.loads((SRC / "excerpts.json").read_text(encoding="utf-8"))
    prompt = (SRC / "prompt.txt").read_text(encoding="utf-8").strip()
    o, y = [], 40
    o.append(t(M, y + 28, "같은 요청, 두 결과", 28, C["title"], 700))
    o.append(t(M, y + 62, f"요청: {prompt}", 17, C["dim"]))
    y += 92
    left, lh = column(M, y, "left", spec["left"], C["bad"])
    right, rh = column(M + COL + GAP, y, "right", spec["right"], C["good"])
    o += left + right
    y += max(lh, rh) + 36
    o.append(t(M, y, "어느 글인지 알리지 않고 AI 판정자에게 두 번 물었더니(두 번째는 순서를 바꿔서) 두 번 다 오른쪽을 골랐습니다.", 17, C["text"]))
    o.append(t(M, y + 30, "판정자가 짚은 문장만 뽑았습니다. 전문은 docs/samples/before-after/ · 생성과 판정 claude-opus-5 · 2026-09-11", 15, C["dim"]))
    H = y + 64
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" rx="16" fill="{C["bg"]}"/>'] + o + ["</svg>"]
    OUT.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(REPO)} 를 그렸다. 높이 {H}px")


if __name__ == "__main__":
    main()
