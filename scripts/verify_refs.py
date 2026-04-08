#!/usr/bin/env python3
"""
verify_refs.py — Extract DOIs from compbio field guide, verify via doi.org,
look up PubMed IDs via NCBI E-utilities, and flag issues.

Output:
  - pmids.json : {entry_id: pmid_string}
  - issues.txt : duplicate URLs, 404s, mismatches
"""

import re
import json
import time
import sys
import urllib.request
import urllib.parse
import urllib.error
from collections import defaultdict

HTML_FILE = "../index.html"
OUT_PMIDS = "pmids.json"
OUT_ISSUES = "issues.txt"
NCBI_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_EFETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NCBI_RATE    = 0.4   # seconds between NCBI requests (≤3/sec without API key)
DOI_RATE     = 0.15  # seconds between doi.org HEAD requests

# ─── Parse DATA entries from index.html ──────────────────────────────────────

def parse_entries(html):
    """Extract id, title, authors, url from each DATA object."""
    # Match each {...} object in the DATA array
    # We rely on the fact that each entry starts with "id: N," on its own line
    entries = []
    # Split on entry boundaries
    blocks = re.split(r'\n  \{\n', html)
    for block in blocks[1:]:  # skip preamble
        id_m     = re.search(r'\bid:\s*(\d+)', block)
        title_m  = re.search(r'\btitle:\s*"([^"]+)"', block)
        authors_m= re.search(r'\bauthors:\s*"([^"]+)"', block)
        url_m    = re.search(r'\burl:\s*"([^"]+)"', block)
        if id_m and url_m:
            entries.append({
                "id":      int(id_m.group(1)),
                "title":   title_m.group(1) if title_m else "",
                "authors": authors_m.group(1) if authors_m else "",
                "url":     url_m.group(1),
            })
    return entries

# ─── DOI extraction ───────────────────────────────────────────────────────────

def extract_doi(url):
    """Return DOI string from URL, or None if not extractable."""
    u = url.strip()

    # Explicit DOI in URL path
    m = re.search(r'doi\.org/(10\.\S+)', u)
    if m:
        return m.group(1).rstrip('/')

    # science.org
    m = re.search(r'science\.org/doi/(10\.\S+)', u)
    if m:
        return m.group(1).rstrip('/')

    # NEJM
    m = re.search(r'nejm\.org/doi/(?:full|abs)/(10\.\S+)', u)
    if m:
        return m.group(1).rstrip('/')

    # Nature (articles/slug → 10.1038/slug)
    m = re.search(r'nature\.com/articles/([^\s/?#]+)', u)
    if m:
        slug = m.group(1)
        return f"10.1038/{slug}"

    # ACS
    m = re.search(r'pubs\.acs\.org/doi/(10\.\S+)', u)
    if m:
        return m.group(1).rstrip('/')

    # ASCO
    m = re.search(r'ascopubs\.org/doi/(10\.\S+)', u)
    if m:
        return m.group(1).rstrip('/')

    # BioMed Central / Genome Biology (URL contains full DOI)
    m = re.search(r'biomedcentral\.com/articles/(10\.\S+)', u)
    if m:
        return m.group(1).rstrip('/')

    # PLOS ONE
    m = re.search(r'journals\.plos\.org/plosone/article\?id=(10\.\S+)', u)
    if m:
        return m.group(1).rstrip('/')

    # genome.cshlp.org (Genome Research) — DOI not in URL, skip
    # academic.oup.com — DOI not directly in URL, skip (will use title search)
    # cell.com fulltext — PII in URL, can try title search
    # dl.acm.org
    m = re.search(r'dl\.acm\.org/doi/(10\.\S+)', u)
    if m:
        return m.group(1).rstrip('/')

    # IEEE Xplore — no clean DOI in URL
    # JMLR, MLPR, openreview, arxiv, github, terra.bio, 10xgenomics — skip

    return None

# ─── NCBI lookup ──────────────────────────────────────────────────────────────

def ncbi_pmid_by_doi(doi):
    """Return PMID string or None."""
    term = urllib.parse.quote(f"{doi}[doi]")
    url  = f"{NCBI_ESEARCH}?db=pubmed&term={term}&retmode=json&retmax=1"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        ids = data.get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None
    except Exception as e:
        return None

def ncbi_pmid_by_title(title):
    """Return PMID string or None using title search."""
    # Use first ~60 chars for search to avoid noise
    short = title[:80]
    term  = urllib.parse.quote(f"{short}[title]")
    url   = f"{NCBI_ESEARCH}?db=pubmed&term={term}&retmode=json&retmax=1"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        ids = data.get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None
    except Exception:
        return None

def ncbi_fetch_title(pmid):
    """Fetch paper title from NCBI to cross-validate."""
    url = f"{NCBI_EFETCH}?db=pubmed&id={pmid}&retmode=json&rettype=abstract"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        article = (data.get("PubmedArticleSet", {})
                      .get("PubmedArticle", [{}])[0]
                      .get("MedlineCitation", {})
                      .get("Article", {}))
        t = article.get("ArticleTitle", "")
        return str(t)
    except Exception:
        return ""

# ─── DOI verification ─────────────────────────────────────────────────────────

def verify_doi(doi):
    """HEAD request to doi.org; returns True if 200/301/302."""
    url = f"https://doi.org/{doi}"
    req = urllib.request.Request(url, method="HEAD",
          headers={"User-Agent": "Mozilla/5.0 verify_refs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status < 400
    except urllib.error.HTTPError as e:
        return e.code < 400
    except Exception:
        return False

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    with open(HTML_FILE, encoding="utf-8") as f:
        html = f.read()

    entries = parse_entries(html)
    print(f"Parsed {len(entries)} entries.")

    # Check for duplicate URLs
    url_to_ids = defaultdict(list)
    for e in entries:
        url_to_ids[e["url"]].append(e["id"])
    dup_urls = {url: ids for url, ids in url_to_ids.items() if len(ids) > 1}

    pmids   = {}   # id -> pmid
    issues  = []

    if dup_urls:
        issues.append("=== DUPLICATE URLs ===")
        for url, ids in sorted(dup_urls.items()):
            issues.append(f"  IDs {ids}: {url}")
        issues.append("")

    issues.append("=== PER-ENTRY RESULTS ===")

    for e in entries:
        eid   = e["id"]
        title = e["title"]
        url   = e["url"]
        doi   = extract_doi(url)

        pmid  = None
        note  = ""

        # Skip non-resolvable URLs
        skip_patterns = ["arxiv.org", "github.com", "terra.bio",
                         "10xgenomics.com", "illumina.com",
                         "openreview.net", "nlp.stanford.edu",
                         "jmlr.org", "proceedings.mlr.press",
                         "ieeexplore.ieee.org", "dl.acm.org"]
        skip = any(p in url for p in skip_patterns)

        if doi and not skip:
            # Verify DOI resolves
            ok = verify_doi(doi)
            time.sleep(DOI_RATE)
            if not ok:
                note = f"DOI 404: {doi}"
                issues.append(f"  ID {eid:3d} [{title[:50]}]: {note}")

            # Look up PMID
            pmid = ncbi_pmid_by_doi(doi)
            time.sleep(NCBI_RATE)

            if not pmid:
                note = f"No PMID for DOI {doi} — trying title search"
                pmid = ncbi_pmid_by_title(title)
                time.sleep(NCBI_RATE)
                if pmid:
                    note += f" → found {pmid}"
                else:
                    note += " → not found"

        elif not skip and not doi:
            # Try title search for cell.com, OUP, Genome Research, etc.
            pmid = ncbi_pmid_by_title(title)
            time.sleep(NCBI_RATE)
            note = f"No DOI extracted from URL; title search → {pmid or 'not found'}"

        if pmid:
            pmids[eid] = pmid

        status = f"PMID={pmid}" if pmid else ("SKIP" if skip else "NOT_FOUND")
        print(f"  [{eid:3d}] {status:25s} {title[:55]}")
        if note:
            issues.append(f"  ID {eid:3d} [{title[:50]}]: {note}")

    # Write outputs
    with open(OUT_PMIDS, "w") as f:
        json.dump(pmids, f, indent=2)
    print(f"\nWrote {len(pmids)} PMIDs to {OUT_PMIDS}")

    with open(OUT_ISSUES, "w") as f:
        f.write("\n".join(issues))
    print(f"Wrote issues to {OUT_ISSUES}")

    return pmids

if __name__ == "__main__":
    main()
