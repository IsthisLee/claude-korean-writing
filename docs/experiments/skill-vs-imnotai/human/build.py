#!/usr/bin/env python3
"""사람 블라인드 평가 페이지를 만든다.

블라인드 판정 스크립트(run.sh)가 만든 출력 폴더의 body/ 에서 스킬 글과 im-not-ai 윤문본을 짝지어
쌍마다 글 A·글 B 순서를 섞는다. 어느 쪽이 스킬인지는 페이지에 넣지 않고 mapping.json 에만 남긴다.
AI 판정자가 본 것과 같은 본문(요약 블록과 본문 뒤 안내를 걷어낸 글)을 사람도 본다.

사용: python3 build.py <run.sh 출력 폴더> <페이지 출력 경로>
      mapping.json 은 이 파일 옆에 쓴다. 섞는 순서는 SEED 로 고정한다.
"""
import json
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
PROMPTS = HERE.parent / "prompts"
SEED = 20260911


def main():
    run, page = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    ids = sorted({re.sub(r"^(skill|imnotai)_", "", p.stem) for p in (run / "body").glob("*.md")})
    rng = random.Random(SEED)
    pairs, mapping = [], {}
    for i in ids:
        skill = (run / "body" / f"skill_{i}.md").read_text(encoding="utf-8").strip()
        imnotai = (run / "body" / f"imnotai_{i}.md").read_text(encoding="utf-8").strip()
        a_is_skill = rng.random() < 0.5
        a, b = (skill, imnotai) if a_is_skill else (imnotai, skill)
        pairs.append({"id": i, "prompt": (PROMPTS / f"{i}.txt").read_text(encoding="utf-8").strip(), "a": a, "b": b})
        mapping[i] = {"A": "skill" if a_is_skill else "imnotai", "B": "imnotai" if a_is_skill else "skill"}
    rng.shuffle(pairs)
    (HERE / "mapping.json").write_text(json.dumps({"seed": SEED, "run": run.name, "pairs": mapping},
                                                  ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    html = (HERE / "page.html").read_text(encoding="utf-8")
    data = json.dumps(pairs, ensure_ascii=False).replace("</", "<\\/")
    page.write_text(html.replace("/*__PAIRS__*/[]", data), encoding="utf-8")
    print(f"쌍 {len(pairs)}개로 {page} 를 만들었다. 짝 정보는 {HERE / 'mapping.json'}")


if __name__ == "__main__":
    main()
