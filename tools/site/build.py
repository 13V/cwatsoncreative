# Builds the Selah Stories pages.
#
#   python3 tools/site/build.py           # writes into the repo root
#   python3 tools/site/build.py out_dir   # or somewhere else, for a look before replacing the real pages
#
# Writes the HTML pages, styles.css, main.js and favicon.svg, then checks them (verify(): the honesty net, the SVG and
# breakpoint rules, and the budgets); the build fails if a check does. styles.css and main.js are joined from the
# numbered parts in tools/site/css/ and tools/site/js/ (in file-name order), so edit the parts, not the joined files.
# Every SVG comes from art.py; this file holds none. A photo only appears once its file exists, so run this again
# after adding photos (tools/prepare_photos.py does that for you).
import glob, gzip, hashlib, html, json, os, re, sys
from html.parser import HTMLParser
from urllib.parse import quote_plus

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import art  # noqa: E402
from art import icon, mark  # noqa: E402
# Everything the pages read from content.py (plan §4.3), imported once here so page packages never edit this line.
from content import (  # noqa: E402,F401
    PHOTOS, WEDDING_KEYS, FOCUS, PLACES, EXTRA_GALLERIES, INSTAGRAM, ENDPOINT, FORM_ACTION, FORM_SESSION, FORM_OPTIONS,
    HERO, HERO_TITLE, HOME_WINDOWS, HOME_STATEMENT_PHOTO, HOME_TILE_PHOTO, STATEMENT_LINE, INTRO, INSTAGRAM_STRIP,
    CLOSING, CLOSING_LEAD, GALLERY_CHAPTERS, rhythm, rhythm_groups, landscape,
    SESSIONS, SESSION, SPEC_LABELS, LOCATION, GALLERY, INVESTMENT_HERO, INVESTMENT_INTRO, WEDDING_PACKAGES,
    WEDDING_INCLUDES, WEDDING_TERMS, STEPS, FAQ, min_price, CONTACT_PHOTO, OLD_ANCHORS,
    KIND_WORDS, KIND_WORDS_ARE_PLACEHOLDERS, KIND_WORDS_HOLDING_PHOTO, plain)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))  # the photos are looked up here

try:
    from PIL import Image
except ImportError:  # photo sizes then come from content.py, and photo wells stay Sand
    Image = None


def e(s):
    return html.escape(s, quote=True)


# ------------------------------------------------------------------ breakpoints and photo sizes (UI spec §2.5, §7.6)
BP_XS, BP_SM, BP_MD, BP_LG, BP_XL = 400, 600, 861, 1100, 1440   # min-widths; their complements are one less
WRAP = 1240
PHONE, SMALL, WIDE = f'(max-width: {BP_MD - 1}px)', f'(max-width: {BP_SM - 1}px)', f'(max-width: {WRAP}px)'
WIDTHS = (320, 480, 800, 1000, 1200)   # WebP copies at these widths, plus the full-size file (tools/prepare_photos.py)

# How wide each kind of photo shows, so phones load a small copy and large screens a big one. Photos that fill a
# screen-tall layer render two-thirds of the screen's height wide (66.7vh). Keys are API for the page packages.
SIZES = {
    'hero': f'{PHONE} max(100vw, 66.7vh), max(50vw, 66.7vh)',
    'window1': f'{PHONE} max(100vw, 66.7vh), 100vw',
    'window3': f'{PHONE} max(100vw, 66.7vh), max(34vw, 66.7vh)',
    'window2': f'{PHONE} max(100vw, 66.7vh), max(50vw, 66.7vh)',
    'inv-hero': f'{PHONE} 100vw, 50vw',
    'statement': f'(max-width: 499px) 80vw, {PHONE} 400px, {WIDE} calc(30vw - 12px), 360px',
    'contact': f'{PHONE} 64vw, {WIDE} calc(30vw - 12px), 360px',
    'cover': f'{PHONE} min(82vw, 480px), {WIDE} calc(38vw - 14px), 455px',
    'kw-holding': f'{PHONE} 48vw, 300px',
    'tile': f'{PHONE} calc(50vw - 26px), {WIDE} calc(30vw - 16px), 355px',
    'session': f'{PHONE} 100vw, {WIDE} calc(45vw - 8px), 548px',
    'rg-wide': f'{SMALL} 100vw, {PHONE} 90vw, {WIDE} calc(75vw - 14px), 935px',
    'rg-land': f'{SMALL} 100vw, {WIDE} calc(45vw - 8px), 548px',
    'rg-pair-wide': f'{SMALL} calc(100vw - 40px), {PHONE} calc(45vw - 6px), {WIDE} calc(45vw - 8px), 548px',
    'rg-pair-narrow': f'{SMALL} max(calc(64vw - 26px), 220px), {PHONE} calc(45vw - 6px), {WIDE} calc(30vw - 12px), 360px',
    'rg-solo': f'{SMALL} max(calc(78vw - 31px), 220px), {PHONE} 58vw, {WIDE} calc(38vw - 14px), 455px',
    'sheet': f'{PHONE} calc(33vw - 17px), {WIDE} calc(15vw - 6px), 180px',
    'viewer': '100vw',
}


# ------------------------------------------------------------------ line plans
def lines(plan):
    """A heading's line plan as HTML: '|' breaks below 861px only, '/' from 861px only, '//' at every width (each break
    is followed by a space, so the accessible name keeps it), '*…*' is the italic phrase."""
    out = e(plan).replace('//', '\0').replace('|', '<br class="br-sm"> ').replace('/', '<br class="br-md"> ')
    return re.sub(r'\*(.+?)\*', r'<em>\1</em>', out.replace('\0', '<br> '))


# ------------------------------------------------------------------ photos
def exists(path):
    return os.path.isfile(os.path.join(ROOT, path))


_size, _tone = {}, {}


def size_of(path, fallback):
    if path not in _size:
        _size[path] = fallback
        if Image:
            try:
                with Image.open(os.path.join(ROOT, path)) as im:
                    _size[path] = im.size
            except OSError:
                pass
    return _size[path]


def tone(path):
    """The photo's own average colour mixed 65% toward Paper: the well a lazy photo arrives out of."""
    if path not in _tone:
        _tone[path] = None
        if Image:
            try:
                with Image.open(os.path.join(ROOT, path)) as im:
                    im.draft('RGB', (64, 64))
                    avg = im.convert('RGB').resize((1, 1), Image.BOX).getpixel((0, 0))
                _tone[path] = '#' + ''.join(f'{round(c + .65 * (p - c)):02X}' for c, p in zip(avg, (0xF6, 0xF2, 0xEA)))
            except OSError:
                pass
    return _tone[path]


def srcset(path, w):
    stem = path.rsplit('.', 1)[0]
    rungs = [(v, f'{stem}-{v}.webp') for v in WIDTHS if v <= w and exists(f'{stem}-{v}.webp')]
    if not any(v == w for v, _ in rungs) and exists(f'{stem}.webp'):
        rungs.append((w, f'{stem}.webp'))
    return ', '.join(f'{p} {v}w' for v, p in rungs)


def _picture(path, w, h, alt, sizes, priority=False, eager=False, high=False):
    ss, sz = srcset(path, w), SIZES.get(sizes, sizes)
    source = f'<source type="image/webp" srcset="{ss}" sizes="{sz}">' if ss else ''
    load = (' fetchpriority="high" data-lcp' if priority else '' if eager else
            ' loading="lazy" decoding="async"' + (' fetchpriority="high"' if high else ''))
    return f'<picture>{source}<img src="{path}" width="{w}" height="{h}" alt="{e(alt)}"{load}></picture>'


def picture(key, sizes, *, alt=None, priority=False, eager=False, high=False):
    """A photo: WebP copies for browsers that take them, the JPEG for the rest. `sizes` is a SIZES key or a literal.
    priority (the page's LCP photo): fetchpriority="high" and data-lcp, never lazy. high: lazy, but first in line."""
    path, w, h, text, _ = PHOTOS[key]
    w, h = size_of(path, (w, h))
    return _picture(path, w, h, text if alt is None else alt, sizes, priority, eager, high)


def fig(key, sizes, *, cls='', ratio=None, tag='figure', fill=False, priority=False, eager=False, high=False, alt=None,
        tray=False, attrs='', style=''):
    """A photo slot (.ph): '' when the file doesn't exist, so empty slots never render. Inline: --ph (the photo's
    tone), --focus (where the faces are) and the aspect ratio (native, or `ratio` like '4/5'), unless `fill` (the
    slot's box sets its size: windows, hero panes, the Instagram sheet). tray: M10 develops it on arrival."""
    path = PHOTOS[key][0]
    if not exists(path):
        return ''
    w, h = size_of(path, PHOTOS[key][1:3])
    classes = ' '.join(c for c in ('ph', 'ph--tray' if tray else '', cls) if c)
    st = [f'--ph:{tone(path)}'] if tone(path) else []
    if key in FOCUS:
        st.append(f'--focus:{FOCUS[key]}')
    if not fill:
        st.append('aspect-ratio:' + (ratio.replace('/', ' / ') if ratio else f'{w} / {h}'))
    if style:
        st.append(style)
    return (f'<{tag} class="{classes}" style="{"; ".join(st)}"{attrs}>'
            f'{picture(key, sizes, alt=alt, priority=priority, eager=eager, high=high)}</{tag}>')


def arch_frame(key, sizes, ratio, *, keyline=False, door=False, cls='', **fig_kwargs):
    """An arch-masked photo (ratio '2x3', '3x4' or '4x5'); keyline adds the gold A3 line 8px outside it; door marks
    it as a doorway for the page change (M14). '' when the photo is missing."""
    f = fig(key, sizes, cls='frame--arch', ratio=ratio.replace('x', '/'), attrs=' data-door-frame' if door else '', **fig_kwargs)
    if not f:
        return ''
    return f'<div class="frame frame--{ratio}{(" " + cls) if cls else ""}">{f}{art.arch_line(ratio) if keyline else ""}</div>'


ABOVE = {'paper': 'paper', 'limestone': 'limestone'}


def window(keys, kind, *, above='paper', overlay='', label_id=None):
    """A photo window (M02). kind 'hero': the Home hero, a flush section holding the LCP photo (first key) and the
    page's overlay (scrim and copy). kind 'a' | 'b': decorative, seen through an arcade of arches in the colour of the
    section above (`above`), one arch per photo. Phones show the first photo; from 861px every photo, mullioned."""
    keys = [k for k in keys if exists(PHOTOS[k][0])]
    if not keys:
        return ''
    n = len(keys)
    sizes = ('hero' if n > 1 else 'window1') if kind == 'hero' else {1: 'window1', 2: 'window2'}.get(n, 'window3')
    photos = ''.join(fig(k, sizes, fill=True, alt='', priority=kind == 'hero' and i == 0, cls='ph--wide-only' if i else '')
                     for i, k in enumerate(keys))
    aperture = f'<div class="window-aperture"><div class="window-photos">{photos}</div></div>'
    if kind == 'hero':
        label = f' aria-labelledby="{label_id}"' if label_id else ''
        return (f'<section class="window window--hero sec--flush" data-window="hero" data-count="{n}"{label}>'
                f'{aperture}{overlay}</section>')
    arches = ''.join(f'<span style="--i:{i}">{art.window_arch()}</span>' for i in range(n))
    return (f'<div class="window window--{kind}" data-window="{kind}" data-count="{n}" aria-hidden="true" '
            f'style="--above: var(--{ABOVE[above]})">{aperture}<div class="window-arches">{arches}</div></div>')


# ------------------------------------------------------------------ links and buttons
def link_arrow(href, text, *, light=False, external=False, cls=''):
    """A text link with the long arrow (B1); external links (Instagram) take the up-right arrow (B2) and rel="me"."""
    classes = ' '.join(c for c in ('link-arrow', 'link-arrow--light' if light else '',
                                   'link-arrow--external' if external else '', cls) if c)
    return (f'<a class="{classes}" href="{href}"{" rel=" + chr(34) + "me" + chr(34) if external else ""}>'
            f'<span class="la-label">{e(text)}</span>{icon("arrow-ne" if external else "arrow")}</a>')


def button(href, text, *, variant='primary', arrow=True, cls='', attrs=''):
    """A pill link (the sunrise button). variant: primary | secondary | sm."""
    return (f'<a class="btn btn--{variant}{(" " + cls) if cls else ""}" href="{href}"{attrs}><span class="btn-label">{e(text)}</span>'
            f'{icon("arrow") if arrow else ""}</a>')


# ------------------------------------------------------------------ shared sections
def page_head(eyebrow, title_html, lead_html='', *, layout='left', extra='', cls='', grid=False):
    lead = f'<p class="lead">{lead_html}</p>' if lead_html else ''
    return (f'<section class="page-head sec--compact head--{layout}{(" " + cls) if cls else ""}"><div class="wrap{" grid-12" if grid else ""}">'
            f'<p class="eyebrow">{e(eyebrow)}</p><h1>{title_html}</h1>{lead}{extra}</div></section>')


def index_bar(label, items):
    """The sticky index under the header (Gallery chapters, Investment sessions). items: [(ids, text, count|None)];
    the link goes to the first id, and the scroll-spy marks it current for any of them."""
    links = ''
    for ids, text, count in items:
        sup = ''   # no counts: the owner asked for the numbers to go
        links += (f'<a href="#{ids[0]}" data-spy="{" ".join(ids)}"><span class="ix-label">{e(text)}{art.brush()}</span>'
                  f'{sup}</a>')
    return f'<nav class="index-bar" aria-label="{e(label)}"><div class="index wrap">{links}</div></nav>'


def closing(page_key):
    """The closing invitation: the last section before the footer on Home, Gallery, Investment and Kind words, each
    with its own line."""
    ig_name, ig_url = INSTAGRAM
    facts = ['Based in Adelaide', 'Coast, hills &amp; home', f'Weddings from {e(min_price(WEDDING_PACKAGES))}']
    return (f'<section class="closing sec--breath head--center" aria-labelledby="closing-title"><div class="wrap">'
            f'{art.orn_window()}<h2 id="closing-title" class="t-display-xl">{lines(CLOSING[page_key])}</h2>'
            f'<p class="closing-lead">{e(CLOSING_LEAD)}</p>'
            f'<div class="actions closing-actions">{button("contact.html", "Check my dates")}'
            f'{link_arrow(ig_url, "Or message me on Instagram", external=True)}</div>'
            f'<ul class="facts t-caption" role="list">{"".join(f"<li>{x}</li>" for x in facts)}</ul></div></section>')


def instagram_sheet(tone='paper'):
    """The Instagram contact sheet (Home, and Kind words on Limestone): one link, six portraits at full strength."""
    ig_name, ig_url = INSTAGRAM
    photos = ''.join(fig(k, 'sheet', tag='span', fill=True, alt='', style=f'--i:{i}') for i, k in enumerate(INSTAGRAM_STRIP))
    return (f'<section class="sheet sec--compact panel{" sheet--limestone" if tone == "limestone" else ""}" '
            f'aria-labelledby="sheet-title"><a class="sheet-link wrap" href="{ig_url}" rel="me">'
            f'<span class="sheet-label">{icon("instagram")}<span class="eyebrow" id="sheet-title">On Instagram</span> '
            f'<span class="sheet-rule" aria-hidden="true"></span><span class="sheet-handle">{e(ig_name)} {icon("arrow-ne")}</span></span>'
            f'<span class="sheet-photos" aria-hidden="true">{photos}</span></a></section>')


def kind_words(where):
    """The Kind words interlude on Home ('index') and Investment ('investment'): one real review. Nothing at all while
    the reviews are placeholders. (The body is WP4's.)"""
    if KIND_WORDS_ARE_PLACEHOLDERS or not KIND_WORDS:
        return ''
    r = review_for(where)
    return (f'<section class="interlude sec--breath panel head--center" aria-label="Kind words"><div class="wrap">'
            f'{art.orn_window()}<figure><blockquote><p class="t-quote"><span class="q-open">“</span>{review_words(r, True)}”</p>'
            f'</blockquote><figcaption class="cite">{review_cite(r)}</figcaption></figure></div></section>')


def review_for(where):
    """The interlude's review: a featured one first; on Investment a wedding review, and a different one from Home's
    when there is one."""
    pool = [r for r in KIND_WORDS if r.get('feature')] or KIND_WORDS
    if where == 'investment':
        weddings = [r for r in pool if 'wedding' in r['session'].lower()] or pool
        return next((r for r in weddings if r is not pool[0]), weddings[0])
    return pool[0]


def review_words(r, pull=False):
    """A review exactly as written (never edited), escaped; its pull phrase, an exact part of it, set in italic."""
    assert not r['pull'] or r['pull'] in r['words'], f'the pull phrase must be an exact part of the review: {r["pull"]!r}'
    words = e(r['words'])
    return words.replace(e(r['pull']), f'<em>{e(r["pull"])}</em>', 1) if pull and r['pull'] else words


def review_cite(r):
    return ' · '.join(e(v) for v in (r['names'], r['session'], r.get('place'), r.get('season')) if v)


# ------------------------------------------------------------------ chrome
NAV = [('gallery.html', 'Gallery'), ('investment.html', 'Investment'), ('kind-words.html', 'Kind words'),
       ('contact.html', 'Contact')]
SUN = '<span class="nav-sun" aria-hidden="true"></span>'


def current(href, active):
    return ' aria-current="page"' if href == active else ''


def header(active):
    ig_name, ig_url = INSTAGRAM
    links = ''.join(f'<a href="{h}"{" class=" + chr(34) + "nav-contact" + chr(34) if h == "contact.html" else ""} style="--i:{i}"'
                    f'{current(h, active)}><span class="nl"><span>{t}</span></span>{SUN if h == active else ""}</a>'
                    for i, (h, t) in enumerate(NAV))
    return (f'<a class="skip" href="#main">Skip to content</a>\n'
            f'<header class="site-header" id="top" tabindex="-1"><div class="header-inner wrap">'
            f'<nav id="site-nav" class="site-nav xfade" aria-label="Main"><span class="nav-sheet" aria-hidden="true"></span>{links}'
            f'<div class="menu-foot"><a class="nav-instagram" href="{ig_url}" rel="me">{icon("instagram")}'
            f'<span><span class="sr-only">Instagram </span>{e(ig_name)}</span>{icon("arrow-ne")}</a>'
            f'<span class="menu-place t-micro">Adelaide, South Australia</span></div></nav>'
            f'<a class="brand" href="index.html" aria-label="Selah Stories, home">{mark("h", "sm")}'
            f'<span class="brand-name">Selah Stories</span></a>'
            f'<a class="btn btn--sm btn--secondary header-cta" href="contact.html"{current("contact.html", active)}>Contact</a>'
            f'<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">'
            f'<span class="nav-toggle-label">Menu</span><span class="bars" aria-hidden="true"></span></button>'
            f'</div></header>\n')


def footer(active):
    ig_name, ig_url = INSTAGRAM
    nav = ''.join(f'<a href="{h}"{current(h, active)}>{t}{SUN if h == active else ""}</a>' for h, t in NAV)
    dot = '<span class="dot" aria-hidden="true"> · </span>'   # hidden below 861px, where each part gets its own line
    return (f'<footer class="site-footer"><a class="sundown" href="index.html" aria-label="Selah Stories, home">'
            f'<span class="sundown-scene">{art.footer_scene("m")}{art.footer_scene("w")}</span>'
            f'<span class="sundown-word" aria-hidden="true"><span>Selah Stories</span></span></a>'
            f'<div class="footer-inner wrap"><nav class="footer-nav" aria-label="Footer">{nav}</nav>'
            f'<a class="footer-instagram" href="{ig_url}" rel="me">{icon("instagram")}'
            f'<span><span class="sr-only">Instagram </span>{e(ig_name)}</span>{icon("arrow-ne")}</a>'
            f'<p class="golden-hour" data-golden>Golden hour: the last hour before sunset, and the best light of the day.</p>'
            f'<p class="footer-base t-caption"><span class="fb">&copy; <span data-year>2026</span> Selah Stories</span>'
            f'<span class="fb">{dot}Adelaide, South Australia</span>'
            f'<span class="fb">{dot}<a href="privacy.html">Privacy</a> · Website by <a href="https://www.lumenadl.com/">Lumen</a></span>'
            f'<span class="fb fb-still" hidden>{dot}<button class="still-toggle" type="button" aria-pressed="false">Hold still</button></span>'
            f'<span class="fb">{dot}<a class="to-top" href="#top">Back to top {icon("to-top")}</a></span></p>'
            f'</div></footer>\n')


JSONLD = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "Selah Stories",
    "description": "Natural, light-filled wedding, couples, engagement, family, maternity and newborn photography in Adelaide, South Australia.",
    "areaServed": {"@type": "City", "name": "Adelaide"},
    "address": {"@type": "PostalAddress", "addressLocality": "Adelaide", "addressRegion": "SA", "addressCountry": "AU"},
    "knowsAbout": ["Wedding photography", "Engagement photography", "Couples photography",
                   "Family photography", "Maternity photography", "Newborn photography"],
    "sameAs": [INSTAGRAM[1]],
}

# Runs before first paint. Sets .js; .m when motion is welcome (no reduced motion, not "Hold still"); .first-light
# on the first page of a visit; and lets the page change (M01) through only for fresh link navigations.
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


def font_preload(name):
    return f'<link rel="preload" href="fonts/{name}.woff2" as="font" type="font/woff2" crossorigin>\n'


# The name in the header and the footer is wordmark.svg (art.py A2b) painted through a CSS mask, and a mask paints
# nothing until its image arrives. So the file is named by its content (the build writes styles.css with that name),
# vercel.json caches it for good, and every page preloads it (crossorigin: mask images are fetched in CORS mode).
WORDMARK = f'wordmark-{hashlib.sha256(art.wordmark_svg().encode()).hexdigest()[:10]}.svg'
WORDMARK_PRELOAD = f'<link rel="preload" href="{WORDMARK}" as="image" type="image/svg+xml" crossorigin>\n'


def lcp_preload(lcp):
    """The LCP photo's preload, from the same srcset builder and SIZES entry as its <source>."""
    key, sizes = lcp
    path, w, h, _, _ = PHOTOS[key]
    if not exists(path):
        return ''
    w, _ = size_of(path, (w, h))
    return (f'<link rel="preload" as="image" type="image/webp" imagesrcset="{srcset(path, w)}" '
            f'imagesizes="{SIZES.get(sizes, sizes)}" fetchpriority="high">\n')


FONT_PRELOADS = 2   # at most: Brygada roman, and Proza 400 where a page names it


def head(title, desc, *, jsonld=False, lcp=None, fonts=()):
    # The LCP photo first, then Brygada roman (every page's headings) and any face a page names in fonts (Proza 400,
    # where body text is in the first view), then the wordmark; every other face swaps onto its metric-matched
    # fallback without moving anything (00-base.css).
    preload = ((lcp_preload(lcp) if lcp else '') + ''.join(map(font_preload, ('brygada-1918-400-700', *fonts)))
               + WORDMARK_PRELOAD)
    ld = f'<script type="application/ld+json">{json.dumps(JSONLD, ensure_ascii=False)}</script>\n' if jsonld else ''
    return (f'{preload}<title>{e(title)}</title>\n<meta name="description" content="{e(desc)}">\n'
            f'<meta property="og:title" content="{e(title)}">\n<meta property="og:description" content="{e(desc)}">\n'
            f'<meta property="og:type" content="website">\n<meta property="og:image" content="images/og-card.jpg">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n<meta name="theme-color" content="#F6F2EA">\n'
            f'<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
            f'<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">\n'
            f'<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
            f'<link rel="stylesheet" href="styles.css">\n<script>{HEAD_SCRIPT}</script>\n'
            f'<script src="main.js" defer></script>\n{ld}')


def page(page_key, active, title, desc, main, *, lcp=None, jsonld=False, robots=None, body_extra='', fonts=()):
    """A whole page. page_key: home | gallery | investment | kind-words | contact | privacy | 404 (data-page). lcp: the
    LCP photo as (key, SIZES key) on pages that preload it (Home, Investment). fonts: a face to preload beside Brygada
    roman: Proza 400 where body text is in the first view and no LCP photo needs the bandwidth (Contact, Privacy).
    Late or not, every face lands on a metric-matched fallback without moving anything (pages.test.js)."""
    attrs = f' data-page="{page_key}"' + (' data-nf' if page_key == '404' else '')
    out = (f'<!doctype html>\n<html lang="en-AU"{attrs}>\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           + (f'<meta name="robots" content="{robots}">\n' if robots else '')
           + head(title, desc, jsonld=jsonld, lcp=lcp, fonts=fonts) + '</head>\n<body>\n' + header(active)
           + f'<main id="main" tabindex="-1">\n{main}\n</main>\n' + footer(active) + body_extra + '</body>\n</html>\n')
    return root_absolute(out) if page_key == '404' else out


def root_absolute(out):
    """The 404 is served for missing paths at any depth, so every URL resolves from the site root (no <base>, which
    would also send #main and #top to the home page)."""
    local = r'(?![/#]|[a-z][a-z0-9+.-]*:)'   # not already absolute, a fragment, or another scheme
    out = re.sub(r'(\s(?:href|src)=")' + local, r'\1/', out)
    out = re.sub(r'(\s(?:srcset|imagesrcset)=")([^"]*)"',
                 lambda m: m.group(1) + re.sub(r'(^|,\s*)' + local, r'\1/', m.group(2)) + '"', out)
    return out.replace('property="og:image" content="images/', 'property="og:image" content="/images/')


# ------------------------------------------------------------------ pages


def index():
    """Home (spec §5.1): hero window → statement → window A → sessions band → window B → (interlude) → Instagram
    sheet → closing. Every section after a window is a .panel that slides over the held photo."""
    main = f'''{window(HERO, "hero", overlay=home_hero_copy(), label_id="hero-title")}

{home_statement()}

{window(HOME_WINDOWS[0], "a", above="paper")}

{home_sessions()}

{window(HOME_WINDOWS[1], "b", above="limestone")}

{kind_words("index")}

{instagram_sheet()}

{closing("index")}'''
    return page('home', 'index.html', 'Selah Stories | Adelaide wedding & family photographer',
                'Natural, light-filled photography for weddings, couples, families, maternity and newborns across Adelaide. Relaxed sessions on the coast, in the hills and at home.',
                main, lcp=(HERO[0], 'hero'), jsonld=True)


def home_hero_copy():
    """The h1 on the hero photo (§4.4): Mist over a scrim anchored to the photo's bottom edge, so every glyph sits in
    the measured contrast bands (§2.2). Nothing here moves at load."""
    cue = (f'<a class="scroll-cue" href="#statement" aria-label="Scroll to read more">'
           f'<span class="t-micro" aria-hidden="true">Scroll</span>{art.scroll_cue()}</a>')
    return (f'<div class="hero-scrim" aria-hidden="true"></div><div class="hero-copy">'
            f'<h1 class="hero-title t-display" id="hero-title">{lines(HERO_TITLE)}</h1>'
            f'<div class="hero-meta">{link_arrow("contact.html", "Check my dates", light=True)}{cue}</div></div>')


def home_statement():
    """Her first sentence as the type moment, then the arch photo (M05) beside the rest of her intro (§4.8). The last
    two sentences of INTRO[1] are the closing's line, so nothing repeats."""
    first, rest = INTRO[0].split('. ', 1)
    guide, after = INTRO[1].split('. ', 1)
    assert plain(STATEMENT_LINE) == first + '.' and after == plain(CLOSING['index'])
    body = ''.join(f'<p>{e(p)}</p>' for p in (rest, guide + '.'))
    return (f'<section class="statement sec--breath panel" id="statement"><div class="wrap">'
            f'<p class="t-display-xl statement-line">{lines(STATEMENT_LINE)}</p>'
            f'<div class="statement-body grid-12">{arch_frame(HOME_STATEMENT_PHOTO, "statement", "2x3", keyline=True)}'
            f'<div class="statement-text">{body}{link_arrow("investment.html", "Sessions & pricing")}</div></div>'
            f'</div></section>')


# Where each session's Home tile leads, and what its small label says (§4.9, §6.3).
HOME_TILE_LINK = {'weddings': ('gallery.html', 'See the gallery'),
                  'couples': ('investment.html#couples', 'Engagements &\u00a0proposals too')}   # never ends a line on '&'


def home_sessions():
    """Session tiles (§4.9): an arch photo tile for every session with a photo (it opens the next page through its
    arch, M14, and develops as it arrives, M10); every session without one is named in a single text tile."""
    items, words = [], []
    for s in SESSIONS:
        name = s.get('short', s['name'])
        href, sub = HOME_TILE_LINK.get(s['id'], (f'investment.html#{s["id"]}', 'Sessions & pricing'))
        photo = arch_frame(HOME_TILE_PHOTO.get(s['id'], s['photo']), 'tile', '3x4', door=True, tray=True, alt='')
        if not photo:
            words.append(s)
            continue
        items.append(f'<li style="--i:{len(items)}"><a class="tile" href="{href}" data-door>{photo}'
                     f'<span class="tile-name">{e(name)}</span><span class="sr-only">, </span>'
                     f'<span class="tile-sub">{e(sub)}</span></a></li>')
    if words:
        names = '<br> '.join(e(s.get('short', s['name'])) for s in words)
        items.append(f'<li class="tiles-words" style="--i:{len(items)}"><a class="tile tile--words" '
                     f'href="investment.html#{words[0]["id"]}"><span class="tile-words">{names}</span>'
                     f'<span class="tile-rule" aria-hidden="true"></span><span class="sr-only">, </span>'
                     f'<span class="tile-sub">Sessions &amp; pricing</span></a></li>')
    return (f'<section class="sessions sec--band panel" aria-labelledby="sessions-title"><div class="wrap">'
            f'<div class="sessions-head"><p class="eyebrow">Sessions</p>'
            f'<h2 id="sessions-title">From the coast <em>to the hills.</em></h2>'
            f'<p class="sessions-lead">Weddings, couples, families, maternity and newborns.</p></div>'
            f'<ul class="tiles" role="list">{"".join(items)}</ul></div></section>')


def gallery():
    """Gallery (spec §5.2): the wedding chapters, cover first and then the rhythm grid; extra galleries once their
    files exist; the closing; the photo viewer. DOM order is the viewing order (grid, tab and viewer)."""
    chapters = [(cid, title, line, [k for k in keys if exists(PHOTOS[k][0])]) for cid, title, line, keys in GALLERY_CHAPTERS]
    chapters = [c for c in chapters if c[3]]
    extras = []
    for gid, name, pattern, n, alt in EXTRA_GALLERIES:
        keys = []
        for i in range(1, n + 1):
            path = pattern.format(i)
            if exists(path):   # registered as a photo slot so fig() and rhythm_groups() read it like any other
                PHOTOS.setdefault(f'{gid}-{i:02d}', (path, *size_of(path, (1333, 2000)), alt, ''))
                keys.append(f'{gid}-{i:02d}')
        if keys:
            extras.append((gid, name, '', keys))
    def listing(galleries):
        names = [g if i == 0 else g.lower() for i, g in enumerate(galleries)]
        return (', '.join(names[:-1]) + ' and ' + names[-1]) if len(names) > 1 else ''.join(names)
    names, kinds = listing((['Weddings'] if chapters else []) + [x[1] for x in extras]), \
        listing((['Wedding'] if chapters else []) + [x[1] for x in extras])
    lead = (f'{e(names)} from around Adelaide. ' if names else '') + \
        f'The newest sessions go up on <a href="{INSTAGRAM[1]}">Instagram</a> first.'
    desc = f'{kinds} photography from around Adelaide by Selah Stories.' if kinds else 'Photography by Selah Stories, Adelaide.'
    if extras:   # spec §4.10: galleries once others exist, chapters while only weddings do
        bar = index_bar('Galleries', ([(['weddings'], 'Weddings', sum(len(c[3]) for c in chapters))] if chapters else [])
                        + [([gid], name, len(keys)) for gid, name, _, keys in extras])
    else:
        bar = index_bar('Chapters', [([cid], title, len(keys)) for cid, title, _, keys in chapters]) if chapters else ''
    groups, index, sections = rhythm_groups(chapters + extras), 0, []
    for c, (cid, title, line, keys) in enumerate(chapters + extras):
        sections.append(gallery_section(c, cid, title, line, keys, groups[c], index, numbered=c < len(chapters)))
        index += len(keys)
    weddings = ''.join(sections[:len(chapters)])
    main = f'''{page_head("Gallery", lines("A few//*favourite days.*"), lead, layout="left", cls="gallery-head", grid=True)}
{bar}
{f'<div id="weddings">{weddings}</div>' if weddings else ''}
{''.join(sections[len(chapters):])}
{closing("gallery")}'''
    return page('gallery', 'gallery.html', 'Gallery | Selah Stories', desc, main, body_extra=viewer(index))


RG_SIZES = {'wide': ['rg-wide'], 'land-pair': ['rg-land', 'rg-land'], 'pair-l': ['rg-pair-wide', 'rg-pair-narrow'],
            'pair-r': ['rg-pair-narrow', 'rg-pair-wide'], 'solo-l': ['rg-solo'], 'solo-r': ['rg-solo']}


def ph_link(key, index, chapter, inner, cls=''):
    """A photo that opens the viewer (spec §4.11); without JS it opens the full JPEG."""
    return (f'<a class="ph-link{cls}" href="{PHOTOS[key][0]}" data-viewer data-index="{index}" '
            f'data-chapter="{e(chapter)}">{inner}</a>')


def gallery_section(c, cid, title, line, keys, groups, index, numbered=True):
    """A chapter (or an extra gallery): the cover-first opener (spec §4.11), then the rest of its photos in the rhythm
    grid, one .rg per group from content.rhythm_groups(). Chapter 01's cover is the page's LCP photo (spec §7.6)."""
    cover = arch_frame(keys[0], 'cover', '2x3', priority=c == 0)
    head = (f'<div class="chapter-head grid-12">{ph_link(keys[0], index, title, cover, " chapter-cover")}'
            f'<div class="chapter-text"><h2 id="{cid}-title">{e(title)}</h2>'
            + (f'<p class="lead-i">{e(line)}</p>' if line else '') + '</div></div>')
    rows, i = '', index + 1
    for kind, members in groups:
        links = ''
        for key, sizes in zip(members, RG_SIZES[kind]):
            links += ph_link(key, i, title, fig(key, sizes, tray=True))
            i += 1
        rows += f'<div class="rg rg--{kind}">{links}</div>'
    return (f'<section class="chapter sec--standard{" chapter--alt" if c % 2 else ""}" id="{cid}" aria-labelledby="{cid}-title">'
            f'<div class="wrap">{head}{rows}</div></section>\n')


def viewer(total):
    """The photo viewer (spec §4.12; M06, M11): an opaque darkroom, bare controls, a track and a rolling counter.
    50-viewer.js fills it from the photo links; without showModal() the links simply open the JPEG."""
    return (f'<dialog class="viewer" aria-label="Photo viewer" data-sizes="{SIZES["viewer"]}">'
            '<div class="viewer-dark xfade" aria-hidden="true"></div>'
            '<div class="viewer-top"><p class="viewer-caption t-label"></p>'
            f'<button class="viewer-close btn-bare" type="button" autofocus><span>Close</span> {icon("close")}</button></div>'
            '<div class="viewer-stage"><img class="viewer-img is-front" alt="" width="2" height="3">'
            '<img class="viewer-img is-back" alt="" aria-hidden="true" width="2" height="3"></div>'
            f'<button class="viewer-prev btn-bare" type="button" aria-label="Previous photo">{icon("chev-l")}</button>'
            f'<button class="viewer-next btn-bare" type="button" aria-label="Next photo">{icon("chev-r")}</button>'
            '<div class="viewer-foot"><span class="viewer-progress" aria-hidden="true"></span>'
            '<p class="viewer-count t-count" aria-hidden="true"><span class="wheel"><span>0</span></span>'
            f'<span class="wheel"><span>1</span></span> / <span class="viewer-total">{total:02d}</span></p></div>'
            '<p class="sr-only viewer-live" aria-live="polite"></p></dialog>\n')


def investment():
    """Investment (spec §5.3): split hero, index bar, a photo row per session with a photo (the wedding packages straight
    after Weddings), the carte for sessions still without one, How it works, Questions, the closing invitation."""
    pictured = [s for s in SESSIONS if exists(PHOTOS[s['photo']][0])]
    worded = [s for s in SESSIONS if s not in pictured]
    parts = [inv_hero(), index_bar('Sessions', [(['weddings', 'wedding-packages'] if s['id'] == 'weddings' else [s['id']],
                                                 s.get('short', s['name']), None) for s in pictured + worded])]
    for i, s in enumerate(pictured):
        parts.append(session_row(s, mirror=i % 2 == 1))
        if s['id'] == 'weddings':
            parts.append(wedding_packages())
    if worded:
        parts.append(carte(worded))
    if 'weddings' not in [s['id'] for s in pictured]:
        parts.append(wedding_packages())
    parts += [kind_words('investment'), how_it_works(), questions(), closing('investment')]
    return page('investment', 'investment.html', 'Investment | Selah Stories',
                'Wedding, couples and engagement, family, maternity and newborn photography sessions in Adelaide: prices and what each includes.',
                '\n\n'.join(p for p in parts if p), lcp=(INVESTMENT_HERO, 'inv-hero'))


def inv_hero():
    """Split hero (§4.14): the words on the left, one photo bleeding to the right edge; on phones the photo comes first."""
    lead, *rest = INVESTMENT_INTRO
    return (f'<section class="inv-hero sec--flush" aria-labelledby="investment-title">'
            f'{fig(INVESTMENT_HERO, "inv-hero", cls="inv-hero-photo", fill=True, priority=True)}'
            f'<div class="inv-hero-text wrap"><p class="eyebrow">Investment</p>'
            f'<h1 id="investment-title">{lines("Photos you’ll/keep|*for good.*")}</h1>'
            f'<p class="lead">{e(lead)}</p>{"".join(f"<p>{e(p)}</p>" for p in rest)}</div></section>')


def spec_sheet(s):
    """Every include as a labelled row, in her order, then the price row, or "Pricing on enquiry" in the same slot."""
    rows = s['includes']
    price = f'<dd class="t-price">{e(s["price"])}</dd>' if s.get('price') else '<dd class="spec-ask">Pricing on enquiry</dd>'
    return (f'<dl class="spec" data-rules>'
            + ''.join(f'<div style="--i:{i}"><dt>{e(SPEC_LABELS[x])}</dt><dd>{e(x)}</dd></div>' for i, x in enumerate(rows))
            + f'<div class="spec-price" style="--i:{len(rows)}"><dt>Investment</dt>{price}</div></dl>')


def session_text(s):
    """Her paragraphs, the spec sheet and the session's one action (its `more` link, or an enquiry)."""
    if s.get('more'):
        action = link_arrow(*s['more'])
    else:
        action = link_arrow(f'contact.html?session={quote_plus(FORM_SESSION[s["id"]])}',
                            f'Enquire about {s.get("short", s["name"]).lower()}')
    body = ''.join(f'<p>{e(p)}</p>' for p in s['body'])
    return f'<div class="session-body">{body}</div>{spec_sheet(s)}<div class="session-action">{action}</div>'


def old_anchor(sid):
    """Empty targets for the old sessions.html ids of this session, inside its heading (no box, so no layout)."""
    return ''.join(f'<span id="{old}"></span>' for old, new in OLD_ANCHORS.items() if new == sid)


def session_row(s, mirror=False):
    """A session with its photo: photo in cols 1-6 and words in 8-12 (mirrored on alternate rows); on phones the photo
    runs full-bleed above the words."""
    sid = s['id']
    return (f'<article class="session sec--standard{" session--mirror" if mirror else ""}" id="{sid}" aria-labelledby="{sid}-title">'
            f'<div class="wrap grid-12">{fig(s["photo"], "session", cls="session-photo", ratio="4/5")}'
            f'<div class="session-text"><h2 id="{sid}-title">{old_anchor(sid)}{e(s["name"])}</h2>{session_text(s)}</div></div></article>')


def carte(sessions):
    """Sessions whose photo has not arrived yet: one ruled row each, the name set large, under an eyebrow built from
    the names. No section head, so it never repeats a neighbour's."""
    names = [s.get('short', s['name']) for s in sessions]
    label = (', '.join(names[:-1]) + ' & ' + names[-1]) if len(names) > 1 else names[0]
    rows = ''.join(f'<article class="session session--word" id="{s["id"]}" aria-labelledby="{s["id"]}-title">'
                   f'<h2 class="t-word" id="{s["id"]}-title">{old_anchor(s["id"])}{e(s.get("short", s["name"]))}</h2>'
                   f'<div class="session-text">{session_text(s)}</div></article>' for s in sessions)
    return (f'<section class="carte sec--standard" aria-labelledby="carte-label"><div class="wrap">'
            f'<p class="eyebrow" id="carte-label">{e(label[0] + label[1:].lower())}</p>{rows}</div></section>')


def wedding_packages():
    """The five packages (§4.15): arch-topped cards from 861px, arch rows below; the hours of light (M08) in each dome.
    No package is marked: nothing says one is preferred."""
    longest = max(h for _, h, _ in WEDDING_PACKAGES)
    tiers = ''.join(f'<li class="tier" data-hours="{h}" style="--i:{i}"><div class="tier-sky">{art.tier_arc(h, longest)}</div>'
                    f'<h3 class="tier-name">{e(name)}</h3><p class="tier-hours t-caption">Up to {h} hours</p>'
                    f'<p class="tier-price t-price">{e(price)}</p></li>' for i, (name, h, price) in enumerate(WEDDING_PACKAGES))
    notes = ''.join(f'<div><h3>{title}</h3><ul role="list">{"".join(f"<li>{e(x)}</li>" for x in items)}</ul></div>'
                    for title, items in (('Every package includes', WEDDING_INCLUDES), ('Good to know', WEDDING_TERMS)))
    return (f'<section class="packages sec--band" id="wedding-packages" aria-labelledby="wedding-packages-title"><div class="wrap">'
            f'<div class="head--split"><h2 id="wedding-packages-title">Wedding <em>packages</em></h2>'
            f'<p class="lead">The packages differ only in hours. Everything else is the same in every one.</p></div>'
            f'<ol class="tiers" role="list" data-rules style="--i:{len(WEDDING_PACKAGES)}">{tiers}</ol>'
            f'<div class="tier-notes">{notes}</div><div class="actions">{button("contact.html?session=" + quote_plus(FORM_SESSION["weddings"]), "Check my wedding dates")}</div></div></section>')


def how_it_works():
    """The steps as a ledger on a thread, each marked by a sun warming from morning to golden hour (§4.16)."""
    steps = ''.join(f'<li class="step" style="--i:{i}"><span class="step-marker">{art.step_sun(i + 1, len(STEPS))}</span>'
                    f'<h3>{e(t)}</h3><p>{e(d)}</p></li>'
                    for i, (t, d) in enumerate(STEPS))
    return (f'<section class="how sec--standard head--left" aria-labelledby="how-title"><div class="wrap">'
            f'<h2 id="how-title">How it <em>works</em></h2><ol class="steps" role="list" data-rules>{steps}</ol></div></section>')


def questions():
    """FAQ (§4.17): native details (never name="", so a tapped row never jumps), the plus turning to a minus."""
    ig_url = INSTAGRAM[1]
    qa = ''.join(f'<details class="qa" style="--i:{i}"><summary><span class="qa-row"><span class="t-question">{e(q)}</span>'
                 f'{icon("plus")}</span></summary><div class="qa-body"><p>{e(a)}</p></div></details>' for i, (q, a) in enumerate(FAQ))
    return (f'<section class="questions sec--standard" aria-labelledby="faq-title"><div class="wrap head--split">'
            f'<div class="faq-head"><h2 id="faq-title">Questions, <em>answered</em></h2>'
            f'<p>Still wondering? Message me on <a href="{ig_url}" rel="me">Instagram</a>.</p></div>'
            f'<div class="faq" data-rules style="--i:{len(FAQ)}">{qa}</div></div></section>')


def kind_words_page():
    """Kind words: real reviews as stories (spec §5.4), or, until there are some, the honest holding state (§5.5): her
    photo, the page's promise in plain words and the newest sessions on Instagram. Kept out of search meanwhile."""
    ig_name, ig_url = INSTAGRAM
    title, desc = 'Kind words | Selah Stories', 'What couples and families say about their sessions with Selah Stories, Adelaide photographer.'
    h1 = lines('From the people//*in the photos.*')
    if KIND_WORDS_ARE_PLACEHOLDERS or not KIND_WORDS:   # the link preview promises no reviews either
        desc = 'Where couples and families share how their sessions felt with Selah Stories, Adelaide photographer.'
        main = f'''<section class="page-head kw-holding sec--compact head--center"><div class="wrap">
{arch_frame(KIND_WORDS_HOLDING_PHOTO, "kw-holding", "3x4", priority=True)}
<p class="eyebrow">Kind words</p><h1>{h1}</h1>
<p class="lead">This is where couples and families share how their sessions felt.<br class="br-md"> The newest sessions go up on Instagram first.</p>
<div class="actions">{link_arrow(ig_url, "See the newest sessions on Instagram", external=True)}</div>
</div></section>

{instagram_sheet("limestone")}

{closing("kind-words")}'''
        return page('kind-words', 'kind-words.html', title, desc, main, robots='noindex')
    stories = ''.join(kw_story(n, r) for n, r in enumerate(KIND_WORDS, 1))
    main = f'''{page_head("Kind words", h1, "A few words from the couples and families I’ve photographed.", layout="left")}

<section class="stories sec--standard"><div class="wrap">{stories}</div></section>

{closing("kind-words")}'''
    return page('kind-words', 'kind-words.html', title, desc, main)


def kw_story(n, r):
    """One review (spec §4.13): its number, the photo only when it is of the people who wrote it, the pull line (a
    repeat, so hidden from screen readers), the review as written, and who wrote it. Photos alternate sides."""
    assert not r['photo'] or r['photo_is_theirs'], f'a photo may only sit beside the review of the people in it ({r["names"]})'
    photo = arch_frame(r['photo'], 'cover', '4x5', cls='story-photo') if r['photo'] and r['photo_is_theirs'] else ''
    side = (' story--photo' + (' story--flip' if n % 2 == 0 else '')) if photo else ''
    pull = f'<p class="t-quote story-pull" aria-hidden="true"><em>{e(r["pull"])}</em></p>' if r['pull'] else ''
    return (f'<article class="story{side}" id="review-{n}">{photo}<div class="story-text">'
            f'<p class="eyebrow--num"><span class="t-count">No. {n:02d}</span></p>{pull}<figure><blockquote>'
            f'<p class="t-quote-body">“{review_words(r)}”</p></blockquote><figcaption class="cite">{review_cite(r)}</figcaption>'
            f'</figure></div></article>')


def contact():
    """Contact (spec §5.6, §4.18): the head and the enquiry in one column, her photo and the details beside them. The
    form posts to FormSubmit, which emails each enquiry to Charne (content.py, FORM_TO). Without JavaScript it is a plain
    post to FORM_ACTION; with it, 60-form.js sends labelled JSON to ENDPOINT. The hidden _subject and _template fields
    shape the no-JS email, and _honey is FormSubmit's own bot trap."""
    ig_name, ig_url = INSTAGRAM
    # the summary's links, one per required field, shown by 60-form.js for the fields that need a look (spec §4.18)
    summary = ''.join(f'<li data-n="{n}" hidden><a href="#{t}"></a></li>' for n, t in
                      (('name', 'name'), ('email', 'email'), ('session', 'session-0'), ('message', 'message')))
    main = f'''<section class="contact sec--standard" aria-labelledby="contact-title"><div class="wrap grid-12">
<div class="contact-main">
<p class="eyebrow">Contact</p>
<h1 id="contact-title">{lines('Let’s plan//*something lovely.*')}</h1>
<p class="lead">Tell me a little about what you’re planning. I’ll get back to you with availability and pricing.</p>
<div class="enquire-slot">
<form id="enquiry-form" class="form" method="post" action="{FORM_ACTION}" data-endpoint="{ENDPOINT}">
<input type="hidden" name="_subject" value="New enquiry from the Selah Stories website"><input type="hidden" name="_template" value="table">
<div id="form-summary" class="form-summary" role="group" aria-labelledby="form-summary-title" tabindex="-1" data-n="One thing,Two things,Three things,Four things" hidden><h2 id="form-summary-title" class="t-question">Things to check</h2><ul>{summary}</ul></div>
<fieldset class="fs"><legend class="t-question">About you</legend>
{form_field("name", "Your name", 'autocomplete="name" autocapitalize="words" required maxlength="200"', err="Add your name so I know who I’m writing to.")}
<div class="fields">{form_field("email", "Email", 'type="email" autocomplete="email" required maxlength="254"', err="Add your email so I can reply.", bad="That email doesn’t look quite right.")}
{form_field("phone", "Phone", 'type="tel" autocomplete="tel" maxlength="40"', hint="(optional)")}</div>
</fieldset>
<fieldset class="fs"><legend class="t-question">What are we celebrating?</legend>
<div class="chips">{form_chips("session", FORM_OPTIONS, required=True)}</div>
{form_error("session", "Choose the kind of session.")}
</fieldset>
<fieldset class="fs"><legend class="t-question">When and where?</legend>
<div class="fields">{form_field("date", "Date or season", 'placeholder="e.g. March 2027" maxlength="120"', hint="(rough is fine)")}
{form_field("location", "Where", 'autocapitalize="words" placeholder="Beach, hills, home or venue" maxlength="200"', hint="(optional)")}</div>
</fieldset>
<div class="fs field field--letter"><label class="legend t-question" for="message">Tell me about it</label>
<textarea id="message" name="message" required maxlength="4000" placeholder="Who’s involved, what you’re picturing, anything I should know" aria-describedby="err-message"></textarea>
{form_error("message", "Add a line or two about what you’re planning.")}
</div>
<fieldset class="fs"><legend class="t-question">How did you find me? <span class="t-caption">(optional)</span></legend>
<div class="chips">{form_chips("heard", ["Instagram", "A friend", "Google", "A wedding vendor", "Somewhere else"])}</div>
</fieldset>
<div class="hp sr-only" aria-hidden="true"><label for="company">Leave this empty</label><input id="company" name="_honey" tabindex="-1" autocomplete="off"></div>
<div class="form-foot"><button class="btn btn--primary btn--send" type="submit"><span>Send enquiry</span> <i class="btn-rule" aria-hidden="true"></i></button>
<div class="form-report"><p id="form-status" class="form-status t-caption" aria-hidden="true">Sending…</p>
<div id="form-error" class="form-error" role="group" aria-labelledby="form-error-text" tabindex="-1" hidden><p id="form-error-text" class="t-small">Your enquiry didn’t send. Your details are still here, so please try again, or message me on Instagram at <a href="{ig_url}">{e(ig_name)}</a>.</p></div></div>
</div>
</form>
<section id="form-success" class="form-success head--center" aria-labelledby="success-title" hidden>{mark("success", "lg")}
<p class="eyebrow">Sent</p><h2 id="success-title" class="success-title" tabindex="-1">Thank you.</h2>
<p>Your enquiry is on its way. I’ll be in touch soon with dates and details.</p>
<div class="actions">{link_arrow("gallery.html", "Browse the gallery")}{link_arrow(ig_url, "Instagram", external=True)}</div>
</section>
</div>
<p id="form-live" class="sr-only" role="status"></p>
</div>
<div class="contact-aside">
{arch_frame(CONTACT_PHOTO, "contact", "3x4", keyline=True, high=True)}
<dl class="details" data-rules>
<div style="--i:0"><dt>What happens next</dt><dd class="t-small">I’ll reply with available dates, pricing and a few ideas for your session.</dd></div>
<div style="--i:1"><dt>Instagram</dt><dd>{link_arrow(ig_url, ig_name, external=True)}</dd></div>
<div style="--i:2"><dt>Based in</dt><dd class="t-small">Adelaide, South Australia.<p class="t-caption">Sessions on the coast, in the hills and at home.</p></dd></div>
</dl>
</div>
</div></section>'''
    return page('contact', 'contact.html', 'Contact | Selah Stories',   # the details beside the form are body text
                'Check dates for wedding, couples, family, maternity and newborn photography in Adelaide.', main,
                fonts=('proza-libre-400',))


def form_error(name, message, bad=''):
    """A required field's error slot: always there (one line reserved, so a message never moves anything), linked by
    aria-describedby, filled by 60-form.js from its data-m (empty) and data-bad (malformed) messages."""
    bad = f' data-bad="{e(bad)}"' if bad else ''
    return f'<p class="field-error t-caption" id="err-{name}" data-m="{e(message)}"{bad}>{icon("alert")}<span></span></p>'


def form_field(name, label, attrs, *, hint='', err='', bad=''):
    """A text field: label (with its hint), input, then the error slot; an optional field keeps an empty slot too, so
    every field has the same rhythm."""
    hint = f' <span class="t-caption">{e(hint)}</span>' if hint else ''
    described = f' aria-describedby="err-{name}"' if err else ''
    slot = form_error(name, err, bad) if err else '<p class="field-error t-caption"></p>'
    return (f'<div class="field"><label for="{name}">{e(label)}{hint}</label><input id="{name}" name="{name}" {attrs}{described}>'
            f'{slot}</div>')


def form_chips(name, options, *, required=False):
    """Radio chips: each input lies over its chip, so the chip is the control (one swipe, one focus box)."""
    extra = f' required aria-describedby="err-{name}"' if required else ''
    return ''.join(f'<label class="chip"><input class="chip-input" type="radio" name="{name}" id="{name}-{i}" value="{e(o)}"{extra}>'
                   f'<span class="chip-face">{e(o)}</span></label>' for i, o in enumerate(options))


def privacy():
    ig_name, ig_url = INSTAGRAM
    main = f'''{page_head("Your details", "Privacy")}
<section class="text-page sec--standard"><div class="wrap"><div class="text">
<p>This page explains what happens to the details you share through this website.</p>
<h2 class="h2--sm">What I collect</h2><p>When you send an enquiry, I receive the details you type into the form: your name, email, and anything else you choose to include, such as a phone number, date or message. The form is delivered to my email by FormSubmit (formsubmit.co), a service that turns website forms into emails.</p>
<h2 class="h2--sm">How I use it</h2><p>Only to reply to your enquiry and, if you book, to plan your session. I don’t sell or share your details for marketing.</p>
<h2 class="h2--sm">Photos</h2><p>Some session photos appear on this website and on Instagram. If you’d like a photo of you removed, just ask and I’ll take it down.</p>
<h2 class="h2--sm">Questions or changes</h2><p>To see, correct or delete the details you’ve sent, message me on Instagram at <a href="{ig_url}">{e(ig_name)}</a>.</p>
</div></div></section>'''
    return page('privacy', '', 'Privacy | Selah Stories', 'How Selah Stories handles the details you share.', main,
                fonts=('proza-libre-400',))   # the first view is body text


def not_found():
    # The footer scene stays at golden hour here (never scroll-linked); the dusk plays in this mark instead (M03).
    main = f'''<section class="nf sec--breath head--center"><div class="wrap">
{mark("nf", "xl")}
<p class="eyebrow">Page not found</p><h1>{lines('This page has//*wandered off.*')}</h1>
<p class="lead">It may have moved, or the link may be old.</p>
<div class="actions nf-actions">{button("index.html", "Back home", cls="nf-home")}{link_arrow("gallery.html", "See the gallery")}</div>
</div></section>'''
    return page('404', '', 'Page not found | Selah Stories', 'This page could not be found.', main)


PAGES = {'index.html': index, 'gallery.html': gallery, 'investment.html': investment, 'kind-words.html': kind_words_page,
         'contact.html': contact, 'privacy.html': privacy, '404.html': not_found}
RETIRED = ['portfolio.html', 'sessions.html', 'about.html', 'enquire.html']  # replaced by the pages above


# ------------------------------------------------------------------ checks (UI spec §6.5, build plan §4.1)
KB = 1024
WP0_CSS = ['00-base', '10-buttons', '20-header-menu', '30-photos-windows', '50-instagram', '55-page-head', '85-text',
           '90-footer', '95-hover', '97-motion', '99-calm']
WP0_JS = ['00-kernel', '05-moments', '10-menu', '15-header', '20-photos', '25-index', '70-year-golden-hour', '99-end']
# Bytes, unminified, comments included; each package is held to its own slice (plan §8). The slices served the parallel
# build; fix round 2 rebalanced them within the unchanged totals (CSS: WP0 38 → 37.6875KB, WP2 6.5 → 7.25KB, WP4
# contact 5 → 5.0625KB, WP4 kind words 2 → 1.5KB; JS: WP0 18 → 18.5KB, WP2 7 → 7.25KB, WP1 1 → .75KB, WP3 1 → .5KB),
# and the type change moved 128 bytes of CSS to WP3 (tabular prices on phones, the hero h1 cap): 64 from WP4 contact,
# 32 each from WP1 and WP4 kind words (WP3 7.625KB, WP4 contact 5KB, WP1 4.96875KB, WP4 kind words 1.46875KB); its
# review fixes moved 96 more from WP0, freed by tighter commas there: 64 to WP3 (narrow-phone tier rows, the spec-term
# measure), 32 to WP4 contact (the legend's '(optional)'), so WP0 37.59375KB, WP3 7.6875KB, WP4 contact 5.03125KB.
PART_BUDGET = {
    'css': {'WP0': (WP0_CSS, 37.59375 * KB), 'WP1': (['40-home'], 4.96875 * KB), 'WP2': (['60-gallery-viewer'], 7.25 * KB),
            'WP3': (['70-investment'], 7.6875 * KB), 'WP4 contact': (['80-contact'], 5.03125 * KB),
            'WP4 kind words': (['45-kind-words'], 1.46875 * KB)},
    'js': {'WP0': (WP0_JS, 18.5 * KB), 'WP1': (['32-home'], .5 * KB), 'WP2': (['50-viewer'], 7.25 * KB),
           'WP3': (['36-investment'], .375 * KB), 'WP4': (['60-form', '40-session-prefill'], 5.375 * KB)},
}
assert all(sum(limit for _, limit in PART_BUDGET[k].values()) <= {'css': 64, 'js': 32}[k] * KB for k in PART_BUDGET)
TOTAL_BUDGET = {'css': 64 * KB, 'js': 32 * KB}
HEAD_SCRIPT_BUDGET = 1.25 * KB
SVG_BUDGET = (20_000, 3_000)   # inline SVG per page: raw, gzipped
BREAKPOINTS = {399, 400, 599, 600, 860, 861, 1099, 1100, 1439, 1440}
BANNED = ('placeholder.svg', 'ph--empty', '<use', '<symbol', 'icon-sprite', 'sprig', 'mark-ellipse', 'mark-swash',
          'mark-underline', 'sc-quote', 'mark-quote', '<base')
HONESTY = re.compile(r'will go here|placeholder|names’?\b|Send three to six|coming soon', re.I)
PRELOADED = ('index.html', 'investment.html')   # the pages whose LCP photo is preloaded (spec §7.6)
HOVER_GATE = re.compile(r'@media\s*\(hover:\s*hover\)\s*and\s*\(pointer:\s*fine\)')
SVG_TAG = '<' + 'svg'   # spelled out so this file holds no SVG markup


def parts(ext):
    return sorted(glob.glob(os.path.join(HERE, ext, f'*.{ext}')))


def visible_text(page_html):
    s = re.sub(r'<(script|style)\b.*?</\1>', ' ', page_html, flags=re.S | re.I)
    return html.unescape(re.sub(r'<[^>]+>', ' ', s))


def squash(s):
    return re.sub(r' ([,.;:!?)])', r'\1', re.sub(r'\s+', ' ', s).strip())


class Names(HTMLParser):
    """The text of every heading, button, link, label and legend, read twice: tags dropped, and tags as spaces. The
    two must match, or a name has lost a space (a line break with no space after it, say)."""
    TAGS = {'h1', 'h2', 'h3', 'button', 'a', 'label', 'legend'}
    VOID = {'br', 'img', 'input', 'source', 'meta', 'link', 'hr', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.open, self.found, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        for el in self.open:
            el[2].append(' ')
        if tag in self.TAGS:
            self.open.append([tag, [], []])

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1
        for el in self.open:
            el[2].append(' ')
        if self.open and self.open[-1][0] == tag:
            t, a, b = self.open.pop()
            self.found.append((t, ''.join(a), ''.join(b)))

    def handle_data(self, data):
        if not self.skip:
            for el in self.open:
                el[1].append(data)
                el[2].append(data)


def css_rules(text):
    """(enclosing at-rule preludes, selector) for every style rule in a stylesheet."""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    stack, start = [], 0
    for i, ch in enumerate(text):
        if ch == '{':
            prelude = text[start:i].strip()
            if not prelude.startswith('@'):
                yield list(stack), prelude
            stack.append(prelude)
            start = i + 1
        elif ch == '}':
            if stack:
                stack.pop()
            start = i + 1
        elif ch == ';':
            start = i + 1


def bad_query(q):
    """Why a media query breaks the breakpoint set (spec §2.5, D23), or None."""
    if re.search(r'(?:width|height)\s*(?::|[<>]=?)\s*[\d.]+(?:em|rem|vw|vh)\b', q):
        return 'breakpoints are px'
    for value in re.findall(r'(?:(?:min|max)-width\s*:|\bwidth\s*[<>]=?)\s*([\d.]+)px', q):
        if float(value) not in BREAKPOINTS:
            return f'{value}px is not a breakpoint ({", ".join(map(str, sorted(BREAKPOINTS)))})'
    if 'height' in q and not re.fullmatch(r'\s*\(max-width:\s*860px\)\s*and\s*\(max-height:\s*500px\)\s*', q):
        return 'the only height query is (max-width: 860px) and (max-height: 500px)'
    return None


def check_js(fail):
    """The scripts' media queries use the same breakpoints as the CSS."""
    for path in parts('js'):
        bare = re.sub(r'//[^\n]*|/\*.*?\*/', '', open(path, encoding='utf-8').read(), flags=re.S)
        for q in re.findall(r'["\'](\([^"\']*(?:width|height)[^"\']*\))["\']', bare):
            problem = bad_query(q)
            if problem:
                fail(f'{os.path.basename(path)}: "{q}": {problem}')


def check_css(fail):
    sizes = {}
    for path in parts('css'):
        name = os.path.basename(path)[:-4]
        text = open(path, encoding='utf-8').read()
        sizes[name] = len(text.encode())
        bare = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
        for q in re.findall(r'@media([^{]*)\{', bare):
            problem = bad_query(q)
            if problem:
                fail(f'{name}.css: @media{q.rstrip()}: {problem}')
        for outer, sel in css_rules(text):
            if ':hover' in sel and not any(HOVER_GATE.search(p) for p in outer):
                fail(f'{name}.css: ":hover" outside @media (hover: hover) and (pointer: fine): {sel[:80]}')
        if re.search(r'\b(will-change|backdrop-filter)\s*:', bare):
            fail(f'{name}.css: will-change and backdrop-filter are not used')
    return sizes


def check_budgets(fail, css_sizes):
    js_sizes = {os.path.basename(p)[:-3]: len(open(p, encoding='utf-8').read().encode()) for p in parts('js')}
    report = []
    for kind, sizes in (('css', css_sizes), ('js', js_sizes)):
        total = sum(sizes.values())
        report.append(f'{kind.upper()} {total / KB:.1f}KB of {TOTAL_BUDGET[kind] / KB:.0f}KB')
        if total > TOTAL_BUDGET[kind]:
            fail(f'{kind}: {total} bytes, over the {TOTAL_BUDGET[kind]} byte total')
        for pkg, (names, limit) in PART_BUDGET[kind].items():
            used = sum(sizes.get(n, 0) for n in names)
            report.append(f'  {pkg} {used / KB:.1f}/{limit / KB:.1f}KB')
            if used > limit:
                fail(f'{kind} {pkg}: {used} bytes, over its {int(limit)} byte slice')
    print('sizes: ' + ' · '.join(f'{n} {s / KB:.1f}' for n, s in {**css_sizes, **js_sizes}.items()))
    print('budgets: ' + ' | '.join(report))


def check_page(fail, name, page_html):
    text = visible_text(page_html)
    m = HONESTY.search(text)
    if m:
        fail(f'{name}: "{m.group(0)}" in the visible text')
    for marker in BANNED:
        if marker in page_html:
            fail(f'{name}: "{marker}" in the page')
    svgs = ''.join(re.findall(SVG_TAG + r'\b.*?</svg>', page_html, flags=re.S)).encode()
    if len(svgs) > SVG_BUDGET[0] or len(gzip.compress(svgs, mtime=0)) > SVG_BUDGET[1]:
        fail(f'{name}: inline SVG {len(svgs)} bytes ({len(gzip.compress(svgs, mtime=0))} gzipped), over {SVG_BUDGET}')
    names = Names()
    names.feed(page_html)
    for tag, a, b in names.found:
        if squash(a) != squash(b):
            fail(f'{name}: the accessible name of a <{tag}> loses a space: "{squash(a)}" / "{squash(b)}"')
    # The LCP photo (spec §7.6): at most one per page, never lazy, never developed (M10), high priority; the image
    # preload only on Home and Investment, built from the same srcset and SIZES entry as its <source>.
    preload = re.search(r'<link rel="preload" as="image"[^>]*imagesrcset="([^"]*)" imagesizes="([^"]*)"', page_html)
    lcp = re.search(r'<source type="image/webp" srcset="([^"]*)" sizes="([^"]*)"><img [^>]*data-lcp', page_html)
    if preload and (not lcp or preload.groups() != lcp.groups()):
        fail(f'{name}: the image preload does not match the LCP photo\'s <source>')
    if bool(preload) != (name in PRELOADED):
        fail(f'{name}: an image preload belongs on {" and ".join(PRELOADED)} only (spec §7.6)')
    lcp_imgs = re.findall(r'<img [^>]*\bdata-lcp\b[^>]*>', page_html)
    if len(lcp_imgs) > 1:
        fail(f'{name}: {len(lcp_imgs)} LCP photos (data-lcp)')
    for img in lcp_imgs:
        if 'loading=' in img or 'fetchpriority="high"' not in img:
            fail(f'{name}: the LCP photo must be eager with fetchpriority="high": {img[:120]}')
    if re.search(r'class="[^"]*\bph--tray\b[^"]*"[^>]*><picture>(?:<source[^>]*>)?<img [^>]*data-lcp', page_html):
        fail(f'{name}: the LCP photo is never developed (.ph--tray)')
    for img in re.findall(r'<img\b[^>]*>', page_html):   # every photo reserves its box (CLS 0)
        if not re.search(r'\swidth="\d+"', img) or not re.search(r'\sheight="\d+"', img):
            fail(f'{name}: an <img> without width and height: {img[:120]}')
    if page_html.count('<h1') != 1:
        fail(f'{name}: {page_html.count("<h1")} h1 elements')
    if '<main id="main" tabindex="-1">' not in page_html or ' data-page="' not in page_html:
        fail(f'{name}: main#main[tabindex=-1] and data-page are required')
    ids = re.findall(r'\sid="([^"]+)"', page_html)
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        fail(f'{name}: id="{dup}" is used more than once')
    refs = re.findall(r'\shref="#([^"]+)"', page_html) + [
        r for v in re.findall(r'\saria-(?:labelledby|describedby|controls)="([^"]+)"', page_html) for r in v.split()]
    for ref in sorted(set(refs) - set(ids)):
        fail(f'{name}: "#{ref}" points at nothing on the page')
    # Placeholder-review policy (spec §6.1): no review markup at all until real reviews exist; the holding page is
    # kept out of search, and nothing else is.
    if KIND_WORDS_ARE_PLACEHOLDERS or not KIND_WORDS:
        for marker in ('<blockquote', 'class="interlude', 'class="story', 'class="review', 'class="cite'):
            if marker in page_html:
                fail(f'{name}: review markup ({marker}) while the reviews are placeholders')
    if ('noindex' in page_html) != (name == 'kind-words.html' and (KIND_WORDS_ARE_PLACEHOLDERS or not KIND_WORDS)):
        fail(f'{name}: noindex belongs on the Kind words holding page only')
    if name == '404.html':
        for attr, url in re.findall(r'\s(href|src|content)="([^"]*)"', page_html):
            if (attr != 'content' or url.startswith('images/')) and not re.match(r'/|#|https?:|mailto:', url):
                fail(f'404.html: {attr}="{url}" is not root-absolute')
    if name == 'investment.html':   # her prices, packages and terms reach the page exactly (spec §6.5)
        must = ([s['price'] for s in SESSIONS if s.get('price')] + [p for _, _, p in WEDDING_PACKAGES]
                + [n for n, _, _ in WEDDING_PACKAGES] + WEDDING_INCLUDES + WEDDING_TERMS)
        for text in must:
            if e(text) not in page_html:
                fail(f'investment.html: "{text}" is missing (prices, packages and terms are copied byte for byte)')
        hours = re.findall(r'<p class="tier-hours\b[^"]*">([^<]*)</p>', page_html)   # coverage hours are contract terms
        if hours != [f'Up to {h} hours' for _, h, _ in WEDDING_PACKAGES]:
            fail(f'investment.html: the tier hours read {hours}; her package sheet says "Up to N hours"')


def check_fonts(fail, pages, out):
    """Self-hosted OFL faces only: every @font-face file exists and every font file is used, each family ships its
    licence (fonts/OFL-<Family>.txt) and no licence outlives its family, every other url() in the built CSS exists
    (the wordmark mask), each page preloads Brygada roman first and at most FONT_PRELOADS faces, all of them in use, and
    each page preloads the wordmark the CSS masks with."""
    css = re.sub(r'/\*.*?\*/', '', ''.join(open(p, encoding='utf-8').read() for p in parts('css')), flags=re.S)
    faces = re.findall(r'@font-face\{font-family:"([^"]+)";[^}]*?src:url\("fonts/([^"]+)"\)', css)
    used, have = {f for _, f in faces}, set(os.listdir(os.path.join(ROOT, 'fonts')))
    for f in sorted(used - have):
        fail(f'styles.css: fonts/{f} does not exist')
    for f in sorted(x for x in have if x.endswith('.woff2') and x not in used):
        fail(f'fonts/{f} is not used by any @font-face: remove it')
    families, licences = {fam.replace(' ', '') for fam, _ in faces}, {x[4:-4] for x in have if x.startswith('OFL-')}
    for fam in sorted(families - licences):
        fail(f'fonts/OFL-{fam}.txt is missing: every self-hosted family ships its licence')
    for fam in sorted(licences - families):
        fail(f'fonts/OFL-{fam}.txt belongs to a family nothing uses: remove it')
    built = re.sub(r'/\*.*?\*/', '', open(os.path.join(out, 'styles.css'), encoding='utf-8').read(), flags=re.S)
    for url in re.findall(r'url\("?([^")]+)"?\)', built):
        if not url.startswith(('data:', 'fonts/')) and not os.path.isfile(os.path.join(out, url)):
            fail(f'styles.css: url({url}) does not exist')
    if f'url({WORDMARK})' not in built:
        fail(f'styles.css: the name is not masked with {WORDMARK}')
    for name, page_html in pages.items():
        pre = re.findall(r'<link rel="preload" href="/?fonts/([^"]+)" as="font"', page_html)
        if not pre or pre[0] != 'brygada-1918-400-700.woff2' or len(pre) > FONT_PRELOADS or set(pre) - used:
            fail(f'{name}: font preloads {pre}: Brygada roman first, at most {FONT_PRELOADS}, each one in use')
        if WORDMARK_PRELOAD.replace('href="', 'href="/' if name == '404.html' else 'href="') not in page_html:
            fail(f'{name}: no preload for {WORDMARK} (the name paints nothing until it arrives)')


def verify(pages, out):
    errors = []
    fail = errors.append
    css_sizes = check_css(fail)
    check_fonts(fail, pages, out)
    check_js(fail)
    check_budgets(fail, css_sizes)
    if len(HEAD_SCRIPT.encode()) > HEAD_SCRIPT_BUDGET:
        fail(f'head script: {len(HEAD_SCRIPT.encode())} bytes, over {HEAD_SCRIPT_BUDGET:.0f}')
    for name, page_html in pages.items():
        check_page(fail, name, page_html)
    for k in PHOTOS:   # the rhythm grid reads orientation from content.py: it must match the files
        path = PHOTOS[k][0]
        if exists(path):
            w, h = size_of(path, PHOTOS[k][1:3])
            if (w > h) != landscape(k):
                fail(f'{k}: content.py says {"landscape" if landscape(k) else "portrait"}, the file says otherwise')
            stem = os.path.join(ROOT, path.rsplit('.', 1)[0])   # a copy is never heavier than the full file it stands in for
            for v in WIDTHS:
                if v < w and os.path.isfile(f'{stem}-{v}.webp') and os.path.isfile(f'{stem}.webp') and \
                        os.path.getsize(f'{stem}-{v}.webp') >= os.path.getsize(f'{stem}.webp'):
                    fail(f'{k}: the {v}px WebP copy is not lighter than the full-size one (tools/prepare_photos.py qualities)')
    for where in {out, ROOT}:
        if os.path.exists(os.path.join(where, 'images', 'placeholder.svg')):
            fail(f'{where}/images/placeholder.svg exists: placeholder art is retired (spec §6.2)')
    for ext in ('css', 'js'):
        for path in parts(ext):
            text = open(path, encoding='utf-8').read()
            for marker in ('placeholder.svg', 'ph--empty', 'icon-sprite'):
                if marker in text:
                    fail(f'{os.path.basename(path)}: "{marker}" is retired (spec §6.2, §3)')
    source = open(__file__, encoding='utf-8').read()
    for old in ('art_icons', 'art_marks', 'art_scenes'):
        if old in sys.modules or os.path.exists(os.path.join(HERE, old + '.py')):
            fail(f'{old}.py must be gone and never imported (art.py is canonical)')
    if source.count(SVG_TAG) or source.count('<' + 'path') or source.count('<' + 'circle'):
        fail('build.py holds SVG markup: every SVG comes from art.py')
    return errors


# ------------------------------------------------------------------ build
def assemble(out):
    """Join the stylesheet and script parts into styles.css and main.js."""
    for ext, name, note in (('css', 'styles.css', '/* Selah Stories. Built from tools/site/css/ by tools/site/build.py: edit the parts there. */\n'),
                            ('js', 'main.js', '// Selah Stories. Built from tools/site/js/ by tools/site/build.py: edit the parts there.\n')):
        with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
            joined = ''.join(open(part, encoding='utf-8').read() for part in parts(ext))
            f.write(note + (joined.replace('url(wordmark.svg)', f'url({WORDMARK})') if ext == 'css' else joined))


def main(out=ROOT):
    os.makedirs(out, exist_ok=True)
    assemble(out)
    pages = {name: fn() for name, fn in PAGES.items()}
    for name, page_html in pages.items():
        with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
            f.write(page_html)
    for name in RETIRED:
        if os.path.exists(os.path.join(out, name)):
            os.remove(os.path.join(out, name))
    for name in glob.glob(os.path.join(out, 'wordmark*.svg')):   # an earlier wordmark
        if os.path.basename(name) != WORDMARK:
            os.remove(name)
    for name, svg in (('favicon.svg', art.FAVICON), (WORDMARK, art.wordmark_svg())):
        with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
            f.write(svg)
    print('built', ', '.join(PAGES), '->', out)
    errors = verify(pages, out)
    if KIND_WORDS_ARE_PLACEHOLDERS:
        print('Reminder: there are no real reviews yet. Add them to KIND_WORDS in tools/site/content.py before launch.')
    if errors:
        print('\nBUILD CHECKS FAILED:\n  ' + '\n  '.join(errors))
        sys.exit(1)
    print('checks passed')


if __name__ == '__main__':
    main(os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
