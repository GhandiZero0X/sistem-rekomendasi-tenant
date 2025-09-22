
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# 1. Load dataset
df = pd.read_csv('processed_tenant_data.csv')

# 2. Handle Missing Values
# rating: isi null dengan rata-rata global
if df['rating'].isnull().any():
	mean_rating = df['rating'].mean()
	df['rating'] = df['rating'].fillna(mean_rating)

# total_review: isi null dengan 0
df['total_review'] = df['total_review'].fillna(0)

# rentang_harga: jika jenis_usaha Services, isi dengan 'non_applicable'
df.loc[df['jenis_usaha'].str.lower() == 'services', 'rentang_harga'] = 'non_applicable'
df['rentang_harga'] = df['rentang_harga'].fillna('non_applicable')

# 3. Encoding untuk Clustering (K-Prototypes)
# Numerik: rating (standarisasi), total_review (log transform)
df['rating_std'] = (df['rating'] - df['rating'].mean()) / df['rating'].std()
df['log_total_review'] = np.log1p(df['total_review'])

# Kategorikal: tetap string
clustering_features = [
	'rating_std',
	'log_total_review',
	'jenis_usaha',
	'lokasi',
	'rentang_harga'
]
df_clustering = df[clustering_features].copy()

# 4. Encoding untuk Content-Based Filtering (OneHot + Normalisasi)
# OneHot Encoding
df_cbf = df.copy()
cat_cols = ['jenis_usaha', 'lokasi', 'rentang_harga']
df_cbf = pd.get_dummies(df_cbf, columns=cat_cols)

# Normalisasi rating dan log_total_review
scaler = MinMaxScaler()
df_cbf['rating_norm'] = scaler.fit_transform(df[['rating']])
df_cbf['log_total_review_norm'] = scaler.fit_transform(np.log1p(df[['total_review']]))

# Drop kolom yang tidak dipakai (opsional, misal nama_brand)
# df_cbf = df_cbf.drop(['nama_brand'], axis=1)

# 5. Hybrid Score untuk Ranking
def bayesian_average(row, global_mean, m=10):
	# Bayesian average rating
	v = row['total_review']
	R = row['rating']
	return (v / (v + m)) * R + (m / (v + m)) * global_mean

global_mean = df['rating'].mean()
df['weighted_rating'] = df.apply(lambda row: bayesian_average(row, global_mean), axis=1)

# Contoh perhitungan hybrid score
def hybrid_score(cosine_sim, weighted_rating, alpha=0.7, beta=0.3):
	return alpha * cosine_sim + beta * weighted_rating

# Simpan hasil preprocessing
df.to_csv('processed_tenant_data_preprocessed.csv', index=False)
df_clustering.to_csv('tenant_clustering_ready.csv', index=False)
df_cbf.to_csv('tenant_cbf_ready.csv', index=False)

print("Preprocessing selesai. File hasil: processed_tenant_data_preprocessed.csv, tenant_clustering_ready.csv, tenant_cbf_ready.csv")
