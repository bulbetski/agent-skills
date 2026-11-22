---
name: skill-audit
description: >
  Audit and improve Claude Code skill files (SKILL.md) for better agent triggering and understandability.
  Use when the user asks to: review skills, audit skills, improve skill descriptions, check skill quality,
  "make my skills better", "fix skill triggering", "why isn't my skill triggering", "review my SKILL.md",
  "audit my skills folder", "improve skill descriptions", "skills aren't working", or wants to ensure
  their skills are well-written and trigger correctly on user input. Also trigger when the user mentions
  skill quality, skill relevance, or skill maintenance.
license: MIT
---

# Skill Audit

Audit skill files (SKILL.md) to improve agent triggering accuracy and instruction clarity.

## When to use

- User asks to review, audit, or improve their skills
- User reports a skill not triggering when expected
- User wants to check skill quality across a folder
- After creating or modifying skills, as a quality pass

## Audit process

### Step 1 — Discover skills

Find all SKILL.md files in the target directory (default: current working directory). If the user points to a specific folder, use that. Read every SKILL.md found.

### Step 2 — Evaluate each skill

For each skill, check these criteria:

#### Description quality (most important — this is what the agent sees to decide whether to trigger)

| Problem | What to look for |
|---------|-----------------|
| **Too vague** | Generic descriptions like "helps with X" without concrete trigger phrases |
| **Missing user phrases** | Description only uses technical terms, not how users actually ask ("how should I name this" vs "naming conventions") |
| **Scope-limiting language** | Phrases like "for this project" or "for this codebase" that prevent triggering in other contexts |
| **No trigger guidance** | Says what the skill IS but not WHEN to use it — agent can't decide when to invoke |
| **Missing disambiguation** | When multiple skills could match, no guidance on which one to pick (e.g. an audit of a live site vs an audit of a Figma mockup) |
| **Too long** | Description over ~200 words becomes noise; the agent skims metadata, not essays |

A good description answers: "If a user typed X in the chat, would the agent know to use this skill?" for at least 5-10 realistic X values.

#### Instruction clarity

| Problem | What to look for |
|---------|-----------------|
| **Ambiguous steps** | Instructions the agent could interpret multiple ways |
| **Missing tool requirements** | Skill needs specific tools (Bash, Playwright, MCP) but doesn't declare them in frontmatter or mention them early |
| **Wall of text** | No structure, no headers, no clear sequence — agent loses track |
| **Contradictory instructions** | Two sections say different things about the same step |
| **Dead references** | Points to files/scripts that may not exist (check with Glob) |

#### Relevance

| Problem | What to look for |
|---------|-----------------|
| **Duplicate skills** | Two skills covering the same use case in the same scope |
| **Obsolete content** | References to deprecated tools, old APIs, or abandoned workflows |
| **Overlap without disambiguation** | Similar skills that don't explain when to use one vs the other |

### Step 3 — Report findings

Present a summary table:

```
| Skill | Description | Clarity | Relevance | Issues |
|-------|-------------|---------|-----------|--------|
| name  | good/fix    | good/fix| good/fix  | brief  |
```

Then list specific issues per skill with concrete fix suggestions.

### Step 4 — Apply fixes

For each skill that needs changes:

1. **Description** — rewrite to include:
   - What the skill does (1 sentence)
   - Concrete trigger phrases in quotes that match how users actually type
   - Disambiguation from related skills when applicable
   - Use `>` YAML multiline syntax for readability

2. **Instructions** — only fix if the user asked for it or if there's a clear structural problem. Don't rewrite logic the user considers correct.

3. **Cross-references** — add "for X use skill-Y instead" where skills overlap

### Step 5 — Sync copies

If skills exist in multiple locations (e.g. project folder and ~/.claude/skills/), offer to sync changes to all copies. Don't sync without asking.

## Description writing checklist

When rewriting a description, verify:

- [ ] Starts with what the skill does, not "This skill..."
- [ ] Contains 3+ realistic user phrases in quotes
- [ ] No scope-limiting language ("for this project/codebase")
- [ ] Disambiguates from similar skills if any exist
- [ ] Under 200 words
- [ ] Uses `>` YAML multiline for readability
- [ ] Includes both technical terms AND casual user phrases

## Example: bad vs good description

**Bad:**
```yaml
description: This skill helps with Go testing in the current project.
```

**Good:**
```yaml
description: >
  Go testing guidelines: TDD workflow, ZOMBIES methodology, table-driven tests,
  mock generation with gomock. Use whenever writing or reviewing Go tests. Trigger
  on: "write tests for", "add test cases", "generate mocks", "how to mock this",
  "what tests should I add", or any _test.go workflow.
```

The good version tells the agent exactly when to fire and what phrases to watch for.
