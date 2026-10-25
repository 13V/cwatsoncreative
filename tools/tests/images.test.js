// Each screen loads the right photo size.
module.exports = async ({ browser: b, base, ok, watch }) => {
  for (const [label, vp, dpr, page, sel, expect] of [
    ['iPhone (3x)', [390, 844], 3, 'index', '.window--hero img', 'vineyard-sunset.webp'],
    ['older phone (2x)', [390, 844], 2, 'index', '.window--hero img', 'vineyard-sunset-1200.webp'],
    ['desktop (1x)', [1440, 900], 1, 'index', '.window--hero img', 'vineyard-sunset-800.webp'],
    ['iPhone (3x)', [390, 844], 3, 'gallery', '.masonry img', 'arch-mirror-800.webp'],
    ['desktop (1x)', [1440, 900], 1, 'gallery', '.masonry img', 'arch-mirror-480.webp'],
  ]) {
    const ctx = await b.newContext({ viewport: { width: vp[0], height: vp[1] }, deviceScaleFactor: dpr });
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/${page}.html`, { waitUntil: 'networkidle' });
    const src = await p.$eval(sel, i => i.currentSrc);
    ok(src.endsWith(expect), `${label} ${page}: loads ${src.split('/').pop()}`);
    await ctx.close();
  }
};
