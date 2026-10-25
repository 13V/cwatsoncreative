// Motion: First light once per visit; one-shots arm below the fold and never above it, then play; the footer line
// draws; the golden-hour line; Hold still on, remembered, off; the 404 dusk. The finished-frame test: every page,
// with no JS, with Reduce Motion and with Hold still, at 390 and 1440, is complete after scrolling through.
const { context, scrollThrough, scrollTo, PAGES, PHONE, DESKTOP } = require('./lib');
const HOSTS = '[data-rules], .window-arches, .sundown-scene, .ph--tray';
const cls = el => el.getAttribute('class') || '';

// Elements below the fold are armed; anything on screen at first sight is finished.
const arming = p => p.evaluate(hosts => {
  const vh = innerHeight, out = { armedOnScreen: [], liveOnScreen: [], armed: [] };
  const onScreen = r => r.bottom > 0 && r.top < vh && (r.width || r.height);
  document.querySelectorAll('.is-armed').forEach(el => {
    out.armed.push((el.getAttribute('class') || '').split(' ')[0]);
    if (onScreen(el.getBoundingClientRect())) out.armedOnScreen.push(el.getAttribute('class'));
  });
  document.querySelectorAll(hosts).forEach(el => {
    if (onScreen(el.getBoundingClientRect()) && !el.classList.contains('is-done')) out.liveOnScreen.push(el.getAttribute('class'));
  });
  return out;
}, HOSTS);

// What a finished page must look like (motion plan rule 1; build plan WP0 item 14).
const finished = p => p.evaluate(() => {
  const out = { dash: [], armed: [], filter: [], faded: [] };
  const name = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + ((el.getAttribute('class') || '').trim() ? '.' + el.getAttribute('class').trim().split(/\s+/).join('.') : '');
  document.querySelectorAll('path[pathLength]:not(.glint)').forEach(el => {
    if (Math.abs(parseFloat(getComputedStyle(el).strokeDashoffset) || 0) > .001) out.dash.push(name(el) + ' ' + getComputedStyle(el).strokeDashoffset);
  });
  document.querySelectorAll('.is-armed:not(.is-done)').forEach(el => out.armed.push(name(el)));
  document.querySelectorAll('img').forEach(el => {   // shown photos only (a display: none pane has no frame to show)
    if (el.getClientRects().length && getComputedStyle(el).filter !== 'none') out.filter.push(name(el) + ' ' + getComputedStyle(el).filter);
  });
  const closedNav = n => n.classList.contains('site-nav') && document.documentElement.classList.contains('js') && !n.classList.contains('is-open') && innerWidth <= 860;
  document.querySelectorAll('header, header *, main, main *, footer, footer *').forEach(el => {
    if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') return;   // drawings: checked by their dashes and moments
    if (!el.getClientRects().length) return;                                  // display: none
    // transparent by design: hidden things, radio inputs under their chip faces, the brush of an index link not current
    if (el.closest('[hidden], dialog:not([open]), .sr-only, .chip-input, .index a:not([aria-current="true"]) .brush') || [...ancestors(el)].some(closedNav)) return;
    if (parseFloat(getComputedStyle(el).opacity) < .99) out.faded.push(name(el) + ' ' + getComputedStyle(el).opacity);
  });
  function* ancestors(el) { for (; el; el = el.parentElement) yield el; }
  return out;
});

module.exports = async ({ browser: b, base, ok, watch }) => {
  {
    const ctx = await context(b, 'motion', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    await p.waitForTimeout(300);
    ok(await p.evaluate(() => document.documentElement.classList.contains('first-light')), 'First light plays on the first page of a visit');
    const a = await arming(p);
    ok(['steps', 'faq', 'sundown-scene'].every(c => a.armed.includes(c)), 'groups below the fold wait to draw (' + a.armed.join(', ') + ')');
    await scrollThrough(p, { settle: 3600 });
    ok(await p.$$eval('.is-armed:not(.is-drawn):not(.is-done)', els => els.map(e => e.getAttribute('class'))).then(l => !l.length), 'everything has played after scrolling through');
    ok(await p.$eval('.sundown-scene', f => f.classList.contains('is-drawn')), 'the footer line has drawn (.sundown-scene.is-drawn)');
    const gh = await p.textContent('[data-golden]');
    ok(/^Golden hour (in Adelaide tonight|in Adelaide now|tomorrow) · (from|until) \d{1,2}:\d{2} [ap]m$/.test(gh), `golden hour shows tonight's time (${gh})`);
    await p.goto(`${base}/contact.html`, { waitUntil: 'networkidle' });
    ok(!(await p.evaluate(() => document.documentElement.classList.contains('first-light'))), 'First light does not replay on the next page');
    await p.click('.still-toggle');
    ok(await p.evaluate(() => document.documentElement.classList.contains('still') && !document.documentElement.classList.contains('m')) &&
       (await p.getAttribute('.still-toggle', 'aria-pressed')) === 'true', 'Hold still turns motion off');
    ok(await p.$$eval('.is-armed:not(.is-done)', els => els.length) === 0, 'Hold still shows every finished frame');
    await p.reload({ waitUntil: 'networkidle' });
    ok(await p.evaluate(() => document.documentElement.classList.contains('still')) && (await p.getAttribute('.still-toggle', 'aria-pressed')) === 'true', 'Hold still is remembered');
    await p.click('.still-toggle');
    ok(await p.evaluate(() => !document.documentElement.classList.contains('still') && document.documentElement.classList.contains('m')), 'Hold still can be turned off again');
    await ctx.close();
  }
  {   // Hold still is hidden when Reduce Motion is on: it could change nothing
    const ctx = await context(b, 'reduced', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/privacy.html`, { waitUntil: 'networkidle' });
    ok(!(await p.isVisible('.still-toggle')) && !(await p.evaluate(() => document.documentElement.classList.contains('m'))), 'with Reduce Motion: no .m and no Hold still button');
    await ctx.close();
  }
  for (const vp of [PHONE, DESKTOP]) {   // arming on every page: below the fold only
    const ctx = await context(b, 'motion', vp);
    const p = await ctx.newPage(); watch(p);
    const problems = [];
    for (const name of PAGES) {
      await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' }); await p.waitForTimeout(250);
      const a = await arming(p);
      if (a.armedOnScreen.length) problems.push(`${name}: armed on screen: ${a.armedOnScreen.join(', ')}`);
      if (a.liveOnScreen.length) problems.push(`${name}: on screen but not finished: ${a.liveOnScreen.join(', ')}`);
    }
    ok(!problems.length, `${vp.viewport.width}: one-shots arm below the fold only; on screen at load they are finished` + (problems.length ? ': ' + problems.join(' | ') : ''));
    await ctx.close();
  }
  {   // the 404 dusk: plays once on load in the mark, and its finished frame is dusk
    const ctx = await context(b, 'motion', PHONE);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/404.html`, { waitUntil: 'domcontentloaded' });   // the dusk waits 400ms after it starts
    const look = () => p.$eval('#nf-mark', m => ({ dusk: +getComputedStyle(m.querySelector('.nf-dusk')).opacity, sun: getComputedStyle(m.querySelector('.mk-sun')).transform, cls: m.getAttribute('class') }));
    const start = await look();
    await p.waitForTimeout(3200);
    const end = await look();
    await scrollTo(p, 400); await p.waitForTimeout(300); await scrollTo(p, 0); await p.waitForTimeout(600);
    const again = await look();
    ok(start.dusk < .1 && Math.abs(end.dusk - .55) < .02 && /\bis-dusk\b/.test(end.cls) && start.sun !== end.sun && again.dusk === end.dusk && again.sun === end.sun,
       `404: the dusk plays once on load (dusk ${start.dusk} → ${end.dusk}, sun ${start.sun} → ${end.sun})`);
    ok(!(await p.evaluate(() => document.documentElement.classList.contains('first-light'))), '404: no First light (one moving sun)');
    for (const state of ['nojs', 'reduced', 'still']) {
      const c = await context(b, state, PHONE), q = await c.newPage(); watch(q);
      await q.goto(`${base}/404.html`, { waitUntil: 'networkidle' });
      const f = await q.$eval('#nf-mark', m => ({ dusk: +getComputedStyle(m.querySelector('.nf-dusk')).opacity, sun: getComputedStyle(m.querySelector('.mk-sun')).transform }));
      ok(Math.abs(f.dusk - .55) < .02 && f.sun === end.sun, `404 (${state}): the mark shows the finished dusk`);
      await c.close();
    }
    await ctx.close();
  }
  // The finished-frame test.
  for (const state of ['nojs', 'reduced', 'still']) {
    for (const vp of [PHONE, DESKTOP]) {
      const ctx = await context(b, state, vp);
      const problems = [];
      for (const name of PAGES) {
        const p = await ctx.newPage(); watch(p);
        await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' });
        await scrollThrough(p);
        const f = await finished(p);
        await scrollTo(p, 0); await p.waitForTimeout(150);   // scroll-linked silver exits are by design while a window leaves
        f.filter = (await finished(p)).filter;
        for (const [k, label] of [['dash', 'half-drawn'], ['armed', 'armed'], ['filter', 'filtered'], ['faded', 'faded']])
          if (f[k].length) problems.push(`${name} ${label}: ${f[k].slice(0, 4).join(', ')}${f[k].length > 4 ? ' …' : ''}`);
        await p.close();
      }
      ok(!problems.length, `finished frame, ${state} at ${vp.viewport.width}: ` + (problems.length ? problems.join(' | ') : 'all 7 pages complete'));
      await ctx.close();
    }
  }
};
