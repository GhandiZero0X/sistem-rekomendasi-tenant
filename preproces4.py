import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.neighbors import kneighbors_graph
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

# ======= Start Preprocessing =======
# Step 1: Load dataset
df = pd.read_csv("processed_tenant_data.csv")

# Step 2: Handle Missing Values
df["rating"] = df["rating"].fillna(df["rating"].mean())
df["total_review"] = df["total_review"].fillna(0)
df["rentang_harga"] = df["rentang_harga"].fillna("non_applicable")

# Step 3: Preprocessing for CBF
categorical_cols = ["jenis_usaha", "lokasi", "rentang_harga"]
numeric_cols = ["rating", "total_review"]

# OneHot Encode categorical
encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
cat_encoded = encoder.fit_transform(df[categorical_cols])

# Scale numeric
scaler = MinMaxScaler()
num_scaled = scaler.fit_transform(df[numeric_cols])

# Gabung fitur
content_features = np.hstack([cat_encoded, num_scaled])
# ======= End Preprocessing =======

# ======= Start Algoritma Rekomendasi & Clustering =======
# Step 4: Content-Based Filtering (Cosine Similarity)
cosine_sim = cosine_similarity(content_features)

idx = 0
similar_indices = cosine_sim[idx].argsort()[::-1][1:6]  # ambil 5 tenant mirip
print("\n=== Rekomendasi Tenant Mirip (CBF) untuk:", df.loc[idx, "nama_brand"], "===")
print(df.loc[similar_indices, ["nama_brand", "jenis_usaha", "lokasi", "rating", "total_review"]])

# Step 5: Clustering (KMeans)
X = df[["rating", "total_review"]].copy()
X["total_review"] = np.log1p(X["total_review"])  # biar lebih stabil

kmeans = KMeans(n_clusters=2, random_state=0, n_init=10)
df["cluster_kmeans"] = kmeans.fit_predict(X)

print("\n=== Distribusi Cluster (KMeans) ===")
print(df["cluster_kmeans"].value_counts())

# Evaluasi KMeans
sil_kmeans = silhouette_score(X, df["cluster_kmeans"])
ch_kmeans = calinski_harabasz_score(X, df["cluster_kmeans"])
db_kmeans = davies_bouldin_score(X, df["cluster_kmeans"])

print("\n--- Evaluasi KMeans ---")
print("Silhouette Score:", sil_kmeans)
print("Calinski-Harabasz Index:", ch_kmeans)
print("Davies-Bouldin Index:", db_kmeans)

# Step 6: Clustering (Spectral Clustering dengan KNN graph)
knn_graph = kneighbors_graph(X, n_neighbors=10, include_self=False)
adj_matrix = 0.5 * (knn_graph.toarray() + knn_graph.toarray().T)  # bikin simetris

spectral = SpectralClustering(
    n_clusters=2,
    affinity="precomputed",
    random_state=0,
    assign_labels="kmeans"
)
df["cluster_spectral"] = spectral.fit_predict(adj_matrix)

print("\n=== Distribusi Cluster (Spectral KNN) ===")
print(df["cluster_spectral"].value_counts())
# ======= End Algoritma Rekomendasi & Clustering =======

# ======= Start Evaluasi & Simpan Hasil =======
# Evaluasi Spectral
sil_spec = silhouette_score(X, df["cluster_spectral"])
ch_spec = calinski_harabasz_score(X, df["cluster_spectral"])
db_spec = davies_bouldin_score(X, df["cluster_spectral"])

print("\n--- Evaluasi Spectral ---")
print("Silhouette Score:", sil_spec)
print("Calinski-Harabasz Index:", ch_spec)
print("Davies-Bouldin Index:", db_spec)

# Step 7: Ringkasan Cluster
summary_kmeans = df.groupby("cluster_kmeans").agg({
    "rating": "mean",
    "total_review": "mean",
    "rentang_harga": lambda x: x.mode()[0]
})

print("\n=== Ringkasan per Cluster (KMeans) ===")
print(summary_kmeans)

# Tambahkan nama cluster (contoh: bisa disesuaikan)
def label_cluster(row):
    if row["cluster_kmeans"] == 0:
        return "Tenant Baru / Review Sedikit"
    elif row["cluster_kmeans"] == 1:
        return "Tenant Populer"
    else:
        return "Tenant Best Seller"

df["cluster_kmeans_label"] = df.apply(label_cluster, axis=1)

print("\n=== Contoh Label Cluster (KMeans) ===")
print(df[["nama_brand", "rating", "total_review", "cluster_kmeans", "cluster_kmeans_label"]].head())

# Step 8: Save hasil
df.to_csv("tenant_recommendation_with_clusters.csv", index=False)
print("\nFile hasil disimpan: tenant_recommendation_with_clusters.csv")
# ======= End Evaluasi & Simpan Hasil =======