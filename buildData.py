import pandas as pd

# 1. Load dataset dari file xlsx
data = pd.read_excel('dataset_tenant.xlsx')

# 2. Tampilkan 5 baris pertama sebelum diproses
print("=== Data asli (5 baris pertama) ===")
print(data.head())

# 3. Ambil hanya kolom yang diperlukan
# Kolom: NO, BRAND, JENIS USAHA, LOKASI (gabungan LOKASI + TERMINAL)
data = data[['NO', 'BRAND', 'JENIS USAHA', 'LOKASI', 'TERMINAL']].copy()

# 4. Gabungkan kolom LOKASI + TERMINAL (konversi TERMINAL ke string dulu)
data['LOKASI'] = data['LOKASI'] + ' Terminal ' + data['TERMINAL'].astype(str)

# 5. Pilih hanya kolom final
data = data[['NO', 'BRAND', 'JENIS USAHA', 'LOKASI']]

# 6. Ubah nama kolom agar lebih konsisten
data.columns = ['id', 'nama_brand', 'jenis_usaha', 'lokasi']

# 7. Tampilkan hasil olahan
print("\n=== Data setelah diproses (5 baris pertama) ===")
print(data.head())

# 8. Simpan hasil ke file CSV baru
output_file = 'processed_tenant_data.csv'
data.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\n✅ Data telah disimpan ke '{output_file}'")

# 9. Load ulang file CSV untuk verifikasi
verify_data = pd.read_csv(output_file)
print("\n=== Data dari file CSV (5 baris pertama) ===")
print(verify_data.head())
