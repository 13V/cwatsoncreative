# Builds the Sunday Light pages.
#
#   python3 tools/site/build.py           # writes into the repo root
#   python3 tools/site/build.py out_dir   # or somewhere else, for a look before replacing the real pages
#
# Writes the seven HTML pages, favicon.svg and images/placeholder.svg. styles.css and main.js live in
# the repo root and are edited there directly. A photo only appears once its file exists, so run this
# again after adding photos (tools/prepare_photos.py does that for you).
import html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content import (PHOTOS, PORTFOLIO_WEDDINGS, EXTRA_GALLERIES, SESSIONS, STRIP, STEPS, WEAR, FAQ,  # noqa: E402
                     INSTAGRAM, ENDPOINT, FOCUS)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))  # the photos are looked up here

try:
    from PIL import Image
except ImportError:  # photo sizes then come from content.py
    Image = None


def e(s):
    return html.escape(s, quote=True)


# ------------------------------------------------------------------ photos
# Each photo is a JPEG plus WebP copies at these widths and at full size (made by tools/prepare_photos.py).
WIDTHS = (480, 800, 1200)

# How wide each kind of photo shows, so phones load a small copy and large screens a big one.
SIZES = {
    'hero': '(max-width: 460px) calc(100vw - 68px), (max-width: 900px) 388px, (max-width: 1220px) 38vw, 468px',
    'arch': '(max-width: 380px) calc(100vw - 36px), (max-width: 860px) 340px, 440px',
    'strip': '(max-width: 700px) 47vw, (max-width: 1220px) 23vw, 280px',
    'strip-wide': '(max-width: 700px) 94vw, (max-width: 1220px) 46vw, 560px',
    'grid': '(max-width: 600px) 48vw, (max-width: 1000px) 46vw, 370px',
    'band': '(max-width: 700px) 120vw, 100vw',
}


def exists(path):
    return os.path.isfile(os.path.join(ROOT, path))


def size_of(path, fallback):
    if Image:
        try:
            with Image.open(os.path.join(ROOT, path)) as im:
                return im.size
        except OSError:
            pass
    return fallback


def picture(path, w, h, alt, sizes, priority=False, eager=False, focus=None):
    """A photo: the WebP copies for browsers that take them, the JPEG for the rest."""
    stem = path.rsplit('.', 1)[0]
    candidates = [f'{stem}-{v}.webp {v}w' for v in WIDTHS if v < w and exists(f'{stem}-{v}.webp')]
    if exists(f'{stem}.webp'):
        candidates.append(f'{stem}.webp {w}w')
    source = f'<source type="image/webp" srcset="{", ".join(candidates)}" sizes="{sizes}">' if candidates else ''
    if priority:
        load = ' fetchpriority="high"'
    elif eager:
        load = ' decoding="async"'
    else:
        load = ' loading="lazy" decoding="async"'
    style = f' style="object-position: {focus}"' if focus else ''
    return f'<picture>{source}<img src="{path}" width="{w}" height="{h}" alt="{e(alt)}"{load}{style}></picture>'


def fig(key, sizes, cls='', priority=False, focus=None, attrs=''):
    """A photo slot. Until its photo exists it shows the landscape art instead."""
    path, w, h, alt, _ = PHOTOS[key]
    classes = ' '.join(c for c in ('ph', cls) if c)
    if not exists(path):
        return f'<figure class="{classes} ph--empty"{attrs}></figure>'
    w, h = size_of(path, (w, h))
    return f'<figure class="{classes}"{attrs}>{picture(path, w, h, alt, sizes, priority, focus=focus)}</figure>'


# ------------------------------------------------------------------ the arch mark and icons
ARCH = 'M44,206 V100 A56,56 0 0 1 156,100 V206 Z'


def arch_svg(uid, cls='brand-mark', stroke=6, outline='#5C4D3F', inside='#ECE6DB', wave=True,
             vb='38 38 124 174', label=None):
    aria = f'role="img" aria-label="{e(label)}"' if label else 'aria-hidden="true" focusable="false"'
    wave_svg = (f'<path d="M58,196 q9,-5 18,0 t18,0 t18,0 t18,0 t18,0" fill="none" stroke="#A7BBC3" '
                f'stroke-width="{max(2.4, stroke * .6):.1f}" stroke-linecap="round"/>') if wave else ''
    return (f'<svg class="{cls}" viewBox="{vb}" {aria} xmlns="http://www.w3.org/2000/svg">'
            f'<defs><clipPath id="arch-{uid}"><path d="{ARCH}"/></clipPath></defs>'
            f'<g clip-path="url(#arch-{uid})"><rect x="40" y="40" width="120" height="170" fill="{inside}"/>'
            f'<circle cx="100" cy="150" r="30" fill="#C3964F"/>'
            f'<path d="M40,168 C70,146 104,150 160,134 V210 H40 Z" fill="#C1C3B2"/>'
            f'<path d="M40,184 C78,168 116,182 160,166 V210 H40 Z" fill="#8B937A"/>{wave_svg}</g>'
            f'<path d="{ARCH}" fill="none" stroke="{outline}" stroke-width="{stroke}" stroke-linejoin="round"/></svg>')


FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="14 39 172 172">'
           f'<defs><clipPath id="a"><path d="{ARCH}"/></clipPath></defs>'
           '<g clip-path="url(#a)"><rect x="40" y="40" width="120" height="170" fill="#F6F2EA"/>'
           '<circle cx="100" cy="148" r="32" fill="#C3964F"/>'
           '<path d="M40,166 C70,144 104,148 160,132 V210 H40 Z" fill="#C1C3B2"/>'
           '<path d="M40,182 C78,166 116,180 160,164 V210 H40 Z" fill="#8B937A"/></g>'
           f'<path d="{ARCH}" fill="none" stroke="#5C4D3F" stroke-width="10" stroke-linejoin="round"/></svg>\n')

# Shown in photo slots until their photo arrives: a soft sun going down behind the hills.
PLACEHOLDER = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" preserveAspectRatio="xMidYMax slice">'
               '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
               '<stop offset="0" stop-color="#F4EEE4"/><stop offset=".5" stop-color="#F2E7D8"/>'
               '<stop offset=".72" stop-color="#EDD8C0"/></linearGradient></defs>'
               '<rect width="400" height="600" fill="url(#sky)"/>'
               '<circle cx="258" cy="402" r="56" fill="#E4C08A" fill-opacity=".8"/>'
               '<path d="M0,420 C64,398 126,400 192,412 C262,425 326,406 400,396 V600 H0 Z" fill="#DCD4C0"/>'
               '<path d="M0,468 C84,442 164,452 244,468 C312,481 356,474 400,464 V600 H0 Z" fill="#CACBB5"/>'
               '<path d="M0,524 C78,504 156,510 236,528 C298,542 350,539 400,528 V600 H0 Z" fill="#B8BEA4"/>'
               '</svg>\n')

ICON = {name: (f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{d}" fill="none" '
               'stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
        for name, d in [('prev', 'M15 5l-7 7 7 7'), ('next', 'M9 5l7 7-7 7'),
                        ('close', 'M6 6l12 12M18 6L6 18'), ('arrow', 'M4 12h15M13 6l6 6-6 6')]}


# ------------------------------------------------------------------ shared chrome
NAV = [('portfolio.html', 'Portfolio'), ('sessions.html', 'Sessions'), ('about.html', 'About')]


def header(active):
    links = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a>' for h, t in NAV)
    cur = ' aria-current="page"' if active == 'enquire.html' else ''
    return (f'<a class="skip" href="#main">Skip to content</a>\n<header class="site-header"><div class="wrap header-inner">'
            f'<a class="brand" href="index.html" aria-label="Sunday Light, home">{arch_svg("h")}'
            f'<span class="brand-name">Sunday Light</span></a>'
            f'<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">'
            f'<span class="sr-only">Menu</span><span class="bars" aria-hidden="true"></span></button>'
            f'<nav id="site-nav" class="site-nav" aria-label="Main">{links}'
            f'<a class="btn btn--small" href="enquire.html"{cur}>Enquire</a></nav></div></header>\n')


def footer():
    ig_name, ig_url = INSTAGRAM
    return (f'<footer class="site-footer"><div class="wrap"><div class="footer-grid">'
            f'<div class="footer-brand"><a class="brand" href="index.html" aria-label="Sunday Light, home">'
            f'{arch_svg("f", outline="#F6F2EA")}<span class="brand-name">Sunday Light</span></a>'
            f'<p>Natural, light-filled photography for weddings, couples and families across Adelaide.</p></div>'
            f'<div class="footer-col"><h2>Explore</h2><ul><li><a href="portfolio.html">Portfolio</a></li>'
            f'<li><a href="sessions.html">Sessions</a></li><li><a href="about.html">About</a></li>'
            f'<li><a href="enquire.html">Enquire</a></li></ul></div>'
            f'<div class="footer-col"><h2>Say hello</h2><ul><li><a href="{ig_url}" rel="me">Instagram {e(ig_name)}</a></li>'
            f'<li>Adelaide, South Australia</li></ul></div></div>'
            f'<div class="footer-base"><span>&copy; <span data-year>2026</span> Sunday Light</span>'
            f'<span><a href="privacy.html">Privacy</a> · Website by <a href="https://www.lumenadl.com/">Lumen</a></span></div>'
            f'</div></footer>\n')


JSONLD = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "Sunday Light",
    "description": "Natural, light-filled wedding, couples and family photography in Adelaide, South Australia.",
    "areaServed": {"@type": "City", "name": "Adelaide"},
    "address": {"@type": "PostalAddress", "addressLocality": "Adelaide", "addressRegion": "SA", "addressCountry": "AU"},
    "knowsAbout": ["Wedding photography", "Couples photography", "Maternity photography",
                   "Newborn photography", "Family photography"],
    "sameAs": [INSTAGRAM[1]],
}

# Fonts used near the top of every page are fetched straight away, so the headings don't jump when they swap in.
FONTS = {'serif': 'cormorant-garamond-500', 'italic': 'cormorant-garamond-500-italic',
         'sans': 'jost-300-600', 'caps': 'marcellus-400'}


def head(title, desc, jsonld=False, italic=False):
    fonts = ['serif'] + (['italic'] if italic else []) + ['sans', 'caps']
    preload = ''.join(f'<link rel="preload" href="fonts/{FONTS[f]}.woff2" as="font" type="font/woff2" crossorigin>\n'
                      for f in fonts)
    ld = (f'<script type="application/ld+json">{json.dumps(JSONLD, ensure_ascii=False)}</script>\n' if jsonld else '')
    return (f'<title>{e(title)}</title>\n<meta name="description" content="{e(desc)}">\n'
            f'<meta property="og:title" content="{e(title)}">\n<meta property="og:description" content="{e(desc)}">\n'
            f'<meta property="og:type" content="website">\n<meta property="og:image" content="images/og-card.jpg">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n<meta name="theme-color" content="#F6F2EA">\n'
            f'<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
            f'<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">\n'
            f'<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
            f'{preload}<link rel="stylesheet" href="styles.css">\n'
            f'<script>document.documentElement.classList.add("js")</script>\n'
            f'<script src="main.js" defer></script>\n{ld}')


def page(active, title, desc, main, jsonld=False, body_extra=''):
    italic = '<em>' in main.split('</h1>', 1)[0]
    return ('<!doctype html>\n<html lang="en-AU">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head(title, desc, jsonld, italic) + '</head>\n<body>\n' + header(active)
            + f'<main id="main">\n{main}\n</main>\n' + footer() + body_extra + '</body>\n</html>\n')


def cta(photo='winery-champagne', title='Tell me what you’re planning.', text='Weddings, couples and families across Adelaide, from the coast to the hills.'):
    return (f'<section class="cta" aria-labelledby="cta-title">{fig(photo, SIZES["band"], focus=FOCUS.get(photo))}'
            f'<div class="cta-card"><p class="eyebrow">Enquiries</p><h2 id="cta-title">{e(title)}</h2>'
            f'<p>{e(text)}</p><a class="btn" href="enquire.html">Check my dates</a></div></section>')


def link_arrow(href, text):
    return f'<a class="link-arrow" href="{href}">{e(text)} <span aria-hidden="true">→</span></a>'


# ------------------------------------------------------------------ pages
def index():
    with_photos = [s for s in SESSIONS if exists(PHOTOS[s['photo']][0])]
    media = ''.join(fig(s['photo'], SIZES['arch'], 'arch is-active' if i == 0 else 'arch', attrs=f' data-for="{s["id"]}"')
                    for i, s in enumerate(with_photos))
    rows = ''.join(
        f'<li><a href="sessions.html#{s["id"]}" data-for="{s["id"]}"><span class="services-name">{e(s["name"])}</span>'
        f'<span class="services-text">{e(s["card"])}</span><span class="services-arrow" aria-hidden="true">{ICON["arrow"]}</span></a></li>'
        for s in SESSIONS)
    strip = ''.join(fig(k, SIZES['strip-wide' if o == 'l' else 'strip'], o) for k, o in STRIP)
    steps = ''.join(f'<li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in STEPS)
    main = f'''<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy"><p class="eyebrow">Adelaide wedding &amp; family photographer</p>
<h1>Photographs that feel like a <em>Sunday afternoon.</em></h1>
<p class="lead">Natural, light-filled photos of the people you love, taken slowly and in the best light of the day. Weddings, couples and families across Adelaide, from the coast to the hills.</p>
<div class="actions"><a class="btn" href="enquire.html">Check my dates</a>{link_arrow("portfolio.html", "See the work")}</div></div>
<div class="hero-media"><span class="sun" aria-hidden="true"></span>{fig("vineyard-sunset", SIZES["hero"], "arch", priority=True)}</div>
</div></section>

<section class="section section--lime" aria-labelledby="why-title"><div class="wrap intro-grid">
{fig("arch-mirror", SIZES["arch"], "arch")}
<div><p class="eyebrow">Why Sunday Light</p><h2 id="why-title">The best light of the week.</h2>
<div class="prose"><p>Sunday light is low, warm and in no hurry. It’s the light I chase, and it’s how I want your session to feel: no stiff poses and no rushing, just time together while I look for the moments in between.</p>
<p>I’ll guide you the whole way, from what to wear to where to stand when the sun drops. You bring your people. I’ll look after the light.</p></div>
{link_arrow("about.html", "More about me")}</div>
</div></section>

<section class="section services" aria-labelledby="sessions-title"><div class="wrap services-grid">
<div class="section-head"><p class="eyebrow">What I photograph</p><h2 id="sessions-title">From the proposal to the <em>yearly family photo.</em></h2></div>
{f'<div class="services-media" aria-hidden="true">{media}</div>' if media else ''}
<ul class="services-list">{rows}</ul>
</div></section>

<section class="section section--lime" aria-labelledby="weddings-title"><div class="wrap">
<div class="section-head"><p class="eyebrow">Recent weddings</p><h2 id="weddings-title">Vineyards, castles and a <em>white Jaguar.</em></h2></div>
<div class="strip">{strip}</div>
<div class="strip-foot"><p>Real weddings from across Adelaide and the vineyards around it.</p>{link_arrow("portfolio.html", "See the wedding gallery")}</div>
</div></section>

<section class="section" aria-labelledby="how-title"><div class="wrap">
<div class="section-head"><p class="eyebrow">How it works</p><h2 id="how-title">Easy from the first message.</h2></div>
<ol class="steps">{steps}</ol></div></section>

{cta()}'''
    return page('index.html', 'Sunday Light | Adelaide wedding & family photographer',
                'Natural, light-filled photography for weddings, couples and families across Adelaide. Relaxed sessions on the coast, in the hills and at home.',
                main, jsonld=True)


def gallery_item(path, alt, i, first_gallery):
    w, h = size_of(path, (1333, 2000))
    # The first photo is the one people see first, so it loads straight away; the rest load as they come into view.
    pic = picture(path, w, h, alt, SIZES['grid'], priority=first_gallery and i == 0)
    return f'<figure class="ph"><a href="{path}" data-lightbox>{pic}</a></figure>'


def portfolio():
    galleries = []
    weddings = [(PHOTOS[k][0], PHOTOS[k][3]) for k in PORTFOLIO_WEDDINGS if exists(PHOTOS[k][0])]
    if weddings:
        galleries.append(('weddings', 'Weddings', weddings))
    for gid, name, pattern, n, alt in EXTRA_GALLERIES:
        photos = [(pattern.format(i), alt) for i in range(1, n + 1) if exists(pattern.format(i))]
        if photos:
            galleries.append((gid, name, photos))
    sections = ''
    for g, (gid, name, photos) in enumerate(galleries):
        figs = ''.join(gallery_item(p, a, i, g == 0) for i, (p, a) in enumerate(photos))
        sections += (f'<section class="gallery wrap" id="{gid}" aria-labelledby="{gid}-title"><div class="gallery-head">'
                     f'<h2 id="{gid}-title">{e(name)}</h2></div><div class="masonry">{figs}</div></section>\n')
    if not galleries:
        sections = (f'<section class="gallery wrap"><p class="gallery-empty">Galleries are on their way. The latest sessions '
                    f'are always on <a href="{INSTAGRAM[1]}">Instagram</a>.</p></section>\n')
    chips = ''
    if len(galleries) > 1:
        chips = ('<nav class="chips" aria-label="Galleries">'
                 + ''.join(f'<a href="#{gid}">{e(name)}</a>' for gid, name, _ in galleries) + '</nav>')
    main = f'''<section class="page-head"><div class="wrap"><p class="eyebrow">Portfolio</p>
<h1>A few <em>favourite days.</em></h1>
<p class="lead">Weddings, couples and families from around Adelaide. The newest sessions go up on <a href="{INSTAGRAM[1]}">Instagram</a> first.</p>
{chips}</div></section>
{sections}<div class="section"></div>
{cta("olive-grove-confetti", "Like what you see?", "Tell me about your day and I’ll come back with dates and details.")}'''
    lightbox = ('<dialog class="lightbox" aria-label="Photo viewer"><div class="lightbox-inner">'
                f'<button class="lb-btn lb-prev" type="button" aria-label="Previous photo">{ICON["prev"]}</button>'
                '<figure class="lb-figure"></figure>'
                f'<button class="lb-btn lb-next" type="button" aria-label="Next photo">{ICON["next"]}</button>'
                f'<button class="lb-btn lb-close" type="button" aria-label="Close">{ICON["close"]}</button>'
                '<p class="lb-count" aria-hidden="true"></p><p class="sr-only lb-live" aria-live="polite"></p>'
                '</div></dialog>\n')
    return page('portfolio.html', 'Portfolio | Sunday Light',
                'Wedding, couples and family photography from around Adelaide by Sunday Light.', main,
                body_extra=lightbox)


def sessions():
    blocks = ''
    for i, s in enumerate(SESSIONS):
        body = ''.join(f'<p>{e(p)}</p>' for p in s['body'])
        blocks += (f'<section class="session" id="{s["id"]}" aria-labelledby="{s["id"]}-title">'
                   f'{fig(s["photo"], SIZES["arch"], "arch", priority=i == 0)}'
                   f'<div><p class="eyebrow">{i + 1:02d}</p><h2 id="{s["id"]}-title">{e(s["name"])}</h2><div class="prose">{body}</div>'
                   f'<p class="price">Pricing on enquiry</p><div class="actions"><a class="btn" href="enquire.html">Enquire about {e(s["name"].lower())}</a></div></div></section>')
    wear = ''.join(f'<li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in WEAR)
    swatches = ''.join(f'<span style="background:{c}" title="{n}"></span>' for n, c in
                       [('Cream', '#F3EDE2'), ('Linen', '#E3D6C1'), ('Sage', '#A9B39A'), ('Rust', '#B26F4C'),
                        ('Denim', '#6E87A1'), ('Bark', '#5C4D3F')])
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in FAQ)
    main = f'''<section class="page-head"><div class="wrap"><p class="eyebrow">Sessions</p>
<h1>Slow, sunny sessions <em>for every chapter.</em></h1>
<p class="lead">Every session is relaxed, guided and planned around the light. Here’s what each one looks like.</p></div></section>
<div class="wrap">{blocks}</div>
<section class="section section--lime" aria-labelledby="wear-title"><div class="wrap">
<div class="section-head"><p class="eyebrow">What to wear</p><h2 id="wear-title">Dress for the light.</h2>
<p>Soft colours glow in golden light. Here’s what works best on camera.</p></div>
<div class="swatches" aria-hidden="true">{swatches}</div><ul class="wear">{wear}</ul></div></section>
<section class="section" aria-labelledby="faq-title"><div class="wrap">
<div class="section-head"><p class="eyebrow">Good to know</p><h2 id="faq-title">Questions, answered.</h2></div>
<div class="faq">{faq}</div></div></section>
{cta("jaguar-flare")}'''
    return page('sessions.html', 'Sessions | Sunday Light',
                'Wedding, couples, maternity, newborn, family and milestone photography sessions in Adelaide.', main)


def about():
    values = ''.join(f'<li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in [
        ('Light first', 'I plan every outdoor session around the last hour of sun.'),
        ('Prompts, not poses', 'Easy direction that keeps you moving, so you look like yourselves.'),
        ('Here for the long run', 'From your wedding to your family photos years later.')])
    main = f'''<section class="page-head"><div class="wrap about-grid">
<div><p class="eyebrow">About</p><h1>Hi, I’m <em>Charne.</em></h1>
<div class="prose"><p class="lead">I’m the photographer behind Sunday Light, based in Adelaide.</p>
<p>I photograph people the way they are on a good day: close, laughing and lit by a low sun. Weddings, couples, bumps, newborns and families, on the beach, in the hills or at home.</p>
<p>I keep sessions relaxed. I’ll give you easy prompts, tell you where to stand when the light is right and let the rest happen. My favourite sessions are the ones where people forget I’m there.</p>
<p>I love it when a family comes back as their story grows: the proposal, then the bump, then the first family photo on the beach.</p></div>
<div class="actions"><a class="btn" href="enquire.html">Say hello</a>{link_arrow("portfolio.html", "See the work")}</div></div>
{fig("about-portrait", SIZES["arch"], "arch", priority=True)}
</div></section>
<section class="section section--lime" aria-labelledby="values-title"><div class="wrap">
<div class="section-head"><p class="eyebrow">How I work</p><h2 id="values-title">What you can count on.</h2></div>
<ul class="values">{values}</ul></div></section>
{cta("castle-window")}'''
    return page('about.html', 'About | Sunday Light',
                'Sunday Light is a relaxed, natural-light photographer based in Adelaide, South Australia.', main)


def enquire():
    ig_name, ig_url = INSTAGRAM
    opts = ''.join(f'<option>{o}</option>' for o in ['Wedding', 'Couples or engagement', 'Proposal', 'Bump',
                                                       'Newborn', 'Family', 'Milestone', 'Something else'])
    heard = ''.join(f'<option>{o}</option>' for o in ['Instagram', 'A friend', 'Google', 'A wedding vendor', 'Somewhere else'])
    main = f'''<section class="page-head"><div class="wrap"><p class="eyebrow">Enquire</p>
<h1>Let’s plan <em>something lovely.</em></h1>
<p class="lead">Tell me a little about what you’re planning. I’ll get back to you with availability and pricing.</p></div></section>
<section class="section" style="padding-top:0"><div class="wrap enquire-grid">
<div>
<form id="enquiry-form" class="form" data-endpoint="{ENDPOINT}" novalidate>
<div class="field"><label for="name">Your name</label><input id="name" name="name" autocomplete="name" autocapitalize="words" required maxlength="200"></div>
<div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required maxlength="254"></div>
<div class="field"><label for="phone">Phone <span>(optional)</span></label><input id="phone" name="phone" type="tel" autocomplete="tel" maxlength="40"></div>
<div class="field"><label for="session">Type of session</label><select id="session" name="session">{opts}</select></div>
<div class="field"><label for="date">Date or season <span>(rough is fine)</span></label><input id="date" name="date" placeholder="e.g. March 2027" maxlength="120"></div>
<div class="field"><label for="location">Where <span>(optional)</span></label><input id="location" name="location" autocapitalize="words" placeholder="Beach, hills, home or venue" maxlength="200"></div>
<div class="field full"><label for="message">Tell me about it</label><textarea id="message" name="message" required maxlength="4000" placeholder="Who’s involved, what you’re picturing, anything I should know"></textarea></div>
<div class="field"><label for="heard">How did you find me? <span>(optional)</span></label><select id="heard" name="heard"><option value="">Choose one</option>{heard}</select></div>
<div class="hp" aria-hidden="true"><label for="company">Leave this empty</label><input id="company" name="company" tabindex="-1" autocomplete="off"></div>
<div id="form-error" class="form-error" tabindex="-1" hidden>Your enquiry didn’t send. Your details are still here, so please try again, or message me on Instagram at <a href="{ig_url}">{e(ig_name)}</a>.</div>
<div class="form-foot"><button class="btn" type="submit">Send enquiry</button><p id="form-status" class="form-status" role="status" aria-live="polite"></p></div>
</form>
<div id="form-success" class="form-success" hidden><p class="eyebrow">Sent</p><h2 tabindex="-1">Thank you.</h2><p>Your enquiry is on its way. I’ll be in touch soon with dates and details.</p>{link_arrow("portfolio.html", "Browse the portfolio")}</div>
</div>
<aside class="aside" aria-label="What happens next">
<div><h2>What happens next</h2><p>I’ll reply with available dates, pricing and a few ideas for your session.</p></div>
<div><h2>Prefer Instagram?</h2><p>Send a message to <a href="{ig_url}">{e(ig_name)}</a>.</p></div>
<div><h2>Based in Adelaide</h2><p>Sessions on the coast, in the hills and at home.</p></div>
</aside>
</div></section>'''
    return page('enquire.html', 'Enquire | Sunday Light',
                'Check dates and pricing for wedding, couples and family photography in Adelaide.', main)


def privacy():
    main = f'''<section class="page-head"><div class="wrap"><p class="eyebrow">Privacy</p><h1>Privacy</h1></div></section>
<section class="section" style="padding-top:0"><div class="wrap text">
<p>This page explains what happens to the details you share through this website.</p>
<h2>What I collect</h2><p>When you send an enquiry, I receive the details you type into the form: your name, email, and anything else you choose to include, such as a phone number, date or message.</p>
<h2>How I use it</h2><p>Only to reply to your enquiry and, if you book, to plan your session. I don’t sell or share your details for marketing.</p>
<h2>Photos</h2><p>Some session photos appear on this website and on Instagram. If you’d like a photo of you removed, just ask and I’ll take it down.</p>
<h2>Questions or changes</h2><p>To see, correct or delete the details you’ve sent, message me on Instagram at <a href="{INSTAGRAM[1]}">{e(INSTAGRAM[0])}</a>.</p>
</div></section>'''
    return page('privacy.html', 'Privacy | Sunday Light', 'How Sunday Light handles the details you share.', main)


def not_found():
    main = f'''<section class="page-head" style="padding-bottom:clamp(72px,10vw,140px)"><div class="wrap" style="display:grid;justify-items:start;gap:22px">
{arch_svg("nf", cls="nf-mark", stroke=3)}
<p class="eyebrow">Page not found</p><h1>This page has <em>wandered off.</em></h1>
<p class="lead">It may have moved, or the link may be old.</p>
<div class="actions"><a class="btn" href="index.html">Back home</a>{link_arrow("portfolio.html", "See the portfolio")}</div></div></section>'''
    out = page('', 'Page not found | Sunday Light', 'This page could not be found.', main)
    # served for missing paths at any depth, so resolve every link from the site root
    return out.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="/">', 1)


PAGES = {'index.html': index, 'portfolio.html': portfolio, 'sessions.html': sessions, 'about.html': about,
         'enquire.html': enquire, 'privacy.html': privacy, '404.html': not_found}


def main(out=ROOT):
    os.makedirs(os.path.join(out, 'images'), exist_ok=True)
    for name, fn in PAGES.items():
        with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
            f.write(fn())
    with open(os.path.join(out, 'favicon.svg'), 'w', encoding='utf-8') as f:
        f.write(FAVICON)
    with open(os.path.join(out, 'images', 'placeholder.svg'), 'w', encoding='utf-8') as f:
        f.write(PLACEHOLDER)
    print('built', ', '.join(PAGES), '->', out)


if __name__ == '__main__':
    main(os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
