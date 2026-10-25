// Photo windows hold still and fade to black and white where supported; still and in colour with reduced motion.
module.exports = async ({ browser: b, base, ok, watch }) => {
  {
    const p = await b.newPage({ viewport: { width: 1440, height: 900 } }); watch(p);
    await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
    const at = async y => { await p.evaluate(y => window.scrollTo({ top: y, behavior: 'instant' }), y); await p.waitForTimeout(200);
      return p.$eval('.window--hero', w => ({ photo: Math.round(w.querySelector('.window-photos').getBoundingClientRect().top), win: Math.round(w.getBoundingClientRect().top), filter: getComputedStyle(w.querySelector('img')).filter })); };
    const a = await at(0), c = await at(500);
    ok(a.photo === 0 && c.photo === 0 && c.win < 0, `hero photos hold still while the page scrolls (window moved ${a.win} → ${c.win}, photos stay at ${c.photo})`);
    ok(/grayscale\(0?\.[3-9]|grayscale\(1\)/.test(c.filter) && /^none$|grayscale\(0\)/.test(a.filter), `hero fades to black and white (${a.filter} → ${c.filter})`);
    await p.close();
    const still = await b.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
    const q = await still.newPage(); watch(q);
    await q.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
    await q.evaluate(() => window.scrollTo({ top: 500, behavior: 'instant' })); await q.waitForTimeout(200);
    const r = await q.$eval('.window--hero', w => ({ photo: Math.round(w.querySelector('.window-photos').getBoundingClientRect().top), win: Math.round(w.getBoundingClientRect().top), filter: getComputedStyle(w.querySelector('img')).filter }));
    ok(r.photo === r.win && r.filter === 'none', 'with reduced motion the photos are simply still and in colour');
    await still.close();
  }
};
