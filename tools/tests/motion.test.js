// Motion kernel: one-shot moments arm below the fold and play once, First light, Hold still and the golden-hour line.
module.exports = async ({ browser: b, base, ok, watch }) => {
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    await p.waitForTimeout(300);
    ok(await p.evaluate(() => document.documentElement.classList.contains('first-light')), 'First light plays on the first page of a visit');
    const armed = await p.$$eval('.is-armed', els => els.map(e => e.className.split(' ')[0]));
    ok(armed.includes('steps') && armed.includes('faq') && armed.includes('sundown'), 'groups below the fold wait to draw (' + armed.join(', ') + ')');
    ok(await p.$eval('.page-head .eyebrow', e => !e.classList.contains('is-armed')), 'what is on screen at load stays finished');
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 300) { window.scrollTo({ top: y, behavior: 'instant' }); await new Promise(r => setTimeout(r, 60)); } });
    await p.waitForTimeout(2200);
    ok(await p.$$eval('.is-armed:not(.is-drawn)', els => els.length) === 0, 'everything has drawn after scrolling through');
    ok(await p.$eval('.sundown', f => f.classList.contains('is-drawn')), 'the footer line has drawn');
    ok(/^Golden hour (in Adelaide tonight|in Adelaide now|tomorrow) · (from|until) \d{1,2}:\d{2} [ap]m$/.test(await p.textContent('[data-golden]')), 'golden hour shows tonight\'s time (' + (await p.textContent('[data-golden]')) + ')');
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
};
