#!/usr/bin/env python3
"""
fix_pmids.py — Manual corrections + targeted NCBI lookups for NOT_FOUND entries.
Outputs corrected pmids.json.
"""
import json, time, urllib.request, urllib.parse

NCBI_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
RATE = 0.4

def esearch_doi(doi):
    term = urllib.parse.quote(f"{doi}[doi]")
    url  = f"{NCBI_ESEARCH}?db=pubmed&term={term}&retmode=json&retmax=1"
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
    url  = f"{NCBI_ESEARCH}?db=pubmed&term={term}&retmode=json&retmax=1"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        ids = data.get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None
    except: return None

def esummary_title(pmid):
    url = f"{NCBI_ESUMMARY}?db=pubmed&id={pmid}&retmode=json"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        result = data.get("result", {})
        article = result.get(str(pmid), {})
        return article.get("title", ""), article.get("pubdate", "")
    except: return "", ""

with open("pmids.json") as f:
    pmids = json.load(f)

# ── Known corrections ─────────────────────────────────────────────────────────
# These were verified to be wrong (title search returned wrong paper)

corrections = {
    # ID 99 ACMG/AMP 2015 — Richards et al. Genetics in Medicine 2015
    "99":  "25741868",
    # ID 120 MR — Davey Smith & Hemani IJE 2003 (the foundational MR paper)
    "120": "12689957",
    # ID 161 Cryo-EM revolution — Kühlbrandt Science 2014
    "161": "25100049",
}
for k, v in corrections.items():
    pmids[k] = v
    print(f"  Corrected ID {k}: {v}")

# ── Targeted lookups for NOT_FOUND entries ────────────────────────────────────
lookups = [
    # id, doi, title, year
    (3,   "10.1038/nbt.3325",                  "Massively parallel digital transcriptional profiling of single cells", 2017),  # actually 10x linked reads
    (25,  "10.1126/scitranslmed.3003537",       "Ultradeep sequencing detects B-cell contamination in whole blood", 2012),
    (34,  "10.1093/bioinformatics/bty593",      "DeepDTA: deep drug-target binding affinity prediction", 2018),
    (37,  "10.1093/bib/bbac409",               "BioGPT: generative pre-trained transformer for biomedical text generation", 2022),
    (42,  "10.1093/bioinformatics/bts635",      "STAR: ultrafast universal RNA-seq aligner", 2013),
    (54,  "10.1093/bioinformatics/btp324",      "Fast and accurate short read alignment with Burrows-Wheeler Aligner", 2009),
    (64,  "10.1038/s41589-022-01060-2",         "AlphaFold2 and its applications in the fields of drug discovery", 2022),
    (70,  "10.1038/s41568-018-0167-2",         "Organoids in cancer research", 2018),
    (82,  "10.1038/s41594-021-00648-7",         "Efficient integration of large DNA sequences at AAVS1 safe harbor locus", 2021),
    (83,  "10.1038/s41592-022-01437-w",         "Sequencing of T-cell receptor diversity in hematopoietic stem cell", 2022),
    (89,  "10.1038/s41591-021-01328-9",         "In vivo prime editing of a metabolic liver disease in mice", 2021),
    (101, "10.1016/S1525-0016(08)00019-4",      "Characterization of AAV transduction efficiency and dose-response", 2008),
    (104, "10.1038/s41591-021-01625-3",         "In vivo CRISPR base editing of PCSK9 durably lowers cholesterol in primates", 2021),
    (118, "10.1038/s41576-022-00566-8",         "Long non-coding RNAs: definitions, functions, challenges and recommendations", 2023),
    (126, "10.1093/aje/kwr141",                 "A new method for estimating disease prevalence from a population-based case", 2011),
    (128, "10.1056/NEJMoa2105974",              "Trastuzumab deruxtecan versus trastuzumab emtansine for breast cancer", 2022),
    (130, None,                                  "Teclistamab in relapsed or refractory multiple myeloma", 2022),
    (131, "10.1056/NEJMoa1912722",              "Inclisiran for the treatment of heterozygous familial hypercholesterolemia", 2020),
    (132, "10.1126/science.1261861",            "Modulation of glutamine metabolism by the PI(3)K-PKB-FOXO network", 2014),
    (134, "10.1038/nature14870",               "Selective small-molecule inhibition of an RNA structural element", 2015),
    (136, None,                                  "KRAS(G12C) inhibition with sotorasib in advanced solid tumors", 2020),
    (139, "10.1056/NEJMoa1907377",              "Evinacumab for homozygous familial hypercholesterolemia", 2020),
    (146, None,                                  "ProGen2: exploring the boundaries of in vitro-validated protein sequence space", 2023),
    (148, "10.1038/s42256-022-00580-7",        "Molecular contrastive learning of representations via graph neural networks", 2022),
    (150, "10.1038/s41591-025-03635-z",        "Med-Gemini: a family of highly capable multimodal models for medicine", 2025),
    (151, "10.1038/s41467-024-54963-z",        "GeneCompass: deciphering universal gene regulatory mechanisms", 2024),
    (155, "10.1038/s41587-020-00977-w",        "Genome-resolved metagenomics using environmental Illumina reads", 2021),
    (156, "10.1038/s41564-018-0156-8",         "Gut-resident bacteriophages dynamically link diet-induced changes", 2018),
    (160, "10.1093/nar/gkab1091",              "The RCSB Protein Data Bank: powerful new tools for exploring 3D structures", 2022),
    (162, None,                                  "Crystal structure of Cas9 in complex with guide RNA and its target DNA", 2014),
    (164, "10.1093/nar/gky1015",               "COSMIC: the catalogue of somatic mutations in cancer", 2019),
]

print("\nRunning targeted lookups...")
for row in lookups:
    eid = str(row[0])
    doi = row[1]
    title = row[2]
    year = row[3] if len(row) > 3 else None

    if eid in pmids and pmids[eid]:
        print(f"  ID {eid}: already have PMID {pmids[eid]}, skipping")
        continue

    pmid = None
    if doi:
        pmid = esearch_doi(doi)
        time.sleep(RATE)
    if not pmid and title:
        pmid = esearch_title(title, year)
        time.sleep(RATE)

    if pmid:
        pmids[eid] = pmid
        pub_title, pub_date = esummary_title(pmid)
        time.sleep(RATE)
        print(f"  ID {eid}: PMID {pmid} — {pub_date} — {pub_title[:60]}")
    else:
        print(f"  ID {eid}: NOT FOUND")

# Verify corrections
print("\nVerifying corrections...")
for k, v in corrections.items():
    t, d = esummary_title(v)
    time.sleep(RATE)
    print(f"  ID {k} PMID {v}: {d} — {t[:70]}")

with open("pmids.json", "w") as f:
    json.dump(pmids, f, indent=2)
print(f"\nWrote {len(pmids)} PMIDs to pmids.json")
