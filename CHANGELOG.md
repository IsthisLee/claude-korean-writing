# Changelog

이 프로젝트의 눈에 띄는 변경을 기록합니다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를, 버전은 [SemVer](https://semver.org/lang/ko/)를 따릅니다. 첫 릴리스가 1.0.0 입니다.

## [Unreleased]

### 추가

- **`korean-writing` 스킬을 im-not-ai 규칙집 수준으로 올렸습니다.** 그 규칙집의 `quick: true` 항목 61개 가운데 처방을 가진 것이 21개였는데 60개가 됐습니다(남은 하나 G-3 은 규칙집이 실증 부족으로 보류한 항목입니다). 빠져 있던 것 중 둘이 그 규칙집의 실측 최강 신호입니다. `A가 아니라 B다` 부정 대구(사람 대비 밀도 9.2배)와 `~하고,` 처럼 연결어미 뒤에 찍는 쉼표(KatFish 측정에서 사람 4.1% 대 AI 19.8%)입니다. 대명사·이중 조사·좌향 수식·만능 동사·사전 은유·결말 공식·명사화 누적 등도 새로 넣고 「글을 끝낼 때」 절을 신설했습니다
- **검사 훅에 `K9` 부정 대구와 `K10` 연결어미 뒤 쉼표를 넣었습니다.** 임계는 이 머신의 한국어 `.md` 205개로 정했습니다. 대구 3회 이상, 쉼표는 6회 이상이면서 연결어미의 30% 이상일 때 알립니다. 2023년 이전에 쓰인 문서 32개에서 오탐은 0건입니다. 쉼표는 줄표와 같은 이유로 파일 전체를 셉니다
- **`docs/experiments/skill-vs-imnotai/` 를 상설 게이트로 넣었습니다.** 스킬로 처음부터 쓴 글과 규칙 없이 쓴 뒤 im-not-ai 로 윤문한 글을 블라인드로 붙입니다. 단문은 Fast Path 한 콜, 장문은 정밀 3콜(진단·윤문·마무리)로 윤문하고 결합 입력은 저장소의 `scripts/prepare_monolith_input.py` 가 만듭니다. 스킬이 진 쌍이 더 많으면 종료 코드 1입니다. `SKILL.md` 를 고쳤으면 릴리스 전에 돌립니다
- **상시 규칙에 연결어미 뒤 쉼표와 부정 대구를 넣었습니다.** 스킬이 뜨지 않는 평소 답변에서도 연결어미 쉼표 비율이 37.7% 였습니다. 한 줄을 더하니 11.3% 가 됐습니다(프롬프트 여섯, 조건마다 12건). 주입문은 한글 371자에서 402자, 실측 726토큰이 됐고 상한을 400에서 420으로 올렸습니다. `docs/experiments/always-on/regress.sh` 회귀 게이트는 새 2승 옛 2승으로 통과했습니다(나빠지지 않았다는 뜻이고 좋아졌다는 뜻은 아닙니다)
- **스킬에 「리듬」 절을 넣었습니다.** 규칙을 늘린 초판은 표지를 크게 줄이고도 블라인드 쌍대 판정에서 옛 스킬을 이기지 못했습니다(5승 6패). 판정자가 되풀이해 지적한 것은 문장 길이가 고르게 짧다는 것이었고, 재 보니 표준편차가 16.28에서 12.93으로 떨어져 있었습니다. 규칙을 지키려다 문장을 자른 것이고 길이 균일성은 규칙집의 E-1 항목입니다. 문단마다 100자 안팎의 긴 문장을 하나 두라는 규칙을 넣으니 표준편차가 18.97로 올라 네 조건 중 가장 높아졌고 판정도 뒤집혔습니다
- 생성 단계를 블라인드 쌍대로 판정했습니다. 생성은 claude-opus-5, 판정은 claude-fable-5-1 로 나누고 쌍마다 순서를 바꿔 두 번 물었습니다. 최종판이 옛 스킬을 12승 4패로 이겼습니다(이항 단측 p=0.038). 판정 기준은 저장소가 쓰던 것을 그대로 써서 이번에 넣은 대구·쉼표 항목이 들어 있지 않습니다
- **장문에서 드러난 결함 둘을 고쳤습니다.** 1,500자를 요청한 칼럼·에세이·리포트 24건에서 규칙을 붙인 쪽이 요청 분량을 덜 채웠고(중앙값 1,128자 대 1,205자) `것` 구문이 1000자당 0.14에서 0.53으로 늘었습니다. 「요청받은 분량을 지킨다」와 `~라는 것이다` 예문을 넣어 각각 1,165자와 0.04가 됐습니다
- **im-not-ai 윤문본을 이겼습니다.** 규칙 없이 쓴 글을 im-not-ai 로 윤문한 것과 스킬로 처음부터 쓴 글을 붙여 56쌍(단문 32, 장문 24)에서 **49승 0패**입니다. 장문은 정밀 3콜(진단·윤문·마무리)을 저장소의 실제 shim 스크립트와 에이전트 정의로 재현해 붙였습니다. im-not-ai 쪽에만 남아 있던 어시스턴트 마무리를 걷어내고 다시 붙여도 장문에서 18승 0패입니다
- 1차 판정은 41쌍 22승 19패로 동등에서 멈췄습니다. 진 쌍의 판정 이유를 읽어 세 가지를 고쳤습니다. 말미의 분량 보고와 후속 제안(표본당 0.29·0.42회), 소제목 남발(헤딩 1.21줄 대 0.62줄), 문단마다 비슷한 길이로 끝나는 리듬(문단 끝 문장 길이 표준편차 14.58 대 16.24)입니다. 셋 다 규칙에 없던 것이고 고친 뒤 각각 0.00·0.00·16.67이 됐습니다. 기록은 EVALUATION.md 의 C7·C9·C10 에 있습니다

### 고침

- **설명 문서를 실제 구현과 전수 대조했습니다.** README 한국어판·영어판, `SECURITY.md`, `EVALUATION.md` 에서 틀린 값 스물여섯 곳을 고쳤습니다. 실측 문서 수(143→205), 회귀 건수(63→79), 상시 규칙 항목 수(아홉→열), 훅 스크립트 줄 수(173→234), CI 검사 문서 수(12→14), 파일 크기 표, 서브에이전트용 규칙 스니펫입니다. 저장소 구성 트리에 `docs/samples/` 와 `docs/experiments/` 둘이 빠져 있어 넣었습니다
- **`EVALUATION.md` 의 「측정 중 고친 것」 절이 편집 중에 통째로 사라져 있었습니다.** 열여섯 건이 지워졌고 헤딩 둘이 중복돼 있었습니다. README 전수 대조 중에 「그렇게 바꾼 열세 건」 이라는 문장의 근거를 세다가 발견했습니다. git 에서 되살리고 이번에 고친 여섯 건을 17~22번으로 더했습니다
- **같은 규칙이 놓인 세 곳이 어긋나 있었습니다.** 규칙 본문은 `SKILL.md` 가 정본이지만 사본이 둘 더 필요합니다. 상시 규칙은 스킬이 안 뜨는 평소 답변을 맡고 `CLAUDE.md` 는 훅도 스킬도 전달되지 않는 서브에이전트를 맡습니다. 이번에 대구와 연결어미 쉼표를 앞의 둘에만 넣고 `CLAUDE.md` 를 빠뜨려서, 실측 최강 신호 둘이 서브에이전트에만 안 걸릴 뻔했습니다. 채워 넣고 `test_sessionstart.py` 에 세 곳 동기화 검사를 더했습니다(22→24건)
- **제외 표시가 문서 일곱 종의 자기 검사를 꺼 놓고 있었습니다.** 훅이 `korean-writing: ignore` 라는 문자열이 어디에 있든 검사를 건너뛰어서, 이 기능을 설명하는 README·CLAUDE.md·CHANGELOG 등이 자기 검사를 통째로 넘겼습니다. 이제 파일 앞 열 줄에 줄 하나로 선 `<!-- korean-writing: ignore -->` 만 지시로 봅니다. 실제로 끄려고 붙인 표시 여섯 개는 전부 1행에 있어 그대로 동작합니다
- `scripts/measure.sh` 가 두 자리 코드를 세지 못했습니다. 집계 정규식이 `K\d` 라 `K10` 줄이 코드별 표에서 빠졌습니다
- 저장소의 산문 문서를 새 판정에 맞춰 고쳤습니다. 연결어미 뒤 쉼표 86개를 지우고 부정 대구를 문서마다 둘 이하로 줄였습니다
- CI 의 자기 검사 대상에 `README.en.md` 를 넣었습니다

- **im-not-ai 의 윤문 파이프라인을 내장했습니다.** 커밋 `9747f036cdc2`(2026-09-06)의 런타임 부분집합을 그대로 넣었습니다. 스킬 셋(`humanize-korean`·`humanize`·`humanize-redo`), 에이전트 셋(진단·윤문·마무리 검토), 파이썬 스크립트 아홉, 규칙집과 참조 문서입니다. `/korean-writing:humanize` 와 `/korean-writing:humanize-redo` 로 부르고 "AI 티 없애줘" 같은 요청에는 `humanize-korean` 스킬이 뜹니다. 가져온 파일에서 고친 것은 스킬 설명의 트리거 문구 하나뿐입니다(NOTICE.md). 개발용 에이전트 여섯은 싣지 않았습니다
- 격리된 HOME 에서 확인했습니다. 설치 뒤 `/humanize` 자동완성에 `/korean-writing:` 셋만 뜨고 `/korean-writing:humanize` 에 AI 티를 몰아넣은 200자 문단을 넣으니 세 콜이 끝까지 돌아 변경률 39%, 등급 A-, 자체검증 6/6 으로 끝났습니다(451초, 1.64달러). 기록은 `docs/samples/humanize-run.md` 에 있습니다
- CI 에 내장 스크립트의 `py_compile` 과 `--help` 실행 확인 단계
- `docs/samples/`: 같은 질문에 상시 규칙을 넣지 않은 답과 넣은 답의 원문(claude-sonnet-5). README 의 전후 발췌가 여기서 나왔습니다
- README 머리에 정답 문장 넷을 전후 표로, 상시 규칙 주입 전후를 실제 답변 발췌로 보였습니다

### 변경

- **README 의 소개를 「한국어가 나오는 네 자리」 하나로 묶었습니다.** 머리에서 같은 말을 되풀이하던 인용구와 다섯 줄 목록을 빼고 「어디에 붙나」 절을 소개 절의 네 자리 표에 합쳤습니다. 증거(전후 문장, 주입 전후, 훅 화면)를 소개 바로 뒤로 올리고 소제목을 붙였으며 글자 수 스크립트 출력은 해당 스킬 절로 옮겼습니다. 배너 넷과 소셜 카드의 문구, `plugin.json` 과 `marketplace.json` 의 설명도 같은 문장으로 맞췄습니다
- 상시 컨텍스트 비용은 약 1,450토큰(상시 규칙 726, 스킬 설명 넷 430, 에이전트 셋 297)입니다. 이 가운데 상시 규칙 726 만 껐다 켜서 잰 값이고 나머지는 `/context` 의 추정입니다. 그 추정이 환경에 따라 흔들린다는 것을 확인해 EVALUATION.md 에 적었습니다. 같은 에이전트 파일이 격리 HOME 에서 297, 실제 사용 환경에서 773 으로 잡힙니다
- 윤문 스크립트는 Python 3.10 이상이 필요합니다. 검사 훅은 그대로 어느 python3 든 됩니다
- SECURITY.md 의 확인 명령이 내장 스크립트까지 봅니다. 네트워크 호출과 외부 프로그램 실행은 없습니다
- 실험 문서 `docs/experiments/skill-vs-imnotai/README.md` 의 결과 줄이 1차 판정(41쌍 22승 19패)에서 멈춰 있어 2차 판정 56쌍 49승 0패까지 적었습니다
- `crafting-effective-readmes` 스킬을 경유본 softaworks/agent-toolkit 대신 원본 joshuadavidthomas/agent-skills(커밋 `516dee7a422b`, 2026-07-20)에서 직접 가져왔습니다. 내용은 같고 경유본에만 있던 스킬 폴더의 `README.md` 를 지웠습니다
- 출판사 편집부 일화는 claude-forge 규칙집에만 있던 내용이라 SKILL.md·README·훅 주석에서 빼고 정답 데이터 G05·G06 을 근거로 적었습니다. NOTICE.md 에서 claude-forge 항목을 뺐습니다

### 제거

- 이 저장소가 쓰던 `humanize-korean` 스킬과 `references/taxonomy.md`·`references/quick-rules.md` 사본. im-not-ai 의 파이프라인이 규칙집째 들어오면서 필요 없어졌습니다

## [1.1.0] - 2026-09-10

### 추가

- **상시 규칙 주입.** 세션이 열릴 때 `hooks-handlers/always-on.md`(약 660토큰)를 한 번 넣는 SessionStart 훅을 넣었습니다. 스킬이 뜨지 않는 평소 답변을 맡습니다. 프롬프트 12개에 조건 2개와 표본 2개로 48건을 생성하고 순서를 바꿔 두 번씩 블라인드로 판정한 결과 24쌍에서 21승 3무 0패였습니다. 기술 오류만 따로 본 검사에서 심각한 오류는 양쪽 0건입니다. 근거는 EVALUATION.md 의 C5 에 있습니다
- `hooks-handlers/test_sessionstart.py`: 주입 내용, 끄기 두 종, 규칙 파일이 없을 때의 안전 종료, 크기 상한을 보는 회귀 20건
- 상시 규칙만 끄는 환경변수 `KOREAN_WRITING_ALWAYS_ON_DISABLED=1`. `KOREAN_WRITING_HOOK_DISABLED=1` 은 그대로 훅 전체를 끕니다

- 공개 저장소 문서: `CONTRIBUTING.md`(한국어·영어), `CODE_OF_CONDUCT.md`(Contributor Covenant 2.1 공식 한국어판), `SECURITY.md`(한국어·영어). SECURITY.md 에는 훅이 무엇을 읽고 무엇을 하지 않는지, 네트워크를 쓰지 않는다는 것을 직접 확인하는 명령 세 가지를 적었습니다
- `CLAUDE.md`: 이 저장소에서 작업하는 Claude 를 위한 규칙. 기준선 명령, 네트워크 금지, 가져온 파일 취급, 버전 정본, 커밋 형식, 판정 기준을 바꿀 때의 실측 의무
- `.claude/settings.json`: 기여자가 공유하는 프로젝트 설정. 검증 명령은 묻지 않고 허용하고 가져온 파일과 `plugin.json` 편집은 확인을 받습니다
- `.github/`: PR 양식, 이슈 양식 세 종(어색한 문장 제보, 버그 신고, 판정 규칙 제안), 이슈 첫 화면의 보안·기여 안내 링크, `CODEOWNERS`, `dependabot.yml`
- `.gitattributes`: 셸 스크립트를 LF 로 고정합니다. CRLF 로 체크아웃되면 훅이 `bad interpreter` 로 죽습니다. 가져온 파일은 GitHub 언어 통계에서 뺍니다
- `.editorconfig`
- `docs/social-preview.png`(1280×640): 링크를 공유할 때 GitHub 이 보여주는 카드 이미지. 저장소 설정에서 올립니다
- CI 작업 셋: `shellcheck`, 버전 표기 일치(`plugin.json`·README 배지·CHANGELOG), 이슈 양식과 워크플로의 YAML 문법

### 변경

- **claude-forge 를 거치지 않습니다.** 규칙집 `references/taxonomy.md` 와 압축 룰북 `references/quick-rules.md` 를 원본인 im-not-ai(커밋 `9747f036cdc2`, 2026-09-06)에서 직접 가져왔습니다. 이전 판은 claude-forge 가 im-not-ai v2.0 에 항목을 더한 것과 forge 가 따로 만든 압축본이었습니다. 항목은 73개에서 84개가 됩니다. `humanize-korean` 스킬은 im-not-ai 의 절차와 철칙을 바탕으로 다시 썼고 길이로 나누던 규칙(5,000자)을 없앴습니다. 승패 의인화·추상 구조어의 근거로 적혀 있던 출판사 편집부 일화는 forge 규칙집에서 온 것이라 빼고 정답 데이터 G05·G06 을 근거로 적었습니다. 훅의 판정은 바뀌지 않았습니다(회귀 43/43). NOTICE.md 에서 claude-forge 항목을 뺐습니다
- **agent-toolkit 도 거치지 않습니다.** `crafting-effective-readmes` 스킬을 경유본 softaworks/agent-toolkit 대신 원본 joshuadavidthomas/agent-skills(커밋 `516dee7a422b`, 2026-07-20)에서 직접 가져왔습니다. 내용은 같고 경유본에만 있던 스킬 폴더의 `README.md` 를 지웠습니다. NOTICE.md 에서 agent-toolkit 항목을 뺐습니다
- **상시 규칙을 넣으며 남겼던 세 가지를 전부 쟀습니다.** 서브에이전트에는 훅도 스킬도 전달되지 않아 플러그인 범위 밖으로 두고 쓰는 쪽 `CLAUDE.md` 에 넣도록 안내합니다. 긴 대화에서는 30턴을 쌓은 뒤에도 주입 조건이 네 쌍 모두 이깁니다. 규칙을 고쳤을 때의 회귀는 `docs/experiments/always-on/regress.sh` 로 봅니다. 근거는 EVALUATION.md 의 「상시 규칙을 넣으며 남겼던 것」에 있습니다
- 실험 장비를 `docs/experiments/always-on/` 에 보존했습니다. 스크립트, 프롬프트 12개, 주입문 초안, 판정 기준과 결과 보고입니다. README 에 `--strict-mcp-config` 와 `--setting-sources ""` 를 빠뜨렸을 때 무슨 일이 생기는지 먼저 적었습니다

- `korean-writing` 스킬이 맡는 범위를 "밖으로 나갈 글" 에서 "글 작성 요청" 으로 넓혔습니다. 슬랙·메일·보고서처럼 남에게 보내는 글만이 아니라 회의록·작업 메모처럼 안에서 보는 글도, 써 달라는 요청이면 스킬이 로드됩니다. 코드만 쓰는 작업은 그대로 대상이 아닙니다. 스킬 설명과 README 두 판, CLAUDE.md, EVALUATION.md 의 표현을 맞췄습니다. 설명이 길어져 `/context` 기준 약 50토큰에서 70토큰이 됐습니다
- **목적을 "Claude Code 가 쓰는 모든 한국어" 로 넓혔습니다.** 이전에는 글 작성 요청과 `.md` 편집만 맡아서 가장 양이 많은 평소 답변이 비어 있었습니다. README 에 어느 자리를 맡고 어느 자리를 안 맡는지 적은 표를 넣었습니다
- EVALUATION.md 의 D2 예산을 상시 500 토큰에서 1,000 토큰으로 올렸습니다. 상시 규칙 662 토큰이 들어가면서 합계가 약 950 이 됩니다. 시험한 규칙을 그대로 넣고 예산을 다시 잡았습니다
- CI 를 macOS 와 Linux 양쪽에서 돌립니다. 훅은 bash 와 python3 만 쓰므로 platform 배지를 `macOS | Linux` 로 고쳤습니다
- CI 워크플로에 `permissions: contents: read` 와 같은 브랜치 중복 실행 취소를 넣고 액션을 v7 로 올렸습니다
- README 두 판에 CI 배지를 넣고 파일 구조와 CI 설명을 실제와 맞췄습니다
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
- PostToolUse 훅: `.md` 편집 시 이번에 쓴 부분만 AI 티 패턴 K1~K8로 검사합니다. 편집을 되돌리지 않고 알리기만 합니다. 코드블록·인라인 코드·URL·표 행은 검사하지 않고 편집분의 한글 비중이 30% 미만이면 한글 비중 30% 이상인 줄만 모아 다시 봅니다. 줄표는 이번 편집에 하나라도 있으면 파일 전체 개수로 판정합니다(문단씩 고치며 쌓이는 것). `~~~` 코드블록과 HTML 주석도 검사에서 뺍니다. K7 은 "죽다" 를 잡지 않고 K8 은 `~에 대해`·`~를 통해` 횟수를 세지 않습니다(실제 문서 143개 실측)
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
