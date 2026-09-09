#!/usr/bin/env python3
"""posttooluse.sh 회귀 테스트.

pytest 없이 assert 만 쓴다. 실행: python3 hooks-handlers/test_posttooluse.py

위반 케이스는 실제로 생성됐던 어색한 문장에서 가져왔다. 합성 예문이 아니다.
오탐(정상 글을 막는 것)이 미탐(위반을 놓치는 것)보다 나쁘다.
게이트가 정상 작업을 막으면 사람이 게이트를 꺼버리기 때문이다.

첫 assert 에서 멈추지 않고 전부 모아 보고한다. 변이 테스트로 커버리지를
검증할 때, 어느 케이스가 깨졌는지 정확히 알아야 하기 때문이다.
"""
import json
import pathlib
import re
import subprocess
import sys

HOOK = pathlib.Path(__file__).resolve().parent / "posttooluse.sh"
CODES = ("K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8")
FILLER = "이번 배포에서 고칠 곳이 나왔다. 담당자가 수강생을 옮기면 기록이 남는다. "
FAILS = []


def run(content, path="/tmp/x.md", tool="Write", key="content"):
    payload = json.dumps(
        {"tool_name": tool, "tool_input": {"file_path": path, key: content}},
        ensure_ascii=False,
    )
    p = subprocess.run([str(HOOK)], input=payload, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def expect_clean(name, content, **kw):
    rc, out = run(content, **kw)
    if rc != 0:
        FAILS.append(f"[오탐] {name}: {out.strip()[:140]}")
        print(f"  x {name}")
    else:
        print(f"  o {name}")


def expect_hit(name, content, code, count=None, **kw):
    """count 를 주면 보고된 횟수까지 검증한다.

    정규식 대안(A|B|C) 중 하나가 조용히 빠져도 다른 대안이 케이스를 살리므로,
    횟수를 보지 않으면 그 손실을 놓친다."""
    rc, out = run(content, **kw)
    got = [c for c in CODES if c + "  " in out]
    if rc != 2:
        FAILS.append(f"[미탐] {name}")
        print(f"  x {name}")
        return
    if code not in got:
        FAILS.append(f"[오분류] {name}: {code} 기대, {got} 나옴")
        print(f"  x {name}")
        return
    if count is not None:
        m = re.search(re.escape(code) + r"\s+[^\n]*?(\d+)회", out)
        n = int(m.group(1)) if m else -1
        if n != count:
            FAILS.append(f"[횟수] {name}: {count}회 기대, {n}회 나옴")
            print(f"  x {name}")
            return
    print(f"  o {name}  ({code}{'' if count is None else f' {count}회'})")


print("통과해야 하는 것 - 오탐 검사")
expect_clean(
    "정상 한국어 문단",
    "이번 작업에서 고칠 곳이 일곱 군데 나왔다. 그중 둘은 그대로 내보냈으면 바로 탈이 날 문제였다. "
    "담당자 두 명이 같은 수강생을 동시에 옮기면 변경 기록이 뒤엉킨다.",
)
expect_clean(
    "배포 설명 문단",
    "배포 방식도 손봤다. 전에는 명령을 하나씩 넣었고 중간에 잘못돼도 그냥 넘어갔다. "
    "이제는 거기서 멈추고 무엇이 문제인지 알려준다.",
)
expect_clean("한글이 적은 문서", "# Title\n\n" + "English body text here. " * 20)
expect_clean("짧은 수정", "오타 하나 고침")
expect_clean(".md 아닌 파일", FILLER * 3 + "축이 두 개고 갈래가 셋이며 레이어가 다르다.", path="/tmp/x.js")
expect_clean("편집 도구가 아님", FILLER * 3 + "결론적으로 혁신적이다.", tool="Bash")
expect_clean(
    "코드블록 안의 위반은 제외",
    FILLER * 3 + "\n```\n축이 두 개다. 갈래가 셋. 레이어가 다르다.\n```\n",
)
expect_clean(
    "인라인 코드 안의 위반은 제외",
    FILLER * 3 + "`축이 두 개고 갈래가 셋이며 레이어가 다르다`",
)
expect_clean(
    "표 셀의 줄표는 삽입구가 아니다",
    FILLER * 2 + "\n\n| 항목 | 결과 |\n|---|---|\n"
    "| 옵션 변경 | **PASS** - 정상 |\n| 출석 반영 | **PASS** — 확인 |\n"
    "| 화면 표시 | **PASS** — 일치 |\n| 이력 기록 | **PASS** — 남음 |\n"
    "| 캐시 갱신 | **PASS** — 반영 |\n",
)
expect_clean("줄표 삽입구 3개는 통과 (임계 4)", FILLER * 2 + "가 — 나. 다 — 라. 마 — 바.")
expect_clean("승패 1회는 통과 (임계 2)", FILLER * 3 + "충돌하면 규칙이 이깁니다.")

print("\n걸려야 하는 것 - 미탐 검사")
expect_hit("K1 줄표 삽입구 4개", FILLER * 2 + "가 — 나. 다 — 라. 마 — 바. 사 — 아.", "K1")
expect_hit(
    "K2 추상 구조어",
    "여기서 갈리는 축은 프로젝트 전용 여부가 아니라 성격이다. 기존 다섯 개는 구현 가이드이고 "
    "규칙은 다른 갈래다. 두 문제는 결이 다르고 레이어도 다르다.",
    "K2",
    count=4,
)
expect_hit(
    "K3 것 구문",
    "마지막 점검에서 손볼 곳이 일곱 군데 나왔다. 그중 둘은 그대로 내보냈으면 탈이 날 것들이었다.",
    "K3",
)
expect_hit(
    "K4 AI 관용구",
    "결론적으로 이번 변경은 혁신적이다. 종합하면 시사하는 바가 크다. 주목할 만한 개선이다.",
    "K4",
    count=4,
)
expect_hit(
    "K5 기계적 병렬",
    FILLER * 2 + "첫째, 기록이 어긋난다. 둘째, 화면이 멈춘다. 셋째, 캐시가 안 바뀐다.",
    "K5",
)
expect_hit(
    "K6 승패 의인화 2회",
    "규칙이 충돌하면 상위 문서가 이깁니다. 둘 다 값이 있으면 텍스트가 이기고 참조는 무시됩니다.",
    "K6",
)
expect_hit(
    "K7 사물 의인화 - 화면이 굳다",
    "변경이 실패하면 화면이 굳어버리는 문제다. 취소도 안 눌려서 창을 닫는 수밖에 없다.",
    "K7",
)
expect_hit(
    "K7 사물 의인화 - 넘어뜨리다",
    "점검용으로 켜둔 자동 확인 장치가 장비를 계속 넘어뜨리고 있었다. 원인을 찾는 데 오래 걸렸다.",
    "K7",
)
expect_hit(
    "K8 번역투 - 이중 피동",
    "이 문제에 대해 여러 방법으로 접근했다. 로그가 없어 원인이 파악되어지지 않았다.",
    "K8",
)
expect_hit(
    "K8 번역투 - 가지고 있다",
    "담당자가 로그를 가지고 있지 않아 원인을 확인하지 못했다. 다시 살펴봐야 한다.",
    "K8",
)

print("\n형식")
rc, out = run("결론적으로 축은 두 개고 갈래가 셋이며 레이어도 다르다. 혁신적인 변화다.")
if "K2" not in out or "K4" not in out:
    FAILS.append("복수 위반이 함께 보고되지 않는다")
    print("  x 복수 위반 동시 보고")
else:
    print("  o 복수 위반 동시 보고")
if "korean-writing" not in out:
    FAILS.append("교정 안내에 스킬 이름이 없다")
    print("  x 스킬 지목")
else:
    print("  o 교정 안내에 스킬 지목")

print("\n이상 입력에 죽지 않는다")
for label, payload in [
    ("빈 입력", ""),
    ("빈 객체", "{}"),
    ("JSON 아님", "not json"),
    ("tool_input null", '{"tool_name":"Write","tool_input":null}'),
]:
    p = subprocess.run([str(HOOK)], input=payload, capture_output=True, text=True)
    if p.returncode != 0:
        FAILS.append(f"[크래시] {label}: exit {p.returncode}")
        print(f"  x {label}")
    else:
        print(f"  o {label}")

print()
if FAILS:
    print(f"실패 {len(FAILS)}건")
    for f in FAILS:
        print(f"  {f}")
    sys.exit(1)
print("전부 통과")
