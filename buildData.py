import pandas as pd
import numpy as np

# load dataset dari file xlsx
data = pd.read_excel('dataset_tenant.xlsx')

# tampilkan 5 baris pertama sebelum diproses
print("=== Data asli (5 baris pertama) ===")
print(data.head())

# ambil hanya kolom yang diperlukan
# kolom: NO, BRAND, JENIS USAHA, LOKASI (gabungan LOKASI + TERMINAL)
data = data[['NO', 'BRAND', 'JENIS USAHA', 'LOKASI', 'TERMINAL']]

# gabungkan kolom LOKASI + TERMINAL (ubah TERMINAL ke string dulu)
data['LOKASI'] = data['LOKASI'] + ' Terminal ' + data['TERMINAL'].astype(str)

# tampilkan hasil olahan
print("\n=== Data setelah diproses (5 baris pertama) ===")
print(data.head())

# simpan hasil ke file CSV baru dengan kolom yang dimasukkan adalah NO, BRAND, JENIS USAHA, LOKASI
# filter hanya kolom yang diperlukan
data = data[['NO', 'BRAND', 'JENIS USAHA', 'LOKASI']]
# rubah nama kolom NO = id, BRAND = nama_brand, JENIS USAHA = jenis_usaha, LOKASI = lokasi
data.columns = ['id', 'nama_brand', 'jenis_usaha', 'lokasi']
data.to_csv('processed_tenant_data.csv', index=False)
print("\nData telah disimpan ke 'processed_tenant_data.csv'")

data = pd.read_csv('processed_tenant_data.csv')
print("\n=== Data dari file CSV (5 baris pertama) ===")
print(data.head())


