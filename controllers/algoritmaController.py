import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.neighbors import kneighbors_graph
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")

# Load hasil preprocessing
df = pd.read_csv(os.path.join(DATA_DIR, "tenant_preprocessed.csv"))
content_features = np.load(os.path.join(DATA_DIR, "content_features.npy"))
encoder = joblib.load(os.path.join(DATA_DIR, "encoder.pkl"))
scaler = joblib.load(os.path.join(DATA_DIR, "scaler.pkl"))

# Normalisasi lokasi → terminal
df["terminal"] = df["lokasi"].str.extract(r"(Terminal\s*\d)", expand=False).fillna("Unknown")
df["terminal"] = df["terminal"].str.replace("Terminal ", "T")

# Content-Based Filtering
cosine_sim = cosine_similarity(content_features)

aktivitas_mapping = {
    "Belanja": ["Retail", "Event & Promotion", "Fashion", "Shop"],
    "Makanan": ["Food & Beverage", "Event & Promotion", "Restaurant", "Cafe", "Dining", "Lounge"],
    "Service": ["Services", "Bank", "ATM", "Financial"]
}

def get_recommendations_by_filters(lokasi=None, aktivitas=None, rentang_harga=None, top_n=10):
    if not lokasi and not aktivitas and not rentang_harga:
        return None

    filtered_df = df.copy()
    if lokasi:
        filtered_df = filtered_df[filtered_df["terminal"].str.contains(lokasi, case=False, na=False)]
    if aktivitas:
        if aktivitas not in aktivitas_mapping:
            return f"Aktivitas {aktivitas} tidak dikenali!"
        filtered_df = filtered_df[filtered_df["jenis_usaha"].isin(aktivitas_mapping[aktivitas])]
    if rentang_harga:
        sub_df = filtered_df[filtered_df["rentang_harga"].str.lower() == rentang_harga.lower()]
        if not sub_df.empty:
            filtered_df = sub_df

    if filtered_df.empty:
        return "⚠️ Tidak ada tenant sesuai filter yang diberikan."

    weights = filtered_df["total_review"] + 1
    idx = random.choices(filtered_df.index.tolist(), weights=weights, k=1)[0]

    similar_indices = cosine_sim[idx].argsort()[::-1][1:top_n+1]
    return df.loc[similar_indices, ["nama_brand", "jenis_usaha", "lokasi",
                                    "rating", "total_review", "rentang_harga"]]

def run_clustering():
    """Jalankan clustering KMeans & Spectral + evaluasi"""
    X = df[["rating", "total_review"]].copy()
    X["total_review"] = np.log1p(X["total_review"])  # stabilisasi distribusi

    # --- KMeans ---
    kmeans = KMeans(n_clusters=2, random_state=0, n_init=10)
    df["cluster_kmeans"] = kmeans.fit_predict(X)

    # kmeans_eval = {
    #     "Silhouette": silhouette_score(X, df["cluster_kmeans"]),
    #     "Calinski-Harabasz": calinski_harabasz_score(X, df["cluster_kmeans"]),
    #     "Davies-Bouldin": davies_bouldin_score(X, df["cluster_kmeans"]),
    # }

    all_kmeans = {}
    for cluster_id in sorted(df["cluster_kmeans"].unique()):
        all_kmeans[cluster_id] = df[df["cluster_kmeans"] == cluster_id][
            ["nama_brand", "jenis_usaha", "lokasi", "rating", "total_review", "rentang_harga", "gambar"]
        ].sort_values(by="total_review", ascending=False)

    # --- Spectral ---
    knn_graph = kneighbors_graph(X, n_neighbors=10, include_self=False)
    adj_matrix = 0.5 * (knn_graph.toarray() + knn_graph.toarray().T)

    spectral = SpectralClustering(n_clusters=2, affinity="precomputed", random_state=0, assign_labels="kmeans")
    df["cluster_spectral"] = spectral.fit_predict(adj_matrix)

    # spectral_eval = {
    #     "Silhouette": silhouette_score(X, df["cluster_spectral"]),
    #     "Calinski-Harabasz": calinski_harabasz_score(X, df["cluster_spectral"]),
    #     "Davies-Bouldin": davies_bouldin_score(X, df["cluster_spectral"]),
    # }

    all_spectral = {}
    for cluster_id in sorted(df["cluster_spectral"].unique()):
        all_spectral[cluster_id] = df[df["cluster_spectral"] == cluster_id][
            ["nama_brand", "jenis_usaha", "lokasi", "rating", "total_review", "rentang_harga", "gambar"]
        ].sort_values(by="total_review", ascending=False)

    return {
        # "kmeans_eval": kmeans_eval,
        # "spectral_eval": spectral_eval,
        "all_kmeans": all_kmeans,
        "all_spectral": all_spectral
    }

# if __name__ == "__main__":
#     print("=== Testing algoritmaController.py ===\n")

#     print("\n=== Cek Rekomendasi Manual ===")
#     lokasi_input = input("Masukkan Lokasi (T1/T2) [Opsional]: ").strip() or None
#     aktivitas_input = input("Masukkan Aktivitas (Belanja/Makanan/Service) [Opsional]: ").strip() or None
#     harga_input = input("Masukkan Rentang Harga (murah/sedang/mahal) [Opsional]: ").strip() or None

#     hasil = get_recommendations_by_filters(lokasi_input, aktivitas_input, harga_input, top_n=10)

#     print("\n=== Hasil Rekomendasi ===")
#     print(hasil if isinstance(hasil, str) else hasil.head(10))

#     # Test clustering
#     print("--- Hasil Evaluasi Clustering ---")
#     hasil_cluster = run_clustering()
#     print("KMeans Eval:", hasil_cluster["kmeans_eval"])
#     print("Spectral Eval:", hasil_cluster["spectral_eval"])

#     for cluster_id, tenants in hasil_cluster["top_kmeans"].items():
#         print(f"\nTop 5 KMeans Cluster {cluster_id}:")
#         print(tenants.head(5))

#     for cluster_id, tenants in hasil_cluster["top_spectral"].items():
#         print(f"\nTop 5 Spectral Cluster {cluster_id}:")
#         print(tenants.head(5))

#     # Test rekomendasi sederhana
#     print("\n--- Hasil Rekomendasi ---")
#     rekom = get_recommendations_by_filters(lokasi="T1", aktivitas="Makanan", rentang_harga="sedang", top_n=5)
#     print(rekom)
