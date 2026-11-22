---
name: self-improve
description: >
  Weekly retrospective over Claude Code chat history: repeated requests, corrections and
  frustration, hand-typed instructions a rule should cover, skills used vs never used, plus an
  ecosystem radar (Claude Code changelog, Go releases, skills marketplaces). Writes one report with
  proposed diffs; never edits config. Use for "self-improve", "ретро", "что я повторяю",
  "почему я горю", "разбор недели", "weekly retro", "what should I automate".
tools: Bash, Read, Grep, Glob, WebFetch
license: MIT
---

# Self-improve: weekly retrospective

Output is ONE file: `~/.claude/reports/self-improve-YYYY-MM-DD.md` (today's date). Read-only
everywhere else. Never edit CLAUDE.md, AGENTS.md, skills, settings.json or hooks, even when a fix
is obvious: the user decides later.

## 0. Read the decisions log

If the repo this skill lives in (`realpath` of this skill's folder, then up to the repo root) keeps a decisions log at its root, a markdown file of settled setup decisions and verdicts on new tools, read it first. Do not propose anything it already settled, and keep its verdicts unless something material changed. Put new radar verdicts in the report as a ready-to-append block for its verdicts table; the user appends it.

## 1. Mine the transcripts

```bash
mkdir -p ~/.claude/reports
python3 -I <this skill>/scripts/mine.py | head -250
```

The script picks the window itself: since the newest `~/.claude/reports/self-improve-*.md`, else
the last 7 days. Override with `--since YYYY-MM-DD`. It reads `~/.claude/projects/*/*.jsonl`,
keeps only human-typed messages (drops tool results, system reminders, task notifications,
compaction summaries, pasted log blocks) and prints: counts per project, interrupts, frustration
and correction messages (swearing, "no", "again", "I already said", "?????", in English and Russian), hand-typed intent
counts, repeated 3-grams, skills invoked vs never invoked.

Need more context for a finding? Open the one session with python and read around that
timestamp. Do not cat whole jsonl files; they are tens of MB.

## 2. Turn signals into findings

A finding needs evidence: a count (messages or sessions, 3+ for "repeated") and one short verbatim
quote with date and project. No quote, no finding.

Look for:
- The same instruction typed again and again ("commit and push", "no tests", "all in one
  pass"). Candidate for a skill or a CLAUDE.md line.
- Corrections after Claude acted: what Claude did, what the user wanted. Candidate for a rule.
- Interrupts and "?????" bursts: usually slowness, hanging commands, or acting when only asked a
  question. Candidate for a hook if a rule already exists and is still ignored.
- Skills that should have fired but did not (the task matched, the Skill tool was not called):
  sharpen the description triggers. Never invoked this week and in the previous reports
  (or `--since` a month back): propose removal.

## 3. Check against existing config before proposing

Read `~/.claude/CLAUDE.md`, `~/.claude/rules/*.md`, `~/.claude/settings.json` hooks
(`~/.claude/hooks/*.py`), and the CLAUDE.md of each project that produced findings. For each
finding decide:
- Not covered: propose a new rule, skill or hook.
- Covered but violated: the rule is not enough; propose a stronger form (hook or skill), or a
  rewording that names the exact trigger.
- Covered and followed: drop it.

Pick the cheapest mechanism that works: CLAUDE.md line for judgment calls, skill for multi-step
recipes, hook for "must never happen" (prod pushes, probing prod, printing secrets). Remember the
CLAUDE.md / AGENTS.md twin rule: a per-folder CLAUDE.md diff needs the identical AGENTS.md diff.

Each proposal is an exact unified diff against the real file, small enough to paste.

## 4. Ecosystem radar

Only items since the last report. Fetch, skim, keep what touches the stack the transcripts' projects use
(read it from their CLAUDE.md or AGENTS.md; Claude Code skills and hooks always count):

| Source | URL |
|---|---|
| Claude Code changelog | https://code.claude.com/docs/en/changelog (raw: https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md) |
| Claude Code what's new | https://code.claude.com/docs/en/whats-new |
| Go releases | `curl -s 'https://go.dev/dl/?mode=json' \| python3 -c "import json,sys;print([r['version'] for r in json.load(sys.stdin)])"`, notes at https://go.dev/doc/devel/release |
| Skills directory | https://skills.sh |
| Official plugins / skills | https://github.com/anthropics/claude-plugins-official, https://github.com/anthropics/skills |

Verdict per item: adopt, try, or ignore. Default is ignore; adopt needs a concrete pain from
section 2 that it removes. At most 6 radar items.

## 5. Report format (fits one screen, about 40 lines)

~~~markdown
# self-improve YYYY-MM-DD (window: <since> to <today>)

<N> messages, <M> sessions, <K> interrupts, <F> frustration messages.

## Top findings
1. <finding>. Evidence: <count>, "<quote>" (<date>, <project>).
   Proposal (<CLAUDE.md|skill|hook>, <path>):
   ```diff
   ...
   ```

## Skills
Used: <name xN, ...>. Never used: <names>. Should have fired: <name>, because <evidence>.

## Radar
- <item>: adopt|try|ignore. <one-line reason>.

## Sources
- <urls fetched>
~~~

Rules for the report: at most 5 findings, ranked by how often they burned the user. Plain neutral
English, no em or en dashes, no bold labels, no filler. Quote the user in the original language.
Do not paste transcripts, secrets, tokens or env values. Finish by printing the report path and
the top three findings in three lines.
