import hdbscan
import numpy as np
import umap

#X_reduced = np.load("Eurekhalineage/X_reduced.npy")

def cluster(X_reduced):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=3, min_samples=2, metric='euclidean')
    cluster_labels = clusterer.fit_predict(X_reduced)
    return cluster_labels



'''
reducer_2d = umap.UMAP(n_neighbors=15, n_components=2, metric='cosine')
X_2d = reducer_2d.fit_transform(X_reduced)
'''



