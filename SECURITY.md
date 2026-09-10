# 보안 정책

<p><strong>한국어</strong> · <a href="#security-policy">English</a></p>

## 지원 버전

| 버전    | 보안 수정 |
| ------- | --------- |
| 1.0.x   | 지원      |
| 1.0.0 미만 | 해당 없음 (1.0.0 이 첫 릴리스) |

## 신고 방법

취약점을 공개 이슈로 올리지 말아 주세요. 다음 두 가지 중 하나를 씁니다.

1. [Security → Report a vulnerability](https://github.com/IsthisLee/claude-korean-writing/security/advisories/new) 로 비공개 신고
2. 메일 `rjsgmldnwn@gmail.com`

받은 날부터 영업일 기준 5일 안에 접수 여부를 알려 드립니다. 수정이 필요하면 패치와 함께 권고문을 공개하고 신고자가 원하면 이름을 올립니다.

## 이 플러그인이 하는 일

설치하면 `.md` 파일을 편집할 때마다 셸 스크립트 하나가 자동으로 실행됩니다. 무엇을 하는지 알고 설치할 수 있도록 아래에 적습니다.

| 항목            | 실제                                                                                     |
| --------------- | ---------------------------------------------------------------------------------------- |
| 실행 시점       | `Edit` · `Write` · `MultiEdit` 직후 (PostToolUse)                                          |
| 실행하는 것     | `hooks-handlers/posttooluse.sh` 안의 bash 와 python3. 그 밖의 프로그램을 부르지 않습니다  |
| 읽는 것         | 편집한 내용, 그리고 줄표와 연결어미 쉼표를 셀 때 편집한 `.md` 파일 자체                   |
| 쓰는 것         | 없습니다. 파일을 고치거나 만들지 않습니다                                                 |
| 네트워크        | 쓰지 않습니다. 원문은 이 컴퓨터 밖으로 나가지 않습니다                                    |
| 외부 의존성     | 없습니다. 표준 라이브러리만 씁니다                                                        |
| 결과            | stderr 에 걸린 항목을 적고 종료 코드 2 로 끝냅니다. 편집을 되돌리지 않습니다              |

네트워크를 쓰지 않는다는 것은 직접 확인할 수 있습니다. 스크립트는 234줄입니다. 아래 세 명령 모두 아무것도 출력하지 않아야 정상입니다.

```bash
# 1. 파이썬이 불러오는 모듈. sys, json, re, os 한 줄만 나옵니다
grep -nE '^\s*(import|from) ' hooks-handlers/posttooluse.sh

# 2. 네트워크 호출 — 출력 없음 (훅과 내장 윤문 스크립트 모두)
grep -nE 'curl|wget|urllib|requests|socket|urlopen|http\.client|import ssl' hooks-handlers/posttooluse.sh scripts/*.py skills/humanize-korean/references/*.py

# 3. 외부 프로그램 실행 — 출력 없음
grep -nE 'subprocess|os\.system|popen|exec\b' hooks-handlers/posttooluse.sh scripts/*.py skills/humanize-korean/references/*.py
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

스킬 파일은 모델이 읽는 지시문이고 실행 코드가 아닙니다. 윤문 파이프라인의 파이썬 스크립트(`scripts/*.py`, `skills/humanize-korean/references/*.py`, im-not-ai 에서 내장)는 윤문 요청이 있을 때만 돌고 작업 폴더의 `_workspace/` 에 입력과 결과 파일을 쓰며 네트워크를 쓰지 않습니다. 이 문서의 약속은 이 파일들에도 해당합니다. 취약점 신고 대상은 실제로 실행되는 `hooks-handlers/` 와 `scripts/`, 그리고 `skills/korean-character-count/scripts/` 입니다.

---

<a id="security-policy"></a>

# Security Policy

<p><a href="#보안-정책">한국어</a> · <strong>English</strong></p>

## Supported versions

| Version | Security fixes |
| ------- | -------------- |
| 1.0.x   | Supported      |
| < 1.0.0 | N/A (1.0.0 is the first release) |

## Reporting a vulnerability

Please do not open a public issue. Use one of these instead:

1. [Security → Report a vulnerability](https://github.com/IsthisLee/claude-korean-writing/security/advisories/new) (private)
2. Email `rjsgmldnwn@gmail.com`

You will get an acknowledgement within 5 business days. If a fix is needed, an advisory is published alongside the patch, and reporters are credited on request.

## What this plugin does

Installing it means a shell script runs automatically every time you edit a `.md` file. Here is exactly what it does:

| Item              | Reality                                                                       |
| ----------------- | ----------------------------------------------------------------------------- |
| When it runs      | Right after `Edit` / `Write` / `MultiEdit` (PostToolUse)                        |
| What it executes  | bash and python3 inside `hooks-handlers/posttooluse.sh`, nothing else           |
| What it reads     | The edited content, plus the edited `.md` file when counting em dashes and commas after connective endings |
| What it writes    | Nothing. It never modifies or creates files                                    |
| Network           | None. Your text never leaves your machine                                      |
| Dependencies      | None. Standard library only                                                    |
| Output            | Writes findings to stderr, exits 2. It never reverts your edit                  |

You can verify the network claim yourself. The script is 234 lines. All three commands below should print nothing:

```bash
# 1. Python imports. Prints one line: sys, json, re, os
grep -nE '^\s*(import|from) ' hooks-handlers/posttooluse.sh

# 2. Network calls - no output (the hook and the vendored polishing scripts)
grep -nE 'curl|wget|urllib|requests|socket|urlopen|http\.client|import ssl' hooks-handlers/posttooluse.sh scripts/*.py skills/humanize-korean/references/*.py

# 3. Spawning external programs - no output
grep -nE 'subprocess|os\.system|popen|exec\b' hooks-handlers/posttooluse.sh
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

Skill files are instructions the model reads, not code that runs. The polishing pipeline's Python scripts (`scripts/*.py` and `skills/humanize-korean/references/*.py`, vendored from im-not-ai) run only on a polish request, write input and result files under `_workspace/` in the working directory, and use no network. The promises in this document cover those files as well. Vulnerability reports apply to `hooks-handlers/`, `scripts/`, and `skills/korean-character-count/scripts/`.
