// static/js/rekomendasi.js
document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("lihatRekomendasiBtn");
    const hasilSection = document.getElementById("hasilRekomendasi");
    const container = document.getElementById("rekomendasiContainer");
    const tenantDefault = document.getElementById("tenantDefault");

    btn.addEventListener("click", async function () {
        const lokasi = document.getElementById("kategoriSelect1").value;
        const aktivitas = document.getElementById("kategoriSelect2").value;
        const harga = document.getElementById("kategoriSelect3").value;

    // Validasi minimal satu filter diisi
    if (!lokasi && !aktivitas && !harga) {
        alert("Pilih minimal satu kategori untuk mendapatkan rekomendasi!");
        return;
    }

    // Sembunyikan tenant default & tampilkan section hasil rekomendasi
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

      // Render hasil rekomendasi
        container.innerHTML = data.map(
            (tenant) => `
                <div class="col-lg-3 col-12 mb-3 mb-lg-0 mt-2">
                    <div class="custom-block custom-block-full h-100" data-bs-toggle="modal" data-bs-target="#detailModal"
                        style="cursor:pointer;"
                        data-nama="${tenant.nama_brand}"
                        data-jenis="${tenant.jenis_usaha}"
                        data-lokasi="${tenant.lokasi}"
                        data-rating="${tenant.rating}"
                        data-review="${tenant.total_review}"
                        data-harga="${tenant.rentang_harga}"
                        data-gambar="/static/images/tenant/${tenant.gambar}">

                        <div class="custom-block-image-wrap">
                            <a href="#" data-bs-toggle="modal" data-bs-target="#detailModal">
                                <img src="/static/images/tenant/${tenant.gambar}" 
                                class="custom-block-image img-fluid" alt="${tenant.nama_brand}">
                            </a>
                        </div>
                        <div class="custom-block-info">
                        <h6 class="mb-2">
                            <a href="#" data-bs-toggle="modal" data-bs-target="#detailModal">
                        ${tenant.nama_brand}
                        </a></h6>

                        <div class="profile-block d-flex">
                            <p><strong>${tenant.lokasi}</strong></p>
                        </div>

                        <a href="#" class="mb-0" data-bs-toggle="modal" data-bs-target="#detailModal">
                            Lihat Detail
                        </a>

                        <div class="custom-block-bottom d-flex justify-content-between mt-3">
                            <a href="#" data-bs-toggle="modal" data-bs-target="#detailModal" class="me-1">
                                <i class="bi bi-star-fill"></i>
                                <span>${ tenant.rating }</span>
                            </a>
                            <a href="#" data-bs-toggle="modal" data-bs-target="#detailModal" class="bi-heart me-1">
                                <span>${ tenant.total_review }</span>
                            </a>
                            <a href="#" data-bs-toggle="modal" data-bs-target="#detailModal" class="me-1">
                                <i class="bi bi-coin"></i>
                                <span>
                                    ${
                                        !tenant.rentang_harga ||
                                        (typeof tenant.rentang_harga === "string" &&
                                        tenant.rentang_harga.toLowerCase() === "non_applicable")
                                            ? "-"
                                            : (typeof tenant.rentang_harga === "string"
                                                ? tenant.rentang_harga.charAt(0).toUpperCase() + tenant.rentang_harga.slice(1)
                                                : tenant.rentang_harga)
                                    }
                                </span>
                            </a>
                        </div>
                        </div>
                    </div>
                </div>
            `).join("");
        } catch (err) {
            console.error(err);
            container.innerHTML = `<p class="text-danger text-center">❌ Gagal mengambil data rekomendasi.</p>`;
        }
    });
});
