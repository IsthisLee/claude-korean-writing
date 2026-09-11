# 도움 받는 곳

<p><strong>한국어</strong> · <a href="#getting-help">English</a></p>

무엇을 물어볼지에 따라 가는 곳이 다릅니다. 이슈를 열기 전에 여기서 골라 주세요.

| 상황                                            | 가는 곳                                                                                                        |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 설치와 사용법을 모르겠다                        | [README](README.md) 의 설치 절부터 봅니다                                                                        |
| 훅이 왜 이 문장을 걸었는지 모르겠다             | [EVALUATION.md](EVALUATION.md) 에 판정 규칙 K1~K10 과 각각의 실측 근거가 있습니다                                |
| 훅을 끄고 싶다                                  | `/plugin` 에서 `edit_check` 를 끕니다. 환경변수도 듣습니다([SECURITY.md](SECURITY.md))                          |
| 사람이 쓴 문장을 훅이 잘못 걸었다               | [오탐 이슈](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=awkward-sentence.yml)          |
| 훅이 놓친 AI 티가 있다                          | [규칙 제안 이슈](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=rule.yml)                 |
| 훅이나 스크립트가 죽는다                        | [버그 이슈](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=bug.yml)                       |
| 취약점을 찾았다                                 | 공개 이슈로 올리지 말고 [비공개 신고](https://github.com/IsthisLee/claude-korean-writing/security/advisories/new)  |
| 규칙을 어떻게 잡을지 의논하고 싶다              | [Discussions](https://github.com/IsthisLee/claude-korean-writing/discussions)                                    |
| 고쳐서 보내고 싶다                              | [CONTRIBUTING.md](CONTRIBUTING.md)                                                                               |

## 이슈를 열 때 넣어 주시면 좋은 것

오탐과 버그는 재현이 전부입니다. 걸린 문장을 그대로, `plugin/scripts/check.sh` 의 출력을 그대로 붙여 주세요. 요약하면 어느 규칙이 걸렸는지 저희 쪽에서 다시 찾아야 합니다.

이 저장소는 한 사람이 짬을 내 관리합니다. 답이 며칠 늦을 수 있습니다. 보안 신고만 영업일 기준 5일 안에 접수 여부를 알려 드립니다.

---

<a id="getting-help"></a>

# Getting help

<p><a href="#도움-받는-곳">한국어</a> · <strong>English</strong></p>

Where to go depends on what you need. Please pick from this list before opening an issue.

| Situation                                     | Where to go                                                                                                       |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Installing or using the plugin                | Start with the install section of the [README](README.en.md)                                                        |
| Not sure why the hook flagged a sentence      | [EVALUATION.md](EVALUATION.md) lists rules K1–K10 and the measurements behind each                                  |
| You want to turn the hook off                 | Toggle `edit_check` in `/plugin`. Environment variables work too ([SECURITY.md](SECURITY.md))                     |
| The hook flagged human-written prose          | [False positive](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=awkward-sentence.yml)        |
| The hook missed an AI tell                    | [Rule proposal](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=rule.yml)                     |
| A hook or script crashes                      | [Bug report](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=bug.yml)                         |
| You found a vulnerability                     | Do not open a public issue. [Report privately](https://github.com/IsthisLee/claude-korean-writing/security/advisories/new) |
| You want to discuss how a rule should work    | [Discussions](https://github.com/IsthisLee/claude-korean-writing/discussions)                                       |
| You want to send a patch                      | [CONTRIBUTING.en.md](CONTRIBUTING.en.md)                                                                            |

## What helps in an issue

For false positives and bugs, reproduction is everything. Paste the flagged sentence verbatim and the raw output of `plugin/scripts/check.sh`. A summary means we have to work out which rule fired.

One person maintains this repository in spare time, so a reply may take a few days. Security reports are the exception: you get an acknowledgement within 5 business days.
