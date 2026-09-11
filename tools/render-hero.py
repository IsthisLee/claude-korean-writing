#!/usr/bin/env python3
"""README 맨 위 그림(docs/hero*.svg)을 그린다. 한국어·영어 두 판을 어두운 테마와 밝은 테마로 하나씩 만든다.

왼쪽 문장은 정답 데이터(tests/ground-truth.json)에서 한 문장씩 그대로 뽑았다. Claude Code 가 실제로 썼던 문장이다.
오른쪽은 규칙대로 고친 문장이다. 앞의 셋은 README 「문장, 전과 후」 표, K3 은 검사 훅 안내의 예시와 같고
K8 은 규칙집 처방(가지고 있다 → 있다·없다)대로 고쳤다. 왼쪽 문장이 정답 데이터에 없으면 멈춘다.

사용: python3 tools/render-hero.py
"""
import json
import pathlib
import sys
import unicodedata
from xml.sax.saxutils import escape

REPO = pathlib.Path(__file__).resolve().parent.parent
GT = {it["id"]: it["text"] for it in json.loads((REPO / "tests" / "ground-truth.json").read_text(encoding="utf-8"))}

# (정답 데이터 id, 규칙 코드, 한국어 이름, 영어 이름, 고치기 전, 고친 뒤)
ROWS = [
    ("G06", "K6", "승패 의인화", "win/lose metaphor", "규칙이 충돌하면 상위 문서가 이깁니다", "규칙이 충돌하면 상위 문서를 따릅니다"),
    ("G02", "K7", "사물 의인화", "objects acting", "시험용 장비가 몇 초 만에 쓰러졌습니다", "시험용 장비가 몇 초 만에 멈췄습니다"),
    ("G05", "K2", "추상 구조어", "structure metaphors", "두 문제는 결이 다르고 레이어도 다릅니다", "두 문제는 성격이 다른 별개의 문제입니다"),
    ("G04", "K3", "것 구문", "'geot' clauses", "바로 탈이 날 것들이었습니다", "바로 탈이 날 문제였습니다"),
    ("G10", "K8", "번역투", "translationese", "로그를 가지고 있지 않아", "로그가 없어"),
]
TEXT = {
    "ko": {"tag1": "Claude Code 플러그인", "tag2": "번역투와 AI 티 없는 한국어로 쓰게 합니다",
           "left": "Claude Code가 실제로 쓴 문장", "right": "규칙대로 고친 문장",
           "stages": [("쓸 때", "작성 스킬이 처음부터 규칙대로"), ("저장할 때", "검사 훅이 걸린 줄을 짚어 줌"), ("다 쓴 뒤", "im-not-ai로 윤문")],
           "foot": "네트워크를 쓰지 않습니다 · MIT"},
    "en": {"tag1": "A Claude Code plugin", "tag2": "Korean without translationese or AI tells",
           "left": "Written by Claude Code", "right": "Fixed by the rules",
           "stages": [("While writing", "the skill writes to the rules"), ("On save", "the hook points at flagged lines"), ("Afterwards", "im-not-ai polishing")],
           "foot": "No network · MIT"},
}
THEME = {
    "dark": {"bg": "#1e2229", "text": "#e6eaf0", "dim": "#9aa4b2", "before": "#ff8fa3", "after": "#7ee0a3",
             "chip": "#2d333d", "chipt": "#ffd166", "rule": "#39404b", "stage": "#262b33"},
    "light": {"bg": "#f6f7f9", "text": "#1f2328", "dim": "#59636e", "before": "#b42318", "after": "#1a7f37",
              "chip": "#e7ebf0", "chipt": "#9a6700", "rule": "#d0d7de", "stage": "#eceff3"},
}
W, H, M = 1280, 720, 64
SANS = "'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif"
MONO = "'SF Mono', Menlo, Consolas, monospace"
X_BEFORE, X_ARROW, X_AFTER = 272, 752, 796


def width(s, size):
    # 대략의 글자 폭. 한글은 1em, 로마자와 빈칸은 0.55em 으로 잡는다.
    return sum(size if unicodedata.east_asian_width(c) in "WF" else size * 0.55 for c in s)


def check_fit():
    for gid, code, *_rest, before, after in ROWS:
        if before not in GT[gid]:
            sys.exit(f"{gid} 에 「{before}」 가 없다. 정답 데이터와 맞춘다")
        if X_BEFORE + width(before, 21) > X_ARROW - 12 or X_AFTER + width(after, 21) > W - M + 24:
            sys.exit(f"{code} 문장이 칸을 넘친다")


def t(x, y, s, size, fill, weight=400, family=SANS, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')


def render(lang, theme):
    c, tx = THEME[theme], TEXT[lang]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" rx="16" fill="{c["bg"]}"/>',
         t(M, 112, "korean-writing", 56, c["text"], 700, MONO),
         t(W - M, 84, tx["tag1"], 20, c["dim"], 400, anchor="end"),
         t(W - M, 116, tx["tag2"], 24, c["text"], 700, anchor="end"),
         f'<line x1="{M}" y1="148" x2="{W - M}" y2="148" stroke="{c["rule"]}" stroke-width="2"/>',
         t(X_BEFORE, 186, tx["left"], 15, c["before"], 700),
         t(X_AFTER, 186, tx["right"], 15, c["after"], 700)]
    y = 238
    for _gid, code, ko, en, before, after in ROWS:
        label = f"{code} {ko if lang == 'ko' else en}"
        o.append(f'<rect x="{M}" y="{y - 22}" width="{X_BEFORE - M - 20}" height="32" rx="16" fill="{c["chip"]}"/>')
        o.append(t(M + 16, y, label, 15, c["chipt"], 700))
        o.append(t(X_BEFORE, y, before, 21, c["before"]))
        o.append(t(X_ARROW + 10, y, "→", 21, c["dim"], 700))
        o.append(t(X_AFTER, y, after, 21, c["after"], 700))
        y += 62
    y += 8
    sw = (W - 2 * M - 2 * 16) / 3
    for i, (head, body) in enumerate(tx["stages"]):
        x = M + i * (sw + 16)
        o.append(f'<rect x="{x:.0f}" y="{y}" width="{sw:.0f}" height="64" rx="12" fill="{c["stage"]}"/>')
        o.append(t(x + 20, y + 27, head, 15, c["chipt"], 700))
        o.append(t(x + 20, y + 51, body, 17, c["text"]))
    o.append(t(M, H - 36, "claude plugin install korean-writing", 18, c["dim"], 400, MONO))
    o.append(t(W - M, H - 36, tx["foot"], 16, c["dim"], 400, anchor="end"))
    o.append("</svg>")
    return "\n".join(o) + "\n"


def main():
    check_fit()
    for lang in ("ko", "en"):
        for theme in ("dark", "light"):
            name = "hero" + ("-light" if theme == "light" else "") + (".en" if lang == "en" else "") + ".svg"
            (REPO / "docs" / name).write_text(render(lang, theme), encoding="utf-8")
            print("그렸다:", "docs/" + name)


if __name__ == "__main__":
    main()
