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

