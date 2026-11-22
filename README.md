# agent-skills

General skills for coding agents (Claude Code, Codex and others that read `SKILL.md`): explanatory
writing, skill audits and a weekly retrospective of your Claude Code chats.

## Skills

| Skill | What it does |
|---|---|
| [waterfall-explainer](skills/waterfall-explainer) | Writes explanations in waterfall order, where nothing is used before it is explained, so a reader new to the subject can follow from start to finish |
| [skill-audit](skills/skill-audit) | Audits `SKILL.md` files for triggering and clarity: vague descriptions, missing trigger phrases, overlap with other skills, unclear instructions |
| [self-improve](skills/self-improve) | Weekly retrospective over your Claude Code chat history: repeated requests, corrections, interrupts, skills that should have fired, plus a radar of Claude Code and Go releases. Writes one report with proposed diffs and never edits your config. Needs Python 3 |

## Install

As a Claude Code plugin:

```bash
claude plugin marketplace add bulbetski/agent-skills
claude plugin install agent-skills@bulbetski-agent-skills
```

One skill, for any agent that supports the `npx skills` installer:

```bash
npx skills add bulbetski/agent-skills --skill waterfall-explainer
```

Or copy a folder from `skills/` into `~/.claude/skills/` (or your agent's skills folder).

## License

MIT, see [LICENSE](LICENSE).
