"""Sunday Light: gold grease-pencil marks and small ornaments.

These are single-colour line art in currentColor, so CSS colours them Paddock or paddock-ink. Every function
returns one inline <svg> string. The markup is the finished, fully drawn state. Motion is added later by CSS.

Conventions for the motion layer:
- path.draw has pathLength="1" and style="--d:n". n is the draw order (0 first). Paths that share an n draw together.
- Filled pieces that move as a unit have their own class (sc-sun, sc-quote). Their geometry is a tidy closed
  shape, so transform-box: fill-box with transform-origin: center (or 50% 100%) behaves.
- Stroke weight is set once on the <svg> (stroke-width), so a stylesheet rule can override it.
- No vector-effect="non-scaling-stroke" on any path.draw. In Chromium, pathLength is resolved in user space
  while a non-scaling stroke dashes in screen space. A stretched underline with stroke-dasharray:1 and
  stroke-dashoffset:0 would stop part of the way along. Only the dotted rule, which never draws, uses it.
  Stretched marks are drawn for the size they usually render at, and arch_frame(width=...) evens out its line.
"""
from html import escape

_ATTRS = ('aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" fill="none" '
          'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"')


def _svg(cls, vb, w, h, body, sw, stretch=False):
    par = ' preserveAspectRatio="none"' if stretch else ''
    return (f'<svg class="{escape(cls)}" viewBox="{vb}" width="{w}" height="{h}"{par} {_ATTRS} '
            f'stroke-width="{sw}">{body}</svg>')


def _draw(d, n=0, extra=''):
    return f'<path class="draw" pathLength="1" style="--d:{n}"{extra} d="{d}"/>'


# Underlines sit under one italic word. viewBox 0 0 200 16, stretched to the word's width.
# The CSS should keep the height near 12-16px so horizontals stay about 1.5-2px thick.
UNDERLINES = {
    # one confident stroke, easing up at the end as the pencil lifts
    1: 'M4.5,11.2C30,10.4 60,11.5 94,10.9C127,10.3 156,10.4 175,9.2C184,8.6 190.5,7.2 195.5,4.6',
    # across, a light turn, and back underneath
    2: 'M5,8.4C46,7.1 104,7.4 160,6.3C176,6 189.5,5.6 193.4,6.7C196.3,7.6 192.4,9.3 182,10C141,12.5 88,12.5 38,13.5',
    # a short swash tail: the stroke rises into one small loop and runs out
    3: 'M4,11C40,9.8 90,9.6 140,10C156,10.1 166,9.8 172,8C178,6 181,2.8 177.6,2.4C174,2 172.4,6.6 175,9.4C178.6,13 188,12 196,8.6',
}

# For under a closing invitation heading. viewBox 0 0 240 40, natural size.
SWASH = ('M8,22C30,30 64,33 96,27C112,24 128,16 130,10C132,4 124,2.6 119,5.4C113,9 113,19 121,24.5'
         'C133,32 168,34 196,28C212,24.6 224,19 232,13')

# The sun's path across the sky. The arc stays within a hair of a circle of radius 134.2 centred on
# (100, 151.2) in viewBox units, so .sc-sun can travel along it with
#   transform-box: view-box; transform-origin: 100px 151.2px; transform: rotate(-57.5deg) -> none
# (-57.5deg puts it on the left horizon; the finished dot sits 22 degrees past noon, in the low afternoon).
SUN_ARC = 'M22,42C44.6,25.9 71.8,17.1 100,17C128.4,16.9 155.4,25.8 178,42'
SUN_ARC_ORIGIN = (100, 151.2)

# --- sprig data (generated) ---
# Stem(s) first, then leaves from the bottom up, each its own path.draw so the sprig grows.
SPRIGS = {
    1: (
        'M31,88C28,66 32.5,40 28.5,13',
        'M30,56.9C36,48.9 43,43.9 47,31.9',
        'M30.2,79.2L29.2,78.5C30,73.5 22.5,69.2 19.1,72C18.6,76.3 25.5,81.7 29.2,78.5',
        'M29.9,70.1L30.8,69.3C34.7,71.9 40.7,66 39.8,61.9C36.1,59.5 29.4,64.5 30.8,69.3',
        'M30,60.6L29.2,59.8C30.8,55.4 24.7,50.3 21.1,52.3C20,56.1 25.4,62.1 29.2,59.8',
        'M30.2,47.8L29.6,47C31.4,43 26.1,37.9 22.6,39.6C21.3,43.1 25.8,49 29.6,47',
        'M37.8,47.7L38.8,47.6C40,51.5 47,50.5 48.5,47.2C47.2,43.7 40.3,43.5 38.8,47.6',
        'M44,38.9L43.8,37.9C47,35.8 45.5,30 42.2,29.6C39.7,31.6 40.3,37.7 43.8,37.9',
        'M30.2,36.9L30.6,36C34.4,36.6 36.7,30.2 34.6,27.5C31.1,27 27.9,33 30.6,36',
        'M47,31.9L47.5,31.2C51,31.9 53.6,26.7 51.7,24.4C48.8,24.1 45.5,28.9 47.5,31.2',
        'M29.9,26.7L29.2,25.9C30.7,22.4 26.2,18.1 23.2,19.5C22.1,22.5 26,27.6 29.2,25.9',
        'M28.5,13L28.6,12.2C32.1,11 31.9,5 29,3.8C26.3,5 25.6,11 28.6,12.2',
    ),  # saltbush: small blunt leaves on short stalks, one side shoot
    2: (
        'M29,88C31.5,66 25.5,42 31.5,15',
        'M29.6,76.6C35.1,74.3 41.7,63.9 46,57.6C39.5,61.8 30.4,69.6 29.5,76.4',
        'M29.4,65.5C28.2,59 19,52 12.6,48.4C17.1,54.2 24,63.7 29.6,65.4',
        'M29,54.1C33.7,51.7 38.5,42 41.6,36.1C36.3,40.2 28.9,47.9 28.8,54',
        'M28.7,43.8C28.5,38.1 21.5,31.6 16.4,28C19.5,33.3 24.2,41.9 28.9,43.7',
        'M29,33.2C33,31.6 36.7,24.1 39.1,19.5C34.9,22.6 28.9,28.2 28.9,33.1',
        'M29.8,24.6C31.2,20.7 27.7,14.9 25,11.4C25.7,15.7 26.8,22.5 29.9,24.6',
        'M31.5,15C34.2,12.9 34.6,6.8 34.7,2.9C32.6,6.2 29.9,11.7 31.5,15',
        'M29.6,71.1C26.6,71.7 24,73.4 22.4,76C24.2,77 24.6,79.8 23.3,82.2C21.9,84.7 19.4,86 17.6,85C15.8,84.1 15.4,81.3 16.7,78.8C18.1,76.3 20.6,75 22.4,76',
    ),  # olive: slender alternate leaves, one olive hanging low
}
# Circles a word: tilted, a touch egg-shaped, the pencil crossing its start and lifting away.
# viewBox 0 0 220 90, stretched.
ELLIPSE = 'M21.6,28.9C35.2,21 59.9,16.7 81.2,12.9C102.6,9.1 126.1,7.8 147,9.7C167.9,11.5 186,16.6 197.5,23.8C209,31 213.6,40.3 210.1,49.2C206.7,58.2 195.1,66.7 177.7,72.8C160.4,78.8 137.4,82.4 114,82.9C90.6,83.5 67,81 48.6,76.4C30.2,71.8 17.1,65.1 12.1,57.6C7.2,50.1 10.7,41.9 19.6,33.9C28.5,26 44.6,17.8 66.5,12.8'
# --- end sprig data ---

# Opening quotation mark: two "6" forms, a full ball with a tapering hairline tail. viewBox 0 0 72 52.
_Q = ('M{a},3C{b},8 {c},19 {d},33C{e},43 {f},50 {g},50C{h},50 {i},44.5 {i},38C{i},31.5 {h},26.5 {j},26.5'
      'C{k},26.5 {l},27.8 {m},29.6C{n},18 {o},9 {a},3Z')


def _q(dx):
    xs = dict(a=30, b=17, c=5, d=3.5, e=2.5, f=8.5, g=16, h=23.5, i=28.5, j=17, k=13.5, l=10.8, m=9,
              n=10.5, o=18.5)
    return _Q.format(**{key: f'{v + dx:g}' for key, v in xs.items()})


QUOTE = (_q(1), _q(37))

ARCH_FRAME = 'M4,166V60A56,56 0 0 1 116,60V166Z'


def underline(variant=1, cls='mark mark-underline'):
    return _svg(cls, '0 0 200 16', 200, 16, _draw(UNDERLINES[variant]), 2, stretch=True)


def ellipse(cls='mark mark-ellipse'):
    return _svg(cls, '0 0 220 90', 220, 90, _draw(ELLIPSE), 1.8, stretch=True)


def swash(cls='mark mark-swash'):
    return _svg(cls, '0 0 240 40', 240, 40, _draw(SWASH), 1.6)


def sun_arc(cls='mark mark-sun-arc'):
    body = (_draw('M15,42.3H29', 0) + _draw(SUN_ARC, 1) + _draw('M171,42.1H185', 2) +
            '<circle class="sc-sun" cx="150.3" cy="26.8" r="3.6" fill="currentColor" stroke="none"/>')
    return _svg(cls, '0 0 200 46', 200, 46, body, 1.4)


def sprig(variant=1, cls='mark mark-sprig'):
    data = SPRIGS[variant]
    return _svg(cls, '0 0 60 90', 60, 90, ''.join(_draw(d, n) for n, d in enumerate(data)), 1.6)


def quote_mark(cls='mark mark-quote'):
    body = ''.join(f'<path class="sc-quote" style="--d:{n}" d="{d}"/>' for n, d in enumerate(QUOTE))
    return (f'<svg class="{escape(cls)}" viewBox="0 0 72 52" width="72" height="52" aria-hidden="true" '
            f'focusable="false" xmlns="http://www.w3.org/2000/svg" fill="currentColor">{body}</svg>')


def arch_frame(cls='mark mark-arch', width=120):
    """The logo arch outline. Pass the width it usually renders at so the line stays about 1.6px."""
    sw = f'{1.6 * 120 / width:.2f}'.rstrip('0').rstrip('.')
    return _svg(cls, '0 0 120 170', width, round(width * 170 / 120), _draw(ARCH_FRAME), sw)


def dotted_rule(cls='mark mark-dots'):
    """Round dots at a steady 8px pitch at any width (the dashes are laid out in screen space)."""
    return _svg(cls, '0 0 240 6', 240, 6,
                '<path d="M3,3H237" stroke-dasharray="0 8" vector-effect="non-scaling-stroke"/>', 2.2,
                stretch=True)


def divider(cls='mark mark-divider'):
    body = (_draw('M107.5,15.2H132.5', 0) +
            '<g stroke-width="1">' + _draw('M99,15.1C72,15.3 40,14.8 10,15.1', 1) +
            _draw('M141,15.1C168,14.9 200,15.3 230,15', 1) + '</g>' +
            _draw('M110.5,20.4q4.8,-2.4 9.6,0t9.6,0', 2, ' stroke-width="1.2"') +
            '<path class="sc-sun" d="M113,15.2a7,7 0 0 1 14,0Z" fill="currentColor" stroke="none"/>')
    return _svg(cls, '0 0 240 24', 240, 24, body, 1.6)


MARKS = {
    'underline-1': lambda cls='mark mark-underline': underline(1, cls),
    'underline-2': lambda cls='mark mark-underline': underline(2, cls),
    'underline-3': lambda cls='mark mark-underline': underline(3, cls),
    'ellipse': ellipse,
    'swash': swash,
    'sun_arc': sun_arc,
    'sprig-1': lambda cls='mark mark-sprig': sprig(1, cls),
    'sprig-2': lambda cls='mark mark-sprig': sprig(2, cls),
    'quote_mark': quote_mark,
    'arch_frame': arch_frame,
    'dotted_rule': dotted_rule,
    'divider': divider,
}
