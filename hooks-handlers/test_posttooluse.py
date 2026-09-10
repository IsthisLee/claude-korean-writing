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
import os
import pathlib
import re
import subprocess
import sys
import tempfile

HOOK = pathlib.Path(__file__).resolve().parent / "posttooluse.sh"
CODES = ("K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9", "K10")
FILLER = "이번 배포에서 고칠 곳이 나왔다. 담당자가 수강생을 옮기면 기록이 남는다. "
FAILS = []


def run(content, path="/tmp/x.md", tool="Write", key="content", env=None):
    payload = json.dumps(
        {"tool_name": tool, "tool_input": {"file_path": path, key: content}},
        ensure_ascii=False,
    )
    full_env = {**os.environ, **env} if env else None
    p = subprocess.run([str(HOOK)], input=payload, capture_output=True, text=True, env=full_env)
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
expect_clean("서버가 죽다는 개발자의 일상어", FILLER * 3 + "새벽에 서버가 죽어서 재시작했다. 훅이 죽어도 편집은 남는다.")
expect_clean(
    "~에 대해·~를 통해는 사람도 많이 쓴다 (실측 후 제외)",
    "이 글에서는 중첩 DTO 검증에 대해 다룬다. 먼저 데코레이터를 통해 규칙을 붙이고, "
    "실패 응답에 대해 어떤 형식을 쓸지 정한다. 마지막으로 테스트를 통해 동작을 확인하고, "
    "운영에서 만난 문제에 대해 적는다.",
)
expect_clean(
    "~~~ 울타리 코드블록 안의 위반은 제외",
    FILLER * 3 + "\n~~~\n축이 두 개다. 갈래가 셋. 레이어가 다르다. 결론적으로 혁신적이다.\n~~~\n",
)
expect_clean(
    "HTML 주석 안의 위반은 제외",
    FILLER * 3 + "\n<!-- 축이 두 개다. 갈래가 셋. 레이어가 다르다. 결론적으로 혁신적이다. -->\n",
)
expect_clean(
    "표 안의 교정 예시(전/후)는 위반이 아니다",
    FILLER * 2 + "\n\n| 전 | 후 |\n|---|---|\n"
    "| 화면이 굳어 취소도 안 됩니다 | 화면이 멈춰 취소도 안 됩니다 |\n"
    "| 탈이 날 것들이었습니다 | 탈이 날 문제였습니다 |\n"
    "| 축이 두 개다. 세 갈래다 | 기준이 두 개다. 세 가지다 |\n",
)

expect_clean("부정 대구 2회는 통과 (임계 3)", FILLER * 2 + "이것은 성능 문제가 아니라 설정 문제다. 고칠 곳은 코드가 아니라 문서다.")
expect_clean(
    "조건절 아니라면·아니라서는 대구가 아니다",
    FILLER * 2 + "기준이 이번 주가 아니라면 날짜만 고친다. 원인이 설정이 아니라서 더 봐야 한다. "
    "값이 숫자가 아니라면 그대로 둔다.",
)
expect_clean(
    "연결어미 뒤 쉼표 5회는 통과 (임계 6, 비율 100%)",
    FILLER * 2 + "훅을 더했고, 규칙을 바꿨고, 테스트를 돌렸고, 문서를 고쳤고, 배지를 올렸고, 태그를 달았다.",
)
expect_clean(
    "연결어미 뒤 쉼표 6회여도 비율이 30% 미만이면 통과 (6/21 = 28.6%)",
    FILLER + "훅을 더했고, 규칙을 바꿨고, 테스트를 돌렸고, 문서를 고쳤고, 배지를 올렸고, 태그를 달았고, 배포를 마쳤다. "
    + "설정을 읽고 값을 채우고 결과를 남기고 로그를 쌓고 화면에 뿌리고 기록을 지우고 "
    + "다시 읽고 다시 채우고 다시 남기고 다시 쌓고 다시 뿌리고 다시 지우고 "
    + "마지막으로 검사하고 확인하고 정리하고 끝낸다.",
)

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
expect_hit(
    "K9 부정 대구 3회",
    FILLER * 2 + "이것은 성능 문제가 아니라 설정 문제다. 고칠 곳은 코드가 아니라 문서다. "
    "필요한 것은 새 기능이 아니라 기준이다.",
    "K9",
    count=3,
)
expect_hit(
    "K10 비율 46%도 걸린다 (6/13, 임계 30%)",
    FILLER + "훅을 더했고, 규칙을 바꿨고, 테스트를 돌렸고, 문서를 고쳤고, 배지를 올렸고, 태그를 달았고, 배포를 마쳤다. "
    "설정을 읽고 값을 채우고 결과를 남기고 로그를 쌓고 화면에 뿌리고 기록을 지우고 마지막으로 정리하고 끝낸다.",
    "K10",
    count=6,
)
expect_hit(
    "K10 연결어미 뒤 쉼표 6회",
    FILLER * 2 + "훅을 더했고, 규칙을 바꿨고, 테스트를 돌렸고, 문서를 고쳤고, 배지를 올렸고, 태그를 달았고, 배포를 마쳤다.",
    "K10",
    count=6,
)

EN = "This section explains how the release script works and what it checks. " * 8
EN_DASH = "The plan — as agreed — is fine. Also — yes — done. " * 8

print("\n영어가 대부분인 편집 - 한글 비중 30% 이상인 줄만 모아 다시 본다")
expect_hit(
    "영어 문서 안의 한국어 위반 문단",
    EN + "\n\n규칙이 충돌하면 상위 문서가 이깁니다. 둘 다 값이 있으면 텍스트가 이기고 참조는 무시됩니다.\n\n" + EN,
    "K6",
)
expect_clean("영어 문서 안의 정상 한국어 문단", EN + "\n\n" + FILLER * 2 + "\n\n" + EN)
expect_clean("영어 문서 안의 한국어가 20자 미만", EN + "\n\n오타 하나 고침\n\n" + EN)
expect_clean("영어 줄의 줄표는 세지 않는다", EN_DASH + "\n\n" + FILLER * 2)

print("\n끄기 - 표시가 없으면 걸리고, 있으면 통과한다")
BAD = FILLER * 3 + "결론적으로 혁신적이다."
expect_hit("표시가 없으면 같은 글이 걸린다", BAD, "K4")
expect_clean("이번에 쓴 부분에 korean-writing: ignore 표시", "<!-- korean-writing: ignore -->\n" + BAD)
_formal = os.path.join(tempfile.mkdtemp(), "formal.md")
with open(_formal, "w", encoding="utf-8") as _f:
    _f.write("<!-- korean-writing: ignore -->\n# 이용 약관\n")
expect_clean("파일 머리의 표시 (Edit 로 일부만 고칠 때)", BAD, path=_formal, tool="Edit", key="new_string")
expect_clean("환경변수 KOREAN_WRITING_HOOK_DISABLED=1", BAD, env={"KOREAN_WRITING_HOOK_DISABLED": "1"})

# 표시는 줄 하나로 서 있을 때만 지시다. 이 기능을 설명하는 문서가 자기 검사를 건너뛰면 안 된다.
expect_hit(
    "본문이 표시 문자열을 인용해도 검사는 돈다",
    "격식 문서면 파일 머리에 `<!-- korean-writing: ignore -->` 를 넣습니다.\n\n" + BAD,
    "K4",
)
expect_hit(
    "표 칸의 표시 인용도 끄지 않는다",
    "| 범위 | 방법 |\n|---|---|\n| 파일 하나 | 파일 머리에 `<!-- korean-writing: ignore -->` |\n\n" + BAD,
    "K4",
)
expect_hit(
    "머리 10줄 밖의 표시는 끄지 않는다",
    "\n".join(["첫 줄부터 열 줄을 채운다."] * 11) + "\n<!-- korean-writing: ignore -->\n" + BAD,
    "K4",
)

print("\n누적 - 이번 편집에 있으면 파일 전체 개수로 판정한다 (K1 줄표, K10 연결어미 쉼표)")
_dir = tempfile.mkdtemp()
_acc = os.path.join(_dir, "acc.md")
with open(_acc, "w", encoding="utf-8") as _f:
    _f.write(FILLER * 2 + "가 — 나. 다 — 라. 마 — 바.\n" + FILLER * 2 + "사 — 아.\n")
expect_hit("파일에 3개 있고 이번 편집이 1개를 더해 4개", FILLER * 2 + "사 — 아.", "K1", path=_acc, tool="Edit", key="new_string")
_many = os.path.join(_dir, "many.md")
with open(_many, "w", encoding="utf-8") as _f:
    _f.write(FILLER * 2 + "가 — 나. 다 — 라. 마 — 바. 사 — 아. 자 — 차.\n" + FILLER * 3 + "\n")
expect_clean("파일에 5개 있어도 이번 편집에 없으면 잡지 않는다", FILLER * 3, path=_many, tool="Edit", key="new_string")
_one = os.path.join(_dir, "one.md")
with open(_one, "w", encoding="utf-8") as _f:
    _f.write(FILLER * 3 + "가 — 나.\n")
expect_clean("이번 편집 1개, 파일 전체 1개", FILLER * 3 + "가 — 나.", path=_one, tool="Edit", key="new_string")
_cm = os.path.join(_dir, "comma.md")
with open(_cm, "w", encoding="utf-8") as _f:
    _f.write(FILLER * 2 + "훅을 더했고, 규칙을 바꿨고, 테스트를 돌렸고, 문서를 고쳤고, 배지를 올렸고, 로그를 남겼다.\n"
             + FILLER + "태그를 달았고, 배포를 마쳤다.\n")
expect_hit(
    "K10 파일에 5회 있고 이번 편집이 1회를 더해 6회",
    FILLER + "태그를 달았고, 배포를 마쳤다.",
    "K10",
    path=_cm, tool="Edit", key="new_string",
)
_cm2 = os.path.join(_dir, "comma2.md")
with open(_cm2, "w", encoding="utf-8") as _f:
    _f.write(FILLER * 2 + "훅을 더했고, 규칙을 바꿨고, 테스트를 돌렸고, 문서를 고쳤고, 배지를 올렸고, "
             "태그를 달았고, 로그를 남겼고, 배포를 마쳤다.\n")
expect_clean(
    "K10 파일에 7회 있어도 이번 편집에 없으면 잡지 않는다",
    FILLER * 3,
    path=_cm2, tool="Edit", key="new_string",
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
