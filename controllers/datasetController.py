# controllers/datasetController.py
from flask import send_file, Response
import io
import os
import pandas as pd
import tempfile
from io import BytesIO
from flask import Response
from pyexcelerate import Workbook

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
    df = pd.read_csv(RAW_PATH) if os.path.exists(RAW_PATH) else pd.DataFrame(columns=[
        "id", "nama_brand", "jenis_usaha", "lokasi", "rating", "total_review", "rentang_harga", "gambar"
    ])
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

# Download dataset dalam format CSV
def download_dataset_csv():
    """Download dataset dalam format CSV"""
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}, 404

    df = pd.read_csv(RAW_PATH)

    # Buat buffer file CSV di memori
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return Response(
        csv_buffer.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=tenant_dataset.csv"
        }
    )

# Download dataset dalam format Excel
def download_dataset_excel():
    """Download dataset dalam format Excel"""
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}, 404

    df = pd.read_csv(RAW_PATH)

    # Simpan sementara ke memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Tenant Data")
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="tenant_dataset.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Download dataset CSV yang dikonversi ke Excel
def download_csv_converted_to_excel():
    """Baca CSV, konversi ke Excel (.xlsx) menggunakan pyexcelerate (via temp file),
    lalu kembalikan sebagai attachment bytes (sama gaya dengan download_users_excel)."""
    if not os.path.exists(RAW_PATH):
        return {"error": "Dataset tidak ditemukan."}, 404

    # Load CSV
    df = pd.read_csv(RAW_PATH)

    # Replace NaN -> empty string supaya pyexcelerate ga error dan tampilan lebih bersih
    df = df.fillna("")

    # Siapkan data sebagai list of lists: header + rows
    data = [df.columns.tolist()] + df.values.tolist()

    # Tulis ke temporary .xlsx file karena pyexcelerate save() butuh path
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        wb = Workbook()
        # pyexcelerate expects a 1-based row/col indexing, but new_sheet with data works
        wb.new_sheet("Tenant Data", data=data)
        wb.save(tmp_path)

        # Baca file sementara ke memory
        with open(tmp_path, "rb") as f:
            file_bytes = f.read()

        return Response(
            file_bytes,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=tenant_dataset_from_csv.xlsx"
            }
        )
    finally:
        # cleanup file sementara jika ada
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass