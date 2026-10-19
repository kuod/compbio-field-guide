# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A curated, interactive single-page reference guide of landmark papers, assays, and tools in computational biology and genomics since 2010. Covers 23 domains including CRISPR, single-cell genomics, ML/AI for biology, protein folding, clinical genomics, and more.

## Running the Project

This is a zero-dependency, no-build static HTML application:

```bash
# Open directly in browser
open index.html

# Or serve via local HTTP server
python3 -m http.server 8000
# Visit http://localhost:8000
```

There is no build step, no package manager, and no linting configuration. A dependency-free data check lives in `tests/validate-data.js` (`node tests/validate-data.js`); run it after editing `DATA`. Helper scripts in `scripts/` verify references and PMIDs against NCBI and can be run from any directory.

## Architecture

The entire application is `index.html` (~4,000 lines). It is organized into three logical sections:

**Embedded CSS** — CSS custom properties for design tokens (colors, typography), card and carousel layout, and responsive breakpoints at ≤900px (tablet), ≤640px (mobile), ≤380px (very small).

**Data layer** — A `DATA` array of 179 entry objects near the top of the `<script>` block. Each entry has:
```javascript
{
  id, year, cats,       // metadata
  impact,               // 1–5 score
  title, authors, journal, summary,
  pros, cons,           // string arrays (abbreviation-tooltip-enabled)
  details,              // technical deep dive
  url,
  pmid,                 // optional PubMed ID string
  citations,            // optional citation count
  papers                // optional [{label, url, pmid?}] for multi-paper entries
}
```

**Application logic** — Vanilla ES6+ JavaScript managing:
- Global mutable state: `currentSearch`, `currentCat`, `currentSort`, `_carouselIdx`, `showUnreadOnly`, `_carouselData`
- Rendering: `render()` → `getFiltered()` → `renderCarousel()` → `renderCard()`
- Persistence: `getRead()`/`saveRead()`/`toggleRead()` store read ids in the URL hash (`#r=1,2,3`); `localStorage` is only read once to migrate the legacy key. `renderCarousel()` calls `updateReadState()` so read state survives every re-render.
- Abbreviation tooltips: `ABBR` object (~150 entries) + `addTooltips(html)` wraps recognized terms in `<abbr>` tags at render time
- Carousel: 50% center / 25% left-peek / 25% right-peek layout; collapses to 100% on mobile

## Making Content Changes

To add a new entry, append an object to the `DATA` array following the existing schema. The `id` must be unique (enforced by `tests/validate-data.js`) and incrementing. The `cats` array should use existing category keys from `catLabels` (e.g., `"crispr"`, `"ml_ai"`, `"single_cell"`).

To add a new category, add a key/value to `catLabels` and create a corresponding filter pill in the controls HTML section.

To add an abbreviation, add an entry to the `ABBR` object. Abbreviations are automatically linked wherever they appear in `pros`, `cons`, `summary`, and `details` fields.
