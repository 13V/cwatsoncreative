// Photo viewer on a phone: opens with a counter, moves on, closes.
module.exports = async ({ browser: b, base, ok, watch }) => {
  {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/gallery.html`, { waitUntil: 'networkidle' });
    await p.tap('#weddings .masonry a >> nth=0');
    const img = 'dialog.lightbox .lb-figure img';
    await p.waitForFunction(s => { const i = document.querySelector(s); return i.complete && i.naturalWidth > 0; }, img);
    ok((await p.textContent('.lb-count')).trim() === '01 / 23', 'viewer opens with the counter');
    await p.keyboard.press('ArrowRight'); await p.waitForTimeout(150);
    ok((await p.textContent('.lb-count')).trim() === '02 / 23', 'viewer moves on');
    await p.keyboard.press('Escape'); await p.waitForTimeout(200);
    ok(!(await p.isVisible('dialog.lightbox')), 'viewer closes');
    await ctx.close();
  }
};
