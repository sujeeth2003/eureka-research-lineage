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

