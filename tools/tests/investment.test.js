// Investment: session cards, enquire links, prices and the wedding packages match her sheet.
module.exports = async ({ browser: b, base, ok, watch }) => {
  {
    const p = await b.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    const cards = await p.$$eval('.package', ps => ps.map(x => x.id + (x.classList.contains('package--text') ? ':text' : ':photo')));
    ok(JSON.stringify(cards) === JSON.stringify(['weddings:photo', 'couples:photo', 'family:text', 'maternity:text', 'newborn:text']),
       'sessions with photos get photo cards, the rest wait as text (' + cards.join(', ') + ')');
    ok((await p.getAttribute('#maternity .link-arrow', 'href')) === 'contact.html?session=Maternity', 'each session links to the form with itself chosen');
    const prices = await p.$$eval('.package', ps => ps.map(x => x.id + ' ' + x.querySelector('.package-price').textContent));
    ok(JSON.stringify(prices) === JSON.stringify(['weddings From $1,700', 'couples $350', 'family $400', 'maternity $350', 'newborn $350']),
       'prices show on each session (' + prices.join(', ') + ')');
    const tiers = await p.$$eval('.tier', ts => ts.map(t => t.querySelector('.tier-name').textContent + ' ' + t.querySelector('.tier-hours').textContent + ' ' + t.querySelector('.tier-price').textContent));
    ok(JSON.stringify(tiers) === JSON.stringify(['Basic Up to 4 hours $1,700', 'Standard Up to 6 hours $2,100', 'Premium Up to 8 hours $2,500', 'Deluxe Up to 10 hours $2,900', 'Ultimate Up to 12 hours $3,300']),
       'wedding packages match her sheet (' + tiers.join('; ') + ')');
    await p.close();
  }
};
