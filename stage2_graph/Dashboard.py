"""
Dashboard.py

Renders lineage_graph.json into a single self-contained HTML file:
  - left: list of clusters (research themes) with paper counts
  - right: chronological node-link graph for the selected cluster, using
    vis-network (loaded from CDN) colored by relation type, plus a
    "current frontier" panel listing papers not yet superseded.

Usage: python Dashboard.py  (reads lineage_graph.json, writes dashboard.html)
"""

import json
import os

RELATION_COLOR = {
    "extends": "#4C8BF5",
    "improves": "#2E9E5B",
    "disproves": "#D64545",
    "uses": "#9AA0A6",
}


def render_dashboard(lineage, out_path):
    clusters = lineage["clusters"]

    # Build vis-network compatible node/edge sets per cluster
    graph_data = {}
    for cid, c in clusters.items():
        nodes = [
            {
                "id": n["arxiv_id"],
                "label": (n["title"][:40] + "...") if len(n["title"]) > 40 else n["title"],
                "title": f"{n['title']} ({n['year']})",
                "year": n["year"],
            }
            for n in c["nodes"]
        ]
        edges = [
            {
                "from": e["target"],  # older paper -> points arrow toward newer
                "to": e["source"],
                "label": e["relation"],
                "color": RELATION_COLOR.get(e["relation"], "#9AA0A6"),
                "title": (e["evidence"] or "")[:200],
            }
            for e in c["edges"]
        ]
        graph_data[cid] = {"nodes": nodes, "edges": edges}

