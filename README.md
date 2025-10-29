# 🏬 Sistem Rekomendasi Tenant Bandara

Proyek ini adalah implementasi **Sistem Rekomendasi Tenant di Bandara** menggunakan **Python, Flask, dan Machine Learning (Clustering + Content-Based Filtering)**. Sistem ini dirancang untuk membantu pengelola bandara dalam melakukan analisis tenant, pemberian rekomendasi otomatis, dan manajemen data tenant serta user secara efisien dan aman.

---

## 🚀 Fitur Utama

### 🧠 Machine Learning & Rekomendasi
- **Preprocessing Otomatis**  
  Dataset akan otomatis diperbarui dan diproses (encoding, scaling, feature extraction) saat terjadi perubahan data.
- **Clustering Tenant**  
  Menggunakan:
  - **KMeans** untuk pengelompokan tenant populer & baru  
  - Evaluasi menggunakan **Silhouette**, **Calinski-Harabasz**, dan **Davies-Bouldin**
- **Content-Based Filtering (CBF)**  
  Rekomendasi tenant berdasarkan:
  - Lokasi (Terminal 1, 2, dst)
  - Jenis aktivitas (Makanan, Belanja, Layanan)
  - Rentang harga
- **Rekomendasi Dinamis**  
  Menampilkan top-10 tenant populer yang dipilih berdasarkan **rating**, **jumlah review**, dan **bobot fitur**.

---

### 🔐 Autentikasi & Keamanan
- **Login & Register Admin / Superadmin**  
  Sistem autentikasi menggunakan **bcrypt** untuk hashing password dan **JWT token** untuk sesi login.
- **Approval System (Superadmin)**  
  Superadmin dapat menyetujui akun admin sebelum aktif.
- **Rate Limiting**  
  Membatasi login 5x per menit per IP menggunakan `flask-limiter`.
- **Session & Token Handling**  
  Token disimpan di session dengan masa berlaku tertentu.
- **Logout Aman**  
  Menghapus session dan JWT dari browser.

---

### 👥 Manajemen User
CRUD lengkap untuk data user:
- Tambah user satuan / batch  
- Update data user  
- Nonaktifkan user (soft delete)  
- Download dataset user dalam format:
  - `.csv`
  - `.xlsx`  
- Hashing password otomatis dan status approval untuk kontrol akses.

---

### 🏪 Manajemen Tenant
CRUD lengkap untuk data tenant:
- Tambah tenant satuan / batch  
- Update & hapus tenant  
- Reindex ID setelah penghapusan otomatis  
- Ekspor dataset tenant ke format:
  - `.csv` (langsung dari browser)
  - `.xlsx` (Excel-friendly)

---

### 📊 Dashboard Analitik
Statistik dan metrik analisis untuk Superadmin & Admin:
- Jumlah tenant & user  
- Distribusi tenant berdasarkan **jenis usaha**, **terminal**, dan **rentang harga**  
- Rata-rata rating & total review  
- Status approval user dan peran (admin/superadmin)

---

### 🧩 Fitur Teknis Tambahan
- **File Watcher Otomatis**  
  Memantau perubahan pada file dataset (`processed_tenant_data.csv`) dan otomatis menjalankan *preprocessing* ulang.
- **Keamanan HTTP Headers**  
  Implementasi `Flask-Talisman` untuk CSP, HSTS, dan keamanan cookie.
- **Rate Limit Login Endpoint**  
  Proteksi dari brute force login.
- **JWT-based Authentication Middleware**  
  Mengamankan setiap route yang membutuhkan otorisasi.
- **Lazy Loading Gambar**  
  Optimasi tampilan agar efisien saat memuat banyak data tenant.

---

## 📂 Struktur Direktori

```bash
sistem-rekomendasi-tenant/
│── controllers/
│   ├── algoritmaControllers.py
│   ├── authController.py
│   ├── dashboardController.py
│   ├── dataController.py
│   ├── datasetController.py
│   ├── userController.py
│── data/
│   ├── processed_tenant_data.csv
│   ├── processed_tenant_last.csv
│   ├── tenant_preprocessed.csv
│   ├── content_features.npy
│   ├── encoder.pkl
│   ├── scaler.pkl
│   ├── users.csv
│── middlewares/
│   └── auth_middleware.py
│── routes/
│   └── routes.py
│── services/
│   ├── preprocessing.py
│   ├── init_admin.py
│   ├── keysecrets.py
│   ├── watcher.py
│── static/
│   ├── css/
│   ├── fonts/
│   ├── images/
│   └── js/
│── templates/
│   ├── layout/
│   ├── pages/
│   ├── partials/
│   └── index.html
│── utils/
│   └── jwt_utils.py
│── __init__.py
│── .env.example
│── .gitignore
│── .hintrc
│── app.py
│── catatan.txt
│── README.md
└── requirement.txt
```

---

## ⚙️ Instalasi & Setup
1. Clone repositori:
   ```bash
   git clone https://github.com/GhandiZero0X/sistem-rekomendasi-tenant.git
2. Install dependencies
   ```bash
   pip install -r requirements.txt
3. Buat file .env
   ```bash
   cp .env.example .env
4. Generate secret key
   ```bash
   python services/keysecrets.py
5. Masukkan secrect key kedalam env sesuai jenisnya
6. Jalanakan prepocessing data:
   ```bash
   python services/preprocessing.py
7. Jalankan aplikasi Flask:
   ```bash
   python app.py