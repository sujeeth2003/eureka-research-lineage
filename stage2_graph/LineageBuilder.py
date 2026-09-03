"""
LineageBuilder.py

Assembles the final EurekaLineage graph:

  - Papers grouped by cluster (fundamental research theme, e.g. "wave-particle
    duality", from Cluster_title.py's top TF-IDF terms)
  - Within each cluster, papers ordered by year
  - Edges between papers labeled with a relation (extends/improves/disproves/uses),
    confidence, and evidence snippet
  - A "frontier" per cluster: the most recent paper(s) not yet superseded by
    a later `disproves` or `improves` edge -> "where the field currently is"

Output: lineage_graph.json, structured for the dashboard.
"""

