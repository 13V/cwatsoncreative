# Five logo directions for "Photos with Charne", all in the boho palette from the coastal badge.
import math
from logos import FONTS, svg, gum_sprig, waves, leaf

B = dict(lime='#ECE6DB', paper='#F6F2EA', bush='#8B937A', paddock='#C3964F', bark='#5C4D3F', gulf='#A7BBC3')
MARC, CORM, JOST = FONTS['marc'], FONTS['corm'], FONTS['jost']
FRAUN = "'Fraunces', 'Iowan Old Style', Georgia, serif"
EPH = "'Ephesis', 'Snell Roundhand', 'Apple Chancery', cursive"
SOFT = "font-variation-settings:'SOFT' 100,'WONK' 1,'opsz' 144"


def _with(size, color):
    return (f'<tspan font-family="{CORM}" font-style="italic" font-weight="500" font-size="{size:.1f}" '
            f'letter-spacing="0" fill="{color}">with</tspan>')


# ------------------------------------------------------------------ 1 · the badge
def badge_mark(ink, accent, sea, bg='none', uid='b'):
    return svg('0 0 240 240', f'''
  <defs><path id="pt{uid}" d="M27,120 A93,93 0 0 1 213,120"/><path id="pb{uid}" d="M15,120 A105,105 0 0 0 225,120"/></defs>
  <circle cx="120" cy="120" r="114" fill="{bg}" stroke="{ink}" stroke-width="1.6"/>
  <circle cx="120" cy="120" r="80" fill="none" stroke="{ink}" stroke-width="1"/>
  <text font-family="{MARC}" font-size="15" letter-spacing="4.5" fill="{ink}"><textPath href="#pt{uid}" startOffset="50%" text-anchor="middle">PHOTOS WITH CHARNE</textPath></text>
  <text font-family="{MARC}" font-size="10.5" letter-spacing="3" fill="{ink}"><textPath href="#pb{uid}" startOffset="50%" text-anchor="middle">ADELAIDE · COAST &amp; HILLS</textPath></text>
  <circle cx="22" cy="120" r="2.2" fill="{accent}"/><circle cx="218" cy="120" r="2.2" fill="{accent}"/>
  <g transform="translate(124,62)">{gum_sprig(ink, 2)}</g>
  <g transform="translate(120,166)">{waves(sea, 2.2)}</g>''', 'Photos with Charne badge')


def badge_primary(ink, accent, sea, uid='bp'):
    inner = badge_mark(ink, accent, sea, uid=uid)
    inner = inner[inner.index('>') + 1:-6]  # strip the outer <svg>
    s = 50  # Marcellus size; PHOTOS adv 470.4 / CHARNE 474.2 per 100
    ls = s * 0.14
    return svg('0 0 640 340', f'''
  <g transform="translate(26,50)">{inner}</g>
  <text x="300" y="142" font-family="{MARC}" font-size="{s}" letter-spacing="{ls}" fill="{ink}">PHOTOS</text>
  <text x="302" y="196" font-family="{CORM}" font-style="italic" font-weight="500" font-size="{s * 1.12:.1f}" fill="{accent}">with</text>
  <text x="300" y="252" font-family="{MARC}" font-size="{s}" letter-spacing="{ls}" fill="{ink}">CHARNE</text>''',
               'Photos with Charne')


# ------------------------------------------------------------------ 2 · the arch
ARCH = 'M44,206 V100 A56,56 0 0 1 156,100 V206 Z'


def arch_mark(ink, accent, hill, sea, fill, uid='a', far='#C1C3B2'):
    return svg('0 0 200 240', f'''
  <defs><clipPath id="ac{uid}"><path d="{ARCH}"/></clipPath></defs>
  <g clip-path="url(#ac{uid})">
    <rect x="40" y="40" width="120" height="170" fill="{fill}"/>
    <circle cx="100" cy="150" r="30" fill="{accent}"/>
    <path d="M40,168 C70,146 104,150 160,134 V210 H40 Z" fill="{far}"/>
    <path d="M40,184 C78,168 116,182 160,166 V210 H40 Z" fill="{hill}"/>
    <path d="M58,196 q9,-5 18,0 t18,0 t18,0 t18,0 t18,0" fill="none" stroke="{sea}" stroke-width="2.4" stroke-linecap="round"/>
  </g>
  <path d="{ARCH}" fill="none" stroke="{ink}" stroke-width="2.6" stroke-linejoin="round"/>''', 'Arch mark: sun over the hills')


def arch_primary(ink, accent, hill, sea, fill, uid='ap', far='#C1C3B2'):
    inner = arch_mark(ink, accent, hill, sea, fill, uid=uid, far=far)
    inner = inner[inner.index('>') + 1:-6]
    s = 40
    return svg('0 0 640 400', f'''
  <g transform="translate(210,-6) scale(1.1)">{inner}</g>
  <text x="{320 + s * 0.07:.1f}" y="300" text-anchor="middle" font-family="{MARC}" font-size="{s}" letter-spacing="{s * 0.14:.1f}" fill="{ink}">PHOTOS {_with(s * 1.12, accent)} CHARNE</text>
  <text x="322.4" y="350" text-anchor="middle" font-family="{JOST}" font-size="12" font-weight="400" letter-spacing="4.8" fill="{ink}">ADELAIDE PHOTOGRAPHER</text>''',
               'Photos with Charne, Adelaide photographer').replace('viewBox="0 0 640 400"', 'viewBox="0 0 640 370"')


# ------------------------------------------------------------------ 3 · the sun
def _sun(cx, cy, r, ink, sun, n=11, r1=None, short=None, long=None, sw=4.5):
    r1 = r1 or r + 9
    short = short or r + 22
    long = long or r + 34
    rays = []
    for i in range(n):
        a = math.pi + math.pi * (i + 0.5) / n
        r2 = long if i % 2 == 0 else short
        rays.append(f'<line x1="{cx + r1 * math.cos(a):.1f}" y1="{cy + r1 * math.sin(a):.1f}" '
                    f'x2="{cx + r2 * math.cos(a):.1f}" y2="{cy + r2 * math.sin(a):.1f}"/>')
    return (f'<g stroke="{sun}" stroke-width="{sw}" stroke-linecap="round">{"".join(rays)}</g>'
            f'<path d="M{cx - r},{cy} A{r},{r} 0 0 1 {cx + r},{cy} Z" fill="{sun}"/>'
            f'<line x1="{cx - r - 40}" y1="{cy + 6}" x2="{cx + r + 40}" y2="{cy + 6}" stroke="{ink}" stroke-width="2.4" stroke-linecap="round"/>')


def sun_mark(ink, sun, bg='none'):
    return svg('0 0 200 200', f'<circle cx="100" cy="100" r="96" fill="{bg}"/>{_sun(100, 120, 34, ink, sun)}'
                              f'<line x1="70" y1="140" x2="130" y2="140" stroke="{ink}" stroke-width="2.4" stroke-linecap="round" opacity=".55"/>',
               'Sun mark')


def sun_primary(ink, sun, accent):
    s = 112  # Fraunces 400 soft: Charne adv 290.4 per 100
    return svg('0 0 640 340', f'''{_sun(320, 112, 38, ink, sun, sw=5)}
  <text x="320" y="170" text-anchor="middle" font-family="{FRAUN}" font-size="34" font-weight="300" font-style="italic" fill="{accent}" style="{SOFT}">photos with</text>
  <text x="320" y="272" text-anchor="middle" font-family="{FRAUN}" font-size="{s}" font-weight="400" fill="{ink}" style="{SOFT}">Charne</text>''',
               'Photos with Charne')


# ------------------------------------------------------------------ 4 · the signature
def _flourish(color, x, y, w):
    o, r = leaf(30, bend=0.2, width=0.13)
    return (f'<path d="M{x},{y} C{x + w * 0.35},{y + 10} {x + w * 0.7},{y + 9} {x + w},{y - 4}" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round"/>'
            f'<g transform="translate({x + w},{y - 4}) rotate(-120)" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linejoin="round"><path d="{o}"/></g>'
            f'<g transform="translate({x + w},{y - 4}) rotate(-60) scale(.8)" fill="none" stroke="{color}" stroke-width="2.4" '
            f'stroke-linejoin="round"><path d="{o}"/></g>')


def sig_mark(ink, accent, bg='none'):
    return svg('0 0 200 200', f'<circle cx="100" cy="100" r="96" fill="{bg}"/>'
                              f'<text x="96" y="132" text-anchor="middle" font-family="{EPH}" font-size="132" fill="{ink}">C</text>'
                              f'{_flourish(accent, 58, 150, 74)}', 'Signature mark')


def sig_primary(ink, accent, small):
    return svg('0 0 640 300', f'''
  <text x="{320 + 2.6:.1f}" y="86" text-anchor="middle" font-family="{JOST}" font-size="13" font-weight="500" letter-spacing="5.2" fill="{small}">PHOTOS WITH</text>
  <text x="314" y="206" text-anchor="middle" font-family="{EPH}" font-size="160" fill="{ink}">Charne</text>
  {_flourish(accent, 218, 238, 196)}''', 'Photos with Charne')


# ------------------------------------------------------------------ 5 · the rainbow
def _rainbow(cx, cy, colors, r0=78, step=16, sw=12):
    out = []
    for i, c in enumerate(colors):
        r = r0 - i * step
        out.append(f'<path d="M{cx - r},{cy} A{r},{r} 0 0 1 {cx + r},{cy}" fill="none" stroke="{c}" stroke-width="{sw}"/>')
    return ''.join(out)


def rainbow_mark(colors, bg='none'):
    return svg('0 0 200 200', f'<circle cx="100" cy="100" r="96" fill="{bg}"/>{_rainbow(100, 134, colors, r0=64, step=14, sw=10)}',
               'Rainbow mark')


def rainbow_primary(colors, ink, sub):
    return svg('0 0 640 320', f'''{_rainbow(320, 170, colors)}
  <text x="320" y="246" text-anchor="middle" font-family="{JOST}" font-size="46" font-weight="300" fill="{ink}">photos with <tspan font-weight="500">charne</tspan></text>
  <text x="322.4" y="288" text-anchor="middle" font-family="{JOST}" font-size="12" font-weight="400" letter-spacing="4.8" fill="{sub}">ADELAIDE PHOTOGRAPHER</text>''',
               'photos with charne')
