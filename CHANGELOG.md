# Changelog

이 프로젝트의 눈에 띄는 변경을 기록합니다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를, 버전은 [SemVer](https://semver.org/lang/ko/)를 따릅니다.

## [Unreleased]

### 바뀜

- 목적을 "번역투를 걷어낸다"에서 "Claude Code가 쓰는 한국어의 품질을 맡는다"로 다시 잡았습니다. `plugin.json`·`marketplace.json`의 설명과 `EVALUATION.md`의 목적 문장도 같이 바꿨습니다
- README를 참고 저장소(claude-forge, harness, orca, archify)의 요소와 쓰는 방식에 맞춰 합니다체로 다시 썼습니다. 배너, 앵커 내비, 정의·비유 인용구, 선택 표, 동작 단계표, 이웃 도구 관계, FAQ, 기여 요청
- 훅이 표 행 전체를 검사에서 제외합니다. 전/후 교정표의 나쁜 예가 위반으로 잡히던 문제
- 버전의 정본을 `plugin.json` 한 곳으로 두고 `marketplace.json`의 중복 버전을 뺐습니다

### 추가

- 영어판 README(`README.en.md`)와 언어 전환 줄
- 릴리스 노트(`CHANGELOG.md`)와 릴리스 스크립트(`scripts/release.sh`)
- 훅 출력 데모 이미지(`docs/hook-output.svg`), 파일별 출처 표
- 회귀 케이스 1건(표 안의 교정 예시는 위반이 아니다). 27 → 28

### 고침

- 설치 명령의 계정·저장소 이름(`IsthisLee/claude-korean-writing`)과 `plugin.json`의 저장소 주소
- LICENSE에 빠져 있던 `skills/humanize-korean/SKILL.md`와 훅의 출처 표기

## [0.1.0] - 2026-09-09

### 추가

- `korean-writing` 스킬: 밖으로 나갈 글을 처음 쓸 때 번역투·AI 관용구를 피하는 원칙과 교정 예시
- `humanize-korean` 스킬: 이미 쓴 글을 사실 불변으로 다듬는 윤문 (claude-forge에서 이식)
- `korean-character-count` 스킬: grapheme 기준 글자 수 (k-skill에서 이식)
- PostToolUse 훅: `.md` 편집 시 AI 티 패턴 K1~K8 검사. 편집을 되돌리지 않고 알리기만 합니다
- 실제 실패 문장 10건·정상 문장 5건으로 만든 검증(`EVALUATION.md`)과 회귀 테스트 27건
- LICENSE에 claude-forge·k-skill 원 저작권 표시

[Unreleased]: https://github.com/IsthisLee/claude-korean-writing/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/IsthisLee/claude-korean-writing/releases/tag/v0.1.0
