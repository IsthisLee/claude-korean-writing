<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/banner-light.svg">
  <img src="docs/banner.svg" alt="korean-writing" width="100%">
</picture>

<p align="center">
  <strong>한국어</strong> · <a href="README.en.md">English</a>
</p>

<p align="center">
  <strong>Claude Code가 쓰는 모든 한국어의 품질 향상을 맡는 플러그인.</strong><br>
  평소 답변에는 규칙이 들어가고, 글은 첫 줄부터 사람이 쓴 것처럼 나오고, .md 파일은 저장하는 순간 검사받습니다.<br>
  원문은 이 컴퓨터를 떠나지 않습니다.
</p>

<p align="center">
  <a href="https://github.com/IsthisLee/claude-korean-writing/actions/workflows/validate.yml"><img alt="Validate" src="https://github.com/IsthisLee/claude-korean-writing/actions/workflows/validate.yml/badge.svg?branch=main"></a>
  <img alt="MIT" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Claude Code Plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2">
  <img alt="version" src="https://img.shields.io/badge/version-1.1.0-lightgrey">
  <img alt="network" src="https://img.shields.io/badge/network-none-success">
  <img alt="platform" src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey">
  <a href="https://github.com/IsthisLee/claude-korean-writing/commits/main"><img alt="last commit" src="https://img.shields.io/github/last-commit/IsthisLee/claude-korean-writing"></a>
</p>

<p align="center">
  <a href="#어떤-플러그인인가">소개</a> ·
  <a href="#실제로-보면">실제로 보면</a> ·
  <a href="#3분-안에-해-보기">3분 시작</a> ·
  <a href="#설치">설치</a> ·
  <a href="#부탁하는-법">쓰는 법</a> ·
  <a href="#구성-요소">구성</a> ·
  <a href="#판정-규칙">판정 규칙</a> ·
  <a href="#검증">검증</a> ·
  <a href="#자주-묻는-질문">FAQ</a>
</p>

> **v1.1.0**: 평소 답변까지 맡습니다. 세션이 열릴 때 답변용 규칙을 넣는 훅을 더했고, 규칙집 둘을 원본의 새 판으로 갈아 끼웠습니다. 블라인드 판정 24쌍에서 21승 3무 0패, 30턴 뒤에도 4승 0패입니다. 상세: [CHANGELOG.md](CHANGELOG.md)

> **korean-writing은 Claude Code가 쓰는 한국어를 사람이 쓴 것처럼 만듭니다.** 설치만 하면 평소 답변부터 규칙이 붙습니다. **"운영팀에 보낼 안내문 써줘"**라고 하면 스킬이 스스로 뜨고, `.md` 파일을 저장하면 훅이 번역투와 AI 관용구를 짚어 줍니다.

## 어떤 플러그인인가

Claude Code의 한국어는 문법이 틀리지 않습니다. 그런데도 읽으면 눈에 걸립니다. 영어 문장을 그대로 옮긴 어순, 영어에서 건너온 비유, 어느 문서에서나 같은 자리에 나오는 상투구 때문입니다. 실제 문서 143개를 훅에 넣었을 때 걸린 60개 중 59개가 Claude가 쓴 문서였고, 대부분 줄표 삽입구였습니다.

이 플러그인은 그 한국어가 만들어지는 자리마다 하나씩 붙습니다. 세션이 열리면 답변용 규칙이 들어가고, 글을 부탁하면 처음부터 규칙대로 쓰는 스킬이 뜨고, 써 둔 글을 다듬어 달라면 사실은 두고 문체만 손보는 스킬이 뜨고, `.md`를 저장하면 훅이 방금 쓴 부분을 검사합니다. 글자 수는 모델이 어림하지 않고 스크립트가 세고, README는 절 구성을 잡는 스킬이 먼저 나섭니다.

> 코드에 붙는 린터를 한국어 산문에 붙인 것과 같습니다. 다만 고쳐 주지는 않고 짚어만 줍니다. 고칠지는 사람이 정합니다.

| 구성        | 수     | 무엇                                                                                            |
| ----------- | ------ | ----------------------------------------------------------------------------------------------- |
| 스킬        | 4      | `korean-writing`, `humanize-korean`, `korean-character-count`, `crafting-effective-readmes`     |
| 훅          | 2      | 세션 시작에 규칙 주입, `.md` 편집 직후 검사                                                     |
| 검사 패턴   | 8      | `K1`~`K8`. 줄표, 추상 구조어, 것 구문, AI 관용구, 기계적 병렬, 승패 의인화, 사물 의인화, 번역투 |
| 규칙집      | 84항목 | im-not-ai의 분류 체계. 10분류, 항목마다 심각도와 처방                                           |
| 정답 데이터 | 15문장 | Claude Code가 실제로 생성한 위반 10건, 같은 맥락의 정상 5건                                     |
| 회귀 테스트 | 63건   | 검사 훅 43, 상시 규칙 20                                                                        |
| 스크립트    | 4      | 글자 수, 통째 검사, 오탐 측정, 릴리스                                                           |
| 네트워크    | 없음   | 훅은 bash와 python3 정규식, 글자 수는 `node:fs`                                                 |

## 실제로 보면

`.md` 파일을 고쳤을 때 Claude Code 화면에 나오는 모습입니다. 화면 틀은 그린 것이고, 노란 줄부터는 훅이 실제로 낸 출력 그대로입니다.

<p align="center"><img src="docs/hook-output.svg" alt="훅이 K1·K2·K3·K4·K7을 잡은 실제 출력" width="860"></p>

정답 데이터의 승패 문장과 줄표 문장을 편집분으로 넣었을 때 훅이 stderr에 낸 원문입니다.

```
[korean-writing] 배포-지연.md 에 AI 티 패턴이 있다. 편집은 그대로 두었으니 확인하고 고쳐라.
  K1  줄표(—) 삽입구 4개 — 쉼표나 문장 분리로 바꾼다. 한국어에서 가장 강한 AI 티다
  K6  승패 의인화 2회 — 우선한다·따른다·앞선다 로 직결한다
  교정 규칙은 korean-writing 스킬에 있다. 격식 문서(계약·약관·법률)면 파일 머리에 <!-- korean-writing: ignore --> 를 넣으면 다시 알리지 않는다.
```

글자 수 스킬이 돌리는 스크립트의 실제 출력입니다. 이모지가 든 두 줄짜리 문장을 넣었습니다.

```
$ node skills/korean-character-count/scripts/korean_character_count.js --text "옵션 변경은 어드민에서 바로 할 수 있습니다.
정원이 찬 옵션은 회색으로 막힙니다 🙂" --format text
profile: default
characters: 47
characters_without_whitespace: 35
code_points: 47
utf16_code_units: 48
lines: 2
bytes: 116
bytes_utf8: 116
bytes_neis: 117
character_contract: Unicode extended grapheme clusters via Intl.Segmenter
byte_contract: Actual UTF-8 encoded byte length
line_contract: Empty string => 0 lines; otherwise count CRLF, LF, CR, U+2028, U+2029 as one line break each and add 1
```

규칙이 잡는 문장이 어떤 것인지는 정답 데이터 넷으로 보면 됩니다. 전부 Claude Code가 실제로 썼던 문장입니다.

> 규칙이 충돌하면 상위 문서가 **이깁니다**. 둘 다 값이 있을 때는 텍스트가 **이기고** 강의실 참조는 무시됩니다.

문서와 설정은 서로 겨루지 않습니다. 우선한다, 따른다라고 씁니다. 사건이나 개념을 사람처럼 움직이게 하는 습관이고, im-not-ai 분류로는 D-5 의인화된 추상 주어에 듭니다.

> 원인은 힙 부족이 아니었습니다 **—** 실측해보니 **—** 설정이 아예 먹히지 않았습니다.

줄표로 끼워 넣는 삽입구는 영어 문장 부호를 그대로 옮긴 것입니다. 실제 문서 143개에서 걸린 60개 대부분이 이 패턴이었고, 줄표가 34개, 66개, 207개 든 파일도 있었습니다.

> 여기서 갈리는 **축은** 프로젝트 전용 여부가 아니라 성격입니다. 두 문제는 **결이** 다르고 **레이어도** 다릅니다.

`축`, `결`, `레이어`는 구조를 비유로 말하는 버릇입니다. 기준이 다르다, 성격이 다르다, 다른 문제다라고 쓰면 그만입니다.

> 시험용 장비가 몇 초 만에 **쓰러졌습니다**. **일으켜 세우면** 또 쓰러지기를 스무 분 넘게 반복했습니다.

장비는 쓰러지지 않습니다. 멈췄고 다시 켰다고 쓰면 됩니다.

## 3분 안에 해 보기

1. 설치합니다. 명령 두 줄이고 설정할 것은 없습니다.
   ```bash
   claude plugin marketplace add IsthisLee/claude-korean-writing
   claude plugin install korean-writing
   ```
2. 새 세션을 열고 아무 글이나 부탁합니다. 스킬이 스스로 뜹니다.
   ```
   운영팀에 보낼 옵션 변경 안내문 써줘. 슬랙에 캐주얼하게.
   ```
3. 그 글을 `.md` 파일로 저장해 달라고 합니다. 훅이 방금 쓴 부분을 검사하고, 걸리는 것이 있으면 위와 같은 출력이 나옵니다. 없으면 아무 말도 하지 않습니다.

## 설치

```bash
claude plugin marketplace add IsthisLee/claude-korean-writing
claude plugin install korean-writing
```

`claude plugin list`에 `korean-writing`이 `enabled`로 보이면 됩니다. 새 버전은 `claude plugin update korean-writing`으로 받습니다. 받아 둔 저장소 경로를 마켓플레이스로 등록해도 됩니다. 사내 사본이나 포크를 쓸 때입니다.

```bash
claude plugin marketplace add /경로/claude-korean-writing
claude plugin install korean-writing
```

| 필요한 것   | 어디에 쓰나            | 없으면                   |
| ----------- | ---------------------- | ------------------------ |
| Claude Code | 전부. 2.1.267에서 확인 |                          |
| `bash`      | 훅 둘과 스크립트 셋    | 훅이 돌지 않습니다       |
| `python3`   | 검사 훅의 판정 부분    | 검사 없이 통과합니다     |
| `node` 18+  | 글자 수 스크립트       | 그 스킬만 쓸 수 없습니다 |

따로 받는 패키지는 없습니다. CI가 macOS와 Linux에서 같은 검사를 돌리고, Windows는 Git Bash나 WSL이 필요한데 아직 돌려 보지 못했습니다.

## 부탁하는 법

평소처럼 말하면 됩니다. 스킬은 요청을 보고 스스로 뜹니다. 아래 문장은 그대로 붙여 써도 됩니다.

```
운영팀에 보낼 옵션 변경 안내문 써줘. 슬랙에 캐주얼하게.
아래 글 번역투만 고쳐줘. 사실과 숫자는 그대로 두고.
이 자기소개서 공백 포함 몇 자야? 1,000자 제한이야.
이 프로젝트 README 써줘. 오픈소스용으로.
이번 배포 QA 보고서를 배포-QA.md 로 써줘.
```

직접 부르려면 슬래시 이름을 씁니다.

| 부탁                         | 직접 부를 때                                 |
| ---------------------------- | -------------------------------------------- |
| 글을 처음부터 쓰기           | `/korean-writing`                            |
| 써 둔 글에서 번역투 걷어내기 | `/korean-writing:humanize-korean`            |
| 글자 수 세기                 | `/korean-writing:korean-character-count`     |
| README 쓰기                  | `/korean-writing:crafting-effective-readmes` |

평소 답변에는 부를 이름이 없습니다. 세션이 열리는 순간 규칙이 먼저 들어가 있기 때문입니다.

윤문을 맡기면 고친 글 위에 한 줄 상태가 붙습니다. 변경률 추정과 A부터 D까지의 등급입니다. 그 아래에 주요 교정 서너 개에서 여섯 개를 전과 후로 나란히 보여 줍니다. 변경률이 절반을 넘으면 결과 대신 그 사실만 알립니다. 절반 넘게 바뀐 글은 윤문이 아니라 재작성입니다.

써 둔 문서를 한꺼번에 검사하려면 `scripts/check.sh 파일...`을 씁니다. 훅과 같은 기준으로 보고, 걸린 파일이 있으면 종료 코드 1을 냅니다. CI와 pre-commit에 그대로 씁니다.

끄는 방법은 범위에 따라 넷입니다.

| 범위          | 방법                                                                                                     |
| ------------- | -------------------------------------------------------------------------------------------------------- |
| 파일 하나     | 파일 머리에 `<!-- korean-writing: ignore -->`. 계약서나 나쁜 예 모음처럼 매번 걸리는 게 맞지 않는 파일용 |
| 세션 전체     | `KOREAN_WRITING_HOOK_DISABLED=1`. 훅 둘을 모두 끕니다                                                    |
| 상시 규칙만   | `KOREAN_WRITING_ALWAYS_ON_DISABLED=1`                                                                    |
| 플러그인 전체 | `claude plugin disable korean-writing`                                                                   |

## 어디에 붙나

| 자리            | 담당                              | 언제 움직이나                   | 규칙이 적힌 곳                       |
| --------------- | --------------------------------- | ------------------------------- | ------------------------------------ |
| 평소 답변       | SessionStart 훅                   | 세션 시작·재개·`/clear`·압축    | `hooks-handlers/always-on.md`        |
| 글 작성 요청    | `korean-writing` 스킬             | 써 달라는 요청이 오면           | `SKILL.md`                           |
| 써 둔 글 다듬기 | `humanize-korean` 스킬            | 다듬어 달라는 요청이 오면       | `skills/humanize-korean/SKILL.md`    |
| `.md` 파일 편집 | PostToolUse 훅                    | `Edit`·`Write`·`MultiEdit` 직후 | `hooks-handlers/posttooluse.sh`      |
| 글자 수 제한    | `korean-character-count` 스킬     | 몇 자인지 물으면                | `skills/korean-character-count/`     |
| README          | `crafting-effective-readmes` 스킬 | README를 만들거나 고치자고 하면 | `skills/crafting-effective-readmes/` |

## 구성 요소

### 상시 규칙

하루 동안 Claude Code가 내는 한국어의 대부분은 파일도 아니고 글 작성 요청도 아닌 평소 답변입니다. 스킬도 검사 훅도 거기에는 닿지 않습니다. SessionStart 훅이 그 빈자리를 맡습니다. 세션이 시작하거나 재개될 때, `/clear`를 했을 때, 컨텍스트가 압축됐을 때 `hooks-handlers/always-on.md`를 한 번 컨텍스트에 넣습니다. 압축 뒤에도 넣는 것은 앞쪽이 잘려 나가도 규칙은 남아 있어야 하기 때문입니다.

항목은 아홉입니다. 평소대로 존댓말로 답한다, 주어는 사람이나 조직으로 둔다, 영어에서 온 비유는 버리고 서술한다, 줄표 삽입구와 첫째·둘째 병렬과 이모지를 쓰지 않는다, 번역투와 AI 관용구를 쓰지 않는다, 문장 길이를 섞고 한 문체로 간다, 격식과 사실은 그대로 두고 코드·인용·고유명사는 손대지 않는다, 글 작성 요청이면 `korean-writing` 스킬을 먼저 로드한다.

파일은 1.4KB, 한글 371자이고 토큰으로 약 660입니다. 프롬프트 캐시에 들어가므로 턴마다 다시 내는 비용은 없습니다. 막는 일은 하지 않습니다. 규칙 파일이 없거나 읽을 수 없어도 종료 코드는 0입니다. 회귀 테스트 20건은 주입된 내용, 아홉 항목이 다 남아 있는지, 한글 400자 상한, 끄기 두 종, 안전 종료를 봅니다.

### korean-writing 스킬

써 달라는 요청이면 뜹니다. 슬랙 안내문과 메일, 공지, 보고서, 릴리스 노트, 커밋 메시지, README와 기획 문서, 회의록과 작업 메모가 다 해당합니다. 남에게 보내는 글인지 혼자 볼 글인지는 가리지 않고, 코드만 쓰는 작업에는 뜨지 않습니다.

규칙의 핵심은 사람이 말하듯 쓰는 것이고, 영어 문장을 옮긴 티가 나면 실패입니다. 시점이 중요합니다. 첫 문장부터 그렇게 쓰지, 다 써 놓고 손보지 않습니다. 완성된 글은 구조부터 번역투로 잡혀 있어서 나중에 다듬어도 잘 빠지지 않습니다.

원칙은 다섯 가지입니다. 처음부터 깨끗하게 씁니다. 걷어내는 대상은 기계성뿐이라 격식, 전문성, 장르, 논지, 사실은 건드리지 않습니다. 원문에 없던 비유나 수사를 보태지 않습니다. 다 쓰고도 미달이면 `humanize-korean`으로 보정합니다. 어떤 모델로 쓸지는 이 규칙이 정하지 않습니다.

문장을 만드는 규칙은 이렇습니다. 주어는 사람이나 조직으로 둔다. 한국어에 실제로 있는 비유만 쓴다. 구조를 은유로 설명하지 않는다. 승패로 비유하지 않는다. `것` 구문을 줄인다. 한 문체로 끝까지 간다. 문장 길이를 섞는다. 서식 규칙은 줄표 삽입구를 한 문서에 두 번까지, 불릿은 정말 목록일 때만, 기계적 병렬은 피하고, 이모지는 슬랙 인사말 정도로만 두는 것입니다.

보내기 전에 보는 것은 네 가지뿐입니다. 줄표가 셋 이상인지, `축`·`갈래`·`결`·`레이어`를 합쳐 세 번 이상 썼는지, 사물이 사람처럼 움직이는 문장이 있는지, 소리 내어 읽었을 때 걸리는 데가 있는지. 넷 중 마지막이 가장 무겁습니다. 계약서와 약관, 법률 문서, 공문은 딱딱함이 요건이라 이 규칙 밖에 있고, 코드와 로그, 명령어, 직접 인용, 고유명사, 영어 원문에도 손대지 않습니다.

### humanize-korean 스킬

써 둔 글이 대상입니다. "AI 티 없애줘", "번역투 고쳐줘", "이 글 다듬어줘"라고 하면 뜨고, 번역투와 AI 관용구만 걷어냅니다. 아직 쓰지 않은 글은 `korean-writing`의 몫입니다.

한 번의 패스로 끝냅니다. 읽으면서 문장마다 핵심 명사를 잡아 두고, 압축 룰북 `references/quick-rules.md`로 훑고, 판정이 애매한 항목만 규칙집에서 찾아보고, 걸린 구간만 고치고, 룰북의 자체검증 여섯 항목을 돌린 뒤 돌려줍니다. 길이로 나누지 않습니다. 원본 프로젝트의 실측에서 청킹은 토큰만 늘리고 품질은 같았습니다. 진단과 마무리 검토를 나눈 다단계 처리가 필요하면 원본인 im-not-ai를 쓰라고 안내합니다.

어기면 되돌리는 철칙이 다섯 있습니다. 사실과 주장, 숫자, 날짜, 고유명사, 인용은 하나도 바꾸지 않습니다. 룰북이나 규칙집의 패턴에 걸린 구간 밖은 건드리지 않습니다. 장르와 문체와 서법은 원문 그대로 둡니다. 원문에 없던 비유나 상투구를 새로 넣지 않습니다. 변경률이 30%를 넘으면 경고 신호로 보고, 50%를 넘으면 결과를 내놓지 않습니다.

목적은 어색한 번역투를 자연스러운 한국어로 바꾸는 데 있습니다. AI 탐지기를 피하는 도구가 아니며, 스킬 본문이 그렇게 설명하는 것도 금합니다.

### korean-character-count 스킬

길이 제한이 걸린 글에 뜹니다. "500자 이내로", "글자 수 세줘", "자소서 분량 맞춰줘"가 신호입니다. 한국어 글자 수는 무엇을 세느냐에 따라 달라집니다. `각`은 한 글자인데 UTF-8로는 3바이트이고, 자모를 조합한 글자는 눈에 한 글자여도 코드포인트로는 셋입니다. 그래서 모델의 어림 대신 스크립트가 셉니다.

흔히 말하는 글자 수는 `characters`(grapheme cluster)입니다. 공백 제외를 명시한 폼이면 `characters_without_whitespace`, 교육행정시스템 양식이면 `--profile neis`의 `bytes_neis`, DB 컬럼 길이면 `bytes_utf8`을 씁니다. Node 18 이상이 필요하고 `node:fs` 외의 패키지는 쓰지 않습니다. 세는 규칙의 계약은 `skills/korean-character-count/instruction.md`에 있습니다.

### crafting-effective-readmes 스킬

README를 새로 만들거나 고쳐 달라고 하면 뜹니다. 먼저 작업의 종류를 가립니다. 새로 만들기인지, 절 추가인지, 갱신인지, 점검인지. 다음으로 프로젝트 유형을 정합니다. 오픈소스, 개인, 사내, 설정 저장소 가운데 하나이고, 유형마다 템플릿과 절 체크리스트가 따로 있습니다. 어떤 README라도 이름과 한두 문장의 설명과 사용법은 빠지지 않습니다. 이 스킬은 절을 잡는 데까지이고 문장은 `korean-writing` 규칙대로 씁니다.

### 검사 훅과 스크립트

검사 훅은 `Edit`, `Write`, `MultiEdit`가 `.md` 파일을 고친 직후에 돕니다. 파일 전체가 아니라 이번에 쓴 부분만 봅니다. 전체를 보면 예전 표현이 편집마다 다시 걸려 소음이 되기 때문입니다. 판정 방법은 다음 절에 있습니다.

| 스크립트             | 하는 일                                                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/check.sh`   | 파일을 통째로 훅에 넣어 검사합니다. 써 둔 문서를 점검하거나 CI·pre-commit에서 씁니다. 걸린 파일이 있으면 종료 코드 1                  |
| `scripts/measure.sh` | 디렉터리 아래 한국어 `.md`를 전부 훅에 넣어 걸린 파일과 코드별 수를 냅니다. 걸린 파일이 사람 글인지 Claude 글인지는 사람이 판단합니다 |
| `scripts/release.sh` | 버전 하나로 `plugin.json`, README 배지, CHANGELOG를 맞추고 커밋과 태그를 만듭니다. `--push`면 push와 GitHub 릴리스까지                |

## 판정 규칙

훅은 이 순서로 판정합니다.

1. `Edit`, `Write`, `MultiEdit` 가운데 하나가 끝나면 Claude Code는 그 도구 입력을 JSON으로 만들어 `hooks-handlers/posttooluse.sh`의 stdin에 넣습니다.
2. 환경변수 `KOREAN_WRITING_HOOK_DISABLED`가 1이면, 또는 `python3`를 찾지 못하면 아무것도 보지 않고 통과합니다.
3. 경로가 `.md`가 아니면 통과합니다.
4. 도구 입력에서 이번에 쓴 부분만 모읍니다. `content`, `new_string`, `edits[].new_string`입니다. 거기에든 파일 머리 4,000자 안에든 `korean-writing: ignore`가 있으면 통과합니다.
5. 코드블록(백틱 셋 또는 `~~~`), 인라인 코드, URL, 표 행, HTML 주석을 걷어냅니다. 표를 통째로 빼는 이유는 나쁜 예를 인용하는 문서가 그 예 때문에 걸리면 안 되기 때문입니다.
6. 남은 본문에서 한글이 30%를 넘으면 그대로 검사하고, 못 미치면 줄 단위로 다시 골라 한글이 30% 이상인 줄만 검사합니다. 영어 문서 한가운데 들어간 한국어 문단 하나를 놓치지 않기 위한 장치입니다. 골라낸 뒤 남은 한글이 20자가 안 되면 통과합니다.
7. `K1`부터 `K8`까지 정규식을 돌립니다.
8. 하나도 걸리지 않으면 종료 코드 0으로 조용히 끝납니다. 걸리면 항목마다 무엇이 몇 번 나왔고 어떻게 고치는지를 stderr에 쓰고 종료 코드 2를 냅니다. 어느 쪽이든 파일에는 손대지 않습니다.

| 코드 | 무엇을           | 정규식이 보는 것                                                                    | 걸리는 시점                                     |
| ---- | ---------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------- |
| `K1` | 줄표 삽입구      | 양쪽에 공백과 글자가 있는 `—`·`–`                                                   | 4개. 이번 편집에 하나라도 있으면 파일 전체로 셈 |
| `K2` | 추상 구조어      | `축이·축은·축을·축으로`, `갈래`, `결이 다르`, `레이어`                              | 3회                                             |
| `K3` | 번역투 `것` 구문 | `것들이었`·`것들이다`, `것들을`, `하는 것이 가능`                                   | 1회                                             |
| `K4` | AI 관용구        | `결론적으로`, `종합하면`, `시사하는 바가 크`, `혁신적`, `압도적` 등                 | 1회                                             |
| `K5` | 기계적 병렬      | 쉼표나 마침표를 단 `첫째`와 `둘째`                                                  | 둘이 함께 나올 때                               |
| `K6` | 승패 의인화      | `~가 이긴다·이깁니다·이겼다·이기고`                                                 | 2회                                             |
| `K7` | 사물 의인화      | 화면·서버·장비 등이 `굳·쓰러지·넘어지·일어서·잠들`, `넘어뜨리·일으켜 세우·쓰러뜨리` | 1회                                             |
| `K8` | 번역투           | `가지고 있`, 이중 피동 `되어지·지게 된다`, `에 의해`                                | 항목별로 1회, `에 의해`는 2회                   |

줄표 하나만 예외로 파일 전체를 셉니다. 문단을 하나씩 고쳐 나가면 편집마다 줄표가 한두 개씩 들어가 파일에는 수십 개가 쌓이는데, 편집분만 세면 그중 어느 편집도 임계에 닿지 않습니다. 그래서 이번 편집에 줄표 삽입구가 하나라도 있으면 파일을 다시 읽어 같은 제외 규칙으로 전체 개수를 셉니다. 이번 편집에 줄표가 없으면 파일에 몇 개가 있든 잡지 않으므로, 예전 문서를 고칠 때 소음이 늘지는 않습니다.

임계는 규칙집보다 하나씩 높습니다. 규칙집이 한 문서에 1회까지 허용한다고 하면 훅은 2회부터 알립니다. 이 훅은 막는 장치가 아니라 알리는 장치이고, 멀쩡한 문장을 잡아 작업을 끊는 쪽이 하나를 놓치는 쪽보다 해롭기 때문입니다.

## 설계 원칙

**처음 쓸 때 잡습니다.** 세션 시작에 규칙을 넣고 글 작성 요청마다 스킬을 붙이는 이유입니다. 다 쓴 뒤의 검사는 그 둘을 빠져나온 문장을 받는 마지막 그물이지 주된 수단이 아닙니다.

**막지 않습니다.** 검사 훅은 알릴 뿐 편집을 되돌리지 않고, 주입 훅은 어떤 상황에서도 종료 코드 0입니다. `python3`가 없는 컴퓨터에서는 검사를 건너뜁니다. 검사기가 작업을 막기 시작하면 사람은 검사기를 끕니다.

**숫자 없이는 규칙을 바꾸지 않습니다.** 패턴 하나를 넣거나 빼거나 임계를 옮길 때마다 실제 문서에 돌린 결과가 있어야 합니다. 그렇게 바꾼 열세 건의 기록이 [`EVALUATION.md`](./EVALUATION.md)에 있습니다. 승패 의인화는 한 문서 1회는 허용하기로 하고 훅 임계를 1에서 2로 올렸습니다. 사물 의인화에서 "죽다"를 뺀 것은 서버가 죽었다, 프로세스가 죽었다가 개발자의 일상어이기 때문입니다. 번역투에서 `~에 대해`와 `~를 통해`의 횟수를 빼니 실제 문서에서 사람이 쓴 글만 잡던 규칙이 사라졌습니다.

**멀쩡한 문장을 잡는 것이 놓치는 것보다 나쁩니다.** 합격 기준의 순서가 그렇습니다. 정상 문장 오탐 0건이 먼저이고 위반 검출 10건은 그다음입니다. 실제 문서 143개를 넣었을 때 사람이 쓴 글에서 걸린 것은 하나입니다.

**바깥과 통신하지 않습니다.** 훅이 무엇을 읽고 무엇을 하지 않는지는 [SECURITY.md](./SECURITY.md)에 있고, 그것을 직접 확인하는 `grep` 명령 세 개도 거기 있습니다.

**늘 읽히는 것은 작게 둡니다.** 평소에 컨텍스트에 들어가는 것은 상시 규칙과 스킬 설명 넷뿐이고, 큰 파일은 그 일이 생겼을 때만 열립니다.

```
hooks-handlers/always-on.md     1.4 KB   세션마다 한 번
SKILL.md                        8.1 KB   글 작성 요청에
references/quick-rules.md      16.6 KB   윤문을 시작할 때
references/taxonomy.md        124   KB   판정이 애매한 항목 하나를 볼 때
```

**가져온 파일은 가져온 대로 둡니다.** 규칙집과 압축 룰북, README 스킬, 글자 수 스크립트는 다른 MIT 프로젝트의 것입니다. 어디서 가져왔고 어느 줄을 고쳤는지는 [`NOTICE.md`](./NOTICE.md)에 파일 단위로 적어 두었습니다.

## 검증

합격 기준과 측정 결과는 [`EVALUATION.md`](./EVALUATION.md)에 있습니다. 기준은 훅 정확도, 스킬 트리거, 스킬 내용 유효성, 구조 건전성, 실패 모드, 사용하는 사람의 기준까지 여섯 묶음이고, 하나라도 미달이면 고치고 다시 잽니다.

| 측정                      | 결과                                       |
| ------------------------- | ------------------------------------------ |
| 위반 문장 검출            | 10 / 10                                    |
| 정상 문장 오탐            | 0 / 5                                      |
| 실제 문서 오탐            | 1 / 143 (0.7%)                             |
| 검출된 항목의 코드 정확도 | 10 / 10                                    |
| 글 작성 요청 트리거       | 5 / 5, 코드 작업 오매칭 0 / 5              |
| 변이 테스트               | 심은 결함 15 / 15 검출                     |
| 상시 규칙 주입 효과       | 블라인드 24쌍에서 21승 0패 3무             |
| 상시 컨텍스트 비용        | 약 950토큰 (스킬 설명 290 + 상시 규칙 662) |
| 외부 네트워크 호출        | 0                                          |
| 회귀 테스트               | 63 / 63                                    |

실제 문서 오탐은 이 플러그인과 관계없이 한 컴퓨터에 쌓여 있던 한국어 `.md` 143개로 쟀습니다. 파일을 통째로 훅에 넣으니 60개가 걸렸습니다. 그중 59개는 2026년에 Claude가 쓴 구현 로그와 QA 보고서, CLAUDE.md였고 사람이 쓴 문서는 하나였습니다. 규칙을 고치기 전 같은 측정에서는 사람이 쓴 문서 7개, 4.9%가 걸렸습니다.

상시 규칙의 효과는 함수 설명, 에러 진단, PR 리뷰 같은 프롬프트 12개로 쟀습니다. 주입한 조건과 안 한 조건으로 48건을 만들고, 같은 모델에게 순서를 바꿔 두 번씩 어느 쪽이 나은지 블라인드로 물었습니다. 24쌍에서 주입 쪽이 21승 3무였고 프롬프트 12개 전부에서 이기거나 비겼습니다. 문체를 빼고 기술적 오류만 따로 본 검사에서는 심각한 오류가 양쪽 다 없었습니다.

스킬 유무는 같은 프롬프트 4개로 비교했습니다. 2026-09-10의 claude-opus-5에서는 유효 표본 7건이 전부 훅을 통과해 생성 단계 효과를 이 표본으로 구분하지 못했습니다. 이 결과도 그대로 적어 두었습니다.

로컬에서 같은 검사를 돌리는 명령입니다.

```bash
python3 hooks-handlers/test_posttooluse.py     # 검사 훅 회귀 43건
python3 hooks-handlers/test_sessionstart.py    # 상시 규칙 회귀 20건
scripts/check.sh README.md CLAUDE.md           # 문서가 자기 훅을 통과하는가
scripts/measure.sh ~/Documents                 # 실제 문서 뭉치의 오탐
```

GitHub Actions는 push와 PR마다 macOS와 Linux에서 같은 검사를 돌립니다. 매니페스트와 이슈 양식의 문법, 훅의 실행 비트, 회귀 테스트 둘, 한국어 문서 13종이 자기 훅을 통과하는지, 글자 수 스크립트의 스모크 테스트입니다. 여기에 shellcheck, `plugin.json`과 README 배지와 CHANGELOG의 버전이 같은지, `claude plugin validate`가 더해집니다.

## 하지 않는 것

- 검사 훅은 `.md` 파일만 봅니다. 코드 안의 한국어 주석과 문자열, 슬랙으로 바로 나가는 답변은 생성 단계의 상시 규칙과 스킬이 맡고 사후 검사는 없습니다.
- 정규식은 알려진 패턴 여덟 종만 잡습니다. 새로운 어색함은 사람이 찾아 넣어야 합니다.
- 상시 규칙은 30턴을 쌓은 뒤에도 효과가 남습니다. 컨텍스트 3만에서 4만 토큰 깊이에서 네 쌍을 블라인드로 판정해 네 쌍 모두 주입 쪽이 이겼습니다. 그보다 긴 대화는 재지 않았습니다.
- **서브에이전트는 이 플러그인이 맡지 못합니다.** 세션 시작 훅은 서브에이전트를 위해 아예 돌지 않습니다(훅 실행 기록이 서브에이전트를 둘 띄워도 한 줄). 서브에이전트 시작 훅은 돌지만 출력이 서브에이전트 컨텍스트로 가지 않고, 스킬 목록도 전달되지 않습니다. 전달되는 것은 `CLAUDE.md` 하나입니다. 서브에이전트까지 맡으려면 아래 한 줄을 쓰는 쪽 `CLAUDE.md` 에 넣으세요.

```markdown
한국어로 답하거나 한국어 글을 쓸 때는 korean-writing 규칙을 따른다.
사물 의인화, 영어 직역 비유, 축·갈래·결·레이어, 줄표 삽입구, 첫째·둘째 병렬,
번역투, AI 관용구를 쓰지 않는다.
```

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
│   ├── always-on.md                  세션마다 주입되는 답변용 규칙 아홉 항목
│   ├── sessionstart.sh               주입 본체. 언제나 exit 0
│   ├── posttooluse.sh                검사 본체. bash 안의 python3 정규식 K1~K8
│   ├── ground-truth.json             실제로 생성됐던 위반 문장 10건
│   ├── clean.json                    같은 맥락의 정상 문장 5건
│   ├── test_posttooluse.py           검사 훅 회귀 43건. 보고 횟수까지 검증합니다
│   └── test_sessionstart.py          상시 규칙 회귀 20건
├── SKILL.md                          korean-writing 스킬
├── references/
│   ├── quick-rules.md                윤문 첫 패스용 압축 룰북. im-not-ai 원본
│   └── taxonomy.md                   AI 티 분류 체계. im-not-ai 원본, 10분류 84항목
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
├── .editorconfig
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

## 이웃 도구와 이 플러그인의 자리

한국어 산문 품질 도구는 두 층으로 놓입니다. 규칙집을 만드는 쪽과 그 규칙을 특정 편집기에 붙이는 쪽입니다. 이 플러그인은 뒤쪽입니다. 규칙집과 압축 룰북은 im-not-ai에서 그대로 가져왔고, Claude Code에 붙이는 방식은 여기서 만들었습니다.

| 도구                                                 | 무엇인가                                                                                                            | 이 플러그인과의 관계                                                                                                                               |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| [im-not-ai](https://github.com/epoko77-ai/im-not-ai) | 이미 쓴 한글에서 AI 티를 걷어내는 윤문 스킬. 진단·윤문·마무리를 나눈 다중 호출 파이프라인이고 여러 CLI를 지원합니다 | 규칙집과 압축 룰북을 그대로 가져왔고, 윤문 절차도 이 프로젝트의 단일 콜 경로를 줄인 것입니다. 이 플러그인은 처음 쓸 때와 평소 답변에 무게를 둡니다 |
| [k-skill](https://github.com/NomaDamas/k-skill)      | 한국인을 위한 스킬 모음. 글자 수부터 교통·날씨·검색까지                                                             | 글자 수 스크립트를 가져왔습니다. 맞춤법 검사 스킬은 원문을 외부 서버로 보내서 가져오지 않았습니다                                                  |
| 맞춤법·띄어쓰기 검사기                               | 맞춤법을 봅니다                                                                                                     | 이 플러그인은 문체만 봅니다. 겹치지 않으니 같이 쓰면 됩니다                                                                                        |

## 자주 묻는 질문

<details>
<summary><b>왜 검사 훅은 .md 파일만 보나요?</b></summary>

훅은 파일 편집 도구가 끝난 뒤에 도구 입력을 받는 구조라 파일이 아닌 답변은 볼 수 없습니다. 답변은 세션 시작에 들어가는 상시 규칙과 글 작성 스킬이 생성 단계에서 맡습니다. 답변을 정규식으로 사후 검사하는 것도 재 봤는데, 평소 답변에서는 표본당 0.21건밖에 잡지 못해 감시 수단으로 쓰지 않습니다.

근거: `hooks-handlers/sessionstart.sh` 머리 주석, [`EVALUATION.md`](./EVALUATION.md)의 N3.

</details>

<details>
<summary><b>훅이 내 편집을 되돌리나요?</b></summary>

되돌리지 않습니다. 훅이 하는 일은 걸린 항목을 stderr에 쓰고 종료 코드 2를 내는 것까지입니다. 파일은 편집된 그대로 남고, 고칠지 말지는 Claude Code와 사람이 정합니다.

근거: [SECURITY.md](./SECURITY.md)의 「이 플러그인이 하는 일」 표.

</details>

<details>
<summary><b>내 글이 외부로 나가나요?</b></summary>

나가지 않습니다. 훅은 bash 안에서 python3 정규식을 돌릴 뿐이고 글자 수 스크립트는 `node:fs` 말고는 아무것도 불러오지 않습니다. 네트워크 호출과 외부 프로그램 실행이 없다는 것은 [SECURITY.md](./SECURITY.md)의 `grep` 명령 세 개로 누구나 확인할 수 있습니다. 원문을 외부 서버로 보내는 맞춤법 검사 스킬을 가져오지 않은 것도 같은 이유입니다.

</details>

<details>
<summary><b>계약서나 약관을 고칠 때도 걸리나요?</b></summary>

걸립니다. 그래서 파일 머리에 `<!-- korean-writing: ignore -->` 한 줄을 넣어 그 파일만 검사에서 빼는 방법을 두었습니다. 격식이 요건인 글은 스킬 규칙에서도 예외입니다. 이 저장소의 규칙집은 나쁜 예를 일부러 모아 둔 파일이라 같은 표시가 붙어 있습니다.

</details>

<details>
<summary><b>토큰을 얼마나 쓰나요?</b></summary>

상시로 드는 것은 스킬 설명 넷 약 290토큰과 세션당 한 번 들어가는 상시 규칙 약 660토큰입니다. 상시 규칙은 설치된 플러그인을 그대로 두고 상시 규칙만 껐다 켜며 `claude -p`의 입력 토큰 총량을 뺀 값으로, 끄면 12,364, 켜면 13,026이었습니다. MCP 도구 정의와 사용자 설정을 빼야 값이 고정됩니다. 규칙은 프롬프트 캐시에 들어가 턴마다 다시 내지 않습니다. 스킬 본문은 글 작성 요청이 있을 때만 로드되고 훅은 LLM을 부르지 않습니다.

근거: [`EVALUATION.md`](./EVALUATION.md)의 D2와 F7.

</details>

<details>
<summary><b>설치했는데 스킬이 안 보여요.</b></summary>

먼저 `claude plugin list`에서 `korean-writing`이 `enabled`로 나오는지 봅니다. 저장소를 `~/.claude/skills/`에 링크해 둔 채로 마켓플레이스 설치까지 했다면 둘 중 하나를 지웁니다. 스킬 목록은 세션을 새로 열어야 바뀝니다.

</details>

<details>
<summary><b>위반 검출 10/10이면 다 잡는다는 뜻인가요?</b></summary>

그런 뜻이 아닙니다. 정규식은 그 열 문장을 보고 만들었으니 열 문장을 잡는 것은 당연하고, 그 숫자는 규칙을 고치다 무엇을 깨뜨리지 않았는지 보는 회귀용입니다. 봐야 할 숫자는 오탐입니다. 실제 문서 143개 중 사람이 쓴 글에서 걸린 것은 하나입니다. 정규식은 알려진 여덟 가지 패턴만 잡고, 새로운 어색함은 잡지 못합니다.

근거: [`EVALUATION.md`](./EVALUATION.md)의 A1~A3와 2026-09-10 재측정, [`hooks-handlers/ground-truth.json`](./hooks-handlers/ground-truth.json).

</details>

<details>
<summary><b>Windows에서 되나요?</b></summary>

돌려 보지 않았습니다. 훅이 bash 스크립트여서 Git Bash나 WSL이 있어야 합니다. `.gitattributes`가 스크립트를 LF로 고정하므로 CRLF로 체크아웃되어 훅이 깨지는 일은 없습니다. 써 본 결과를 이슈로 남겨 주시면 여기에 적겠습니다.

</details>

## 기여

절차는 [CONTRIBUTING.md](./CONTRIBUTING.md)에 있습니다. 가장 값진 기여는 코드가 아니라 문장입니다. Claude Code가 쓴 어색한 한국어를 봤거나 훅이 멀쩡한 문장을 잡았다면 [어색한 문장 제보](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=awkward-sentence.yml) 양식으로 고치지 않은 원문 그대로 보내 주세요. 제보한 문장은 정답 데이터나 정상 문장에 들어가 회귀 테스트가 됩니다. 버그 신고와 판정 규칙 제안 양식도 있고, 쓰는 법을 묻거나 사례를 나누는 자리는 [Discussions](https://github.com/IsthisLee/claude-korean-writing/discussions)입니다.

작업을 시작하면 기준선부터 잡습니다.

```bash
git clone https://github.com/IsthisLee/claude-korean-writing.git
cd claude-korean-writing
python3 hooks-handlers/test_posttooluse.py
python3 hooks-handlers/test_sessionstart.py
scripts/check.sh README.md CLAUDE.md
```

판정 규칙을 바꾸는 변경에는 `scripts/measure.sh`로 실제 문서에 돌린 숫자와 회귀 테스트가 같이 옵니다. 한국어 문서를 고쳤으면 `scripts/check.sh`를 통과시키고, README는 한국어판과 영어판을 함께 고칩니다. 커밋 제목은 Conventional Commits 형식의 한국어이고 버전 번호는 손대지 않습니다. 참여하는 사람은 [행동 강령](./CODE_OF_CONDUCT.md)을 따르고, 보안 문제는 공개 이슈 대신 [SECURITY.md](./SECURITY.md)의 절차로 알립니다.

## 릴리스

[SemVer](https://semver.org/lang/ko/)를 따르고 버전의 정본은 `.claude-plugin/plugin.json` 한 곳입니다. `marketplace.json`에는 버전을 적지 않습니다.

릴리스는 `scripts/release.sh <버전>` 한 번입니다. 작업 트리가 깨끗한지와 버전 형식을 보고, CHANGELOG의 `[Unreleased]` 내용을 새 버전 절로 옮기고, 두 README의 상단 인용구에 그 버전이 적혀 있는지 확인한 다음, `plugin.json`과 README 배지를 올리고, 회귀 테스트와 `claude plugin validate`를 돌리고, 커밋과 주석 태그를 만듭니다. `--push`를 붙이면 push와 GitHub 릴리스 생성까지 이어서 합니다.

```bash
scripts/release.sh 1.1.0
scripts/release.sh 1.1.0 --push
```

## 출처와 라이선스

| 파일                                 | 어디서                                                                                                                                      | 고친 것                                                     |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `references/taxonomy.md`             | [im-not-ai](https://github.com/epoko77-ai/im-not-ai)의 `skills/humanize-korean/references/ai-tell-taxonomy.md`, 커밋 `9747f03` (2026-09-06) | 머리에 훅 제외 표시 한 줄                                   |
| `references/quick-rules.md`          | im-not-ai의 `skills/humanize-korean/references/quick-rules.md`, 같은 커밋                                                                   | 머리에 훅 제외 표시 한 줄                                   |
| `skills/humanize-korean/SKILL.md`    | im-not-ai의 절차와 철칙                                                                                                                     | 단일 패스에 맞춰 이 저장소에서 다시 씀                      |
| `skills/korean-character-count/`     | [k-skill](https://github.com/NomaDamas/k-skill)                                                                                             | 스크립트는 그대로, 설명서는 실행 경로만, SKILL.md는 다시 씀 |
| `skills/crafting-effective-readmes/` | [agent-skills](https://github.com/joshuadavidthomas/agent-skills)의 `crafting-effective-readmes/`, 커밋 `516dee7` (2026-07-20)              | `style-guide.md`에서 관련 스킬을 가리키는 한 줄             |

나머지는 이 저장소에서 썼습니다. `korean-writing` 스킬, 상시 규칙, 검사 훅 전체, 정답 데이터, 검증 기준이 그것입니다. 가져온 파일의 라이선스는 전부 MIT이고 원 저작권 표시는 [`NOTICE.md`](./NOTICE.md)에 모아 두었습니다. 이 저장소의 라이선스도 [MIT](./LICENSE)입니다.
