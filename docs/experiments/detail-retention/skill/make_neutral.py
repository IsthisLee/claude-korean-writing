#!/usr/bin/env python3
"""중립 대조군(N)에 붙일 문서를 만든다 (EVALUATION.md J3).

문체와 관계없는 저장소 운영 문서를 이어 붙여 plugin/SKILL.md 와 글자 수를 맞춘다.
2026-09-11 실측에서 글자 수는 같았지만 영어가 섞여 입력 토큰은 약 7,700 으로 스킬(약 10,100)보다 적었다.
출력은 ../out/skill/neutral.md 이고 커밋하지 않는다.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUT = HERE.parent / "out" / "skill"
OUT.mkdir(parents=True, exist_ok=True)

target = len((REPO / "plugin/SKILL.md").read_text(encoding="utf-8"))
parts = ["CODE_OF_CONDUCT.md", "CONTRIBUTING.md", "plugin/skills/korean-character-count/instruction.md", "SECURITY.md"]
text = "# 참고 문서\n\n이 저장소의 운영 문서를 모은 것이다. 지금 요청과는 관계없다.\n\n"
text += "\n\n".join((REPO / p).read_text(encoding="utf-8") for p in parts)
(OUT / "neutral.md").write_text(text[:target], encoding="utf-8")
print(f"neutral.md {len(text[:target])}글자 / SKILL.md {target}글자")
