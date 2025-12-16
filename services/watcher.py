# services/watcher.py
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from services.preprocessing import run_preprocessing
from watchdog.events import PatternMatchingEventHandler
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_PATH = os.path.join(DATA_DIR, "processed_tenant_data.csv")
LAST_SNAPSHOT_PATH = os.path.join(DATA_DIR, "processed_tenant_last.csv")

# Handler untuk perubahan file dataset tenant
class TenantFileHandler(PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(patterns=["*processed_tenant_data.csv"], ignore_directories=True)

    def on_modified(self, event):
        print("📂 Dataset tenant berubah, mulai cek...")

        max_retries = 5   # coba max 5x
        delay = 0.5       # jeda 0.5 detik antar percobaan

        for attempt in range(max_retries):
            try:
                # Test dulu file bisa dibaca
                df_raw = pd.read_csv(RAW_PATH)

                # Kalau sukses → langsung preprocessing
                run_preprocessing()

                # Update snapshot juga biar sinkron
                df_raw.to_csv(LAST_SNAPSHOT_PATH, index=False)

                print(f"✅ Preprocessing & snapshot update selesai (via watcher) setelah percobaan ke-{attempt+1}")
                break
            except Exception as e:
                print(f"⚠️ Gagal baca/preprocessing (percobaan {attempt+1}): {e}")
                time.sleep(delay)
        else:
            print("❌ Gagal preprocessing setelah beberapa percobaan.")

# Fungsi untuk memulai watcher
def start_watcher():
    event_handler = TenantFileHandler()
    observer = Observer()
    observer.schedule(event_handler, DATA_DIR, recursive=False)
    observer.start()
    print("👀 Watcher aktif, monitor perubahan dataset...")
    return observer
