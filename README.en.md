<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/banner.en.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/banner-light.en.svg">
  <img src="docs/banner.en.svg" alt="korean-writing" width="100%">
</picture>

<p align="center">
  <a href="README.md">한국어</a> · <strong>English</strong>
</p>

<p align="center">
  <strong>The plugin that owns the quality of every piece of Korean Claude Code writes.</strong><br>
  Ordinary replies carry the rules, drafts read as if a person wrote them from the first line, and .md files are checked the moment they are saved.<br>
  Nothing you write leaves your machine.
</p>

<p align="center">
  <a href="https://github.com/IsthisLee/claude-korean-writing/actions/workflows/validate.yml"><img alt="Validate" src="https://github.com/IsthisLee/claude-korean-writing/actions/workflows/validate.yml/badge.svg?branch=main"></a>
  <img alt="MIT" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Claude Code Plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2">
  <img alt="version" src="https://img.shields.io/badge/version-1.0.0-lightgrey">
  <img alt="network" src="https://img.shields.io/badge/network-none-success">
  <img alt="platform" src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey">
  <a href="https://github.com/IsthisLee/claude-korean-writing/commits/main"><img alt="last commit" src="https://img.shields.io/github/last-commit/IsthisLee/claude-korean-writing"></a>
</p>

<p align="center">
  <a href="#what-kind-of-plugin-is-this">Introduction</a> ·
  <a href="#seeing-it-work">Seeing it work</a> ·
  <a href="#three-minutes-to-try-it">3-minute start</a> ·
  <a href="#install">Install</a> ·
  <a href="#how-to-ask">How to ask</a> ·
  <a href="#components">Components</a> ·
  <a href="#the-verdict-rules">Verdict rules</a> ·
  <a href="#verification">Verification</a> ·
  <a href="#faq">FAQ</a>
</p>

> **v1.0.0**: First release. Four skills, a hook that checks every `.md` edit, and scripts for document checks and releases. Since the release, main has gained a hook that injects reply rules when a session opens. Details: [CHANGELOG.md](CHANGELOG.md) (Korean).

> **korean-writing makes the Korean Claude Code writes read as if a person wrote it.** Install it and the rules apply from the very first reply. Say **"운영팀에 보낼 안내문 써줘"** (write a notice for the ops team) and a skill loads on its own; save a `.md` file and a hook points out translation-ese and AI idioms.

## What kind of plugin is this

Claude Code's Korean is grammatically fine. It still reads wrong: word order carried over from English, metaphors that arrived through English, and stock phrases that land in the same spot of every document. A publisher's editorial desk saw such phrases and suspected the manuscript was machine-written.

This plugin attaches wherever that Korean is produced. When a session opens, reply rules go in. When you ask for text, a skill writes it under the rules from the first line. When you ask to touch up existing text, a skill fixes the style and leaves the facts alone. When a `.md` file is saved, a hook checks what was just written. Character counts come from a script rather than the model's guess, and READMEs start with a skill that lays out the sections.

> Think of a linter, attached to Korean prose instead of code. It points things out and does not fix them; fixing is your call.

| Part           | Count        | What                                                                                                                                                         |
| -------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Skills         | 4            | `korean-writing`, `humanize-korean`, `korean-character-count`, `crafting-effective-readmes`                                                                  |
| Hooks          | 2            | rule injection at session start, a check right after `.md` edits                                                                                             |
| Check patterns | 8            | `K1` to `K8`: em-dashes, abstract structure words, 것 constructions, AI idioms, mechanical enumeration, win/lose and object personification, translation-ese |
| Rulebook       | 73 items     | 10 categories, each item with a severity and a fix                                                                                                           |
| Ground truth   | 15 sentences | 10 violations Claude Code actually generated, 5 clean sentences from the same context                                                                        |
| Regression     | 63 cases     | 43 for the check hook, 20 for the always-on rules                                                                                                            |
| Scripts        | 4            | character count, whole-file check, false-positive measurement, release                                                                                       |
| Network        | none         | the hooks are bash and python3 regular expressions; the counter uses `node:fs`                                                                               |

## Seeing it work

This is what appears in Claude Code after a `.md` edit. The window frame is drawn; from the yellow line down it is the hook's actual output, unchanged.

<p align="center"><img src="docs/hook-output.svg" alt="Hook output flagging K1, K2, K3, K4 and K7" width="860"></p>

This is the exact stderr the hook produced when the win/lose sentence and the em-dash sentence from the ground truth were fed in as an edit.

```
[korean-writing] 배포-지연.md 에 AI 티 패턴이 있다. 편집은 그대로 두었으니 확인하고 고쳐라.
  K1  줄표(—) 삽입구 4개 — 쉼표나 문장 분리로 바꾼다. 한국어에서 가장 강한 AI 티다
  K6  승패 의인화 2회 — 우선한다·따른다·앞선다 로 직결한다
  교정 규칙은 korean-writing 스킬에 있다. 격식 문서(계약·약관·법률)면 파일 머리에 <!-- korean-writing: ignore --> 를 넣으면 다시 알리지 않는다.
```

And the real output of the script behind the character-count skill, given a two-line sentence with an emoji.

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

Four sentences from the ground truth show what the rules are after. Claude Code actually wrote every one of them.

> 규칙이 충돌하면 상위 문서가 **이깁니다**. 둘 다 값이 있을 때는 텍스트가 **이기고** 강의실 참조는 무시됩니다.

"The upper document wins." Documents and settings do not compete; Korean says one takes precedence or is followed. A publisher's editors found the same "이깁니다" in the same spot in manuscripts by two different authors.

> 원인은 힙 부족이 아니었습니다 **—** 실측해보니 **—** 설정이 아예 먹히지 않았습니다.

An em-dash interjection, English punctuation copied into Korean. It is the other expression those editors singled out, and the most visible tell in Korean prose.

> 여기서 갈리는 **축은** 프로젝트 전용 여부가 아니라 성격입니다. 두 문제는 **결이** 다르고 **레이어도** 다릅니다.

Axis, grain, layer: a habit of describing structure through metaphor. "The criteria differ" or "these are different problems" says it plainly.

> 시험용 장비가 몇 초 만에 **쓰러졌습니다**. **일으켜 세우면** 또 쓰러지기를 스무 분 넘게 반복했습니다.

Equipment does not fall over and get stood back up. It stopped and was restarted.

## Three minutes to try it

1. Install. Two commands, nothing to configure.
   ```bash
   claude plugin marketplace add IsthisLee/claude-korean-writing
   claude plugin install korean-writing
   ```
2. Open a new session and ask for any piece of text. The skill loads on its own.
   ```
   운영팀에 보낼 옵션 변경 안내문 써줘. 슬랙에 캐주얼하게.
   ```
3. Ask to save that text as a `.md` file. The hook checks what was just written and, if anything is flagged, prints output like the one above. If nothing is flagged, it stays silent.

## Install

```bash
claude plugin marketplace add IsthisLee/claude-korean-writing
claude plugin install korean-writing
```

When `claude plugin list` shows `korean-writing` as `enabled`, you are done. New versions come with `claude plugin update korean-writing`. A local checkout can be registered as a marketplace too, for an internal copy or a fork.

```bash
claude plugin marketplace add /path/to/claude-korean-writing
claude plugin install korean-writing
```

| Needed      | Used by                          | Without it                     |
| ----------- | -------------------------------- | ------------------------------ |
| Claude Code | Everything. Verified on 2.1.267  |                                |
| `bash`      | Both hooks and the three scripts | The hooks do not run           |
| `python3`   | The check hook's verdict         | It passes without checking     |
| `node` 18+  | The character-count script       | Only that skill is unavailable |

There are no packages to download. CI runs the same checks on macOS and Linux, and Windows needs Git Bash or WSL and has not been tried yet.

## How to ask

Talk to Claude Code as usual; the skills load from the request. These lines can be pasted as they are.

```
운영팀에 보낼 옵션 변경 안내문 써줘. 슬랙에 캐주얼하게.      (a casual Slack notice to the ops team about the option change)
아래 글 번역투만 고쳐줘. 사실과 숫자는 그대로 두고.           (fix only the translation-ese below; keep facts and numbers)
이 자기소개서 공백 포함 몇 자야? 1,000자 제한이야.            (how many characters including spaces? the limit is 1,000)
이 프로젝트 README 써줘. 오픈소스용으로.                       (write a README for this project, open-source style)
이번 배포 QA 보고서를 배포-QA.md 로 써줘.                       (write this release's QA report to 배포-QA.md)
```

To call a skill directly, use its slash name.

| Ask for                              | Direct call                                  |
| ------------------------------------ | -------------------------------------------- |
| Text written well from the start     | `/korean-writing`                            |
| Translation-ese removed from a draft | `/korean-writing:humanize-korean`            |
| A character count                    | `/korean-writing:korean-character-count`     |
| A README                             | `/korean-writing:crafting-effective-readmes` |

Ordinary replies have nothing to call, because the rules are in place the moment the session opens.

Hand a draft to the polish skill and the fixed text comes back with a one-line status: an estimated change rate and a grade from A to D. Below it, three to six of the main edits are shown side by side, before and after. If more than half the text changed, you get that fact instead of a result. A text changed by half is a rewrite, not a polish.

To check existing documents in one go, run `scripts/check.sh FILE...`. It applies the same rules as the hook and exits 1 if any file is flagged, so it works as-is in CI and pre-commit.

It can be switched off at four scopes.

| Scope                | How                                                                                                                                 |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| One file             | `<!-- korean-writing: ignore -->` at the top. For contracts, or a catalog of bad examples, where flagging every time makes no sense |
| Whole session        | `KOREAN_WRITING_HOOK_DISABLED=1`. Turns off both hooks                                                                              |
| Always-on rules only | `KOREAN_WRITING_ALWAYS_ON_DISABLED=1`                                                                                               |
| The whole plugin     | `claude plugin disable korean-writing`                                                                                              |

## Where it attaches

| Place                   | Owner                              | When it runs                                | Where the rules live                 |
| ----------------------- | ---------------------------------- | ------------------------------------------- | ------------------------------------ |
| Ordinary replies        | SessionStart hook                  | Session start, resume, `/clear`, compaction | `hooks-handlers/always-on.md`        |
| Writing requests        | `korean-writing` skill             | When you ask for text                       | `SKILL.md`                           |
| Polishing existing text | `humanize-korean` skill            | When you ask for a touch-up                 | `skills/humanize-korean/SKILL.md`    |
| Editing `.md` files     | PostToolUse hook                   | Right after `Edit`, `Write`, `MultiEdit`    | `hooks-handlers/posttooluse.sh`      |
| Length limits           | `korean-character-count` skill     | When you ask how many characters            | `skills/korean-character-count/`     |
| READMEs                 | `crafting-effective-readmes` skill | When you ask to write or update a README    | `skills/crafting-effective-readmes/` |

## Components

### Always-on rules

Most of the Korean Claude Code produces in a day is neither a file nor a writing request. It is the ordinary reply, and neither the skills nor the check hook reach it. The SessionStart hook fills that gap. When a session starts or resumes, after `/clear`, and after the context is compacted, it injects `hooks-handlers/always-on.md` once. It injects after compaction too, because the rules must survive when the front of the context is cut away.

There are nine items. Answer in polite form as usual; keep people or organizations as subjects; drop metaphors that came through English and just describe; no em-dash interjections, no firstly-secondly enumeration, no emoji; no translation-ese and no AI idioms; vary sentence length and keep one register; leave formality and facts alone and do not touch code, quotations or proper nouns; on a writing request, load the `korean-writing` skill first.

The file is 1.4 KB and 371 Hangul characters, about 660 tokens. It lands in the prompt cache, so there is no per-turn cost of resending it. It blocks nothing: with the rules file missing or unreadable the exit code is still 0. Twenty regression checks look at the injected content, whether all nine items are still there, the 400-Hangul ceiling, both off switches, and the safe exit.

### The korean-writing skill

Any request to write text triggers it: Slack notices and mail, announcements, reports, release notes, commit messages, READMEs and planning documents, meeting notes and working memos. Whether the reader is someone else or only you makes no difference, and code-only work does not trigger it.

The heart of the rule is to write as a person speaks, and a sentence that reads like translated English has failed. Timing matters. The skill writes that way from the first sentence rather than fixing a finished draft, because a finished draft is already translation-ese in its structure and polishing rarely gets it out.

Five principles sit underneath. Write clean from the start. Strip only the machine tics, and leave formality, expertise, genre, argument and facts untouched. Add no metaphor or rhetoric the source did not have. If the draft still misses the bar, hand it to `humanize-korean`. Which model writes is not this rule's concern.

The sentence rules: keep people or organizations as subjects; use only metaphors Korean actually uses; do not explain structure through metaphor; do not frame things as winning and losing; cut back on 것 constructions; keep one register to the end; vary sentence length. The formatting rules: at most two em-dash interjections per document, bullets only for real lists, no mechanical enumeration, emoji only for a Slack greeting.

Before sending, only four things are checked: three or more em-dashes; `축`, `갈래`, `결` and `레이어` three or more times combined; a sentence where an object acts like a person; anything that snags when read aloud. The last of the four weighs most. Contracts, terms, legal documents and official letters sit outside the rule because stiffness is their requirement, and code, logs, commands, quotations, proper nouns and English source text are left untouched.

### The humanize-korean skill

Existing text is its material. Say "remove the AI tells," "fix the translation-ese" or "tidy this up" and it loads, stripping translation-ese and AI idioms and nothing else. Text not yet written belongs to `korean-writing`.

It finishes in a single pass: read, scan with the compressed rulebook `references/quick-rules.md`, open the full taxonomy only where the verdict is unclear, fix only the flagged spans, run the self-check, hand it back. Text over 5,000 Hangul characters is cut into logical sections and run section by section. Over 8,000 characters, or where accuracy matters most, it says a single pass is not enough.

Four iron rules, each rolled back if broken. Facts, claims, numbers, dates, proper nouns and quotations are not changed at all. Nothing outside a span matched by the rulebook or taxonomy is touched. Genre and register stay as the source had them. A change rate over 30% is treated as a warning sign, and over 50% the result is withheld.

Its purpose is to turn awkward translation-ese into natural Korean. It is not a tool for slipping past AI detectors, and the skill text forbids describing it that way.

### The korean-character-count skill

It loads for text under a length limit; "within 500 characters," "count the characters" and "fit the personal statement" are the signals. A Korean character count depends on what is being counted: 각 is one character but three bytes in UTF-8, and a syllable assembled from separate jamo looks like one character while being three code points. So a script counts, in place of the model's estimate.

`characters` (grapheme clusters) is what people usually mean by the character count. Use `characters_without_whitespace` when a form says so, `bytes_neis` with `--profile neis` for the Korean education administration system, and `bytes_utf8` for database column limits. Node 18 or newer is required and nothing beyond `node:fs` is used. The counting contract is in `skills/korean-character-count/instruction.md`.

### The crafting-effective-readmes skill

It loads when you ask for a README to be created or revised. First it settles the kind of task: creating, adding a section, updating, or reviewing. Then the project type, one of open source, personal, internal or config repository, each with its own template and section checklist. Whatever the README, a name, a one- or two-sentence description and usage are never left out. This skill goes as far as laying out the sections, and the sentences follow the `korean-writing` rules.

### The check hook and the scripts

The check hook runs right after `Edit`, `Write` or `MultiEdit` touches a `.md` file and looks only at what was just written, because checking the whole file would re-flag old wording on every edit. The verdict is described in the next section.

| Script               | What it does                                                                                                                                                                            |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/check.sh`   | Pushes whole files through the hook, for existing documents, CI and pre-commit. Exits 1 if any file is flagged                                                                          |
| `scripts/measure.sh` | Pushes every Korean `.md` under a directory through the hook and reports flagged files and counts per code. Whether a flagged file was written by a person or by Claude is a human call |
| `scripts/release.sh` | Aligns `plugin.json`, the README badges and CHANGELOG to one version, then commits and tags. With `--push` it also pushes and creates the GitHub release                                |

## The verdict rules

1. When one of `Edit`, `Write` or `MultiEdit` finishes, Claude Code serializes the tool input as JSON and feeds it to `hooks-handlers/posttooluse.sh` on stdin.
2. If the environment variable `KOREAN_WRITING_HOOK_DISABLED` is 1, or `python3` cannot be found, it passes without looking at anything.
3. A path that does not end in `.md` passes.
4. From the tool input it gathers only what was just written: `content`, `new_string`, `edits[].new_string`. If `korean-writing: ignore` appears there, or within the first 4,000 characters of the file, it passes.
5. It strips code blocks (three backticks or `~~~`), inline code, URLs, table rows and HTML comments. Table rows go entirely because a document that quotes bad examples must not be flagged for the examples.
6. If Hangul makes up more than 30% of what is left, all of it is checked. If not, the lines are filtered again and only those that are at least 30% Hangul are kept, so a single Korean paragraph in the middle of an English document is not missed. If fewer than 20 Hangul characters survive the filter, it passes.
7. The regular expressions `K1` through `K8` run over what remains.
8. With no hits it ends quietly with exit code 0. With hits it writes each item to stderr, with the count and how to fix it, and exits 2. Either way the file is not touched.

| Code | What                             | What the regex looks for                                                                                    | Fires at                                                    |
| ---- | -------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `K1` | Em-dash interjection             | `—` or `–` with a space and a character on both sides                                                       | 4. If the edit adds at least one, the whole file is counted |
| `K2` | Abstract structure words         | `축이·축은·축을·축으로`, `갈래`, `결이 다르`, `레이어`                                                      | 3                                                           |
| `K3` | Translation-ese 것 constructions | `것들이었`·`것들이다`, `것들을`, `하는 것이 가능`                                                           | 1                                                           |
| `K4` | AI idioms                        | `결론적으로`, `종합하면`, `시사하는 바가 크`, `혁신적`, `압도적` and others                                 | 1                                                           |
| `K5` | Mechanical enumeration           | `첫째` and `둘째` followed by a comma or period                                                             | both present                                                |
| `K6` | Win/lose personification         | `~가 이긴다·이깁니다·이겼다·이기고`                                                                         | 2                                                           |
| `K7` | Personified objects              | screens, servers, devices and the like that `굳·쓰러지·넘어지·일어서·잠들`; `넘어뜨리·일으켜 세우·쓰러뜨리` | 1                                                           |
| `K8` | Translation-ese                  | `가지고 있`, double passives `되어지·지게 된다`, `에 의해`                                                  | 1 per item, `에 의해` at 2                                  |

The em-dash is the one exception that is counted across the whole file. Fixing a document one paragraph at a time adds one or two dashes per edit and dozens to the file, yet no single edit ever reaches the threshold when only the edit is counted. So when the edit adds even one em-dash interjection, the hook re-reads the file and counts them all under the same exclusion rules. An edit with no dashes is never flagged no matter how many the file holds, so editing old documents does not get noisier.

Thresholds are one step above the rulebook's. Where the rulebook allows one per document, the hook reports from two. It informs rather than blocks, and flagging a sound sentence and breaking someone's flow does more harm than missing one.

## Principles

**Catch it while writing.** That is why the rules go in at session start and a skill attaches to every writing request. Checking a finished text is the last net for what slipped past those two, not the primary tool.

**Do not block.** The check hook informs and never reverts an edit, and the injection hook exits 0 whatever happens. On a machine without `python3` the check is skipped. The moment a checker starts blocking work, people switch it off.

**No rule changes without numbers.** Adding or removing a pattern, or moving a threshold, needs a result from real documents. Thirteen such changes are on record in [`EVALUATION.md`](./EVALUATION.md). The win/lose threshold went from one to two because the rulebook allows one. "죽다" (to die) left the personification rule because "the server died" is everyday developer speech. Dropping the counts for `~에 대해` and `~를 통해` from the translation-ese rule removed a check that, on real documents, only ever flagged human writing.

**Flagging a sound sentence is worse than missing one.** The pass criteria are ordered that way: zero false positives on clean sentences comes first, ten out of ten detections second. Across 143 real documents, one human-written file was flagged.

**No contact with the outside.** What the hook reads and never does is in [SECURITY.md](./SECURITY.md), together with three `grep` commands that let you check for yourself.

**What is always loaded stays small.** Ordinarily only the always-on rules and the four skill descriptions enter the context, and the large files open when their job comes up.

```
hooks-handlers/always-on.md     1.4 KB   once per session
SKILL.md                        8.0 KB   on writing requests
references/quick-rules.md       9.7 KB   when polishing starts
references/taxonomy.md         66   KB   to look up one ambiguous item
```

**Imported files stay imported.** The taxonomy, the compressed rulebook, the README skill and the counting script belong to other MIT projects. [`NOTICE.md`](./NOTICE.md) records, file by file, where each came from and which lines were changed.

## Verification

The pass criteria and the measurements are in [`EVALUATION.md`](./EVALUATION.md) (Korean). The criteria form six groups, hook accuracy, skill triggering, skill effectiveness, structural soundness, failure modes and the user's own criteria, and any group that falls short gets fixed and measured again.

| Measurement                        | Result                                          |
| ---------------------------------- | ----------------------------------------------- |
| Violations detected                | 10 / 10                                         |
| False positives on clean sentences | 0 / 5                                           |
| False positives on real documents  | 1 / 143 (0.7%)                                  |
| Correct code on detected items     | 10 / 10                                         |
| Writing-request triggers           | 5 / 5, with 0 / 5 misfires on code work         |
| Mutation testing                   | 15 / 15 injected defects caught                 |
| Always-on rules, blind pairs       | 21 won, 0 lost, 3 tied out of 24                |
| Always-on context cost             | about 950 tokens (descriptions 290 + rules 662) |
| Network calls                      | 0                                               |
| Regression tests                   | 63 / 63                                         |

False positives on real documents were measured on 143 Korean `.md` files that had accumulated on one machine, unrelated to this plugin. Fed through the hook whole, 60 were flagged: 59 were implementation logs, QA reports and CLAUDE.md files that Claude wrote in 2026, and one was written by a person. The same measurement before the rule changes flagged seven human-written files, 4.9%.

The always-on rules were measured on twelve prompts such as explaining a function, diagnosing an error and reviewing a PR. Forty-eight replies were generated with and without the injection, and the same model was asked blind, twice per pair with the order swapped, which one read better. The injected side won 21 of 24 pairs and tied 3, and won or tied on all twelve prompts. A separate check of technical errors alone, style set aside, found no serious error on either side.

The skill itself was compared with and without on four identical prompts. On claude-opus-5 as of 2026-09-10 all seven valid samples passed the hook, so this sample could not separate the generation-time effect. That result is recorded as is.

The same checks run locally with these commands.

```bash
python3 hooks-handlers/test_posttooluse.py     # check hook regression, 43 cases
python3 hooks-handlers/test_sessionstart.py    # always-on rules regression, 20 cases
scripts/check.sh README.md CLAUDE.md           # do the documents pass their own hook
scripts/measure.sh ~/Documents                 # false positives over real documents
```

GitHub Actions repeats the checks on macOS and Linux for every push and pull request: manifest and issue-form syntax, the hooks' executable bits, both regression suites, thirteen Korean documents passing their own hook, and a smoke test of the counting script. On top of those come shellcheck, a check that `plugin.json`, the README badges and CHANGELOG name the same version, and `claude plugin validate`.

## What it does not do

- The check hook looks only at `.md` files. Korean comments and strings inside code, and replies that go straight out to Slack, are covered by the always-on rules and the skills at generation time, with no check afterwards.
- The regular expressions catch eight known markers. New kinds of awkwardness have to be found by a person and added.
- The always-on rules were measured on single turns. Whether the effect fades in long conversations is being measured now.
- **Subagents are outside what this plugin can reach.** The session-start injection, a subagent-start hook's output, and the skill list were each confirmed not to reach a subagent. The one thing that does reach them is `CLAUDE.md`. To cover subagents, put a line like this in your own `CLAUDE.md`.

```markdown
When answering in Korean or writing Korean prose, follow the korean-writing rules:
no personified objects, no calqued metaphors, no abstract structure words,
no em-dash interjections, no first/second enumerations, no translation-ese, no AI idioms.
```
- Contracts, terms of service, legal documents and official letters are out of scope; formality is their requirement. Code, logs, commands, quotations, proper nouns and English source text are left alone.
- Spelling and spacing are not checked. Style only.

## Repository layout

```
korean-writing/
├── .claude-plugin/
│   ├── plugin.json                   manifest: name, version (the source of truth), four skill paths
│   └── marketplace.json              marketplace catalog; carries no version
├── hooks/hooks.json                  registers SessionStart and PostToolUse, 10 s limit each
├── hooks-handlers/
│   ├── always-on.md                  the nine reply rules injected once per session
│   ├── sessionstart.sh               the injector; always exits 0
│   ├── posttooluse.sh                the checker: python3 regular expressions K1 to K8 inside bash
│   ├── ground-truth.json             10 awkward sentences that were actually generated
│   ├── clean.json                    5 clean sentences from the same context
│   ├── test_posttooluse.py           43 regression cases for the check hook; verifies reported counts
│   └── test_sessionstart.py          20 regression cases for the always-on rules
├── SKILL.md                          the korean-writing skill
├── references/
│   ├── quick-rules.md                compressed rulebook for the first polishing pass
│   └── taxonomy.md                   AI-tell taxonomy: 10 categories, 73 items
├── skills/
│   ├── humanize-korean/SKILL.md      the polish skill
│   ├── korean-character-count/       the counting skill: SKILL.md, instruction.md, scripts/
│   └── crafting-effective-readmes/   the README structure skill: 4 templates, 5 references
├── scripts/
│   ├── check.sh                      whole-file check
│   ├── measure.sh                    false-positive measurement over a corpus
│   └── release.sh                    version, CHANGELOG, badges, tag, release
├── docs/                             banners (Korean and English, light and dark), hook output demo, social preview
├── .github/                          CI workflow, three issue forms, PR template, CODEOWNERS, dependabot
├── .claude/settings.json             shared project settings for contributors
├── .gitattributes                    pins shell scripts to LF
├── .editorconfig
├── EVALUATION.md                     pass criteria, measurements, what was fixed while measuring
├── CHANGELOG.md                      release notes
├── CLAUDE.md                         rules for Claude working in this repository
├── CONTRIBUTING.md · .en.md          how to contribute
├── CODE_OF_CONDUCT.md                code of conduct
├── SECURITY.md                       security policy and what the hook does
├── NOTICE.md                         origin and modification scope of imported files
├── LICENSE                           MIT
└── README.md · README.en.md
```

## Neighbors and where this plugin sits

Korean prose-quality tools come in three layers: the ones that build the rulebook, the ones that attach the rules to a particular editor, and the frameworks that outfit the whole editor. This plugin sits in the middle. The rulebook came from im-not-ai, the way it attaches to Claude Code was built here, and claude-forge is there if you want the framework.

| Tool                                                        | What it is                                                                                                                                  | Relation to this plugin                                                                                                                                                                         |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [im-not-ai](https://github.com/epoko77-ai/im-not-ai)        | A polishing skill that strips AI tells from existing Korean. A multi-call pipeline (diagnose, rewrite, finalize) that supports several CLIs | The origin of the taxonomy. This plugin puts its weight on first drafts and ordinary replies, and its polish is a single pass                                                                   |
| [claude-forge](https://github.com/sangrokjung/claude-forge) | A Claude Code framework bundling agents, commands, hooks and rules. Its Korean prose guardrail is one part                                  | The polish skill, the compressed rulebook and the em-dash hook's trigger came from there. With Forge fully installed you do not need this plugin, and running both duplicates the em-dash check |
| [k-skill](https://github.com/NomaDamas/k-skill)             | A collection of skills for Korean users, from character counting to transit, weather and search                                             | The counting script came from there. Its spell-check skill sends text to an external server and was not taken                                                                                   |
| Spelling and spacing checkers                               | Check spelling                                                                                                                              | This plugin checks style only. They do not overlap; use both                                                                                                                                    |

## FAQ

<details>
<summary><b>Why does the check hook look only at .md files?</b></summary>

The hook receives the tool input after a file-editing tool finishes, so it cannot see replies that are not files. Replies are covered at generation time by the always-on rules injected at session start and by the writing skill. Checking replies with the regular expressions afterwards was tried too: on ordinary replies it caught 0.21 items per sample, too few to serve as a monitor.

Evidence: the header comment of `hooks-handlers/sessionstart.sh`, and N3 in [`EVALUATION.md`](./EVALUATION.md).

</details>

<details>
<summary><b>Does the hook revert my edit?</b></summary>

It does not. The hook's job ends at writing the items to stderr and exiting 2. The file stays exactly as edited, and whether to fix it is for Claude Code and you to decide.

Evidence: the "What this plugin does" table in [SECURITY.md](./SECURITY.md).

</details>

<details>
<summary><b>Does my text leave my machine?</b></summary>

It does not. The hooks run python3 regular expressions inside bash and the counting script imports nothing but `node:fs`. Anyone can confirm there is no network call and no external program with the three `grep` commands in [SECURITY.md](./SECURITY.md). The spell-check skill that posts text to an external server was left out for the same reason.

</details>

<details>
<summary><b>Does it flag contracts and terms of service?</b></summary>

It does, which is why a single line at the top of the file, `<!-- korean-writing: ignore -->`, takes that file out of the check. Text where formality is the requirement is an exception in the skill rules as well. This repository's own taxonomy, a deliberate collection of bad examples, carries the same marker.

</details>

<details>
<summary><b>How many tokens does it cost?</b></summary>

The always-on cost is the four skill descriptions, about 290 tokens, plus the reply rules injected once per session, about 660. The rules figure comes from keeping the plugin installed, switching only the always-on rules off and on, and subtracting total input tokens from `claude -p`: 12,364 off, 13,026 on. The value only holds still with MCP tool definitions and user settings excluded. The rules land in the prompt cache and are not resent every turn. Skill bodies load only on writing requests, and the hook never calls an LLM.

Evidence: D2 and F7 in [`EVALUATION.md`](./EVALUATION.md).

</details>

<details>
<summary><b>I installed it but the skills do not show up.</b></summary>

First check that `claude plugin list` reports `korean-writing` as `enabled`. If the repository is symlinked into `~/.claude/skills/` and also installed from the marketplace, remove one of the two. The skill list only changes in a new session.

</details>

<details>
<summary><b>Does 10/10 detection mean it catches everything?</b></summary>

That is not what it means. The regular expressions were written by looking at those ten sentences, so catching them is expected, and the number exists to show that a rule change broke nothing. The number to watch is the false-positive rate: across 143 real documents, one human-written file was flagged. The patterns catch the eight known markers and nothing new.

Evidence: A1 to A3 and the 2026-09-10 re-measurement in [`EVALUATION.md`](./EVALUATION.md), and [`hooks-handlers/ground-truth.json`](./hooks-handlers/ground-truth.json).

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

It has not been tried. The hooks are bash scripts, so Git Bash or WSL has to be there. `.gitattributes` pins the scripts to LF, so a CRLF checkout cannot break them. If you try it, open an issue with the result and it will be recorded here.

</details>

## Contributing

The procedure is in [CONTRIBUTING.en.md](./CONTRIBUTING.en.md). The most valuable contribution is not code but sentences. If you have seen Claude Code write awkward Korean, or the hook flag a perfectly fine sentence, send the unedited original through the [awkward sentence report](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=awkward-sentence.yml) form. Reported sentences go into the ground truth or the clean set and become regression tests. There are separate forms for bug reports and rule proposals, and [Discussions](https://github.com/IsthisLee/claude-korean-writing/discussions) is the place for questions and examples.

The first step is a baseline run.

```bash
git clone https://github.com/IsthisLee/claude-korean-writing.git
cd claude-korean-writing
python3 hooks-handlers/test_posttooluse.py
python3 hooks-handlers/test_sessionstart.py
scripts/check.sh README.md CLAUDE.md
```

A change to a rule comes with numbers from `scripts/measure.sh` on real documents and with regression tests. Korean documents you touch must pass `scripts/check.sh`, and a README change lands in both the Korean and the English edition. Commit subjects are Conventional Commits in Korean, and the version number is left alone. Participants follow the [code of conduct](./CODE_OF_CONDUCT.md), and security issues go through the procedure in [SECURITY.md](./SECURITY.md) rather than a public issue.

## Releases

[SemVer](https://semver.org/) applies, and the version lives in `.claude-plugin/plugin.json` alone. `marketplace.json` carries no version.

A release is one run of `scripts/release.sh <version>`. It checks that the working tree is clean and the version is well formed, moves the CHANGELOG's `[Unreleased]` content under the new version, confirms that the callout at the top of both READMEs names that version, bumps `plugin.json` and the README badges, runs the regression tests and `claude plugin validate`, and creates the commit and an annotated tag. With `--push` it goes on to push and create the GitHub release.

```bash
scripts/release.sh 1.1.0
scripts/release.sh 1.1.0 --push
```

## Sources and license

| File                                 | From                                                                                                                                                            | Changed                                                                     |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `references/taxonomy.md`             | [im-not-ai](https://github.com/epoko77-ai/im-not-ai), via [claude-forge](https://github.com/sangrokjung/claude-forge), which added D-8, D-9 and the J-3 upgrade | One line at the top that exempts the file from the hook                     |
| `references/quick-rules.md`          | claude-forge                                                                                                                                                    | Two paths that pointed at a missing file                                    |
| `skills/humanize-korean/SKILL.md`    | claude-forge                                                                                                                                                    | Translated into Korean and restructured; procedure and iron rules unchanged |
| `hooks-handlers/posttooluse.sh`      | claude-forge's em-dash hook                                                                                                                                     | Only the trigger and the K1 regex are taken; the rest was written here      |
| `skills/korean-character-count/`     | [k-skill](https://github.com/NomaDamas/k-skill)                                                                                                                 | Script unchanged, run path in the instructions, SKILL.md rewritten          |
| `skills/crafting-effective-readmes/` | [agent-toolkit](https://github.com/softaworks/agent-toolkit), whose original is [agent-skills](https://github.com/joshuadavidthomas/agent-skills)               | One line each that names the companion skill                                |

The rest was written in this repository: the `korean-writing` skill, the always-on rules, patterns `K2` through `K8` of the check hook, the ground truth and the evaluation criteria. Every imported file is MIT-licensed and the original copyright notices are gathered in [`NOTICE.md`](./NOTICE.md). This repository is [MIT](./LICENSE) too.
