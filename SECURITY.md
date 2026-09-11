# 보안 정책

<p><strong>한국어</strong> · <a href="#security-policy">English</a></p>

## 지원 버전

보안 수정은 최신 마이너 판에만 올립니다. 옛 판으로 되돌려 고쳐 드리지 않으니 올려서 쓰세요.

| 버전       | 보안 수정                                       |
| ---------- | ----------------------------------------------- |
| 2.0.x      | 지원                                            |
| 1.3.x      | 지원하지 않음. 2.0.x 로 올려 주세요             |
| 1.2.x      | 지원하지 않음. 2.0.x 로 올려 주세요             |
| 1.1.x      | 지원하지 않음. 2.0.x 로 올려 주세요             |
| 1.0.x      | 지원하지 않음. 2.0.x 로 올려 주세요             |
| 1.0.0 미만 | 해당 없음 (1.0.0 이 첫 릴리스)                  |

이 표의 지원 판은 `plugin/.claude-plugin/plugin.json` 의 버전을 따릅니다. 둘이 어긋나면 CI 의 `버전 표기 일치` 작업이 막습니다.

## 신고 방법

취약점을 공개 이슈로 올리지 말아 주세요. 다음 두 가지 중 하나를 씁니다.

1. [Security → Report a vulnerability](https://github.com/IsthisLee/claude-korean-writing/security/advisories/new) 로 비공개 신고
2. 메일 `rjsgmldnwn@gmail.com`

받은 날부터 영업일 기준 5일 안에 접수 여부를 알려 드립니다. 수정이 필요하면 패치와 함께 권고문을 공개하고 신고자가 원하면 이름을 올립니다.

## 이 플러그인이 하는 일

설치하면 셸 스크립트 둘이 자동으로 실행됩니다. 하나는 `.md` 파일을 편집할 때마다, 다른 하나는 모델이 `korean-writing` 스킬을 부르기 직전에 돕니다. 무엇을 하는지 알고 설치할 수 있도록 아래에 적습니다. 표는 편집 검사 훅의 것입니다.

| 항목            | 실제                                                                                     |
| --------------- | ---------------------------------------------------------------------------------------- |
| 실행 시점       | `Edit` · `Write` · `MultiEdit` 직후 (PostToolUse)                                          |
| 실행하는 것     | `plugin/hooks-handlers/posttooluse.sh` 안의 bash 와 python3. 그 밖의 프로그램을 부르지 않습니다  |
| 읽는 것         | 편집한 내용, 편집한 `.md` 파일(줄표·쉼표를 파일 전체로 셀 때와 걸린 자리의 줄 번호를 찾을 때), 그 파일에서 저장소 루트까지 올라가며 찾은 `.korean-writing.json` |
| 쓰는 것         | 없습니다. 파일을 고치거나 만들지 않습니다                                                 |
| 네트워크        | 쓰지 않습니다. 원문은 이 컴퓨터 밖으로 나가지 않습니다                                    |
| 외부 의존성     | 없습니다. 표준 라이브러리만 씁니다                                                        |
| 결과            | stderr 에 걸린 항목을 적고 종료 코드 2 로 끝냅니다. 편집을 되돌리지 않습니다              |

스킬 확인 훅(`plugin/hooks-handlers/pretooluse-skill.sh`)은 훅 입력과 이 세션의 기록 파일을 읽고 아무것도 쓰지 않습니다. 기록 파일은 Claude Code 가 `transcript_path` 로 알려 주는 이 컴퓨터의 파일이고 뒤쪽 4MB 만 읽습니다. 사용자가 적용 여부 질문에 무엇을 골랐는지 찾는 데만 씁니다. `korean-writing` 호출이면 호출을 막거나 통과시키는 JSON 한 줄을 stdout 에 내고 그 밖의 호출에는 아무것도 내지 않습니다. 네트워크와 외부 프로그램을 쓰지 않습니다. 아래 명령의 파일 목록에 이 스크립트를 더하면 1번에 `import json, os, re, sys` 한 줄이 더 나오고 2번과 3번은 여전히 아무것도 나오지 않습니다.

네트워크를 쓰지 않는다는 것은 직접 확인할 수 있습니다. 스크립트는 392줄입니다. 1번은 `import sys, json, re, os, fnmatch` 한 줄만 나오고 2번과 3번은 아무것도 나오지 않아야 정상입니다.

```bash
# 1. 파이썬이 불러오는 모듈. sys, json, re, os, fnmatch 한 줄만 나옵니다
grep -nE '^\s*(import|from) ' plugin/hooks-handlers/posttooluse.sh

# 2. 네트워크 호출 — 출력 없음 (훅과 내장 윤문 스크립트 모두)
grep -nE 'curl|wget|urllib|requests|socket|urlopen|http\.client|import ssl' plugin/hooks-handlers/posttooluse.sh plugin/scripts/*.py plugin/skills/humanize-korean/references/*.py

# 3. 외부 프로그램 실행 — 출력 없음
grep -nE 'subprocess|os\.system|popen|exec\b' plugin/hooks-handlers/posttooluse.sh plugin/scripts/*.py plugin/skills/humanize-korean/references/*.py
```

`https?://` 라는 문자열이 스크립트 안에 한 번 나옵니다. 검사하기 전에 본문에서 링크 주소를 지우는 정규식이고 어디에 접속하는 코드가 아닙니다.

## 끄는 방법

훅 때문에 문제가 생기면 코드를 고치지 않고 끌 수 있습니다.

| 범위        | 방법                                                  |
| ----------- | ----------------------------------------------------- |
| 파일 하나   | 파일 머리에 `<!-- korean-writing: ignore -->`          |
| 세션 전체   | 환경변수 `KOREAN_WRITING_HOOK_DISABLED=1`              |
| 완전히 제거 | `claude plugin uninstall korean-writing`               |

`python3` 가 없는 환경에서는 검사하지 않고 그냥 통과합니다. 검사기가 작업을 막는 쪽보다 낫다고 봤습니다.

## 범위 밖

스킬 파일은 모델이 읽는 지시문이고 실행 코드가 아닙니다. 윤문 파이프라인의 파이썬 스크립트(`plugin/scripts/*.py`, `plugin/skills/humanize-korean/references/*.py`, im-not-ai 에서 내장)는 윤문 요청이 있을 때만 돌고 작업 폴더의 `_workspace/` 에 입력과 결과 파일을 쓰며 네트워크를 쓰지 않습니다. 이 문서의 약속은 이 파일들에도 해당합니다. 취약점 신고 대상은 실제로 실행되는 `plugin/hooks-handlers/` 와 `plugin/scripts/`, 그리고 `plugin/skills/korean-character-count/scripts/` 입니다.

---

<a id="security-policy"></a>

# Security Policy

<p><a href="#보안-정책">한국어</a> · <strong>English</strong></p>

## Supported versions

Security fixes land on the latest minor only. Older lines are not backported, so upgrade.

| Version | Security fixes                     |
| ------- | ---------------------------------- |
| 2.0.x   | Supported                          |
| 1.3.x   | Not supported. Please move to 2.0.x |
| 1.2.x   | Not supported. Please move to 2.0.x |
| 1.1.x   | Not supported. Please move to 2.0.x |
| 1.0.x   | Not supported. Please move to 2.0.x |
| < 1.0.0 | N/A (1.0.0 is the first release)   |

This table tracks the version in `plugin/.claude-plugin/plugin.json`. The `버전 표기 일치` CI job fails if the two drift apart.

## Reporting a vulnerability

Please do not open a public issue. Use one of these instead:

1. [Security → Report a vulnerability](https://github.com/IsthisLee/claude-korean-writing/security/advisories/new) (private)
2. Email `rjsgmldnwn@gmail.com`

You will get an acknowledgement within 5 business days. If a fix is needed, an advisory is published alongside the patch, and reporters are credited on request.

## What this plugin does

Installing it means two shell scripts run automatically: one every time you edit a `.md` file, the other right before Claude calls the `korean-writing` skill. Here is exactly what the first one does:

| Item              | Reality                                                                       |
| ----------------- | ----------------------------------------------------------------------------- |
| When it runs      | Right after `Edit` / `Write` / `MultiEdit` (PostToolUse)                        |
| What it executes  | bash and python3 inside `plugin/hooks-handlers/posttooluse.sh`, nothing else           |
| What it reads     | The edited content; the edited `.md` file (to count em dashes and commas across the whole file and to find line numbers for flagged spots); the first `.korean-writing.json` found walking up to the repository root |
| What it writes    | Nothing. It never modifies or creates files                                    |
| Network           | None. Your text never leaves your machine                                      |
| Dependencies      | None. Standard library only                                                    |
| Output            | Writes findings to stderr, exits 2. It never reverts your edit                  |

The skill-confirm hook (`plugin/hooks-handlers/pretooluse-skill.sh`) reads the hook input and this session's transcript, and writes nothing. The transcript is the local file Claude Code names in `transcript_path`; only its last 4 MB are read, and only to find what you answered when asked whether to apply the rules. For a `korean-writing` call it prints one line of JSON that blocks or lets the call through, and it prints nothing for any other call. It uses no network and runs no other program. Adding it to the file lists below makes the first command print one more line, `import json, os, re, sys`; the other two still print nothing.

You can verify the network claim yourself. The script is 392 lines. The first command should print a single `import sys, json, re, os, fnmatch` line; the other two should print nothing:

```bash
# 1. Python imports. Prints one line: sys, json, re, os, fnmatch
grep -nE '^\s*(import|from) ' plugin/hooks-handlers/posttooluse.sh

# 2. Network calls - no output (the hook and the vendored polishing scripts)
grep -nE 'curl|wget|urllib|requests|socket|urlopen|http\.client|import ssl' plugin/hooks-handlers/posttooluse.sh plugin/scripts/*.py plugin/skills/humanize-korean/references/*.py

# 3. Spawning external programs - no output
grep -nE 'subprocess|os\.system|popen|exec\b' plugin/hooks-handlers/posttooluse.sh
```

The string `https?://` does appear once. It is a regex that strips link URLs out of the text before checking, not code that connects anywhere.

## Turning it off

| Scope        | How                                              |
| ------------ | ------------------------------------------------ |
| One file     | Put `<!-- korean-writing: ignore -->` at the top |
| Whole session| Set `KOREAN_WRITING_HOOK_DISABLED=1`             |
| Remove it    | `claude plugin uninstall korean-writing`         |

Where `python3` is missing, the hook exits quietly without checking.

## Out of scope

Skill files are instructions the model reads, not code that runs. The polishing pipeline's Python scripts (`plugin/scripts/*.py` and `plugin/skills/humanize-korean/references/*.py`, vendored from im-not-ai) run only on a polish request, write input and result files under `_workspace/` in the working directory, and use no network. The promises in this document cover those files as well. Vulnerability reports apply to `plugin/hooks-handlers/`, `plugin/scripts/`, and `plugin/skills/korean-character-count/scripts/`.
