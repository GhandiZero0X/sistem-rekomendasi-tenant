const puppeteer = require("puppeteer");
const fs = require("fs");

// load tenant Juanda dari file
let tenants = JSON.parse(fs.readFileSync("tenant_juanda.json", "utf-8"));

async function getGoogleMapsData(browser, tenantName) {
  const page = await browser.newPage();
  const searchQuery = `${tenantName} Juanda Airport`;
  const url = `https://www.google.com/maps/search/${encodeURIComponent(searchQuery)}`;

  console.log(`🔍 Cari di Google Maps: ${searchQuery}`);
  await page.goto(url, { waitUntil: "domcontentloaded" });

  try {
    // klik hasil pertama biar masuk ke detail
    await page.waitForSelector("a.hfpxzc", { timeout: 10000 });
    await page.click("a.hfpxzc");
    await page.waitForNavigation({ waitUntil: "domcontentloaded" });

    // ambil rating & total review
    const placeData = await page.evaluate(() => {
      const ratingEl = document.querySelector("span[aria-label*='bintang']");
      const reviewEl = document.querySelector("button[jsaction*='reviews']");

      const rating = ratingEl ? parseFloat(ratingEl.textContent.replace(",", ".")) : null;
      const totalReviews = reviewEl ? parseInt(reviewEl.textContent.replace(/\D/g, "")) : 0;

      return { rating, totalReviews };
    });

    // buka tab review
    const reviewTab = await page.$("button[jsaction*='reviews']");
    if (reviewTab) {
      await reviewTab.click();
      await page.waitForSelector(".jftiEf", { timeout: 10000 });

      // scroll biar reviewnya keluar lebih banyak
      for (let i = 0; i < 3; i++) {
        await page.evaluate(() => {
          document.querySelector(".DxyBCb").scrollBy(0, 2000);
        });
        await new Promise((r) => setTimeout(r, 2000));
      }

      // ambil review user
      const reviews = await page.evaluate(() => {
        const data = [];
        document.querySelectorAll(".jftiEf").forEach((el) => {
          const name = el.querySelector(".d4r55")?.innerText || "Anonim";
          const rating = el.querySelector("span[aria-label*='bintang']")?.getAttribute("aria-label") || null;
          const text = el.querySelector(".MyEned")?.innerText || "";
          const date = el.querySelector(".rsqaWe")?.innerText || "";
          data.push({ reviewer: name, rating, review: text, date });
        });
        return data;
      });

      await page.close();
      return { ...placeData, reviews };
    }

    await page.close();
    return { ...placeData, reviews: [] };
  } catch (err) {
    console.log(`⚠️ Tidak menemukan data untuk: ${tenantName}`);
    await page.close();
    return { rating: null, totalReviews: 0, reviews: [] };
  }
}

(async () => {
  const browser = await puppeteer.launch({ headless: false });

  let allReviews = [];

  for (let tenant of tenants) {
    const gmapData = await getGoogleMapsData(browser, tenant.nama);

    // update tenant_juanda.json
    tenant.rating = gmapData.rating;
    tenant.total_reviews = gmapData.totalReviews;

    // simpan review ke file terpisah
    allReviews.push({
      tenant: tenant.nama,
      lokasi: tenant.lokasi,
      reviews: gmapData.reviews,
    });

    // delay random biar aman
    await new Promise((r) => setTimeout(r, Math.floor(Math.random() * 4000) + 2000));
  }

  // tulis kembali tenant dengan rating
  fs.writeFileSync("tenant_juanda.json", JSON.stringify(tenants, null, 2), "utf-8");
  console.log("✅ tenant_juanda.json diperbarui dengan rating");

  // tulis review ke file baru
  fs.writeFileSync("reviewer_tenant_juanda.json", JSON.stringify(allReviews, null, 2), "utf-8");
  console.log("✅ reviewer_tenant_juanda.json berhasil dibuat");

  await browser.close();
})();
