# Eureka - Research Lineage

Maps how research ideas flow between papers, authors and companies.

## Pipeline
`Extraction.py` (papers) -> `Embedding.py` -> `Clustering.py` / `Cluster_title.py` (topic clusters, `cluster_top_terms.csv`) -> `Citations.py` (citation edges via Semantic Scholar / OpenAlex) -> `main.py`.

The schema is 3NF SQLite: papers, authors, mentors, company adoption. Lineage is a self-referential relation queried with multi-table joins and self-joins. Scaling to a graph store or PostgreSQL is outlined, not built.

