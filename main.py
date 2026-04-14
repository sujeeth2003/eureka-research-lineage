from Embedding import embed_paper
from Extraction import fetch_papers
from Clustering import cluster
from Cluster_title import extract_top_terms_per_cluster

import numpy as np
import umap
import pandas as pd



papers = fetch_papers("all:quant-ph", max_results=100)
embedded_papers = [embed_paper(paper['title'], paper['abstract']) for paper in papers]

