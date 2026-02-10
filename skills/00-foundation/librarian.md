---
name: librarian
description: >
  Skill discovery and routing. Maps fuzzy user intent to concrete skills
  using fuzzy matching and semantic search.
version: "1.0.0"
dependencies:
  - constitution
reasoning_mode: linear
---

# Librarian — Skill Discovery

> _"You don't need to know the exact name. Just tell me what you need."_

## Role

The Librarian is the **entry point** for every user request. It:

1. Parses the user's natural-language intent.
2. Matches it to one or more registered skills.
3. Returns a ranked list of candidates with confidence scores.

---

## Capabilities

### Fuzzy Matching

Handles typos and abbreviations gracefully.

| User types   | Resolved skill      | Confidence |
|-------------|---------------------|------------|
| `clnup`     | `cleanup`           | 0.92       |
| `refactr`   | `refactor`          | 0.88       |
| `fmt`       | `format`            | 0.85       |
| `tdd`       | `test-driven-dev`   | 0.95       |

Algorithm: Levenshtein distance + prefix matching against `registry.yaml`.

### Semantic Search

For intent-based queries that don't map to a skill name.

| User says                          | Resolved skill           |
|------------------------------------|--------------------------|
| "make this code cleaner"           | `cleanup`                |
| "I need to rename some variables"  | `cleanup → safe-renaming`|
| "add tests for this function"      | `tdd-loop`               |
| "split this file"                  | `refactor → extract`     |

Algorithm: Embedding similarity against skill descriptions in `registry.yaml`.

---

## Routing Protocol

```text
1. user_input → librarian.parse(input)
2. candidates = librarian.match(parsed_intent, registry)
3. if candidates[0].confidence >= 0.80:
       return candidates[0]
   elif candidates[0].confidence >= 0.60:
       return ask_user("Did you mean: {candidates}?")
   else:
       return ask_user("I couldn't find a matching skill. Can you rephrase?")
```

---

## Fallback

If no skill matches with confidence ≥ 0.60, the Librarian:

1. Logs the unmatched query for future skill gap analysis.
2. Suggests the closest 3 skills.
3. Offers to create a new skill stub from `templates/skill-template.md`.
