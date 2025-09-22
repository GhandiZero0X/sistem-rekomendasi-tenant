# main.py
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.neighbors import kneighbors_graph
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.metrics.pairwise import cosine_similarity
import joblib

# Load hasil preprocessing
df = pd.read_csv("tenant_preprocessed.csv")
content_features = np.load("content_features.npy")
encoder = joblib.load("encoder.pkl")
scaler = joblib.load("scaler.pkl")

# Normalisasi kolom lokasi → terminal (T1 / T2)
df["terminal"] = df["lokasi"].str.extract(r"(Terminal\s*\d)", expand=False).fillna("Unknown")
df["terminal"] = df["terminal"].str.replace("Terminal ", "T")

# Content-Based Filtering (CBF)
cosine_sim = cosine_similarity(content_features)

aktivitas_mapping = {
    "Belanja": ["Retail", "Event & Promotion", "Fashion", "Shop"],
    "Makanan": ["Food & Beverage", "Restaurant", "Cafe", "Dining"],
    "Service": ["Services", "Bank", "ATM", "Financial"]
}

def get_recommendations_by_filters(lokasi, aktivitas, top_n=5):
    if aktivitas not in aktivitas_mapping:
        return f"Aktivitas {aktivitas} tidak dikenali!"

    # Filter tenant sesuai lokasi (T1/T2) dan jenis usaha
    filtered_df = df[
        (df["terminal"].str.contains(lokasi, case=False, na=False)) &
        (df["jenis_usaha"].isin(aktivitas_mapping[aktivitas]))
    ]

    if filtered_df.empty:
        return f"Tidak ada tenant di {lokasi} untuk aktivitas {aktivitas}"

    # Ambil index pertama tenant hasil filter
    idx = filtered_df.index[0]

    # Cari tenant mirip (CBF)
    similar_indices = cosine_sim[idx].argsort()[::-1][1:top_n+1]
    return df.loc[similar_indices, ["nama_brand", "jenis_usaha", "lokasi", "rating", "total_review"]]

# Clustering (KMeans & Spectral)
X = df[["rating", "total_review"]].copy()
X["total_review"] = np.log1p(X["total_review"])  # stabilisasi

# --- KMeans ---
kmeans = KMeans(n_clusters=2, random_state=0, n_init=10)
df["cluster_kmeans"] = kmeans.fit_predict(X)

print("\n=== Distribusi Cluster (KMeans) ===")
print(df["cluster_kmeans"].value_counts())

print("\n--- Evaluasi KMeans ---")
print("Silhouette Score:", silhouette_score(X, df["cluster_kmeans"]))
print("Calinski-Harabasz Index:", calinski_harabasz_score(X, df["cluster_kmeans"]))
print("Davies-Bouldin Index:", davies_bouldin_score(X, df["cluster_kmeans"]))

# Ringkasan cluster KMeans
summary_kmeans = df.groupby("cluster_kmeans").agg({
    "rating": "mean",
    "total_review": "mean",
    "rentang_harga": lambda x: x.mode()[0]
})
print("\n=== Ringkasan Cluster (KMeans) ===")
print(summary_kmeans)

# --- Spectral Clustering ---
knn_graph = kneighbors_graph(X, n_neighbors=10, include_self=False)
adj_matrix = 0.5 * (knn_graph.toarray() + knn_graph.toarray().T)

spectral = SpectralClustering(n_clusters=2, affinity="precomputed", random_state=0, assign_labels="kmeans")
df["cluster_spectral"] = spectral.fit_predict(adj_matrix)

print("\n=== Distribusi Cluster (Spectral KNN) ===")
print(df["cluster_spectral"].value_counts())

print("\n--- Evaluasi Spectral ---")
print("Silhouette Score:", silhouette_score(X, df["cluster_spectral"]))
print("Calinski-Harabasz Index:", calinski_harabasz_score(X, df["cluster_spectral"]))
print("Davies-Bouldin Index:", davies_bouldin_score(X, df["cluster_spectral"]))

# Ringkasan cluster Spectral
summary_spectral = df.groupby("cluster_spectral").agg({
    "rating": "mean",
    "total_review": "mean",
    "rentang_harga": lambda x: x.mode()[0]
})
print("\n=== Ringkasan Cluster (Spectral) ===")
print(summary_spectral)

# Rekomendasi dari Input User
lokasi_input = input("\nMasukkan Lokasi (T1/T2): ")
aktivitas_input = input("Mau ngapain? (Belanja/Makanan/Service): ")

print("\n=== Rekomendasi Tenant (CBF) ===")
print(get_recommendations_by_filters(lokasi_input, aktivitas_input, top_n=10))

# Save hasil akhir
df.to_csv("tenant_recommendation_with_clusters.csv", index=False)
print("\n✅ File hasil akhir disimpan: tenant_recommendation_with_clusters.csv")
