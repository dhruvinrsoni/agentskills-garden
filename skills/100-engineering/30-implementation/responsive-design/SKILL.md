---
name: responsive-design
description: >
  Make a web page work on every screen — phone to ultrawide — without text or
  media ever escaping its container. Invoke whenever building or changing any
  page/CSS that will be viewed on more than one screen size (i.e. always).
  Overflow and word-wrap bugs are treated as correctness bugs, not polish.
license: Apache-2.0
domain: engineering
status: published
tags: [category, build, coding, frontend, reversible]
keywords: [responsive, overflow, word-wrap, overflow-wrap, min-width, flexbox, grid, mobile, breakpoint, viewport, ellipsis]
metadata:
  version: 1.0.0
  reasoning_mode: linear
  skill_type: standard
---


# Responsive Design

> _"If text can escape its box, it will — on someone's screen."_

## Context

Invoke when authoring or editing any HTML/CSS that ships to a browser: a landing
page, a docs site, a card grid, a list/table view. **Content overflowing its
container is a correctness bug** (horizontal page scroll, text under other
elements, unreadable layouts), not a cosmetic nit — handle it with the same
seriousness as a logic error. Assume a real device range: ~320px phones →
tablets → laptops → ultrawide monitors.

---

## Micro-Skills

### 1. Drop in the overflow-safety baseline 🌿 (Eco Mode)

**Goal:** A defensive CSS layer that keeps the common offenders inside their box.
Add it once, near the top of the site's stylesheet, before component styles.

```css
*, *::before, *::after { box-sizing: border-box; }

/* media never wider than its container */
img, svg, video, canvas, iframe, embed, object { max-width: 100%; }
img, video, canvas { height: auto; }

/* long code / wide tables scroll inside themselves, not the page */
pre { overflow-x: auto; }

/* long words / URLs / hashes wrap instead of pushing the layout wide.
   :where() keeps specificity 0 so component styles still win. */
:where(h1, h2, h3, h4, h5, h6, p, li, dt, dd, td, th, figcaption, blockquote) {
  overflow-wrap: break-word;
}
```

### 2. The #1 cause: flex/grid items that won't shrink ⚡ (Power Mode)

**Nano: `min-width: 0` on flex/grid children.** A flex or grid item defaults to
`min-width: auto`, which **refuses to shrink below its content's intrinsic size**.
One long word or a wide sibling then forces the row past the container → overflow.
Any flex/grid child that holds text (or that should be allowed to shrink) needs
`min-width: 0` (and `min-height: 0` for column flex):

```css
.row { display: flex; gap: 1rem; }
.row .desc { flex: 1 1 auto; min-width: 0; }   /* now it can shrink + wrap */
```

This single rule fixes the majority of "text overflows the card" bugs. If the item
should truncate rather than wrap, add `overflow: hidden; text-overflow: ellipsis;
white-space: nowrap;` (single line) or a 2-line clamp:

```css
.clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
```

### 3. Fluid sizing, never fixed widths bigger than a phone 🌿 (Eco Mode)

- Prefer `%`, `fr`, `minmax()`, `clamp()`, `min()`, `max()` over fixed `px` widths.
- Responsive grids that reflow with no media query:
  `grid-template-columns: repeat(auto-fill, minmax(min(100%, 280px), 1fr));`
  The `min(100%, 280px)` stops the 280px track from overflowing a 320px phone.
- A `viewport` meta tag is mandatory: `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`.

### 4. Tables, and honoring notches 🌿 (Eco Mode)

- Wide tables: wrap in a scroll container or `table { display: block; overflow-x: auto; }` at narrow widths so they scroll instead of stretching the page.
- Use `env(safe-area-inset-*)` for fixed/edge UI on notched phones.

### 5. Verify across the real width range ⚡ (Power Mode)

**Nano: Width sweep.** Before declaring done, check at **~320, 375, 768, 1024,
1440, and 2560px** (browser devtools device toolbar, then drag-resize). At each:
no horizontal page scroll, no text under/over other elements, no clipped content,
no tall skinny "rectangle" columns. The fastest tell: if the page scrolls
sideways at any width, something overflowed — find it before shipping.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target_css` | `string` | yes | The stylesheet / component being made responsive |
| `layout_kind` | `string` | no | flex row, grid, table, prose — picks which guards apply |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `safe_css` | `string` | CSS with the baseline + per-layout overflow guards applied |
| `widths_checked` | `string[]` | The breakpoints verified (the width sweep) |

## Scope

- **In scope:** preventing overflow/word-wrap breakage; fluid sizing; the safety baseline; the width sweep.
- **Out of scope:** visual design/branding, color/theming, animation. This skill is about *robustness*, not aesthetics.

## Guardrails

- **Do not** paper over overflow with `html, body { overflow-x: hidden }` — it's a crutch that hides the real bug and **breaks `position: sticky`**. Fix the root cause (min-width:0, break-word, max-width).
- Never set a fixed width larger than ~320px on content that must fit a phone.
- Media (`img`/`video`/`iframe`) without `max-width: 100%` is an overflow waiting to happen.
- A flex/grid child holding text without `min-width: 0` is the default overflow bug — add it.

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Flex/grid child overflows | add `min-width: 0` (then wrap or clamp/ellipsis) |
| Long URL/word breaks layout | `overflow-wrap: break-word` (or `anywhere`) |
| Image/iframe too wide | `max-width: 100%` |
| Wide table on mobile | scroll container / `display: block; overflow-x: auto` |
| Tempted to use `overflow-x: hidden` on body | stop — find and fix the overflowing element instead |

## Success Criteria

- No horizontal page scroll at any width from ~320px up.
- No text escaping, clipping, or overlapping its container on any screen.
- Layout reflows sensibly (columns collapse, text wraps/clamps) rather than breaking.
- Verified with the width sweep (Micro-Skill 5).

## Failure Modes

- **Sideways scrollbar appears** → an element is wider than the viewport. **Recovery:** binary-search the DOM (or `* { outline: 1px solid red }`) to find it; apply min-width:0 / max-width / break-word.
- **Sticky header stopped sticking after a "fix"** → someone added `overflow` to an ancestor. **Recovery:** remove it; fix the actual overflow source.
- **Text truncated that shouldn't be** → an over-aggressive ellipsis/clamp. **Recovery:** allow wrap instead, or raise the line clamp.

## Examples

```text
Before:  .card { display:flex } .card .desc { flex:1 }
         → long description forces the card wider than the viewport (h-scroll)
After:   .card .desc { flex:1 1 auto; min-width:0; overflow-wrap:break-word }
         → description shrinks and wraps inside the card; no overflow
```

## Edge Cases

- **CJK / no-space text:** `overflow-wrap: break-word` may not break it; use `word-break: break-word` or `line-break: anywhere`.
- **`white-space: pre` blocks** won't wrap by design — give them `overflow-x: auto`.
- **Flex column** overflow needs `min-height: 0` (the vertical analog of min-width:0).
