import pandas as pd

# Baca dataset
df = pd.read_csv('processed_tenant_data.csv')

# Hapus duplikasi baris
df = df.drop_duplicates()

# Isi nilai kosong dengan 'unknown'
df = df.fillna('unknown')

# Ubah nama kolom menjadi lowercase
df.columns = [col.lower() for col in df.columns]

# Bersihkan spasi di awal/akhir pada kolom string
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.strip()

# Simpan hasil preprocessing ke file baru
df.to_csv('processed_tenant_data_preprocessed.csv', index=False)

print("Preprocessing selesai. File hasil: processed_tenant_data_preprocessed.csv")