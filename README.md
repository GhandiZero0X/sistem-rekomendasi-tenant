# 🏬 Sistem Rekomendasi Tenant Bandara

Proyek ini adalah implementasi **Sistem Rekomendasi Tenant di Bandara** menggunakan **Python, Flask, dan Machine Learning (Clustering + Content-Based Filtering)**.  
Dataset tenant digunakan sebagai pengganti database, dan sistem ini mampu memberikan **rekomendasi dinamis** serta melakukan **evaluasi clustering** untuk menganalisis tenant mana yang dikategorikan tenant popular dan tenant baru.

---

## 🚀 Fitur Utama
- **Preprocessing Data**  
  Membersihkan dataset tenant, encoding fitur kategorikal, dan scaling fitur numerik.
- **Content-Based Filtering (CBF)**  
  Memberikan rekomendasi tenant berdasarkan **lokasi, aktivitas, dan rentang harga**.
- **Clustering Tenant**  
  Mengelompokkan tenant dengan:
  - **KMeans**
  - **Spectral Clustering (KNN Graph)**
- **Evaluasi Clustering**  
  Menggunakan 3 metrik populer:
  - Silhouette Score
  - Calinski-Harabasz Index
  - Davies-Bouldin Index
- **REST API dengan Flask**  
  Endpoint untuk rekomendasi dan hasil clustering.

---

## 📂 Struktur Direktori

```bash
sistem-rekomendasi-tenant/
│── controllers/
│   └── algoritmaControllers.py
│── data/
│   ├── processed_tenant_data.csv
│   ├── tenant_preprocessed.csv
│   ├── content_features.npy
│   ├── encoder.pkl
│   └── scaler.pkl
│── routes/
│   └── routes.py
│── services/
│   └── preprocessing.py
│── static/
│   ├── css/
│   ├── fonts/
│   ├── images/
│   └── js/
│── templates/
│   └── index.html
│── __init__.py
│── app.py
└── README.md
```

---

## ⚙️ Instalasi & Setup
1. Clone repositori:
   ```bash
   git clone https://github.com/GhandiZero0X/sistem-rekomendasi-tenant.git
2. Install dependencies
   ```bash
   pip install -r requirements.txt
3. Buat file env
4. Copy isi .env.example
5. Jalanakan generate secrect key
   ```bash
   python services/keysecrets.py
6. Masukkan secrect key kedalam env sesuai jenisnya
7. Jalanakan prepocessing data:
   ```bash
   python services/preprocessing.py
8. Jalankan aplikasi Flask:
   ```bash
   python app.py