// Photo viewer (spec §4.12; M06, M11) at 390 and 1440: opens from a grid photo and from a chapter cover, counts and
// announces, pages with arrows, keys and swipes (wrapping), keeps the alt on exactly one image, closes every way
// (Esc, Close, beside the photo, swipe down, Chrome's second Esc) with focus back on the link and the page unmoved,
// locks scrolling while open, loads the full WebP (never the JPEG), and with Reduce Motion only fades. Cmd/Ctrl-,
// Shift- and middle-clicks are the browser's: they open the JPEG, never the viewer.
const { context, PHONE, DESKTOP } = require('./lib');

const state = p => p.evaluate(() => {
  const d = document.querySelector('dialog.viewer'), imgs = [...d.querySelectorAll('.viewer-img')];
  return {
    open: d.open, lock: document.documentElement.classList.contains('viewer-open'),
    count: d.querySelector('.viewer-count').textContent.replace(/\s+/g, ' ').trim(), live: d.querySelector('.viewer-live').textContent,
    alts: imgs.filter(i => i.alt).map(i => i.alt), hiddenAlt: imgs.filter(i => i.alt && i.getAttribute('aria-hidden')).length,
    front: d.querySelector('.viewer-img.is-front').currentSrc, focus: document.activeElement.getAttribute('href'), y: Math.round(scrollY),
    thumbs: [...document.querySelectorAll('.ph-link img')].filter(i => i.style.visibility).length,
    running: d.getAnimations({ subtree: true }).length,
  };
});
const alt = (p, i) => p.$eval(`[data-viewer][data-index="${i}"] img`, img => img.alt);
// A one-finger swipe on the viewer, as touch events (Playwright's touchscreen only taps).
const swipe = (p, dx, dy, ms = 240) => p.evaluate(async ([dx, dy, ms]) => {
  const d = document.querySelector('dialog.viewer'), x = innerWidth / 2, y = innerHeight / 2, n = 8;
  const t = (cx, cy) => new Touch({ identifier: 1, target: d, clientX: cx, clientY: cy });
  const fire = (type, cx, cy) => d.dispatchEvent(new TouchEvent(type, { bubbles: true, cancelable: true,
    touches: type === 'touchend' ? [] : [t(cx, cy)], changedTouches: [t(cx, cy)] }));
  fire('touchstart', x, y);
  for (let i = 1; i <= n; i++) { await new Promise(r => setTimeout(r, ms / n)); fire('touchmove', x + dx * i / n, y + dy * i / n); }
  fire('touchend', x + dx, y + dy);
}, [dx, dy, ms]);
const settle = p => p.waitForFunction(() => !document.querySelector('dialog.viewer').getAnimations({ subtree: true }).length, null, { timeout: 4000 }).catch(() => {});

module.exports = async ({ browser: b, base, ok, watch }) => {
  for (const vp of [PHONE, DESKTOP]) {
    const w = vp.viewport.width, ctx = await context(b, 'motion', vp);
    const p = await ctx.newPage(); watch(p);
    const jpegs = [];
    p.on('request', r => { if (/\/images\/weddings\/[^/]+\.jpg$/.test(r.url())) jpegs.push(r.url()); });
    await p.goto(`${base}/gallery.html`, { waitUntil: 'networkidle' });
    const total = await p.$$eval('[data-viewer]', a => a.length);

    // from the first link (chapter 01's cover)
    await p.click('[data-viewer][data-index="0"]');
    await p.waitForTimeout(60);
    const mid = await p.evaluate(() => document.querySelector('.viewer-img.is-front').getAnimations().map(a => a.effect.getTiming().duration).sort());
    await settle(p);
    let s = await state(p);
    const y0 = s.y;   // the page never moves while the viewer is open, or as it closes
    ok(s.open && s.lock && s.count === `01 / ${total}` && total === 23, `${w}: opens from a cover with "${s.count}", html.viewer-open locks the page`);
    ok(mid.includes(240) && mid.includes(480), `${w}: from a cover the photo flies 480ms while the arch radius settles in 240ms (${mid.join(', ')})`);
    ok(s.alts.length === 1 && !s.hiddenAlt && s.alts[0] === await alt(p, 0), `${w}: exactly one .viewer-img carries the alt`);
    await p.waitForFunction(() => /\.webp$/.test(document.querySelector('.viewer-img.is-front').currentSrc) && !document.querySelector('dialog.viewer').classList.contains('is-loading'));
    s = await state(p);
    ok(/\.webp$/.test(s.front) && /\/gilded-mirror(-\d+)?\.webp$/.test(s.front), `${w}: the full file comes from the WebP srcset (${s.front.replace(/.*\//, '')})`);

    await p.keyboard.press('ArrowRight'); await settle(p);
    s = await state(p);
    ok(s.count === `02 / ${total}` && s.live === `Photo 2 of ${total}: ${await alt(p, 1)}` && s.alts.length === 1 && s.alts[0] === await alt(p, 1),
       `${w}: → moves on; the live region says "${s.live}"`);
    const empty = await p.$$eval('.ph-link img', is => is.filter(i => i.style.visibility === 'hidden').map(i => i.closest('a').dataset.index));
    ok(empty.join() === '1', `${w}: only the shown photo's slot is left empty behind the darkroom (${empty.join()})`);
    await p.keyboard.press('ArrowLeft'); await p.keyboard.press('ArrowLeft'); await settle(p);
    s = await state(p);
    ok(s.count === `${total} / ${total}`, `${w}: ← wraps from the first photo to the last (${s.count})`);
    await p.click('.viewer-next'); await settle(p);
    ok((await state(p)).count === `01 / ${total}`, `${w}: Next wraps from the last photo to the first`);
    await p.keyboard.press('Escape'); await settle(p);
    s = await state(p);
    ok(!s.open && !s.lock && s.focus === await p.getAttribute('[data-index="0"]', 'href') && s.y === y0 && !s.thumbs,
       `${w}: Esc closes; focus back on the link without scrolling (y ${y0} → ${s.y}); scroll unlocked`);

    // from a grid photo, closed with the Close button and beside the photo
    const grid = await p.$eval('.rg [data-viewer]', a => +a.dataset.index);
    await p.click(`[data-index="${grid}"]`); await settle(p);
    const y1 = await p.evaluate(() => Math.round(scrollY));
    s = await state(p);
    ok(s.open && s.count === `0${grid + 1} / ${total}`, `${w}: opens from a grid photo (${s.count})`);
    await p.click('.viewer-close'); await settle(p);
    s = await state(p);
    ok(!s.open && s.focus === await p.getAttribute(`[data-index="${grid}"]`, 'href') && s.y === y1, `${w}: Close closes; focus returns to the photo's link`);
    await p.click(`[data-index="${grid}"]`); await settle(p);
    const box = await p.$eval('.viewer-stage', st => { const r = st.getBoundingClientRect(), i = st.querySelector('.is-front').getBoundingClientRect(); return { x: r.left + 4, y: i.top > r.top + 8 ? r.top + 4 : r.bottom - 4 }; });
    await p.mouse.click(box.x, box.y); await settle(p);
    ok(!(await state(p)).open, `${w}: a tap beside the photo closes`);

    // the in-flight close from a far photo: the slot comes into view behind the darkroom and the photo lands on it
    await p.click(`[data-index="${grid}"]`); await settle(p);
    for (let i = 0; i < 12; i++) await p.keyboard.press('ArrowRight');
    await settle(p);
    const far = (await state(p)).count;
    await p.keyboard.press('Escape'); await settle(p);
    const landed = await p.evaluate(() => { const r = document.activeElement.querySelector('.ph').getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight; });
    ok(landed && !(await state(p)).open, `${w}: closing on a far photo (${far}) brings its slot into view and focuses its link`);

    // Chrome's second Esc closes natively: everything is still clean
    await p.click(`[data-index="${grid}"]`); await p.waitForTimeout(500);
    await p.keyboard.press('Escape'); await p.keyboard.press('Escape'); await p.waitForTimeout(700);
    s = await state(p);
    const imgStyle = await p.$$eval('.viewer-img, .viewer-dark', els => els.map(e => e.getAttribute('style')).filter(Boolean).length);
    ok(!s.open && !s.lock && !s.thumbs && !s.running && !imgStyle, `${w}: a second Esc leaves a clean state`);

    if (vp === PHONE) {   // swipes
      await p.click(`[data-index="${grid}"]`); await settle(p);
      await swipe(p, -120, 6); await settle(p);
      ok((await state(p)).count === `0${grid + 2} / ${total}`, '390: a swipe left moves on');
      await swipe(p, 120, -4); await settle(p);
      ok((await state(p)).count === `0${grid + 1} / ${total}`, '390: a swipe right moves back');
      const follow = await p.evaluate(async () => {   // the photo follows a downward drag and the darkroom thins
        const d = document.querySelector('dialog.viewer'), x = 195, t = (y) => new Touch({ identifier: 1, target: d, clientX: x, clientY: y });
        const fire = (type, y) => d.dispatchEvent(new TouchEvent(type, { bubbles: true, cancelable: true, touches: type === 'touchend' ? [] : [t(y)], changedTouches: [t(y)] }));
        fire('touchstart', 400);
        for (let y = 410; y <= 460; y += 10) { await new Promise(r => setTimeout(r, 40)); fire('touchmove', y); }
        const f = d.querySelector('.is-front'), r = { tf: f.style.transform, dark: getComputedStyle(d.querySelector('.viewer-dark')).opacity };
        await new Promise(r => setTimeout(r, 300));
        fire('touchend', 460);
        return r;
      });
      await settle(p);
      s = await state(p);
      ok(/scale\(0\.98/.test(follow.tf) && +follow.dark < 1 && s.open, `390: a short drag down follows the finger (${follow.tf}) and settles back`);
      await swipe(p, 4, 160, 300); await settle(p);
      s = await state(p);
      ok(!s.open && !s.lock && s.focus === await p.getAttribute(`[data-index="${grid}"]`, 'href'), '390: a swipe down closes');
    }
    ok(!jpegs.length, `${w}: no JPEG requested while the WebP loads` + (jpegs.length ? ': ' + jpegs.join(', ') : ''));
    await ctx.close();
  }
  for (const [state, vp] of [['reduced', PHONE], ['reduced', DESKTOP], ['still', DESKTOP]]) {   // focus returns to a photo in view
    const ctx = await context(b, state, vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/gallery.html`, { waitUntil: 'networkidle' });
    await p.focus('[data-index="0"]'); await p.keyboard.press('Enter'); await p.waitForTimeout(300);
    for (let i = 0; i < 6; i++) { await p.keyboard.press('ArrowRight'); await p.waitForTimeout(200); }
    await p.keyboard.press('Escape'); await p.waitForTimeout(500);
    const f = await p.evaluate(() => { const a = document.activeElement, r = a.getBoundingClientRect();
      return { index: a.dataset.index, top: Math.round(r.top), bottom: Math.round(r.bottom), open: document.querySelector('dialog.viewer').open }; });
    const h = vp.viewport.height;
    ok(!f.open && f.index === '6' && f.bottom > 0 && f.top < h, `${vp.viewport.width} ${state}: after paging to photo 7 and closing, focus is on it and it is on screen (top ${f.top}px of ${h})`);
    await ctx.close();
  }
  for (const vp of [PHONE, DESKTOP]) {   // Reduce Motion: the 150ms fade only
    const ctx = await context(b, 'reduced', vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/gallery.html`, { waitUntil: 'networkidle' });
    const look = () => p.evaluate(() => document.getAnimations().map(a => `${a.effect.target.className || a.effect.target.tagName}:${a.effect.getTiming().duration}`));
    await p.click('.rg [data-viewer]');
    const opening = await look();
    await p.waitForTimeout(300);
    await p.keyboard.press('ArrowRight');
    const paging = await look();
    await p.waitForTimeout(300);
    await p.keyboard.press('Escape');
    const closing = await look();
    await p.waitForTimeout(400);
    const s = await state(p);
    const fade = l => l.length === 1 && /:150$/.test(l[0]);
    ok(fade(opening) && fade(paging) && fade(closing) && !s.open && !s.lock,
       `${vp.viewport.width} reduced: opens, pages and closes with one 150ms fade each (${[opening, paging, closing].map(l => l.join(' ')).join(' | ')})`);
    await ctx.close();
  }
  {   // a modified or middle click opens the photo's JPEG the browser's way, never the viewer
    const ctx = await context(b, 'motion', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/gallery.html`, { waitUntil: 'networkidle' });
    const link = '.rg a.ph-link', href = await p.$eval(link, a => a.href);
    for (const [how, opts] of [['Cmd/Ctrl-click', { modifiers: ['ControlOrMeta'] }], ['Shift-click', { modifiers: ['Shift'] }], ['middle-click', { button: 'middle' }]]) {
      const opened = ctx.waitForEvent('page', { timeout: 3000 }).catch(() => null);
      await p.click(link, opts);
      const tab = await opened;
      const url = tab ? (await tab.waitForURL(/\.jpg$/, { timeout: 3000 }).catch(() => {}), tab.url()) : '';
      const s = await state(p);
      ok(!s.open && !s.lock && url === href, `${how} on a grid photo opens its JPEG in a new tab, not the viewer (${url.split('/').pop() || 'no tab'})`);
      if (tab) await tab.close();
    }
    await ctx.close();
  }
};
