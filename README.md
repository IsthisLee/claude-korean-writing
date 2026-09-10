<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/banner-light.svg">
  <img src="docs/banner.svg" alt="korean-writing" width="100%">
</picture>

<p align="center">
  <strong>한국어</strong> · <a href="README.en.md">English</a>
</p>

<p align="center">
  <strong>Claude Code가 쓰는 모든 한국어의 품질을 맡는 플러그인.</strong><br>
  답변에는 규칙이 붙고, 글은 처음부터 사람이 쓴 것처럼 나오고, .md 파일은 저장할 때 검사받습니다.<br>
  원문은 이 컴퓨터를 떠나지 않습니다.
</p>

<p align="center">
  <a href="https://github.com/IsthisLee/claude-korean-writing/actions/workflows/validate.yml"><img alt="Validate" src="https://github.com/IsthisLee/claude-korean-writing/actions/workflows/validate.yml/badge.svg?branch=main"></a>
  <img alt="MIT" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Claude Code Plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2">
  <img alt="version" src="https://img.shields.io/badge/version-1.0.0-lightgrey">
  <img alt="network" src="https://img.shields.io/badge/network-none-success">
  <img alt="platform" src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey">
</p>

<p align="center">
  <a href="#무엇을-하는-플러그인인가">소개</a> ·
  <a href="#설치">설치</a> ·
  <a href="#쓰는-법">쓰는 법</a> ·
  <a href="#안에-무엇이-있나">구성</a> ·
  <a href="#검사-훅의-판정">훅의 판정</a> ·
  <a href="#정한-원칙">원칙</a> ·
  <a href="#얼마나-믿을-수-있나">검증</a> ·
  <a href="#자주-하는-질문">FAQ</a>
</p>

> **v1.0.0**: 첫 릴리스입니다. 스킬 넷, `.md` 편집을 검사하는 훅, 문서 검사와 릴리스 스크립트가 들어 있습니다. 릴리스 뒤 main에는 세션이 열릴 때 상시 규칙을 넣는 훅이 더해졌습니다. 상세: [CHANGELOG.md](CHANGELOG.md)

## 무엇을 하는 플러그인인가

Claude Code는 한국어를 틀리지 않게 씁니다. 문제는 틀리지 않는데도 읽으면 걸린다는 점입니다. 영어 문장을 그대로 옮긴 어순, 영어에서 건너온 비유, 어느 문서에서나 같은 자리에 나오는 상투구가 그렇습니다. 출판사 편집부가 그런 표현을 보고 원고를 AI가 썼다고 의심할 정도입니다.

이 플러그인은 그 한국어가 만들어지는 자리마다 하나씩 붙습니다. 세션이 열리면 답변용 규칙이 들어가고, 글을 부탁하면 처음부터 규칙대로 쓰는 스킬이 뜨고, 써 둔 글을 다듬어 달라면 사실은 두고 문체만 손보는 스킬이 뜨고, `.md` 파일을 저장하면 훅이 방금 쓴 부분을 검사합니다. 글자 수를 물으면 모델이 어림하지 않고 스크립트가 세고, README를 부탁하면 절 구성을 잡는 스킬이 먼저 나섭니다.

| 자리            | 담당                              | 언제 움직이나                   | 규칙이 적힌 곳                       |
| --------------- | --------------------------------- | ------------------------------- | ------------------------------------ |
| 평소 답변       | SessionStart 훅                   | 세션 시작·재개·`/clear`·압축    | `hooks-handlers/always-on.md`        |
| 글 작성 요청    | `korean-writing` 스킬             | 써 달라는 요청이 오면           | `SKILL.md`                           |
| 써 둔 글 다듬기 | `humanize-korean` 스킬            | 다듬어 달라는 요청이 오면       | `skills/humanize-korean/SKILL.md`    |
| `.md` 파일 편집 | PostToolUse 훅                    | `Edit`·`Write`·`MultiEdit` 직후 | `hooks-handlers/posttooluse.sh`      |
| 글자 수 제한    | `korean-character-count` 스킬     | 몇 자인지 물으면                | `skills/korean-character-count/`     |
| README          | `crafting-effective-readmes` 스킬 | README를 만들거나 고치자고 하면 | `skills/crafting-effective-readmes/` |

네트워크는 어디서도 쓰지 않습니다. 훅은 bash와 python3 정규식이고, 글자 수 스크립트는 `node:fs`만 씁니다.

## 실제 문장 넷

판정 규칙은 지어낸 예문이 아니라 Claude Code가 실제로 생성했던 문장에서 나왔습니다. 그런 문장 열 건이 [`hooks-handlers/ground-truth.json`](./hooks-handlers/ground-truth.json)에 있습니다. 넷만 보면 이렇습니다.

> 규칙이 충돌하면 상위 문서가 **이깁니다**. 둘 다 값이 있을 때는 텍스트가 **이기고** 강의실 참조는 무시됩니다.

문서와 설정은 서로 겨루지 않습니다. 우선한다, 따른다라고 쓰면 됩니다. 출판사 편집부가 서로 다른 저자의 원고 두 건에서 같은 자리에 같은 "이깁니다"를 보고 지목한 표현입니다.

> 원인은 힙 부족이 아니었습니다 **—** 실측해보니 **—** 설정이 아예 먹히지 않았습니다.

줄표로 끼워 넣는 삽입구는 영어 문장 부호를 그대로 옮긴 것입니다. 같은 편집부가 지목한 나머지 하나이고, 한국어 산문에서 가장 눈에 띄는 표지입니다. 쉼표를 쓰거나 문장을 나누면 사라집니다.

> 여기서 갈리는 **축은** 프로젝트 전용 여부가 아니라 성격입니다. 두 문제는 **결이** 다르고 **레이어도** 다릅니다.

구조를 은유로 설명하는 습관입니다. 기준, 경우, 종류, 단계처럼 구체적인 명사로 바꾸면 됩니다.

> 시험용 장비가 몇 초 만에 **쓰러졌습니다**. **일으켜 세우면** 또 쓰러지기를 스무 분 넘게 반복했습니다.

장비가 쓰러지지는 않습니다. 멈췄고 다시 켰다고 쓰면 됩니다. 영어 비유를 직역한 의인화입니다.

검사 훅은 이런 표지 여덟 종을 정규식으로 잡습니다. 그보다 넓은 판정은 규칙집 [`references/taxonomy.md`](./references/taxonomy.md)가 맡습니다. 번역투, 영어 인용 과다, 구조적 AI 패턴, AI 관용구, 리듬 균일성, 과도한 수식, 완곡 남발, 접속사 남발, 형식명사 과다, 시각 장식 남용의 열 분류 아래 73항목이 심각도와 처방과 함께 적혀 있습니다.

## 설치

```bash
claude plugin marketplace add IsthisLee/claude-korean-writing
claude plugin install korean-writing
```

설정할 것은 없습니다. `claude plugin list`에 `korean-writing`이 `enabled`로 보이면 됩니다. 새 버전은 `claude plugin update korean-writing`으로 받습니다.

받아 둔 저장소 경로를 마켓플레이스로 등록하는 방법도 있습니다. 사내 사본이나 포크를 쓸 때입니다.

```bash
claude plugin marketplace add /경로/claude-korean-writing
claude plugin install korean-writing
```

| 필요한 것   | 어디에 쓰나            | 없으면                   |
| ----------- | ---------------------- | ------------------------ |
| Claude Code | 전부. 2.1.266에서 확인 |                          |
| `bash`      | 훅 둘과 스크립트 셋    | 훅이 돌지 않습니다       |
| `python3`   | 검사 훅의 판정 부분    | 검사 없이 통과합니다     |
| `node` 18+  | 글자 수 스크립트       | 그 스킬만 쓸 수 없습니다 |

패키지를 따로 설치하지 않습니다. macOS와 Linux는 CI가 같은 검사를 돌립니다. Windows는 Git Bash나 WSL이 있어야 하고 아직 확인하지 않았습니다.

## 쓰는 법

평소처럼 말하면 됩니다. 스킬은 요청을 보고 스스로 뜹니다. 직접 부르려면 슬래시 이름을 씁니다.

| 부탁                         | 예                                                        | 직접 부를 때                                 |
| ---------------------------- | --------------------------------------------------------- | -------------------------------------------- |
| 글을 처음부터 쓰기           | "운영팀에 보낼 옵션 변경 안내문 써줘. 슬랙에 캐주얼하게." | `/korean-writing`                            |
| 써 둔 글에서 번역투 걷어내기 | "아래 글 번역투만 고쳐줘. 사실과 숫자는 그대로 두고."     | `/korean-writing:humanize-korean`            |
| 글자 수 세기                 | "이 자기소개서 공백 포함 몇 자야? 1,000자 제한이야."      | `/korean-writing:korean-character-count`     |
| README 쓰기                  | "이 프로젝트 README 써줘. 오픈소스용으로."                | `/korean-writing:crafting-effective-readmes` |

평소 답변은 부를 것이 없습니다. 세션이 열릴 때 규칙이 이미 들어가 있습니다.

윤문 스킬은 고친 글과 함께 변경률 추정과 등급 A~~D를 한 줄로 붙이고, 주요 교정 3~~6개를 전 → 후로 보여 줍니다. 변경률이 50%를 넘으면 결과를 내놓지 않고 그 사실을 알립니다. 그 정도면 윤문이 아니라 재작성이기 때문입니다.

글자 수 스킬은 스크립트를 돌립니다. 이모지가 든 두 줄짜리 문장을 실제로 넣은 출력입니다.

```
$ node skills/korean-character-count/scripts/korean_character_count.js --text "옵션 변경은 어드민에서 바로 할 수 있습니다.
정원이 찬 옵션은 회색으로 막힙니다 🙂" --format text
profile: default
characters: 47
characters_without_whitespace: 35
code_points: 47
utf16_code_units: 48
lines: 2
bytes_utf8: 116
bytes_neis: 117
```

검사 훅은 `.md`를 저장할 때 돕니다. 정답 데이터의 승패 문장과 줄표 문장을 편집분으로 넣었을 때 stderr에 실제로 나온 출력입니다.

```
[korean-writing] 배포-지연.md 에 AI 티 패턴이 있다. 편집은 그대로 두었으니 확인하고 고쳐라.
  K1  줄표(—) 삽입구 4개 — 쉼표나 문장 분리로 바꾼다. 한국어에서 가장 강한 AI 티다
  K6  승패 의인화 2회 — 우선한다·따른다·앞선다 로 직결한다
  교정 규칙은 korean-writing 스킬에 있다. 격식 문서(계약·약관·법률)면 파일 머리에 <!-- korean-writing: ignore --> 를 넣으면 다시 알리지 않는다.
```

파일은 그대로 남습니다. Claude Code가 이 출력을 받아 고치고, 사람은 그 결과를 봅니다. 써 둔 문서를 한꺼번에 검사하려면 `scripts/check.sh 파일...`을 씁니다. 훅과 같은 기준으로 보고, 걸린 파일이 있으면 종료 코드 1을 냅니다.

끄는 범위는 넷입니다.

| 범위          | 방법                                                                                                     |
| ------------- | -------------------------------------------------------------------------------------------------------- |
| 파일 하나     | 파일 머리에 `<!-- korean-writing: ignore -->`. 계약서나 나쁜 예 모음처럼 매번 걸리는 게 맞지 않는 파일용 |
| 세션 전체     | `KOREAN_WRITING_HOOK_DISABLED=1`. 훅 둘을 모두 끕니다                                                    |
| 상시 규칙만   | `KOREAN_WRITING_ALWAYS_ON_DISABLED=1`                                                                    |
| 플러그인 전체 | `claude plugin disable korean-writing`                                                                   |

## 안에 무엇이 있나

### 상시 규칙

스킬은 글을 써 달라고 할 때만 뜨고 검사 훅은 파일에만 걸립니다. 그 사이에 남는 것이 하루 중 가장 양이 많은 평소 답변인데, SessionStart 훅이 그것을 맡습니다. 세션이 시작·재개·`/clear`·압축될 때마다 `hooks-handlers/always-on.md`를 한 번 컨텍스트에 넣습니다. 압축 뒤에 다시 넣는 이유는 앞쪽 컨텍스트가 잘려도 규칙이 남아야 하기 때문입니다.

규칙은 열 줄입니다. 평소대로 존댓말로 답한다, 주어는 사람이나 조직으로 둔다, 영어에서 온 비유는 버리고 서술한다, 줄표 삽입구와 첫째·둘째 병렬과 이모지를 쓰지 않는다, 번역투와 AI 관용구를 쓰지 않는다, 문장 길이를 섞고 한 문체로 간다, 격식과 사실은 그대로 두고 코드·인용·고유명사는 손대지 않는다, 글 작성 요청이면 `korean-writing` 스킬을 먼저 로드한다.

크기는 1.4KB, 한글 371자, 약 660토큰입니다. 프롬프트 캐시에 들어가 턴마다 다시 들지 않습니다. 이 훅은 무엇도 막지 않습니다. 규칙 파일이 없거나 읽히지 않아도 종료 코드 0으로 끝납니다. 회귀 테스트 20건이 주입 내용, 규칙 항목 아홉 개, 한글 400자 상한, 끄기 두 종, 안전 종료를 확인합니다.

### korean-writing 스킬

글을 써 달라는 요청에 뜹니다. 슬랙·메일·공지, 보고서, 릴리스 노트, 커밋 메시지, README·기획 문서, 회의록·작업 메모까지, 남에게 보내든 안에서 보든 가리지 않습니다. 코드만 쓰는 작업은 대상이 아닙니다.

핵심은 한 줄입니다. 사람이 말하듯 쓴다, 영어 문장을 옮긴 티가 나면 실패다. 다 쓰고 고치는 것이 아니라 처음 쓸 때부터 그렇게 씁니다. 다 쓰고 고치려 들면 구조가 이미 번역투로 잡혀 있어 안 고쳐지기 때문입니다.

원칙은 다섯입니다. 처음부터 깨끗하게 쓴다. 기계성만 걷어내고 격식·전문성·장르·논지·사실은 그대로 둔다. 원문에 없던 비유나 수사를 넣지 않는다. 다 쓰고도 미달이면 `humanize-korean`으로 보정한다. 어떤 모델로 쓸지는 이 규칙이 정하지 않는다.

문장 규칙은 일곱입니다. 주어는 사람이나 조직으로 둔다. 한국어에 실제로 있는 비유만 쓴다. 구조를 은유로 설명하지 않는다. 승패로 비유하지 않는다. `것` 구문을 줄인다. 한 문체로 끝까지 간다. 문장 길이를 섞는다. 서식 규칙은 줄표 삽입구를 한 문서에 두 번까지, 불릿은 정말 목록일 때만, 기계적 병렬은 피하고, 이모지는 슬랙 인사말 정도로만 두는 것입니다.

보내기 전 점검은 넷입니다. 줄표가 세 개 이상인가, `축`·`갈래`·`결`·`레이어`가 합쳐 세 번 이상인가, 사물이 사람처럼 행동하는가, 소리 내어 읽어 걸리는 데가 있는가. 마지막이 제일 중요합니다. 계약서·약관·법률 문서·공문은 격식이 요건이라 예외이고, 코드·로그·명령어·직접 인용·고유명사·영어 원문도 손대지 않습니다.

### humanize-korean 스킬

이미 써 둔 글에서 번역투와 AI 관용구를 걷어냅니다. "AI 티 없애줘", "번역투 고쳐줘", "이 글 다듬어줘" 같은 요청에 뜹니다. 아직 쓰지 않은 글은 이 스킬이 아니라 `korean-writing`이 맡습니다.

절차는 한 번에 끝납니다. 글을 읽고, 압축 룰북 `references/quick-rules.md`로 훑고, 애매한 것만 규칙집에서 확인하고, 찾은 구간만 고치고, 자기 점검을 돌리고, 돌려줍니다. 한글 5,000자가 넘으면 논리 단위로 나눠 돌리고, 8,000자가 넘거나 정확도가 특히 중요한 글은 단일 패스로 부족하다고 알립니다.

철칙은 넷이고 어기면 되돌립니다. 사실·주장·숫자·날짜·고유명사·인용은 100% 보존한다. 룰북이나 규칙집의 패턴에 걸리는 구간만 손댄다. 장르와 문체는 그대로 둔다. 변경률 30%를 넘으면 경고하고 50%를 넘으면 결과를 내놓지 않는다.

이 스킬의 목적은 어색한 번역투를 자연스러운 한국어로 고치는 것입니다. AI 탐지기 우회가 아니고, 그렇게 설명하지도 않습니다.

### korean-character-count 스킬

"500자 이내로", "글자 수 세줘", "자소서 분량 맞춰줘"처럼 길이 제한이 걸린 글에 뜹니다. 한국어는 세는 기준에 따라 숫자가 달라집니다. `각`은 한 글자지만 UTF-8로 3바이트이고, 조합형 자모는 눈에는 한 글자인데 코드포인트로는 셋입니다. 그래서 모델이 추정하지 않고 스크립트가 셉니다.

사람이 세는 방식에 가장 가까운 값은 `characters`(grapheme cluster)입니다. 공백 제외를 명시한 폼이면 `characters_without_whitespace`, 교육행정시스템 양식이면 `--profile neis`의 `bytes_neis`, DB 컬럼 길이면 `bytes_utf8`을 씁니다. Node 18 이상이 필요하고 `node:fs` 외의 패키지는 쓰지 않습니다. 세는 규칙의 계약은 `skills/korean-character-count/instruction.md`에 있습니다.

### crafting-effective-readmes 스킬

README를 만들거나 고쳐 달라는 요청에 뜹니다. 무슨 작업인지 먼저 가립니다. 새로 만들기, 절 추가, 갱신, 점검. 그다음 프로젝트 유형을 고릅니다. 오픈소스, 개인, 사내, 설정 저장소 넷이고 유형마다 템플릿과 절 체크리스트가 있습니다. 어느 README든 이름, 한두 문장의 설명, 사용법은 반드시 둡니다. 절 구성은 이 스킬이 잡고 문장은 `korean-writing` 규칙으로 씁니다.

### 검사 훅

`Edit`, `Write`, `MultiEdit`가 `.md` 파일을 고친 직후에 돕니다. 파일 전체가 아니라 이번에 쓴 부분만 봅니다. 전체를 보면 예전 표현이 편집마다 다시 걸려 소음이 되기 때문입니다. 판정 방법은 다음 절에 있습니다.

### 스크립트

| 스크립트             | 하는 일                                                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/check.sh`   | 파일을 통째로 훅에 넣어 검사합니다. 써 둔 문서를 점검하거나 CI·pre-commit에서 씁니다. 걸린 파일이 있으면 종료 코드 1                  |
| `scripts/measure.sh` | 디렉터리 아래 한국어 `.md`를 전부 훅에 넣어 걸린 파일과 코드별 수를 냅니다. 걸린 파일이 사람 글인지 Claude 글인지는 사람이 판단합니다 |
| `scripts/release.sh` | 버전 하나로 `plugin.json`, README 배지, CHANGELOG를 맞추고 커밋과 태그를 만듭니다. `--push`면 push와 GitHub 릴리스까지                |

```bash
scripts/check.sh docs/*.md        # 걸린 파일이 있으면 exit 1
scripts/measure.sh ~/Documents    # 실제 문서 뭉치의 오탐 측정
```

## 검사 훅의 판정

훅은 이 순서로 판정합니다.

1. `Edit`·`Write`·`MultiEdit`가 끝나면 Claude Code가 `hooks-handlers/posttooluse.sh`에 도구 입력 JSON을 stdin으로 넘깁니다.
2. `KOREAN_WRITING_HOOK_DISABLED=1`이거나 `python3`가 없으면 통과합니다.
3. 경로가 `.md`가 아니면 통과합니다.
4. 이번에 쓴 부분(`content`, `new_string`, `edits[].new_string`)을 모읍니다. 그 안이나 파일 머리 4,000자 안에 `korean-writing: ignore`가 있으면 통과합니다.
5. 코드블록(``` 과 ~~~), 인라인 코드, URL, 표 행, HTML 주석을 걷어냅니다. 표를 통째로 빼는 이유는 나쁜 예를 인용하는 문서가 그 예 때문에 걸리면 안 되기 때문입니다.
6. 남은 본문의 한글 비중이 30% 이상이면 전체를 보고, 미만이면 한글 비중 30% 이상인 줄만 남깁니다. 영어 문서 안의 한국어 문단을 놓치지 않기 위해서입니다. 남은 한글이 20자 미만이면 통과합니다.
7. `K1`부터 `K8`까지 정규식을 돌립니다.
8. 걸린 것이 없으면 종료 코드 0입니다. 있으면 stderr에 항목과 고치는 법을 쓰고 종료 코드 2입니다. 파일은 그대로입니다.

| 코드 | 무엇을           | 정규식이 보는 것                                                                    | 걸리는 시점                                     |
| ---- | ---------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------- |
| `K1` | 줄표 삽입구      | 양쪽에 공백과 글자가 있는 `—`·`–`                                                   | 4개. 이번 편집에 하나라도 있으면 파일 전체로 셈 |
| `K2` | 추상 구조어      | `축이·축은·축을·축으로`, `갈래`, `결이 다르`, `레이어`                              | 3회                                             |
| `K3` | 번역투 `것` 구문 | `것들이었다`, `것들을`, `하는 것이 가능`                                            | 1회                                             |
| `K4` | AI 관용구        | `결론적으로`, `종합하면`, `시사하는 바가 크`, `혁신적`, `압도적` 등                 | 1회                                             |
| `K5` | 기계적 병렬      | `첫째,`와 `둘째,`                                                                   | 둘이 함께 나올 때                               |
| `K6` | 승패 의인화      | `~가 이긴다·이깁니다·이겼다·이기고`                                                 | 2회                                             |
| `K7` | 사물 의인화      | 화면·서버·장비 등이 `굳·쓰러지·넘어지·일어서·잠들`, `넘어뜨리·일으켜 세우·쓰러뜨리` | 1회                                             |
| `K8` | 번역투           | `가지고 있`, 이중 피동 `되어지·지게 된다`, `에 의해`                                | 항목별로 1회, `에 의해`는 2회                   |

줄표만은 파일 전체를 봅니다. 문단 하나씩 고치는 동안 파일에 줄표가 쌓여도 편집분만 세면 한 번도 안 걸리기 때문입니다. 이번 편집에 줄표가 하나라도 있으면 파일을 읽어 같은 규칙으로 전체 개수를 세고, 이번 편집에 없으면 파일에 아무리 많아도 잡지 않습니다.

임계는 규칙집보다 한 단계 느슨합니다. 규칙집이 "한 문서에 1회 이하"라고 하면 훅은 2회부터 잡습니다. 막는 장치가 아니라 알리는 장치라서, 오탐으로 작업을 방해하는 쪽이 더 나쁘기 때문입니다.

## 정한 원칙

**생성 단계에서 잡습니다.** 사후 검사는 보조 수단입니다. 세션 시작에 규칙을 넣고 글 작성 요청에 스킬을 붙이는 이유가 이것입니다. 검사 훅은 그 둘을 빠져나온 것을 잡는 마지막 그물입니다.

**아무것도 막지 않습니다.** 검사 훅은 알리기만 하고 편집을 되돌리지 않습니다. 주입 훅은 어떤 경우에도 종료 코드 0입니다. `python3`가 없으면 검사 없이 통과합니다. 검사기가 작업을 막는 순간 사람이 검사기를 끄기 때문입니다.

**실측 없이 규칙을 만지지 않습니다.** 패턴을 넣거나 빼거나 임계를 조정할 때는 숫자가 있어야 합니다. 그렇게 고친 기록 열세 건이 [`EVALUATION.md`](./EVALUATION.md)에 있습니다. 승패 의인화는 규칙집보다 엄격해서 임계를 1에서 2로 올렸습니다. 사물 의인화에서 "죽다"는 서버가 죽다, 프로세스가 죽다처럼 개발자가 늘 쓰는 말이라 뺐습니다. 번역투의 `~에 대해`·`~를 통해` 횟수는 실제 문서에서 사람이 쓴 글만 잡아서 뺐습니다.

**오탐이 미탐보다 나쁩니다.** 합격 기준에서 정상 문장 오탐 0건이 위반 검출 10건보다 앞에 옵니다. 실제 문서 143개를 넣었을 때 사람이 쓴 글이 걸린 것은 1개입니다.

**네트워크를 쓰지 않습니다.** [SECURITY.md](./SECURITY.md)에 훅이 무엇을 읽고 무엇을 하지 않는지, 그리고 그것을 직접 확인하는 `grep` 명령 세 개가 있습니다.

**비용은 층으로 나눕니다.** 평소에는 상시 규칙과 스킬 설명만 읽히고 큰 파일은 필요할 때만 엽니다.

```
hooks-handlers/always-on.md     1.4 KB   세션마다 한 번
SKILL.md                        8.0 KB   글 작성 요청에
references/quick-rules.md       9.7 KB   윤문을 시작할 때
references/taxonomy.md         66   KB   판정이 애매한 항목 하나를 볼 때
```

**가져온 파일은 손대지 않습니다.** 규칙집, 압축 룰북, README 스킬, 글자 수 스크립트는 다른 MIT 프로젝트에서 왔습니다. 무엇을 어디서 가져와 어디를 고쳤는지 [`NOTICE.md`](./NOTICE.md)에 파일별로 적혀 있습니다.

## 얼마나 믿을 수 있나

[`EVALUATION.md`](./EVALUATION.md)가 합격 기준과 측정 결과를 적습니다. 기준은 여섯 묶음입니다. 훅 정확도, 스킬 트리거, 스킬 내용 유효성, 구조 건전성, 실패 모드, 사용하는 사람의 기준. 하나라도 미달이면 고칩니다.

| 측정                      | 결과                                       |
| ------------------------- | ------------------------------------------ |
| 위반 문장 검출            | 10 / 10                                    |
| 정상 문장 오탐            | 0 / 5                                      |
| 실제 문서 오탐            | 1 / 143 (0.7%)                             |
| 검출된 항목의 코드 정확도 | 10 / 10                                    |
| 글 작성 요청 트리거       | 5 / 5, 코드 작업 오매칭 0 / 5              |
| 변이 테스트               | 심은 결함 15 / 15 검출                     |
| 상시 규칙 주입 효과       | 블라인드 24쌍에서 21승 0패 3무             |
| 상시 컨텍스트 비용        | 약 950토큰 (스킬 설명 290 + 상시 규칙 659) |
| 외부 네트워크 호출        | 0                                          |
| 회귀 테스트               | 63 / 63                                    |

실제 문서 오탐은 이 플러그인과 무관하게 한 컴퓨터에 쌓여 있던 한국어 `.md` 143개를 통째로 넣어 쟀습니다. 60개가 걸렸는데 59개는 2026년에 Claude가 쓴 구현 로그·QA 보고서·CLAUDE.md였고, 사람이 쓴 문서는 1개였습니다. 규칙을 고치기 전에는 사람 글 7개(4.9%)가 걸렸습니다.

상시 규칙의 효과는 함수 설명, 에러 진단, PR 리뷰 같은 프롬프트 12개로 쟀습니다. 주입 유무 두 조건으로 48건을 생성하고 같은 모델이 순서를 바꿔 두 번씩 블라인드로 판정했습니다. 24쌍에서 주입 쪽이 21승 3무였고 12개 프롬프트 전부에서 이기거나 비겼습니다. 문체를 빼고 기술 오류만 따로 본 검사에서 심각한 오류는 양쪽 0건입니다.

스킬 유무는 같은 프롬프트 4개로 비교했습니다. 2026-09-10의 claude-opus-5에서는 두 조건 모두 훅을 통과해 생성 단계 효과를 이 표본으로 구분하지 못했습니다. 이 결과도 그대로 적어 두었습니다.

로컬에서 같은 검사를 돌리는 명령입니다.

```bash
python3 hooks-handlers/test_posttooluse.py     # 검사 훅 회귀 43건
python3 hooks-handlers/test_sessionstart.py    # 상시 규칙 회귀 20건
scripts/check.sh README.md CLAUDE.md           # 문서가 자기 훅을 통과하는가
scripts/measure.sh ~/Documents                 # 실제 문서 뭉치의 오탐
```

GitHub Actions가 push와 PR마다 macOS와 Linux 양쪽에서 매니페스트·이슈 양식 문법, 훅 실행 비트, 회귀 테스트 둘, 한국어 문서 13종의 자기 훅 통과, 글자 수 스모크를 돌립니다. 여기에 shellcheck, `plugin.json`·README 배지·CHANGELOG의 버전 일치, `claude plugin validate`가 붙습니다.

## 하지 않는 것

- 검사 훅은 `.md` 파일만 봅니다. 코드 안의 한국어 주석과 문자열, 슬랙으로 바로 나가는 답변은 생성 단계의 상시 규칙과 스킬이 맡고 사후 검사는 없습니다.
- 정규식은 알려진 패턴 여덟 종만 잡습니다. 새로운 어색함은 사람이 찾아 넣어야 합니다.
- 상시 규칙의 효과 측정은 단일 턴이었습니다. 긴 대화에서 효과가 약해지는지, 서브에이전트 세션에도 주입이 전파되는지는 재지 않았습니다.
- 계약서, 약관, 법률 문서, 공문처럼 격식이 요건인 글은 대상이 아닙니다. 코드, 로그, 명령어, 직접 인용, 고유명사, 영어 원문도 손대지 않습니다.
- 맞춤법과 띄어쓰기는 보지 않습니다. 문체만 봅니다.

## 저장소 구성

```
korean-writing/
├── .claude-plugin/
│   ├── plugin.json                   매니페스트. 이름, 버전(정본), 스킬 경로 넷
│   └── marketplace.json              마켓플레이스 카탈로그. 버전은 두지 않습니다
├── hooks/hooks.json                  SessionStart 와 PostToolUse 등록. 각 10초 제한
├── hooks-handlers/
│   ├── always-on.md                  세션마다 주입되는 답변용 규칙 열 줄
│   ├── sessionstart.sh               주입 본체. 언제나 exit 0
│   ├── posttooluse.sh                검사 본체. bash 안의 python3 정규식 K1~K8
│   ├── ground-truth.json             실제로 생성됐던 위반 문장 10건
│   ├── clean.json                    같은 맥락의 정상 문장 5건
│   ├── test_posttooluse.py           검사 훅 회귀 43건. 보고 횟수까지 검증합니다
│   └── test_sessionstart.py          상시 규칙 회귀 20건
├── SKILL.md                          korean-writing 스킬
├── references/
│   ├── quick-rules.md                윤문 첫 패스용 압축 룰북
│   └── taxonomy.md                   AI 티 분류 체계. 10분류 73항목
├── skills/
│   ├── humanize-korean/SKILL.md      윤문 스킬
│   ├── korean-character-count/       글자 수 스킬. SKILL.md, instruction.md, scripts/
│   └── crafting-effective-readmes/   README 구조 스킬. 템플릿 4종, 참고 문서 5종
├── scripts/
│   ├── check.sh                      파일 통째 검사
│   ├── measure.sh                    실제 문서 뭉치 오탐 측정
│   └── release.sh                    버전·CHANGELOG·배지·태그·릴리스
├── docs/                             배너(한·영, 밝음·어두움), 훅 출력 데모, 소셜 프리뷰
├── .github/                          CI 워크플로, 이슈 양식 3종, PR 양식, CODEOWNERS, dependabot
├── .claude/settings.json             기여자용 프로젝트 설정
├── .gitattributes                    셸 스크립트 LF 고정
├── EVALUATION.md                     합격 기준, 측정 결과, 측정 중 고친 것
├── CHANGELOG.md                      릴리스 노트
├── CLAUDE.md                         이 저장소에서 작업하는 Claude 의 규칙
├── CONTRIBUTING.md · .en.md          기여 안내
├── CODE_OF_CONDUCT.md                행동 강령
├── SECURITY.md                       보안 정책과 훅이 하는 일
├── NOTICE.md                         가져온 파일의 출처와 수정 범위
├── LICENSE                           MIT
└── README.md · README.en.md
```

## 다른 도구와 비교

| 도구                                                        | 무엇인가                                                                                                            | 이 플러그인과의 관계                                                                                                                       |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| [im-not-ai](https://github.com/epoko77-ai/im-not-ai)        | 이미 쓴 한글에서 AI 티를 걷어내는 윤문 스킬. 진단·윤문·마무리를 나눈 다중 호출 파이프라인이고 여러 CLI를 지원합니다 | 규칙집의 원본입니다. 이 플러그인은 처음 쓸 때와 평소 답변에 무게를 두고 윤문은 단일 패스입니다                                             |
| [claude-forge](https://github.com/sangrokjung/claude-forge) | 에이전트·커맨드·훅·규칙을 묶은 Claude Code 프레임워크. 한국어 산문 가드레일은 그중 한 부분입니다                    | 윤문 스킬과 압축 룰북, 줄표 훅의 발동 조건을 가져왔습니다. Forge를 전체 설치했다면 이 플러그인은 필요 없고, 같이 쓰면 줄표 검사가 겹칩니다 |
| [k-skill](https://github.com/NomaDamas/k-skill)             | 한국인을 위한 스킬 모음. 글자 수부터 교통·날씨·검색까지                                                             | 글자 수 스크립트를 가져왔습니다. 맞춤법 검사 스킬은 원문을 외부 서버로 보내서 가져오지 않았습니다                                          |
| 맞춤법·띄어쓰기 검사기                                      | 맞춤법을 봅니다                                                                                                     | 이 플러그인은 문체만 봅니다. 겹치지 않으니 같이 쓰면 됩니다                                                                                |

## 자주 하는 질문

<details>
<summary><b>왜 검사 훅은 .md 파일만 보나요?</b></summary>

훅은 파일 편집 도구가 끝난 뒤에 도구 입력을 받는 구조라 파일이 아닌 답변은 볼 수 없습니다. 답변은 세션 시작에 들어가는 상시 규칙과 글 작성 스킬이 생성 단계에서 맡습니다. 답변마다 다시 검토하는 Stop 훅은 토큰을 매 턴 쓰기 때문에 두지 않았습니다.

</details>

<details>
<summary><b>훅이 내 편집을 되돌리나요?</b></summary>

아닙니다. 걸린 항목을 stderr로 알리고 종료 코드 2로 끝낼 뿐입니다. 파일은 그대로 남고, 고칠지는 Claude Code와 사람이 정합니다.

</details>

<details>
<summary><b>내 글이 외부로 나가나요?</b></summary>

나가지 않습니다. 훅은 bash와 python3 정규식이고 글자 수 스크립트는 `node:fs`만 씁니다. [SECURITY.md](./SECURITY.md)의 `grep` 명령 세 개로 네트워크 호출과 외부 프로그램 실행이 없다는 것을 직접 확인할 수 있습니다. 원문을 외부 서버로 보내는 맞춤법 검사 스킬은 그래서 가져오지 않았습니다.

</details>

<details>
<summary><b>계약서나 약관을 고칠 때도 걸리나요?</b></summary>

파일 머리에 `<!-- korean-writing: ignore -->`를 넣으면 그 파일은 검사하지 않습니다. 격식이 요건인 글은 스킬의 예외이기도 합니다. 나쁜 예를 일부러 모아 둔 이 저장소의 규칙집도 같은 표시로 뺐습니다.

</details>

<details>
<summary><b>토큰을 얼마나 쓰나요?</b></summary>

상시로 드는 것은 스킬 설명 넷 약 290토큰과 세션당 한 번 들어가는 상시 규칙 약 660토큰입니다. 상시 규칙은 `claude -p`를 같은 조건으로 돌려 입력 토큰 총량을 뺀 값으로, 주입이 없으면 9,514, 있으면 10,173이었습니다. 규칙은 프롬프트 캐시에 들어가 턴마다 다시 내지 않습니다. 스킬 본문은 글 작성 요청이 있을 때만 로드되고 훅은 LLM을 부르지 않습니다.

</details>

<details>
<summary><b>설치했는데 스킬이 안 보여요.</b></summary>

`claude plugin list`에서 `korean-writing`이 `enabled`인지 봅니다. 저장소를 `~/.claude/skills/`에 링크해 두고 마켓플레이스로도 설치했다면 둘 중 하나만 두세요. 스킬 목록은 새 세션에서 갱신됩니다.

</details>

<details>
<summary><b>위반 검출 10/10이면 다 잡는다는 뜻인가요?</b></summary>

아닙니다. 그 열 건으로 패턴을 만들었으니 잡히는 것이 당연하고, 고치다 깨뜨리지 않았는지 보는 회귀용 숫자입니다. 의미 있는 숫자는 오탐 쪽입니다. 실제 문서 143개에서 사람이 쓴 글이 걸린 것은 1개입니다. 정규식은 알려진 패턴만 잡습니다.

</details>

<details>
<summary><b>Windows에서 되나요?</b></summary>

확인하지 않았습니다. 훅이 bash 스크립트라 Git Bash나 WSL이 필요합니다. `.gitattributes`가 스크립트를 LF로 고정해 두어 CRLF 체크아웃 때문에 훅이 죽는 일은 막았습니다. 돌려 본 결과를 이슈로 알려 주시면 적겠습니다.

</details>

## 기여

절차는 [CONTRIBUTING.md](./CONTRIBUTING.md)에 있습니다. 가장 값진 기여는 코드가 아니라 문장입니다. Claude Code가 쓴 어색한 한국어를 봤거나 훅이 멀쩡한 문장을 잡았다면 [어색한 문장 제보](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=awkward-sentence.yml) 양식으로 고치지 않은 원문 그대로 보내 주세요. 제보한 문장은 정답 데이터나 정상 문장에 들어가 회귀 테스트가 됩니다. 버그 신고와 판정 규칙 제안 양식도 따로 있습니다.

작업을 시작하면 기준선부터 잡습니다.

```bash
git clone https://github.com/IsthisLee/claude-korean-writing.git
cd claude-korean-writing
python3 hooks-handlers/test_posttooluse.py
python3 hooks-handlers/test_sessionstart.py
scripts/check.sh README.md CLAUDE.md
```

판정 규칙을 넣거나 빼거나 임계를 조정하는 변경은 `scripts/measure.sh`로 실제 문서에 돌린 숫자와 회귀 테스트를 함께 보냅니다. 한국어 문서를 고쳤으면 `scripts/check.sh`를 통과시키고, README는 한국어판과 영어판을 같이 고칩니다. 커밋은 Conventional Commits에 한국어 제목이고 버전은 손대지 않습니다. 참여하는 사람은 [행동 강령](./CODE_OF_CONDUCT.md)을 따르고, 보안 문제는 공개 이슈 대신 [SECURITY.md](./SECURITY.md)의 절차로 보냅니다.

## 릴리스

[SemVer](https://semver.org/lang/ko/)를 따르고 버전의 정본은 `.claude-plugin/plugin.json` 한 곳입니다. 마켓플레이스 항목에도 버전이 있으면 `plugin.json`이 우선하므로 `marketplace.json`에는 두지 않습니다.

`scripts/release.sh <버전>`이 순서대로 합니다. 작업 트리가 깨끗한지와 버전 형식을 검사하고, CHANGELOG의 `[Unreleased]`를 새 버전 절로 옮기고, 두 README 상단 인용구에 그 버전이 적혀 있는지 확인하고, `plugin.json`과 README 배지를 올리고, 회귀 테스트와 `claude plugin validate`를 돌리고, 커밋과 주석 태그를 만듭니다. `--push`를 붙이면 push와 GitHub 릴리스까지 합니다.

```bash
scripts/release.sh 1.1.0
scripts/release.sh 1.1.0 --push
```

## 출처와 라이선스

| 파일                                 | 어디서                                                                                                                                                          | 고친 것                                                     |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `references/taxonomy.md`             | [im-not-ai](https://github.com/epoko77-ai/im-not-ai). [claude-forge](https://github.com/sangrokjung/claude-forge)를 거쳐 왔고 Forge가 D-8·D-9와 J-3 상향을 더함 | 머리에 훅 제외 표시 한 줄                                   |
| `references/quick-rules.md`          | claude-forge                                                                                                                                                    | 없는 파일을 가리키던 경로 두 곳                             |
| `skills/humanize-korean/SKILL.md`    | claude-forge                                                                                                                                                    | 한국어로 옮기고 구조 정리. 절차와 철칙은 원본과 같음        |
| `hooks-handlers/posttooluse.sh`      | claude-forge의 줄표 훅                                                                                                                                          | 발동 조건과 K1 정규식만 가져오고 나머지는 여기서 씀         |
| `skills/korean-character-count/`     | [k-skill](https://github.com/NomaDamas/k-skill)                                                                                                                 | 스크립트는 그대로, 설명서는 실행 경로만, SKILL.md는 다시 씀 |
| `skills/crafting-effective-readmes/` | [agent-toolkit](https://github.com/softaworks/agent-toolkit). 원 저작은 [agent-skills](https://github.com/joshuadavidthomas/agent-skills)                       | 관련 스킬을 가리키는 한 줄씩                                |

`korean-writing` 스킬, 상시 규칙, 검사 훅의 `K2`~`K8`, 정답 데이터와 검증 기준은 이 저장소에서 썼습니다. 가져온 파일은 모두 MIT이고 원 저작권 표시는 [`NOTICE.md`](./NOTICE.md)에 있습니다. 이 저장소도 [MIT](./LICENSE)입니다.
