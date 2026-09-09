<p align="center">
  <b>korean-writing</b>
</p>

<p align="center">
  번역투와 AI 관용구를 <b>처음 쓸 때부터</b> 걷어내는 Claude Code 플러그인
</p>

<p align="center">
  <img alt="MIT" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Claude Code Plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2">
  <img alt="version" src="https://img.shields.io/badge/version-0.1.0-lightgrey">
  <img alt="network" src="https://img.shields.io/badge/network-none-success">
</p>

---

## 무엇이 달라지나

같은 내용을 쓰는데 문장만 바뀐다. 아래는 실제로 생성됐던 문장과 그 교정이다.

| 전                                                                  | 후                                                                 |
| ------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 변경이 실패하면 화면이 **굳어** 취소도 안 됩니다                    | 변경이 실패하면 화면이 **멈춰** 취소도 안 됩니다                   |
| 점검 장치가 장비를 계속 **넘어뜨리고 있었습니다**                   | 점검 장치 **때문에** 장비가 계속 **멈췄습니다**                    |
| 그대로 내보냈으면 탈이 날 **것들이었습니다**                        | 그대로 내보냈으면 탈이 날 **문제였습니다**                         |
| **축이** 두 개다. 세 **갈래**로 나뉜다                              | **기준이** 두 개다. 세 **가지**로 나뉜다                           |
| 충돌하면 상위 문서가 **이깁니다**                                   | 충돌하면 상위 문서를 **따릅니다**                                  |
| 원인은 힙 부족이 아니라 **—** 실측해보니 **—** 설정이 안 먹혔습니다 | 원인은 힙 부족이 아니었습니다**.** 실측해보니 설정이 안 먹혔습니다 |

왼쪽은 문법적으로 맞다. 그런데 한국어로 읽으면 걸린다. 영어 문장을 옮긴 흔적이기 때문이다.

## 빠른 시작

```bash
claude plugin marketplace add IsthisLee/claude-korean-writing
claude plugin install korean-writing
```

설치하면 끝난다. 설정할 것이 없다.

**필요한 것**

- Claude Code (2.1.266 에서 확인)
- `python3` (훅), `node` (글자 수 스크립트). 별도 패키지는 설치하지 않는다
- 훅이 bash 스크립트라 macOS 에서 확인했다. Windows 는 확인하지 않았다

## 사용법

설치 후 평소처럼 말하면 된다. 스킬은 요청 내용을 보고 스스로 로드되고, 직접 부르려면 슬래시 이름을 쓴다.

**처음 쓸 때** `/korean-writing`

```
운영 담당자에게 보낼 옵션 변경 안내문 써줘. 슬랙에 캐주얼하게.
```

슬랙·메일·공지·보고서·README 처럼 밖으로 나갈 글이면 자동으로 걸린다. 다 쓰고 고치는 것이 아니라 처음부터 규칙을 적용한다.

**이미 쓴 글 다듬을 때** `/korean-writing:humanize-korean`

```
아래 글 번역투만 고쳐줘. 사실과 숫자는 그대로 두고.
(글 붙여넣기)
```

주요 교정 3~6개를 전 → 후로 보여주고, 변경률이 50% 를 넘으면 결과 대신 그 사실을 알린다.

**글자 수 셀 때** `/korean-writing:korean-character-count`

```
이 자기소개서 공백 포함 몇 자야? 1,000자 제한이야.
```

grapheme 기준으로 세고 줄 수와 바이트를 함께 낸다. 세는 일은 스크립트가 하므로 모델이 어림하지 않는다.

**`.md` 를 고칠 때** 훅이 자동으로 검사한다. 실제로는 이렇게 보인다.

<p align="center"><img src="docs/hook-output.svg" alt="훅이 K1·K2·K3·K4·K7 을 잡은 실제 출력" width="860"></p>

## 훅이 잡는 것

`.md` 를 편집하면 **이번에 쓴 부분만** 검사한다. 파일 전체를 보면 예전 표현이 매 편집마다 다시 걸려 소음이 된다.

| 코드 | 패턴             | 예                                         | 임계      |
| ---- | ---------------- | ------------------------------------------ | --------- |
| `K1` | 줄표 삽입구      | `가 — 나 — 다`                             | 4개       |
| `K2` | 추상 구조어      | `축`·`갈래`·`결이 다`·`레이어`             | 3회       |
| `K3` | 번역투 `것` 구문 | `탈이 날 것들이었다`                       | 1회       |
| `K4` | AI 관용구        | `결론적으로`·`혁신적`·`시사하는 바가 크다` | 1회       |
| `K5` | 기계적 병렬      | `첫째 … 둘째 …`                            | 동시 등장 |
| `K6` | 승패 의인화      | `규칙이 이깁니다`                          | 2회       |
| `K7` | 사물 의인화      | `화면이 굳어`·`장비를 넘어뜨리고`          | 1회       |
| `K8` | 번역투           | `되어지`·`가지고 있다`·`~에 대해` 남발     | 항목별    |

코드블록, 인라인 코드, URL, 표 행은 검사하지 않는다. 한글이 20자 미만이거나 비중이 30% 미만이면 대상이 아니다.

편집을 되돌리지는 않는다. 걸린 항목을 알려 고치게 한다.

## 왜 이 패턴인가

**외부 출판사 편집부의 지적이 근거다.** 단행본 초고 검토에서 줄표 삽입구와 `이깁니다` 류를 "요즘 원고에 공통적으로 나온다. 잘못된 표현은 아니지만 AI 생성 의심을 살 수 있다"며 짚었다. 서로 다른 저자의 원고 2건에서 **같은 자리에 같은 `이깁니다`** 가 나오기도 했다.

문법적으로 맞아도 AI 서명처럼 굳으면 피한다. 그것이 이 플러그인의 기준이다.

**목적은 탐지기 우회가 아니다.** 어색한 번역투를 자연스러운 한국어로 고치는 것이고, 누가 초안을 썼는지와 무관한 품질 개선이다.

## 구성

세 층으로 나뉜다. 평소 비용은 낮게 두고 깊은 판정만 큰 파일로 넘긴다.

```
SKILL.md                        4.6 KB   글쓰기 요청에 로드. 원칙·품질 바·교정 예시
references/quick-rules.md       9.7 KB   다듬기 시작할 때. 압축 룰북
references/taxonomy.md         66   KB   판정이 애매할 때만. 10분류 73항목
```

`references/` 두 파일은 claude-forge 에서 그대로 가져왔다. 파일별 출처는 「출처」에 있다.

스킬은 셋이다.

| 스킬                     | 언제                            | 무엇                                  |
| ------------------------ | ------------------------------- | ------------------------------------- |
| `korean-writing`         | 밖으로 나갈 글을 **처음 쓸 때** | 원칙, 품질 바, 서식 규칙              |
| `humanize-korean`        | 이미 써둔 글을 **다듬을 때**    | 사실 불변, 변경률 50% 상한, 반환 형식 |
| `korean-character-count` | 글자 수를 **정확히 셀 때**      | grapheme·줄·바이트. 외부 호출 없음    |

`humanize-korean` 은 사실을 한 글자도 바꾸지 않는다. 수치·고유명사·인용·날짜는 그대로 두고 문체만 손본다. 변경률이 50% 를 넘으면 결과를 내놓지 않고 알린다. 그건 윤문이 아니라 재작성이다.

## 검증

합격 기준과 측정 결과는 [`EVALUATION.md`](./EVALUATION.md) 에 있다.

| 기준               | 결과           |
| ------------------ | -------------- |
| 위반 검출          | 10 / 10        |
| 정상 오탐          | 0 / 5          |
| 실문서 오탐        | 1 / 269 (0.4%) |
| 분류 정확          | 10 / 10        |
| 변이 검출          | 15 / 15        |
| 회귀 테스트        | 28 / 28        |
| 외부 호출          | 0 건           |
| 상시 컨텍스트 비용 | 416 토큰       |

정답 데이터는 [`hooks-handlers/ground-truth.json`](./hooks-handlers/ground-truth.json) 에 있다. **실제로 생성됐던 어색한 문장 10건과 같은 맥락의 정상 문장 5건**이고, 합성 예문이 아니다.

**오탐을 미탐보다 무겁게 잡았다.** 게이트가 정상 작업을 막으면 사람이 게이트를 꺼버리기 때문이다.

변이 테스트는 훅에 결함을 주입하고 회귀 테스트가 잡는지 확인한다. 정규식 대안 하나가 조용히 빠지는 경우까지 검출한다.

```bash
python3 hooks-handlers/test_posttooluse.py
```

## 개발

저장소를 `~/.claude/skills/` 로 링크하면 `korean-writing@skills-dir` 로 자동 로드된다. 마켓플레이스를 거치지 않으므로 고치는 즉시 반영된다.

마켓플레이스로 설치한 사본이 있으면 그쪽이 우선하고 링크 사본은 로드되지 않는다. 개발 전에 `claude plugin uninstall korean-writing` 으로 설치본을 뺀다.

```bash
git clone https://github.com/IsthisLee/claude-korean-writing.git
ln -s "$PWD/claude-korean-writing" ~/.claude/skills/korean-writing
claude plugin list                            # loaded 확인
python3 hooks-handlers/test_posttooluse.py    # 회귀 28건
```

패턴을 추가하려면 세 곳을 함께 고친다.

1. `hooks-handlers/posttooluse.sh` 에 검사 추가
2. `hooks-handlers/ground-truth.json` 에 실제 문장 추가
3. `hooks-handlers/test_posttooluse.py` 에 케이스 추가 — 오탐 케이스를 먼저

## 적용 밖

- **격식이 요건인 글** — 계약서, 약관, 법률 문서, 공문. 딱딱한 것이 그 글의 요건이다
- 코드, 로그, 명령어, 직접 인용, 고유명사, 영어 원문
- 맞춤법·띄어쓰기 검사 — 이 플러그인은 문체만 본다

정규식은 알려진 패턴만 잡는다. 새로운 어색함은 사람이 찾아 목록에 넣어야 한다.

## 자주 묻는 것

<details>
<summary><b>훅이 편집을 되돌리나?</b></summary>

아니다. 걸린 항목을 stderr 로 알리고 종료 코드 2 를 낼 뿐 파일은 건드리지 않는다. 고칠지는 사람이 정한다.

</details>

<details>
<summary><b>내 글이 외부로 나가나?</b></summary>

아니다. 훅은 `python3` 정규식이고 글자 수 스크립트는 `node:fs` 만 쓴다. 네트워크 호출이 한 건도 없다. 원문을 외부 서버로 보내는 `korean-spell-check` 를 가져오지 않은 이유이기도 하다.

</details>

<details>
<summary><b>오탐이 나면?</b></summary>

격식 문서(계약·약관·법률)면 무시하면 된다. 훅 메시지가 그렇게 안내한다. 패턴 자체가 틀렸으면 `hooks-handlers/test_posttooluse.py` 에 그 문장을 오탐 케이스로 넣고 훅을 고친다(「개발」). 훅째 끄려면 `claude plugin disable korean-writing`.

</details>

<details>
<summary><b>토큰을 얼마나 쓰나?</b></summary>

상시로 드는 것은 스킬 설명 416 토큰뿐이다. 스킬 본문은 글쓰기 요청이 있을 때만 로드되고, 훅은 LLM 을 부르지 않는 정규식이다. 답변마다 다시 검토하는 Stop 훅은 그래서 두지 않았다.

</details>

<details>
<summary><b>왜 <code>.md</code> 파일만 검사하나?</b></summary>

훅은 파일 편집 도구에만 걸린다. 슬랙 메시지처럼 파일이 아닌 답변은 훅이 볼 수 없고, 그건 처음 쓸 때 스킬이 맡는다. 이번에 쓴 부분의 한글이 20자 미만이거나 비중이 30% 미만이면 건너뛴다.

</details>

## 출처

이 플러그인은 [claude-forge](https://github.com/sangrokjung/claude-forge) 의 한국어 산문 품질 부분에서 출발했다. 규칙집과 윤문 스킬을 거기서 가져왔고, 편집 훅은 Forge 의 `emdash-slop-guard` 에서 착안했다. 여기서 더한 것은 처음 쓸 때 쓰는 `korean-writing` 스킬, 훅의 K2~K8, 실제 실패 문장으로 만든 검증이다.

| 파일                                           | 원본                                                            | 가져온 정도                                                                    |
| ---------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `references/taxonomy.md`                       | claude-forge `reference/ai-tell-taxonomy.md`                    | 그대로                                                                         |
| `references/quick-rules.md`                    | claude-forge `skills/humanize-korean/references/quick-rules.md` | 그대로                                                                         |
| `skills/humanize-korean/SKILL.md`              | claude-forge `skills/humanize-korean/SKILL.md`                  | 한국어로 옮기고 구조 정리. 절차와 철칙은 원본과 같다                           |
| `hooks-handlers/posttooluse.sh`                | claude-forge `hooks/emdash-slop-guard.sh`                       | 착안. 발동 조건(`.md` 편집, 한글 비중)과 K1 정규식이 같고 나머지는 여기서 썼다 |
| `skills/korean-character-count/scripts/*.js`   | [k-skill](https://github.com/NomaDamas/k-skill)                 | 그대로                                                                         |
| `skills/korean-character-count/instruction.md` | k-skill                                                         | 실행 경로만 `node` 로 바꿈                                                     |
| `skills/korean-character-count/SKILL.md`       | k-skill                                                         | 원본을 바탕으로 다시 씀                                                        |

둘 다 MIT 이고 [`LICENSE`](./LICENSE) 에 원 저작권 표시와 파일별 범위를 남겼다.

`korean-spell-check` 는 가져오지 않았다. 검사할 원문을 외부 서버로 전송하고, 그 서비스 약관이 개인·학생 무료로 제한한다.

## 라이선스

[MIT](./LICENSE)
