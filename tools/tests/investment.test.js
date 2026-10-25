// Investment (spec §4.14-4.17, §5.3, plan WP3): her prices, packages, inclusions and terms reach the page byte for byte;
// photo rows and carte rows follow the photo files; the split hero holds the preloaded LCP photo; tiers as arch cards
// and arch rows, none highlighted; the steps ledger; the FAQ; the hours of light (M08) and its finished frame.
const { context, scrollTo, PHONE, DESKTOP } = require('./lib');

const GALLERY = ['Gallery', 'Every edited image in a professional online gallery'];   // her inclusion, on every session that lists it
const SPEC = {   // spec §6.3, label → value, in her order
  weddings: [['Coverage', 'Five packages, from 4 to 12 hours of coverage'], ['Previews', 'Sneak peeks within 24 hours'],
             ['Before the day', 'A pre-wedding consultation'], ['Investment', 'From $1,700']],
  couples: [['Time', 'About 45 minutes'], GALLERY, ['Where', 'Your choice of location around Adelaide (travel further out can be quoted)'], ['Investment', '$350']],
  family: [['Time', '45 to 60 minutes'], GALLERY, ['Who', 'Up to five people, then $25 for each extra person'],
           ['Where', 'Your choice of location around Adelaide (travel further out can be quoted)'], ['Investment', '$400']],
  maternity: [['Time', 'About 45 minutes'], GALLERY, ['Where', 'Your choice of location around Adelaide (travel further out can be quoted)'],
              ['Packages', 'Maternity and newborn packages available'], ['Investment', '$350']],
  newborn: [GALLERY, ['Where', 'At your home or an outdoor location'], ['Packages', 'Maternity and newborn packages available'], ['Investment', '$350']],
};
const TIERS = ['Basic|Up to 4 hours|$1,700', 'Standard|Up to 6 hours|$2,100', 'Premium|Up to 8 hours|$2,500', 'Deluxe|Up to 10 hours|$2,900', 'Ultimate|Up to 12 hours|$3,300'];
const INCLUDES = ['Continuous coverage for the hours you choose', 'A fully edited digital gallery', 'Sneak peeks within 24 hours', 'A pre-wedding consultation'];
const TERMS = ['Your full gallery within three months', 'A 25% non-refundable deposit secures your date',
               'Payment plans available, with the balance due 14 days before the wedding'];
const FORM = { weddings: 'Wedding', couples: 'Couples, engagement or proposal', family: 'Family', maternity: 'Maternity', newborn: 'Newborn' };
const PHOTO = { weddings: 'images/weddings/castle-balcony.jpg', couples: 'images/weddings/jaguar-flare.jpg', family: 'images/sessions/family.jpg',
                maternity: 'images/sessions/maternity.jpg', newborn: 'images/sessions/newborn.jpg' };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

module.exports = async ({ browser: b, base, ok, watch }) => {
  const exists = {};
  for (const [id, path] of Object.entries(PHOTO)) exists[id] = (await fetch(`${base}/${path}`, { method: 'HEAD' })).ok;

  {   // content, byte for byte, and structure
    const ctx = await context(b, 'reduced', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    const d = await p.evaluate(() => {
      const t = el => el ? el.textContent : null, all = (s, r = document) => [...r.querySelectorAll(s)];
      const sessions = {};
      all('article.session').forEach(a => {
        const link = a.querySelector('.session-action a');
        sessions[a.id] = { kind: a.classList.contains('session--word') ? 'carte' : 'photo', photo: !!a.querySelector('.session-photo img'),
          title: t(a.querySelector('h2')), rows: all('.spec > div', a).map(r => [t(r.querySelector('dt')), t(r.querySelector('dd'))]),
          priceClass: a.querySelector('.spec > div:last-child dd').className, last: a.querySelector('.spec > div:last-child').className,
          rules: a.querySelector('.spec').hasAttribute('data-rules'), link: link && [link.getAttribute('href'), link.textContent], links: all('a', a).length };
      });
      const bg = el => el ? getComputedStyle(el).backgroundColor : null;
      return { sessions, order: all('main > *').map(el => el.id || el.className.split(' ')[0]),
        bgs: ['#weddings', '#wedding-packages', '#couples', '.carte', '.how', '.questions', '.closing'].map(s => bg(document.querySelector(s))),
        paper: getComputedStyle(document.body).backgroundColor,
        tiers: all('.tier').map(li => [t(li.querySelector('.tier-name')), t(li.querySelector('.tier-hours')), t(li.querySelector('.tier-price'))].join('|')),
        tierLook: all('.tier').map(li => li.className + ' ' + li.attributes.length + ' ' + bg(li) + ' ' + getComputedStyle(li).transform + ' ' + getComputedStyle(li.querySelector('.tier-name')).fontSize),
        hours: all('.tier').map(li => li.dataset.hours), arcs: all('.tier .tier-sky > svg.tier-arc').length,
        notes: all('.tier-notes > div').map(n => [t(n.querySelector('h3')), all('li', n).map(t)]),
        packagesLead: t(document.querySelector('.packages .head--split .lead')),
        cta: [document.querySelector('.packages .actions .btn--primary').getAttribute('href'), t(document.querySelector('.packages .actions .btn-label'))],
        index: [document.querySelector('.index-bar').getAttribute('aria-label'), all('.index-bar a').map(a => a.getAttribute('href') + ' ' + a.dataset.spy + ' ' + a.textContent)],
        carteLabel: t(document.querySelector('.carte > .wrap > .eyebrow')),
        steps: all('.steps > li.step').map(li => [t(li.querySelector('.t-numeral')), t(li.querySelector('h3')), !!li.querySelector('.step-marker .step-sun'), !!li.querySelector('.step-glow')]),
        qa: all('.faq > details.qa').map(dt => [dt.hasAttribute('name'), !!dt.querySelector('summary > .qa-row > .t-question + svg .pm-v')]),
        faqHead: [t(document.querySelector('.faq-head h2')), t(document.querySelector('.faq-head p')), (document.querySelector('.faq-head a') || {}).href],
        closing: document.querySelector('#closing-title').innerText.replace(/\s+/g, ' ').trim(),
        retired: ['.package', '.packages-text', '.window', '.sheet', '.tier-number', '.center-title', 'blockquote'].filter(s => document.querySelector(s)),
        h2s: all('h2').map(t),
        lcp: (() => { const i = document.querySelector('img[data-lcp]'); return i && { src: i.currentSrc, hi: i.getAttribute('fetchpriority'), lazy: i.hasAttribute('loading'),
          inHero: !!i.closest('section.inv-hero.sec--flush'), look: [getComputedStyle(i).transform, getComputedStyle(i).filter, getComputedStyle(i).opacity].join(' ') }; })(),
        preload: (document.querySelector('link[rel="preload"][as="image"]') || {}).getAttribute?.('imagesrcset') || '',
        preloadFirst: document.head.firstElementChild.matches('meta') && document.querySelector('head link').matches('link[rel="preload"][as="image"]'),
      };
    });
    const ids = ['weddings', 'couples', 'family', 'maternity', 'newborn'];
    ok(ids.every(id => d.sessions[id] && d.sessions[id].kind === (exists[id] ? 'photo' : 'carte') && d.sessions[id].photo === exists[id]),
       'photo rows for the sessions whose photo file exists, carte rows for the rest (' + ids.map(id => id + ':' + (d.sessions[id] || {}).kind).join(', ') + ')');
    ok(ids.every(id => same(d.sessions[id].rows, SPEC[id])), 'every spec-sheet label and value byte for byte, in her order, the Gallery row on every session that lists it' +
       (ids.every(id => same(d.sessions[id].rows, SPEC[id])) ? '' : ': ' + JSON.stringify(ids.map(id => d.sessions[id].rows))));
    ok(ids.map(id => d.sessions[id].rows.at(-1)[1]).join(' / ') === 'From $1,700 / $350 / $400 / $350 / $350' &&
       ids.every(id => d.sessions[id].priceClass === 't-price' && d.sessions[id].last === 'spec-price' && d.sessions[id].rules),
       'session prices From $1,700 / $350 / $400 / $350 / $350, each the last row of a ruled sheet');
    ok(same(d.sessions.weddings.link, ['#wedding-packages', 'See the five packages']) && d.sessions.weddings.links === 1,
       'the Weddings row has one action: "See the five packages" → #wedding-packages');
    ok(ids.slice(1).every(id => { const [href, text] = d.sessions[id].link, u = new URL(href, base + '/');
      return u.pathname.endsWith('/contact.html') && u.searchParams.get('session') === FORM[id] && text === 'Enquire about ' + (id === 'couples' ? 'couples' : id) && d.sessions[id].links === 1; }),
       'every other session has one action, "Enquire about …", to the form with its own session chosen');
    ok(d.sessions.couples.title === 'Couples, engagements & proposals' && ['family', 'maternity', 'newborn'].every(id => d.sessions[id].title === id[0].toUpperCase() + id.slice(1)),
       'session titles: her names; the carte words are the short names');
    ok(d.carteLabel === 'Family, maternity & newborn', `the carte eyebrow is built from the names (${d.carteLabel})`);
    ok(same(d.tiers, TIERS) && same(d.hours, ['4', '6', '8', '10', '12']) && d.arcs === 5, 'tiers: names, "Up to 4 hours" … "Up to 12 hours" and prices byte for byte, each with its sun path');
    ok(new Set(d.tierLook).size === 1, 'no tier is highlighted (identical classes, attributes and looks)');
    ok(same(d.notes, [['Every package includes', INCLUDES], ['Good to know', TERMS]]), 'the wedding inclusions and terms, exactly');
    ok(d.packagesLead === 'The packages differ only in hours. Everything else is the same in every one.', `the packages lead (${d.packagesLead})`);
    ok(new URL(d.cta[0], base + '/').searchParams.get('session') === 'Wedding' && d.cta[1] === 'Check my wedding dates', 'packages CTA: "Check my wedding dates" → the form with Wedding chosen');
    ok(d.index[0] === 'Sessions' && same(d.index[1], ['#weddings weddings wedding-packages Weddings', '#couples couples Couples', '#family family Family', '#maternity maternity Maternity', '#newborn newborn Newborn']),
       'index bar "Sessions": five links, Weddings also spying on the packages');
    ok(same(d.order, ['inv-hero', 'index-bar', 'weddings', 'wedding-packages', 'couples', 'carte', 'how', 'questions', 'closing']),
       'section order: hero, index, Weddings, packages, Couples, carte, How it works, Questions, closing (' + d.order.join(' → ') + ')');
    const L = 'rgb(236, 230, 219)';
    ok(same(d.bgs.map(c => c === L ? 'L' : (c === 'rgba(0, 0, 0, 0)' || c === d.paper) ? 'P' : c), ['P', 'L', 'P', 'P', 'L', 'P', 'P']),
       'backgrounds: Paper, Limestone band, Paper, Paper, Limestone, Paper, Paper (' + d.bgs.join(', ') + ')');
    ok(same(d.steps, [['i.', 'Say hello', true, false], ['ii.', 'Plan it together', true, false], ['iii.', 'The session', true, false], ['iv.', 'Your gallery', true, true]]),
       'steps: lower-roman numerals, a sun on each, the last one glowing');
    ok(d.qa.length === 5 && d.qa.every(([named, row]) => !named && row), 'FAQ: five native details, none with a name, each summary a .qa-row with the B5 plus');
    ok(d.faqHead[0] === 'Questions, answered' && d.faqHead[1] === 'Still wondering? Message me on Instagram.' && /instagram\.com\/cwatson\.creative/.test(d.faqHead[2]), 'FAQ head copy and its Instagram link');
    ok(d.closing === 'Let’s plan your session.', `the closing shows the Investment line (${d.closing})`);
    ok(!d.retired.length && !d.h2s.includes('Sessions'), 'the window hero, lime cards, "Sessions" heading, old tiers and the strip are gone' + (d.retired.length ? ': ' + d.retired.join(', ') : ''));
    ok(d.lcp && /jaguar-veil/.test(d.lcp.src) && d.lcp.hi === 'high' && !d.lcp.lazy && d.lcp.inHero && d.lcp.look === 'none none 1' && /jaguar-veil/.test(d.preload) && d.preloadFirst,
       'the hero photo is the LCP: jaguar-veil, high priority, never lazy, preloaded first, untouched');
    await ctx.close();
  }

  for (const vp of [PHONE, DESKTOP]) {   // layout
    const ctx = await context(b, 'reduced', vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    const w = vp.viewport.width;
    const r = await p.evaluate(() => {
      const box = s => { const r = document.querySelector(s).getBoundingClientRect(); return { l: r.left, r: r.right, t: r.top + scrollY, b: r.bottom + scrollY, w: r.width, h: r.height }; };
      const tiers = [...document.querySelectorAll('.tier')].map(li => { const r = li.getBoundingClientRect(), s = li.querySelector('.tier-sky').getBoundingClientRect();
        return { t: Math.round(r.top), w: r.width, sky: [Math.round(s.width), Math.round(s.height)], radius: getComputedStyle(li).borderTopLeftRadius, leader: getComputedStyle(li, '::after').backgroundImage }; });
      const sun = document.querySelector('.tier-arc .sun').getBoundingClientRect(), arc = document.querySelector('.tier-arc').getBoundingClientRect();
      return { vw: Math.round(document.querySelector('main').getBoundingClientRect().right), photo: box('.inv-hero-photo'), h1: box('.inv-hero h1'), tiers,
        sunHalf: Math.abs((sun.top + sun.bottom) / 2 - arc.bottom) < 1 && Math.abs((sun.left + sun.right) / 2 - arc.right) < 1 && getComputedStyle(document.querySelector('.tier-arc')).clipPath !== 'none',
        light: [...document.querySelectorAll('.tier-arc .light')].map(l => getComputedStyle(l).strokeDashoffset),
        hosts: [...document.querySelectorAll('.tiers, .tier, .faq, .qa summary, .steps, .step, .spec > div')].every(el => getComputedStyle(el).position !== 'static'),
        rows: [...document.querySelectorAll('.qa summary')].map(s => Math.round(s.getBoundingClientRect().height)),
        weddings: [box('#weddings .session-photo'), box('#weddings .session-text')], couples: [box('#couples .session-photo'), box('#couples .session-text')] };
    });
    if (w === 390) {
      ok(r.photo.t < r.h1.t && Math.round(r.photo.l) === 0 && Math.round(r.photo.r) === r.vw && Math.abs(r.photo.h / r.photo.w - 1.25) < .01,
         '390: the hero photo comes first, full-bleed, 4:5');
      ok(r.tiers.every(t => t.sky[0] === 52 && t.sky[1] === 70 && /radial-gradient/.test(t.leader)) && new Set(r.tiers.map(t => t.t)).size === 5,
         '390: tiers are arch rows, each with a 52×70 mini arch and a dotted leader');
      ok([...r.weddings, ...r.couples].every(b => b) && Math.round(r.weddings[0].l) === 0 && Math.round(r.weddings[0].r) === r.vw && r.weddings[0].b <= r.weddings[1].t,
         '390: session photos run full-bleed above their words');
    } else {
      ok(Math.round(r.photo.r) === r.vw && r.photo.l >= r.vw / 2 - 1 && r.h1.r <= r.photo.l && r.photo.h >= 800,
         `1440: the split hero bleeds to the right edge (${Math.round(r.photo.l)}–${Math.round(r.photo.r)} of ${r.vw}), words on the left`);
      ok(new Set(r.tiers.map(t => t.t)).size === 1 && r.tiers.every(t => t.w >= 145 && t.w <= 210 && t.radius !== '0px' && t.leader === 'none'),
         '1440: five arch-topped cards in one row (' + r.tiers.map(t => Math.round(t.w)).join(', ') + 'px)');
      ok(r.weddings[0].r < r.weddings[1].l && r.couples[1].r < r.couples[0].l, '1440: the Weddings photo sits left, the Couples row mirrors');
    }
    ok(r.sunHalf && r.light.every(v => parseFloat(v) === 0), `${w}: arcs lit to sunset and every sun half set on the right horizon`);
    ok(r.hosts, `${w}: every drawn rule sits on its own row or list (positioned hosts)`);
    ok(r.rows.every(h => h >= 56), `${w}: FAQ rows are at least 56px (${r.rows.join(', ')})`);
    await ctx.close();
  }

  {   // spec rows stack under 400px, sit side by side from 400px
    const ctx = await context(b, 'reduced', { viewport: { width: 399, height: 800 } });
    const p = await ctx.newPage(); watch(p);
    const look = () => p.$eval('#couples .spec > div', d => { const a = d.querySelector('dt').getBoundingClientRect(), b = d.querySelector('dd').getBoundingClientRect(); return b.top >= a.bottom - 1 ? 'stacked' : b.left > a.right ? 'side' : 'other'; });
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    const narrow = await look();
    await p.setViewportSize({ width: 400, height: 800 });
    const wide = await look();
    ok(narrow === 'stacked' && wide === 'side', `spec rows stack under 400px (${narrow}) and sit side by side from 400px (${wide})`);
    await ctx.close();
  }

  {   // FAQ by keyboard; the plus becomes a minus
    const ctx = await context(b, 'reduced', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    await p.focus('.qa summary');
    const st = () => p.$eval('.qa', d => ({ open: d.open, v: getComputedStyle(d.querySelector('.pm-v')).transform, body: d.querySelector('.qa-body').getBoundingClientRect().height }));
    const a = await st(); await p.keyboard.press('Enter'); const b1 = await st(); await p.keyboard.press(' '); const c = await st();
    ok(!a.open && b1.open && b1.body > 0 && !c.open, 'the FAQ opens with Enter and closes with Space');
    ok(a.v === 'none' && /^matrix\((-?0|[0-9.e-]+), 1, -1, (-?0|[0-9.e-]+), 0, 0\)$/.test(b1.v), `open, the plus is a minus (vertical stroke turned flat: ${b1.v})`);
    await ctx.close();
  }

  for (const width of [1099, 1440]) {   // the FAQ head is sticky from 1100px, clear of the header and the index bar
    const ctx = await context(b, 'motion', { viewport: { width, height: 900 } });
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    const y = await p.$eval('.faq', f => f.getBoundingClientRect().top + scrollY);
    for (const dy of [-400, -200, -60]) { await scrollTo(p, y + dy); await p.waitForTimeout(60); }   // arrive from above (the header hides),
    await scrollTo(p, y - 80); await p.waitForTimeout(500);                                          // then a little back up (it returns)
    const s = await p.evaluate(() => {
      const h = document.querySelector('.faq-head').getBoundingClientRect(), bar = document.querySelector('.index-bar').getBoundingClientRect(),
        hd = document.querySelector('.site-header').getBoundingClientRect();
      return { pos: getComputedStyle(document.querySelector('.faq-head')).position, top: Math.round(h.top), clear: Math.round(h.top - Math.max(bar.bottom, hd.bottom)) };
    });
    ok(width < 1100 ? s.pos !== 'sticky' : s.pos === 'sticky' && s.clear >= 0, `${width}: FAQ head ${s.pos}` + (width >= 1100 ? `, ${s.clear}px clear of the header and index bar` : ''));
    await ctx.close();
  }

  {   // M08 hours of light: armed below the fold, lit once 90% is in view, every sun lands at 1200ms
    const ctx = await context(b, 'motion', DESKTOP);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    const armed = await p.$eval('.tiers', t => ({ cls: t.className, dash: getComputedStyle(t.querySelector('.light')).strokeDashoffset, sun: getComputedStyle(t.querySelector('.sun-arm')).opacity }));
    ok(/\bis-armed\b/.test(armed.cls) && parseFloat(armed.dash) > 1 && armed.sun === '0', `the tiers wait below the fold: light hidden, suns away (${armed.dash}, ${armed.sun})`);
    await p.$eval('.tiers', t => window.scrollTo({ top: t.getBoundingClientRect().top + scrollY - 200, behavior: 'instant' }));
    await p.waitForFunction(() => document.querySelector('.tiers').classList.contains('is-lit'), null, { timeout: 3000 });
    const t = await p.evaluate(() => document.getAnimations().filter(a => a.transitionProperty && !a.effect.pseudoElement && a.effect.target.closest('.tiers'))
      .map(a => a.transitionProperty + ' ' + Math.round(a.effect.getTiming().delay + a.effect.getTiming().duration)));
    const ends = t.filter(x => /^(stroke-dashoffset|transform) /.test(x)).map(x => +x.split(' ')[1]);
    ok(ends.length === 10 && ends.every(e => Math.abs(e - 1200) <= 1), `every light and sun ends together at 1200ms (${ends.join(', ')})`);
    await p.waitForTimeout(1500);
    const lit = await p.$$eval('.tier-arc', s => s.map(a => getComputedStyle(a.querySelector('.light')).strokeDashoffset + ' ' + getComputedStyle(a.querySelector('.sun-arm')).transform + ' ' + getComputedStyle(a.querySelector('.sun-arm')).opacity));
    ok(lit.every(x => x === '0px none 1' || x === '0 none 1'), 'lit: every arc drawn to sunset, every sun home and half set (' + lit[0] + ')');
    await ctx.close();
  }

  for (const state of ['reduced', 'still', 'nojs']) {   // finished frames
    const ctx = await context(b, state, PHONE);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    await p.$eval('.tiers', t => window.scrollTo({ top: t.getBoundingClientRect().top + scrollY - 200, behavior: 'instant' })); await p.waitForTimeout(300);
    const f = await p.evaluate(() => ({ arcs: [...document.querySelectorAll('.tier-arc')].map(a => [getComputedStyle(a.querySelector('.light')).strokeDashoffset, getComputedStyle(a.querySelector('.sun-arm')).transform, getComputedStyle(a.querySelector('.sun-arm')).opacity].join(' ')),
      rules: [...document.querySelectorAll('.tier, .spec > div, .qa summary')].map(el => getComputedStyle(el, '::before').transform).concat([...document.querySelectorAll('.step')].map(el => getComputedStyle(el, '::after').transform)) }));
    ok(f.arcs.every(x => /^0(px)? none 1$/.test(x)) && f.rules.every(x => x === 'none'), `${state}: arcs lit to sunset, suns half set, every rule drawn`);
    if (state === 'nojs') {
      await p.click('.qa summary');
      ok(await p.$eval('.qa', d => d.open), 'no-JS: the FAQ opens natively');
    }
    await ctx.close();
  }

  for (const vp of [PHONE, DESKTOP]) {   // a cold load at #family: what is in view is finished at once (never armed, never half drawn)
    const ctx = await context(b, 'motion', vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html#family`, { waitUntil: 'networkidle' }); await p.waitForTimeout(150);
    const r = await p.evaluate(() => {
      const inView = el => { const r = el.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight; };
      return { armed: [...document.querySelectorAll('.is-armed')].filter(inView).map(el => el.className),
        half: [...document.querySelectorAll('#family .spec > div')].filter(inView).map(d => getComputedStyle(d, '::before').transform).filter(t => t !== 'none').length,
        spec: document.querySelector('#family .spec').className };
    });
    ok(!r.armed.length && !r.half && /is-done/.test(r.spec), `${vp.viewport.width}: a cold load at #family shows its rules drawn, nothing armed in view (${r.spec})`);
    await ctx.close();
  }

  for (const vp of [PHONE, DESKTOP]) {   // the old sessions.html#bump (now Maternity) lands on Maternity, its heading clear of the bars
    const ctx = await context(b, 'reduced', vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html#bump`, { waitUntil: 'networkidle' }); await p.waitForTimeout(300);
    const r = await p.evaluate(() => {
      const bar = document.querySelector('.index-bar').getBoundingClientRect(), h = document.querySelector('#maternity h2').getBoundingClientRect();
      return { gap: Math.round(h.top - bar.bottom), inView: h.bottom < innerHeight, name: document.querySelector('#maternity h2').textContent,
        current: (document.querySelector('.index-bar a[aria-current]') || {}).textContent };
    });
    ok(r.gap >= 0 && r.inView && r.name === 'Maternity' && r.current === 'Maternity',
       `${vp.viewport.width}: an old #bump link lands on Maternity below the bar (${r.gap}px, current ${r.current})`);
    await ctx.close();
  }

  for (const vp of [PHONE, DESKTOP]) {   // a jump from the index bar lands with the heading clear and nothing half drawn
    const ctx = await context(b, 'motion', vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/investment.html`, { waitUntil: 'networkidle' });
    await p.click('.index-bar a[href="#family"]'); await p.waitForTimeout(2200);
    const r = await p.evaluate(() => {
      const bar = document.querySelector('.index-bar').getBoundingClientRect(), h = document.querySelector('#family h2').getBoundingClientRect();
      return { gap: Math.round(h.top - bar.bottom), current: (document.querySelector('.index-bar a[aria-current]') || {}).textContent,
        half: [...document.querySelectorAll('#family .spec > div')].map(d => getComputedStyle(d, '::before').transform).filter(t => t !== 'none').length };
    });
    ok(r.gap >= 0 && r.current === 'Family' && !r.half, `${vp.viewport.width}: the Family link lands below the bar (${r.gap}px), Family current, its rules drawn`);
    await ctx.close();
  }
};
