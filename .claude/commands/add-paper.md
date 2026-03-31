---
description: Add a new paper or tool entry to the compbio field guide
allowed-tools: Read, Edit, WebFetch, AskUserQuestion
argument-hint: [paper URL, DOI, or title]
---

You are adding a new entry to the DATA array in `index.html` of the compbio-field-guide.

## Step 1 — Read current state

Read `index.html` and extract:
- The highest `id` value currently in DATA (the new entry gets that value + 1)
- All valid category keys from the `catLabels` object (e.g. "crispr", "ml_ai", "single_cell", etc.)

## Step 2 — Gather paper info

The user provided: $ARGUMENTS

If a URL was provided, use WebFetch to retrieve the paper page and extract: title, authors, journal, and year.

If $ARGUMENTS is empty, use AskUserQuestion to ask the user for the paper title or URL before continuing.

## Step 3 — Fill in the schema

You need values for every field below. Use your knowledge of the paper where confident. Use AskUserQuestion for anything you cannot determine — especially `cats`, `impact`, `job_impact`, `pros`, `cons`, and `details`.

- `year` — publication year (integer)
- `cats` — array of 1–3 category keys; show the user the valid options from catLabels and ask them to choose
- `impact` — integer 1–5; ask the user or estimate based on journal prestige and citation impact
- `title` — full paper or tool title
- `authors` — "LastName et al." or "ToolName (org)" format
- `journal` — publication venue or platform (e.g. "Nature", "bioRxiv", "GitHub")
- `summary` — 1–2 sentence plain-language overview of what the paper does
- `job_impact` — 1–2 sentences on why this matters for biotech/pharma practitioners (hiring relevance)
- `pros` — array of 2–4 concise advantage strings; may use abbreviations defined in the ABBR object
- `cons` — array of 1–3 concise limitation strings
- `details` — 2–4 sentence technical paragraph covering methods, key algorithms, and downstream tools
- `url` — canonical link to the paper or resource

## Step 4 — Insert the entry

Use Edit to append the new object to the DATA array in `index.html`. Insert it just before the closing `];` that ends the DATA array.

Match the formatting of existing entries exactly:
- Add a comma after the previous last entry if one is missing
- Use the same indentation (two spaces inside the array, consistent property alignment)
- End the new object with a trailing comma

## Step 5 — Confirm

Tell the user the entry was added with its assigned id and briefly summarize the title, year, and categories used.
