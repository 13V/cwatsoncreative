// Every page loads, the tabs are right and nothing links to retired pages.
module.exports = async ({ browser: b, base, ok, watch }) => {
  {
    const p = await b.newPage(); watch(p);
    for (const name of ['index', 'gallery', 'investment', 'kind-words', 'contact', 'privacy', '404']) {
      const r = await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' });
      ok(r.status() === 200, `${name}.html loads`);
    }
    await p.goto(`${base}/index.html`);
    const nav = await p.$$eval('#site-nav a:not(.nav-instagram)', as => as.map(a => a.textContent.trim()));
    ok(JSON.stringify(nav) === JSON.stringify(['Gallery', 'Investment', 'Kind words', 'Contact']), 'tabs are Gallery, Investment, Kind words, Contact (' + nav.join(', ') + ')');
    const links = await p.$$eval('a[href]', as => as.map(a => a.getAttribute('href')));
    ok(!links.some(h => /portfolio\.html|sessions\.html|about\.html|enquire\.html/.test(h)), 'no links to the retired pages');
    await p.close();
  }
};
