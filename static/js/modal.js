// static/js/modal.js
// modal untuk menampilkan detail tenant populer dan baru
document.addEventListener("DOMContentLoaded", function () {
  // Tangkap modal utama dan elemen di dalamnya
  const modal = document.getElementById("detailModal");
  const modalTitle = modal.querySelector(".modal-title");
  const modalBody = modal.querySelector(".modal-body");

  // Tangkap semua card tenant
  document.querySelectorAll(".custom-block").forEach(card => {
    card.addEventListener("click", function () {
      const data = this.dataset; // ambil semua data-* di card itu
      modalTitle.textContent = `Detail ${data.nama}`;
      modalBody.innerHTML = `
        <div class="row g-3 align-items-center">
          <div class="col-md-5 text-center">
            <img src="${data.gambar}" alt="${data.nama}"
                 class="img-fluid rounded" style="max-height: 350px; object-fit: cover;">
          </div>

          <div class="col-md-7">
            <table class="table table-borderless">
              <tr><th style="width: 40%;">Nama</th><td>${data.nama}</td></tr>
              <tr><th>Jenis Usaha</th><td>${data.jenis}</td></tr>
              <tr><th>Lokasi</th><td>${data.lokasi}</td></tr>
              <tr><th>Rating</th><td>⭐ ${data.rating}</td></tr>
              <tr><th>Total Review</th><td>${data.review}</td></tr>
              <tr><th>Harga</th><td>${data.harga && data.harga.toLowerCase() !== 'non_applicable' ? data.harga : '-'}</td></tr>
            </table>
          </div>
        </div>
      `;
    });
  });
});

// modal untuk menampilkan detail tenant rekomendasi 
document.addEventListener("click", function (e) {
  const card = e.target.closest(".custom-block");
  if (!card) return; // bukan elemen card

  const data = card.dataset;
  const modal = document.getElementById("detailModal");

  modal.querySelector(".modal-title").textContent = `Detail ${data.nama}`;
  modal.querySelector(".modal-body").innerHTML = `
    <div class="row g-3 align-items-center">
      <div class="col-md-5 text-center">
        <img src="${data.gambar}" alt="${data.nama}" class="img-fluid rounded" style="max-height: 350px;">
      </div>
      <div class="col-md-7">
        <table class="table table-borderless">
          <tr><th>Nama</th><td>${data.nama}</td></tr>
          <tr><th>Jenis Usaha</th><td>${data.jenis}</td></tr>
          <tr><th>Lokasi</th><td>${data.lokasi}</td></tr>
          <tr><th>Rating</th><td>⭐ ${data.rating}</td></tr>
          <tr><th>Total Review</th><td>${data.review}</td></tr>
          <tr><th>Harga</th><td>${data.harga}</td></tr>
        </table>
      </div>
    </div>
  `;
});
