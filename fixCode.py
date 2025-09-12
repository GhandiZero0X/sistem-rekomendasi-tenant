import pandas as pd

# 1. Load dataset dari file JSON
data = pd.read_json('processed_tenant_data.json')

# 2. Tampilkan 5 baris pertama sebelum diperbaiki
print("=== Data sebelum fix ID (5 baris pertama) ===")
print(data.head())

# 3. Urutkan data berdasarkan id lama (jaga konsistensi)
data = data.sort_values(by='id').reset_index(drop=True)

# 4. Reset id baru mulai dari 1
data['id'] = range(1, len(data) + 1)

# 5. Tampilkan 5 baris pertama setelah diperbaiki
print("\n=== Data setelah fix ID (5 baris pertama) ===")
print(data.head())

# 6. Simpan hasil fix ke file baru
output_file = 'processed_tenant_data.json'
data.to_json(output_file, orient='records', indent=4, force_ascii=False)
print(f"\n✅ Data dengan ID sudah diperbaiki dan disimpan ke '{output_file}'")
