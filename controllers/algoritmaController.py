# controllers/algoritmaController.py
# cek jika menggunakan terminal langsung
# import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import kneighbors_graph
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
import random
from controllers.dataController import load_dataset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")

# Load dataset (auto cek + update kalau ada perubahan)
df = load_dataset()
content_features = np.load(os.path.join(DATA_DIR, "content_features.npy"))
encoder = joblib.load(os.path.join(DATA_DIR, "encoder.pkl"))
scaler = joblib.load(os.path.join(DATA_DIR, "scaler.pkl"))

# Normalisasi lokasi → terminal
df["terminal"] = df["lokasi"].str.extract(r"(Terminal\s*\d)", expand=False).fillna("Unknown")
df["terminal"] = df["terminal"].str.replace("Terminal ", "T")

# Content-Based Filtering
# Mapping bobot per fitur
weight_mapping = {
    "jenis_usaha": 2.0,
    "lokasi": 1.5,
    "rentang_harga": 1.0,
    "rating": 2.0,
    "total_review": 1.5,
}

# Ambil jumlah kolom hasil encoding
feature_weights = []
for i, cats in enumerate(encoder.categories_):
    if i == 0:  # jenis_usaha
        feature_weights.extend([weight_mapping["jenis_usaha"]] * len(cats))
    elif i == 1:  # lokasi
        feature_weights.extend([weight_mapping["lokasi"]] * len(cats))
    elif i == 2:  # rentang_harga
        feature_weights.extend([weight_mapping["rentang_harga"]] * len(cats))

# Tambahkan bobot untuk fitur numerik
feature_weights.extend([weight_mapping["rating"]])       # rating
feature_weights.extend([weight_mapping["total_review"]]) # total_review
feature_weights = np.array(feature_weights)

# Safety check
assert feature_weights.shape[0] == content_features.shape[1], \
    f"Mismatch: weights {feature_weights.shape[0]} vs features {content_features.shape[1]}"

# Terapkan bobot ke content features
weighted_features = content_features * feature_weights
cosine_sim = cosine_similarity(weighted_features)
# cosine_sim = cosine_similarity(content_features)

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

    # Sampling tenant awal berdasarkan popularitas
    weights = filtered_df["total_review"] + 1
    idx = random.choices(filtered_df.index.tolist(), weights=weights, k=1)[0]
    # idx = filtered_df.sort_values(by="total_review", ascending=False).index[0]

    # Hitung similarity berdasarkan weighted cosine
    sim_scores = cosine_sim[idx]

    # Urutkan tenant berdasarkan skor similarity
    similar_indices = sim_scores.argsort()[::-1][1:top_n+1]

    return df.loc[similar_indices, ["id", "nama_brand", "jenis_usaha", "lokasi",
                                    "rating", "total_review", "rentang_harga"]]

def run_clustering():
    """Jalankan clustering KMeans & Spectral"""
    X = df[["rating", "total_review"]].copy()
    X["total_review"] = np.log1p(X["total_review"])  # stabilisasi distribusi

    # --- KMeans ---
    kmeans = KMeans(n_clusters=2, random_state=0, n_init=10)
    df["cluster_kmeans"] = kmeans.fit_predict(X)

    all_kmeans = {}
    kmeans_eval = { 
        "Silhouette": silhouette_score(X, df["cluster_kmeans"]),
        "Calinski-Harabasz": calinski_harabasz_score(X, df["cluster_kmeans"]),
        "Davies-Bouldin": davies_bouldin_score(X, df["cluster_kmeans"]),
    }  
    
    for cluster_id in sorted(df["cluster_kmeans"].unique()):
        all_kmeans[cluster_id] = df[df["cluster_kmeans"] == cluster_id][
            ["id", "nama_brand", "jenis_usaha", "lokasi", "rating", "total_review", "rentang_harga", "gambar"]
        ].sort_values(by="total_review", ascending=False)

    return {
        # "kmeans_eval": kmeans_eval,
        "all_kmeans": all_kmeans,
    }

# def evaluate_recommendation(lokasi="T1", aktivitas="Makanan", rentang_harga="murah", top_n=10):
#     """Evaluasi rekomendasi sederhana pakai Precision@K & Recall@K"""
#     hasil = get_recommendations_by_filters(lokasi, aktivitas, rentang_harga, top_n=top_n)
    
#     if isinstance(hasil, str) or hasil is None:
#         print("⚠️", hasil)
#         return

#     # Anggap relevan kalau rating >= 4.0
#     relevan = hasil[hasil["rating"] >= 3.7]

#     precision = len(relevan) / top_n
#     total_relevan = df[(df["rating"] >= 3.7)].shape[0]
#     recall = len(relevan) / total_relevan if total_relevan > 0 else 0

#     print("=== Evaluasi Rekomendasi ===")
#     print(f"Precision@{top_n}: {precision:.2f}")
#     print(f"Recall@{top_n}: {recall:.2f}")
#     print("\nTop-N Rekomendasi:")
#     print(hasil)

# if __name__ == "__main__":
    # print("=== Testing Terminal algoritmaController.py ===\n")
    # print("=== Testing Evaluasi Rekomendasi ===\n")

    # # Coba evaluasi dengan filter tertentu
    # evaluate_recommendation(lokasi="T1", aktivitas="Makanan", rentang_harga="murah", top_n=10)

    # # Coba clustering
    # print("\n=== Testing Clustering ===")
    # clusters = run_clustering()
    # for cluster_id, tenants in clusters["all_kmeans"].items():
    #     print(f"\nCluster KMeans {cluster_id} (Top 3):")
    #     print(tenants.head(3)[["nama_brand", "rating", "total_review"]])

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
