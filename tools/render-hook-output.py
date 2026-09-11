#!/usr/bin/env python3
"""README 의 훅 출력 그림(docs/hook-output.svg)을 실제 훅 출력으로 다시 그린다.

정답 데이터(tests/ground-truth.json)의 문장으로 7줄짜리 문서를 만들어 훅에 넣고 그 stderr 를
글자 하나 바꾸지 않고 옮긴다. 화면 틀(프롬프트와 Write 줄)만 그린 것이고 노란 줄부터가 훅의 출력이다.
훅의 안내 문구를 바꿨으면 이 스크립트를 다시 돌려 그림을 맞춘다.

사용: python3 tools/render-hook-output.py           docs/hook-output.svg 를 다시 쓴다
      python3 tools/render-hook-output.py --print   그림 대신 입력 문서와 훅 출력을 찍는다
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unicodedata
from xml.sax.saxutils import escape

REPO = pathlib.Path(__file__).resolve().parent.parent
HOOK = REPO / "plugin" / "hooks-handlers" / "posttooluse.sh"
OUT = REPO / "docs" / "hook-output.svg"
NAME = "배포-지연.md"

G = {it["id"]: it["text"] for it in json.loads((REPO / "tests" / "ground-truth.json").read_text(encoding="utf-8"))}
DOC = "\n".join([
    "# 배포 지연 사유",
    "",
    G["G07"],
    "",
    G["G05"],
    "",
    " ".join([G["G01"], G["G03"], G["G04"], "결론적으로 다음 배포 전에 다시 봐야 합니다."]),
]) + "\n"


def run_hook():
    path = os.path.join(tempfile.mkdtemp(), NAME)
    with open(path, "w", encoding="utf-8") as f:
        f.write(DOC)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("KOREAN_WRITING", "CLAUDE_PLUGIN_OPTION"))}
    payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": path, "content": DOC}}, ensure_ascii=False)
    r = subprocess.run([str(HOOK)], input=payload, capture_output=True, text=True, env=env)
    if r.returncode != 2:
        sys.exit(f"훅이 걸지 않았다 (exit {r.returncode}). 입력 문서를 확인한다")
    return r.stderr.rstrip("\n").split("\n")


def cols(ch):
    return 2 if unicodedata.east_asian_width(ch) in "WF" else 1


def wrap(line, limit=128, indent="      "):
    # 한글은 두 칸으로 센다. 가능하면 빈칸에서 끊고 이어지는 줄은 여섯 칸 들여 쓴다.
    out = []
    while sum(map(cols, line)) > limit:
        w, cut = 0, len(line)
        for i, ch in enumerate(line):
            w += cols(ch)
            if w > limit:
                cut = i
                break
        sp = line.rfind(" ", len(indent) + 1, cut)
        if sp <= len(indent):
            sp = cut
        out.append(line[:sp].rstrip())
        line = indent + line[sp:].lstrip()
    out.append(line)
    return out


def color(line):
    if line.startswith("[korean-writing]"):
        return "#ffd166"
    if re.match(r"^  K\d+  ", line):
        return "#ff8fa3"
    if line.startswith("      "):
        return "#c9d1d9"
    return "#d7dde5"


def main():
    out = run_hook()
    if "--print" in sys.argv:
        print(DOC)
        print("\n".join(out))
        return
    rows = [
        ("$ claude", "#9aa4b2"),
        (f"> {NAME} 에 지연 사유 정리해줘", "#9aa4b2"),
        ("", "#d7dde5"),
        (f"⏺ Write({NAME})", "#7fb3ff"),
        (f"  ⎿  Wrote {DOC.count(chr(10))} lines to {NAME}", "#7fb3ff"),
        ("", "#d7dde5"),
    ]
    for line in out:
        rows += [(piece, color(line)) for piece in wrap(line)]
    y0, dy, w = 48, 22, 1074
    h = y0 + dy * (len(rows) - 1) + 26
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        "font-family=\"SF Mono, Menlo, Consolas, 'Noto Sans Mono CJK KR', 'Apple SD Gothic Neo', monospace\" font-size=\"13\">",
        f'<rect width="{w}" height="{h}" rx="10" fill="#1e2229"/>',
        '<circle cx="20" cy="18" r="6" fill="#ff5f56"/><circle cx="40" cy="18" r="6" fill="#ffbd2e"/>'
        '<circle cx="60" cy="18" r="6" fill="#27c93f"/>',
    ]
    for i, (text, col) in enumerate(rows):
        svg.append(f'<text x="18" y="{y0 + dy * i}" fill="{col}" xml:space="preserve">{escape(text)}</text>')
    svg.append("</svg>")
    OUT.write_text("\n".join(svg) + "\n", encoding="utf-8")
    codes = [l.split()[0] for l in out if re.match(r"^  K\d+  ", l)]
    print(f"{OUT.relative_to(REPO)} 를 다시 썼다. 줄 {len(rows)}개, 코드 {'·'.join(codes)}")


if __name__ == "__main__":
    main()
