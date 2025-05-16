import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from pathlib import Path

plot_dir = Path('eda_plots')
plot_dir.mkdir(exist_ok=True)

def plot_tsne(logs, name, n_clusters=5, max_samples=2000, max_features=200, svd_components=50):
    # Subsample for speed/memory
    if len(logs) > max_samples:
        idx = np.random.choice(len(logs), max_samples, replace=False)
        logs_sample = [logs[i] for i in idx]
        print(f'Subsampling {max_samples} entries from {len(logs)} for {name}.')
    else:
        logs_sample = logs

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')
    X = vectorizer.fit_transform(logs_sample)

    # SVD for further reduction
    if X.shape[1] > svd_components:
        svd = TruncatedSVD(n_components=svd_components, random_state=42)
        X_reduced = svd.fit_transform(X)
    else:
        X_reduced = X.toarray()

    # KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_reduced)

    # t-SNE embedding
    tsne = TSNE(n_components=2, random_state=42, init='pca', learning_rate='auto')
    X_embedded = tsne.fit_transform(X_reduced)

    # Plot
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(X_embedded[:, 0], X_embedded[:, 1], c=labels, cmap='tab10', alpha=0.6)
    plt.title(f'{name} Log Entry Clusters (t-SNE Projection)')
    plt.xlabel('t-SNE 1')
    plt.ylabel('t-SNE 2')
    plt.tight_layout()
    plt.savefig(plot_dir / f'{name.lower()}_tsne_clusters.png')
    plt.show()

# Example usage (uncomment and provide your log lists):
# plot_tsne(hdfs_logs, 'HDFS')
# plot_tsne(apache_logs, 'APACHE')
# plot_tsne(bgl_logs, 'BGL')
# plot_tsne(healthapp_logs, 'HEALTHAPP')
# plot_tsne(hpc_logs, 'HPC')
# plot_tsne(linux_logs, 'LINUX')
# plot_tsne(mac_logs, 'MAC') 