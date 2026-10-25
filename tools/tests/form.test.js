// Enquiry form (spec §4.18, M09, D15): the chip a session link chooses, the summary and inline errors, when fields
// check themselves, the payload the webhook expects, sending, success (with the name rules), failure and the
// honeypot, and no layout shift through any of it. The webhook is always mocked: nothing is ever sent.
const { PHONE, DESKTOP } = require('./lib');
const HOOK = '**/webhook/sunday-light-enquiry';
const KEYS = ['name', 'email', 'phone', 'session', 'date', 'location', 'message', 'heard', 'submitted', 'source'];

// Every layout shift, recent input or not: the reserved slots mean there should be none at all.
const shifts = () => { window.__ls = []; new PerformanceObserver(l => l.getEntries().forEach(e => window.__ls.push({ v: e.value, input: e.hadRecentInput }))).observe({ type: 'layout-shift', buffered: true }); };
const total = p => p.evaluate(() => window.__ls.reduce((s, e) => s + e.v, 0));

async function open(b, watch, vp, { query = '', status = 200, delay = 0, reduce = false } = {}) {
  const ctx = await b.newContext({ ...vp, reducedMotion: reduce ? 'reduce' : 'no-preference' });
  await ctx.addInitScript(shifts);
  const p = await ctx.newPage(); watch(p, /sunday-light-enquiry/);
  const posted = [];
  await p.route(HOOK, r => { posted.push(r.request().postData()); setTimeout(() => r.fulfill({ status, body: '{}' }), delay); });
  await p.goto(`${base0}/contact.html${query}`, { waitUntil: 'networkidle' });
  await p.waitForTimeout(200);
  await p.evaluate(() => { window.__ls.length = 0; });   // from here on: only what the form does
  return { p, ctx, posted };
}
let base0;
const fill = async (p, name, extra = {}) => {
  await p.fill('#name', name); await p.fill('#email', 'test@example.com');
  await p.$eval(extra.session || '#session-0', r => r.click());
  await p.fill('#message', 'An autumn wedding in the hills');
  if (extra.company) await p.$eval('#company', el => { el.value = 'bot'; });
};
const send = p => p.$eval('#enquiry-form', f => f.requestSubmit());

module.exports = async ({ browser: b, base, ok, watch }) => {
  base0 = base;
  {   // a session link arrives with its chip chosen
    const { p, ctx } = await open(b, watch, PHONE, { query: '?session=Couples%2C+engagement+or+proposal' });
    ok(await p.$eval('#session-1', r => r.checked && r.value === 'Couples, engagement or proposal') &&
       (await p.$$eval('[name="session"]:checked', l => l.length)) === 1, 'form: ?session= checks the matching chip');
    const first = await p.$eval('#name', el => el.getBoundingClientRect().bottom);
    ok(first < 844, `form: the first field is in the first phone screen (bottom ${Math.round(first)}px)`);
    await ctx.close();
  }
  for (const vp of [PHONE, DESKTOP]) {
    const w = vp.viewport.width;
    {   // validation
      const { p, ctx } = await open(b, watch, vp);
      await p.click('.btn--send');
      await p.waitForTimeout(400);
      const s = await p.evaluate(() => {
        const sum = document.getElementById('form-summary');
        return { shown: !sum.hidden, focused: document.activeElement === sum, title: sum.querySelector('h2').textContent,
          links: [...sum.querySelectorAll('li:not([hidden]) a')].map(a => [a.getAttribute('href'), a.textContent]) };
      });
      ok(s.shown && s.focused && s.title === 'Four things to check' && s.links.length === 4 &&
         s.links.map(l => l[0]).join() === '#name,#email,#session-0,#message' && s.links.every(l => l[1].length > 10),
         `form ${w}: an empty send fills and focuses the summary ("${s.title}", ${s.links.length} links)`);
      const inv = await p.evaluate(() => ['name', 'email', 'message'].map(n => {
        const el = document.getElementById(n), err = document.getElementById(el.getAttribute('aria-describedby'));
        return el.getAttribute('aria-invalid') === 'true' && err && err.textContent.trim().length > 10 && err.classList.contains('is-on');
      }).concat([[...document.querySelectorAll('[name="session"]')].every(r => r.getAttribute('aria-invalid') === 'true' && r.getAttribute('aria-describedby') === 'err-session')]));
      ok(inv.every(Boolean), `form ${w}: inline errors with aria-invalid and aria-describedby; every session chip invalid together`);
      ok((await p.textContent('#err-name')).trim() === 'Add your name so I know who I’m writing to.' &&
         (await p.textContent('#err-session')).trim() === 'Choose the kind of session.', `form ${w}: the error copy is the spec's`);
      // a fixed field clears as soon as it is right; the chips clear on choosing
      await p.focus('#email'); await p.keyboard.type('sam@');
      ok((await p.getAttribute('#email', 'aria-invalid')) === 'true', `form ${w}: a half-typed fix leaves the message until it is right`);
      await p.keyboard.type('example.com');
      ok((await p.getAttribute('#email', 'aria-invalid')) === null && (await p.textContent('#err-email')).trim() === '', `form ${w}: a fixed field clears while typing`);
      await p.$eval('#session-2', r => r.click());
      ok(await p.$$eval('[name="session"]', l => l.every(r => !r.hasAttribute('aria-invalid'))) && (await p.textContent('#err-session')).trim() === '', `form ${w}: choosing a chip clears the group`);
      ok(await total(p) === 0 || (await p.evaluate(() => window.__ls.every(e => e.input))), `form ${w}: validation moves nothing except the summary the visitor asked for`);
      await ctx.close();
    }
    {   // typing never adds an error; blur after typing does
      const { p, ctx } = await open(b, watch, vp);
      await p.focus('#email'); await p.keyboard.type('not-an-email');
      const typing = await p.getAttribute('#email', 'aria-invalid');
      await p.focus('#phone');
      const blurred = await p.getAttribute('#email', 'aria-invalid');
      await p.focus('#name'); await p.focus('#date');   // tabbing through without typing adds nothing
      ok(typing === null && blurred === 'true' && (await p.textContent('#err-email')).trim() === 'That email doesn’t look quite right.' &&
         (await p.getAttribute('#name', 'aria-invalid')) === null, `form ${w}: typing never adds an error; blur after typing checks the field`);
      await p.focus('#session-0'); await p.focus('#date');
      ok((await p.getAttribute('#session-0', 'aria-invalid')) === 'true', `form ${w}: leaving the chips without choosing checks the group`);
      ok((await p.evaluate(() => window.__ls.length)) === 0, `form ${w}: messages appear in reserved space (no layout shift at all)`);
      await ctx.close();
    }
    {   // sending, then success
      const { p, ctx, posted } = await open(b, watch, vp, { delay: 900 });
      await fill(p, 'Test Person');
      await send(p); await p.waitForTimeout(150); await send(p);
      const busy = await p.evaluate(() => {
        const f = document.getElementById('enquiry-form'), btn = f.querySelector('button');
        return { busy: f.getAttribute('aria-busy'), dis: btn.getAttribute('aria-disabled'), cls: f.classList.contains('is-sending'),
          caption: getComputedStyle(document.getElementById('form-status')).visibility, live: document.getElementById('form-live').textContent };
      });
      const name = await p.locator('.btn--send').evaluate(el => el.textContent.replace(/\s+/g, ' ').trim());
      ok(busy.busy === 'true' && busy.dis === 'true' && busy.cls && busy.caption === 'visible' && busy.live === 'Sending…' && name === 'Send enquiry',
         `form ${w}: while sending: aria-busy, aria-disabled, the in-flight rule, "Sending…" (button still "${name}")`);
      await p.waitForTimeout(2200);
      ok(posted.length === 1, `form ${w}: a second send while one is in flight is ignored (${posted.length} sent)`);
      const data = JSON.parse(posted[0] || '{}');
      ok(Object.keys(data).join() === KEYS.join() && data.heard === '' && !('company' in data) && data.session === 'Wedding' && data.name === 'Test Person',
         `form ${w}: the payload keeps its keys (${Object.keys(data).join(', ')}), heard "" when unchosen, no company`);
      const s = await p.evaluate(() => {
        const f = document.getElementById('enquiry-form'), card = document.getElementById('form-success'), h = document.getElementById('success-title');
        const live = document.getElementById('form-live'), cs = getComputedStyle(card), hs = getComputedStyle(h);
        return { title: h.textContent, focused: document.activeElement === h, outline: hs.outlineStyle + ' ' + hs.outlineWidth,
          formHidden: getComputedStyle(f).visibility === 'hidden' && f.inert, sameCell: card.parentElement === f.parentElement && cs.gridArea === getComputedStyle(f).gridArea,
          sticky: cs.position, shown: !card.hidden && card.getBoundingClientRect().height > 200, live: live.textContent, outside: !f.contains(live) && !card.contains(live) };
      });
      ok(s.title === 'Thank you, Test.' && s.shown && s.sameCell && s.sticky === 'sticky', `form ${w}: success shows "${s.title}" in the form's own cell, sticky`);
      ok(s.focused && s.outline === 'solid 2px' && s.formHidden, `form ${w}: focus on the thank-you heading with a visible outline; the form hidden and inert`);
      ok(s.live === 'Enquiry sent. Thank you, Test.' && s.outside, `form ${w}: the announcement comes from the live region outside the form ("${s.live}")`);
      ok(await total(p) < .001, `form ${w}: no layout shift through sending and success (${(await total(p)).toFixed(4)})`);
      await ctx.close();
    }
    {   // failure
      const { p, ctx } = await open(b, watch, vp, { status: 500, delay: 700 });
      await fill(p, 'Test Person');
      await send(p); await p.waitForTimeout(1300);
      const f = await p.evaluate(() => {
        const err = document.getElementById('form-error'), form = document.getElementById('enquiry-form');
        return { inReport: !!err.closest('.form-report'), shown: !err.hidden && err.getBoundingClientRect().height > 40, focused: document.activeElement === err,
          kept: document.getElementById('message').value === 'An autumn wedding in the hills' && document.getElementById('session-0').checked,
          restored: !form.hasAttribute('aria-busy') && !form.classList.contains('is-sending') && !form.querySelector('button').hasAttribute('aria-disabled'),
          live: document.getElementById('form-live').textContent, fits: err.getBoundingClientRect().height <= err.closest('.form-report').getBoundingClientRect().height };
      });
      ok(f.inReport && f.shown && f.focused && f.kept && f.restored && f.fits, `form ${w}: failure shows the error in the reserved report, focused, values kept, button restored`);
      ok(/didn’t send/.test(f.live), `form ${w}: the failure is announced ("${f.live}")`);
      ok(await total(p) < .001, `form ${w}: no layout shift on failure (${(await total(p)).toFixed(4)})`);
      await ctx.close();
    }
    {   // the honeypot: the finished card at once, nothing sent
      const { p, ctx, posted } = await open(b, watch, vp);
      await fill(p, 'Test Person', { company: true });
      await send(p); await p.waitForTimeout(100);
      const h = await p.evaluate(() => ({ shown: !document.getElementById('form-success').hidden, playing: document.querySelector('.enquire-slot').classList.contains('is-sent'),
        anims: document.getAnimations().filter(a => document.getElementById('form-success').contains(a.effect && a.effect.target)).length }));
      ok(h.shown && !h.playing && h.anims === 0 && posted.length === 0, `form ${w}: the honeypot gets the finished card at once and nothing is sent`);
      ok((await p.evaluate(() => window.__ls.length)) === 0, `form ${w}: no layout shift for the honeypot`);
      await ctx.close();
    }
  }
  {   // the name rules (M09)
    const names = [['Mr Smith', 'Thank you.'], ['the Smiths', 'Thank you.'], ['Dr. Jones', 'Thank you.'], ['Sam & Alex', 'Thank you, Sam & Alex.'],
      ['Alexandra and Christopher Smith', 'Thank you.'], ['sam', 'Thank you, Sam.'], ['JO-ANNE', 'Thank you, Jo-anne.'], ['McKenzie Smith', 'Thank you, McKenzie.'],
      ['Theo Grant', 'Thank you, Theo.'], ['  Zoë  ', 'Thank you, Zoë.'], ['J.', 'Thank you.'], ['1234', 'Thank you.']];
    const got = [];
    for (const [name, want] of names) {
      const { p, ctx } = await open(b, watch, DESKTOP, { reduce: true });
      await fill(p, name); await send(p);
      await p.waitForFunction(() => !document.getElementById('form-success').hidden);
      const t = await p.textContent('#success-title');
      if (t !== want) got.push(`"${name}" → "${t}" (want "${want}")`);
      await ctx.close();
    }
    ok(!got.length, 'form: the thank-you uses a clear first name, a couple whole up to 24 characters, never a title' + (got.length ? ': ' + got.join(' | ') : ''));
  }
  {   // reduced motion: a calm crossfade and the sketch already drawn
    const { p, ctx } = await open(b, watch, PHONE, { reduce: true, delay: 600 });
    await fill(p, 'Test Person'); await send(p); await p.waitForTimeout(1200);
    const r = await p.evaluate(() => ({ focused: document.activeElement.id, playing: document.querySelector('.enquire-slot').classList.contains('is-sent'),
      dash: [...document.querySelectorAll('#success-mark path[pathLength]')].map(el => parseFloat(getComputedStyle(el).strokeDashoffset) || 0) }));
    ok(r.focused === 'success-title' && !r.playing && r.dash.every(d => d === 0), 'form (reduced motion): the card fades in with the sketch drawn, then focus');
    await ctx.close();
  }
  {   // no JS: a real form that posts (never a GET with details in the URL)
    const ctx = await b.newContext({ ...PHONE, javaScriptEnabled: false });
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/contact.html`, { waitUntil: 'networkidle' });
    const f = await p.$eval('#enquiry-form', f => ({ method: f.getAttribute('method'), action: f.getAttribute('action'), novalidate: f.noValidate,
      required: [...f.querySelectorAll('[required]')].map(e => e.name).filter((v, i, a) => a.indexOf(v) === i).join(),
      chipsUsable: getComputedStyle(f.querySelector('.chip-input')).pointerEvents !== 'none', hidden: !!f.closest('[hidden]') }));
    ok(f.method === 'post' && /webhook\/sunday-light-enquiry$/.test(f.action) && !f.novalidate && f.required === 'name,email,session,message' && f.chipsUsable && !f.hidden,
       'form (no JS): posts to the webhook, the browser checks the required fields, chips usable');
    await p.$eval('#session-3', r => r.click());
    ok(await p.$eval('#session-3', r => r.checked && getComputedStyle(r.nextElementSibling).backgroundColor !== 'rgba(0, 0, 0, 0)'), 'form (no JS): a chip checks and shows it');
    await ctx.close();
  }
};
