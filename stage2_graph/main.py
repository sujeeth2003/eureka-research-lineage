"""
main.py - EurekaLineage end-to-end pipeline

    fetch_papers
        -> SPECTER2 embeddings
        -> UMAP + HDBSCAN clustering
        -> cluster top terms (theme labels)
        -> citation graph (OpenAlex + PDFs, restricted to your corpus)
        -> relation classification (extends / improves / disproves / uses)
        -> lineage graph (chronological, per cluster, with a "frontier")
        -> dashboard.html

Run:  python main.py
Tune the constants below before running.
"""

import os
import numpy as np
import pandas as pd
import umap

from Embedding import embed_paper
from Extraction import fetch_papers
from Clustering import cluster
from Cluster_title import extract_top_terms_per_cluster
from CitationGraph import build_citation_graph
from HypothesisExtraction import annotate_edges
from LineageBuilder import build_lineage
from Dashboard import render_dashboard

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SEARCH_QUERY = "all:quant-ph"     # arXiv search query
MAX_RESULTS = 100                 # corpus size
OUT_DIR = "eurekalineage_out"     # all outputs land here
DOWNLOAD_PDFS = True              # False = skip citation-context evidence (faster, less signal)
USE_LLM_FOR_AMBIGUOUS = False     # True = call Claude for low-confidence edges (needs ANTHROPIC_API_KEY)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1. Fetch -------------------------------------------------------------
    print(f"[1/7] Fetching papers: {SEARCH_QUERY} (n={MAX_RESULTS})")
    papers = fetch_papers(SEARCH_QUERY, max_results=MAX_RESULTS)
    print(f"  got {len(papers)} papers")

    # 2. Embed ---------------------------------------------------------------
    print("[2/7] Embedding papers with SPECTER2...")
    embedded = [embed_paper(p["title"], p["abstract"]) for p in papers]
    X = np.vstack(embedded)
    if X.shape[0] < 3:
        raise ValueError("Need at least 3 papers to cluster")

