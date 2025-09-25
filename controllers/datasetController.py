# controllers/datasetController.py
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
RAW_PATH = os.path.join(DATA_DIR, "processed_tenant_data.csv")

def delete_tenant(tenant_id: int):
    """Hapus tenant berdasarkan ID"""
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}

    df = pd.read_csv(RAW_PATH)

    if "id" not in df.columns:
        return {"error": "Kolom 'id' tidak ada di dataset."}

    if tenant_id not in df["id"].astype(int).values:
        return {"error": f"Tenant dengan id {tenant_id} tidak ditemukan."}

    # Hapus row
    df = df[df["id"].astype(int) != tenant_id]

    # Re-assign ID biar urut lagi
    if "id" in df.columns:  
        df = df.drop(columns=["id"])  # drop dulu kalau ada
    df = df.reset_index(drop=True)
    df.insert(0, "id", range(1, len(df) + 1))
    df["id"] = df["id"].astype(int)  # pastikan int

    # Simpan ulang
    df.to_csv(RAW_PATH, index=False)

    return {"success": f"Tenant dengan id {tenant_id} berhasil dihapus."}
