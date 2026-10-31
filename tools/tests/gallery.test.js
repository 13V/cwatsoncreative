// Gallery (spec §5.2, §4.11): chapters in data order with cover-first openers, the rhythm grid exactly as
// content.rhythm() groups it (portraits pair unless none follows; groups alternate sides, the first opposite the cover;
// every portrait whole on a laptop screen), DOM order = viewer order, nothing under 220px on phones, chapter 01's cover as the LCP,
// prints that develop below the fold, the index spy, a failed photo leaving the grid and the viewer, the closing.
const { execFileSync } = require('child_process');
const path = require('path');
const { context, scrollThrough, scrollTo, PHONE, DESKTOP } = require('./lib');

// The data the page is built from (tools/site/content.py), so the counts and groups are checked against it.
const DATA = JSON.parse(execFileSync('python3', ['-c', `
import json, sys; sys.path.insert(0, sys.argv[1])
from content import GALLERY_CHAPTERS, PHOTOS, CLOSING, rhythm, plain
print(json.dumps({'chapters': [[c[0], c[1], [PHOTOS[k][0] for k in c[3]]] for c in GALLERY_CHAPTERS], 'rhythm': rhythm(),
                  'closing': plain(CLOSING['gallery'])}))`, path.join(__dirname, '..', 'site')]).toString());
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

module.exports = async ({ browser: b, base, ok, watch }) => {
  const url = `${base}/gallery.html`;
  {   // structure, from the markup
    const ctx = await context(b, 'motion', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(url, { waitUntil: 'networkidle' });
    const s = await p.evaluate(() => {
      const bar = document.querySelector('nav.index-bar');
      return {
        label: bar && bar.getAttribute('aria-label'),
        index: [...document.querySelectorAll('.index-bar a')].map(a => [a.getAttribute('href'), !!a.querySelector('sup')]),
        wrapped: [...document.querySelectorAll('#weddings > section.chapter.sec--standard')].map(c => c.id),
        chapters: [...document.querySelectorAll('section.chapter')].map(c => ({
          id: c.id, title: c.querySelector(`h2#${c.id}-title`)?.textContent, num: c.querySelector('.eyebrow--num')?.textContent,
          first: c.querySelector('.ph-link').classList.contains('chapter-cover'),
          links: [...c.querySelectorAll('.ph-link')].map(a => a.getAttribute('href')),
          groups: [...c.querySelectorAll('.rg')].map(g => g.className.replace(/^rg rg--/, '')),
          grouped: [...c.querySelectorAll('.rg')].every(g => [...g.children].every(a => a.matches('a.ph-link[data-viewer]') && a.children.length === 1 && a.firstElementChild.matches('figure.ph.ph--tray'))),
        })),
        order: [...document.querySelectorAll('[data-viewer]')].map(a => +a.dataset.index),
        closing: document.querySelector('#closing-title')?.textContent.replace(/\s+/g, ' ').trim(),
        desc: ['meta[name="description"]', 'meta[property="og:description"]'].map(s => document.querySelector(s)?.content),
        lead: document.querySelector('.page-head .lead')?.textContent, extras: document.querySelectorAll('main > section.chapter').length,
        old: document.querySelectorAll('blockquote, .duo, .chips, .masonry, .lightbox, .strip, .insta-strip, .words, .sheet').length,
        lcp: (() => { const i = document.querySelector('img[data-lcp]'); return i && { cover: !!i.closest('#getting-ready .chapter-cover'),
          high: i.getAttribute('fetchpriority'), loading: i.getAttribute('loading'), tray: !!i.closest('.ph--tray') }; })(),
      };
    });
    ok(s.label === 'Chapters' && same(s.index, DATA.chapters.map(c => ['#' + c[0], false])),
       `index bar "Chapters" links every chapter, with no counts (${s.index.map(x => x.join(' ')).join(', ')})`);
    ok(same(s.wrapped, DATA.chapters.map(c => c[0])), `div#weddings wraps the four chapters in data order (${s.wrapped.join(', ')})`);
    ok(s.chapters.every((c, i) => c.title === DATA.chapters[i][1] && !c.num),
       'each opener: the chapter title, with no number or photo count');
    ok(s.chapters.every(c => c.first) && s.chapters.every((c, i) => same(c.links, DATA.chapters[i][2])),
       'cover first in every chapter, then its photos in data order');
    ok(same(s.chapters.map(c => c.groups), DATA.rhythm) && s.chapters.every(c => c.grouped),
       `each chapter's .rg groups equal content.rhythm() (${s.chapters.map(c => c.groups.join(' ')).join(' · ')})`);
    // the rule, read from the page: a portrait stands alone only when no portrait follows it; portrait groups
    // alternate sides; each chapter's first group leads on the side opposite its cover
    const rule = await p.evaluate(() => [...document.querySelectorAll('section.chapter')].map(c => {
      const mid = c.querySelector('.wrap').getBoundingClientRect(), half = x => x < mid.left + mid.width / 2 ? 'l' : 'r';
      const cover = c.querySelector('.chapter-cover').getBoundingClientRect(), groups = [...c.querySelectorAll('.rg')];
      const portrait = g => /rg--(pair|solo)/.test(g.className), sides = groups.filter(portrait).map(g => g.className.slice(-1));
      const lead = groups[0] && [...groups[0].children].map(a => a.getBoundingClientRect()).sort((x, y) => y.width - x.width)[0];   // the larger photo
      return { lone: groups.some((g, i) => /solo/.test(g.className) && groups[i + 1] && portrait(groups[i + 1])),
        alternate: sides.every((x, i) => !i || x !== sides[i - 1]),
        opposite: !lead || half(cover.left + cover.width / 2) !== half(lead.left + lead.width / 2) };
    }));
    ok(rule.every(r => !r.lone && r.alternate && r.opposite),
       `rhythm rule: no portrait alone before another, sides alternate, the first group opposite the cover (${JSON.stringify(rule)})`);
    ok(same(s.order, s.order.map((_, i) => i)) && s.order.length === 23, 'viewer order (data-index) equals DOM order, 23 photos');
    ok(s.closing === DATA.closing, `the closing shows the Gallery line ("${s.closing}")`);
    ok(s.old === 0, 'no blockquote, duo, chips, masonry, old lightbox, strip or sheet');
    ok(s.extras || (s.lead.startsWith('Weddings from around Adelaide.') && s.desc.every(d => d === 'Wedding photography from around Adelaide by Selah Stories.')),
       `the description, like the lead, names only the galleries on the page (${s.desc[0]})`);
    ok(s.lcp && s.lcp.cover && s.lcp.high === 'high' && s.lcp.loading === null && !s.lcp.tray,
       'chapter 01 cover is the LCP photo: eager, fetchpriority high, never a tray print');
    await ctx.close();
  }
  for (const vp of [PHONE, DESKTOP]) {   // the browser agrees the cover is the LCP; nothing on it is armed or moved
    const ctx = await context(b, 'motion', vp);
    await ctx.addInitScript(() => {
      window.__lcp = [];
      new PerformanceObserver(l => l.getEntries().forEach(e => window.__lcp.push(e.element))).observe({ type: 'largest-contentful-paint', buffered: true });
    });
    const p = await ctx.newPage(); watch(p);
    await p.goto(url, { waitUntil: 'networkidle' });
    await p.waitForTimeout(300);
    const r = await p.evaluate(() => {
      const el = window.__lcp[window.__lcp.length - 1], f = document.querySelector('#getting-ready .chapter-cover .ph'), img = f.querySelector('img'),
        box = f.getBoundingClientRect(), cs = getComputedStyle(img);
      return { lcp: el && el.matches('img[data-lcp]'), cls: f.className, op: cs.opacity, tf: cs.transform,
        top: box.top, w: box.width, h: box.height, vh: innerHeight };
    });
    ok(r.lcp && !/is-armed/.test(r.cls) && r.op === '1' && r.tf === 'none', `${vp.viewport.width}: the LCP element is chapter 01's cover, never armed, faded or moved`);
    if (vp === PHONE) {
      const shown = (r.vh - r.top) / r.h;
      ok(r.top + r.w / 2 <= r.vh && shown >= .5, `390x844: chapter 01's whole arch and ${Math.round(shown * 100)}% of its photo are in the first screen (top ${Math.round(r.top)})`);
    }
    await ctx.close();
  }
  for (const vp of [PHONE, DESKTOP]) {   // every photo's box is reserved before its file arrives (CLS 0 by construction)
    const ctx = await context(b, 'motion', vp);
    const p = await ctx.newPage(); watch(p);
    await p.route(/\/images\/weddings\//, () => {});   // the photos never arrive
    await p.goto(url, { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(300);
    const bad = await p.$$eval('.ph-link .ph', fs => fs.filter(f => { const r = f.getBoundingClientRect(), i = f.querySelector('img');
      return r.width < 200 || Math.abs(r.height / r.width - i.getAttribute('height') / i.getAttribute('width')) > .01; }).map(f => f.closest('a').getAttribute('href')));
    ok(!bad.length, `${vp.viewport.width}: every cover and grid photo holds its full box before its file loads` + (bad.length ? ': ' + bad.join(', ') : ''));
    await ctx.close();
  }
  for (const [w, h] of [[1440, 900], [1366, 768], [1280, 720], [1920, 1080]]) {   // every grid portrait whole on screen
    const ctx = await b.newContext({ viewport: { width: w, height: h } });
    const p = await ctx.newPage(); watch(p);
    await p.goto(url, { waitUntil: 'networkidle' });
    const r = await p.evaluate(() => {
      const room = innerHeight - document.querySelector('.site-header').offsetHeight - document.querySelector('.index-bar').offsetHeight;
      const tall = [...document.querySelectorAll('.rg:not(.rg--wide, .rg--land-pair) .ph')].map(f => f.getBoundingClientRect().height);
      return { room, max: Math.round(Math.max(...tall)), min: Math.round(Math.min(...tall)) };
    });
    ok(r.max <= r.room && r.min >= 300, `${w}x${h}: grid portraits ${r.min}–${r.max}px tall, all within the ${r.room}px under the header and index bar`);
    await ctx.close();
  }
  for (const w of [320, 375, 390, 430]) {   // nothing under 220px, nothing past the edge; wide and land-pair bleed
    const ctx = await b.newContext({ viewport: { width: w, height: 800 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const p = await ctx.newPage(); watch(p);
    await p.goto(url, { waitUntil: 'networkidle' });
    const r = await p.evaluate(() => {
      const vw = document.documentElement.clientWidth, imgs = [...document.querySelectorAll('.rg .ph')].map(f => f.getBoundingClientRect());
      const bleed = [...document.querySelectorAll('.rg--wide .ph, .rg--land-pair .ph')].every(f => { const b = f.getBoundingClientRect(); return Math.abs(b.left) < 1 && Math.abs(b.right - vw) < 1; });
      return { narrow: Math.min(...imgs.map(b => b.width)), over: document.documentElement.scrollWidth - vw, bleed };
    });
    ok(r.narrow >= 220 && r.over <= 0 && r.bleed, `${w}px: narrowest grid photo ${Math.round(r.narrow)}px (>= 220), no sideways scroll, wide rows full-bleed`);
    await ctx.close();
  }
  {   // prints below the fold arm, develop in reading order and end done
    const ctx = await context(b, 'motion', PHONE);
    await ctx.addInitScript(() => {
      window.__dev = [];
      new MutationObserver(ms => ms.forEach(m => { if (m.target.classList.contains('is-developing') && !window.__dev.includes(m.target)) window.__dev.push(m.target); }))
        .observe(document, { subtree: true, attributes: true, attributeFilter: ['class'] });
    });
    const p = await ctx.newPage(); watch(p);
    await p.goto(url, { waitUntil: 'networkidle' });
    await p.waitForTimeout(300);
    const armed = await p.$$eval('.rg .ph', fs => fs.map(f => f.getBoundingClientRect().top > innerHeight ? f.classList.contains('is-armed') : f.classList.contains('is-done')));
    await scrollThrough(p, { step: 300, pause: 120, settle: 2500 });
    const end = await p.evaluate(() => ({
      done: [...document.querySelectorAll('.rg .ph')].every(f => f.classList.contains('is-done') && !f.classList.contains('is-armed')),
      developed: window.__dev.length, all: document.querySelectorAll('.rg .ph').length,
      order: window.__dev.map(f => [...document.querySelectorAll('.rg .ph')].indexOf(f)),
    }));
    ok(armed.every(Boolean), 'grid prints below the fold wait armed (those on screen at load are done)');
    ok(end.done && end.developed >= end.all - 3, `every grid print developed and ended .is-done (${end.developed} of ${end.all} developed)`);
    ok(same(end.order, [...end.order].sort((x, y) => x - y)), 'prints develop in reading order');
    await ctx.close();
  }
  for (const vp of [PHONE, DESKTOP]) {   // the index spy follows the chapters; the brush only under the current link
    const ctx = await context(b, 'motion', vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(url, { waitUntil: 'networkidle' });
    const seen = [];
    for (const [id] of DATA.chapters) {
      await p.evaluate(id => { const c = document.getElementById(id); window.scrollTo({ top: c.getBoundingClientRect().top + scrollY - 140, behavior: 'instant' }); }, id);
      await p.waitForTimeout(400);
      seen.push(await p.evaluate(() => {
        const cur = [...document.querySelectorAll('.index a[aria-current="true"]')], brushes = [...document.querySelectorAll('.index .brush')].filter(b => getComputedStyle(b).opacity !== '0');
        return cur.length === 1 && brushes.length === 1 && cur[0].contains(brushes[0]) ? cur[0].getAttribute('href') : `x${cur.length}/${brushes.length}`;
      }));
    }
    ok(same(seen, DATA.chapters.map(c => '#' + c[0])), `${vp.viewport.width}: the spy marks each chapter in turn, one brush (${seen.join(', ')})`);
    await ctx.close();
  }
  {   // a photo whose file fails leaves the grid and the viewer
    const ctx = await context(b, 'motion', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.route(/castle-laugh/, r => r.abort());
    await p.goto(url, { waitUntil: 'networkidle' });
    await p.evaluate(() => document.querySelectorAll('img[loading="lazy"]').forEach(i => { i.loading = 'eager'; }));
    await p.waitForFunction(() => document.querySelector('a[href$="castle-laugh.jpg"] .ph').classList.contains('is-missing'), null, { timeout: 10000 });
    const gone = await p.$eval('a[href$="castle-laugh.jpg"]', a => getComputedStyle(a).display === 'none');
    await p.click('#getting-ready .chapter-cover');
    await p.waitForTimeout(700);
    const count = (await p.textContent('.viewer-count')).replace(/\s+/g, ' ').trim();
    ok(gone && count === '01 / 22', `a failed photo leaves the grid and the viewer (${count})`);
    await p.keyboard.press('Escape');
    await ctx.close();
  }
  for (const vp of [PHONE, DESKTOP]) {   // without JS: every photo shows and opens its full JPEG
    const ctx = await context(b, 'nojs', vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(url, { waitUntil: 'networkidle' });
    await scrollThrough(p, { step: 500, pause: 60, settle: 800 });
    const r = await p.evaluate(() => ({
      hidden: [...document.querySelectorAll('.ph-link img')].filter(i => !i.complete || !i.naturalWidth || getComputedStyle(i).visibility !== 'visible' || getComputedStyle(i).opacity !== '1').length,
      hrefs: [...document.querySelectorAll('.ph-link')].every(a => /^images\/weddings\/[a-z-]+\.jpg$/.test(a.getAttribute('href'))),
    }));
    const first = await p.getAttribute('.rg .ph-link', 'href');
    await Promise.all([p.waitForURL(u => u.pathname.endsWith(first.replace(/^.*\//, ''))), p.click('.rg .ph-link')]);
    ok(!r.hidden && r.hrefs, `no JS, ${vp.viewport.width}: every photo shows and opens its full JPEG (${first})`);
    await ctx.close();
  }
};
