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

