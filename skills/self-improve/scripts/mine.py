#!/usr/bin/env python3
"""Mine Claude Code transcripts for a self-improve retrospective.

Usage: python3 -I mine.py [--since YYYY-MM-DD] [--projects ~/.claude/projects]

Default --since: the date in the newest ~/.claude/reports/self-improve-YYYY-MM-DD.md,
otherwise 7 days ago. Prints a compact plain-text digest; never prints tool output.
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os
import re

HOME = os.path.expanduser("~")
HOME_SLUG = HOME.replace("/", "-") + "-"  # project dir names start with the home path, slashes as dashes
FRUSTRATION = re.compile(
    r"бля|хуй|хуе|хуя|пизд|еба|ебу|заеб|нахуя|похуй|сука|"
    r"\bопять\b|\bснова\b|я же (говорил|сказал|просил)|сколько (раз|можно)|"
    r"\bзачем ты\b|\bне просил|\bне надо\b|\bнет[,.!\s]|\?{3,}|!{3,}|"
    r"\bagain\b|i (already )?(told|said|asked)|\bwhy did you\b|\bstop\b|\bwtf\b|fuck|\bshit\b|"
    r"not what i asked|didn.t ask|don.t do that|\bno[,.!]",
    re.I,
)
# Hand-typed instructions that a rule, skill or hook could cover. Extend as patterns emerge.
INTENTS = {
    "commit/push": r"коммит|закомм|пуш|запуш|commit|push",
    "deploy branches": r"\buat\b|\bstaging\b|\bprod\b|\bпрод|мэйн|\bmain\b|master|мастер|деплой|deploy",
    "no tests / be fast": r"без тестов|не тест|не надо тест|по-быстрому|быстрее|долго|too slow|no tests|skip (the )?tests|faster",
    "no phases / one shot": r"без этап|никаких этап|целиком|за раз|one.?shot|сразу всё|сразу все|no phases|all at once|in one (go|pass)",
    "logs": r"\bлог|\blogs?\b",
    "env / secrets": r"\bэнв|\benv\b|переменн|секрет|secret|env var",
    "regenerate images": r"перегенер|регенер|regenerat|промпт|prompt",
    "explain / doc": r"waterfall|humanizer|объясни|сводк|explain",
    "only answer, do not act": r"не просил|не делай|ничего не делай|пока ничего|just answer|only answer|don.t change|didn.t ask",
}
SKIP_PREFIX = ("<", "This session is being continued", "Caveat:")
STOP = set("и в на не что это как я ты мне по с а у то за из так же ну там все всё да "
           "the a to of and is it in for you that this".split())


def default_since():
    reps = sorted(glob.glob(os.path.join(HOME, ".claude/reports/self-improve-*.md")))
    if reps:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", reps[-1])
        if m:
            return m.group(1)
    return (dt.date.today() - dt.timedelta(days=7)).isoformat()


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(p, dict) and p.get("type") == "tool_result" for p in content):
            return None
        return "\n".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=default_since())
    ap.add_argument("--projects", default=os.path.join(HOME, ".claude/projects"))
    a = ap.parse_args()

    msgs, interrupts = [], collections.Counter()
    skills, slash, mentions, cwds = collections.Counter(), collections.Counter(), collections.Counter(), set()
    for path in glob.glob(os.path.join(a.projects, "*", "*.jsonl")):
        proj = os.path.basename(os.path.dirname(path)).replace(HOME_SLUG, "").strip("-")
        with open(path, errors="replace") as fh:
            for line in fh:
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                ts = o.get("timestamp") or ""
                if ts[:10] < a.since:
                    continue
                if o.get("cwd"):
                    cwds.add(o["cwd"])
                t, c = o.get("type"), (o.get("message") or {}).get("content")
                if t == "assistant" and isinstance(c, list):
                    for p in c:
                        if isinstance(p, dict) and p.get("type") == "tool_use" and p.get("name") == "Skill":
                            skills[(p.get("input") or {}).get("skill")] += 1
                if t == "attachment":
                    at = o.get("attachment") or {}
                    if at.get("type") == "skill_mention":
                        mentions[at.get("skillName")] += 1
                    if at.get("type") == "queued_command" and not str(at.get("prompt", "")).startswith("<"):
                        msgs.append((proj, ts[:16], str(at["prompt"])))
                if t != "user" or o.get("isMeta") or o.get("isSidechain") or o.get("isCompactSummary"):
                    continue
                if (o.get("origin") or {}).get("kind") not in (None, "human"):
                    continue
                txt = text_of(c)
                if not txt:
                    continue
                m = re.search(r"<command-name>(.*?)</command-name>", txt)
                if m:
                    slash[m.group(1)] += 1
                if txt.startswith("[Request interrupted"):
                    interrupts[proj] += 1
                    continue
                if txt.startswith(SKIP_PREFIX):
                    continue
                msgs.append((proj, ts[:16], txt))

    seen, uniq = set(), []
    for m in sorted(msgs, key=lambda m: m[1]):
        key = (m[0], " ".join(m[2].split())[:200])
        if key not in seen:
            seen.add(key)
            uniq.append(m)
    msgs = uniq
    print(f"since {a.since}: {len(msgs)} human messages, {sum(interrupts.values())} interrupts {dict(interrupts)}")
    print("\n## per project")
    for p, n in collections.Counter(m[0] for m in msgs).most_common():
        print(f"{n:4} {p}")

    print("\n## frustration / corrections (newest 40)")
    fr = [m for m in msgs if FRUSTRATION.search(m[2])]
    print(f"total {len(fr)}")
    for p, ts, txt in sorted(fr, key=lambda m: m[1])[-40:]:
        print(f"- {ts} [{p}] {' '.join(txt.split())[:220]}")

    print("\n## hand-typed intents (messages / sessions)")
    for name, rx in INTENTS.items():
        hit = [m for m in msgs if re.search(rx, m[2], re.I)]
        if hit:
            ex = " ".join(hit[-1][2].split())[:120]
            print(f"{len(hit):4} / {len(set(m[0] for m in hit))} proj  {name}: e.g. \"{ex}\"")

    print("\n## repeated phrases (3+ messages, word 3-grams)")
    grams = collections.Counter()
    for _, _, txt in msgs:
        txt = re.split(r"<pasted_content|[{\[]", txt)[0][:400]
        txt = re.sub(r"(https?:/)?/\S+|@\S+", " ", txt.lower())
        w = [x for x in re.findall(r"[a-zа-яё_-]{2,}", txt) if x not in STOP]
        grams.update(set(" ".join(w[i:i + 3]) for i in range(len(w) - 2)))
    for g, n in grams.most_common(60):
        if n >= 3:
            print(f"{n:3}x {g}")

    print("\n## skills invoked (Skill tool) / slash commands / mentions")
    print(dict(skills.most_common()), dict(slash.most_common()), dict(mentions.most_common()))
    installed = {os.path.basename(os.path.dirname(f)) for f in glob.glob(os.path.join(HOME, ".claude/skills/*/SKILL.md"))}
    for cwd in cwds:
        installed |= {os.path.basename(os.path.dirname(f)) for f in glob.glob(os.path.join(cwd, ".claude/skills/*/SKILL.md"))}
    used = {str(s).split(":")[-1] for s in list(skills) + list(mentions)} | {s.lstrip("/") for s in slash}
    print("never invoked:", ", ".join(sorted(installed - used)))


if __name__ == "__main__":
    main()
