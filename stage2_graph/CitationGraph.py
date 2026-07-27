"""
CitationGraph.py

Builds the citation graph restricted to your own corpus (the papers you
fetched and clustered). For each paper:
  1. Map arXiv ID -> OpenAlex work ID (title/arXiv match)
  2. Pull referenced_works from OpenAlex
  3. Keep only edges where the cited paper is ALSO in your corpus
     (that's your "candidate predecessor" edge)
  4. Download the source PDF and extract the sentence(s) around the
     in-text citation marker for that specific reference, so later
     stages have real textual evidence, not just "A cites B".

Output files (written to OUT_DIR):
  - arxiv_to_openalex.json
  - candidate_edges.csv        (source cites target, same cluster, target earlier)
  - citation_contexts.json     (edge + surrounding sentence(s) as evidence)
"""

import os
import re
import time
import json
import requests
import pandas as pd

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None

OPENALEX_URL = "https://api.openalex.org/works"


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def ensure_dirs(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "papers"), exist_ok=True)


# ---------------------------------------------------------------------------
# Step 1: download PDFs
# ---------------------------------------------------------------------------

def download_pdf(paper, out_dir):
    arxiv_id = paper["arxiv_id"].replace("/", "_")
    path = os.path.join(out_dir, "papers", f"{arxiv_id}.pdf")

    if os.path.exists(path):
        return path

    pdf_url = paper.get("pdf_url")
    if not pdf_url:
        return None

    try:
        resp = requests.get(pdf_url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        with open(path, "wb") as f:
            f.write(resp.content)
        return path
    except Exception as e:
        print(f"  [pdf] failed {arxiv_id}: {e}")
        return None


def download_all_pdfs(papers, out_dir, sleep=1.0):
    for paper in papers:
        paper["pdf_path"] = download_pdf(paper, out_dir)
        time.sleep(sleep)
    return papers


# ---------------------------------------------------------------------------
# Step 2: extract raw text from PDF
# ---------------------------------------------------------------------------

def extract_pdf_text(pdf_path):
    if not pdf_path or fitz is None:
        return ""
    try:
        doc = fitz.open(pdf_path)
        pages = [page.get_text("text") for page in doc]
        doc.close()
        return "\n".join(pages)
    except Exception as e:
        print(f"  [extract] failed {pdf_path}: {e}")
        return ""


# ---------------------------------------------------------------------------
# Step 3: arXiv -> OpenAlex mapping
# ---------------------------------------------------------------------------

def find_openalex_work(paper):
    params = {"search": paper["title"], "per-page": 10}
    try:
        resp = requests.get(OPENALEX_URL, params=params, timeout=30)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception as e:
        print(f"  [openalex] search failed {paper['arxiv_id']}: {e}")
        return None

    clean_arxiv = paper["arxiv_id"].split("v")[0]

    for work in results:
        arxiv_url = work.get("ids", {}).get("arxiv")
        if arxiv_url and clean_arxiv in arxiv_url:
            return work

    if fuzz is None:
        return None

    best_work, best_score = None, 0
    for work in results:
        score = fuzz.token_set_ratio(paper["title"].lower(), work.get("title", "").lower())
        if score > best_score:
            best_score, best_work = score, work

    return best_work if best_score >= 90 else None


def build_openalex_mapping(papers, out_dir, sleep=0.2):
    arxiv_to_openalex = {}
    for paper in papers:
        work = find_openalex_work(paper)
        if work:
            arxiv_to_openalex[paper["arxiv_id"]] = work["id"]
            print(f"  {paper['arxiv_id']} -> {work['id']}")
        else:
            print(f"  {paper['arxiv_id']} -> NOT FOUND")
        time.sleep(sleep)

    with open(os.path.join(out_dir, "arxiv_to_openalex.json"), "w") as f:
        json.dump(arxiv_to_openalex, f, indent=2)

    return arxiv_to_openalex


# ---------------------------------------------------------------------------
# Step 4: in-corpus candidate edges (source cites target, same cluster, target earlier)
# ---------------------------------------------------------------------------

def get_referenced_works(openalex_id):
    try:
        resp = requests.get(openalex_id, timeout=30)
        resp.raise_for_status()
        return resp.json().get("referenced_works", [])
    except Exception as e:
        print(f"  [refs] failed {openalex_id}: {e}")
        return []


def get_year(paper):
    return pd.to_datetime(paper["published"]).year


def build_candidate_edges(papers, arxiv_to_openalex, out_dir, sleep=0.2):
    openalex_to_arxiv = {v: k for k, v in arxiv_to_openalex.items()}
    paper_by_arxiv = {p["arxiv_id"]: p for p in papers}

    edges = []
    for source in papers:
        source_openalex = arxiv_to_openalex.get(source["arxiv_id"])
        if not source_openalex:
            continue

        for ref in get_referenced_works(source_openalex):
            target_arxiv = openalex_to_arxiv.get(ref)
            if not target_arxiv or target_arxiv == source["arxiv_id"]:
                continue

            target = paper_by_arxiv[target_arxiv]
            source_year, target_year = get_year(source), get_year(target)
            same_cluster = source["cluster_id"] == target["cluster_id"]

            if same_cluster and target_year <= source_year:
                edges.append({
                    "source_arxiv": source["arxiv_id"],
                    "target_arxiv": target_arxiv,
                    "source_title": source["title"],
                    "target_title": target["title"],
                    "source_year": source_year,
                    "target_year": target_year,
                    "cluster_id": int(source["cluster_id"]),
                })
        time.sleep(sleep)

    df = pd.DataFrame(edges)
    df.to_csv(os.path.join(out_dir, "candidate_edges.csv"), index=False)
    return df


# ---------------------------------------------------------------------------
# Step 5: locate the citation marker + surrounding sentence(s) as evidence
# ---------------------------------------------------------------------------

REF_HEADER_PATTERNS = [
    r"\nReferences\s*\n", r"\nREFERENCES\s*\n",
    r"\nBibliography\s*\n", r"\nBIBLIOGRAPHY\s*\n",
]


def get_reference_section(text):
    matches = []
    for pattern in REF_HEADER_PATTERNS:
        matches.extend(list(re.finditer(pattern, text)))
    if not matches:
        return ""
    start = max(m.start() for m in matches)
    return text[start:]


