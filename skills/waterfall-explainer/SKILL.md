---
name: waterfall-explainer
description: |
  Write explanatory prose in waterfall order, where nothing is referenced before it has been
  explained, so a reader who does not already know the subject can follow it start to finish.
  Use this for research notes, API and library evaluations, design documents, architecture
  write-ups, post-mortems, onboarding explainers, and any answer to "how does X work", "how
  would we implement X", "does X fit what we have", "read these docs and tell me what you
  think", or "explain this to me". Use it even when the user did not say "document": if the
  answer is longer than a few paragraphs and the reader has to learn something new to act on
  it, this is the shape it should take. Use it especially when someone says an earlier answer
  was too terse, too bullet-pointy, assumed too much, or "impossible to read if you don't
  already know what it's about". Do not use it for quick factual lookups, code diffs, commit
  messages, changelogs, or reference tables where the reader already has the context.
license: MIT
---

# Waterfall explainer

## The failure this exists to fix

The default shape for a researched answer is a list of conclusions: findings up front, each
one a line or two, terminology used freely because the writer has it loaded. That shape is
excellent for someone who already knows the subject and wants the delta. It is unreadable
for everyone else, and the reason is specific. A thesis is compressed evidence. A reader who
cannot decompress it gets a sequence of claims they have no way to evaluate, and by the time
the explanation arrives, three sentences later, they have already stopped tracking.

One user put it exactly: "bullet points are impossible to read if you don't know what it's about." Terse
is unreadable when you do not already know the subject.

Waterfall order fixes it by making one promise and keeping it: at no point in the read does
the text lean on something it has not already explained. The payoff is that the reader never
has to hold an unexplained term in suspension, which is the thing that actually costs them
the thread.

## Find the order before writing a sentence

List every claim you intend to make and every term you intend to use. For each one, ask what
the reader must already understand for it to land. Then sort so that dependencies come first.

The result is almost never the order you discovered things in, and almost never the order of
importance. The most interesting finding usually lands last, because it depends on the most
setup. Resist moving it up. An important claim delivered to a reader who cannot evaluate it
is not important yet, it is just loud.

When two orderings are both valid, prefer the one where the reader spends less time holding
open questions.

## The three movements

Most of these documents compare something external against something the reader's team owns.
That naturally falls into three movements, and keeping them separate is most of the work:

1. **The subject on its own terms.** What the external thing is, how it is built, what it
   constrains. Written as if the reader's codebase did not exist. No comparisons yet, because
   a comparison needs both sides defined.
2. **Our side, in the same vocabulary.** Recap the parts of the reader's own system the
   comparison will touch, including things they nominally know. They know their code; they do
   not necessarily hold the exact method list or the exact invariant in working memory, and
   the join depends on specifics.
3. **The join.** What fits, what does not, and what it costs. Only here does anything get
   compared, and by now both sides are defined, so each comparison is one sentence instead of
   a paragraph of re-explanation.

Interleaving these is the most common way the order breaks. A sentence like "their batching
maps onto our resolver" in movement 1 forces the reader to know both halves before either has
been explained.

If the document is not a comparison, the same discipline applies with different movements:
mechanism before consequence, normal case before edge case, the thing before its history.

## Paragraph rules

**Explain each thing once, fully, where it first appears.** Splitting an explanation across
two places means the first mention is incomplete and the second is a repetition. Both are
worse than one complete pass.

**State consequences, do not leave them as an exercise.** If a limit is 60 points and a write
costs 3, write the sentence that says this is twenty writes per five minutes and that this
does not work. The arithmetic is the finding. Leaving it implicit is how a document gets
nodded at and ignored.

**Prefer prose paragraphs to bullets for anything that has reasoning in it.** A bullet list
is a good shape for enumerable, parallel, independent items: endpoints, parameters, ordered
steps, source lists. It is a bad shape for an argument, because it strips the connective
tissue that carries the argument.

**Name the thing you are about to lean on, even if it feels obvious to you.** The test is not
"would a colleague know this" but "does this sentence work if they do not have it loaded".

## Promissory notes

Sometimes a fact genuinely has to be stated early and only pays off later. Handle it by saying
so: "three differences matter later", "this will come back in the section on the sink". That
converts an unexplained forward reference into an explicit, bounded loan, and the reader can
stop trying to resolve it.

Then redeem it, visibly: "the second difference, the one about scope, is what breaks here".
An unredeemed promise is worse than never making it.

## Honesty about what you checked

Research documents get quoted later, so what is verified and what is inferred have to be
distinguishable in the text, not just in your head.

- Say what you read and against what version or date.
- When something is plausible but unverified, say so in the sentence that makes the claim,
  not in a disclaimer at the end: "this was not verified in this pass, check it before
  writing the transport".
- When an existing document or note is contradicted by what you found, say which one and
  correct it rather than quietly writing something different.
- Link to the specific section, not the landing page. Verify the anchors actually exist
  rather than guessing them from heading text, because a confidently wrong deep link is worse
  than a page link.
- End with a `## Sources` section listing what you used, noting which claim each source
  backs when that is not obvious.

## Register

Plain and neutral. These documents are read by people who have to decide or act on them,
so flourish reads as padding.

No em or en dashes: use a period, a comma, a colon, or parentheses. No decorative bold, no
bullet lists whose items are a bold header and a colon, no emoji, sentence case in headings.
No generic upbeat closer. If the project has a documentation house style with a dated snapshot
line, a conventions file, or a doc-lint script, follow it and run the script before claiming
the work is done.

## Before you deliver, read it as the reader

Walk the document once, in order, pretending you know nothing about the subject. Stop at the
first sentence that uses something not yet explained. That is the only test that matters, and
it reliably finds two or three breaks in a first draft.

Then check: does every section depend only on sections above it, is every promissory note
redeemed, does every number that implies a consequence have that consequence written out, and
could a reader act on this without asking you a follow-up question.

## Worked contrast

The same finding, written both ways.

Terse, and unreadable to anyone not already fluent:

> `dedup.Store` won't work for the provider's webhooks: retries reuse the event id across
> endpoints, so `Seen` has to be keyed per endpoint, not globally, and the consumer owns the
> TTL. Ack first, process async on timeout.

Waterfall, after the webhook flow and the dedup store have each been explained in their own movement:

> Our dedup store remembers an event id once and rejects every later copy of it, whichever
> endpoint receives it. The provider sends the same event to every endpoint we registered,
> with the same id, and retries each delivery separately until that endpoint answers 200. So
> the delivery to the second endpoint looks to us like a duplicate of the first, and we drop it.
>
> So the idea of remembering ids is reused and the key is not: the key has to be the pair of
> endpoint and event id. The deeper consequence is about time rather than format. The provider
> keeps retrying for up to three days, while our store forgets an id after an hour. So
> something has to keep ids for as long as the provider may resend them, and only the consumer
> knows how long that is, because only the consumer reads the provider's retry policy.

The second is longer, and length is not the point. The point is that the first assumes four
things the second establishes, so only one of them can be read by the person who has to
approve the work.
