from Embedding import embed_paper
from Extraction import fetch_papers
from Clustering import cluster
from Cluster_title import extract_top_terms_per_cluster

import numpy as np
import umap
import pandas as pd



papers = fetch_papers("all:quant-ph", max_results=100)
embedded_papers = [embed_paper(paper['title'], paper['abstract']) for paper in papers]

X = np.vstack(embedded_papers)
if X.shape[0] < 3:
	raise ValueError("UMAP requires at least 3 embedded papers")

n_neighbors = min(5, X.shape[0] - 1)
n_components = min(10, X.shape[0] - 2)
reducer = umap.UMAP(
	n_neighbors=n_neighbors,
	n_components=n_components,
	metric='cosine',
	random_state=42,
)
X_reduced = reducer.fit_transform(X)

#np.save("Eurekhalineage/X_reduced.npy", X_reduced)

cluster_labels = cluster(X_reduced)

result = [[item, cid] for item, cid in zip(papers, cluster_labels)]

flattened_result = []

for paper, cluster_id in result:
	row = paper.copy()
	row['cluster_id'] = cluster_id
	flattened_result.append(row)

#np.save("Eurekhalineage/cluster_labels.npy", cluster_labels)

df = pd.DataFrame(flattened_result)
df.to_csv("Eurekhalineage/clustered_papers.csv", index=False)


export_data = extract_top_terms_per_cluster(df)
pd.DataFrame(export_data).to_csv("Eurekhalineage/cluster_top_terms.csv", index=False)

paper_by_arxiv = {
    row["arxiv_id"]: row
    for _, row in df.iterrows()
}