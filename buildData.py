import pandas as pd

# Load dataset dari file xlsx
data = pd.read_excel('dataset_tenant.xlsx')

# Tampilkan 5 baris pertama sebelum diproses
print("=== Data asli (5 baris pertama) ===")
print(data.head())

# Ambil hanya kolom yang diperlukan
# Kolom: NO, BRAND, JENIS USAHA, LOKASI (gabungan LOKASI + TERMINAL)
data = data[['NO', 'BRAND', 'JENIS USAHA', 'LOKASI', 'TERMINAL']].copy()

# Menggabungkan kolom LOKASI + TERMINAL (konversi TERMINAL ke string dulu)
data['LOKASI'] = data['LOKASI'] + ' Terminal ' + data['TERMINAL'].astype(str)

# Pilih hanya kolom final
data = data[['NO', 'BRAND', 'JENIS USAHA', 'LOKASI']]

# Ubah nama kolom agar lebih konsisten
data.columns = ['id', 'nama_brand', 'jenis_usaha', 'lokasi']

# Menampilkan hasil olahan
print("\n=== Data setelah diproses (5 baris pertama) ===")
print(data.head())

# Simpan hasil ke file CSV baru
output_file = 'processed_tenant_data.csv'
data.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\n✅ Data telah disimpan ke '{output_file}'")

# Load ulang file CSV untuk verifikasi
verify_data = pd.read_csv(output_file)
print("\n=== Data dari file CSV (5 baris pertama) ===")
print(verify_data.head())

#comvert file csv to json
json_output_file = 'processed_tenant_data.json'
data.to_json(json_output_file, orient='records', force_ascii=False, indent=4)
print(f"\n✅ Data telah disimpan ke '{json_output_file}'")
# menambahkan kolom untuk file json ini rating, total_review, penjualan dan masukkan ke dalam file json 'processed_tenant_data.json'
data['rating'] = None
data['total_review'] = None
data['penjualan'] = None
data.to_json(json_output_file, orient='records', force_ascii=False, indent=4)
print(f"\n✅ Data telah disimpan ke '{json_output_file}' dengan kolom tambahan")