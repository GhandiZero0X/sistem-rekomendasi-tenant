const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  let tenants = [];
  let pageNum = 1;
  let hasData = true;

  while (hasData) {
    const url = `https://juanda-airport.com/id/data-directory/direktori-belanja-makanan/all?page=${pageNum}`;
    console.log(`Mengambil data page ${pageNum}...`);

    await page.goto(url, { waitUntil: 'networkidle2' });

    const data = await page.evaluate(() => {
      const items = [];
      const cards = document.querySelectorAll('.item');

      cards.forEach(card => {
        const img = card.querySelector('img')?.getAttribute('src') || null;
        const lokasi = card.querySelector('p.ico_round')?.innerText.trim() || null;
        const nama = card.querySelector('h4 a')?.innerText.trim() || null;
        const tipe = card.querySelector('h4 span')?.innerText.trim() || null;

        items.push({ nama, tipe, lokasi, img });
      });

      return items;
    });

    if (data.length === 0) {
      hasData = false;
    } else {
      tenants = tenants.concat(data);
      pageNum++;
    }
  }

  fs.writeFileSync('tenant_juanda.json', JSON.stringify(tenants, null, 2), 'utf-8');
  console.log(`✅ Data berhasil disimpan ke tenant_juanda.json (${tenants.length} tenant ditemukan)`);

  await browser.close();
})();
