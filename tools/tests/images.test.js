// Each screen loads the right photo size, on every page: for the LCP photo and every photo in the first view, at
// 390x844@3, 390x844@2 and 1440x900@1, the file chosen covers at least 90% of the pixels its box needs (object-fit:
// cover taken into account) and is at most one rung above the smallest file that would. Home's hero exactly; the
// hero's second photo (desktop only) is never fetched on a phone.
const { PAGES } = require('./lib');
const CONFIGS = [['iPhone (3x)', 390, 844, 3], ['older phone (2x)', 390, 844, 2], ['desktop (1x)', 1440, 900, 1]];
const HERO = { 3: 'vineyard-sunset.webp', 2: 'vineyard-sunset-1200.webp', 1: 'vineyard-sunset-800.webp' };

const firstView = p => p.evaluate(() => {
  const vh = innerHeight, dpr = devicePixelRatio, out = [];
  document.querySelectorAll('img').forEach(img => {
    const r = img.getBoundingClientRect(), s = getComputedStyle(img);
    const lcp = img.hasAttribute('data-lcp');
    if (!lcp && (!r.width || r.bottom <= 0 || r.top >= vh || s.visibility === 'hidden' || img.closest('[hidden], dialog:not([open])'))) return;
    const pic = img.parentElement.tagName === 'PICTURE' ? img.parentElement : null;
    const source = pic && [...pic.querySelectorAll('source')].find(x => img.currentSrc && x.srcset.includes(img.currentSrc.split('/').pop()));
    const set = (source || img).getAttribute('srcset') || '';
    const cands = set.split(',').map(c => c.trim().split(/\s+/)).filter(c => c[0]).map(([u, w]) => ({ file: u.split('/').pop(), w: parseInt(w, 10) }))
      .sort((a, b) => a.w - b.w);
    const aspect = img.naturalWidth / img.naturalHeight;
    // the source width that fills the box at this density; object-fit: cover crops the longer side
    const fit = s.objectFit === 'cover' ? Math.max(r.width, r.height * aspect) : r.width;
    out.push({ src: img.currentSrc.split('/').pop(), need: Math.round(fit * dpr), cands, lcp, w: Math.round(r.width), h: Math.round(r.height) });
  });
  return out;
});

module.exports = async ({ browser: b, base, ok, watch }) => {
  // The Instagram sheet's thumbnails (Home and Kind words) take the 320 copy wherever it covers their box (Moto G,
  // desktop); a 3x phone needs 338px there, so it takes the 480. Browsers take the first copy at or above the density.
  for (const [label, w, h, dpr] of [['iPhone (3x)', 390, 844, 3], ['Moto G (1.75x)', 412, 823, 1.75], ['desktop (1x)', 1440, 900, 1]]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: dpr, isMobile: w < 861, hasTouch: w < 861 });
    for (const name of ['index', 'kind-words']) {
      const p = await ctx.newPage(); watch(p);
      await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' });
      await p.$eval('.sheet', el => el.scrollIntoView({ block: 'center' }));
      await p.waitForFunction(() => [...document.querySelectorAll('.sheet img')].every(i => i.complete && i.naturalWidth), null, { timeout: 8000 }).catch(() => {});
      const r = await p.$$eval('.sheet img', l => l.map(i => { const b = i.getBoundingClientRect(), a = i.naturalWidth / i.naturalHeight;
        return { src: i.currentSrc.split('/').pop(), need: Math.round(Math.max(b.width, b.height * a) * devicePixelRatio) }; }));
      ok(r.length === 6 && r.every(x => x.src.endsWith(x.need <= 320 ? '-320.webp' : '-480.webp')) && (dpr === 3 || r.every(x => x.src.endsWith('-320.webp'))),
         `${label} ${name}: the six sheet thumbnails load the smallest copy that covers them (${r.map(x => x.src.replace(/^.*-/, '') + ' for ' + x.need + 'px').join(', ')})`);
      await p.close();
    }
    await ctx.close();
  }

  for (const [label, w, h, dpr] of CONFIGS) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: dpr, isMobile: w < 861, hasTouch: w < 861 });
    const problems = [];
    let checked = 0;
    for (const name of PAGES) {
      const p = await ctx.newPage(); watch(p);
      const requested = [];
      p.on('request', r => requested.push(r.url()));
      await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' });
      for (const img of await firstView(p)) {
        if (!img.cands.length || !img.src) continue;
        checked++;
        const covers = c => (c.w / img.need) ** 2 >= .9;   // pixels, not width
        const smallest = img.cands.findIndex(covers), chosen = img.cands.findIndex(c => c.file === img.src);
        const best = smallest < 0 ? img.cands.length - 1 : smallest;
        if (chosen < 0) problems.push(`${name}: ${img.src} is not in its srcset`);
        else if (chosen < best) problems.push(`${name}: ${img.src} is too small for ${img.w}x${img.h} (needs ${img.need}w)`);
        else if (chosen > best + 1) problems.push(`${name}: ${img.src} is ${chosen - best} rungs above ${img.cands[best].file} for ${img.w}x${img.h} (needs ${img.need}w)`);
      }
      if (name === 'index') {
        const lcp = await p.$eval('img[data-lcp]', i => i.currentSrc.split('/').pop()).catch(() => '');
        ok(lcp === HERO[dpr], `${label} index: the hero loads ${lcp} (expected ${HERO[dpr]})`);
        if (w < 861) ok(!requested.some(u => /jaguar-flare/.test(u)), `${label} index: the hero's desktop-only photo is never fetched`);
      }
      await p.close();
    }
    ok(!problems.length && checked > 0, `${label}: every first-view photo is the right size (${checked} checked)` + (problems.length ? ': ' + problems.join(' | ') : ''));
    await ctx.close();
  }
};
