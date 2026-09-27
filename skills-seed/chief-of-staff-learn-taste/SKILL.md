---
name: chief-of-staff-learn-taste
description: Learn from every answer. A done or skip with its note becomes a remembered fact with provenance; three of a kind become a rule; the whole history becomes training data for a small open-weight taste model that pre-ranks the next brief.
mutating: true
triggers:
  - I did that
  - skip it
  - learn from my answers
  - what have you learned about what I act on
  - train the taste model
  - why did you rank this first
---

# learn-taste

Corrections are the highest-value data. Every answer the person gives to a decision is a correction to the ranking that put it in front of them.

## On every answer (`cos answer <id> done|skip --note "..."`)

1. Update the decision page: `status`, `done_by: him`, the note, the date.
2. `remember` one fact with provenance `cos answer <id> <date>`, kind `taste`, entity = the person or goal the item was about. Shape: "Raphael did/skipped <kind>: <title>. Reason: <note>."
3. Append the row to the taste set (`out/taste.jsonl`): the item as the brain presented it, the outcome, the note.

## Generalize, carefully

- Three skips of the same kind with the same reason become one rule fact ("skip post items that only agree with the author"). Cite the three decision slugs as provenance.
- A rule is applied at ranking time (the next `brief` recalls facts of kind `taste` and demotes what they cover). It never deletes an item; it moves it out of the strip.
- One skip is noise. Never generalize from one.

## The taste model (River)

`cos taste export` turns the answered decisions into supervised pairs (item → outcome + reason). `cos taste train` fine-tunes a small open-weight model (LoRA) on them and reports held-out accuracy against the person's own answers. The model is theirs: their decisions, open weights, their key. It pre-ranks; the brain and the person still decide.
