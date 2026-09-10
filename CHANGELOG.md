# Changelog

이 프로젝트의 눈에 띄는 변경을 기록합니다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를, 버전은 [SemVer](https://semver.org/lang/ko/)를 따릅니다. 첫 릴리스가 1.0.0 입니다.

## [Unreleased]

### 추가

- **im-not-ai 의 윤문 파이프라인을 내장했습니다.** 커밋 `9747f036cdc2`(2026-09-06)의 런타임 부분집합을 그대로 넣었습니다. 스킬 셋(`humanize-korean`·`humanize`·`humanize-redo`), 에이전트 셋(진단·윤문·마무리 검토), 파이썬 스크립트 아홉, 규칙집과 참조 문서입니다. `/korean-writing:humanize` 와 `/korean-writing:humanize-redo` 로 부르고, "AI 티 없애줘" 같은 요청에는 `humanize-korean` 스킬이 뜹니다. 가져온 파일에서 고친 것은 스킬 설명의 트리거 문구 하나뿐입니다(NOTICE.md). 개발용 에이전트 여섯은 싣지 않았습니다
- 격리된 HOME 에서 확인했습니다. 설치 뒤 `/humanize` 자동완성에 `/korean-writing:` 셋만 뜨고, `/korean-writing:humanize` 에 AI 티를 몰아넣은 200자 문단을 넣으니 세 콜이 끝까지 돌아 변경률 39%, 등급 A-, 자체검증 6/6 으로 끝났습니다(451초, 1.64달러). 기록은 `docs/samples/humanize-run.md` 에 있습니다
- CI 에 내장 스크립트의 `py_compile` 과 `--help` 실행 확인 단계
- `docs/samples/`: 같은 질문에 상시 규칙을 넣지 않은 답과 넣은 답의 원문(claude-sonnet-5). README 의 전후 발췌가 여기서 나왔습니다
- README 머리에 무엇을 하는지 다섯 줄 목록을 두고, 정답 문장 넷을 전후 표로, 상시 규칙 주입 전후를 실제 답변 발췌로 보였습니다

### 변경

- 상시 컨텍스트 비용은 약 1,390토큰(상시 규칙 662, 스킬 설명 넷 430, 에이전트 셋 297)입니다. EVALUATION.md 의 D2 예산을 1,000 에서 1,500 으로 올렸습니다
- 윤문 스크립트는 Python 3.10 이상이 필요합니다. 검사 훅은 그대로 어느 python3 든 됩니다
- SECURITY.md 의 확인 명령이 내장 스크립트까지 봅니다. 네트워크 호출과 외부 프로그램 실행은 없습니다
- `crafting-effective-readmes` 스킬을 경유본 softaworks/agent-toolkit 대신 원본 joshuadavidthomas/agent-skills(커밋 `516dee7a422b`, 2026-07-20)에서 직접 가져왔습니다. 내용은 같고, 경유본에만 있던 스킬 폴더의 `README.md` 를 지웠습니다
- 출판사 편집부 일화는 claude-forge 규칙집에만 있던 내용이라 SKILL.md·README·훅 주석에서 빼고, 정답 데이터 G05·G06 을 근거로 적었습니다. NOTICE.md 에서 claude-forge 항목을 뺐습니다

### 제거

- 이 저장소가 쓰던 `humanize-korean` 스킬과 `references/taxonomy.md`·`references/quick-rules.md` 사본. im-not-ai 의 파이프라인이 규칙집째 들어오면서 필요 없어졌습니다

## [1.1.0] - 2026-09-10

### 추가

- **상시 규칙 주입.** 세션이 열릴 때 `hooks-handlers/always-on.md`(약 660토큰)를 한 번 넣는 SessionStart 훅을 넣었습니다. 스킬이 뜨지 않는 평소 답변을 맡습니다. 프롬프트 12개에 조건 2개와 표본 2개로 48건을 생성하고 순서를 바꿔 두 번씩 블라인드로 판정한 결과 24쌍에서 21승 3무 0패였습니다. 기술 오류만 따로 본 검사에서 심각한 오류는 양쪽 0건입니다. 근거는 EVALUATION.md 의 C5 에 있습니다
- `hooks-handlers/test_sessionstart.py`: 주입 내용, 끄기 두 종, 규칙 파일이 없을 때의 안전 종료, 크기 상한을 보는 회귀 20건
- 상시 규칙만 끄는 환경변수 `KOREAN_WRITING_ALWAYS_ON_DISABLED=1`. `KOREAN_WRITING_HOOK_DISABLED=1` 은 그대로 훅 전체를 끕니다

- 공개 저장소 문서: `CONTRIBUTING.md`(한국어·영어), `CODE_OF_CONDUCT.md`(Contributor Covenant 2.1 공식 한국어판), `SECURITY.md`(한국어·영어). SECURITY.md 에는 훅이 무엇을 읽고 무엇을 하지 않는지, 네트워크를 쓰지 않는다는 것을 직접 확인하는 명령 세 가지를 적었습니다
- `CLAUDE.md`: 이 저장소에서 작업하는 Claude 를 위한 규칙. 기준선 명령, 네트워크 금지, 가져온 파일 취급, 버전 정본, 커밋 형식, 판정 기준을 바꿀 때의 실측 의무
- `.claude/settings.json`: 기여자가 공유하는 프로젝트 설정. 검증 명령은 묻지 않고 허용하고, 가져온 파일과 `plugin.json` 편집은 확인을 받습니다
- `.github/`: PR 양식, 이슈 양식 세 종(어색한 문장 제보, 버그 신고, 판정 규칙 제안), 이슈 첫 화면의 보안·기여 안내 링크, `CODEOWNERS`, `dependabot.yml`
- `.gitattributes`: 셸 스크립트를 LF 로 고정합니다. CRLF 로 체크아웃되면 훅이 `bad interpreter` 로 죽습니다. 가져온 파일은 GitHub 언어 통계에서 뺍니다
- `.editorconfig`
- `docs/social-preview.png`(1280×640): 링크를 공유할 때 GitHub 이 보여주는 카드 이미지. 저장소 설정에서 올립니다
- CI 작업 셋: `shellcheck`, 버전 표기 일치(`plugin.json`·README 배지·CHANGELOG), 이슈 양식과 워크플로의 YAML 문법

### 변경

- **claude-forge 를 거치지 않습니다.** 규칙집 `references/taxonomy.md` 와 압축 룰북 `references/quick-rules.md` 를 원본인 im-not-ai(커밋 `9747f036cdc2`, 2026-09-06)에서 직접 가져왔습니다. 이전 판은 claude-forge 가 im-not-ai v2.0 에 항목을 더한 것과 forge 가 따로 만든 압축본이었습니다. 항목은 73개에서 84개가 됩니다. `humanize-korean` 스킬은 im-not-ai 의 절차와 철칙을 바탕으로 다시 썼고, 길이로 나누던 규칙(5,000자)을 없앴습니다. 승패 의인화·추상 구조어의 근거로 적혀 있던 출판사 편집부 일화는 forge 규칙집에서 온 것이라 빼고, 정답 데이터 G05·G06 을 근거로 적었습니다. 훅의 판정은 바뀌지 않았습니다(회귀 43/43). NOTICE.md 에서 claude-forge 항목을 뺐습니다
- **agent-toolkit 도 거치지 않습니다.** `crafting-effective-readmes` 스킬을 경유본 softaworks/agent-toolkit 대신 원본 joshuadavidthomas/agent-skills(커밋 `516dee7a422b`, 2026-07-20)에서 직접 가져왔습니다. 내용은 같고, 경유본에만 있던 스킬 폴더의 `README.md` 를 지웠습니다. NOTICE.md 에서 agent-toolkit 항목을 뺐습니다
- **상시 규칙을 넣으며 남겼던 세 가지를 전부 쟀습니다.** 서브에이전트에는 훅도 스킬도 전달되지 않아 플러그인 범위 밖으로 두고 쓰는 쪽 `CLAUDE.md` 에 넣도록 안내합니다. 긴 대화에서는 30턴을 쌓은 뒤에도 주입 조건이 네 쌍 모두 이깁니다. 규칙을 고쳤을 때의 회귀는 `docs/experiments/always-on/regress.sh` 로 봅니다. 근거는 EVALUATION.md 의 「상시 규칙을 넣으며 남겼던 것」에 있습니다
- 실험 장비를 `docs/experiments/always-on/` 에 보존했습니다. 스크립트, 프롬프트 12개, 주입문 초안, 판정 기준과 결과 보고입니다. README 에 `--strict-mcp-config` 와 `--setting-sources ""` 를 빠뜨렸을 때 무슨 일이 생기는지 먼저 적었습니다

- `korean-writing` 스킬이 맡는 범위를 "밖으로 나갈 글" 에서 "글 작성 요청" 으로 넓혔습니다. 슬랙·메일·보고서처럼 남에게 보내는 글만이 아니라 회의록·작업 메모처럼 안에서 보는 글도, 써 달라는 요청이면 스킬이 로드됩니다. 코드만 쓰는 작업은 그대로 대상이 아닙니다. 스킬 설명과 README 두 판, CLAUDE.md, EVALUATION.md 의 표현을 맞췄습니다. 설명이 길어져 `/context` 기준 약 50토큰에서 70토큰이 됐습니다
- **목적을 "Claude Code 가 쓰는 모든 한국어" 로 넓혔습니다.** 이전에는 글 작성 요청과 `.md` 편집만 맡아서, 가장 양이 많은 평소 답변이 비어 있었습니다. README 에 어느 자리를 맡고 어느 자리를 안 맡는지 적은 표를 넣었습니다
- EVALUATION.md 의 D2 예산을 상시 500 토큰에서 1,000 토큰으로 올렸습니다. 상시 규칙 662 토큰이 들어가면서 합계가 약 950 이 됩니다. 시험한 규칙을 그대로 넣고 예산을 다시 잡았습니다
- CI 를 macOS 와 Linux 양쪽에서 돌립니다. 훅은 bash 와 python3 만 쓰므로 platform 배지를 `macOS | Linux` 로 고쳤습니다
- CI 워크플로에 `permissions: contents: read` 와 같은 브랜치 중복 실행 취소를 넣고, 액션을 v7 로 올렸습니다
- README 두 판에 CI 배지를 넣고, 파일 구조와 CI 설명을 실제와 맞췄습니다
- `.gitignore` 가 `.claude/` 를 통째로 무시하던 것을 고쳐 `.claude/settings.json` 만 추적합니다
- GitHub 저장소 설정: 설명 문구, 토픽 15종, 비공개 취약점 신고 활성화

### 고침

- `hooks-handlers/posttooluse.sh` 에 shellcheck 지시문 한 줄을 넣어 정적 검사를 통과시켰습니다. 판정 동작은 그대로입니다

## [1.0.0] - 2026-09-10

### 추가

- `korean-writing` 스킬: 밖으로 나갈 글을 처음 쓸 때 번역투·AI 관용구를 피하는 원칙과 교정 예시
- `humanize-korean` 스킬: 이미 쓴 글을 사실 불변으로 다듬는 윤문 (claude-forge에서 이식)
- `korean-character-count` 스킬: grapheme 기준 글자 수 (k-skill에서 이식)
- `crafting-effective-readmes` 스킬: README의 절 구성을 프로젝트 유형(오픈소스·개인·사내·설정)에 맞춰 잡습니다 (agent-toolkit에서 이식)
- PostToolUse 훅: `.md` 편집 시 이번에 쓴 부분만 AI 티 패턴 K1~K8로 검사합니다. 편집을 되돌리지 않고 알리기만 합니다. 코드블록·인라인 코드·URL·표 행은 검사하지 않고, 편집분의 한글 비중이 30% 미만이면 한글 비중 30% 이상인 줄만 모아 다시 봅니다. 줄표는 이번 편집에 하나라도 있으면 파일 전체 개수로 판정합니다(문단씩 고치며 쌓이는 것). `~~~` 코드블록과 HTML 주석도 검사에서 뺍니다. K7 은 "죽다" 를 잡지 않고, K8 은 `~에 대해`·`~를 통해` 횟수를 세지 않습니다(실제 문서 143개 실측)
- 훅 끄기 수단 두 가지. 파일 머리의 `<!-- korean-writing: ignore -->` 표시(그 파일만), 환경변수 `KOREAN_WRITING_HOOK_DISABLED=1`(세션 전체). python3 가 없으면 검사 없이 통과합니다
- `scripts/check.sh`: 이미 써 둔 문서를 통째로 훅과 같은 기준으로 검사합니다. 걸리면 종료 코드 1이라 CI·pre-commit 에 그대로 씁니다
- `scripts/release.sh`: 버전·CHANGELOG·README 배지·커밋·태그를 한 번에. 버전의 정본은 `plugin.json` 한 곳입니다
- 검증 기준(`EVALUATION.md`): 실제 실패 문장 10건과 정상 문장 5건으로 만든 훅 정확도 기준, 스킬 트리거 기준, 사용하는 사람의 기준. 회귀 테스트 43건
- GitHub Actions 워크플로(`.github/workflows/validate.yml`): push와 PR마다 회귀 테스트, 매니페스트 JSON, 훅 실행 비트, 한국어 문서의 자기 훅 통과, 글자 수 스크립트 스모크, `claude plugin validate`를 돌립니다
- README 한국어판·영어판, 훅 출력 데모 이미지(`docs/hook-output.svg`)
- 제3자 고지(`NOTICE.md`): im-not-ai·claude-forge·k-skill·agent-toolkit 의 원 저작권 표시

[Unreleased]: https://github.com/IsthisLee/claude-korean-writing/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/IsthisLee/claude-korean-writing/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/IsthisLee/claude-korean-writing/releases/tag/v1.0.0
