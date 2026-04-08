#!/usr/bin/env python3
"""
inject_pmids.py — Add pmid fields to DATA entries in index.html
and fix known URL issues.
"""
import json, re

HTML = "../index.html"
PMIDS = "pmids.json"

with open(PMIDS) as f:
    pmids = json.load(f)   # {str(id): str(pmid)}

with open(HTML, encoding="utf-8") as f:
    html = f.read()

# ── URL fixes ─────────────────────────────────────────────────────────────────
url_fixes = {
    # ID 157 (ESM Metagenomic Atlas): same URL as ID 14 (ESMFold). Both are
    # actually the same Lin et al. Science 2023 paper, so keep as is.
    # But ID 14 AND 157 sharing a URL is intentional — one entry describes the
    # tool, the other the application. No fix needed.
}

for old, new in url_fixes.items():
    html = html.replace(old, new)

# ── Inject pmid fields ────────────────────────────────────────────────────────
# Strategy: for each entry block, find "url: ..." and insert pmid after it
# Pattern: find id line, then find url line in same block

count = 0
for id_str, pmid in pmids.items():
    eid = int(id_str)

    # Match the entry block: id: N, followed eventually by url: "..."
    # We need to find the url: line for this specific id and add pmid after it
    # Use a pattern that finds id: N near the start of a block
    # then the first url: after it (before the next id: block)

    # Find position of "id: N," in the file
    id_pattern = re.compile(
        rf'\bid:\s*{eid}\b',
    )
    id_match = id_pattern.search(html)
    if not id_match:
        print(f"  ID {eid}: id marker not found in HTML")
        continue

    # Find the url: line after this id marker (and before the next entry)
    # Search from id_match position forward
    start = id_match.start()
    # Find next entry start (id: N+1 or similar) as a limit
    next_entry = re.search(r'\n  \{', html[start + 10:])
    end = start + 10 + next_entry.start() if next_entry else len(html)

    block = html[start:end]

    # Check if pmid already injected
    if 'pmid:' in block:
        continue

    # Find the url: line in this block
    url_match = re.search(r'(    url:\s*"[^"]+"\n)', block)
    if not url_match:
        print(f"  ID {eid}: url line not found")
        continue

    url_line = url_match.group(1)
    pmid_line = f'    pmid: "{pmid}",\n'
    new_block = block.replace(url_line, url_line + pmid_line, 1)

    html = html[:start] + new_block + html[end:]
    count += 1

print(f"Injected {count} pmid fields")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)
print("Wrote index.html")
