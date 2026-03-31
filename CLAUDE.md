# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A curated, interactive single-page reference guide of landmark papers, assays, and tools in computational biology and genomics since 2010. Covers 21 domains including CRISPR, single-cell genomics, ML/AI for biology, protein folding, clinical genomics, and more.

## Running the Project

This is a zero-dependency, no-build static HTML application:

```bash
# Open directly in browser
open index.html

# Or serve via local HTTP server (recommended for testing localStorage behavior)
python3 -m http.server 8000
# Visit http://localhost:8000
```

There is no build step, no package manager, no test suite, and no linting configuration.

## Architecture

The entire application is `index.html` (~3,600 lines). It is organized into three logical sections:

**Embedded CSS** — CSS custom properties for design tokens (colors, typography), card and carousel layout, and responsive breakpoints at ≤900px (tablet), ≤640px (mobile), ≤380px (very small).

**Data layer** — A `DATA` array of ~168 entry objects near the top of the `<script>` block. Each entry has:
```javascript
{
  id, year, cats,       // metadata
  impact,               // 1–5 score
  title, authors, journal, summary,
  job_impact,           // career relevance for practitioners
  pros, cons,           // string arrays (abbreviation-tooltip-enabled)
  details,              // technical deep dive
  url
}
```

**Application logic** — Vanilla ES6+ JavaScript managing:
- Global mutable state: `currentSearch`, `currentCat`, `currentSort`, `_carouselIdx`, `showUnreadOnly`, `_carouselData`
- Rendering: `render()` → `getFiltered()` → `renderCarousel()` → `renderCard()`
- Persistence: `getRead()`/`saveRead()`/`toggleRead()` via `localStorage`
- Abbreviation tooltips: `ABBR` object (~150 entries) + `addTooltips(html)` wraps recognized terms in `<abbr>` tags at render time
- Carousel: 50% center / 25% left-peek / 25% right-peek layout; collapses to 100% on mobile

## Making Content Changes

To add a new entry, append an object to the `DATA` array following the existing schema. The `id` should be unique and incrementing. The `cats` array should use existing category keys from `catLabels` (e.g., `"crispr"`, `"ml_ai"`, `"single_cell"`).

To add a new category, add a key/value to `catLabels` and create a corresponding filter pill in the controls HTML section.

To add an abbreviation, add an entry to the `ABBR` object. Abbreviations are automatically linked wherever they appear in `pros`, `cons`, `summary`, `details`, and `job_impact` fields.
