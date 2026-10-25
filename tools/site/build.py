# Builds the Sunday Light pages.
#
#   python3 tools/site/build.py           # writes into the repo root
#   python3 tools/site/build.py out_dir   # or somewhere else, for a look before replacing the real pages
#
# Writes the HTML pages, styles.css, main.js and favicon.svg, then checks them (verify(): the honesty net, the SVG and
# breakpoint rules, and the budgets); the build fails if a check does. styles.css and main.js are joined from the
# numbered parts in tools/site/css/ and tools/site/js/ (in file-name order), so edit the parts, not the joined files.
# Every SVG comes from art.py; this file holds none. A photo only appears once its file exists, so run this again
# after adding photos (tools/prepare_photos.py does that for you).
import glob, gzip, html, json, os, re, sys
from html.parser import HTMLParser
from urllib.parse import quote_plus

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import art  # noqa: E402
from art import icon, mark  # noqa: E402
# Everything the pages read from content.py (plan §4.3), imported once here so page packages never edit this line.
from content import (  # noqa: E402,F401
    PHOTOS, WEDDING_KEYS, FOCUS, PLACES, EXTRA_GALLERIES, INSTAGRAM, ENDPOINT, FORM_SESSION, FORM_OPTIONS,
    HERO, HERO_TITLE, HOME_WINDOWS, HOME_STATEMENT_PHOTO, HOME_TILE_PHOTO, STATEMENT_LINE, INTRO, INSTAGRAM_STRIP,
    CLOSING, CLOSING_LEAD, GALLERY_CHAPTERS, rhythm, rhythm_groups, landscape,
    SESSIONS, SESSION, SPEC_LABELS, LOCATION, GALLERY, INVESTMENT_HERO, INVESTMENT_INTRO, WEDDING_PACKAGES,
    WEDDING_INCLUDES, WEDDING_TERMS, STEPS, FAQ, min_price, CONTACT_PHOTO,
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
WIDTHS = (480, 800, 1000, 1200)   # WebP copies at these widths, plus the full-size file

# How wide each kind of photo shows, so phones load a small copy and large screens a big one. Photos that fill a
# screen-tall layer render two-thirds of the screen's height wide (66.7vh). Keys are API for the page packages.
SIZES = {
    'hero': f'{PHONE} max(100vw, 66.7vh), max(50vw, 66.7vh)',
    'window1': f'{PHONE} max(100vw, 66.7vh), 100vw',
    'window3': f'{PHONE} max(100vw, 66.7vh), max(34vw, 66.7vh)',
    'window2': f'{PHONE} max(100vw, 66.7vh), max(50vw, 66.7vh)',
    'inv-hero': f'{PHONE} 100vw, 50vw',
    'statement': f'{PHONE} 72vw, {WIDE} calc(30vw - 12px), 360px',
    'contact': f'{PHONE} 64vw, {WIDE} calc(30vw - 12px), 360px',
    'cover': f'{PHONE} 82vw, {WIDE} calc(38vw - 14px), 455px',
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


def _picture(path, w, h, alt, sizes, priority=False, eager=False):
    ss, sz = srcset(path, w), SIZES.get(sizes, sizes)
    source = f'<source type="image/webp" srcset="{ss}" sizes="{sz}">' if ss else ''
    load = ' fetchpriority="high" data-lcp' if priority else '' if eager else ' loading="lazy" decoding="async"'
    return f'<picture>{source}<img src="{path}" width="{w}" height="{h}" alt="{e(alt)}"{load}></picture>'


def picture(key, sizes, *, alt=None, priority=False, eager=False):
    """A photo: WebP copies for browsers that take them, the JPEG for the rest. `sizes` is a SIZES key or a literal.
    priority (the page's LCP photo): fetchpriority="high" and data-lcp, never lazy."""
    path, w, h, text, _ = PHOTOS[key]
    w, h = size_of(path, (w, h))
    return _picture(path, w, h, text if alt is None else alt, sizes, priority, eager)


def fig(key, sizes, *, cls='', ratio=None, tag='figure', fill=False, priority=False, eager=False, alt=None,
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
            f'{picture(key, sizes, alt=alt, priority=priority, eager=eager)}</{tag}>')


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
def page_head(eyebrow, title_html, lead_html='', *, layout='left', extra='', cls=''):
    lead = f'<p class="lead">{lead_html}</p>' if lead_html else ''
    return (f'<section class="page-head sec--compact head--{layout}{(" " + cls) if cls else ""}"><div class="wrap">'
            f'<p class="eyebrow">{e(eyebrow)}</p><h1>{title_html}</h1>{lead}{extra}</div></section>')


def index_bar(label, items):
    """The sticky index under the header (Gallery chapters, Investment sessions). items: [(ids, text, count|None)];
    the link goes to the first id, and the scroll-spy marks it current for any of them."""
    links = ''
    for ids, text, count in items:
        sup = (f'<sup><span class="sr-only">, </span>{count}<span class="sr-only"> photographs</span></sup>'
               if count is not None else '')
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
    return ''


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
            f'<div class="menu-foot"><a class="nav-instagram t-label" href="{ig_url}" rel="me">{icon("instagram")}'
            f'<span><span class="sr-only">Instagram </span>{e(ig_name)}</span>{icon("arrow-ne")}</a>'
            f'<span class="menu-place t-micro">Adelaide, South Australia</span></div></nav>'
            f'<a class="brand" href="index.html" aria-label="Sunday Light, home">{mark("h", "sm")}'
            f'<span class="brand-name">Sunday Light</span></a>'
            f'<a class="btn btn--sm btn--secondary header-cta" href="contact.html"{current("contact.html", active)}>Contact</a>'
            f'<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">'
            f'<span class="nav-toggle-label">Menu</span><span class="bars" aria-hidden="true"></span></button>'
            f'</div></header>\n')


def footer(active):
    ig_name, ig_url = INSTAGRAM
    nav = ''.join(f'<a href="{h}"{current(h, active)}>{t}{SUN if h == active else ""}</a>' for h, t in NAV)
    dot = '<span class="dot" aria-hidden="true"> · </span>'   # hidden on phones, where each part gets its own line
    return (f'<footer class="site-footer"><a class="sundown" href="index.html" aria-label="Sunday Light, home">'
            f'<span class="sundown-scene">{art.footer_scene("m")}{art.footer_scene("w")}</span>'
            f'<span class="sundown-word" aria-hidden="true"><span>Sunday Light</span></span></a>'
            f'<div class="footer-inner wrap"><nav class="footer-nav" aria-label="Footer">{nav}</nav>'
            f'<a class="footer-instagram" href="{ig_url}" rel="me">{icon("instagram")}'
            f'<span><span class="sr-only">Instagram </span>{e(ig_name)}</span>{icon("arrow-ne")}</a>'
            f'<p class="golden-hour" data-golden>Golden hour: the last hour before sunset, and the best light of the day.</p>'
            f'<p class="footer-base t-caption"><span class="fb">&copy; <span data-year>2026</span> Sunday Light</span>'
            f'<span class="fb">{dot}Adelaide, South Australia</span>'
            f'<span class="fb">{dot}<a href="privacy.html">Privacy</a> · Website by <a href="https://www.lumenadl.com/">Lumen</a></span>'
            f'<span class="fb fb-still" hidden>{dot}<button class="still-toggle" type="button" aria-pressed="false">Hold still</button></span>'
            f'<span class="fb">{dot}<a class="to-top" href="#top">Back to top {icon("to-top")}</a></span></p>'
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


def lcp_preload(lcp):
    """The LCP photo's preload, from the same srcset builder and SIZES entry as its <source>."""
    key, sizes = lcp
    path, w, h, _, _ = PHOTOS[key]
    if not exists(path):
        return ''
    w, _ = size_of(path, (w, h))
    return (f'<link rel="preload" as="image" type="image/webp" imagesrcset="{srcset(path, w)}" '
            f'imagesizes="{SIZES.get(sizes, sizes)}" fetchpriority="high">\n')


def head(title, desc, *, jsonld=False, italic=False, lcp=None):
    # The LCP photo first, then Cormorant 300 (and its italic where the h1 has one); every other face swaps onto its
    # metric-matched fallback without moving anything.
    preload = (lcp_preload(lcp) if lcp else '') + font_preload('cormorant-garamond-300')
    if italic:
        preload += font_preload('cormorant-garamond-300-italic')
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


def page(page_key, active, title, desc, main, *, lcp=None, jsonld=False, robots=None, body_extra=''):
    """A whole page. page_key: home | gallery | investment | kind-words | contact | privacy | 404 (data-page). lcp: the
    LCP photo as (key, SIZES key) on pages that preload it (Home, Investment)."""
    italic = '<em>' in main.split('</h1>', 1)[0]
    attrs = f' data-page="{page_key}"' + (' data-nf' if page_key == '404' else '')
    out = (f'<!doctype html>\n<html lang="en-AU"{attrs}>\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           + (f'<meta name="robots" content="{robots}">\n' if robots else '')
           + head(title, desc, jsonld=jsonld, italic=italic, lcp=lcp) + '</head>\n<body>\n' + header(active)
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
# The pre-redesign page bodies below keep building against the new helpers until the page packages replace them.
# --- legacy shims: delete at merge ---
from content import TILES, PORTFOLIO_WEDDINGS  # noqa: E402
LEGACY_SIZES = {   # the old layouts' photo sizes, for the old page bodies only
    'arch': '(max-width: 380px) calc(100vw - 36px), (max-width: 860px) 340px, 440px',
    'tile': '(max-width: 700px) calc(100vw - 36px), 380px',
    'card': '(max-width: 760px) calc(100vw - 36px), 560px',
    'grid': '(max-width: 600px) 48vw, (max-width: 1000px) 46vw, 370px',
}
# --- end of legacy shims ---


def index():
    tiles = ''.join(f'<li><a class="tile" href="{href}">{fig(key, LEGACY_SIZES["tile"], cls="tile-photo", ratio="4/5")}'
                    f'<span class="tile-name">{e(name)}</span></a></li>' for name, key, href in TILES if exists(PHOTOS[key][0]))
    intro = ''.join(f'<p>{e(p)}</p>' for p in INTRO)
    main = f'''{window(HERO, "hero")}

<section class="quote panel"><div class="wrap narrow">
<h1>Photographs that feel like a <em>Sunday afternoon.</em></h1>
<p class="quote-line">Weddings, couples, families, maternity and newborns, from the coast to the hills</p>
</div></section>

<section class="section intro" aria-labelledby="intro-title"><div class="wrap intro-grid">
<div><p class="eyebrow">Why Sunday Light</p><h2 id="intro-title">The best light of the week.</h2>
<div class="prose">{intro}</div><div class="actions">{button("contact.html", "Book a session", variant="secondary")}</div></div>
{fig("arch-mirror", LEGACY_SIZES["arch"], cls="arch")}
</div></section>

{window(HOME_WINDOWS[0], "a", above="paper")}

<section class="section panel" aria-labelledby="work-title"><div class="wrap">
<h2 class="center-title" id="work-title">See the work</h2>
<ul class="tiles">{tiles}</ul>
<div class="center">{link_arrow("gallery.html", "View the gallery")}</div>
</div></section>

{window(HOME_WINDOWS[1], "b", above="paper")}

{kind_words("index")}

{instagram_sheet()}

{closing("index")}'''
    return page('home', 'index.html', 'Sunday Light | Adelaide wedding & family photographer',
                'Natural, light-filled photography for weddings, couples, families, maternity and newborns across Adelaide. Relaxed sessions on the coast, in the hills and at home.',
                main, lcp=(HERO[0], 'hero'), jsonld=True)


def gallery_item(path, alt, i, first_gallery):
    w, h = size_of(path, (1333, 2000))
    # The first photo is the one people see first, so it loads straight away; the rest load as they come into view.
    pic = _picture(path, w, h, alt, LEGACY_SIZES['grid'], priority=first_gallery and i == 0)
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
    main = f'''{page_head("Gallery", "A few <em>favourite days.</em>", lead, layout="center", extra=chips)}
{sections}
{closing("gallery")}'''
    lightbox = ('<dialog class="lightbox" aria-label="Photo viewer"><div class="lightbox-inner">'
                f'<button class="lb-btn lb-prev" type="button" aria-label="Previous photo">{icon("chev-l")}</button>'
                '<figure class="lb-figure"></figure>'
                f'<button class="lb-btn lb-next" type="button" aria-label="Next photo">{icon("chev-r")}</button>'
                f'<button class="lb-btn lb-close" type="button" aria-label="Close">{icon("close")}</button>'
                '<p class="lb-count" aria-hidden="true"></p><p class="sr-only lb-live" aria-live="polite"></p>'
                '</div></dialog>\n')
    return page('gallery', 'gallery.html', 'Gallery | Sunday Light',
                'Wedding, couples, family, maternity and newborn photography from around Adelaide by Sunday Light.', main,
                body_extra=lightbox)


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
    return page('investment', 'investment.html', 'Investment | Sunday Light',
                'Wedding, couples and engagement, family, maternity and newborn photography sessions in Adelaide: prices and what each includes.',
                '\n\n'.join(p for p in parts if p), lcp=(INVESTMENT_HERO, 'inv-hero'))


def inv_hero():
    """Split hero (§4.14): the words on the left, one photo bleeding to the right edge; on phones the photo comes first."""
    lead, *rest = INVESTMENT_INTRO
    return (f'<section class="inv-hero sec--flush" aria-labelledby="investment-title">'
            f'{fig(INVESTMENT_HERO, "inv-hero", cls="inv-hero-photo", fill=True, priority=True)}'
            f'<div class="inv-hero-text wrap"><p class="eyebrow">Investment</p><h1 id="investment-title">Photos you’ll keep '
            f'<em>for good.</em></h1><p class="lead">{e(lead)}</p>{"".join(f"<p>{e(p)}</p>" for p in rest)}</div></section>')


NUMBER_WORDS = ('no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve')


def spec_sheet(s):
    """Every include but the gallery (the hero intro promises it for every session) as a labelled row, then the price
    row, or "Pricing on enquiry" in the same slot."""
    rows = [x for x in s['includes'] if x != GALLERY]
    price = f'<dd class="t-price">{e(s["price"])}</dd>' if s.get('price') else '<dd class="spec-ask">Pricing on enquiry</dd>'
    return (f'<dl class="spec" data-rules>'
            + ''.join(f'<div style="--i:{i}"><dt>{e(SPEC_LABELS[x])}</dt><dd>{e(x)}</dd></div>' for i, x in enumerate(rows))
            + f'<div class="spec-price" style="--i:{len(rows)}"><dt>Investment</dt>{price}</div></dl>')


def session_text(s):
    """Her paragraphs, the spec sheet and the session's one action."""
    if s['id'] == 'weddings':
        action = link_arrow('#wedding-packages', f'See the {NUMBER_WORDS[len(WEDDING_PACKAGES)]} packages')
    else:
        action = link_arrow(f'contact.html?session={quote_plus(FORM_SESSION[s["id"]])}',
                            f'Enquire about {s.get("short", s["name"]).lower()}')
    body = ''.join(f'<p>{e(p)}</p>' for p in s['body'])
    return f'<div class="session-body">{body}</div>{spec_sheet(s)}<div class="session-action">{action}</div>'


def session_row(s, mirror=False):
    """A session with its photo: photo in cols 1-6 and words in 8-12 (mirrored on alternate rows); on phones the photo
    runs full-bleed above the words."""
    sid = s['id']
    return (f'<article class="session sec--standard{" session--mirror" if mirror else ""}" id="{sid}" aria-labelledby="{sid}-title">'
            f'<div class="wrap grid-12">{fig(s["photo"], "session", cls="session-photo", ratio="4/5")}'
            f'<div class="session-text"><h2 id="{sid}-title">{e(s["name"])}</h2>{session_text(s)}</div></div></article>')


def carte(sessions):
    """Sessions whose photo has not arrived yet: one ruled row each, the name set large, under an eyebrow built from
    the names. No section head, so it never repeats a neighbour's."""
    names = [s.get('short', s['name']) for s in sessions]
    label = (', '.join(names[:-1]) + ' & ' + names[-1]) if len(names) > 1 else names[0]
    rows = ''.join(f'<article class="session session--word" id="{s["id"]}" aria-labelledby="{s["id"]}-title">'
                   f'<h2 class="t-word" id="{s["id"]}-title">{e(s.get("short", s["name"]))}</h2>'
                   f'<div class="session-text">{session_text(s)}</div></article>' for s in sessions)
    return (f'<section class="carte sec--standard" aria-labelledby="carte-label"><div class="wrap">'
            f'<p class="eyebrow" id="carte-label">{e(label[0] + label[1:].lower())}</p>{rows}</div></section>')


def wedding_packages():
    """The five packages (§4.15): arch-topped cards from 861px, arch rows below; the hours of light (M08) in each dome.
    No package is marked: nothing says one is preferred."""
    longest = max(h for _, h, _ in WEDDING_PACKAGES)
    tiers = ''.join(f'<li class="tier" data-hours="{h}" style="--i:{i}"><div class="tier-sky">{art.tier_arc(h, longest)}</div>'
                    f'<h3 class="tier-name">{e(name)}</h3><p class="tier-hours t-caption">{h} hours</p>'
                    f'<p class="tier-price t-price">{e(price)}</p></li>' for i, (name, h, price) in enumerate(WEDDING_PACKAGES))
    notes = ''.join(f'<div><h3>{title}</h3><ul role="list">{"".join(f"<li>{e(x)}</li>" for x in items)}</ul></div>'
                    for title, items in (('Every package includes', WEDDING_INCLUDES), ('Good to know', WEDDING_TERMS)))
    return (f'<section class="packages sec--band" id="wedding-packages" aria-labelledby="wedding-packages-title"><div class="wrap">'
            f'<div class="head--split"><h2 id="wedding-packages-title">Wedding <em>packages</em></h2>'
            f'<p class="lead">The packages differ only in hours. Everything below comes with every one of them.</p></div>'
            f'<ol class="tiers" role="list" data-rules style="--i:{len(WEDDING_PACKAGES)}">{tiers}</ol>'
            f'<div class="tier-notes">{notes}</div><div class="actions">{button("contact.html?session=" + quote_plus(FORM_SESSION["weddings"]), "Check my wedding dates")}</div></div></section>')


def roman(n):
    """Lower-roman numerals for the steps."""
    out = ''
    for v, r in ((10, 'x'), (9, 'ix'), (5, 'v'), (4, 'iv'), (1, 'i')):
        out, n = out + r * (n // v), n % v
    return out


def how_it_works():
    """The steps as a ledger on a thread, each marked by a sun warming from morning to golden hour (§4.16)."""
    steps = ''.join(f'<li class="step" style="--i:{i}"><span class="step-marker">{art.step_sun(i + 1, len(STEPS))}</span>'
                    f'<span class="t-numeral" aria-hidden="true">{roman(i + 1)}.</span><h3>{e(t)}</h3><p>{e(d)}</p></li>'
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
    ig_name, ig_url = INSTAGRAM
    title, desc = 'Kind words | Sunday Light', 'What couples and families say about their sessions with Sunday Light, Adelaide photographer.'
    if KIND_WORDS_ARE_PLACEHOLDERS or not KIND_WORDS:
        main = f'''<section class="page-head holding"><div class="wrap narrow">
{fig(KIND_WORDS_HOLDING_PHOTO, "(max-width: 600px) 64vw, 380px", cls="arch holding-photo", ratio="3/4", priority=True)}
<p class="eyebrow">Kind words</p><h1>From the people <em>in the photos.</em></h1>
<p class="lead">This is where couples and families share how their sessions felt. The newest sessions go up on Instagram first.</p>
<div class="actions">{link_arrow(ig_url, "Newest sessions on Instagram", external=True)}</div>
</div></section>

{instagram_sheet("limestone")}

{closing("kind-words")}'''
        # kept out of search until there are real reviews to show
        return page('kind-words', 'kind-words.html', title, desc, main, robots='noindex')
    reviews = ''.join(
        f'<article class="review">{fig(r["photo"], LEGACY_SIZES["card"], cls="review-photo", ratio="4/5", alt="") if r["photo"] and r["photo_is_theirs"] else ""}'
        f'<div class="review-panel"><blockquote><p>“{e(r["words"])}”</p></blockquote><p class="review-name">{e(r["names"])}</p>'
        f'<p class="review-session">{e(r["session"])}</p></div></article>' for r in KIND_WORDS)
    main = f'''{page_head("Kind words", "From the people <em>in the photos.</em>", "A few words from the couples and families I’ve photographed.", layout="center")}

<section class="section reviews-section"><div class="wrap">
<div class="reviews">{reviews}</div>
</div></section>

{closing("kind-words")}'''
    return page('kind-words', 'kind-words.html', title, desc, main)


def contact():
    ig_name, ig_url = INSTAGRAM
    opts = ''.join(f'<option>{e(o)}</option>' for o in FORM_OPTIONS)
    heard = ''.join(f'<option>{o}</option>' for o in ['Instagram', 'A friend', 'Google', 'A wedding vendor', 'Somewhere else'])
    main = f'''{page_head("Contact", "Let’s plan <em>something lovely.</em>", "Tell me a little about what you’re planning. I’ll get back to you with availability and pricing.", layout="center")}

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
</div></section>'''
    return page('contact', 'contact.html', 'Contact | Sunday Light',
                'Check dates for wedding, couples, family, maternity and newborn photography in Adelaide.', main)


def privacy():
    ig_name, ig_url = INSTAGRAM
    main = f'''{page_head("Your details", "Privacy")}
<section class="text-page sec--standard"><div class="wrap"><div class="text">
<p>This page explains what happens to the details you share through this website.</p>
<h2 class="h2--sm">What I collect</h2><p>When you send an enquiry, I receive the details you type into the form: your name, email, and anything else you choose to include, such as a phone number, date or message.</p>
<h2 class="h2--sm">How I use it</h2><p>Only to reply to your enquiry and, if you book, to plan your session. I don’t sell or share your details for marketing.</p>
<h2 class="h2--sm">Photos</h2><p>Some session photos appear on this website and on Instagram. If you’d like a photo of you removed, just ask and I’ll take it down.</p>
<h2 class="h2--sm">Questions or changes</h2><p>To see, correct or delete the details you’ve sent, message me on Instagram at <a href="{ig_url}">{e(ig_name)}</a>.</p>
</div></div></section>'''
    return page('privacy', '', 'Privacy | Sunday Light', 'How Sunday Light handles the details you share.', main)


def not_found():
    # The footer scene stays at golden hour here (never scroll-linked); the dusk plays in this mark instead (M03).
    main = f'''<section class="nf sec--breath head--center"><div class="wrap">
{mark("nf", "xl")}
<p class="eyebrow">Page not found</p><h1>This page has <em>wandered off.</em></h1>
<p class="lead">It may have moved, or the link may be old.</p>
<div class="actions nf-actions">{button("index.html", "Back home", cls="nf-home")}{link_arrow("gallery.html", "See the gallery")}</div>
</div></section>'''
    return page('404', '', 'Page not found | Sunday Light', 'This page could not be found.', main)


PAGES = {'index.html': index, 'gallery.html': gallery, 'investment.html': investment, 'kind-words.html': kind_words_page,
         'contact.html': contact, 'privacy.html': privacy, '404.html': not_found}
RETIRED = ['portfolio.html', 'sessions.html', 'about.html', 'enquire.html']  # replaced by the pages above


# ------------------------------------------------------------------ checks (UI spec §6.5, build plan §4.1)
KB = 1024
WP0_CSS = ['00-base', '10-buttons', '20-header-menu', '30-photos-windows', '50-instagram', '55-page-head', '85-text',
           '90-footer', '95-hover', '97-motion', '99-calm']
WP0_JS = ['00-kernel', '05-moments', '10-menu', '15-header', '20-photos', '25-index', '70-year-golden-hour', '99-end']
PART_BUDGET = {   # bytes, unminified, comments included; each package is held to its own slice (plan §8)
    'css': {'WP0': (WP0_CSS, 38 * KB), 'WP1': (['40-home'], 5 * KB), 'WP2': (['60-gallery-viewer'], 6.5 * KB),
            'WP3': (['70-investment'], 7.5 * KB), 'WP4 contact': (['80-contact'], 5 * KB),
            'WP4 kind words': (['45-kind-words'], 2 * KB)},
    'js': {'WP0': (WP0_JS, 18 * KB), 'WP1': (['32-home'], 1 * KB), 'WP2': (['50-viewer'], 7 * KB),
           'WP3': (['36-investment'], 1 * KB), 'WP4': (['60-form', '40-session-prefill'], 5 * KB)},
}
TOTAL_BUDGET = {'css': 64 * KB, 'js': 32 * KB}
HEAD_SCRIPT_BUDGET = 1.25 * KB
SVG_BUDGET = (20_000, 3_000)   # inline SVG per page: raw, gzipped
BREAKPOINTS = {399, 400, 599, 600, 860, 861, 1099, 1100, 1439, 1440}
LEGACY_MARKER = '/* bp: legacy */'   # a page part still holding pre-redesign CSS: exempt from the breakpoint and slice checks
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
        legacy = text.startswith(LEGACY_MARKER)
        bare = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
        if not legacy:
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
            legacy = kind == 'css' and any(open(os.path.join(HERE, 'css', n + '.css'), encoding='utf-8').read().startswith(LEGACY_MARKER)
                                           for n in names if n in sizes)
            report.append(f'  {pkg} {used / KB:.1f}/{limit / KB:.1f}KB' + (' (legacy, not held yet)' if legacy else ''))
            if used > limit and not legacy:
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


def verify(pages, out):
    errors = []
    fail = errors.append
    css_sizes = check_css(fail)
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
    for ext, name, note in (('css', 'styles.css', '/* Sunday Light. Built from tools/site/css/ by tools/site/build.py: edit the parts there. */\n'),
                            ('js', 'main.js', '// Sunday Light. Built from tools/site/js/ by tools/site/build.py: edit the parts there.\n')):
        with open(os.path.join(out, name), 'w', encoding='utf-8') as f:
            f.write(note + ''.join(open(part, encoding='utf-8').read() for part in parts(ext)))


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
    with open(os.path.join(out, 'favicon.svg'), 'w', encoding='utf-8') as f:
        f.write(art.FAVICON)
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
