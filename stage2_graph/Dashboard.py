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

    cluster_list_html = "\n".join(
        f'<li class="cluster-item" data-cid="{cid}" onclick="selectCluster({cid})">'
        f'<strong>Cluster {cid}</strong><br><span class="terms">{c["label"]}</span>'
        f'<br><span class="count">{len(c["nodes"])} papers</span></li>'
        for cid, c in clusters.items()
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>EurekaLineage</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.9/vis-network.min.js"></script>
<style>
  body {{ font-family: -apple-system, Segoe UI, sans-serif; margin: 0; display: flex; height: 100vh; background: #0f1115; color: #e8e8e8; }}
  #sidebar {{ width: 280px; overflow-y: auto; border-right: 1px solid #2a2d34; padding: 12px; box-sizing: border-box; }}
  #main {{ flex: 1; display: flex; flex-direction: column; }}
  #graph {{ flex: 1; }}
  #frontier {{ height: 160px; border-top: 1px solid #2a2d34; padding: 10px 16px; overflow-y: auto; }}
  h1 {{ font-size: 16px; padding: 12px 16px; margin: 0; border-bottom: 1px solid #2a2d34; }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  .cluster-item {{ padding: 10px; margin-bottom: 6px; border-radius: 8px; cursor: pointer; background: #1a1d24; }}
  .cluster-item:hover {{ background: #23272f; }}
  .cluster-item.active {{ background: #2d3f6b; }}
  .terms {{ font-size: 11px; color: #9aa0a6; }}
  .count {{ font-size: 11px; color: #6a90ff; }}
  .legend {{ display: flex; gap: 14px; padding: 8px 16px; font-size: 12px; border-bottom: 1px solid #2a2d34; }}
  .swatch {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }}
  .frontier-item {{ font-size: 13px; padding: 4px 0; border-bottom: 1px solid #23272f; }}
</style>
</head>
<body>

<div id="sidebar">
  <h1 style="border:none;padding:0 0 10px 0;">EurekaLineage clusters</h1>
  <ul>{cluster_list_html}</ul>
</div>

<div id="main">
  <div class="legend">
    <span><span class="swatch" style="background:#4C8BF5"></span>extends</span>
    <span><span class="swatch" style="background:#2E9E5B"></span>improves</span>
    <span><span class="swatch" style="background:#D64545"></span>disproves</span>
    <span><span class="swatch" style="background:#9AA0A6"></span>uses</span>
  </div>
  <div id="graph"></div>
  <div id="frontier">
    <strong>Current frontier (not yet superseded):</strong>
    <div id="frontier-list"></div>
  </div>
</div>

<script>
const graphData = {json.dumps(graph_data)};
const clusters = {json.dumps({cid: c["frontier"] for cid, c in clusters.items()})};

let network = null;

function selectCluster(cid) {{
  document.querySelectorAll('.cluster-item').forEach(el => el.classList.remove('active'));
  document.querySelector(`[data-cid="${{cid}}"]`).classList.add('active');

  const data = graphData[cid];
  const nodes = new vis.DataSet(data.nodes.map(n => ({{...n, level: n.year}})));
  const edges = new vis.DataSet(data.edges.map((e, i) => ({{...e, id: i, arrows: 'to', font: {{color:'#ccc', size:10}}}})));

