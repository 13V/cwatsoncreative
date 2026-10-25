// Phone menu: closed on load, opens with the tabs, marks the current page, closes on Escape.
module.exports = async ({ browser: b, base, ok, watch }) => {
  {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    ok(!(await p.isVisible('#site-nav')), 'menu closed on load');
    await p.tap('.nav-toggle'); await p.waitForTimeout(500);
    ok(await p.isVisible('#site-nav a[href="kind-words.html"]') && await p.isVisible('#site-nav .nav-instagram'), 'menu opens with the four tabs and Instagram');
    ok(await p.$eval('#site-nav a[aria-current="page"]', a => a.textContent.trim() === 'Investment' && getComputedStyle(a).fontStyle === 'italic'), 'current tab shows in italic');
    await p.keyboard.press('Escape'); await p.waitForTimeout(500);
    ok(!(await p.isVisible('#site-nav')), 'Escape closes the menu');
    await ctx.close();
  }
};
