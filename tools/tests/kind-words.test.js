// Kind words (spec §6.1, §5.5, §4.13). With no real reviews: no review text, name or quote reaches any page, and the
// Kind words page is the honest holding state (out of search, her photo, the Instagram sheet). With real reviews
// (content.KIND_WORDS): every review appears on Kind words exactly as written, with its names and session; a photo
// sits beside a review only when it is of the people who wrote it; the page is in search; Home and Investment carry
// the interlude; nothing else on the site quotes anyone. Contact has neither closing nor sheet either way.
const { execFileSync } = require('child_process');
const path = require('path');
const { PAGES, PHONE, DESKTOP } = require('./lib');

const DATA = JSON.parse(execFileSync('python3', ['-c', `
import json, sys; sys.path.insert(0, sys.argv[1])
import content as c
print(json.dumps({'holding': bool(c.KIND_WORDS_ARE_PLACEHOLDERS or not c.KIND_WORDS),
                  'reviews': [dict(names=r['names'], session=r['session'], words=r['words'], photo=r['photo'] and c.PHOTOS[r['photo']][0])
                              for r in c.KIND_WORDS]}))`, path.join(__dirname, '..', 'site')]).toString());
const LEAD = 'This is where couples and families share how their sessions felt. The newest sessions go up on Instagram first.';
const BLOCKS = 'blockquote, .interlude, .story, .cite, .words, .review, q';

module.exports = async ({ browser: b, base, ok, watch }) => {
  {   // which pages carry review blocks, robots, and link previews
    const p = await b.newPage(); watch(p);
    const found = [];
    const allowed = DATA.holding ? [] : ['index', 'investment', 'kind-words'];
    for (const name of PAGES) {
      await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' });
      const r = await p.evaluate(sel => ({
        blocks: [...document.querySelectorAll(sel)].map(el => el.tagName.toLowerCase() + '.' + el.className),
        text: document.body.innerText,
        robots: (document.querySelector('meta[name="robots"]') || {}).content || '',
        desc: ['meta[name="description"]', 'meta[property="og:description"]'].map(s => (document.querySelector(s) || {}).content || '').join(' ') }), BLOCKS);
      if (r.blocks.length && !allowed.includes(name)) found.push(`${name}: ${r.blocks.join(', ')}`);
      const m = r.text.match(/will go here|placeholder|names’|Send three to six|coming soon|five stars|★/i);
      if (m) found.push(`${name}: "${m[0]}"`);
      if ((r.robots === 'noindex') !== (name === 'kind-words' && DATA.holding)) found.push(`${name}: robots "${r.robots}"`);
      if (DATA.holding && /\bsay\b|review|testimonial/i.test(r.desc)) found.push(`${name}: the link preview promises reviews ("${r.desc}")`);
    }
    ok(!found.length, `kind words: review blocks only where reviews belong (${allowed.join(', ') || 'nowhere'}), no placeholder text, robots right` + (found.length ? ': ' + found.join(' | ') : ''));
    await p.close();
  }
  for (const vp of [PHONE, DESKTOP]) {
    const w = vp.viewport.width;
    const ctx = await b.newContext(vp);
    const p = await ctx.newPage(); watch(p);
    await p.goto(`${base}/kind-words.html`, { waitUntil: 'networkidle' });
    await p.waitForTimeout(500);
    const r = await p.evaluate(() => {
      const norm = t => (t || '').replace(/\s+/g, ' ').trim();
      const head = document.querySelector('.kw-holding'), link = head && head.querySelector('a.link-arrow--external');
      return {
        h1: document.querySelector('h1').textContent, h1Bottom: document.querySelector('h1').getBoundingClientRect().bottom,
        lead: head && head.querySelector('.lead').textContent,
        link: link && [link.textContent.trim(), link.getAttribute('href')],
        stories: [...document.querySelectorAll('article.story')].map(a => ({ words: norm(a.querySelector('blockquote').textContent).replace(/^“|”$/g, ''),
          cite: norm(a.querySelector('.cite').textContent), img: (a.querySelector('img') || {}).currentSrc || null })),
        closing: (document.getElementById('closing-title') || {}).textContent,
        lcps: document.querySelectorAll('[data-lcp]').length };
    });
    ok(r.h1 === 'From the people in the photos.' && r.closing === 'Let’s plan something lovely.', `kind words ${w}: title and closing`);
    if (w < 861) ok(r.h1Bottom <= 844, `kind words ${w}: the title is in the first phone screen (bottom ${Math.round(r.h1Bottom)}px)`);
    if (DATA.holding) {
      ok(r.lead === LEAD && r.link && /instagram\.com\/selahstories\.adl/.test(r.link[1]) && !r.stories.length, `kind words ${w}: the holding head, its copy and link, no stories`);
    } else {
      const want = DATA.reviews;
      ok(r.stories.length === want.length && want.every((v, i) => r.stories[i].words === v.words && r.stories[i].cite.includes(v.names) && r.stories[i].cite.includes(v.session)),
         `kind words ${w}: every review exactly as written, with its names and session (${r.stories.map(s => s.cite).join(' | ')})`);
      ok(want.every((v, i) => v.photo ? r.stories[i].img && r.stories[i].img.includes(v.photo.split('/').pop().replace('.jpg', '')) : !r.stories[i].img),
         `kind words ${w}: a photo only beside the review of the people in it`);
    }
    await p.goto(`${base}/contact.html`, { waitUntil: 'networkidle' });
    ok(!(await p.$('.closing, .sheet')), `contact ${w}: no closing invitation and no Instagram sheet (the page is the invitation)`);
    await ctx.close();
  }
};
