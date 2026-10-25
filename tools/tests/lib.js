// Shared test harness. Each *.test.js exports `async ({ browser, base, ok, watch }) => {}`.
const { chromium } = require('playwright');

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

module.exports = { harness, launch };
