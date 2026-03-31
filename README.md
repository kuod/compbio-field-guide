# Computational Biology Field Guide

An interactive reference guide to landmark papers, assays, and tools in computational biology and genomics since 2010. ~170 curated entries spanning 22 domains, with pros/cons, technical details, and field impact ratings.

**[View the guide](https://kuod.github.io/compbio-field-guide/)**

## Domains covered

sequencing · crispr · ml/ai · single-cell · immunology · epigenomics · drug discovery · spatial · tools/infra · gene editing · clinical genomics · delivery · population genomics · proteomics · RNA biology · foundation models · cancer genomics · protein folding · metagenomics · validated targets · drug modalities · causal inference

## Features

- **Carousel layout** — browse entries with keyboard arrows or swipe; center card is expanded
- **Filter by domain** — pill buttons to narrow by category
- **Sort** — by year (newest/oldest) or field impact score
- **Full-text search** — searches titles, authors, summaries, and technical details
- **Read tracking** — mark papers as read; filter to unread only; progress persists in the URL hash
- **Abbreviation tooltips** — ~150 field-specific terms auto-linked with hover definitions

## Technical details

Zero dependencies, no build step. The entire app is a single `index.html` file (~3,600 lines) with embedded CSS and vanilla ES6+ JavaScript.

```bash
# Open directly
open index.html

# Or serve locally
python3 -m http.server 8000
```

## Adding entries

Each entry in the `DATA` array follows this schema:

```javascript
{
  id,           // unique integer
  year,         // publication year
  cats,         // array of category keys (see catLabels in source)
  impact,       // field impact score 1–5
  title,
  authors,
  journal,
  summary,      // 2–3 sentence overview
  pros,         // string array
  cons,         // string array
  details,      // technical deep dive
  url
}
```

Use the `/add-paper` slash command in Claude Code for guided entry creation.

## License

MIT
