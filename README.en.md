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
  Replies get rules, drafts come out as if a person wrote them, and .md files are checked when saved.<br>
  Your text never leaves your machine.
</p>

<p align="center">
  <a href="https://github.com/IsthisLee/claude-korean-writing/actions/workflows/validate.yml"><img alt="Validate" src="https://github.com/IsthisLee/claude-korean-writing/actions/workflows/validate.yml/badge.svg?branch=main"></a>
  <img alt="MIT" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Claude Code Plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2">
  <img alt="version" src="https://img.shields.io/badge/version-1.0.0-lightgrey">
  <img alt="network" src="https://img.shields.io/badge/network-none-success">
  <img alt="platform" src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey">
</p>

<p align="center">
  <a href="#what-the-plugin-does">Introduction</a> ·
  <a href="#install">Install</a> ·
  <a href="#how-to-use">How to use</a> ·
  <a href="#what-is-inside">Components</a> ·
  <a href="#how-the-check-hook-decides">The hook's verdict</a> ·
  <a href="#principles">Principles</a> ·
  <a href="#how-much-to-trust-it">Verification</a> ·
  <a href="#questions">FAQ</a>
</p>

> **v1.0.0**: First release. Four skills, a hook that checks every `.md` edit, and scripts for document checks and releases. Since the release, main has gained a hook that injects always-on rules when a session opens. Details: [CHANGELOG.md](CHANGELOG.md) (Korean).

## What the plugin does

Claude Code writes Korean without mistakes. The trouble is that mistake-free Korean can still read wrong: word order carried over from English, metaphors that arrived through English, and stock phrases that land in the same spot of every document. A publisher's editorial desk saw such phrases and suspected the manuscript was machine-written.

This plugin attaches wherever that Korean is produced. When a session opens, reply rules go in. When you ask for text, a skill writes it under the rules from the first line. When you ask to touch up existing text, a skill fixes the style and leaves the facts alone. When a `.md` file is saved, a hook checks what was just written. When you ask for a character count, a script counts instead of the model guessing, and when you ask for a README, a skill lays out the sections first.

| Place                   | Owner                              | When it runs                                | Where the rules live                 |
| ----------------------- | ---------------------------------- | ------------------------------------------- | ------------------------------------ |
| Ordinary replies        | SessionStart hook                  | Session start, resume, `/clear`, compaction | `hooks-handlers/always-on.md`        |
| Writing requests        | `korean-writing` skill             | When you ask for text                       | `SKILL.md`                           |
| Polishing existing text | `humanize-korean` skill            | When you ask for a touch-up                 | `skills/humanize-korean/SKILL.md`    |
| Editing `.md` files     | PostToolUse hook                   | Right after `Edit`, `Write`, `MultiEdit`    | `hooks-handlers/posttooluse.sh`      |
| Length limits           | `korean-character-count` skill     | When you ask how many characters            | `skills/korean-character-count/`     |
| READMEs                 | `crafting-effective-readmes` skill | When you ask to write or update a README    | `skills/crafting-effective-readmes/` |

Nothing uses the network. The hooks are bash plus python3 regular expressions, and the counter uses only `node:fs`.

## Four real sentences

The rules did not come from invented examples. They came from sentences Claude Code actually generated; ten of them are in [`hooks-handlers/ground-truth.json`](./hooks-handlers/ground-truth.json). Here are four.

> 규칙이 충돌하면 상위 문서가 **이깁니다**. 둘 다 값이 있을 때는 텍스트가 **이기고** 강의실 참조는 무시됩니다.

"The upper document wins." Documents and settings do not compete; in Korean you say one takes precedence or is followed. A publisher's editors found the same "이깁니다" in the same spot in manuscripts by two different authors.

> 원인은 힙 부족이 아니었습니다 **—** 실측해보니 **—** 설정이 아예 먹히지 않았습니다.

An em-dash interjection, English punctuation copied into Korean. It is the other expression those editors singled out, and the most visible tell in Korean prose. A comma or a sentence break dissolves it.

> 여기서 갈리는 **축은** 프로젝트 전용 여부가 아니라 성격입니다. 두 문제는 **결이** 다르고 **레이어도** 다릅니다.

"The axis," "the grain," "the layer": structure explained through metaphor. A concrete noun such as criterion, case, kind or stage does the job.

> 시험용 장비가 몇 초 만에 **쓰러졌습니다**. **일으켜 세우면** 또 쓰러지기를 스무 분 넘게 반복했습니다.

Equipment does not fall over and get stood back up. It stopped and was restarted. A personification translated straight from English.

The check hook catches eight such markers with regular expressions. Anything wider is the job of the rulebook [`references/taxonomy.md`](./references/taxonomy.md): 73 items under ten categories (translation-ese, English quoting overuse, structural AI patterns, AI idioms, uniform rhythm, over-modification, hedging, conjunction overuse, formal-noun overuse, visual decoration), each with a severity and a fix.

## Install

```bash
claude plugin marketplace add IsthisLee/claude-korean-writing
claude plugin install korean-writing
```

There is nothing to configure. When `claude plugin list` shows `korean-writing` as `enabled`, you are done. New versions come with `claude plugin update korean-writing`.

A local checkout can be registered as a marketplace too, for an internal copy or a fork.

```bash
claude plugin marketplace add /path/to/claude-korean-writing
claude plugin install korean-writing
```

| Needed      | Used by                          | Without it                     |
| ----------- | -------------------------------- | ------------------------------ |
| Claude Code | Everything. Verified on 2.1.266  |                                |
| `bash`      | Both hooks and the three scripts | The hooks do not run           |
| `python3`   | The check hook's verdict         | It passes without checking     |
| `node` 18+  | The character-count script       | Only that skill is unavailable |

No extra packages are installed. CI runs the same checks on macOS and Linux. Windows needs Git Bash or WSL and has not been verified.

## How to use

Talk to Claude Code as usual. Skills load themselves from the request; to call one directly, use its slash name.

| Ask for                              | For example                                                                                                                     | Direct call                                  |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| Text written well from the start     | "운영팀에 보낼 옵션 변경 안내문 써줘. 슬랙에 캐주얼하게." (write a casual Slack notice to the ops team about the option change) | `/korean-writing`                            |
| Translation-ese removed from a draft | "아래 글 번역투만 고쳐줘. 사실과 숫자는 그대로 두고." (fix only the translation-ese below; keep facts and numbers)              | `/korean-writing:humanize-korean`            |
| A character count                    | "이 자기소개서 공백 포함 몇 자야? 1,000자 제한이야." (how many characters including spaces? the limit is 1,000)                 | `/korean-writing:korean-character-count`     |
| A README                             | "이 프로젝트 README 써줘. 오픈소스용으로." (write a README for this project, open-source style)                                 | `/korean-writing:crafting-effective-readmes` |

Ordinary replies need no call. The rules are already in the session.

The polish skill returns the fixed text with a one-line status (estimated change rate and a grade from A to D) and three to six of its main edits shown as before → after. If the change rate passes 50% it withholds the result and says so, because at that point it is a rewrite, not a polish.

The character-count skill runs a script. This is the real output for a two-line sentence that contains an emoji.

```
$ node skills/korean-character-count/scripts/korean_character_count.js --text "옵션 변경은 어드민에서 바로 할 수 있습니다.
정원이 찬 옵션은 회색으로 막힙니다 🙂" --format text
profile: default
characters: 47
characters_without_whitespace: 35
code_points: 47
utf16_code_units: 48
lines: 2
bytes_utf8: 116
bytes_neis: 117
```

The check hook runs when a `.md` file is saved. This is what it actually printed to stderr when the win/lose sentence and the em-dash sentence from the ground truth were fed in as an edit.

```
[korean-writing] 배포-지연.md 에 AI 티 패턴이 있다. 편집은 그대로 두었으니 확인하고 고쳐라.
  K1  줄표(—) 삽입구 4개 — 쉼표나 문장 분리로 바꾼다. 한국어에서 가장 강한 AI 티다
  K6  승패 의인화 2회 — 우선한다·따른다·앞선다 로 직결한다
  교정 규칙은 korean-writing 스킬에 있다. 격식 문서(계약·약관·법률)면 파일 머리에 <!-- korean-writing: ignore --> 를 넣으면 다시 알리지 않는다.
```

The file is left as it is. Claude Code reads this output and fixes the text; you see the result. To check existing documents in one go, run `scripts/check.sh FILE...`. It applies the same rules and exits 1 if any file is flagged.

There are four scopes for turning it off.

| Scope                | How                                                                                                                                 |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| One file             | `<!-- korean-writing: ignore -->` at the top. For contracts, or a catalog of bad examples, where flagging every time makes no sense |
| Whole session        | `KOREAN_WRITING_HOOK_DISABLED=1`. Turns off both hooks                                                                              |
| Always-on rules only | `KOREAN_WRITING_ALWAYS_ON_DISABLED=1`                                                                                               |
| The whole plugin     | `claude plugin disable korean-writing`                                                                                              |

## What is inside

### Always-on rules

Skills load only when you ask for text, and the check hook fires only on files. What falls between them is the bulk of a day's output: ordinary replies. The SessionStart hook takes those. Each time a session starts, resumes, is cleared or compacted, it injects `hooks-handlers/always-on.md` into the context once. It injects again after compaction because the rules must survive when the front of the context is cut away.

The rules are ten lines. Answer in polite form as usual; keep people or organizations as subjects; drop metaphors that came through English and just describe; no em-dash interjections, no firstly-secondly enumeration, no emoji; no translation-ese and no AI idioms; vary sentence length and keep one register; leave formality and facts alone and do not touch code, quotations or proper nouns; on a writing request, load the `korean-writing` skill first.

It is 1.4 KB, 371 Hangul characters, about 660 tokens, and it lands in the prompt cache so it is not resent every turn. This hook blocks nothing: with the rules file missing or unreadable it still exits 0. Twenty regression checks cover the injected content, the presence of nine rule items, a 400-Hangul ceiling, both off switches, and the safe exit.

### The korean-writing skill

It loads on any request to write text: Slack, mail and notices, reports, release notes, commit messages, READMEs and planning documents, meeting notes and working memos, whether the reader is someone else or yourself. Code-only work is not a trigger.

The core is one line: write as a person speaks, and if it reads like translated English it has failed. The skill writes that way from the first sentence rather than fixing afterwards, because once a draft is finished its structure is already translation-ese and polishing does not undo that.

Five principles: write clean from the start; strip only the machine tics and keep formality, expertise, genre, argument and facts intact; add no metaphor or rhetoric the source did not have; if the draft still misses the bar, hand it to `humanize-korean`; which model writes is not this rule's concern.

Seven sentence rules: keep people or organizations as subjects; use only metaphors Korean actually uses; do not explain structure through metaphor; do not frame things as winning and losing; cut back on 것 constructions; keep one register to the end; vary sentence length. The formatting rules: at most two em-dash interjections per document, bullets only for real lists, no mechanical enumeration, emoji only for a Slack greeting.

Four checks before sending: three or more em-dashes? 축, 갈래, 결 and 레이어 three or more times combined? objects acting like people? anything that snags when read aloud? The last matters most. Contracts, terms, legal documents and official letters are exempt because formality is their requirement, and code, logs, commands, quotations, proper nouns and English source text are left alone.

### The humanize-korean skill

It strips translation-ese and AI idioms from text that already exists, on requests such as "remove the AI tells" or "fix the translation-ese." Text not yet written goes to `korean-writing` instead.

The pass runs once. Read; scan with the compressed rulebook `references/quick-rules.md`; open the full taxonomy only for ambiguous spans; fix only the spans found; run the self-check; return. Text over 5,000 Hangul characters is split into logical sections; over 8,000 characters, or where accuracy matters most, the skill says a single pass is not enough.

Four iron rules, and any violation is rolled back: facts, claims, numbers, dates, proper nouns and quotations are preserved 100%; only spans that match a rulebook pattern are touched; genre and register stay; a change rate above 30% is a warning and above 50% the result is withheld.

The purpose is to turn awkward translation-ese into natural Korean. It is not detector evasion and is never described as such.

### The korean-character-count skill

It loads for text under a length limit: "within 500 characters," "count the characters," "fit the personal statement." Korean counts differ by rule. 각 is one character but three UTF-8 bytes, and a decomposed syllable looks like one character while being three code points. So a script counts instead of the model estimating.

`characters` (grapheme clusters) is closest to how a person counts. Use `characters_without_whitespace` when a form says so, `bytes_neis` with `--profile neis` for the Korean education administration system, and `bytes_utf8` for database column limits. Node 18 or newer is required and nothing beyond `node:fs` is used. The counting contract is in `skills/korean-character-count/instruction.md`.

### The crafting-effective-readmes skill

It loads when you ask to write or update a README. It first identifies the task: creating, adding a section, updating, or reviewing. Then the project type: open source, personal, internal, or a config repository, each with a template and a section checklist. Every README gets at least a name, a one- or two-sentence description and usage. This skill lays out the sections; the sentences follow the `korean-writing` rules.

### The check hook

It runs right after `Edit`, `Write` or `MultiEdit` touches a `.md` file and looks only at what was just written, because checking the whole file would re-flag old wording on every edit. The verdict is described in the next section.

### Scripts

| Script               | What it does                                                                                                                                                                            |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/check.sh`   | Pushes whole files through the hook, for existing documents, CI and pre-commit. Exits 1 if any file is flagged                                                                          |
| `scripts/measure.sh` | Pushes every Korean `.md` under a directory through the hook and reports flagged files and counts per code. Whether a flagged file was written by a person or by Claude is a human call |
| `scripts/release.sh` | Aligns `plugin.json`, the README badges and CHANGELOG to one version, then commits and tags. With `--push` it also pushes and creates the GitHub release                                |

```bash
scripts/check.sh docs/*.md        # exit 1 if anything is flagged
scripts/measure.sh ~/Documents    # false positives over a corpus of real documents
```

## How the check hook decides

1. When `Edit`, `Write` or `MultiEdit` finishes, Claude Code passes the tool input JSON to `hooks-handlers/posttooluse.sh` on stdin.
2. With `KOREAN_WRITING_HOOK_DISABLED=1`, or without `python3`, it passes.
3. If the path is not a `.md` file, it passes.
4. It collects what was just written (`content`, `new_string`, `edits[].new_string`). If `korean-writing: ignore` appears there or within the first 4,000 characters of the file, it passes.
5. It strips code blocks (``` and ~~~), inline code, URLs, table rows and HTML comments. Table rows go entirely because a document that quotes bad examples must not be flagged for the examples.
6. If Hangul makes up at least 30% of what remains, it checks all of it; otherwise it keeps only the lines that are at least 30% Hangul, so a Korean paragraph inside an English document is not missed. Fewer than 20 Hangul characters left, and it passes.
7. It runs the regular expressions `K1` to `K8`.
8. No hits: exit 0. Hits: the items and how to fix them go to stderr and it exits 2. The file is untouched.

| Code | What                             | What the regex looks for                                                                                    | Fires at                                                    |
| ---- | -------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `K1` | Em-dash interjection             | `—` or `–` with a space and a character on both sides                                                       | 4. If the edit adds at least one, the whole file is counted |
| `K2` | Abstract structure words         | `축이·축은·축을·축으로`, `갈래`, `결이 다르`, `레이어`                                                      | 3                                                           |
| `K3` | Translation-ese 것 constructions | `것들이었다`, `것들을`, `하는 것이 가능`                                                                    | 1                                                           |
| `K4` | AI idioms                        | `결론적으로`, `종합하면`, `시사하는 바가 크`, `혁신적`, `압도적` and others                                 | 1                                                           |
| `K5` | Mechanical enumeration           | `첫째,` together with `둘째,`                                                                               | both present                                                |
| `K6` | Win/lose personification         | `~가 이긴다·이깁니다·이겼다·이기고`                                                                         | 2                                                           |
| `K7` | Personified objects              | screens, servers, devices and the like that `굳·쓰러지·넘어지·일어서·잠들`; `넘어뜨리·일으켜 세우·쓰러뜨리` | 1                                                           |
| `K8` | Translation-ese                  | `가지고 있`, double passives `되어지·지게 된다`, `에 의해`                                                  | 1 per item, `에 의해` at 2                                  |

Em-dashes alone are counted over the whole file. Editing one paragraph at a time lets them pile up in a file without any single edit crossing the line, so if the edit adds even one, the hook reads the file and counts all of them under the same rules. An edit that adds none is never flagged, however many the file holds.

Thresholds sit one notch below the rulebook. Where the rulebook says "at most once per document," the hook fires from the second occurrence. It informs rather than blocks, and a false positive that interrupts work is the worse failure.

## Principles

**Catch it at generation time.** Checking afterwards is the backup. That is why the rules go in at session start and a skill attaches to writing requests. The check hook is the last net for what slips past both.

**Block nothing.** The check hook reports and never reverts. The injection hook exits 0 in every case. Without `python3` the check passes. The moment a checker gets in the way, people switch it off.

**Never touch a rule without measurement.** Adding or removing a pattern or moving a threshold requires numbers. Thirteen such changes are recorded in [`EVALUATION.md`](./EVALUATION.md). Win/lose personification was loosened from one occurrence to two because the rulebook allows one. "죽다" (to die) left the personification rule because "the server died" is everyday developer Korean. Counting `~에 대해` and `~를 통해` left the translation-ese rule because on real documents it only ever flagged human writing.

**A false positive is worse than a miss.** In the pass criteria, zero false positives on clean sentences comes before ten out of ten detections. Across 143 real documents, one human-written file was flagged.

**No network.** [SECURITY.md](./SECURITY.md) lists what the hook reads and never does, plus three `grep` commands that let you verify it.

**Cost is layered.** Ordinarily only the always-on rules and the skill descriptions are loaded; the large files open when needed.

```
hooks-handlers/always-on.md     1.4 KB   once per session
SKILL.md                        8.0 KB   on writing requests
references/quick-rules.md       9.7 KB   when polishing starts
references/taxonomy.md         66   KB   to look up one ambiguous item
```

**Imported files stay as they are.** The taxonomy, the compressed rulebook, the README skill and the counting script came from other MIT projects. [`NOTICE.md`](./NOTICE.md) records, file by file, where each came from and what was changed.

## How much to trust it

[`EVALUATION.md`](./EVALUATION.md) (Korean) holds the pass criteria and the measurements. The criteria come in six groups: hook accuracy, skill triggering, skill effectiveness, structural soundness, failure modes, and the user's criteria. If any one fails, it gets fixed.

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

False positives on real documents were measured by pushing 143 Korean `.md` files that had accumulated on one machine, unrelated to this plugin, through the hook in full. Sixty were flagged: 59 were implementation logs, QA reports and CLAUDE.md files written by Claude in 2026, and one was written by a person. Before the rule changes, seven human-written files (4.9%) were flagged.

The always-on rules were measured on twelve prompts such as explaining a function, diagnosing an error, and reviewing a PR. Forty-eight generations across two conditions were judged blind by the same model twice with the order swapped. The injected side won 21 of 24 pairs and tied 3, and won or tied on every prompt. A separate check of technical errors, with style set aside, found no serious error on either side.

The skill itself was compared with and without on four identical prompts. On claude-opus-5 as of 2026-09-10 both conditions passed the hook, so this sample could not separate the generation-time effect. That result is recorded as is.

To run the same checks locally:

```bash
python3 hooks-handlers/test_posttooluse.py     # check hook regression, 43 cases
python3 hooks-handlers/test_sessionstart.py    # always-on rules regression, 20 cases
scripts/check.sh README.md CLAUDE.md           # do the documents pass their own hook
scripts/measure.sh ~/Documents                 # false positives over real documents
```

GitHub Actions runs, on every push and pull request and on both macOS and Linux, the manifest and issue-form syntax checks, the hooks' executable bits, both regression suites, thirteen Korean documents against their own hook, and a character-count smoke test. On top of that come shellcheck, a version-consistency check across `plugin.json`, the README badges and CHANGELOG, and `claude plugin validate`.

## What it does not do

- The check hook looks only at `.md` files. Korean comments and strings inside code, and replies that go straight out to Slack, are covered by the always-on rules and the skills at generation time, with no check afterwards.
- The regular expressions catch eight known markers. New kinds of awkwardness have to be found by a person and added.
- The always-on rules were measured on single turns. Whether the effect fades in long conversations was not measured.
- **The injection does not reach subagents.** An equivalent SessionStart hook carrying an unguessable token was put in place and a subagent was asked about it twice; both times it reported not seeing it. Korean written by a subagent is currently outside the always-on rules.
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
│   ├── always-on.md                  the ten reply rules injected once per session
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

## Compared with other tools

| Tool                                                        | What it is                                                                                                                                  | Relation to this plugin                                                                                                                                                                         |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [im-not-ai](https://github.com/epoko77-ai/im-not-ai)        | A polishing skill that strips AI tells from existing Korean. A multi-call pipeline (diagnose, rewrite, finalize) that supports several CLIs | The origin of the taxonomy. This plugin puts its weight on first drafts and ordinary replies, and its polish is a single pass                                                                   |
| [claude-forge](https://github.com/sangrokjung/claude-forge) | A Claude Code framework bundling agents, commands, hooks and rules. Its Korean prose guardrail is one part                                  | The polish skill, the compressed rulebook and the em-dash hook's trigger came from there. With Forge fully installed you do not need this plugin, and running both duplicates the em-dash check |
| [k-skill](https://github.com/NomaDamas/k-skill)             | A collection of skills for Korean users, from character counting to transit, weather and search                                             | The counting script came from there. Its spell-check skill sends text to an external server and was not taken                                                                                   |
| Spelling and spacing checkers                               | Check spelling                                                                                                                              | This plugin checks style only. They do not overlap; use both                                                                                                                                    |

## Questions

<details>
<summary><b>Why does the check hook look only at .md files?</b></summary>

The hook receives the tool input after a file-editing tool finishes, so it cannot see replies that are not files. Replies are covered at generation time by the always-on rules injected at session start and by the writing skill. A Stop hook that re-reviews every reply would spend tokens on every turn, so there is none.

</details>

<details>
<summary><b>Does the hook revert my edit?</b></summary>

No. It reports the items to stderr and exits 2. The file stays as it is; whether to fix it is up to Claude Code and to you.

</details>

<details>
<summary><b>Does my text leave my machine?</b></summary>

No. The hooks are bash and python3 regular expressions, and the counting script uses only `node:fs`. The three `grep` commands in [SECURITY.md](./SECURITY.md) let you confirm there is no network call and no external program. That is why the spell-check skill, which posts text to an external server, was not taken.

</details>

<details>
<summary><b>Does it flag contracts and terms of service?</b></summary>

Put `<!-- korean-writing: ignore -->` at the top of the file and that file is not checked. Text where formality is the requirement is also an explicit exception in the skill. This repository's own rulebook, a deliberate catalog of bad examples, carries the same marker.

</details>

<details>
<summary><b>How many tokens does it cost?</b></summary>

The always-on cost is the four skill descriptions, about 290 tokens, plus the reply rules injected once per session, about 660. The rules figure comes from toggling the installed plugin with `KOREAN_WRITING_ALWAYS_ON_DISABLED=1` and subtracting total input tokens from `claude -p`: 12,364 off, 13,026 on. Against a session-start context of roughly ten thousand tokens that is about 5 percent. The rules land in the prompt cache and are not resent every turn. Skill bodies load only on writing requests, and the hook never calls an LLM.

</details>

<details>
<summary><b>I installed it but the skills do not show up.</b></summary>

Check that `claude plugin list` shows `korean-writing` as `enabled`. If the repository is symlinked into `~/.claude/skills/` and also installed from the marketplace, keep only one of the two. The skill list refreshes in a new session.

</details>

<details>
<summary><b>Does 10/10 detection mean it catches everything?</b></summary>

No. The patterns were built from those ten sentences, so catching them is expected; the number is a regression check. The number that matters is on the false-positive side: across 143 real documents, one human-written file was flagged. Regular expressions catch known patterns only.

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

Not verified. The hooks are bash scripts, so Git Bash or WSL is required. `.gitattributes` pins the scripts to LF, which prevents the CRLF checkout failure that would kill them. If you try it, open an issue with the result and it goes in here.

</details>

## Contributing

The procedure is in [CONTRIBUTING.en.md](./CONTRIBUTING.en.md). The most valuable contribution is not code but sentences. If you have seen Claude Code write awkward Korean, or the hook flag a perfectly fine sentence, send the unedited original through the [awkward sentence report](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=awkward-sentence.yml) form. Reported sentences go into the ground truth or the clean set and become regression tests. There are separate forms for bug reports and rule proposals.

Start by establishing the baseline.

```bash
git clone https://github.com/IsthisLee/claude-korean-writing.git
cd claude-korean-writing
python3 hooks-handlers/test_posttooluse.py
python3 hooks-handlers/test_sessionstart.py
scripts/check.sh README.md CLAUDE.md
```

A change that adds, removes or re-tunes a rule comes with numbers from `scripts/measure.sh` on real documents and with regression tests. Korean documents you edit must pass `scripts/check.sh`, and README changes go into both the Korean and the English edition. Commits follow Conventional Commits with Korean subjects, and the version number is never bumped by hand. Participants follow the [code of conduct](./CODE_OF_CONDUCT.md), and security issues go through [SECURITY.md](./SECURITY.md) rather than public issues.

## Releases

[SemVer](https://semver.org/) applies, and the version lives in `.claude-plugin/plugin.json` alone. Because a version in the marketplace entry would be overridden by `plugin.json` anyway, `marketplace.json` carries none.

`scripts/release.sh <version>` does the steps in order: checks that the working tree is clean and the version is well formed, moves the CHANGELOG's `[Unreleased]` section under the new version, checks that the callout at the top of both READMEs names that version, bumps `plugin.json` and the README badges, runs the regression tests and `claude plugin validate`, then commits and creates an annotated tag. With `--push` it also pushes and creates the GitHub release.

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

The `korean-writing` skill, the always-on rules, patterns `K2` to `K8` of the check hook, the ground truth and the evaluation criteria were written in this repository. Every imported file is MIT and the original copyright notices are in [`NOTICE.md`](./NOTICE.md). This repository is [MIT](./LICENSE) as well.
