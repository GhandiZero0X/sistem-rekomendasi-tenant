import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # naik 1 folder dari /services
DATA_DIR = os.path.join(BASE_DIR, "data")

# Step 1: Load dataset
df = pd.read_csv(os.path.join(DATA_DIR, "processed_tenant_data.csv"))

# Step 2: Handle Missing Values
df["rating"] = df["rating"].fillna(df["rating"].mean())
df["total_review"] = df["total_review"].fillna(0)
df["rentang_harga"] = df["rentang_harga"].fillna("non_applicable")

# Step 3: Preprocessing
categorical_cols = ["jenis_usaha", "lokasi", "rentang_harga"]
numeric_cols = ["rating", "total_review"]

# OneHot Encode categorical
encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
cat_encoded = encoder.fit_transform(df[categorical_cols])

# Scale numeric
scaler = StandardScaler()
num_scaled = scaler.fit_transform(df[numeric_cols])

# Gabung fitur
content_features = np.hstack([cat_encoded, num_scaled])

# Step 4: Save hasil preprocessing
df.to_csv(os.path.join(DATA_DIR, "tenant_preprocessed.csv"), index=False)
np.save(os.path.join(DATA_DIR, "content_features.npy"), content_features)
joblib.dump(encoder, os.path.join(DATA_DIR, "encoder.pkl"))
joblib.dump(scaler, os.path.join(DATA_DIR, "scaler.pkl"))

print("✅ Preprocessing selesai. File disimpan di folder data/")
