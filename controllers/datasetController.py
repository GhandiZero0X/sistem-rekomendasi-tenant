# controllers/datasetController.py
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
RAW_PATH = os.path.join(DATA_DIR, "processed_tenant_data.csv")

# Hapus tenant berdasarkan ID
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

# hapus tenant berdasarkan list of ID
# def delete_batch_tenants(tenant_ids: list):

# menampilkan semua tenant
def get_all_tenants():
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}

    df = pd.read_csv(RAW_PATH)

    if df.empty:
        return {"error": "Tidak ada tenant yang ditemukan."}

    return df.to_dict(orient="records")

# menampilkan tenant berdasarkan ID
def get_tenant_by_id(tenant_id: int):
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}

    df = pd.read_csv(RAW_PATH)

    if "id" not in df.columns:
        return {"error": "Kolom 'id' tidak ada di dataset."}

    tenant = df[df["id"].astype(int) == tenant_id]

    if tenant.empty:
        return {"error": f"Tenant dengan id {tenant_id} tidak ditemukan."}

    return tenant.to_dict(orient="records")[0]

# update tenant berdasarkan ID
def update_tenant(tenant_id: int, update_data: dict):
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}

    df = pd.read_csv(RAW_PATH)

    if "id" not in df.columns:
        return {"error": "Kolom 'id' tidak ada di dataset."}

    if tenant_id not in df["id"].astype(int).values:
        return {"error": f"Tenant dengan id {tenant_id} tidak ditemukan."}

    # Update data
    for key, value in update_data.items():
        if key in df.columns:
            df.loc[df["id"].astype(int) == tenant_id, key] = value

    # Simpan ulang
    df.to_csv(RAW_PATH, index=False)

    return {"success": f"Tenant dengan id {tenant_id} berhasil diupdate."}

# menambah tenant satu per satu
def add_tenant(tenant_data: dict):
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}

    df = pd.read_csv(RAW_PATH)

    # Tentukan ID baru
    new_id = 1
    if "id" in df.columns and not df.empty:
        new_id = df["id"].astype(int).max() + 1

    tenant_data["id"] = new_id

    # Tambah data baru
    df = df.append(tenant_data, ignore_index=True)

    # Simpan ulang
    df.to_csv(RAW_PATH, index=False)

    return {"success": f"Tenant dengan id {new_id} berhasil ditambahkan."}

# menambah tenant berdasarkan list of data
# def add_batch_tenants(tenants_data: list):