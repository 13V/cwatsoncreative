// Kind words: while there are no real reviews, no review text, names or placeholders appear anywhere; the Kind words
// page shows an honest holding state and is kept out of search.
module.exports = async ({ browser: b, base, ok, watch }) => {
  const p = await b.newPage(); watch(p);
  for (const name of ['index', 'gallery', 'investment', 'kind-words', 'contact']) {
    await p.goto(`${base}/${name}.html`, { waitUntil: 'networkidle' });
    const html = await p.content();
    ok(!/will go here|names’|Send three to six|placeholder/i.test(html.replace(/<input[^>]*>|<textarea[^>]*>/g, '')),
       `${name}: no placeholder review text`);
    if (name !== 'kind-words') ok(!(await p.$('.words, blockquote')), `${name}: no review slider until there are real reviews`);
  }
  await p.goto(`${base}/kind-words.html`, { waitUntil: 'networkidle' });
  ok(await p.$eval('meta[name="robots"]', m => m.content === 'noindex').catch(() => false), 'kind words holding page is kept out of search');
  ok((await p.textContent('h1')).includes('From the people') && !!(await p.$('a[href*="instagram.com"]')), 'kind words holding page points to Instagram');
  await p.close();
};
