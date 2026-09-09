# Changelog

이 프로젝트의 눈에 띄는 변경을 기록합니다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를, 버전은 [SemVer](https://semver.org/lang/ko/)를 따릅니다. 첫 릴리스가 1.0.0 입니다.

## [Unreleased]

### 추가

- 공개 저장소 문서: `CONTRIBUTING.md`(한국어·영어), `CODE_OF_CONDUCT.md`(Contributor Covenant 2.1 공식 한국어판), `SECURITY.md`(한국어·영어). SECURITY.md 에는 훅이 무엇을 읽고 무엇을 하지 않는지, 네트워크를 쓰지 않는다는 것을 직접 확인하는 명령 세 가지를 적었습니다
- `CLAUDE.md`: 이 저장소에서 작업하는 Claude 를 위한 규칙. 기준선 명령, 네트워크 금지, 가져온 파일 취급, 버전 정본, 커밋 형식, 판정 기준을 바꿀 때의 실측 의무
- `.claude/settings.json`: 기여자가 공유하는 프로젝트 설정. 검증 명령은 묻지 않고 허용하고, 가져온 파일과 `plugin.json` 편집은 확인을 받습니다
- `.github/`: PR 양식, 이슈 양식 두 종(버그 신고, 판정 규칙 제안), 이슈 첫 화면의 보안·기여 안내 링크, `CODEOWNERS`, `dependabot.yml`
- `.gitattributes`: 셸 스크립트를 LF 로 고정합니다. CRLF 로 체크아웃되면 훅이 `bad interpreter` 로 죽습니다. 가져온 파일은 GitHub 언어 통계에서 뺍니다
- `.editorconfig`
- CI 작업 셋: `shellcheck`, 버전 표기 일치(`plugin.json`·README 배지·CHANGELOG), 이슈 양식과 워크플로의 YAML 문법

### 변경

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

[Unreleased]: https://github.com/IsthisLee/claude-korean-writing/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/IsthisLee/claude-korean-writing/releases/tag/v1.0.0
