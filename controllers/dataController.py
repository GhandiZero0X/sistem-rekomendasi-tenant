# controllers/dataController.py
import os
import pandas as pd
from services.preprocessing import run_preprocessing

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")

RAW_PATH = os.path.join(DATA_DIR, "processed_tenant_data.csv")
PREPROCESSED_PATH = os.path.join(DATA_DIR, "tenant_preprocessed.csv")
LAST_SNAPSHOT_PATH = os.path.join(DATA_DIR, "processed_tenant_last.csv")


def dataset_changed(df_raw, df_last):
    """Bandingkan apakah ada perubahan data"""
    # 1. Cek jumlah baris
    if df_raw.shape[0] != df_last.shape[0]:
        return True

    # 2. Cek jumlah kolom
    if list(df_raw.columns) != list(df_last.columns):
        return True

    # 3. Cek isi data (apakah ada row/kolom berubah)
    if not df_raw.equals(df_last):
        return True

    return False


def load_dataset():
    """Load dataset terbaru + auto jalankan preprocessing kalau ada perubahan"""
    df_raw = pd.read_csv(RAW_PATH)

    # kalau belum ada snapshot lama → bikin dulu
    if not os.path.exists(LAST_SNAPSHOT_PATH):
        df_raw.to_csv(LAST_SNAPSHOT_PATH, index=False)
        run_preprocessing()

    df_last = pd.read_csv(LAST_SNAPSHOT_PATH)

    if dataset_changed(df_raw, df_last):
        print("⚡ Data berubah, jalankan preprocessing ulang...")
        run_preprocessing()
        df_raw.to_csv(LAST_SNAPSHOT_PATH, index=False)  # update snapshot

    # load hasil preprocessing
    df_pre = pd.read_csv(PREPROCESSED_PATH)

    # Pastikan ID fresh dan int
    if "id" in df_pre.columns:
        df_pre = df_pre.drop(columns=["id"])
    df_pre.insert(0, "id", range(1, len(df_pre) + 1))

    # pastikan tipe id = int
    df_pre["id"] = df_pre["id"].astype(int)

    return df_pre
