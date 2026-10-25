# Builds the Sunday Light pages.
#
#   python3 tools/site/build.py           # writes into the repo root
#   python3 tools/site/build.py out_dir   # or somewhere else, for a look before replacing the real pages
#
# Writes the HTML pages, styles.css, main.js, favicon.svg and images/placeholder.svg. styles.css and main.js are
# joined from the numbered parts in tools/site/css/ and tools/site/js/ (in file-name order), so edit the parts, not
# the joined files. A photo only appears once its file exists, so run this again after adding photos
# (tools/prepare_photos.py does that for you).
import glob, html, json, os, sys
from urllib.parse import quote_plus

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content import (PHOTOS, PORTFOLIO_WEDDINGS, EXTRA_GALLERIES, SESSIONS, STEPS, FAQ, INSTAGRAM, ENDPOINT,  # noqa: E402
                     FOCUS, FORM_SESSION, FORM_OPTIONS, HERO, HERO_CAPTION, HOME_WINDOWS, INTRO, TILES, INSTAGRAM_STRIP,
                     KIND_WORDS, KIND_WORDS_ARE_PLACEHOLDERS, KIND_WORDS_HOLDING_PHOTO, INVESTMENT_HERO, INVESTMENT_INTRO,
                     WEDDING_PACKAGES, WEDDING_INCLUDES, WEDDING_TERMS)

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
# Photos in the hero and the photo windows fill the screen's height, so on phones they show wider than the screen.
SIZES = {
    'window2': '(max-width: 700px) 150vw, 50vw',
    'window3': '(max-width: 700px) 150vw, 45vw',
    'arch': '(max-width: 380px) calc(100vw - 36px), (max-width: 860px) 340px, 440px',
    'tile': '(max-width: 700px) calc(100vw - 36px), 380px',
    'card': '(max-width: 760px) calc(100vw - 36px), 560px',
    'grid': '(max-width: 600px) 48vw, (max-width: 1000px) 46vw, 370px',
    'square': '(max-width: 700px) 34vw, 17vw',
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


def fig(key, sizes, cls='', priority=False, focus=None, attrs='', alt=None):
    """A photo slot. Until its photo exists it shows the landscape art instead."""
    path, w, h, text, _ = PHOTOS[key]
    classes = ' '.join(c for c in ('ph', cls) if c)
    if not exists(path):
        return f'<figure class="{classes} ph--empty"{attrs}></figure>'
    w, h = size_of(path, (w, h))
    pic = picture(path, w, h, text if alt is None else alt, sizes, priority, focus=focus or FOCUS.get(key))
    return f'<figure class="{classes}"{attrs}>{pic}</figure>'


# ------------------------------------------------------------------ the arch mark and icons
ARCH = 'M44,206 V100 A56,56 0 0 1 156,100 V206 Z'


def arch_svg(uid, cls='brand-mark', stroke=6, outline='#5C4D3F', inside='#ECE6DB', wave=True,
             vb='38 38 124 174', label=None):
    aria = f'role="img" aria-label="{e(label)}"' if label else 'aria-hidden="true" focusable="false"'
    wave_svg = (f'<path class="mk-wave" pathLength="1" d="M58,196 q9,-5 18,0 t18,0 t18,0 t18,0 t18,0" fill="none" '
                f'stroke="#A7BBC3" stroke-width="{max(2.4, stroke * .6):.1f}" stroke-linecap="round"/>') if wave else ''
    return (f'<svg class="{cls}" viewBox="{vb}" {aria} xmlns="http://www.w3.org/2000/svg">'
            f'<defs><clipPath id="arch-{uid}"><path d="{ARCH}"/></clipPath></defs>'
            f'<g clip-path="url(#arch-{uid})"><rect x="40" y="40" width="120" height="170" fill="{inside}"/>'
            f'<circle class="mk-sun" cx="100" cy="150" r="30" fill="#C3964F"/>'
            f'<path d="M40,168 C70,146 104,150 160,134 V210 H40 Z" fill="#C1C3B2"/>'
            f'<path d="M40,184 C78,168 116,182 160,166 V210 H40 Z" fill="#8B937A"/>{wave_svg}</g>'
            f'<path class="mk-line" pathLength="1" d="{ARCH}" fill="none" stroke="{outline}" stroke-width="{stroke}" '
            f'stroke-linejoin="round"/></svg>')


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
                        ('close', 'M6 6l12 12M18 6L6 18'),
                        ('instagram', 'M7.5 3h9A4.5 4.5 0 0 1 21 7.5v9a4.5 4.5 0 0 1-4.5 4.5h-9A4.5 4.5 0 0 1 3 16.5v-9A4.5 4.5 0 0 1 7.5 3z'
                                      'M12 8.2a3.8 3.8 0 1 0 0 7.6 3.8 3.8 0 0 0 0-7.6zM17.3 6.7h.01')]}


# The long editorial arrow: a thin shaft that reaches forward on hover, and a small open head (spec B1, B2).
ICON['arrow'] = ('<svg class="arw" viewBox="0 0 32 12" width="28" height="10.5" overflow="visible" aria-hidden="true" focusable="false">'
                 '<path class="arw-shaft" d="M1 6H30" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" vector-effect="non-scaling-stroke"/>'
                 '<path class="arw-head" d="M25.5 1.5 30 6l-4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" '
                 'stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>')
ICON['arrow-ne'] = ('<svg class="arw arw--ne" viewBox="0 0 14 14" width="12" height="12" aria-hidden="true" focusable="false">'
                    '<path class="arw-shaft" d="M2.5 11.5 11.5 2.5" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" vector-effect="non-scaling-stroke"/>'
                    '<path class="arw-head" d="M4.5 2.5h7v7" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" '
                    'stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>')


# ------------------------------------------------------------------ shared chrome
NAV = [('gallery.html', 'Gallery'), ('investment.html', 'Investment'), ('kind-words.html', 'Kind words'),
       ('contact.html', 'Contact')]


def nav_links(active, menu=False):
    if not menu:
        return ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a>' for h, t in NAV)
    # In the menu each link rises out of its own line box; the current page carries a small gold sun.
    sun = '<span class="nav-sun" aria-hidden="true"></span>'
    return ''.join(f'<a href="{h}" style="--i:{i}"{" class=\"nav-contact\"" if h == "contact.html" else ""}'
                   f'{" aria-current=\"page\"" if h == active else ""}>'
                   f'<span class="nl"><span>{t}</span></span>{sun if h == active else ""}</a>' for i, (h, t) in enumerate(NAV))


def header(active):
    ig_name, ig_url = INSTAGRAM
    here = ' aria-current="page"' if active == 'contact.html' else ''
    return (f'<a class="skip" href="#main">Skip to content</a>\n<header class="site-header" id="top"><div class="wrap header-inner">'
            f'<nav id="site-nav" class="site-nav xfade" aria-label="Main"><span class="nav-sheet" aria-hidden="true"></span>'
            f'{nav_links(active, menu=True)}'
            f'<div class="menu-foot"><a class="nav-instagram" href="{ig_url}" rel="me">{ICON["instagram"]}<span>{e(ig_name)}</span></a>'
            f'<span class="menu-place">Adelaide, South Australia</span></div></nav>'
            f'<a class="brand" href="index.html" aria-label="Sunday Light, home">{arch_svg("h")}'
            f'<span class="brand-name">Sunday Light</span></a>'
            f'<a class="btn btn--sm header-cta" href="contact.html"{here}>Enquire</a>'
            f'<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">'
            f'<span class="nav-toggle-label">Menu</span><span class="bars" aria-hidden="true"></span></button>'
            f'</div></header>\n')


# The footer scene (M03 Sundown): one gold line draws the gulf horizon, a large arch window and the hills. Inside the
# window is the logo's own scene, scaled, where the sun sets as the footer scrolls in. Two drawings: phone and wide.
SCENES = {
    # key: (viewBox w, h, scale of the logo inside, logo-to-scene offset x, y, gold line, front hill, gulf waves)
    'm': (390, 230, 1.25, 70, -39.5,
          'M0,218 H125 V85.5 A70,70 0 0 1 265,85.5 V218 C280,211 298,197 321,195 S361,204 390,200',
          'M291,230 C305,222 324,215 343,217 S373,226 390,223',
          ['M14,226 q7,-4 14,0 t14,0 t14,0 t14,0']),
    'w': (1440, 300, 1.45, 575.2, -8.7,
          'M0,290 H639 V136.3 A81.2,81.2 0 0 1 801.4,136.3 V290 C846,277 902,241 982,236 S1102,262 1176,259 S1322,234 1440,244',
          'M934,300 C998,285 1058,268 1128,271 S1268,292 1338,287 S1412,277 1440,279',
          ['M118,296 q10,-5 20,0 t20,0 t20,0 t20,0 t20,0', 'M352,293 q10,-5 20,0 t20,0 t20,0']),
}


def footer_scene(kind):
    w, h, s, tx, ty, line, front, waves = SCENES[kind]
    uid = f'dusk-{kind}'
    gulf = ''.join(f'<path class="dusk-wave" pathLength="1" d="{d}"/>' for d in waves)
    return (f'<svg class="dusk dusk--{kind}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" preserveAspectRatio="xMidYMax meet" '
            f'aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><clipPath id="{uid}-a"><path d="{ARCH}"/></clipPath>'
            f'<linearGradient id="{uid}-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EDD8C0"/>'
            f'<stop offset="1" stop-color="#E4C08A"/></linearGradient></defs>'
            f'<g transform="translate({tx} {ty}) scale({s})"><g clip-path="url(#{uid}-a)">'
            f'<rect x="40" y="40" width="120" height="170" fill="#F6F2EA"/>'
            f'<rect class="sky-gold" x="40" y="40" width="120" height="170" fill="url(#{uid}-g)"/>'
            f'<circle class="dusk-sun" cx="100" cy="150" r="30" fill="#C3964F"/>'
            f'<path d="M40,168 C70,146 104,150 160,134 V210 H40 Z" fill="#C1C3B2"/>'
            f'<path d="M40,184 C78,168 116,182 160,166 V210 H40 Z" fill="#8B937A"/>'
            f'<path d="M58,196 q9,-5 18,0 t18,0 t18,0 t18,0 t18,0" fill="none" stroke="#A7BBC3" stroke-width="2.4" stroke-linecap="round"/>'
            f'<path class="glint" pathLength="1" d="M58,196 q9,-5 18,0 t18,0 t18,0 t18,0 t18,0" fill="none" stroke="#FBF8F2" '
            f'stroke-width="2.4" stroke-linecap="round"/></g></g>'
            f'<path class="dusk-line" pathLength="1" d="{line}"/><path class="dusk-line dusk-line--front" pathLength="1" d="{front}"/>'
            f'{gulf}</svg>')


def footer():
    ig_name, ig_url = INSTAGRAM
    dot = '<span class="dot"> · </span>'  # hidden on phones, where each part gets its own line
    return (f'<footer class="site-footer">'
            f'<a class="sundown" href="index.html" aria-label="Sunday Light, home">'
            f'<span class="sundown-scene">{footer_scene("m")}{footer_scene("w")}</span>'
            f'<span class="sundown-word" aria-hidden="true"><span>Sunday Light</span></span></a>'
            f'<div class="wrap footer-inner">'
            f'<nav class="footer-nav" aria-label="Footer">{nav_links("")}</nav>'
            f'<a class="footer-instagram" href="{ig_url}" rel="me">{ICON["instagram"]}<span>{e(ig_name)}</span></a>'
            f'<p class="golden-hour" data-golden>Golden hour: the last hour before sunset, and the best light of the day.</p>'
            f'<p class="footer-base"><span>&copy; <span data-year>2026</span> Sunday Light</span>{dot}'
            f'<span>Adelaide, South Australia</span>{dot}'
            f'<span><a href="privacy.html">Privacy</a> · Website by <a href="https://www.lumenadl.com/">Lumen</a></span>{dot}'
            f'<span><button class="still-toggle" type="button" aria-pressed="false">Hold still</button></span></p>'
            f'</div></footer>\n')


JSONLD = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "Sunday Light",
    "description": "Natural, light-filled wedding, couples, engagement, family, maternity and newborn photography in Adelaide, South Australia.",
    "areaServed": {"@type": "City", "name": "Adelaide"},
    "address": {"@type": "PostalAddress", "addressLocality": "Adelaide", "addressRegion": "SA", "addressCountry": "AU"},
    "knowsAbout": ["Wedding photography", "Engagement photography", "Couples photography",
                   "Family photography", "Maternity photography", "Newborn photography"],
    "sameAs": [INSTAGRAM[1]],
}

# Runs before first paint. Sets .js; .m when motion is welcome (no reduced motion, not "Hold still"); .first-light
# on the first page of a visit; and drives the page-change arch: it remembers where a link was tapped and skips the
# transition for back, forward, reload and restored pages.
HEAD_SCRIPT = (
    "(function(h){var c=h.classList,s,st=false,nav,k=['x','top','w','h'];c.add('js');"
    "try{st=localStorage.getItem('sl-still')==='1'}catch(e){}"
    "if(st)c.add('still');else if(!matchMedia('(prefers-reduced-motion:reduce)').matches)c.add('m');"
    "try{s=sessionStorage;nav=(performance.getEntriesByType('navigation')[0]||{}).type;"
    "if(c.contains('m')&&nav==='navigate'&&!s.getItem('sl-sun')&&!h.hasAttribute('data-nf'))c.add('first-light');"
    "s.setItem('sl-sun','1')}catch(e){}"
    "addEventListener('pageshow',function(e){if(e.persisted){h.dataset.restored='1';c.remove('vt-keep','vt-quiet')}});"
    "addEventListener('pagereveal',function(e){var vt=e.viewTransition,r={},a=window.navigation&&navigation.activation;"
    "if(!vt)return;try{r=JSON.parse(s.getItem('sl-vt')||'{}');s.removeItem('sl-vt')}catch(x){}"
    "if(!c.contains('m')||h.dataset.restored||/back|reload/.test(nav)||(a&&/traverse|reload/.test(a.navigationType))"
    "||!(Date.now()-r.at<4000)){vt.skipTransition();return}"
    "if(r.keep)c.add('vt-keep');if(r.quiet)c.add('vt-quiet');"
    "k.forEach(function(p){if(r[p])h.style.setProperty('--vt-'+p,r[p])});"
    "window.slSettled=vt.finished.finally(function(){c.remove('vt-keep','vt-quiet');"
    "k.forEach(function(p){h.style.removeProperty('--vt-'+p)})})})"
    "})(document.documentElement)"
)

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
            f'<script>{HEAD_SCRIPT}</script>\n'
            f'<script src="main.js" defer></script>\n{ld}')


def page(active, title, desc, main, jsonld=False, body_extra='', html_attrs=''):
    italic = '<em>' in main.split('</h1>', 1)[0]
    return (f'<!doctype html>\n<html lang="en-AU"{html_attrs}>\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head(title, desc, jsonld, italic) + '</head>\n<body>\n' + header(active)
            + f'<main id="main">\n{main}\n</main>\n' + footer() + body_extra + '</body>\n</html>\n')


def link_arrow(href, text, cls=''):
    return (f'<a class="link-arrow{(" " + cls) if cls else ""}" href="{href}"><span class="la-label">{e(text)}</span>'
            f'{ICON["arrow"]}</a>')


def button(href, text, cls='btn--secondary'):
    return f'<a class="btn {cls}" href="{href}"><span class="btn-label">{e(text)}</span>{ICON["arrow"]}</a>'


# ------------------------------------------------------------------ building blocks
def window(keys, cls='', caption='', priority=False):
    """A full-width photo window. The photos hold still while the page scrolls past, like looking through a window.
    Large screens show every photo side by side; phones show the first."""
    keys = [k for k in keys if exists(PHOTOS[k][0])]
    if not keys:
        return ''
    sizes = SIZES['window3' if len(keys) > 2 else 'window2']
    photos = ''.join(fig(k, sizes, priority=priority and i == 0) for i, k in enumerate(keys))
    cap = f'<p class="window-caption">{e(caption)}</p>' if caption else ''
    hidden = '' if caption else ' aria-hidden="true"'
    return (f'<div class="window{(" " + cls) if cls else ""}"{hidden}><div class="window-photos n{len(keys)}">{photos}</div>'
            f'{cap}</div>')


def duo(first=('contact.html', 'Contact', 'Check my dates'), second=('investment.html', 'Investment', 'Sessions & pricing')):
    links = ''.join(f'<a href="{h}"><span class="duo-title">{e(t)}</span><span class="duo-sub">{e(s)}</span></a>'
                    for h, t, s in (first, second))
    return f'<nav class="duo" aria-label="Next steps"><div class="wrap duo-grid">{links}</div></nav>'


def kind_words(uid='words'):
    """The Kind words slider: a photo beside the words, one review at a time. Nothing until real reviews exist."""
    if KIND_WORDS_ARE_PLACEHOLDERS or not KIND_WORDS:
        return ''
    n = len(KIND_WORDS)
    photos = ''.join(fig(k, SIZES['card'], 'words-photo' + (' is-current' if i == 0 else ''), alt='')
                     for i, (_, _, _, k) in enumerate(KIND_WORDS))
    items = ''.join(f'<figure class="words-item{" is-current" if i == 0 else ""}" role="group" aria-roledescription="slide" '
                    f'aria-label="{i + 1} of {n}"><blockquote><p>“{e(q)}”</p></blockquote>'
                    f'<figcaption><span class="words-name">{e(who)}</span><span class="words-session">{e(s)}</span></figcaption></figure>'
                    for i, (who, s, q, _) in enumerate(KIND_WORDS))
    nav = (f'<div class="words-nav"><button class="words-prev" type="button" aria-label="Previous review">{ICON["prev"]}</button>'
           f'<span class="words-count" aria-hidden="true">1 / {n}</span>'
           f'<button class="words-next" type="button" aria-label="Next review">{ICON["next"]}</button></div>') if n > 1 else ''
    return (f'<section class="words-section" aria-labelledby="{uid}-title"><div class="wrap">'
            f'<div class="words" aria-roledescription="carousel" aria-labelledby="{uid}-title">'
            f'<div class="words-photos" aria-hidden="true">{photos}</div>'
            f'<div class="words-panel"><h2 id="{uid}-title">Kind words</h2><div class="words-items" aria-live="polite">{items}</div>'
            f'{nav}{link_arrow("kind-words.html", "Read them all")}</div></div></div></section>')


def instagram_strip():
    ig_name, ig_url = INSTAGRAM
    photos = ''.join(fig(k, SIZES['square'], alt='') for k in INSTAGRAM_STRIP if exists(PHOTOS[k][0]))
    return (f'<section class="insta" aria-label="Instagram"><a class="insta-link" href="{ig_url}">'
            f'<span class="insta-grid" aria-hidden="true">{photos}</span>'
            f'<span class="insta-label">{ICON["instagram"]}<span class="insta-title">Instagram</span>'
            f'<span class="insta-handle">{e(ig_name)}</span></span></a></section>')


def page_head(eyebrow, title_html, lead='', extra=''):
    lead_html = f'<p class="lead">{lead}</p>' if lead else ''
    return (f'<section class="page-head"><div class="wrap narrow"><p class="eyebrow">{e(eyebrow)}</p>'
            f'<h1>{title_html}</h1>{lead_html}{extra}</div></section>')


# ------------------------------------------------------------------ pages
def index():
    tiles = ''.join(f'<li><a class="tile" href="{href}">{fig(key, SIZES["tile"], "tile-photo")}'
                    f'<span class="tile-name">{e(name)}</span></a></li>' for name, key, href in TILES)
    intro = ''.join(f'<p>{e(p)}</p>' for p in INTRO)
    main = f'''{window(HERO, "window--hero", HERO_CAPTION, priority=True)}

<section class="quote"><div class="wrap narrow">
<h1>Photographs that feel like a <em>Sunday afternoon.</em></h1>
<p class="quote-line">Weddings, couples, families, maternity and newborns, from the coast to the hills</p>
</div></section>

<section class="section intro" aria-labelledby="intro-title"><div class="wrap intro-grid">
<div><p class="eyebrow">Why Sunday Light</p><h2 id="intro-title">The best light of the week.</h2>
<div class="prose">{intro}</div><div class="actions">{button("contact.html", "Book a session")}</div></div>
{fig("arch-mirror", SIZES["arch"], "arch")}
</div></section>

{duo()}

{window(HOME_WINDOWS[0])}

<section class="section" aria-labelledby="work-title"><div class="wrap">
<h2 class="center-title" id="work-title">See the work</h2>
<ul class="tiles">{tiles}</ul>
<div class="center">{link_arrow("gallery.html", "View the gallery")}</div>
</div></section>

{window(HOME_WINDOWS[1])}

{kind_words()}

{instagram_strip()}'''
    return page('index.html', 'Sunday Light | Adelaide wedding & family photographer',
                'Natural, light-filled photography for weddings, couples, families, maternity and newborns across Adelaide. Relaxed sessions on the coast, in the hills and at home.',
                main, jsonld=True)


def gallery_item(path, alt, i, first_gallery):
    w, h = size_of(path, (1333, 2000))
    # The first photo is the one people see first, so it loads straight away; the rest load as they come into view.
    pic = picture(path, w, h, alt, SIZES['grid'], priority=first_gallery and i == 0)
    return f'<figure class="ph"><a href="{path}" data-lightbox>{pic}</a></figure>'


def gallery():
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
    lead = (f'Weddings, couples, families, maternity and newborns from around Adelaide. The newest sessions go up on '
            f'<a href="{INSTAGRAM[1]}">Instagram</a> first.')
    main = f'''{page_head("Gallery", "A few <em>favourite days.</em>", lead, chips)}
{sections}
{kind_words()}

{duo()}

{instagram_strip()}'''
    lightbox = ('<dialog class="lightbox" aria-label="Photo viewer"><div class="lightbox-inner">'
                f'<button class="lb-btn lb-prev" type="button" aria-label="Previous photo">{ICON["prev"]}</button>'
                '<figure class="lb-figure"></figure>'
                f'<button class="lb-btn lb-next" type="button" aria-label="Next photo">{ICON["next"]}</button>'
                f'<button class="lb-btn lb-close" type="button" aria-label="Close">{ICON["close"]}</button>'
                '<p class="lb-count" aria-hidden="true"></p><p class="sr-only lb-live" aria-live="polite"></p>'
                '</div></dialog>\n')
    return page('gallery.html', 'Gallery | Sunday Light',
                'Wedding, couples, family, maternity and newborn photography from around Adelaide by Sunday Light.', main,
                body_extra=lightbox)


def investment():
    intro = ''.join(f'<p>{e(p)}</p>' for p in INVESTMENT_INTRO)
    def package(s, with_photo):
        body = ''.join(f'<p>{e(p)}</p>' for p in s['body'])
        enquire = f'contact.html?session={quote_plus(FORM_SESSION[s["id"]])}'
        photo = fig(s['photo'], SIZES['card'], 'package-photo') if with_photo else ''
        includes = ''.join(f'<li>{e(i)}</li>' for i in s.get('includes', []))
        includes = f'<ul class="package-includes">{includes}</ul>' if includes else ''
        more = link_arrow(*s['more']) if s.get('more') else ''
        price = (f'<p class="package-price">{e(s["price"])}</p>' if s.get('price')
                 else '<p class="package-price package-price--ask">Pricing on enquiry</p>')
        return (f'<article class="package{"" if with_photo else " package--text"}" id="{s["id"]}" aria-labelledby="{s["id"]}-title">'
                f'{photo}<div class="package-panel"><h3 class="package-name" id="{s["id"]}-title">{e(s["name"])}</h3>'
                f'<div class="prose">{body}</div>'
                f'<div class="package-meta">{price}{includes}</div>'
                f'<div class="package-links">{more}{link_arrow(enquire, "Enquire about " + s.get("short", s["name"]).lower())}</div>'
                f'</div></article>')

    # Sessions with a photo get a photo card; the rest sit two to a row as text until their photo arrives.
    pictured = [s for s in SESSIONS if exists(PHOTOS[s['photo']][0])]
    waiting = [s for s in SESSIONS if s not in pictured]
    packages = ''.join(package(s, True) for s in pictured)
    if waiting:
        packages += f'<div class="packages-text">{"".join(package(s, False) for s in waiting)}</div>'
    tiers = ''.join(f'<li class="tier" style="--i:{i - 1}"><span class="tier-number" aria-hidden="true">{i:02d}</span>'
                    f'<h3 class="tier-name">{e(name)}</h3><p class="tier-hours">Up to {hours} hours</p>'
                    f'<p class="tier-price">{e(price)}</p></li>' for i, (name, hours, price) in enumerate(WEDDING_PACKAGES, 1))
    wedding_includes = ''.join(f'<li>{e(x)}</li>' for x in WEDDING_INCLUDES)
    wedding_terms = ''.join(f'<li>{e(x)}</li>' for x in WEDDING_TERMS)
    steps = ''.join(f'<li style="--i:{i}"><h3>{e(t)}</h3><p>{e(d)}</p></li>' for i, (t, d) in enumerate(STEPS))
    faq = ''.join(f'<details style="--i:{i}"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for i, (q, a) in enumerate(FAQ))
    main = f'''{window(INVESTMENT_HERO, "window--hero window--short", priority=True)}

{page_head("Investment", "Photos you’ll keep <em>for good.</em>", "", f'<div class="prose">{intro}</div><div class="actions">{button("contact.html", "Book a session")}</div>')}

<section class="section packages-section" aria-labelledby="packages-title"><div class="wrap">
<h2 class="center-title" id="packages-title">Sessions</h2>
<div class="packages">{packages}</div>
</div></section>

<section class="section section--lime wedding-packages" id="wedding-packages" aria-labelledby="wedding-packages-title"><div class="wrap">
<p class="eyebrow eyebrow--center">Weddings</p>
<h2 class="center-title" id="wedding-packages-title">Wedding <em>packages</em></h2>
<ol class="tiers" data-rules>{tiers}</ol>
<div class="tier-notes">
<div><h3>Every package includes</h3><ul class="package-includes">{wedding_includes}</ul></div>
<div><h3>Good to know</h3><ul class="package-includes">{wedding_terms}</ul></div>
</div>
<div class="center">{link_arrow("contact.html?session=Wedding", "Check my wedding dates")}</div>
</div></section>

<section class="section" aria-labelledby="how-title"><div class="wrap">
<h2 class="center-title" id="how-title">How it works</h2>
<ol class="steps" data-rules>{steps}</ol></div></section>

<section class="section" aria-labelledby="faq-title"><div class="wrap narrow">
<h2 class="center-title" id="faq-title">Questions, answered</h2>
<div class="faq" data-rules>{faq}</div></div></section>

{kind_words()}

{instagram_strip()}'''
    return page('investment.html', 'Investment | Sunday Light',
                'Wedding, couples and engagement, family, maternity and newborn photography sessions in Adelaide: prices and what each includes.',
                main)


def kind_words_page():
    if KIND_WORDS_ARE_PLACEHOLDERS or not KIND_WORDS:
        ig_name, ig_url = INSTAGRAM
        main = f'''<section class="page-head holding"><div class="wrap narrow">
{fig(KIND_WORDS_HOLDING_PHOTO, "(max-width: 600px) 64vw, 380px", "arch holding-photo", priority=True)}
<p class="eyebrow">Kind words</p><h1>From the people <em>in the photos.</em></h1>
<p class="lead">This is where couples and families share how their sessions felt. The first few are on their way. In the meantime, the newest sessions go up on Instagram first.</p>
<div class="actions">{link_arrow(ig_url, "Newest sessions on Instagram")}</div>
</div></section>

{instagram_strip()}'''
        out = page('kind-words.html', 'Kind words | Sunday Light',
                   'What couples and families say about their sessions with Sunday Light, Adelaide photographer.', main)
        # kept out of search until there are real reviews to show
        return out.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
    reviews = ''.join(
        f'<article class="review">{fig(k, SIZES["card"], "review-photo", priority=i == 0, alt="")}<div class="review-panel">'
        f'<blockquote><p>“{e(q)}”</p></blockquote><p class="review-name">{e(who)}</p><p class="review-session">{e(s)}</p>'
        f'</div></article>' for i, (who, s, q, k) in enumerate(KIND_WORDS))
    main = f'''{page_head("Kind words", "From the people <em>in the photos.</em>", "A few words from the couples and families I’ve photographed.")}

<section class="section reviews-section"><div class="wrap">
<div class="reviews">{reviews}</div>
<div class="center">{button("contact.html", "Check my dates")}</div>
</div></section>

{instagram_strip()}'''
    return page('kind-words.html', 'Kind words | Sunday Light',
                'What couples and families say about their sessions with Sunday Light, Adelaide photographer.', main)


def contact():
    ig_name, ig_url = INSTAGRAM
    opts = ''.join(f'<option>{e(o)}</option>' for o in FORM_OPTIONS)
    heard = ''.join(f'<option>{o}</option>' for o in ['Instagram', 'A friend', 'Google', 'A wedding vendor', 'Somewhere else'])
    main = f'''{page_head("Contact", "Let’s plan <em>something lovely.</em>", "Tell me a little about what you’re planning. I’ll get back to you with availability and pricing.")}

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
<div class="form-foot"><button class="btn btn--primary btn--send" type="submit"><span>Send</span> <i class="btn-rule" aria-hidden="true"></i> <span>enquiry</span></button><p id="form-status" class="form-status" role="status" aria-live="polite"></p></div>
</form>
<div id="form-success" class="form-success" hidden><p class="eyebrow">Sent</p><h2 tabindex="-1">Thank you.</h2><p>Your enquiry is on its way. I’ll be in touch soon with dates and details.</p>{link_arrow("gallery.html", "Browse the gallery")}</div>
</div>
<aside class="aside" aria-label="What happens next" data-rules>
<div style="--i:0"><h2>What happens next</h2><p>I’ll reply with available dates, pricing and a few ideas for your session.</p></div>
<div style="--i:1"><h2>Prefer Instagram?</h2><p>Send a message to <a href="{ig_url}">{e(ig_name)}</a>.</p></div>
<div style="--i:2"><h2>Based in Adelaide</h2><p>Sessions on the coast, in the hills and at home.</p></div>
</aside>
</div></section>

{instagram_strip()}'''
    return page('contact.html', 'Contact | Sunday Light',
                'Check dates for wedding, couples, family, maternity and newborn photography in Adelaide.', main)


def privacy():
    main = f'''{page_head("Your details", "Privacy")}
<section class="section" style="padding-top:0"><div class="wrap text">
<p>This page explains what happens to the details you share through this website.</p>
<h2>What I collect</h2><p>When you send an enquiry, I receive the details you type into the form: your name, email, and anything else you choose to include, such as a phone number, date or message.</p>
<h2>How I use it</h2><p>Only to reply to your enquiry and, if you book, to plan your session. I don’t sell or share your details for marketing.</p>
<h2>Photos</h2><p>Some session photos appear on this website and on Instagram. If you’d like a photo of you removed, just ask and I’ll take it down.</p>
<h2>Questions or changes</h2><p>To see, correct or delete the details you’ve sent, message me on Instagram at <a href="{INSTAGRAM[1]}">{e(INSTAGRAM[0])}</a>.</p>
</div></section>'''
    return page('', 'Privacy | Sunday Light', 'How Sunday Light handles the details you share.', main)


def not_found():
    main = f'''<section class="page-head" style="padding-bottom:clamp(72px,10vw,140px)"><div class="wrap narrow">
{arch_svg("nf", cls="nf-mark", stroke=3)}
<p class="eyebrow">Page not found</p><h1>This page has <em>wandered off.</em></h1>
<p class="lead">It may have moved, or the link may be old.</p>
<div class="actions">{button("index.html", "Back home")}{link_arrow("gallery.html", "See the gallery")}</div></div></section>'''
    out = page('', 'Page not found | Sunday Light', 'This page could not be found.', main, html_attrs=' data-nf')
    # served for missing paths at any depth, so resolve every link from the site root
    return out.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="/">', 1)


PAGES = {'index.html': index, 'gallery.html': gallery, 'investment.html': investment, 'kind-words.html': kind_words_page,
         'contact.html': contact, 'privacy.html': privacy, '404.html': not_found}
RETIRED = ['portfolio.html', 'sessions.html', 'about.html', 'enquire.html']  # replaced by the pages above


def assemble(out):
    """Join the stylesheet and script parts into styles.css and main.js."""
    for ext, name, note in (('css', 'styles.css', '/* Sunday Light. Built from tools/site/css/ by tools/site/build.py: edit the parts there. */\n'),
                            ('js', 'main.js', '// Sunday Light. Built from tools/site/js/ by tools/site/build.py: edit the parts there.\n')):
        parts = sorted(glob.glob(os.path.join(HERE, ext, f'*.{ext}')))
        with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
            f.write(note + ''.join(open(part, encoding='utf-8').read() for part in parts))


def main(out=ROOT):
    os.makedirs(os.path.join(out, 'images'), exist_ok=True)
    assemble(out)
    for name, fn in PAGES.items():
        with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
            f.write(fn())
    for name in RETIRED:
        if os.path.exists(os.path.join(out, name)):
            os.remove(os.path.join(out, name))
    with open(os.path.join(out, 'favicon.svg'), 'w', encoding='utf-8') as f:
        f.write(FAVICON)
    with open(os.path.join(out, 'images', 'placeholder.svg'), 'w', encoding='utf-8') as f:
        f.write(PLACEHOLDER)
    print('built', ', '.join(PAGES), '->', out)
    if KIND_WORDS_ARE_PLACEHOLDERS:
        print('Reminder: the Kind words are still placeholders. Swap in real reviews in tools/site/content.py before launch.')


if __name__ == '__main__':
    main(os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
