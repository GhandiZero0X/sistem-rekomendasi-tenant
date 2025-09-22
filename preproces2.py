import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import warnings

warnings.filterwarnings("ignore")

# Step 1: Load dataset
df = pd.read_csv("processed_tenant_data.csv")

# Step 2: Handle Missing Values
df["rating"] = df["rating"].fillna(df["rating"].mean()) if "rating" in df.columns else np.nan
df["total_review"] = df["total_review"].fillna(0) if "total_review" in df.columns else 0

# Step 3: Ambil fitur untuk clustering
X = df[["rating", "total_review"]].copy()

# Log transform review biar skala lebih seimbang
X["total_review"] = np.log1p(X["total_review"])

# Normalisasi biar skala rata
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Step 4: Clustering dengan KMeans
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

# Tambahkan hasil cluster ke dataframe
df["cluster"] = clusters

print("\n=== Data dengan cluster (rating + total_review) ===")
print(df[["nama_brand", "rating", "total_review", "cluster"]].head())

# Step 5: Evaluasi Clustering
print("\n=== Evaluasi Clustering ===")

# Silhouette Score
sil_score = silhouette_score(X_scaled, df["cluster"])
print("Silhouette Score:", sil_score)

# Calinski-Harabasz Index
ch_score = calinski_harabasz_score(X_scaled, df["cluster"])
print("Calinski-Harabasz Index:", ch_score)

# Davies-Bouldin Index
db_score = davies_bouldin_score(X_scaled, df["cluster"])
print("Davies-Bouldin Index:", db_score)

# Distribusi Cluster
print("\n=== Distribusi Tenant per Cluster ===")
print(df["cluster"].value_counts())

# Step 6: Save hasil clustering
df.to_csv("tenant_clusters_rating_review.csv", index=False)
print("\nFile hasil clustering disimpan sebagai: tenant_clusters_rating_review.csv")
