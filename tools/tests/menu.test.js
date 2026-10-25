// Header, phone menu and index bar: the menu is closed and inert on phones (never inert on desktop), opens with the
// four tabs and Instagram, moves focus in, makes the page behind inert, closes on Escape and on widening; the header
// hides on the way down and returns on the way up or on focus; the index bar follows it by transform only, and its
// spy marks the session in view.
const { context, scrollTo, PHONE, DESKTOP } = require('./lib');

const state = p => p.evaluate(() => {
  const nav = document.getElementById('site-nav'), t = document.querySelector('.nav-toggle');
  return {
    open: nav.classList.contains('is-open'), inert: nav.inert, visible: getComputedStyle(nav).visibility !== 'hidden',
    expanded: t.getAttribute('aria-expanded'), label: t.textContent.trim(),
    behind: ['main', '.site-footer', '.skip'].map(s => document.querySelector(s).inert),
    menuOpen: document.documentElement.classList.contains('menu-open'),
  };
});

module.exports = async ({ browser: b, base, ok, watch }) => {
  {
    const ctx = await context(b, 'motion', PHONE);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    let s = await state(p);
    ok(!s.open && s.inert && !s.visible && s.expanded === 'false', '390: the menu is closed and inert on load');
    await p.tap('.nav-toggle'); await p.waitForTimeout(700);
    s = await state(p);
    const tabs = await p.$$eval('#site-nav > a', as => as.map(a => a.textContent.trim()));
    ok(s.open && !s.inert && JSON.stringify(tabs) === JSON.stringify(['Gallery', 'Investment', 'Kind words', 'Contact']) &&
       await p.isVisible('#site-nav > a[href="contact.html"]') && await p.isVisible('#site-nav .nav-instagram'),
       'the menu opens with the four tabs and Instagram');
    ok(await p.evaluate(() => document.activeElement === document.querySelector('#site-nav a[href]')) && s.label === 'Close' && s.expanded === 'true',
       'opening moves focus to the first link; the toggle reads "Close"');
    ok(s.behind.every(Boolean) && s.menuOpen, 'main, the footer and the skip link are inert while it is open');
    ok(await p.$eval('#site-nav > a[aria-current="page"]', a => a.textContent.trim() === 'Investment' && getComputedStyle(a).fontStyle === 'italic' &&
       !!a.querySelector('.nav-sun') && a.querySelector('.nav-sun').getBoundingClientRect().width > 0).catch(() => false),
       'the current tab is italic with the sun dot');
    await p.keyboard.press('Escape'); await p.waitForTimeout(500);
    s = await state(p);
    ok(!s.open && s.inert && !s.visible && !s.behind.some(Boolean) && !s.menuOpen &&
       await p.evaluate(() => document.activeElement === document.querySelector('.nav-toggle')), 'Escape closes it and focus returns to the toggle');
    await p.tap('.nav-toggle'); await p.waitForTimeout(300);
    await p.setViewportSize({ width: 1000, height: 800 }); await p.waitForTimeout(300);
    s = await state(p);
    ok(!s.open && !s.inert && s.expanded === 'false' && !s.behind.some(Boolean) && !s.menuOpen, 'widening past 860px closes it, and the desktop nav is not inert');
    await ctx.close();
  }
  {
    const ctx = await context(b, 'motion', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    const s = await state(p);
    ok(!s.inert && s.visible && await p.isVisible('#site-nav > a[href="gallery.html"]'), '1440: the nav is visible and never inert');
    await ctx.close();
  }
  {   // without motion the menu links are never clipped (they only rise out of a clipped line under .m)
    const ctx = await context(b, 'reduced', PHONE);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    await p.tap('.nav-toggle'); await p.waitForTimeout(400);
    const clip = await p.$$eval('#site-nav .nl', ns => ns.map(n => getComputedStyle(n).overflowY + '/' + getComputedStyle(n).overflowX));
    ok(clip.length === 4 && clip.every(c => c === 'visible/visible'), `no .nl clipping without motion (${clip[0]})`);
    await ctx.close();
  }
  {   // the header and the index bar
    const ctx = await context(b, 'motion', PHONE);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    const look = () => p.evaluate(() => {
      const h = document.querySelector('.site-header'), bar = document.querySelector('.index-bar');
      return { hidden: h.classList.contains('is-hidden'), flag: document.documentElement.classList.contains('header-hidden'),
        scrolled: h.classList.contains('is-scrolled'), headTop: Math.round(h.getBoundingClientRect().bottom),
        top: bar && getComputedStyle(bar).top, barTop: bar && Math.round(bar.getBoundingClientRect().top), sticky: bar && getComputedStyle(bar).position,
        current: [...document.querySelectorAll('.index-bar a[aria-current]')].map(a => a.textContent.trim() + '=' + a.getAttribute('aria-current')) };
    });
    const at0 = await look();
    ok(!at0.hidden && !at0.scrolled && !at0.current.length, 'at the top: header shown, no hairline, no index link current');
    for (let y = 100; y <= 1600; y += 100) { await scrollTo(p, y); await p.waitForTimeout(40); }
    await p.waitForTimeout(500);
    const down = await look();
    ok(down.hidden && down.flag && down.scrolled && down.headTop <= 0, 'scrolling down hides the header (html.header-hidden)');
    ok(down.sticky === 'sticky' && down.top === at0.top && Math.abs(down.barTop) <= 1, `the index bar follows it by transform; its top stays ${at0.top} (bar at ${down.barTop}px)`);
    for (let y = 1500; y >= 1200; y -= 100) { await scrollTo(p, y); await p.waitForTimeout(40); }
    await p.waitForTimeout(500);
    const up = await look();
    ok(!up.hidden && !up.flag && up.headTop > 0, 'scrolling up brings it back');
    await p.evaluate(async () => { for (let y = 1300; y <= 2400; y += 100) { window.scrollTo({ top: y, behavior: 'instant' }); await new Promise(r => setTimeout(r, 40)); } });
    await p.waitForTimeout(400);
    await p.focus('.brand'); await p.waitForTimeout(400);
    ok(!(await look()).hidden, 'focus inside the header shows it');
    // the spy: one link per session, Weddings for both of its sections
    for (const [id, name] of [['couples', 'Couples'], ['wedding-packages', 'Weddings'], ['weddings', 'Weddings'], ['newborn', 'Newborn']]) {
      await p.evaluate(id => { location.hash = '#' + id; }, id); await p.waitForTimeout(1000);
      const s = await look();
      const seen = await p.$eval('.index-bar a[aria-current]', a => { const r = a.getBoundingClientRect(), s = a.closest('.index').getBoundingClientRect(); return r.left >= s.left - 1 && r.right <= s.right + 1; }).catch(() => false);
      ok(JSON.stringify(s.current) === JSON.stringify([name + '=true']) && seen, `#${id}: the spy marks ${name} (${s.current.join(', ')}), scrolled into view`);
    }
    await ctx.close();
  }
  for (const vp of [PHONE, DESKTOP]) {   // a cold load at a session lands with its heading clear of the header and bar
    const ctx = await context(b, 'motion', vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html#family`, { waitUntil: 'networkidle' }); await p.waitForTimeout(400);
    const r = await p.evaluate(() => {
      const bar = document.querySelector('.index-bar').getBoundingClientRect(), h = document.querySelector('#family :is(h2, h3)').getBoundingClientRect();
      return { gap: Math.round(h.top - bar.bottom), current: (document.querySelector('.index-bar a[aria-current]') || {}).textContent };
    });
    ok(r.gap >= 0 && r.current && r.current.trim() === 'Family', `${vp.viewport.width}: investment.html#family lands below the bar (${r.gap}px) with Family current`);
    await ctx.close();
  }
};
