import pandas as pd


def load_dataset(filepath: str) -> pd.DataFrame:
    """Load dataset tenant dari file Excel."""
    return pd.read_excel(filepath)


def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess dataset:
    - Ambil kolom yang relevan
    - Gabungkan lokasi dengan terminal
    - Rename kolom sesuai kebutuhan
    """
    # Pilih kolom yang diperlukan
    df = df[['NO', 'BRAND', 'JENIS USAHA', 'LOKASI', 'TERMINAL']].copy()

    # Gabungkan lokasi + terminal
    df['LOKASI'] = df['LOKASI'] + ' Terminal ' + df['TERMINAL'].astype(str)

    # Pilih hanya kolom final
    df = df[['NO', 'BRAND', 'JENIS USAHA', 'LOKASI']]

    # Rename kolom agar lebih konsisten
    df.columns = ['id', 'nama_brand', 'jenis_usaha', 'lokasi']

    return df


def save_dataset(df: pd.DataFrame, output_path: str) -> None:
    """Simpan dataset ke file CSV."""
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ Data berhasil disimpan ke: {output_path}")


def main():
    # Path file input & output
    input_file = "dataset_tenant.xlsx"
    output_file = "processed_tenant_data.csv"

    # 1. Load dataset
    raw_data = load_dataset(input_file)
    print("=== Data asli (5 baris pertama) ===")
    print(raw_data.head())

    # 2. Preprocess dataset
    processed_data = preprocess_dataset(raw_data)
    print("\n=== Data setelah diproses (5 baris pertama) ===")
    print(processed_data.head())

    # 3. Save dataset hasil olahan
    save_dataset(processed_data, output_file)

    # 4. Load ulang untuk verifikasi
    verify_data = pd.read_csv(output_file)
    print("\n=== Data dari file CSV (5 baris pertama) ===")
    print(verify_data.head())


if __name__ == "__main__":
    main()
