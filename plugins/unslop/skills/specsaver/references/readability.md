# Readable Specifications

Use this guidance when drafting, rewriting, reviewing, or verifying prose.
Develop a connected explanation that a reader can follow without
reconstructing the relationships between isolated facts.

## Organization

Start with organization. Are concepts defined before their use? Can a reader
follow the lifecycle or explanation without collecting rules from scattered
sections? Are an invariant and its exceptions beside the behaviour they
govern? Would an ordered sequence, table, or different outline reveal those
relationships more directly? Restructure when needed; sentence polishing alone
cannot repair a document whose explanation is out of order.

## Sentences

- **Topic and continuity.** Make the component, resource, or process currently
  being explained clear. Introduce the context a reader needs before the new
  information. Connect each sentence to the relevant preceding idea; do not
  force every sentence to use the same subject or an introductory connective.
- **Subject and action.** Keep the subject near its verb. Move interrupting
  definitions or qualifications where they can be understood without holding
  an unfinished sentence in memory. Let verbs express the real action rather
  than hiding it in an abstract noun and an uninformative verb.
- **Descriptive voice.** Describe components, concepts, and behaviour in a
  detached, factual voice. Components can initiate actions; describe those
  actions without personification. State conditions and ordering directly,
  avoiding first-person walkthroughs and conversational, blow-by-blow
  narration. Present tense is appropriate for system facts.
- **Sentence flow.** Vary sentence length and structure to suit the thought.
  Keep related clauses together when this makes their connection easier to
  follow. Use punctuation and connecting words to express relationships, pace
  the explanation, and place emphasis. Split sentences when competing claims
  or nested qualifications obscure the point; do not fragment a coherent
  thought merely to shorten it.
- **Emphasis.** Identify what the reader should emphasise and place it in a
  *stress position*: the end of a sentence or a complete clause before a colon
  or semicolon, where the grammar reaches full closure. Give linked claims
  separate stress positions when each deserves emphasis. Preserve the scope
  of conditions and obligations when restructuring.
- **Distinct claims.** Give independently important claims enough space to be
  understood, using separate sentences or a list where useful. Preserve which
  conditions apply to which obligations when splitting or moving text.
- **Useful repetition.** Repeat a precise term when it anchors the next idea
  or disambiguates a pronoun. Repeating a term is different from repeating an
  assertion. Avoid synonym changes that make readers infer whether two names
  mean the same thing.
- **Logical connections.** Decide whether the source establishes sequence,
  contrast, cause, or an example before choosing connecting language. If a
  clear explanation requires a guess, flag the missing relationship rather
  than supplying it.

Use these diagnostics where they reduce reader effort. Do not enforce word
counts, punctuation quotas, passive-voice bans, or replacement of necessary
technical vocabulary. Leave already-clear prose alone.

## Examples of judgement

The [cleanup-worker example](gotchas-and-examples.md#1-rewrite-a-necessary-but-badly-written-passage)
shows a complete, connected rewrite. The examples below focus on edits that
can affect meaning.

**Buried ordering constraint:**

> The worker, which must commit the lease before sending any request,
> processes the delivery.

can become:

> The worker processes the delivery. Before sending any request, it must
> commit the lease.

The constraint gains prominence without changing its force or implying that
the lease must be committed before every part of processing begins.

**Unsupported causal connection:**

> The service uses a queue. Requests are processed in order.

does not by itself license:

> The service uses a queue, so requests are processed in order.

The connective supplies a causal explanation that the source did not give.
The original also leaves the relationship unclear. Use the attempted rewrite
to identify what needs clarification: does the queue establish the processing
order? Check the source or ask the author before making that connection.

If that relationship is confirmed, a connected rewrite is:

> The service uses a queue to process requests in order.

This keeps the service as the topic and places ordered processing in the
stress position. If the relationship remains unresolved, preserve the claims
and flag the missing explanation.

Do not turn adjacency into causation, or replace "supports" with "guarantees"
merely to make the verb stronger.
