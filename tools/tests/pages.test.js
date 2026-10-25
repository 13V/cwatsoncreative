// Every page loads with its data-page, one h1, a focusable main and the four tabs; nothing links to retired pages;
// only the Kind words holding page is kept out of search; the 404 works at any depth (no <base>, root-absolute URLs);
// the h1s that fill their measure wrap the same in the metric-matched fallback as in the real face (no font-swap reflow).
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
  // the font swap never rewraps an h1: its height with the fonts withheld equals its height with them
  const ctxs = [], pages = {};
  for (const fb of [false, true]) {
    const ctx = await b.newContext({ reducedMotion: 'reduce' }); ctxs.push(ctx);
    if (fb) await ctx.route(/\.woff2$/, r => r.abort());
    for (const name of ['contact', 'investment', '404', 'gallery']) {
      const pg = await ctx.newPage(); watch(pg, /\.woff2$/);
      await pg.goto(`${base}/${name}.html`, { waitUntil: 'load' }); await pg.evaluate(() => document.fonts.ready);
      (pages[name] = pages[name] || []).push(pg);
    }
  }
  const differ = [];
  for (const [name, [real, fallback]] of Object.entries(pages)) {
    for (const w of [375, 390, 393, 402, 412, 414, 428, 430, 600, 860, 861, 1009, 1024, 1280, 1440]) {
      const h = [];
      for (const pg of [real, fallback]) { await pg.setViewportSize({ width: w, height: 900 }); h.push(await pg.$eval('main h1', el => Math.round(el.getBoundingClientRect().height))); }
      if (Math.abs(h[0] - h[1]) > 2) differ.push(`${name} ${w}: ${h[0]} vs ${h[1]}`);
    }
  }
  ok(!differ.length, 'Contact, Investment, 404 and Gallery h1s wrap the same with the fallback face (375–1440)' + (differ.length ? ': ' + differ.join(', ') : ''));
  for (const ctx of ctxs) await ctx.close();
};
