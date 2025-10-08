// static/js/rekomendasi.js
document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("lihatRekomendasiBtn");
  const hasilSection = document.getElementById("hasilRekomendasi");
  const container = document.getElementById("rekomendasiContainer");
  const tenantDefault = document.getElementById("tenantDefault");

  // === Fungsi umum untuk batch display ===
  function showBatchedItems(containerSelector, batchSize, buttonSelector) {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    const items = container.querySelectorAll(".tenant-card");
    const button = document.querySelector(buttonSelector);
    let visibleCount = 0;

    const showNextBatch = () => {
      for (let i = visibleCount; i < visibleCount + batchSize && i < items.length; i++) {
        items[i].style.display = "block";
      }
      visibleCount += batchSize;
      if (visibleCount >= items.length && button) {
        button.style.display = "none";
      }
    };

    if (button) button.addEventListener("click", showNextBatch);
    showNextBatch();
  }

  // === Jalankan batch display default ===
  showBatchedItems("#tenantPopularContainer", 8, "#loadMorePopular");
  showBatchedItems("#tenantNewContainer", 8, "#loadMoreNew");

  // === Event tombol rekomendasi ===
  btn.addEventListener("click", async function () {
    const lokasi = document.getElementById("kategoriSelect1").value;
    const aktivitas = document.getElementById("kategoriSelect2").value;
    const harga = document.getElementById("kategoriSelect3").value;

    if (!lokasi && !aktivitas && !harga) {
      alert("Pilih minimal satu kategori untuk mendapatkan rekomendasi!");
      return;
    }

    tenantDefault.style.display = "none";
    hasilSection.style.display = "block";
    container.innerHTML = `<p class="text-center text-muted">🔍 Sedang mencari rekomendasi...</p>`;

    try {
      const params = new URLSearchParams({
        ...(lokasi && { lokasi }),
        ...(aktivitas && { aktivitas }),
        ...(harga && { harga }),
      });

      const response = await fetch(`/recommend?${params.toString()}`);
      const data = await response.json();

      if (!response.ok) {
        container.innerHTML = `<p class="text-danger text-center">${data.error}</p>`;
        return;
      }

      // Render hasil rekomendasi ke container
      container.innerHTML = data.map((tenant) => `
        <div class="tenant-card col-lg-3 col-12 mb-3 mb-lg-0 mt-2" style="display:none;">
            <div class="custom-block custom-block-full h-100" style="cursor:pointer;" data-bs-toggle="modal"
                data-bs-target="#detailModal"
                data-nama="${tenant.nama_brand}"
                data-jenis="${tenant.jenis_usaha}"
                data-lokasi="${tenant.lokasi}"
                data-rating="${tenant.rating}"
                data-review="${tenant.total_review}"
                data-harga="${tenant.rentang_harga}"
                data-gambar="/static/images/tenant/${tenant.gambar}">
                <div class="custom-block-image-wrap">
                    <img src="/static/images/tenant/${tenant.gambar}" class="custom-block-image img-fluid" alt="${tenant.nama_brand}">
                </div>
                <div class="custom-block-info">
                    <h6 class="mb-2"><a href="#" data-bs-toggle="modal" data-bs-target="#detailModal">${tenant.nama_brand}</a></h6>
                    <div class="profile-block d-flex"><p><strong>${tenant.lokasi}</strong></p></div>
                    <a href="#" class="mb-0" data-bs-toggle="modal" data-bs-target="#detailModal">Lihat Detail</a>
                    <div class="custom-block-bottom d-flex justify-content-between mt-3">
                        <a href="#" class="me-1"><i class="bi bi-star-fill"></i> <span>${tenant.rating}</span></a>
                        <a href="#" class="bi-heart me-1"><span>${tenant.total_review}</span></a>
                        <a href="#" class="me-1"><i class="bi bi-coin"></i> <span>${
                        !tenant.rentang_harga ||
                        (tenant.rentang_harga.toLowerCase() === "non_applicable")
                            ? "-"
                            : tenant.rentang_harga.charAt(0).toUpperCase() + tenant.rentang_harga.slice(1)
                        }</span></a>
                    </div>
                </div>
            </div>
        </div>`).join("");

      // tampilkan batch pertama rekomendasi
      document.getElementById("loadMoreRekomendasi").style.display = "block";
      showBatchedItems("#rekomendasiContainer", 10, "#loadMoreRekomendasi");

    } catch (err) {
      console.error(err);
      container.innerHTML = `<p class="text-danger text-center">❌ Gagal mengambil data rekomendasi.</p>`;
    }
  });
});
