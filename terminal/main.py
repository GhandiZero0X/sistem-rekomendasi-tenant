import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.neighbors import kneighbors_graph
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import random

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
    "Makanan": ["Food & Beverage", "Event & Promotion", "Restaurant", "Cafe", "Dining", "Lounge"],
    "Service": ["Services", "Bank", "ATM", "Financial"]
}

def get_recommendations_by_filters(lokasi=None, aktivitas=None, rentang_harga=None, top_n=10):
    # Minimal 1 input harus ada
    if not lokasi and not aktivitas and not rentang_harga:
        return None  # biar balik ke input ulang

    filtered_df = df.copy()

    # Filter lokasi
    if lokasi:
        filtered_df = filtered_df[filtered_df["terminal"].str.contains(lokasi, case=False, na=False)]

    # Filter aktivitas
    if aktivitas:
        if aktivitas not in aktivitas_mapping:
            return f"Aktivitas {aktivitas} tidak dikenali!"
        filtered_df = filtered_df[filtered_df["jenis_usaha"].isin(aktivitas_mapping[aktivitas])]

    # Filter rentang harga
    if rentang_harga:
        sub_df = filtered_df[filtered_df["rentang_harga"].str.lower() == rentang_harga.lower()]
        if not sub_df.empty:
            filtered_df = sub_df  # hanya ganti kalau ada hasil

    if filtered_df.empty:
        return "⚠️ Tidak ada tenant sesuai filter yang diberikan."

    # Pilih tenant anchor dinamis (berdasarkan popularitas review)
    weights = filtered_df["total_review"] + 1
    idx = random.choices(filtered_df.index.tolist(), weights=weights, k=1)[0]

    # Cari tenant mirip dengan CBF
    similar_indices = cosine_sim[idx].argsort()[::-1][1:top_n+1]
    return df.loc[similar_indices, ["nama_brand", "jenis_usaha", "lokasi",
                                    "rating", "total_review", "rentang_harga"]]

# ================= CLUSTERING ==================
X = df[["rating", "total_review"]].copy()
X["total_review"] = np.log1p(X["total_review"])  # stabilisasi distribusi

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

# Tampilkan top 10 tiap cluster KMeans
for cluster_id in sorted(df["cluster_kmeans"].unique()):
    print(f"\n--- Top 10 Tenant Cluster {cluster_id} (KMeans) ---")
    top_kmeans = df[df["cluster_kmeans"] == cluster_id].sort_values(by="total_review", ascending=False).head(10)
    print(top_kmeans[["nama_brand", "jenis_usaha", "lokasi", "rating", "total_review", "rentang_harga"]])

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

# Tampilkan top 10 tiap cluster Spectral
for cluster_id in sorted(df["cluster_spectral"].unique()):
    print(f"\n--- Top 10 Tenant Cluster {cluster_id} (Spectral) ---")
    top_spectral = df[df["cluster_spectral"] == cluster_id].sort_values(by="total_review", ascending=False).head(10)
    print(top_spectral[["nama_brand", "jenis_usaha", "lokasi", "rating", "total_review", "rentang_harga"]])

# ================= REKOMENDASI ==================
while True:
    lokasi_input = input("\nMasukkan Lokasi (T1/T2) [Opsional]: ").strip()
    aktivitas_input = input("Mau ngapain? (Belanja/Makanan/Service) [Opsional]: ").strip()
    harga_input = input("Rentang harga (murah/sedang/mahal) [Opsional]: ").strip()

    lokasi_input = lokasi_input if lokasi_input else None
    aktivitas_input = aktivitas_input if aktivitas_input else None
    harga_input = harga_input if harga_input else None

    hasil = get_recommendations_by_filters(lokasi_input, aktivitas_input, rentang_harga=harga_input, top_n=15)

    if hasil is None:
        print("\n⚠️ Minimal isi salah satu filter (Terminal / Aktivitas / Rentang Harga). Coba lagi!\n")
        continue
    else:
        print("\n=== Rekomendasi Tenant (CBF) ===")
        print(hasil)
        break

# Save hasil akhir
df.to_csv("tenant_recommendation_with_clusters.csv", index=False)
print("\n✅ File hasil akhir disimpan: tenant_recommendation_with_clusters.csv")
