// Kind words (spec §6.1, §5.5, §4.13): while there are no real reviews, no review text, name, quote or review block
// reaches any page; the Kind words page is the honest holding state (out of search): her photo as the LCP, the
// exact copy, the Instagram sheet on Limestone and the Kind words closing. Contact has neither closing nor sheet.
const { PAGES, PHONE, DESKTOP } = require('./lib');
const LEAD = 'This is where couples and families share how their sessions felt. The newest sessions go up on Instagram first.';

module.exports = async ({ browser: b, base, ok, watch }) => {
  {
    const p = await b.newPage(); watch(p);
    const found = [];
    for (const name of PAGES) {
      await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' });
      const r = await p.evaluate(() => ({
        blocks: [...document.querySelectorAll('blockquote, .interlude, .story, .cite, .words, .review, q')].map(el => el.tagName.toLowerCase() + '.' + el.className),
        text: document.body.innerText,
        robots: (document.querySelector('meta[name="robots"]') || {}).content || '',
        desc: ['meta[name="description"]', 'meta[property="og:description"]'].map(s => (document.querySelector(s) || {}).content || '').join(' ') }));
      if (r.blocks.length) found.push(`${name}: ${r.blocks.join(', ')}`);
      const m = r.text.match(/will go here|placeholder|names’|Send three to six|coming soon|“[^”]{12,}”|five stars|★/i);
      if (m) found.push(`${name}: "${m[0]}"`);
      if ((r.robots === 'noindex') !== (name === 'kind-words')) found.push(`${name}: robots "${r.robots}"`);
      if (/\bsay\b|review|testimonial/i.test(r.desc)) found.push(`${name}: the link preview promises reviews ("${r.desc}")`);
    }
    ok(!found.length, 'kind words: no review text, name, quote or review block (nor a link preview promising one) on any page while there are no real reviews; noindex on Kind words only' + (found.length ? ': ' + found.join(' | ') : ''));
    await p.close();
  }
  for (const vp of [PHONE, DESKTOP]) {
    const w = vp.viewport.width;
    const ctx = await b.newContext(vp);
    await ctx.addInitScript(() => { window.__lcp = null; new PerformanceObserver(l => { const e = l.getEntries().pop(); if (e) window.__lcp = e.element; }).observe({ type: 'largest-contentful-paint', buffered: true }); });
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/kind-words.html`, { waitUntil: 'networkidle' });
    await p.waitForTimeout(500);
    const r = await p.evaluate(() => {
      const head = document.querySelector('.kw-holding'), img = head && head.querySelector('.frame img');
      const link = head && head.querySelector('a.link-arrow--external');
      const sheet = document.querySelector('.sheet');
      return {
        eyebrow: head && head.querySelector('.eyebrow').textContent, h1: document.querySelector('h1').textContent,
        h1Bottom: document.querySelector('h1').getBoundingClientRect().bottom, lead: head && head.querySelector('.lead').textContent,
        link: link && [link.textContent.trim(), link.getAttribute('href'), link.getAttribute('rel')],
        photo: img && { src: img.currentSrc.split('/').pop(), loading: img.getAttribute('loading'), prio: img.getAttribute('fetchpriority'), lcp: img.hasAttribute('data-lcp'),
          w: Math.round(img.getBoundingClientRect().width), isLcp: window.__lcp === img },
        keyline: !!head.querySelector('.frame-line, .orn'), lcps: document.querySelectorAll('[data-lcp]').length,
        sheet: sheet && sheet.classList.contains('sheet--limestone') && getComputedStyle(sheet).backgroundColor,
        order: [...document.querySelectorAll('main > section')].map(s => s.classList[0]).join(),
        closing: (document.getElementById('closing-title') || {}).textContent };
    });
    ok(r.eyebrow === 'Kind words' && r.h1 === 'From the people in the photos.' && r.lead === LEAD, `kind words ${w}: the holding head's copy is exact`);
    ok(r.link && r.link[0] === 'See the newest sessions on Instagram' && /instagram\.com\/selahstories\.adl/.test(r.link[1]) && r.link[2] === 'me',
       `kind words ${w}: the link to the newest sessions on Instagram`);
    ok(r.photo && /^jaguar-kiss(-\d+)?\.webp$/.test(r.photo.src) && r.photo.loading === null && r.photo.prio === 'high' && r.photo.lcp && r.lcps === 1 && r.photo.isLcp,
       `kind words ${w}: her photo is the LCP (eager, high priority; ${r.photo && r.photo.src})`);
    ok(!r.keyline && r.photo.w <= Math.min(w * .48, 300) + 1, `kind words ${w}: the photo has no keyline and no ornament, ${r.photo.w}px wide`);
    ok(r.sheet === 'rgb(236, 230, 219)' && r.order === 'page-head,sheet,closing' && r.closing === 'Let’s plan something lovely.',
       `kind words ${w}: holding head, the sheet on Limestone, the Kind words closing (${r.order})`);
    if (w < 861) ok(r.h1Bottom <= 844, `kind words ${w}: the title is in the first phone screen (bottom ${Math.round(r.h1Bottom)}px)`);
    await p.goto(`${base}/contact.html`, { waitUntil: 'networkidle' });
    ok(!(await p.$('.closing, .sheet')), `contact ${w}: no closing invitation and no Instagram sheet (the page is the invitation)`);
    await ctx.close();
  }
};
