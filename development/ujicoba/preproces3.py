import pandas as pd
import numpy as np
from kmodes.kprototypes import KPrototypes
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import warnings

warnings.filterwarnings("ignore")

# ==============================
# Step 1: Load dataset
# ==============================
df = pd.read_csv("processed_tenant_data.csv")

# ==============================
# Step 2: Handle Missing Values
# ==============================
df["rating"] = df["rating"].fillna(df["rating"].mean()) if "rating" in df.columns else np.nan
df["total_review"] = df["total_review"].fillna(0) if "total_review" in df.columns else 0
df["rentang_harga"] = df["rentang_harga"].fillna("non_applicable") if "rentang_harga" in df.columns else "non_applicable"

# ==============================
# Step 3: Ambil fitur untuk clustering
# ==============================
cluster_features = ["rating", "total_review", "rentang_harga"]
df_cluster = df[cluster_features].copy()

# Ubah kolom kategorikal ke string
categorical_columns = ["rentang_harga"]
for col in categorical_columns:
    df_cluster[col] = df_cluster[col].astype(str)

# Transformasi numerik untuk review (biar seimbang)
df_cluster["total_review"] = np.log1p(df_cluster["total_review"])

# Simpan index kolom kategorikal untuk K-Prototypes
cat_cols_idx = [df_cluster.columns.get_loc(c) for c in categorical_columns]

# ==============================
# Step 4: Clustering dengan K-Prototypes
# ==============================
kproto = KPrototypes(n_clusters=3, init='Huang', verbose=1, random_state=42)
clusters = kproto.fit_predict(df_cluster.values, categorical=cat_cols_idx)

# Tambahkan hasil cluster ke dataframe
df["cluster"] = clusters

print("\n=== Data dengan cluster (rating + total_review + rentang_harga) ===")
print(df[["nama_brand", "rating", "total_review", "rentang_harga", "cluster"]].head())

# ==============================
# Step 5: Evaluasi Clustering
# ==============================
print("\n=== Evaluasi Clustering ===")

# Untuk evaluasi, encode kategorikal biar bisa dipakai metrik sklearn
df_eval = df_cluster.copy()
df_eval_encoded = pd.get_dummies(df_eval, columns=categorical_columns)

# Silhouette Score
try:
    sil_score = silhouette_score(df_eval_encoded, df["cluster"])
    print("Silhouette Score:", sil_score)
except Exception as e:
    print("Silhouette Score tidak bisa dihitung:", e)

# Calinski-Harabasz Index
ch_score = calinski_harabasz_score(df_eval_encoded, df["cluster"])
print("Calinski-Harabasz Index:", ch_score)

# Davies-Bouldin Index
db_score = davies_bouldin_score(df_eval_encoded, df["cluster"])
print("Davies-Bouldin Index:", db_score)

# Distribusi Cluster
print("\n=== Distribusi Tenant per Cluster ===")
print(df["cluster"].value_counts())

# ==============================
# Step 6: Ringkasan tiap cluster
# ==============================
summary = df.groupby("cluster").agg({
    "rating": "mean",
    "total_review": "mean",
    "rentang_harga": lambda x: x.mode()[0]  # ambil kategori dominan
})

print("\n=== Ringkasan per Cluster ===")
print(summary)

# ==============================
# Step 7: Save hasil clustering
# ==============================
df.to_csv("tenant_clusters_rating_review_price.csv", index=False)
print("\nFile hasil clustering disimpan sebagai: tenant_clusters_rating_review_price.csv")
