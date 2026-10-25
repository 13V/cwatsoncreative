# Every SVG on the Sunday Light site (UI spec §3). Each function returns one inline <svg>; there is no sprite and no
# <use>, so motion can target the parts. All of it is decoration: aria-hidden, focusable="false", no <title>, and
# the meaning is always in the HTML text beside it.
#
# Two kinds of path, never mixed:
#   icons and static hairlines  vector-effect="non-scaling-stroke", stroke-width 1.3 (icons) or 1 (hairlines)
#   drawable paths              pathLength="1", no vector-effect, stroke width set in CSS per size band. They hide with
#                               stroke-dasharray: 1 2; stroke-dashoffset: 1.01 and draw to 0 (dot-free with round caps).
# Colours are attributes from the palette, so the art is right even if the CSS fails.
from math import cos, pi, sin

PAPER, LIMESTONE, SALTBUSH, PADDOCK, BARK, GULF, MIST = '#F6F2EA', '#ECE6DB', '#8B937A', '#C3964F', '#5C4D3F', '#A7BBC3', '#FBF8F2'
HILL_TINT, LINE, GOLD_HOUR, SUN_ON_DARK = '#C1C3B2', '#DCD3C4', '#E9D3AE', '#E2C48F'
HIDDEN = 'aria-hidden="true" focusable="false"'


def num(v, places=2):
    """A coordinate with at most two decimals, no trailing zeros and no leading zero (.33, -.1, 150)."""
    t = f'{v:.{places}f}'.rstrip('0').rstrip('.')
    t = t.replace('0.', '.', 1) if t.startswith(('0.', '-0.')) else t
    return '0' if t in ('', '-0', '-') else t


# ------------------------------------------------------------------ A1 the brand mark (the logo)
ARCH = 'M44,206 V100 A56,56 0 0 1 156,100 V206 Z'
HILL_FAR = 'M40,168 C70,146 104,150 160,134 V210 H40 Z'
HILL_NEAR = 'M40,184 C78,168 116,182 160,166 V210 H40 Z'
LOGO_WAVE = 'M58,196 q9,-5 18,0 t18,0 t18,0 t18,0 t18,0'
# size: (outline stroke, wave stroke, width, height, svg id)
MARK = {'sm': (6, 3.6, 27, 38, ''), 'lg': (2.75, 2.4, 63, 88, 'success-mark'), 'xl': (1.6, 1.4, 114, 160, 'nf-mark')}


def mark(uid, size='sm'):
    """The logo: an arch window with the sun low over two hills and the gulf. sm in the header, lg on the enquiry's
    thank-you card, xl on the 404, where a Gulf-blue dusk sits in its sky and the sun has set (the finished frame)."""
    stroke, wave, w, h, sid = MARK[size]
    dusk = (f'<rect class="nf-dusk" x="40" y="40" width="120" height="170" fill="{GULF}" opacity=".55"/>'
            if size == 'xl' else '')
    sid = f' id="{sid}"' if sid else ''
    return (f'<svg class="mark mark--{size}"{sid} viewBox="38 38 124 174" '
            f'width="{w}" height="{h}" {HIDDEN}>'
            f'<defs><clipPath id="arch-{uid}"><path d="{ARCH}"/></clipPath></defs>'
            f'<g clip-path="url(#arch-{uid})"><rect class="mk-sky" x="40" y="40" width="120" height="170" fill="{LIMESTONE}"/>'
            f'{dusk}<circle class="mk-sun" cx="100" cy="150" r="30" fill="{PADDOCK}"/>'
            f'<path class="mk-hill-far" d="{HILL_FAR}" fill="{HILL_TINT}"/><path class="mk-hill-near" d="{HILL_NEAR}" fill="{SALTBUSH}"/>'
            f'<path class="mk-wave" pathLength="1" d="{LOGO_WAVE}" fill="none" stroke="{GULF}" stroke-width="{wave}" '
            f'stroke-linecap="round"/></g>'
            f'<path class="mk-line" pathLength="1" d="{ARCH}" fill="none" stroke="{BARK}" stroke-width="{stroke}" '
            f'stroke-linejoin="round"/></svg>')


# ------------------------------------------------------------------ A2 the favicon (unchanged)
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="14 39 172 172">'
           f'<defs><clipPath id="a"><path d="{ARCH}"/></clipPath></defs>'
           '<g clip-path="url(#a)"><rect x="40" y="40" width="120" height="170" fill="#F6F2EA"/>'
           '<circle cx="100" cy="148" r="32" fill="#C3964F"/>'
           '<path d="M40,166 C70,144 104,148 160,132 V210 H40 Z" fill="#C1C3B2"/>'
           '<path d="M40,182 C78,166 116,180 160,164 V210 H40 Z" fill="#8B937A"/></g>'
           f'<path d="{ARCH}" fill="none" stroke="#5C4D3F" stroke-width="10" stroke-linejoin="round"/></svg>\n')


# ------------------------------------------------------------------ A3 the gold arch keyline
# Drawn 8px outside an arch-masked photo (Home statement 2:3, Contact 3:4), open at the bottom. The box is within 2%
# of the photo's ratio, so the stretch is invisible and the arch stays concentric. Stroke width per band in CSS.
ARCH_LINES = {'2x3': ('0 0 100 150', 'M0 150V50A50 50 0 0 1 100 50V150'),
              '3x4': ('0 0 100 133.333', 'M0 133.333V50A50 50 0 0 1 100 50V133.333')}


def arch_line(ratio):
    vb, d = ARCH_LINES[ratio]
    w, h = (int(float(v)) for v in vb.split()[2:])
    return (f'<svg class="frame-line" viewBox="{vb}" width="{w}" height="{h}" preserveAspectRatio="none" overflow="visible" '
            f'{HIDDEN}><path pathLength="1" d="{d}" fill="none" stroke="{PADDOCK}" stroke-linecap="round"/></svg>')


# ------------------------------------------------------------------ A4 a wedding tier's hours of light
def tier_arc(hours, longest):
    """The card's dome is the sky; the gold light is the stretch of the day the package covers, and every package ends
    at sunset (the right horizon), so more hours start earlier. f = hours / longest. The lit stretch is its own path
    from the point at s = 1 - f to the right horizon; the warmer last twelfth is the hour before sunset (her golden
    hour). The sun rests half set on the horizon (the svg is clipped at the sill in CSS); M08 swings it along the arc
    on .sun-arm (rotate about the dome's centre) while the light draws."""
    f = hours / longest
    s = 1 - f
    x, y = 100 - 100 * cos(pi * s), 100 - 100 * sin(pi * s)
    gx, gy = 100 - 100 * cos(pi * 11 / 12), 100 - 100 * sin(pi * 11 / 12)
    arc = 'A100,100 0 0 1 200,100'
    return (f'<svg class="tier-arc" viewBox="0 0 200 100" width="200" height="100" overflow="visible" style="--f:{num(f, 3)}" '
            f'{HIDDEN}><g fill="none" stroke-linecap="round">'
            f'<path class="track" d="M0,100 {arc}" stroke="{LINE}"/>'
            f'<path class="gold-hour" d="M{num(gx)},{num(gy)} {arc}" stroke="{GOLD_HOUR}"/>'
            f'<path class="light" pathLength="1" d="M{num(x)},{num(y)} {arc}" stroke="{PADDOCK}"/></g>'
            f'<g class="sun-arm"><g class="sun-size"><circle class="sun" cx="200" cy="100" r="5" fill="{PADDOCK}"/></g></g></svg>')


# ------------------------------------------------------------------ A5 the footer scene (Sundown)
# One continuous Paddock line traced from the logo: the gulf horizon from the left, up the jamb of an arch window,
# over the crown, down, and on as the back hill; a shorter front hill; short Gulf waves under the horizon. Inside the
# arch is the logo's own scene, scaled, where the sun sets.
# key: (viewBox w, h, logo scale, logo offset x, y, the line, the front hill, waves as (x, y, half-waves, length, height))
SCENES = {
    'm': (390, 230, 1.25, 70, -39.5,
          'M0,218 H125 V85.5 A70,70 0 0 1 265,85.5 V218 C280,211 298,197 321,195 S361,204 390,200',
          'M291,230 C305,222 324,215 343,217 S373,226 390,223',
          [(14, 226, 4, 14, 4)]),
    'w': (1440, 300, 1.45, 575.2, -8.7,
          'M0,290 H639 V136.3 A81.2,81.2 0 0 1 801.4,136.3 V290 C846,277 902,241 982,236 S1102,262 1176,259 S1322,234 1440,244',
          'M934,300 C998,285 1058,268 1128,271 S1268,292 1338,287 S1412,277 1440,279',
          [(118, 296, 5, 20, 5), (352, 295, 3, 20, 4)]),
}
# The wide scene's farther wave started at y 293, so its crests touched the horizon (y 290) at every stroke band; it
# now starts 2 units lower and a little smaller (farther away), clear of the line. Same x and length as before.
# The hand's rhythm, taken from the illustrators' horizon waves: each half-wave a little longer or shorter, a little
# higher or lower, ending a hair above or below the line (ratios to the even wave).
_LENGTHS = (1.013, .988, 1.006, .981, 1.009, 1.002, 1.013, .988)
_HEIGHTS = (1.051, .973, .941, 1.035, 1.02, .957, 1.051, .973)
_DRIFT = (.031, -.016, .047, -.031, 0, .016, .031, -.016)


def hand_wave(x, y, n, length, height):
    """The logo's q/t wave (n half-waves of `length`, control `height`), re-cut by hand: same start, same overall length,
    back on the line at the end."""
    ls = [length * r for r in _LENGTHS[:n]]
    k = n * length / sum(ls)
    ls = [round(v * k, 1) for v in ls]
    ls[-1] = round(n * length - sum(ls[:-1]), 1)
    drift = [round(height * r, 1) for r in _DRIFT[:n]]
    drift[-1] = round(-sum(drift[:-1]), 1)
    d = f'M{num(x)},{num(y)}'
    for i, (seg, dy) in enumerate(zip(ls, drift)):
        up = -1 if i % 2 == 0 else 1
        d += f'q{num(seg / 2)},{num(up * height * _HEIGHTS[i])} {num(seg)},{num(dy)}'
    return d


def footer_scene(kind):
    w, h, s, tx, ty, line, front, waves = SCENES[kind]
    uid = f'dusk-{kind}'
    fit = 'xMidYMax slice' if kind == 'w' else 'xMidYMax meet'
    gulf = ''.join(f'<path class="dusk-wave" pathLength="1" d="{hand_wave(*wv)}"/>' for wv in waves)
    pen = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'  # colours here too, in case the CSS fails
    return (f'<svg class="dusk dusk--{kind}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" preserveAspectRatio="{fit}" {HIDDEN}>'
            f'<defs><clipPath id="{uid}-a"><path d="{ARCH}"/></clipPath>'
            f'<linearGradient id="{uid}-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EDD8C0"/>'
            f'<stop offset="1" stop-color="#E4C08A"/></linearGradient></defs>'
            f'<g transform="translate({tx} {ty}) scale({s})"><g clip-path="url(#{uid}-a)">'
            f'<rect x="40" y="40" width="120" height="170" fill="{PAPER}"/>'
            f'<rect class="sky-gold" x="40" y="40" width="120" height="170" fill="url(#{uid}-g)"/>'
            f'<circle class="dusk-sun" cx="100" cy="150" r="30" fill="{PADDOCK}"/>'
            f'<path d="{HILL_FAR}" fill="{HILL_TINT}"/><path d="{HILL_NEAR}" fill="{SALTBUSH}"/>'
            f'<path d="{LOGO_WAVE}" fill="none" stroke="{GULF}" stroke-width="2.4" stroke-linecap="round"/>'
            f'<path class="glint" pathLength="1" d="{LOGO_WAVE}" fill="none" stroke="{MIST}" stroke-width="2.4" '
            f'stroke-linecap="round"/></g></g>'
            f'<g {pen} stroke="{PADDOCK}"><path class="dusk-line" pathLength="1" d="{line}"/>'
            f'<path class="dusk-line dusk-line--front" pathLength="1" d="{front}"/></g>'
            f'<g {pen} stroke="{GULF}">{gulf}</g></svg>')


# ------------------------------------------------------------------ A6 an arcade window arch
def window_arch():
    """One per pane of a photo window (M02): the hole is exactly 2:1, so the stretched semicircle stays round. Bark,
    because it is structure. Stroke width per band in CSS; overflow visible so the crown and feet keep their stroke."""
    return (f'<i class="hole"><svg viewBox="0 0 200 100" width="200" height="100" preserveAspectRatio="none" overflow="visible" '
            f'{HIDDEN}><path class="frame" pathLength="1" d="M0,100 A100,100 0 0 1 200,100" fill="none" stroke="{BARK}" '
            f'stroke-linecap="round"/></svg></i>')


# ------------------------------------------------------------------ B icons
# The hand-drawn set: lines with a slight bow and a swept arrowhead, so they read as pen marks. currentColor, so they
# are Bark on light and Mist on dark.
_NSS = ' vector-effect="non-scaling-stroke"'
ICONS = {
    # name: (svg class, viewBox, width, height, paths as (class, d, extra attributes))
    'arrow': ('arw', '0 0 32 12', 28, 10.5, [('arw-shaft', 'M1 6.1Q15.5 5.8 30 6', ''),
                                             ('arw-head', 'M26.4 2.8Q28.5 5 30 6Q28.5 7 26.4 9.1', '')]),
    'arrow-ne': ('arw arw--ne', '4 4 16 16', 12, 12, [('arw-shaft', 'M7.3 16.9Q12.1 11.7 17.2 6.8', ''),
                                                      ('arw-head', 'M12.2 6.7Q15.4 7 17.2 6.8Q17 8.6 17.3 11.7', '')]),
    'chev-l': ('icon icon--chev', '0 0 24 24', 28, 28, [('', 'M14.4 5.3Q11.2 9.5 8.8 12Q11.2 14.5 14.5 18.6', '')]),
    'chev-r': ('icon icon--chev', '0 0 24 24', 28, 28, [('', 'M9.6 5.3Q12.8 9.5 15.2 12Q12.8 14.5 9.7 18.6', '')]),
    'close': ('icon icon--close', '0 0 24 24', 20, 20, [('', 'M6.3 6.2Q12.4 11.6 17.8 17.7', ''),
                                                       ('', 'M17.7 6.3Q11.7 11.8 6.2 17.8', '')]),
    'plus': ('icon icon--plus', '0 0 20 20', 18, 18, [('pm-h', 'M3 10h14', ''), ('pm-v', 'M10 3v14', '')]),
    'instagram': ('icon icon--ig', '0 0 24 24', 18, 18, [
        ('', 'M8.6 3.5Q12.2 3.3 15.7 3.5C18.4 3.5 20.6 5.7 20.6 8.4Q20.7 11.9 20.6 15.4C20.6 18.2 18.3 20.5 15.5 20.5'
             'Q11.9 20.7 8.2 20.5C5.5 20.5 3.4 18.4 3.4 15.7Q3.2 12.2 3.4 8.7C3.4 5.8 5.7 3.5 8.6 3.5Z', ''),
        ('', 'M9.8 8.8C11.6 7.6 14 7.8 15.4 9.6C16.8 11.4 16.1 14 14.2 15.2C12.4 16.4 9.9 16.3 8.6 14.4'
             'C7.3 12.5 7.5 9.9 9.4 8.3C9.7 8.1 10 8 10.2 7.9', ''),
        ('', 'M16.9 7L17 7', '')]),
    'alert': ('icon icon--alert', '0 0 16 16', 14, 14, [('', 'M14.25 8A6.25 6.25 0 1 1 1.75 8a6.25 6.25 0 0 1 12.5 0Z', ''),
                                                       ('', 'M8 4.75v3.75', ''), ('', 'M8 11.1h.01', ' stroke-width="1.6"')]),
    'to-top': ('icon icon--top', '0 0 20 14', 20, 14, [('', 'M1 12.5C5.5 8.5 14.5 8.5 19 12.5', ''),
                                                      ('top-sun', 'M7 9.5a3 3 0 0 1 6 0Z', ' fill="currentColor" stroke="none"')]),
}


def icon(name):
    cls, vb, w, h, paths = ICONS[name]
    over = ' overflow="visible"' if name.startswith('arrow') else ''
    merged = []  # strokes with no class and no attributes of their own share one <path> (same pixels, fewer bytes)
    for c, d, extra in paths:
        if merged and not (c or extra) and not (merged[-1][0] or merged[-1][2]):
            merged[-1] = ('', merged[-1][1] + d, '')
        else:
            merged.append((c, d, extra))
    body = ''.join(f'<path{f" class={chr(34)}{c}{chr(34)}" if c else ""} d="{d}"{extra}{_NSS if "stroke=" not in extra else ""}/>'
                   for c, d, extra in merged)
    return (f'<svg class="{cls}" viewBox="{vb}" width="{num(w)}" height="{num(h)}"{over} {HIDDEN} fill="none" '
            f'stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


# ------------------------------------------------------------------ B13 the ornament: rule, arch, sun, rule
def orn_window():
    """Above a closing heading and in the Kind words interlude only. The two rules start at the centre and run outward
    with a slight hand bow, so M12 draws them outward from the window."""
    rule = f'fill="none" stroke="{PADDOCK}" stroke-width="1" stroke-linecap="round"'
    return (f'<svg class="orn" viewBox="0 0 120 24" width="120" height="24" {HIDDEN} data-rules>'
            f'<path class="orn-rule" pathLength="1" d="M44 20.5C30 20.6 14 20.35 .5 20.5" {rule}/>'
            f'<path class="orn-rule" pathLength="1" d="M76 20.5C90 20.4 106 20.65 119.5 20.5" {rule}/>'
            f'<path class="orn-arch" d="M49 20.5V12a11 11 0 0 1 22 0v8.5" {rule}/>'
            f'<circle class="orn-sun" cx="60" cy="16.5" r="3" fill="{PADDOCK}"/></svg>')


# ------------------------------------------------------------------ B15 the index brush (under the current item)
def brush():
    return (f'<svg class="brush" viewBox="0 0 120 8" width="120" height="8" preserveAspectRatio="none" {HIDDEN}>'
            f'<path d="M2 5.5C22 3.1 48 2.4 74 3.6c18 .8 31 2.2 44 1.1" fill="none" stroke="{PADDOCK}" stroke-width="1.5" '
            f'stroke-linecap="round"/></svg>')


# ------------------------------------------------------------------ B16 the Home scroll cue
def scroll_cue():
    return (f'<svg class="cue" viewBox="0 0 12 56" width="12" height="56" {HIDDEN}><path d="M6 0V56" stroke="currentColor" '
            f'stroke-opacity=".7" stroke-width="1"{_NSS}/><circle class="cue-sun" cx="6" cy="8" r="3.5" fill="{SUN_ON_DARK}"/></svg>')


# ------------------------------------------------------------------ B17 the process markers (warming suns)
WARMTH = (.15, .4, .7, 1)


def step_sun(n, total=len(WARMTH)):
    """Step n of total (from 1): the sun warms from morning to golden hour; the last one glows."""
    a = WARMTH[min(n, len(WARMTH)) - 1]
    glow = (f'<circle class="step-glow" cx="12" cy="12" r="9" fill="none" stroke="{PADDOCK}" stroke-opacity=".35" stroke-width="1"/>'
            if n == total else '')
    return (f'<svg class="step-sun-art" viewBox="0 0 24 24" width="24" height="24" {HIDDEN}>'
            f'<circle class="step-sun" cx="12" cy="12" r="5" fill="{PADDOCK}"{f' fill-opacity="{num(a)}"' if a < 1 else ''} stroke="{PADDOCK}" '
            f'stroke-width="1"/>{glow}</svg>')
