# controllers/datasetController.py
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
RAW_PATH = os.path.join(DATA_DIR, "processed_tenant_data.csv")

# Get all tenants
def get_all_tenants():
    """"Menampilkan semua tenant"""
    if not os.path.exists(RAW_PATH):
        return []
    df = pd.read_csv(RAW_PATH)
    return df.to_dict(orient="records")

# Get tenant by ID
def get_tenant_by_id(tenant_id: int):
    """Menampilkan satu tenant berdasarkan ID"""
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}
    df = pd.read_csv(RAW_PATH)
    tenant = df[df["id"].astype(int) == tenant_id]
    if tenant.empty:
        return {"error": f"Tenant dengan id {tenant_id} tidak ditemukan."}
    return tenant.to_dict(orient="records")[0]

# Add tenant
def add_tenant(tenant_data: dict):
    """"Tambah satu tenant"""
    df = pd.read_csv(RAW_PATH) if os.path.exists(RAW_PATH) else pd.DataFrame()
    
    # auto-assign ID
    next_id = 1 if df.empty else df["id"].max() + 1
    tenant_data["id"] = int(next_id)

    df = pd.concat([df, pd.DataFrame([tenant_data])], ignore_index=True)
    df.to_csv(RAW_PATH, index=False)
    return {"success": f"Tenant baru dengan id {next_id} berhasil ditambahkan."}

# add tenant batch
def add_batch_tenants(tenants_data: list):
    """Tambah banyak tenant sekaligus"""
    if not tenants_data or not isinstance(tenants_data, list):
        return {"error": "Input harus berupa list of tenant data."}

    df = pd.read_csv(RAW_PATH) if os.path.exists(RAW_PATH) else pd.DataFrame()

    # Cari ID terakhir
    next_id = 1 if df.empty else df["id"].max() + 1

    # Tambahkan ID ke setiap tenant baru
    for i, tenant in enumerate(tenants_data):
        tenant["id"] = int(next_id + i)

    # Gabungkan ke dataset
    new_df = pd.DataFrame(tenants_data)
    df = pd.concat([df, new_df], ignore_index=True)

    # Simpan ulang
    df.to_csv(RAW_PATH, index=False)

    return {"success": f"{len(tenants_data)} tenant berhasil ditambahkan."}

# Update tenant
def update_tenant(tenant_id: int, update_data: dict):
    """Merubah data tenant berdasarkan ID"""
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}
    df = pd.read_csv(RAW_PATH)

    if tenant_id not in df["id"].astype(int).values:
        return {"error": f"Tenant dengan id {tenant_id} tidak ditemukan."}

    for key, value in update_data.items():
        if key in df.columns:
            df.loc[df["id"] == tenant_id, key] = value

    df.to_csv(RAW_PATH, index=False)
    return {"success": f"Tenant dengan id {tenant_id} berhasil diperbarui."}

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
def delete_batch_tenants(tenant_ids: list):
    """Hapus banyak tenant berdasarkan list of ID"""
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}

    if not tenant_ids or not isinstance(tenant_ids, list):
        return {"error": "Input harus berupa list of tenant IDs."}

    df = pd.read_csv(RAW_PATH)

    if "id" not in df.columns:
        return {"error": "Kolom 'id' tidak ada di dataset."}

    existing_ids = df["id"].astype(int).values
    invalid_ids = [tid for tid in tenant_ids if tid not in existing_ids]
    if invalid_ids:
        return {"error": f"Tenant dengan id {invalid_ids} tidak ditemukan."}

    # Hapus rows
    df = df[~df["id"].astype(int).isin(tenant_ids)]

    # Re-assign ID biar urut lagi
    if "id" in df.columns:  
        df = df.drop(columns=["id"])  # drop dulu kalau ada
    df = df.reset_index(drop=True)
    df.insert(0, "id", range(1, len(df) + 1))
    df["id"] = df["id"].astype(int)  # pastikan int

    # Simpan ulang
    df.to_csv(RAW_PATH, index=False)

    return {"success": f"{len(tenant_ids)} tenant berhasil dihapus."}