// Shared test harness. Each *.test.js exports `async ({ browser, base, ok, watch }) => {}`.
const { chromium } = require('playwright');

const PAGES = ['index', 'gallery', 'investment', 'kind-words', 'contact', 'privacy', '404'];
const PHONE = { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true };
const DESKTOP = { viewport: { width: 1440, height: 900 } };

function harness(base) {
  const results = [];
  const errors = [], bad = [];
  const ok = (cond, msg) => { results.push([!!cond, msg]); console.log((cond ? 'PASS ' : 'FAIL ') + msg); };
  // Collect JS errors and failed requests from a page; `allow` is a regex of URLs allowed to fail.
  const watch = (page, allow) => {
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errors.push(m.text()); });
    page.on('response', r => { if (r.status() >= 400 && !(allow && allow.test(r.url()))) bad.push(r.status() + ' ' + r.url()); });
  };
  return { ok, watch, results, errors, bad, base };
}

// Proxy settings when testing a live https site from the sandbox; local runs need none.
function launch(base) {
  const remote = /^https:/.test(base) && process.env.HTTPS_PROXY;
  return chromium.launch(remote ? { proxy: { server: process.env.HTTPS_PROXY } } : {});
}

// A browser context in one of the site's states: 'motion' (the default visit), 'reduced' (Reduce Motion on),
// 'still' (Hold still remembered from an earlier visit) or 'nojs'. `vp` is PHONE, DESKTOP or any context options.
async function context(browser, state, vp) {
  const ctx = await browser.newContext({ ...vp, reducedMotion: state === 'reduced' ? 'reduce' : 'no-preference',
    javaScriptEnabled: state !== 'nojs' });
  if (state === 'still') await ctx.addInitScript(() => { try { localStorage.setItem('sl-still', '1'); } catch (e) {} });
  return ctx;
}

// Scroll to the bottom in steps (so observers and lazy photos see every part of the page), then wait.
// Driven from here, not by a timer in the page, so it also works with JavaScript off.
async function scrollThrough(page, { step = 400, pause = 50, settle = 300 } = {}) {
  for (let y = 0; y < await page.evaluate(() => document.documentElement.scrollHeight); y += step) {
    await page.evaluate(y => window.scrollTo({ top: y, behavior: 'instant' }), y);
    await page.waitForTimeout(pause);
  }
  await page.evaluate(() => window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }));
  await page.waitForTimeout(settle);
}

const scrollTo = (page, y) => page.evaluate(y => window.scrollTo({ top: y, behavior: 'instant' }), y);

module.exports = { harness, launch, context, scrollThrough, scrollTo, PAGES, PHONE, DESKTOP };
