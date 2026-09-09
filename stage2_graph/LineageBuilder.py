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

import os
import json
import pandas as pd


def build_lineage(clustered_df, cluster_terms_df, hypothesis_edges, out_dir):
    clusters = {}

    cluster_label = {
        int(row["cluster_id"]): row.get("top_5_terms", "")
        for _, row in cluster_terms_df.iterrows()
    }

    for cid, group in clustered_df.groupby("cluster_id"):
        cid = int(cid)
        papers_sorted = group.sort_values("published")

        nodes = []
        for _, p in papers_sorted.iterrows():
            nodes.append({
                "arxiv_id": p["arxiv_id"],
                "title": p["title"],
                "year": pd.to_datetime(p["published"]).year,
                "published": p["published"],
            })

        edges = [
            {
                "source": e["source_arxiv"],
                "target": e["target_arxiv"],
                "relation": e["relation"],
                "confidence": e["confidence"],
                "evidence": (e["citation_contexts"][0] if e.get("citation_contexts") else None),
                "quant_signal": e.get("quant_signal"),
            }
            for e in hypothesis_edges
            if int(e["cluster_id"]) == cid
        ]

        # Frontier: nodes with no outgoing "disproves"/"improves" edge pointing
        # AWAY from them as the target (i.e. nobody has superseded them yet),
        # restricted to the most recent year(s) in the cluster.
        superseded = {
            e["target"] for e in edges if e["relation"] in ("disproves", "improves")
        }
        frontier_candidates = [n for n in nodes if n["arxiv_id"] not in superseded]
        frontier = sorted(frontier_candidates, key=lambda n: n["year"], reverse=True)[:5]

        clusters[cid] = {
            "cluster_id": cid,
            "label": cluster_label.get(cid, f"cluster {cid}"),
            "nodes": nodes,
            "edges": edges,
            "frontier": frontier,
        }

    lineage = {
        "clusters": clusters,
        "generated_from": {
            "n_papers": len(clustered_df),
            "n_clusters": len(clusters),
            "n_relation_edges": len(hypothesis_edges),
        },
    }

    with open(os.path.join(out_dir, "lineage_graph.json"), "w") as f:
        json.dump(lineage, f, indent=2, default=str)

    return lineage
