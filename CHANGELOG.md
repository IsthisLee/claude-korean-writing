# Changelog

이 프로젝트의 눈에 띄는 변경을 기록합니다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를, 버전은 [SemVer](https://semver.org/lang/ko/)를 따릅니다. 첫 릴리스가 1.0.0 입니다.

## [Unreleased]

### 추가

- `korean-writing` 스킬: 밖으로 나갈 글을 처음 쓸 때 번역투·AI 관용구를 피하는 원칙과 교정 예시
- `humanize-korean` 스킬: 이미 쓴 글을 사실 불변으로 다듬는 윤문 (claude-forge에서 이식)
- `korean-character-count` 스킬: grapheme 기준 글자 수 (k-skill에서 이식)
- `crafting-effective-readmes` 스킬: README의 절 구성을 프로젝트 유형(오픈소스·개인·사내·설정)에 맞춰 잡습니다 (agent-toolkit에서 이식)
- PostToolUse 훅: `.md` 편집 시 이번에 쓴 부분만 AI 티 패턴 K1~K8로 검사합니다. 편집을 되돌리지 않고 알리기만 합니다. 코드블록·인라인 코드·URL·표 행은 검사하지 않고, 편집분의 한글 비중이 30% 미만이면 한글 비중 30% 이상인 줄만 모아 다시 봅니다
- 훅 끄기 수단 두 가지. 파일 머리의 `<!-- korean-writing: ignore -->` 표시(그 파일만), 환경변수 `KOREAN_WRITING_HOOK_DISABLED=1`(세션 전체). python3 가 없으면 검사 없이 통과합니다
- `scripts/check.sh`: 이미 써 둔 문서를 통째로 훅과 같은 기준으로 검사합니다. 걸리면 종료 코드 1이라 CI·pre-commit 에 그대로 씁니다
- `scripts/release.sh`: 버전·CHANGELOG·README 배지·커밋·태그를 한 번에. 버전의 정본은 `plugin.json` 한 곳입니다
- 검증 기준(`EVALUATION.md`): 실제 실패 문장 10건과 정상 문장 5건으로 만든 훅 정확도 기준, 스킬 트리거 기준, 사용하는 사람의 기준. 회귀 테스트 36건
- GitHub Actions 워크플로(`.github/workflows/validate.yml`): push와 PR마다 회귀 테스트, 매니페스트 JSON, 훅 실행 비트, 한국어 문서의 자기 훅 통과, 글자 수 스크립트 스모크, `claude plugin validate`를 돌립니다
- README 한국어판·영어판, 훅 출력 데모 이미지(`docs/hook-output.svg`)
- 제3자 고지(`NOTICE.md`): im-not-ai·claude-forge·k-skill·agent-toolkit 의 원 저작권 표시

[Unreleased]: https://github.com/IsthisLee/claude-korean-writing/commits/main
