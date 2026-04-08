#!/usr/bin/env python3
"""
build_papers.py — Build papers[] arrays for multi-paper entries.
Looks up PMIDs via NCBI esearch, then injects papers: [...] into index.html.
"""
import json, re, time, urllib.request, urllib.parse

HTML = "../index.html"
RATE = 0.4

def esearch_doi(doi):
    term = urllib.parse.quote(f"{doi}[doi]")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={term}&retmode=json&retmax=1"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        ids = data.get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None
    except: return None

def esearch_title(title, year=None):
    q = f'"{title[:70]}"[title]'
    if year: q += f" AND {year}[pdat]"
    term = urllib.parse.quote(q)
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={term}&retmode=json&retmax=1"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        ids = data.get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None
    except: return None

def esummary(pmid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        art = data.get("result", {}).get(str(pmid), {})
        return art.get("title", ""), art.get("pubdate", "")
    except: return "", ""

# ── Paper definitions for each entry ─────────────────────────────────────────
# Format: {entry_id: [{"label", "url", "doi" or "title"+"year", "pmid"(optional)}]}
# "pmid" can be pre-filled if known; otherwise will be looked up via doi/title.

ENTRIES = {
    29: [  # DOGMA-seq / TEA-seq
        {"label": "Mimitou 2021 (DOGMA-seq)", "url": "https://www.nature.com/articles/s41587-021-00927-2", "pmid": "34083792"},
        {"label": "Swanson 2021 (TEA-seq)",   "url": "https://elifesciences.org/articles/63632",            "doi": "10.7554/eLife.63632"},
    ],
    33: [  # CUT&RUN / CUT&TAG
        {"label": "Skene 2017 (CUT&RUN)",     "url": "https://elifesciences.org/articles/21856",            "doi": "10.7554/eLife.21856"},
        {"label": "Kaya-Okur 2019 (CUT&TAG)", "url": "https://www.nature.com/articles/s41467-019-09982-5", "doi": "10.1038/s41467-019-09982-5"},
    ],
    44: [  # Snakemake / Nextflow
        {"label": "Köster 2012 (Snakemake)",    "url": "https://academic.oup.com/bioinformatics/article/28/19/2520/290322", "doi": "10.1093/bioinformatics/bts480"},
        {"label": "Di Tommaso 2017 (Nextflow)", "url": "https://www.nature.com/articles/nbt.3820",                         "pmid": "28398311"},
    ],
    46: [  # GATK / DeepVariant
        {"label": "McKenna 2010 (GATK)",       "url": "https://genome.cshlp.org/content/20/9/1297",  "doi": "10.1101/gr.107524.110"},
        {"label": "Poplin 2018 (DeepVariant)", "url": "https://www.nature.com/articles/nbt.4235",    "pmid": "30247488"},
    ],
    52: [  # GeCKO / Brunello
        {"label": "Shalem 2014 (GeCKO)",    "url": "https://www.science.org/doi/10.1126/science.1247005", "doi": "10.1126/science.1247005"},
        {"label": "Doench 2016 (Brunello)", "url": "https://www.nature.com/articles/nbt.3437",            "pmid": "26780180"},
    ],
    59: [  # Salmon / kallisto
        {"label": "Patro 2017 (Salmon)",   "url": "https://www.nature.com/articles/nmeth.4197", "pmid": "28263959"},
        {"label": "Bray 2016 (kallisto)",  "url": "https://www.nature.com/articles/nbt.3519",  "doi": "10.1038/nbt.3519"},
    ],
    60: [  # CIBERSORT / CIBERSORTx
        {"label": "Newman 2015 (CIBERSORT)",   "url": "https://www.nature.com/articles/nmeth.3337",      "doi": "10.1038/nmeth.3337"},
        {"label": "Newman 2019 (CIBERSORTx)", "url": "https://www.nature.com/articles/s41587-019-0114-2", "pmid": "31061481"},
    ],
    62: [  # CVAE / JTVAE
        {"label": "Gómez-Bombarelli 2018 (CVAE)", "url": "https://pubs.acs.org/doi/10.1021/acscentsci.7b00572", "pmid": "29532027"},
        {"label": "Jin 2018 (JTVAE)",              "url": "https://arxiv.org/abs/1802.04364",                   "pmid": None},  # ICML, no PMID
    ],
    124: [  # Perturb-seq causal GRN
        {"label": "Replogle 2022 (genome-wide)",   "url": "https://www.cell.com/cell/fulltext/S0092-8674(22)00597-9", "pmid": "35688146"},
        {"label": "Norman 2019 (combinatorial)",   "url": "https://www.science.org/doi/10.1126/science.aax4438",      "doi": "10.1126/science.aax4438"},
    ],
    168: [  # CRISPR off-target landscape
        {"label": "Tsai 2015 (GUIDE-seq)",     "url": "https://www.nature.com/articles/nbt.3117",      "pmid": "25513782"},
        {"label": "Tsai 2017 (CIRCLE-seq)",    "url": "https://www.nature.com/articles/nmeth.4278",    "doi": "10.1038/nmeth.4278"},
        {"label": "Kim 2015 (Digenome-seq)",   "url": "https://www.nature.com/articles/nmeth.3284",    "doi": "10.1038/nmeth.3284"},
        {"label": "Lazzarotto 2020 (CHANGE-seq)", "url": "https://www.nature.com/articles/s41587-020-0555-7", "doi": "10.1038/s41587-020-0555-7"},
    ],
}

# ── Resolve PMIDs ─────────────────────────────────────────────────────────────
print("Resolving PMIDs...")
for eid, papers in ENTRIES.items():
    for p in papers:
        if p.get("pmid"):
            t, d = esummary(p["pmid"])
            print(f"  [{eid}] {p['label']}: PMID {p['pmid']} — {t[:60]}")
            time.sleep(RATE)
            continue
        doi = p.get("doi")
        title = p.get("title")
        year = p.get("year")
        pmid = None
        if doi:
            pmid = esearch_doi(doi)
            time.sleep(RATE)
        if not pmid and title:
            pmid = esearch_title(title, year)
            time.sleep(RATE)
        if pmid:
            p["pmid"] = pmid
            t, d = esummary(pmid)
            time.sleep(RATE)
            print(f"  [{eid}] {p['label']}: PMID {pmid} — {t[:60]}")
        else:
            p["pmid"] = None
            print(f"  [{eid}] {p['label']}: NOT FOUND")

# ── Read HTML ─────────────────────────────────────────────────────────────────
with open(HTML, encoding="utf-8") as f:
    html = f.read()

# ── Inject papers arrays ──────────────────────────────────────────────────────
count = 0
for eid, papers in ENTRIES.items():
    # Find the entry block
    id_pattern = re.compile(rf'\bid:\s*{eid}\b')
    id_match = id_pattern.search(html)
    if not id_match:
        print(f"  ID {eid}: not found in HTML")
        continue

    start = id_match.start()
    next_entry = re.search(r'\n  \{', html[start + 10:])
    end = start + 10 + next_entry.start() if next_entry else len(html)
    block = html[start:end]

    # Skip if already has papers array
    if 'papers:' in block:
        print(f"  ID {eid}: papers array already exists, skipping")
        continue

    # Build papers array JS
    paper_items = []
    for p in papers:
        url = p["url"]
        pmid = p.get("pmid")
        label = p["label"]
        if pmid:
            paper_items.append(f'      {{ url: "{url}", pmid: "{pmid}", label: "{label}" }}')
        else:
            paper_items.append(f'      {{ url: "{url}", label: "{label}" }}')
    papers_js = "    papers: [\n" + ",\n".join(paper_items) + ",\n    ],\n"

    # Insert papers array before closing }
    # Find the closing }, of this entry
    close_match = re.search(r'\n  \},', html[start:end])
    if not close_match:
        print(f"  ID {eid}: closing brace not found")
        continue

    insert_pos = start + close_match.start() + 1  # after \n
    html = html[:insert_pos] + papers_js + html[insert_pos:]
    count += 1
    print(f"  ID {eid}: injected {len(papers)}-paper array")

print(f"\nInjected {count} papers arrays")
with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)
print("Wrote index.html")
