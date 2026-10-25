// Home (spec §5.1, §4.4, §4.8, §4.9): section order and backgrounds; one h1 on the hero with its line plan; the hero
// photo is the LCP and nothing on it moves at load; the hero copy passes the §2.2 pixel test; the statement's line
// plan and A3 keyline; M05 opens the arch on scroll and draws the ring once; session tiles from data (photo tiles are
// doorways that develop, the rest named in one text tile); the closing's Home line; finished with no JS, Reduce
// Motion and Hold still.
const { context, scrollThrough, scrollTo, PHONE, DESKTOP } = require('./lib');

// Every session, and the photo its Home tile would show (a session without one is named in the text tile).
const SESSIONS = [['Weddings', 'images/weddings/bougainvillea-embrace.jpg'], ['Couples', 'images/weddings/field-dusk.jpg'],
  ['Family', 'images/sessions/family.jpg'], ['Maternity', 'images/sessions/maternity.jpg'], ['Newborn', 'images/sessions/newborn.jpg']];
const vp = (width, height) => ({ viewport: { width, height }, deviceScaleFactor: width < 861 ? 2 : 1, isMobile: width < 861, hasTouch: width < 861 });

// How many rendered lines a block of text takes (distinct line tops of its text).
const lineCount = (p, sel) => p.$eval(sel, el => {
  const tops = new Set(), w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) {
    const r = document.createRange(); r.selectNodeContents(n);
    [...r.getClientRects()].filter(b => b.width > 1).forEach(b => tops.add(Math.round(b.top / 4)));
  }
  return tops.size;
});

// The hero copy's glyph boxes, then the lightest pixel under each with the copy hidden (spec §2.2).
const contrast = async (p) => {
  const boxes = await p.evaluate(() => {
    const out = [];
    const add = (el, kind) => {
      const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      for (let n; (n = w.nextNode());) {
        if (!n.textContent.trim()) continue;
        const r = document.createRange(); r.selectNodeContents(n);
        [...r.getClientRects()].filter(b => b.width > 1).forEach(b => out.push({ kind, text: n.textContent.trim().slice(0, 18), x: b.left, y: b.top, w: b.width, h: b.height }));
      }
    };
    add(document.querySelector('.hero-title'), 'h1');
    document.querySelectorAll('.hero-copy .la-label, .hero-copy .scroll-cue .t-micro').forEach(el => add(el, 'label'));
    return out;
  });
  await p.addStyleTag({ content: '.hero-copy{visibility:hidden !important}' });
  await p.waitForTimeout(100);
  const png = (await p.screenshot()).toString('base64');
  return p.evaluate(async ({ png, boxes }) => {
    const bmp = await createImageBitmap(await (await fetch('data:image/png;base64,' + png)).blob());
    const c = new OffscreenCanvas(bmp.width, bmp.height), g = c.getContext('2d');
    g.drawImage(bmp, 0, 0);
    const k = bmp.width / innerWidth;
    const lum = (r, gr, b) => [r, gr, b].map(v => { v /= 255; return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; })
      .reduce((s, v, i) => s + v * [.2126, .7152, .0722][i], 0);
    const mist = lum(0xFB, 0xF8, 0xF2);
    return boxes.map(b => {
      const x = Math.max(0, Math.floor(b.x * k)), y = Math.max(0, Math.floor(b.y * k));
      const w = Math.min(bmp.width - x, Math.ceil(b.w * k)), h = Math.min(bmp.height - y, Math.ceil(b.h * k));
      const d = g.getImageData(x, y, w, h).data;
      let max = 0;
      for (let i = 0; i < d.length; i += 4) max = Math.max(max, lum(d[i], d[i + 1], d[i + 2]));
      return { ...b, ratio: +((mist + .05) / (max + .05)).toFixed(2) };
    });
  }, { png, boxes });
};

module.exports = async ({ browser: b, base, ok, watch }) => {
  // Structure, at 1440 with motion (the default visit).
  {
    const ctx = await context(b, 'motion', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
    const s = await p.evaluate(() => {
      const rgb = c => { const d = document.createElement('i'); d.style.color = c; document.body.append(d); const v = getComputedStyle(d).color; d.remove(); return v; };
      const els = [...document.querySelector('main').children];
      return {
        order: els.map(el => (el.className.match(/\b(window--hero|statement|window--a|sessions|window--b|interlude|sheet|closing)\b/) || [el.className])[0]),
        bg: els.map(el => getComputedStyle(el).backgroundColor), above: els.map(el => el.style.getPropertyValue('--above') ? rgb(getComputedStyle(el).getPropertyValue('--above').trim()) : null),
        count: els.map(el => el.dataset.count || null), panel: els.map(el => el.classList.contains('panel')),
        paper: rgb('var(--paper)'), lime: rgb('var(--limestone)'),
        h1: [...document.querySelectorAll('h1')].map(h => ({ inHero: !!h.closest('.window--hero'), id: h.id, cls: h.className, html: h.innerHTML, text: h.textContent })),
        labelled: document.querySelector('.window--hero').getAttribute('aria-labelledby'),
        cue: (a => a && { href: a.getAttribute('href'), label: a.getAttribute('aria-label') })(document.querySelector('.hero-copy a.scroll-cue')),
        link: (a => a && { href: a.getAttribute('href'), text: a.textContent.trim(), light: a.classList.contains('link-arrow--light') })(document.querySelector('.hero-meta .link-arrow')),
        ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map(x => { try { return JSON.parse(x.textContent)['@type']; } catch (e) { return 'bad'; } }),
        retired: ['.words', 'blockquote', '.duo', '.quote', '.intro-grid', '.tile-photo', '.strip', '.center-title'].filter(q => document.querySelector(q)),
        closing: (h => h && h.textContent.replace(/\s+/g, ' ').trim())(document.querySelector('#closing-title')),
      };
    });
    const want = ['window--hero', 'statement', 'window--a', 'sessions', 'window--b', 'sheet', 'closing'];
    ok(JSON.stringify(s.order) === JSON.stringify(want), `Home sections in order: ${s.order.join(' → ')}`);
    const [P, L] = [s.paper, s.lime];
    ok(s.bg[1] === P && s.bg[3] === L && s.bg[5] === P && s.bg[6] === P, 'statement Paper, sessions Limestone, sheet and closing Paper');
    ok(s.above[2] === P && s.count[2] === '3' && s.above[4] === L && s.count[4] === '2', `window A --above Paper with 3 photos, window B --above Limestone with 2 (${s.above[2]} ${s.count[2]} / ${s.above[4]} ${s.count[4]})`);
    ok(s.panel[1] && s.panel[3] && s.panel[5], 'every section after a window is a .panel');
    const h = s.h1[0] || {};
    ok(s.h1.length === 1 && h.inHero && h.id === 'hero-title' && /\bt-display\b/.test(h.cls) && s.labelled === 'hero-title', 'one h1, on the hero (h1#hero-title.t-display labels the hero)');
    ok(/^Photographs that feel<br> like a <em>Sunday afternoon\.<\/em>$/.test(h.html), `the h1 follows its line plan (${h.html})`);
    ok(s.cue && s.cue.href === '#statement' && s.cue.label === 'Scroll to read more' && s.link && s.link.href === 'contact.html' && s.link.text === 'Check my dates' && s.link.light,
       'hero: "Check my dates" (light) and the scroll cue to #statement');
    ok(s.ld.includes('ProfessionalService'), 'JSON-LD on Home');
    ok(!s.retired.length, 'no quote band, intro block, duo, words, blockquote or old strip' + (s.retired.length ? ': ' + s.retired.join(', ') : ''));
    ok(s.closing === 'You bring your people. I’ll look after the light.', `the closing shows the Home line (${s.closing})`);
    await ctx.close();
  }

  // The LCP photo: vineyard-sunset, preloaded, high priority, never lazy; nothing on the hero moves, fades, clips or
  // filters at load; the desktop-only photo is never fetched on a phone.
  for (const v of [PHONE, DESKTOP]) {
    const ctx = await context(b, 'motion', v);
    const p = await ctx.newPage(); watch(p);
    const asked = [];
    p.on('request', r => asked.push(r.url()));
    await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
    const r = await p.evaluate(() => {
      const img = document.querySelector('img[data-lcp]'), hero = document.querySelector('.window--hero');
      const pre = document.querySelector('link[rel="preload"][as="image"]');
      const bad = [];
      for (let el = img; el && el !== hero.parentElement; el = el.parentElement) {
        const cs = getComputedStyle(el);
        if (el === img && cs.transform !== 'none') bad.push('transform');
        if (cs.filter !== 'none' || cs.clipPath !== 'none' || +cs.opacity < 1) bad.push(el.tagName + ' ' + cs.filter + ' ' + cs.clipPath + ' ' + cs.opacity);
      }
      const ir = img.getBoundingClientRect(), ar = img.closest('.ph').getBoundingClientRect();
      const moving = document.getAnimations().filter(a => a.timeline === document.timeline && a.playState === 'running' &&
        a.effect && a.effect.target && a.effect.target.closest && a.effect.target.closest('.window--hero'));
      return { src: img.getAttribute('src'), pri: img.getAttribute('fetchpriority'), lazy: img.hasAttribute('loading'), first: hero.querySelector('img') === img,
        pre: pre && pre.getAttribute('imagesrcset') || '', preFirst: document.head.firstElementChild.nextElementSibling === pre || [...document.head.querySelectorAll('link')][0] === pre,
        bad, covers: ir.left <= ar.left + 1 && ir.right >= ar.right - 1 && ir.top <= ar.top + 1 && ir.bottom >= ar.bottom - 1, moving: moving.length };
    });
    const w = v.viewport.width;
    ok(/vineyard-sunset\.jpg$/.test(r.src) && r.pri === 'high' && !r.lazy && r.first, `${w}: the LCP photo is vineyard-sunset, fetchpriority=high, not lazy`);
    ok(/vineyard-sunset/.test(r.pre) && r.preFirst, `${w}: the hero photo is preloaded first in <head>`);
    ok(!r.bad.length && r.covers && !r.moving, `${w}: at load the hero photo has no transform, filter, clip or fade, fills its window, and nothing on the hero moves` + (r.bad.length ? ': ' + r.bad.join(', ') : '') + (r.moving ? ` (${r.moving} running)` : ''));
    if (w < 861) ok(!asked.some(u => /jaguar-flare/.test(u)), '390: jaguar-flare is never requested on a phone');
    await ctx.close();
  }

  // The §2.2 pixel test: Mist text against the lightest pixel under it, copy hidden. Links and labels 4.5:1, h1 3:1.
  for (const state of ['motion', 'reduced']) {
    for (const [w, h] of [[390, 844], [375, 667], [1440, 900], [1280, 720]]) {
      const ctx = await context(b, state, vp(w, h));
      const p = await ctx.newPage(); watch(p);
      await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
      await p.evaluate(() => document.fonts.ready);
      await p.waitForFunction(() => { const i = document.querySelector('img[data-lcp]'); return i.complete && i.naturalWidth; });
      await p.waitForTimeout(300);
      const res = await contrast(p);
      const fails = res.filter(x => x.ratio < (x.kind === 'h1' ? 3 : 4.5));
      const min = k => Math.min(...res.filter(x => x.kind === k).map(x => x.ratio));
      ok(res.length >= 4 && !fails.length, `${state} ${w}x${h}: hero copy contrast holds (h1 min ${min('h1')}:1, labels min ${min('label')}:1)` +
        (fails.length ? ': ' + fails.map(f => `"${f.text}" ${f.ratio}`).join(', ') : ''));
      await ctx.close();
    }
  }

  // Line plans and clipping: the statement is 3 lines below 861px and 2 from 861px; the h1 2 lines; the closing 4 and 2.
  {
    const problems = [];
    for (const [w, h] of [[320, 640], [375, 667], [390, 844], [430, 932], [861, 900], [1280, 720], [1440, 900]]) {
      const ctx = await context(b, 'reduced', vp(w, h));
      const p = await ctx.newPage(); watch(p);
      await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
      const n = { h1: await lineCount(p, '.hero-title'), st: await lineCount(p, '.statement-line'), cl: await lineCount(p, '#closing-title') };
      const want = { h1: 2, st: w < 861 ? 3 : 2, cl: w < 861 ? 4 : 2 };
      for (const k of Object.keys(want)) if (n[k] !== want[k]) problems.push(`${w}: ${k} ${n[k]} lines (want ${want[k]})`);
      const clipped = await p.evaluate(() => [...document.querySelectorAll('main :is(h1, h2, .t-display-xl, .tile-name, .tile-words)')].filter(el => {
        const r = el.getBoundingClientRect();
        return el.scrollWidth > el.clientWidth + 1 || r.left < -1 || r.right > innerWidth + 1;
      }).map(el => el.className || el.tagName));
      if (clipped.length) problems.push(`${w}: clipped or overflowing: ${clipped.join(', ')}`);
      const hero = await p.evaluate(() => { const c = document.querySelector('.hero-copy').getBoundingClientRect(), hr = document.querySelector('.window--hero').getBoundingClientRect(); return c.top >= hr.top && c.bottom <= hr.bottom && c.left >= hr.left; });
      if (!hero) problems.push(`${w}: hero copy outside the hero`);
      await ctx.close();
    }
    ok(!problems.length, 'line plans hold at 320–1440 (h1 2 lines, statement 3/2, closing 4/2), nothing clipped' + (problems.length ? ': ' + problems.join(' | ') : ''));
  }

  // Tiles: one photo tile per session with a photo (a doorway that develops), the rest named in one text tile.
  {
    const ctx = await context(b, 'motion', PHONE);
    const have = {};
    for (const [name, file] of SESSIONS) have[name] = (await ctx.request.head(`${base}/${file}`)).ok();
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
    const t = await p.evaluate(() => ({
      photo: [...document.querySelectorAll('.tiles a.tile:not(.tile--words)')].map(a => ({
        name: a.querySelector('.tile-name').textContent, door: a.hasAttribute('data-door'), frame: !!a.querySelector('figure.ph.frame--arch.ph--tray[data-door-frame]'),
        alt: a.querySelector('img').getAttribute('alt') })),
      words: [...document.querySelectorAll('.tiles a.tile--words')].map(a => ({ names: a.querySelector('.tile-words').textContent.split(/\s+/).filter(Boolean),
        door: a.hasAttribute('data-door') || !!a.querySelector('[data-door-frame], img'), href: a.getAttribute('href') })),
      tray: [...document.querySelectorAll('.ph--tray')].map(f => !!f.closest('a.tile')),
      list: document.querySelector('ul.tiles') && document.querySelector('ul.tiles').getAttribute('role'),
    }));
    const pictured = SESSIONS.map(s => s[0]).filter(n => have[n]), named = SESSIONS.map(s => s[0]).filter(n => !have[n]);
    ok(JSON.stringify(t.photo.map(x => x.name)) === JSON.stringify(pictured) && t.photo.every(x => x.door && x.frame && x.alt === ''),
       `photo tiles for ${pictured.join(', ')}: a[data-door] > figure.ph--tray[data-door-frame], alt=""`);
    ok(named.length ? t.words.length === 1 && JSON.stringify(t.words[0].names) === JSON.stringify(named) && !t.words[0].door : !t.words.length,
       `one text tile naming exactly the sessions without photos (${named.join(', ')}), no doorway, no image`);
    ok(t.tray.length === t.photo.length && t.tray.every(Boolean) && t.list === 'list', '.ph--tray on the tile photos only; ul.tiles[role=list]');
    // names keep their spaces (Chromium may add one before the comma between blocks, which is not voiced)
    for (const name of ['Weddings, See the gallery', 'Couples, Engagements & proposals too', named.join(' ') + ', Sessions & pricing']) {
      const re = new RegExp('^' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(', ', '\\s*,\\s+').replace(/ /g, '\\s+') + '$');
      ok(await p.getByRole('link', { name: re }).count() === 1, `a link named "${name}"`);
    }
    ok((await p.getAttribute('a.tile:has(img[src*="bougainvillea-embrace"])', 'href')) === 'gallery.html' &&
       (await p.getAttribute('a.tile:has(img[src*="field-dusk"])', 'href')) === 'investment.html#couples', 'Weddings opens the gallery, Couples the Investment row');
    // M10: the tiles wait below the fold, then develop and finish
    const armed = await p.$$eval('.tiles .ph--tray', fs => fs.map(f => f.classList.contains('is-armed')));
    await p.$eval('.tiles', el => window.scrollTo({ top: el.getBoundingClientRect().top + scrollY - 200, behavior: 'instant' }));
    await p.waitForTimeout(3200);
    const done = await p.$$eval('.tiles .ph--tray', fs => fs.map(f => f.classList.contains('is-done')));
    ok(armed.length && armed.every(Boolean) && done.every(Boolean), `tile photos wait below the fold and develop on arrival (${armed} → ${done})`);
    await ctx.close();
  }

  // M05: the slit opens and the photo settles as the frame scrolls in; the ring draws once the frame is seen.
  for (const v of [PHONE, DESKTOP]) {
    const ctx = await context(b, 'motion', v);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
    const look = () => p.$eval('.statement .frame', f => ({ clip: getComputedStyle(f.querySelector('.frame--arch')).clipPath,
      scale: getComputedStyle(f.querySelector('picture')).transform, cls: f.getAttribute('class'),
      ring: parseFloat(getComputedStyle(f.querySelector('.frame-line path')).strokeDashoffset) }));
    const top = await p.$eval('.statement .frame', f => f.getBoundingClientRect().top + scrollY);
    const vh = v.viewport.height;
    await scrollTo(p, top - vh + 20); await p.waitForTimeout(250);
    const a = await look();
    await scrollTo(p, top - 80); await p.waitForTimeout(1500);
    const c = await look();
    const w = v.viewport.width;
    ok(/inset\((0px )?(0px )?33%/.test(a.clip) && /matrix\(1\.0[3-6]/.test(a.scale) && /is-armed/.test(a.cls) && a.ring > 1,
       `${w}: M05 starts as a slit with the photo at ~1.06 and the ring hidden (${a.clip}; ${a.scale})`);
    ok(/inset\(0px (0% )?round/.test(c.clip) && /none|matrix\(1, 0, 0, 1/.test(c.scale) && /is-drawn/.test(c.cls) && Math.abs(c.ring) < .001,
       `${w}: M05 ends open at 1× with the ring drawn (${c.clip}; ${c.scale}; ${c.cls})`);
    await ctx.close();
  }

  // Finished frames: no JS, Reduce Motion, Hold still: statement open with its ring drawn, tiles in colour, all visible.
  for (const state of ['nojs', 'reduced', 'still']) {
    for (const v of [PHONE, DESKTOP]) {
      const ctx = await context(b, state, v);
      const p = await ctx.newPage(); watch(p);
      await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
      await scrollThrough(p);
      await p.$eval('.statement .frame', el => el.scrollIntoView({ block: 'center', behavior: 'instant' }));
      await p.waitForTimeout(150);
      const f = await p.evaluate(() => {
        const fr = document.querySelector('.statement .frame');
        const tiles = [...document.querySelectorAll('.tiles img')].map(i => getComputedStyle(i).filter + '/' + getComputedStyle(i).transform);
        return { clip: getComputedStyle(fr.querySelector('.frame--arch')).clipPath, scale: getComputedStyle(fr.querySelector('picture')).transform,
          ring: parseFloat(getComputedStyle(fr.querySelector('.frame-line path')).strokeDashoffset), keyline: !!fr.querySelector('svg.frame-line path[pathLength]'),
          tiles, veils: [...document.querySelectorAll('.tiles .ph--tray')].map(x => getComputedStyle(x, '::after').content) };
      });
      ok(f.keyline && Math.abs(f.ring) < .001 && /^none$|inset\(0px (0% )?round/.test(f.clip) && /^none$|^matrix\(1, 0, 0, 1, 0, 0\)$/.test(f.scale) && f.tiles.every(x => x === 'none/none') && f.veils.every(x => x === 'none'),
         `${state} ${v.viewport.width}: statement open with its A3 ring drawn, tiles in colour with no veil (${f.clip}; ${f.scale}; ${f.tiles.join(' ')})`);
      await ctx.close();
    }
  }
};
