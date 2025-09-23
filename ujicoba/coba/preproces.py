import pandas as pd
import numpy as np
from sklearn.preprocessing import (
    OneHotEncoder, MinMaxScaler, StandardScaler,
    RobustScaler, PowerTransformer, QuantileTransformer
)
import joblib

# Step 1: Load dataset
df = pd.read_csv("processed_tenant_data.csv")

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

# ==== Pilih scaler yang mau dipakai ====
scaler_choice = "Standard"   # ganti ke: "MinMax", "Standard", "Robust", "Power", "Quantile"

if scaler_choice == "MinMax":
    scaler = MinMaxScaler()
elif scaler_choice == "Standard":
    scaler = StandardScaler()
elif scaler_choice == "Robust":
    scaler = RobustScaler()
elif scaler_choice == "Power":
    scaler = PowerTransformer(method="yeo-johnson")
elif scaler_choice == "Quantile":
    scaler = QuantileTransformer(output_distribution="normal", random_state=0)
else:
    raise ValueError("Scaler tidak dikenali!")

# Scale numeric
num_scaled = scaler.fit_transform(df[numeric_cols])

# Gabung fitur akhir
content_features = np.hstack([cat_encoded, num_scaled])

# Step 4: Save hasil preprocessing
df.to_csv("tenant_preprocessed.csv", index=False)
np.save("content_features.npy", content_features)
joblib.dump(encoder, "encoder.pkl")
joblib.dump(scaler, "scaler.pkl")

print(f"✅ Preprocessing selesai dengan {scaler_choice}Scaler.")
print("- tenant_preprocessed.csv")
print("- content_features.npy")
print("- encoder.pkl, scaler.pkl")
