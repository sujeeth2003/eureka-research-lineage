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





'''
import matplotlib.pyplot as plt

plt.scatter(X_2d[:, 0], X_2d[:, 1], c=cluster_labels, cmap='Spectral', s=5)
plt.colorbar()
plt.title('UMAP Projection with Cluster Labels')
plt.show()


# 1. Update UMAP to output 3 dimensions
reducer_3d = umap.UMAP(n_neighbors=15, n_components=3, metric='cosine')
X_3d = reducer_3d.fit_transform(X_reduced)

# 2. Set up a 3D matplotlib plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 3. Plot points using cluster labels for color
scatter = ax.scatter(X_3d[:, 0], X_3d[:, 1], X_3d[:, 2], c=cluster_labels, cmap='Spectral', s=5)

# 4. Add visual aids
fig.colorbar(scatter, ax=ax, label='Cluster Labels')
ax.set_title('3D UMAP Projection')
plt.show()
'''