#!/usr/bin/env python3
"""README 의 전후 비교 그림(docs/before-after.svg)을 실제 생성물로 그린다.

재료는 docs/samples/before-after/ 에 있다. 블라인드 판정 스크립트(docs/experiments/skill-vs-imnotai/run.sh)가
2026-09-11 에 프롬프트 01 로 만든 글을 글자 하나 바꾸지 않고 옮겼다.

  plain.txt    규칙 없이 쓴 글(claude-opus-5)
  imnotai.txt  그 글을 im-not-ai 파이프라인으로 윤문한 글. 변경률 0.0% 로 plain.txt 와 같다
  skill.txt    korean-writing 스킬을 붙여 처음부터 쓴 글
  judge.json   조건을 모르는 판정자(claude-opus-5)의 두 판정

빨간 글씨는 판정자가 짚은 곳(굵은 글씨, 번호 목록, 형식명사 끝맺음)과 스킬의 「요청한 글만 낸다」 규칙이
막는 본문 뒤 안내다. 그림에 표시하는 곳을 바꾸려면 FLAGS 를 고친다.

사용: python3 tools/render-before-after.py
"""
import json
import pathlib
import re
import unicodedata
from xml.sax.saxutils import escape

REPO = pathlib.Path(__file__).resolve().parent.parent
SRC = REPO / "docs" / "samples" / "before-after"
OUT = REPO / "docs" / "before-after.svg"

W, PAD, GAP = 1200, 28, 24
COL = (W - PAD * 2 - GAP) // 2
LIMIT = 70          # 한 줄 폭. 한글은 두 칸으로 센다
LH = 21             # 줄 간격
FONT = "'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif"
C = {"bg": "#1e2229", "card": "#262b33", "text": "#d7dde5", "dim": "#9aa4b2", "flag": "#ff8fa3",
     "good": "#7ee0a3", "title": "#f2f4f7", "rule": "#39404b"}
FLAGS = [r"\*\*[^*\n]+\*\*", r"(?m)^\d+\. ", r"챙기려는 것입니다"]


def cols(ch):
    return 2 if unicodedata.east_asian_width(ch) in "WF" else 1


def marks(text, tail_from=None):
    # 글자마다 빨간 글씨인지 적는다. tail_from 뒤(본문 뒤 안내)는 통째로 표시한다.
    m = [False] * len(text)
    for pat in FLAGS:
        for x in re.finditer(pat, text):
            for i in range(x.start(), x.end()):
                m[i] = True
    if tail_from is not None:
        for i in range(tail_from, len(text)):
            m[i] = True
    return m


def wrap(text, flags, limit=LIMIT):
    # (글자, 표시) 줄 목록. 빈칸에서 끊을 수 있으면 빈칸에서 끊는다.
    rows = []
    for line, fl in zip(*_split(text, flags)):
        if not line:
            rows.append([])
            continue
        cur, w = [], 0
        for ch, f in zip(line, fl):
            if w + cols(ch) > limit:
                sp = max((i for i, (c, _) in enumerate(cur) if c == " "), default=-1)
                if sp > 0:
                    rows.append(cur[:sp])
                    cur = cur[sp + 1:]
                else:
                    rows.append(cur)
                    cur = []
                w = sum(cols(c) for c, _ in cur)
            cur.append((ch, f))
            w += cols(ch)
        rows.append(cur)
    return rows


def _split(text, flags):
    lines, fls, start = [], [], 0
    for line in text.split("\n"):
        lines.append(line)
        fls.append(flags[start:start + len(line)])
        start += len(line) + 1
    return lines, fls


def tspans(row, base):
    out, run, cur = [], "", None
    for ch, f in row + [(None, None)]:
        if f != cur and run:
            out.append(f'<tspan fill="{C["flag"] if cur else base}">{escape(run)}</tspan>')
            run = ""
        if ch is None:
            break
        cur = f
        run += ch
    return "".join(out)


def column(x, y, head, sub, sub_color, text, flags):
    rows = wrap(text, flags)
    h = 76 + LH * len(rows) + 18
    s = [f'<rect x="{x}" y="{y}" width="{COL}" height="{h}" rx="10" fill="{C["card"]}"/>',
         f'<text x="{x + 20}" y="{y + 32}" fill="{C["title"]}" font-size="17" font-weight="700">{escape(head)}</text>',
         f'<text x="{x + 20}" y="{y + 56}" fill="{sub_color}" font-size="13">{escape(sub)}</text>',
         f'<line x1="{x + 20}" y1="{y + 68}" x2="{x + COL - 20}" y2="{y + 68}" stroke="{C["rule"]}"/>']
    for i, row in enumerate(rows):
        if row:
            s.append(f'<text x="{x + 20}" y="{y + 92 + LH * i}" font-size="13.5" xml:space="preserve">{tspans(row, C["text"])}</text>')
    return s, h


def main():
    prompt = (SRC / "prompt.txt").read_text(encoding="utf-8").strip()
    plain = (SRC / "plain.txt").read_text(encoding="utf-8").strip()
    imnotai = (SRC / "imnotai.txt").read_text(encoding="utf-8").strip()
    skill = (SRC / "skill.txt").read_text(encoding="utf-8").strip()
    judge = json.loads((SRC / "judge.json").read_text(encoding="utf-8"))
    same = plain == imnotai
    tail = plain.find("\n---")
    body = []
    y = PAD
    body.append(f'<text x="{PAD}" y="{y + 26}" fill="{C["title"]}" font-size="22" font-weight="700">같은 요청, 두 결과</text>')
    body.append(f'<text x="{PAD}" y="{y + 54}" fill="{C["dim"]}" font-size="14">요청: {escape(prompt)}</text>')
    y += 76
    left, lh = column(PAD, y, "플러그인 없이 쓰고 다 쓴 뒤 윤문",
                      "im-not-ai 윤문 변경률 0.0% · 윤문 전과 한 글자도 같다" if same else "im-not-ai 로 윤문한 글",
                      C["flag"], imnotai, marks(imnotai, tail if tail >= 0 else None))
    right, rh = column(PAD + COL + GAP, y, "korean-writing 스킬로 처음부터", "블라인드 판정에서 두 순서 모두 이긴 쪽",
                       C["good"], skill, [False] * len(skill))
    body += left + right
    y += max(lh, rh) + 22
    why = judge["order1"]["why"]
    notes = [
        ("빨간 글씨", "판정자가 짚은 굵은 글씨·번호 목록·형식명사 끝맺음, 그리고 스킬의 「요청한 글만 낸다」 규칙이 막는 본문 뒤 안내"),
        ("판정자", why),
        ("출처", "docs/samples/before-after/ · 생성과 판정 claude-opus-5 · 2026-09-11 · 순서를 바꿔 두 번 물었다"),
    ]
    for label, t in notes:
        rows = wrap(t, [False] * len(t), limit=140)
        body.append(f'<text x="{PAD}" y="{y + 16}" fill="{C["dim"]}" font-size="13" font-weight="700">{escape(label)}</text>')
        for i, row in enumerate(rows):
            body.append(f'<text x="{PAD + 84}" y="{y + 16 + LH * i}" fill="{C["dim"]}" font-size="13" xml:space="preserve">{escape("".join(c for c, _ in row))}</text>')
        y += LH * max(1, len(rows)) + 8
    H = y + PAD
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
           f'<rect width="{W}" height="{H}" rx="12" fill="{C["bg"]}"/>'] + body + ["</svg>"]
    OUT.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(REPO)} 를 그렸다. 높이 {H}px, 윤문본이 원문과 같은가 {same}")


if __name__ == "__main__":
    main()
