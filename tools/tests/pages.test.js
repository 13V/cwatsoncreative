// Every page loads with its data-page, one h1, a focusable main and the four tabs; nothing links to retired pages;
// only the Kind words holding page is kept out of search; the 404 works at any depth (no <base>, root-absolute URLs);
// the h1s and display lines wrap the same in the metric-matched fallbacks as in the real faces, and a late font swap
// moves nothing (no font-swap reflow).
const { PAGES } = require('./lib');
const KIND = { index: 'home' };

module.exports = async ({ browser: b, base, ok, watch }) => {
  const p = await b.newPage(); watch(p);
  for (const name of PAGES) {
    const r = await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' });
    const s = await p.evaluate(() => ({
      page: document.documentElement.dataset.page,
      h1: document.querySelectorAll('h1').length,
      main: !!document.querySelector('main#main[tabindex="-1"]') && document.querySelectorAll('main').length === 1,
      top: !!document.querySelector('header.site-header[tabindex="-1"]') && (document.querySelector('a.to-top') || {}).hash === '#top',
      skip: (document.querySelector('a.skip') || {}).hash === '#main',
      tabs: [...document.querySelectorAll('#site-nav > a')].map(a => a.textContent.trim()),
      links: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')),
      robots: [...document.querySelectorAll('meta[name="robots"]')].map(m => m.content).join(' '),
      base: [...document.querySelectorAll('.footer-base a, .footer-base button')].map(a => [a.textContent.trim(), Math.round(a.getBoundingClientRect().height),
        getComputedStyle(a).textDecorationColor]).filter(x => x[1]),
      pill: Math.round(document.querySelector('.header-cta').getBoundingClientRect().height),
    }));
    ok(r.status() === 200 && s.page === (KIND[name] || name), `${name}.html loads with data-page="${s.page}"`);
    ok(s.h1 === 1, `${name}: one h1 (${s.h1})`);
    ok(s.main && s.top && s.skip, `${name}: main#main[tabindex=-1], the header [tabindex=-1], Back to top (#top) and the skip link to #main`);
    ok(JSON.stringify(s.tabs) === JSON.stringify(['Gallery', 'Investment', 'Kind words', 'Contact']),
       `${name}: tabs are Gallery, Investment, Kind words, Contact (${s.tabs.join(', ')})`);
    ok(!s.links.some(h => /(^|\/)(portfolio|sessions|about|enquire)\.html/.test(h)), `${name}: no links to the retired pages`);
    ok(/noindex/.test(s.robots) === (name === 'kind-words'), `${name}: ${name === 'kind-words' ? 'kept out of search (holding page)' : 'indexable'}`);
    ok(s.base.length >= 3 && s.base.every(x => x[1] >= 44 && x[2] === 'rgb(195, 150, 79)') && s.pill >= 44,
       `${name}: footer base-line links are 44px targets with the Paddock underline (${s.base.map(x => x[0] + ' ' + x[1]).join(', ')}); the header pill ${s.pill}px`);
  }

  // Back to top reaches the top with and without JS (the sticky header cannot be the #top target: stuck, it is always
  // "in view", so a jump to it goes nowhere), and with JS focus lands on the header.
  for (const js of [true, false]) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: js, reducedMotion: 'reduce' });
    const q = await ctx.newPage(); watch(q);
    await q.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    await q.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight)); await q.waitForTimeout(200);
    await q.click('.to-top'); await q.waitForTimeout(400);
    const t = await q.evaluate(() => ({ y: Math.round(scrollY), focus: document.activeElement.classList.contains('site-header') }));
    ok(t.y === 0 && (t.focus || !js), `Back to top ${js ? 'with' : 'without'} JS goes to the top (y ${t.y})${js ? ' and focuses the header' : ''}`);
    await ctx.close();
  }

  // The 404 is served for missing paths at any depth: every URL on it must resolve from the site root.
  const r = await p.goto(`${base}/404.html`, { waitUntil: 'networkidle' });
  const urls = await p.evaluate(() => {
    const out = [];
    document.querySelectorAll('[href], [src], [srcset], [imagesrcset]').forEach(el => {
      for (const a of ['href', 'src']) if (el.hasAttribute(a)) out.push(el.getAttribute(a));
      for (const a of ['srcset', 'imagesrcset']) if (el.hasAttribute(a)) el.getAttribute(a).split(',').forEach(c => out.push(c.trim().split(/\s+/)[0]));
    });
    return { base: !!document.querySelector('base'), bad: out.filter(u => !/^(\/|#|https?:|mailto:)/.test(u)) };
  });
  ok(r.status() === 200 && !urls.base && !urls.bad.length, '404.html: no <base>, every href/src root-absolute' + (urls.bad.length ? ': ' + urls.bad.slice(0, 5).join(', ') : ''));
  const q = await b.newPage(); watch(q, /\/no\/such\/page$/);
  const deep = await q.goto(`${base}/no/such/page`, { waitUntil: 'networkidle' });
  const d = await q.evaluate(() => ({
    page: document.documentElement.dataset.page,
    styled: document.styleSheets.length > 0 && [...document.styleSheets].every(s => { try { return s.cssRules.length > 0; } catch (e) { return false; } }),
    skip: document.querySelector('a.skip').href === location.href.split('#')[0] + '#main',
  }));
  ok(deep.status() === 404 && d.page === '404' && d.styled && d.skip, 'a missing deep path shows the styled 404, and its skip link stays on the page');
  await q.close();
  await p.close();
  // The font swap never rewraps a heading line plan: each h1 and display line (the Home hero, statement and closing,
  // and every closing) is as tall with the fonts withheld (the metric-matched fallbacks) as with them, 320–1440.
  const ctxs = [], pages = {}, LINES = ['main h1', '.statement-line', '#closing-title'];
  for (const fb of [false, true]) {
    const ctx = await b.newContext({ reducedMotion: 'reduce' }); ctxs.push(ctx);
    if (fb) await ctx.route(/\.woff2$/, r => r.abort());
    for (const name of ['index', 'gallery', 'investment', 'kind-words', 'contact', '404']) {
      const pg = await ctx.newPage(); watch(pg, /\.woff2$/);
      await pg.goto(`${base}/${name}.html`, { waitUntil: 'load' }); await pg.evaluate(() => document.fonts.ready);
      (pages[name] = pages[name] || []).push(pg);
    }
  }
  const differ = [];
  let lines = 0;
  for (const [name, [real, fallback]] of Object.entries(pages)) {
    for (const w of [320, 375, 390, 393, 402, 412, 414, 428, 430, 600, 860, 861, 1009, 1024, 1280, 1440]) {
      const h = [];
      for (const pg of [real, fallback]) {
        await pg.setViewportSize({ width: w, height: 900 });
        h.push(await pg.evaluate(sels => sels.map(s => document.querySelector(s)).filter(Boolean)
          .map(el => [el.id || el.className || el.tagName, Math.round(el.getBoundingClientRect().height)]), LINES));
      }
      h[0].forEach(([k, v], i) => { lines++; if (!h[1][i] || Math.abs(v - h[1][i][1]) > 2) differ.push(`${name} ${w} ${k}: ${v} vs ${h[1][i] && h[1][i][1]}`); });
    }
  }
  ok(!differ.length && lines > 150, `h1s and display lines wrap the same in the fallback faces (${lines} checks, 320–1440)` + (differ.length ? ': ' + differ.join(', ') : ''));
  for (const ctx of ctxs) await ctx.close();

  // Home links into the middle of Investment (#couples from the Couples tile, #family from the text tile), where a
  // late font would move what the visitor is reading: every text block of those two sessions wraps the same in the
  // fallbacks as in the real faces on phones (375–430 at DPR 2 and 3), and so does everything above them from 390px
  // (a rewrap there moves the landing; at 375px the hero's second paragraph still differs, which scroll anchoring
  // absorbs).
  {
    const differ = [];
    let blocks = 0;
    for (const dpr of [2, 3]) {
      const seen = [];
      for (const fb of [false, true]) {
        const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: dpr, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
        if (fb) await ctx.route(/\.woff2$/, r => r.abort());
        const pg = await ctx.newPage(); watch(pg, /\.woff2$/);
        await pg.goto(`${base}/investment.html`, { waitUntil: 'load' }); await pg.evaluate(() => document.fonts.ready);
        const m = {};
        for (const w of [375, 390, 393, 402, 412, 414, 428, 430]) {
          await pg.setViewportSize({ width: w, height: 844 });
          m[w] = await pg.evaluate(above => {
            const end = document.getElementById('family').getBoundingClientRect().bottom;
            return [...document.querySelectorAll('main :is(h1, h2, h3, p, dt, dd, li)')].filter(el => el.closest('#couples, #family') || (above && el.getBoundingClientRect().bottom <= end))
              .map(el => [(el.closest('[id]') || {}).id, el.textContent.trim().replace(/\s+/g, ' ').slice(0, 32), Math.round(el.getBoundingClientRect().height)]);
          }, w >= 390);
        }
        seen.push(m);
        await ctx.close();
      }
      const [real, fallback] = seen;
      for (const w of Object.keys(real)) real[w].forEach(([id, text, h], i) => {
        blocks++;
        const f = fallback[w][i];
        if (!f || Math.abs(h - f[2]) > 2) differ.push(`${w}@${dpr} #${id} "${text}": ${h} vs ${f && f[2]}`);
      });
    }
    ok(!differ.length && blocks > 400, `#couples and #family (linked from Home), and what is above them, wrap the same in the fallback faces on phones (${blocks} blocks)` + (differ.length ? ': ' + differ.join(', ') : ''));
  }

  // A late font moves nothing: with every font held back ~1.8s, each page paints first in the fallbacks and then swaps
  // (CLS < 0.001 on all 7 pages, phones at 2x and a 1024px laptop).
  const SIZES = { 375: 812, 390: 844, 393: 852, 402: 874, 412: 915, 414: 896, 428: 926, 430: 932, 1024: 768 };
  const late = [];
  for (const [w, h] of Object.entries(SIZES)) {
    const phone = w < 861;
    const ctx = await b.newContext({ viewport: { width: +w, height: h }, deviceScaleFactor: phone ? 2 : 1, isMobile: phone, hasTouch: phone });
    await ctx.route(/\.woff2$/, r => setTimeout(() => r.continue().catch(() => {}), 1800));
    await ctx.addInitScript(() => {
      window.__cls = { total: 0, from: [] };
      new PerformanceObserver(l => l.getEntries().forEach(e => {
        if (e.hadRecentInput) return;
        window.__cls.total += e.value;
        (e.sources || []).forEach(s => window.__cls.from.push((s.node ? s.node.nodeName + '.' + ((s.node.className || (s.node.parentElement || {}).className || '') + '').split(' ')[0] : '?') + ' ' + e.value.toFixed(4)));
      })).observe({ type: 'layout-shift', buffered: true });
    });
    await Promise.all(PAGES.map(async name => {
      const pg = await ctx.newPage(); watch(pg);
      await pg.goto(`${base}/${name}.html`, { waitUntil: 'load' });
      await pg.waitForFunction(() => document.fonts.status === 'loaded' && [...document.fonts].some(f => f.family === 'Brygada 1918' && f.status === 'loaded'), null, { timeout: 20000 });
      await pg.waitForTimeout(600);
      const c = await pg.evaluate(() => window.__cls);
      if (!(c.total < .001)) late.push(`${w} ${name} ${c.total.toFixed(4)} (${c.from.slice(0, 3).join(', ')})`);
      await pg.close();
    }));
    await ctx.close();
  }
  ok(!late.length, 'fonts held back 1.8s: no layout shift when they swap in (CLS < 0.001, 7 pages at 375–430 and 1024)' + (late.length ? ': ' + late.join(' | ') : ''));
};
