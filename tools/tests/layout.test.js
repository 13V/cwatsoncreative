// Every page fits every phone size with no sideways scroll, every photo shows, and tap targets are at least 44px.
const pages = ['index', 'gallery', 'investment', 'kind-words', 'contact', 'privacy', '404'];
const sizes = [[320, 640], [360, 780], [375, 812], [390, 844], [414, 896], [430, 932], [844, 390], [932, 430]];
module.exports = async ({ browser: b, base, ok, watch }) => {
  for (const [w, h] of sizes) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const problems = [];
    for (const name of pages) {
      const p = await ctx.newPage(); watch(p);
      await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' });
      await p.evaluate(async () => {
        document.querySelectorAll('img[loading="lazy"]').forEach(i => { i.loading = 'eager'; });
        for (let y = 0; y < document.body.scrollHeight; y += 500) { window.scrollTo({ top: y, behavior: 'instant' }); await new Promise(r => setTimeout(r, 30)); }
        window.scrollTo({ top: 0, behavior: 'instant' });
      });
      await p.waitForFunction(() => [...document.images].every(i => i.complete), null, { timeout: 30000 });
      const r = await p.evaluate(() => {
        const vw = window.innerWidth;
        const out = { overflow: document.documentElement.scrollWidth - vw, poking: [], broken: [] };
        document.querySelectorAll('main *, header *, footer *').forEach(el => {
          const s = getComputedStyle(el);
          if (s.visibility === 'hidden' || s.display === 'none') return;
          const nav = el.closest('.site-nav');
          if (nav && !nav.classList.contains('is-open') && vw <= 860) return;
          if (el.closest('svg')) return;   // drawings may overhang inside clipped boxes
          const box = el.getBoundingClientRect();
          if (box.width && box.right > vw + 1 && !el.closest('[data-overhang]')) out.poking.push(el.tagName.toLowerCase() + '.' + [...el.classList].join('.') + ' (' + Math.round(box.right - vw) + 'px)');
        });
        document.querySelectorAll('.ph img').forEach(i => { if (!i.naturalWidth || i.closest('.ph').classList.contains('is-missing')) out.broken.push(i.getAttribute('src')); });
        return out;
      });
      if (r.overflow > 0) problems.push(`${name}: sideways scroll ${r.overflow}px`);
      if (r.poking.length) problems.push(`${name}: past the edge: ${r.poking.slice(0, 4).join(', ')}`);
      if (r.broken.length) problems.push(`${name}: photos not showing: ${r.broken.join(', ')}`);
      await p.close();
    }
    ok(!problems.length, `${w}x${h}: ` + (problems.length ? problems.join(' | ') : 'all 7 pages fit, every photo shows'));
    await ctx.close();
  }
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const small = new Map();
  for (const name of pages) {
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' });
    const found = await p.evaluate(() => {
      const list = [];
      document.querySelectorAll('a, button, summary, input, select, textarea, label.chip').forEach(el => {
        // inline links inside running text are exempt (WCAG 2.5.8), as are the closed menu, honeypot, skip link and dialogs
        if (el.closest('p, .prose, .lead, .site-nav, .hp, .skip, dialog') || el.classList.contains('skip')) return;
        const s = getComputedStyle(el);
        if (s.display === 'none' || s.visibility === 'hidden') return;
        const r = el.getBoundingClientRect();
        if (!r.width) return;
        if (r.height < 44 || r.width < 44) list.push(`${el.tagName.toLowerCase()}${el.className ? '.' + String(el.className).split(' ').join('.') : ''} "${(el.textContent || el.name || '').trim().slice(0, 22)}" ${Math.round(r.width)}x${Math.round(r.height)}`);
      });
      return list;
    });
    found.forEach(f => small.set(f.replace(/ \d+x\d+$/, ''), f));
    await p.close();
  }
  ok(small.size === 0, `tap targets of at least 44px on a 390px phone` + (small.size ? ': ' + [...small.values()].join(' | ') : ''));
  await ctx.close();
};
