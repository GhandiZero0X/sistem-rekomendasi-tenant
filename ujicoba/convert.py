import json
import csv

# Baca data dari file JSON
with open('processed_tenant_data.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# Tentukan nama kolom dari kunci dictionary pertama
fieldnames = data[0].keys()

# Tulis data ke file CSV
with open('processed_tenant_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

print("Konversi selesai. File CSV telah dibuat.")