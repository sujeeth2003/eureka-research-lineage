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

