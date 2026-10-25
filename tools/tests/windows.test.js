// Photo windows (M02): the hero holds still and leaves in black and white where scroll timelines exist, and is simply
// still and in colour with Reduce Motion or Hold still; windows A and B show one arch per photo (one on phones), with
// mullions in the colour of the section above, never two photos edge to edge; the arcade draws and ends drawn.
const { context, scrollTo, PHONE, DESKTOP } = require('./lib');

const hero = p => p.$eval('.window--hero', w => ({
  photo: Math.round(w.querySelector('.window-photos').getBoundingClientRect().top), win: Math.round(w.getBoundingClientRect().top),
  filter: getComputedStyle(w.querySelector('img')).filter, arches: !!w.querySelector('.window-arches'),
}));

// The window's arcade, panes and the colours that should agree, with the window scrolled to the top of the screen.
const arcade = (p, sel) => p.$eval(sel, w => {
  const rgb = c => { const d = document.createElement('i'); d.style.color = c; document.body.append(d); const v = getComputedStyle(d).color; d.remove(); return v; };
  const bg = el => { for (; el; el = el.parentElement) { const c = getComputedStyle(el).backgroundColor; if (!/rgba\(.*, 0\)$|transparent/.test(c)) return c; } return 'none'; };
  const shown = el => el.getClientRects().length && el.getBoundingClientRect().width > 0;
  const panes = [...w.querySelectorAll('.window-photos > .ph')].filter(shown).map(el => el.getBoundingClientRect());
  const gaps = panes.slice(1).map((r, i) => Math.round(r.left - panes[i].right));
  const mid = panes.length > 1 ? document.elementFromPoint((panes[0].right + panes[1].left) / 2, Math.max(1, panes[0].top + 200)) : null;
  const hole = w.querySelector('.hole');
  return {
    count: +w.dataset.count, arches: [...w.querySelectorAll('.window-arches > span')].filter(shown).length, panes: panes.length, gaps,
    above: rgb(getComputedStyle(w).getPropertyValue('--above').trim()), mullion: mid ? bg(mid) : null,
    prev: bg(w.previousElementSibling), shoulders: hole ? getComputedStyle(hole).boxShadow : '',
    frames: [...w.querySelectorAll('.window-arches .frame')].filter(shown).map(f => parseFloat(getComputedStyle(f).strokeDashoffset)),
    state: w.querySelector('.window-arches').getAttribute('class'),
  };
});

module.exports = async ({ browser: b, base, ok, watch }) => {
  {
    const ctx = await context(b, 'motion', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
    const at = async y => { await scrollTo(p, y); await p.waitForTimeout(200); return hero(p); };
    const a = await at(0), c = await at(500);
    ok(Math.abs(a.photo - c.photo) <= 2 && c.win < a.win - 400, `hero photos hold still while the page scrolls (window ${a.win} → ${c.win}, photos stay at ${c.photo})`);
    ok(/grayscale\(0?\.[3-9]|grayscale\(1\)/.test(c.filter) && /^none$|grayscale\(0\)/.test(a.filter), `hero fades to black and white as it leaves (${a.filter} → ${c.filter})`);
    ok(!a.arches, 'no arcade on the hero');
    await ctx.close();
  }
  for (const state of ['reduced', 'still']) {
    const ctx = await context(b, state, DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
    await scrollTo(p, 500); await p.waitForTimeout(200);
    const r = await hero(p);
    ok(r.photo === r.win && r.filter === 'none', `${state}: the hero photos are simply still and in colour`);
    await ctx.close();
  }
  for (const [vp, state] of [[DESKTOP, 'motion'], [PHONE, 'motion'], [DESKTOP, 'reduced']]) {
    const ctx = await context(b, state, vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/index.html`, { waitUntil: 'networkidle' });
    const w = vp.viewport.width;
    for (const [sel, n] of [['.window--a', 3], ['.window--b', 2]]) {
      if (!(await p.$(sel))) { ok(false, `${sel} is on Home`); continue; }
      // bring the arcade strip fully on screen, give the draw (900ms + 120ms a cell) time to finish
      await p.$eval(sel, el => window.scrollTo({ top: el.getBoundingClientRect().top + scrollY - 40, behavior: 'instant' }));
      await p.waitForTimeout(state === 'motion' ? 1800 : 200);
      const r = await arcade(p, sel);
      const tag = `${w} ${state} ${sel}`;
      if (state === 'motion') ok(r.count === n && r.arches === (w > 860 ? n : 1) && r.panes === r.arches, `${tag}: ${r.arches} arch(es) over ${r.panes} photo(s) (data-count ${r.count})`);
      if (w > 860) {
        ok(r.gaps.length === n - 1 && r.gaps.every(g => g >= 1), `${tag}: mullions between the photos (${r.gaps.join(', ')}px), never edge to edge`);
        ok(r.mullion === r.above && r.above === r.prev && r.shoulders.includes(r.above), `${tag}: mullions and shoulders are --above, the colour of the section before (${r.mullion} / ${r.above} / ${r.prev})`);
      }
      ok(r.frames.length && r.frames.every(f => Math.abs(f) < .001) && (state === 'motion' ? /is-drawn|is-done/ : /is-done/).test(r.state),
         `${tag}: the frame is drawn (${r.state}; offsets ${r.frames.join(', ')})`);
    }
    await ctx.close();
  }
};
