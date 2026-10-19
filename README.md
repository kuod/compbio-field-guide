# Computational Biology Field Guide

An interactive reference guide to landmark papers, assays, and tools in computational biology and genomics (mostly since 2010, plus a few foundational earlier methods such as t-SNE). 179 curated entries spanning 23 domains, with pros/cons, technical details, field impact ratings, and PubMed links.

**[View the guide](https://kuod.github.io/compbio-field-guide/)**

## Domains covered

sequencing · crispr · ml/ai · single-cell · immunology · epigenomics · drug discovery · spatial · tools/infra · gene editing · clinical genomics · delivery · population genomics · proteomics · RNA biology · foundation models · cancer genomics · protein folding · metagenomics · validated targets · drug modalities · causal inference · visualization

## Features

- **Carousel layout** — browse entries with keyboard arrows or swipe; center card is expanded
- **Filter by domain** — pill buttons to narrow by category
- **Sort** — by year (newest/oldest) or field impact score
- **Full-text search** — searches titles, authors, summaries, and technical details
- **Read tracking** — mark papers as read; filter to unread only; progress persists in the URL hash
- **Abbreviation tooltips** — ~150 field-specific terms auto-linked with hover definitions
- **PubMed links** — 145 entries link directly to their PubMed record for reference verification

## Technical details

Zero dependencies, no build step. The entire app is a single `index.html` file (~4,000 lines) with embedded CSS and vanilla ES6+ JavaScript.

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
  url,
  pmid,         // PubMed ID string (optional; omit for preprints/tools without a canonical paper)
  citations,    // citation count (optional)
  papers        // optional [{label, url, pmid?}]; when present, replaces the single url/pmid links
}
```

Use the `/add-paper` slash command in Claude Code for guided entry creation.

## Tests and maintenance scripts

```bash
node tests/validate-data.js     # schema, unique ids, valid categories, pmids.json in sync
```

The `scripts/` helpers (`verify_refs.py`, `fix_pmids.py`, `inject_pmids.py`, `build_papers.py`) query doi.org / NCBI E-utilities and can be run from any directory. `index.html` is the source of truth for PMIDs; `verify_refs.py` only fills in ids missing from `scripts/pmids.json`.

## License

MIT
