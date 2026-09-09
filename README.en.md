<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/banner.en.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/banner-light.en.svg">
  <img src="docs/banner.en.svg" alt="korean-writing" width="100%">
</picture>

<p align="center">
  <a href="README.md">한국어</a> · <strong>English</strong>
</p>

<p align="center">
  <strong>The Korean output quality plugin for Claude Code.</strong><br>
  Catches problems as the text is written, polishes text that already exists, and checks every <code>.md</code> edit.
</p>

<p align="center">
  <img alt="MIT" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Claude Code Plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2">
  <img alt="version" src="https://img.shields.io/badge/version-0.1.0-lightgrey">
  <img alt="network" src="https://img.shields.io/badge/network-none-success">
  <img alt="platform" src="https://img.shields.io/badge/platform-macOS-lightgrey">
</p>

<p align="center">
  <a href="#what-is-it">What is it</a> ·
  <a href="#install">Install</a> ·
  <a href="#how-to-use">How to use</a> ·
  <a href="#what-the-hook-catches">What the hook catches</a> ·
  <a href="#verification">Verification</a> ·
  <a href="#faq">FAQ</a>
</p>

> **v0.2.0 (2026-09-10)**: Reframed the purpose as "owning the quality of the Korean that Claude Code writes" and rewrote the README around it. Added this English edition, release notes, and a release script. Details: [CHANGELOG.md](CHANGELOG.md) (Korean).

> **korean-writing owns the quality of Claude Code's Korean output.** Say **"운영팀에 보낼 안내문 써줘"** (write a notice for the ops team) and the rules load on their own, so the text comes out as natural Korean from the first draft. Edit a `.md` file and a hook flags translation-ese and AI idioms. Nothing you write leaves your machine.

## What is it?

Claude Code writes grammatical Korean. It still reads wrong, because the sentences keep the shape of the English underneath. Below are sentences it actually produced, and their corrections.

| Before                                                              | After                                                              | What was wrong                                                                      |
| ------------------------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| 변경이 실패하면 화면이 **굳어** 취소도 안 됩니다                    | 변경이 실패하면 화면이 **멈춰** 취소도 안 됩니다                   | "The screen freezes": a calque. Korean says the screen _stops_                      |
| 점검 장치가 장비를 계속 **넘어뜨리고 있었습니다**                   | 점검 장치 **때문에** 장비가 계속 **멈췄습니다**                    | "Kept knocking the server over": a personified object                               |
| 그대로 내보냈으면 탈이 날 **것들이었습니다**                        | 그대로 내보냈으면 탈이 날 **문제였습니다**                         | "Things that would have...": the empty noun 것 standing in for a real one           |
| **축이** 두 개다. 세 **갈래**로 나뉜다                              | **기준이** 두 개다. 세 **가지**로 나뉜다                           | "Two axes, three branches": abstract structure words where a plain noun works       |
| 충돌하면 상위 문서가 **이깁니다**                                   | 충돌하면 상위 문서를 **따릅니다**                                  | "The upper document wins": a win/lose metaphor that an editor flagged as an AI tell |
| 원인은 힙 부족이 아니라 **—** 실측해보니 **—** 설정이 안 먹혔습니다 | 원인은 힙 부족이 아니었습니다**.** 실측해보니 설정이 안 먹혔습니다 | An em-dash interjection. Korean punctuation does not do this                        |

Nothing in the left column is ungrammatical. It is simply not what a person writing in Korean produces. This plugin attaches to the four points where such sentences leave Claude Code.

| Where                         | What attaches                  | What it does                                                                                                |
| ----------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| Writing a first draft         | `korean-writing` skill         | Loads on requests for Slack messages, mail, notices, and reports, and applies the rules from the first line |
| Fixing existing text          | `humanize-korean` skill        | Changes style only; facts and numbers stay untouched                                                        |
| Editing a `.md` file          | PostToolUse hook               | Scans what was just written for eight AI-tell patterns and reports them                                     |
| Counting under a length limit | `korean-character-count` skill | A script counts, so the model does not estimate                                                             |

> Think of a copy editor sitting next to the draft. Instead of fixing the text after it is finished, they point at the awkward sentence while it is being written.

## Install

```bash
claude plugin marketplace add IsthisLee/claude-korean-writing
claude plugin install korean-writing
```

That is the whole setup. There is nothing to configure.

**Requirements**

- Claude Code (verified on 2.1.266)
- `python3` for the hook and `node` for the character-count script. No extra packages
- The hook is a bash script. Verified on macOS; Windows is untested

## How to use

Talk to Claude Code as usual. The skills load themselves from the request; to call one directly, use its slash name.

| You want to                              | Say something like                                                                                                              | Direct call                              |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Write outgoing text well from the start  | "운영팀에 보낼 옵션 변경 안내문 써줘. 슬랙에 캐주얼하게." (write a casual Slack notice to the ops team about the option change) | `/korean-writing`                        |
| Strip translation-ese from existing text | "아래 글 번역투만 고쳐줘. 사실과 숫자는 그대로 두고." (fix only the translation-ese below; keep facts and numbers)              | `/korean-writing:humanize-korean`        |
| Count characters exactly                 | "이 자기소개서 공백 포함 몇 자야? 1,000자 제한이야." (how many characters including spaces? the limit is 1,000)                 | `/korean-writing:korean-character-count` |

The polish skill shows its three to six main edits as before → after, and if the change rate passes 50% it reports that instead of returning a result: at that point it is a rewrite, not a polish. Character counting uses grapheme clusters (what a reader sees as one character) and reports lines and bytes alongside.

Edit a `.md` file and the hook checks it automatically. This is what it looks like:

<p align="center"><img src="docs/hook-output.svg" alt="Hook output flagging K1, K2, K3, K4 and K7" width="860"></p>

It never reverts the edit. It lists what it found and how to fix it; whether to fix it is up to you.

## How it works

| Step      | What happens                                                                                                                                |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 Request | A request such as "write a notice" is matched against the skill description. That description is the only thing loaded at all times         |
| 2 Load    | On a match, `SKILL.md` (principles, quality bar, worked corrections) is read and the text is written under those rules                      |
| 3 Judge   | When polishing, `references/quick-rules.md` is the first pass; only ambiguous cases open `references/taxonomy.md` (10 categories, 73 items) |
| 4 Edit    | Saving a `.md` runs the hook over the part just written, using regular expressions; hits go to stderr. No LLM call                          |

The three tiers exist for cost. Most of the time only the one-line description is loaded; the large files open only when a hard call has to be made.

```
SKILL.md                        4.6 KB   loaded on writing requests: principles, quality bar, corrections
references/quick-rules.md       9.7 KB   when polishing starts: compressed rulebook
references/taxonomy.md         66   KB   only for hard calls: 10 categories, 73 items
```

## What the hook catches

Editing a `.md` checks **only the part you just wrote**. Checking the whole file would re-flag old wording on every edit and turn the hook into noise.

| Code | Pattern                            | Example                                                                                     | Threshold    |
| ---- | ---------------------------------- | ------------------------------------------------------------------------------------------- | ------------ |
| `K1` | Em-dash interjection               | `가 — 나 — 다`                                                                              | 4            |
| `K2` | Abstract structure words           | `축`·`갈래`·`결이 다`·`레이어` (axis, branch, "different grain", layer)                     | 3            |
| `K3` | Translation-ese `것` constructions | `탈이 날 것들이었다`                                                                        | 1            |
| `K4` | AI idioms                          | `결론적으로`·`혁신적`·`시사하는 바가 크다` (in conclusion, innovative, "highly suggestive") | 1            |
| `K5` | Mechanical enumeration             | `첫째 … 둘째 …` (firstly... secondly...)                                                    | both present |
| `K6` | Win/lose personification           | `규칙이 이깁니다` (the rule wins)                                                           | 2            |
| `K7` | Personified objects                | `화면이 굳어`·`장비를 넘어뜨리고` (the screen freezes, knocks the server over)              | 1            |
| `K8` | Translation-ese                    | `되어지`·`가지고 있다`·overused `~에 대해` (double passive, "have", "regarding")            | per item     |

Code blocks, inline code, URLs, and table rows are skipped. If the edited part has fewer than 20 Hangul characters, or Hangul is under 30% of it, the hook does not apply.

## Why these patterns

**The evidence is a publisher's editorial desk.** Reviewing a book manuscript, the editors singled out em-dash interjections and the `이깁니다` (wins) family: "these show up across manuscripts lately; not wrong, but they invite suspicion of AI generation." Two manuscripts by different authors had the same `이깁니다` in the same spot.

Grammatical or not, an expression that has hardened into an AI signature is avoided. That is the plugin's standard.

**The goal is not evading detectors.** It is turning awkward translation-ese into natural Korean, which improves the text regardless of who drafted it.

## Verification

Pass criteria and measurements are in [`EVALUATION.md`](./EVALUATION.md) (Korean).

| Criterion                         | Result         |
| --------------------------------- | -------------- |
| Violations detected               | 10 / 10        |
| False positives on clean text     | 0 / 5          |
| False positives on real documents | 1 / 269 (0.4%) |
| Correct classification            | 10 / 10        |
| Mutations caught                  | 15 / 15        |
| Regression tests                  | 28 / 28        |
| Network calls                     | 0              |
| Always-on context cost            | 416 tokens     |

The ground truth is [`hooks-handlers/ground-truth.json`](./hooks-handlers/ground-truth.json): **ten awkward sentences that were actually generated, plus five clean sentences from the same context.** No synthetic examples.

**False positives weigh more than misses.** A check that blocks normal work gets switched off.

Mutation testing injects defects into the hook and confirms the regression suite catches them, down to a single alternative silently dropping out of a regular expression.

```bash
python3 hooks-handlers/test_posttooluse.py
```

## Neighbors

| Tool                                                        | What it is                                                                                                      | How this plugin relates                                                                                                                                                                                |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [claude-forge](https://github.com/sangrokjung/claude-forge) | A full Claude Code framework: agents, commands, hooks, rules. Its Korean prose guardrails are one part of it    | This plugin is that part, extracted. If you installed Forge in full with `install.sh`, you already have the same hook and polish skill and do not need this. Running both duplicates the em-dash check |
| [k-skill](https://github.com/NomaDamas/k-skill)             | A collection of 100+ skills for Korean users, from character counting and spell checking to transit and weather | Only the character-count skill was taken. The spell checker sends text to an external server, so it was left out; install it from k-skill if you need it, knowing that                                 |
| Spelling and spacing checkers                               | Check spelling                                                                                                  | This plugin checks style only. The two do not overlap, so use both                                                                                                                                     |

## Out of scope

- **Text where formality is the requirement**: contracts, terms of service, legal documents, official letters. Stiffness is the point there
- Code, logs, commands, direct quotations, proper nouns, English source text
- Spelling and spacing. This plugin looks at style only

Regular expressions catch known patterns. New kinds of awkwardness have to be found by a person and added to the list.

## FAQ

<details>
<summary><b>Q1. Does 10/10 detection mean it catches everything?</b></summary>

**A.** No. The patterns were built from those ten sentences, so catching them is expected; that number is a regression check. The meaningful number is the false-positive side: 269 real documents pushed through the hook produced one hit, and that one was a true positive with eight em-dashes. Regular expressions catch known patterns and miss new ones.

**Evidence:**

- [`EVALUATION.md`](./EVALUATION.md), criteria A1 and A3
- [`hooks-handlers/ground-truth.json`](./hooks-handlers/ground-truth.json)

</details>

<details>
<summary><b>Q2. Does the hook revert my edit?</b></summary>

**A.** No. It prints what it found to stderr and exits with code 2. The file is untouched; fixing it is your call.

</details>

<details>
<summary><b>Q3. Does my text leave my machine?</b></summary>

**A.** No. The hook is `python3` regular expressions and the counting script uses only `node:fs`. There is not a single network call. That is also why `korean-spell-check`, which posts text to an external server, was not brought in.

</details>

<details>
<summary><b>Q4. What if it flags something wrongly?</b></summary>

**A.** For formal documents (contracts, terms, legal), ignore it; the hook message says so. If the pattern itself is wrong, add the sentence to `hooks-handlers/test_posttooluse.py` as a false-positive case and fix the hook (see Development). To turn the hook off entirely: `claude plugin disable korean-writing`.

</details>

<details>
<summary><b>Q5. How many tokens does it cost?</b></summary>

**A.** The only always-on cost is the 416-token skill description. Skill bodies load only on writing requests, and the hook is regular expressions with no LLM call. A Stop hook that re-reviews every reply was deliberately left out for the same reason.

</details>

<details>
<summary><b>Q6. Why only <code>.md</code> files?</b></summary>

**A.** The hook fires on file-editing tools only. A Slack message in a reply is not a file, so the hook cannot see it; that case belongs to the writing skill.

</details>

## Development and contributing

Symlink the repository into `~/.claude/skills/` and it loads as `korean-writing@skills-dir`, bypassing the marketplace so changes apply immediately.

If a marketplace-installed copy exists, it takes precedence and the symlinked copy is not loaded. Run `claude plugin uninstall korean-writing` before developing.

```bash
git clone https://github.com/IsthisLee/claude-korean-writing.git
ln -s "$PWD/claude-korean-writing" ~/.claude/skills/korean-writing
claude plugin list                            # should show loaded
python3 hooks-handlers/test_posttooluse.py    # 28 regression cases
```

Adding a pattern touches three places:

1. `hooks-handlers/posttooluse.sh`: the check
2. `hooks-handlers/ground-truth.json`: a real sentence
3. `hooks-handlers/test_posttooluse.py`: the case, false-positive cases first

**If you spot an awkward sentence, open an issue.** The ground truth uses only sentences that were actually generated. One real failure is worth more than any synthetic example.

## Versioning and releases

[SemVer](https://semver.org/). The version lives in `.claude-plugin/plugin.json` and nowhere else; the release script propagates it.

| Bump  | When                                                                                              |
| ----- | ------------------------------------------------------------------------------------------------- |
| Patch | Fewer false positives, wording, docs                                                              |
| Minor | A new pattern or skill, a threshold that catches more, a change of purpose or structure           |
| Major | A change in the contract, such as the hook starting to block edits, or a skill renamed or removed |

Release notes go in [`CHANGELOG.md`](./CHANGELOG.md) under `[Unreleased]`. Update the callout at the top of both READMEs, then run:

```bash
scripts/release.sh 0.3.0          # tests, validate, bump, changelog, commit, tag
scripts/release.sh 0.3.0 --push   # plus git push --follow-tags and a GitHub release
```

## Sources

This plugin started from the Korean prose quality part of [claude-forge](https://github.com/sangrokjung/claude-forge). The rulebooks and the polish skill come from there, and the edit hook was modeled on Forge's `emdash-slop-guard`. What was added here: the `korean-writing` skill for first drafts, hook patterns K2 to K8, and verification built from real failures.

| File                                           | Origin                                                          | Extent                                                                                      |
| ---------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `references/taxonomy.md`                       | claude-forge `reference/ai-tell-taxonomy.md`                    | Verbatim                                                                                    |
| `references/quick-rules.md`                    | claude-forge `skills/humanize-korean/references/quick-rules.md` | Verbatim                                                                                    |
| `skills/humanize-korean/SKILL.md`              | claude-forge `skills/humanize-korean/SKILL.md`                  | Translated to Korean and restructured; procedure and iron rules unchanged                   |
| `hooks-handlers/posttooluse.sh`                | claude-forge `hooks/emdash-slop-guard.sh`                       | Modeled on it: same trigger (`.md` edits, Hangul ratio) and K1 regex; the rest written here |
| `skills/korean-character-count/scripts/*.js`   | [k-skill](https://github.com/NomaDamas/k-skill)                 | Verbatim                                                                                    |
| `skills/korean-character-count/instruction.md` | k-skill                                                         | Only the run path changed to `node`                                                         |
| `skills/korean-character-count/SKILL.md`       | k-skill                                                         | Rewritten from the original                                                                 |

Both are MIT; [`LICENSE`](./LICENSE) keeps the original copyright notices and the per-file scope.

`korean-spell-check` was not taken: it sends the text to an external server, and that service's terms limit free use to individuals and students.

## License

[MIT](./LICENSE). Use it, change it, ship it.
