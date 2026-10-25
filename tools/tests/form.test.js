// Enquiry form: a session chosen from Investment, validation, success and failure (the webhook is mocked).
module.exports = async ({ browser: b, base, ok, watch }) => {
  for (const [code, label] of [[200, 'success'], [500, 'failure']]) {
    const p = await b.newPage(); watch(p, /sunday-light-enquiry/);
    await p.route('**/webhook/sunday-light-enquiry', r => r.fulfill({ status: code, body: '{}' }));
    let posted = null;
    p.on('request', r => { if (r.url().includes('sunday-light-enquiry')) posted = r.postDataJSON(); });
    await p.goto(`${base}/contact.html?session=Couples%2C+engagement+or+proposal`);
    ok((await p.inputValue('#session')) === 'Couples, engagement or proposal', `form ${label}: arrives with the session already chosen`);
    await p.click('button[type=submit]');
    ok((await p.textContent('#form-status')).includes('Please add'), `form ${label}: empty submit asks for details`);
    await p.fill('#name', 'Test Person'); await p.fill('#email', 'test@example.com'); await p.fill('#message', 'Engagement shoot in March');
    await p.click('button[type=submit]');
    await p.waitForTimeout(800);
    if (code === 200) ok(await p.isVisible('#form-success') && posted && posted.session === 'Couples, engagement or proposal' && !('company' in posted), 'form success: thank-you shown, payload sent');
    else ok(await p.isVisible('#form-error') && (await p.inputValue('#message')) === 'Engagement shoot in March', 'form failure: error shown, details kept');
    await p.close();
  }
};
