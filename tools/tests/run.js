// Runs the site tests. Usage: node tools/tests/run.js <baseUrl> [name filter]
//   node tools/tests/run.js http://127.0.0.1:8771            # every *.test.js
//   node tools/tests/run.js http://127.0.0.1:8771 investment # just investment.test.js
// Needs Playwright with Chromium (NODE_PATH pointing at a global install works).
const fs = require('fs'), path = require('path');
const { harness, launch } = require('./lib');
(async () => {
  const base = (process.argv[2] || 'http://127.0.0.1:8771').replace(/\/$/, '');
  const filter = process.argv[3];
  const files = fs.readdirSync(__dirname).filter(f => f.endsWith('.test.js') && (!filter || f.includes(filter))).sort();
  const h = harness(base);
  const browser = await launch(base);
  for (const f of files) {
    const t0 = Date.now();
    console.log(`# ${f}`);
    try { await require(path.join(__dirname, f))({ browser, ...h }); }
    catch (e) { h.ok(false, `${f} crashed: ${e.message.split('\n')[0]}`); }
    console.log(`# ${f}: ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  }
  h.ok(h.bad.length === 0, 'no unexpected missing files' + (h.bad.length ? ': ' + h.bad.join(' | ') : ''));
  h.ok(h.errors.length === 0, h.errors.length ? 'JS errors: ' + h.errors.join(' | ') : 'no JS errors');
  await browser.close();
  const failed = h.results.filter(r => !r[0]).length;
  console.log(`\n${h.results.length - failed} passed, ${failed} failed`);
  process.exitCode = failed ? 1 : 0;
})();
