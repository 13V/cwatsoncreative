"""Sunday Light: illustrated scenes in the logo's style. Flat palette shapes, a few monoline accents.

Every function returns one inline <svg> string (placeholder_svg() returns a whole .svg file). All of it is
decorative: aria-hidden, no <title>. The markup is the finished, fully drawn, still state. Motion is added by CSS.

Hooks for the motion layer:
- path.draw has pathLength="1" and style="--d:n", n being its place in the drawing order (0 first; paths that
  share an n draw together). Strokes are round-capped and round-joined from the <svg> down.
- Hidden state, shared by art_icons, art_marks and art_scenes:
      .draw { stroke-dasharray: 1 2; stroke-dashoffset: 1.01 }   animated to   stroke-dashoffset: 0
  It is dot-free with round caps. A plain "1" / offset 1 leaves a round-cap dot at the start of every path.
- Pieces that move as a unit carry a class: .sc-sun (a <g> in horizon(), so the disc and its three pencil rays
  sink together; a <circle> elsewhere), .sc-hill-far, .sc-hill-mid, .sc-hill-near, .sc-wave, .sc-arch, .sc-sprig,
  and .sc-ground (horizon's foot band, meant to stay still). Hills are closed bands that run to the bottom edge,
  so transform-box: fill-box with transform-origin 50% 100% lifts them from the ground. The sun's box is the sun.
- arch_scene() and tier_sun() clip the sun inside the arch, so it can rise or set without leaving the window.

Drawing conventions:
- Arch geometry: every arch here keeps the logo's semicircle-over-posts proportion (about 1.45 tall to 1 wide).
  The scene arches (arch_scene, tier_sun) carry a slight hand wobble. art_marks.arch_frame is machine-exact on
  purpose, so it sits concentric with arch-masked photos; so is the placeholder's window, which frames a photo slot.
- Suns are filled Paddock discs. horizon()'s sun adds the icon set's three short rays (38, 90 and 142 degrees).
- Plants are smaller cuts of art_marks sprig 1 (saltbush): a stem with one side shoot to the right and blunt
  leaves alternating up it at the master's angles. arch_scene() keeps the master's open-loop leaves. At
  horizon()'s tiny size the leaves become grease-pencil dabs with the same rhythm and angle.
- Waves are the logo's q/t sine family at every scale.
- Land and sky tints beyond the core palette are the named constants below, shared across the scenes.
- uid values are reduced to [A-Za-z0-9_-] before they go into ids. Pass distinct uids when a scene, or a
  same-hours tier_sun(), appears twice on one page.

    from art_scenes import horizon, arch_scene, menu_vignette, tier_sun, placeholder_svg, SCENES
"""
import re
from html import escape

# core palette
PAPER, LIME, PADDOCK, BARK, GULF = '#F6F2EA', '#ECE6DB', '#C3964F', '#5C4D3F', '#A7BBC3'
FAR_HILL, SALTBUSH, BUSH_INK = '#C1C3B2', '#8B937A', '#5F6752'
# scene tints: land from palest to deepest, then sky, then the placeholder's mat and frame
PALE_HILL = '#D1D2C3'   # far hills in the light scenes (menu, placeholder)
SOFT_BUSH = '#9DA38B'   # near hills in the light scenes
DEEP_BUSH = '#737C64'   # horizon's nearest hill
GLOW = '#E7C38C'        # the low sun's haze
WARM_SKY = '#F3E6D3'    # sky just above the hills
DUSK_SKY = '#EFDCC3'    # the placeholder's deeper sky at the horizon
MAT = '#EEE6D8'         # the placeholder's wall, also the slot's CSS background colour
PALE_BARK = '#B9A88F'   # the placeholder's window frame

_ATTRS = ('aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" '
          'stroke-linecap="round" stroke-linejoin="round"')


def _slug(v):
    """A value made safe for an id or a class name: 7.5 -> '7-5', 'a b' -> 'a-b'."""
    return re.sub(r'[^A-Za-z0-9_-]+', '-', str(v)).strip('-') or 'x'


def _svg(cls, w, h, body, slice_=False):
    par = ' preserveAspectRatio="xMidYMax slice"' if slice_ else ''
    return (f'<svg class="{escape(cls)}" viewBox="0 0 {w} {h}" width="{w}" height="{h}"{par} {_ATTRS}>'
            f'{body}</svg>')


def _draw(d, n, stroke=None, sw=None, cls=''):
    """A self-drawing stroke. stroke and sw may be left to inherit from a parent group."""
    c = f'draw {cls}' if cls else 'draw'
    paint = (f' fill="none" stroke="{stroke}"' if stroke else '') + (f' stroke-width="{sw}"' if sw else '')
    return f'<path class="{c}" pathLength="1" style="--d:{n}" d="{d}"{paint}/>'


def _sprig(x, y, n, stroke, data, sw, leaf, scale=1, flip=False, rot=0):
    """A sprig standing at (x, y): the stem and side shoot draw at n, then the leaves together at n + 1.
    The placing transform sits on an outer <g>, so a CSS transform on .sc-sprig (say, a grow from the base with
    transform-box: fill-box; transform-origin: 50% 100%) does not knock it out of place."""
    stems, leaves = data
    t = (f'translate({x} {y})' + (f' rotate({rot})' if rot else '')
         + (f' scale({-scale if flip else scale} {scale})' if scale != 1 or flip else ''))
    return (f'<g transform="{t}" fill="none" stroke="{stroke}" stroke-width="{leaf}"><g class="sc-sprig">'
            + ''.join(_draw(d, n, sw=sw) for d in stems) + ''.join(_draw(d, n + 1) for d in leaves) + '</g></g>')


# Sprig 1 (saltbush) cut down from art_marks: stem, side shoot, then seven leaves from the bottom up (left,
# right, left, the shoot's tip, left, right, the top bud). Both stand on (0, 0).
# About 41 units tall, with the master's open-loop leaves on short stalks: for arch_scene.
_SPRIG_LOOPS = (
    ('M0,0C-1.4,-10.3 0.7,-22.6 -1.2,-35.2', 'M-0.5,-14.6C2.3,-18.4 5.6,-20.7 7.5,-26.4'),
    ('M-0.4,-4.1L-1,-4.5C-0.4,-7.5 -4.8,-9.9 -6.9,-8.4C-7.3,-5.8 -3.3,-2.7 -1,-4.5',
     'M-0.5,-8.4L0,-8.9C2.6,-7.5 5.8,-10.9 4.9,-13.3C2.6,-14.3 -1.2,-11.5 0,-8.9',
     'M-0.5,-12.9L-0.9,-13.4C0.2,-15.9 -3.2,-19.1 -5.5,-18.2C-6.3,-16.1 -3.4,-12.3 -0.9,-13.4',
     'M7.5,-26.4L7.8,-26.8C9.8,-26.5 11.2,-29.5 10.1,-30.8C8.4,-31 6.4,-28.2 7.8,-26.8',
     'M-0.4,-18.9L-0.8,-19.3C0.2,-21.7 -3,-24.3 -5,-23.3C-5.7,-21.3 -3,-18.1 -0.8,-19.3',
     'M-0.4,-24L-0.1,-24.5C2.3,-24.3 3.9,-27.9 2.5,-29.5C0.5,-29.6 -1.8,-26.2 -0.1,-24.5',
     'M-1.2,-35.2L-1.1,-35.7C0.8,-36.4 0.7,-39.9 -0.9,-40.7C-2.5,-40 -3,-36.5 -1.1,-35.7'),
)
# About 27 units tall, the leaves as short dabs at the same places and angles: for horizon.
_SPRIG_DABS = (
    ('M0,0C-0.9,-6.8 0.5,-14.9 -0.8,-23.2', 'M-0.3,-9.6C1.6,-12.1 3.7,-13.7 5,-17.4'),
    ('M-1.7,-3.6Q-3,-5.3 -5,-5.8', 'M0.8,-6.6Q1.8,-8.3 3.6,-9.1', 'M-1.4,-9.6Q-2.2,-11.5 -4,-12.4',
     'M5.5,-18.4Q5.8,-19.7 6.9,-20.7', 'M-1.2,-13.4Q-2,-15 -3.6,-15.7', 'M0.4,-17Q0.7,-18.7 1.9,-19.9',
     'M-0.7,-24.4Q-1.1,-25.8 -0.6,-27.2'),
)


# --- horizon: the footer scene --------------------------------------------------------------------------
_HZ_FAR = ('M0,150C50,143.7 100,135.7 150,131C200,126.3 246.7,120.5 300,122C353.3,123.5 410,131.7 470,140'
           'C530,148.3 595,163.8 660,172C725,180.2 796.7,189.3 860,189C923.3,188.7 976.7,178.7 1040,170'
           'C1103.3,161.3 1173.3,139.7 1240,137C1306.7,134.3 1373.3,148.3 1440,154V260H0Z')
_HZ_MID = ('M0,212C80,207.3 161.7,198.8 240,198C318.3,197.2 390,204.3 470,207C550,209.7 640,215.3 720,214'
           'C800,212.7 873.3,206 950,199C1026.7,192 1116.7,177.5 1180,172C1243.3,166.5 1286.7,166 1330,166'
           'C1373.3,166 1403.3,170 1440,172V260H0Z')
_HZ_NEAR = ('M0,200C43.3,198 80,193.2 130,194C180,194.8 238.3,200.7 300,205C361.7,209.3 433.3,216 500,220'
            'C566.7,224 633.3,227 700,229C766.7,231 833.3,232.2 900,232C966.7,231.8 1028.3,229.8 1100,228'
            'C1171.7,226.2 1273.3,221.7 1330,221C1386.7,220.3 1403.3,223 1440,224V260H0Z')
# the land running into the footer: 12 to 19 units tall, in the footer's own colour
_HZ_GROUND = ('M0,246C66.7,245 128.3,242.8 200,243C271.7,243.2 353.3,246.2 430,247C506.7,247.8 585,248 660,248'
              'C735,248 806.7,247.7 880,247C953.3,246.3 1030,245 1100,244C1170,243 1243.3,241.2 1300,241'
              'C1356.7,240.8 1393.3,242.3 1440,243V260H0Z')
# three short grease-pencil rays at 142, 90 and 38 degrees, the icon set's sun, each with a slight bow
_HZ_RAYS = ('M784.3,123.3Q776.4,116.3 767.6,110.5', 'M865.1,81Q864.3,69.5 864.9,58',
            'M948.5,122.7Q956.4,115.7 965.2,109.9')
_HZ_WAVES = (
    'M708,239.5q14.2,-6.7 28.4,0.2q13.8,6.2 27.7,-0.1q14.1,-6 28.2,0.3q13.8,6.6 27.5,-0.2q14.2,-6.5 28.3,0'
    'q14.1,6.1 28.1,0.1q14.2,-6.7 28.4,0.2q13.8,6.2 27.7,-0.1',
    'M1236,232.5q12.8,-5.6 25.7,-0.1q13.1,5.4 26.2,0.3q12.8,-6 25.5,-0.2q13.2,5.9 26.3,0q13.1,-5.5 26.1,0.1'
    'q13.2,6.1 26.4,0.2',
)


def horizon(cls='horizon', uid='ft', ground=LIME):
    """The footer scene, 1440 x 260, sliced from the bottom centre. The sun sits 60% from the left so a phone's
    centre crop keeps it. The sky starts transparent, so the page shows through at the top. ground is the colour
    of the footer below: the scene ends in a band of it, so the land runs into the footer (None leaves it off).
    uid prefixes the two gradient ids (pass another one if the scene appears twice)."""
    g = f'hz-{_slug(uid)}'
    body = (f'<defs><linearGradient id="{g}-sky" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset=".2" stop-color="{WARM_SKY}" stop-opacity="0"/>'
            f'<stop offset=".8" stop-color="{WARM_SKY}" stop-opacity=".9"/></linearGradient>'
            f'<radialGradient id="{g}-glow" cx="866" cy="186" r="340" gradientUnits="userSpaceOnUse" '
            f'gradientTransform="matrix(1 0 0 .5 0 93)"><stop offset="0" stop-color="{GLOW}" stop-opacity=".6"/>'
            f'<stop offset="1" stop-color="{GLOW}" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="1440" height="260" fill="url(#{g}-sky)"/><rect width="1440" height="260" fill="url(#{g}-glow)"/>'
            f'<g class="sc-sun"><circle cx="866" cy="186" r="88" fill="{PADDOCK}"/>'
            + ''.join(_draw(d, 0, PADDOCK, 2.2) for d in _HZ_RAYS) + '</g>'
            f'<path class="sc-hill-far" d="{_HZ_FAR}" fill="{FAR_HILL}"/>'
            f'<path class="sc-hill-mid" d="{_HZ_MID}" fill="{SALTBUSH}"/>'
            f'<path class="sc-hill-near" d="{_HZ_NEAR}" fill="{DEEP_BUSH}"/>'
            + (f'<path class="sc-ground" d="{_HZ_GROUND}" fill="{escape(ground)}"/>' if ground else '')
            + ''.join(_draw(d, i + 1, GULF, 3, 'sc-wave') for i, d in enumerate(_HZ_WAVES))
            + _sprig(146, 196, 3, BUSH_INK, _SPRIG_DABS, 1.3, 2.3, scale=1.15, rot=-4)
            + _sprig(159, 196.6, 3, BUSH_INK, _SPRIG_DABS, 1.3, 2.3, scale=.7, flip=True, rot=-10)
            + _sprig(560, 225, 5, BUSH_INK, _SPRIG_DABS, 1.3, 2.3, scale=.95, rot=-3))
    return _svg(cls, 1440, 260, body, slice_=True)


# --- arch_scene: the logo's window, large, for the form's thank-you and the 404 ---------------------------
# the posts end at y 231, so their round caps finish inside the 3-unit ground line
_AS_ARCH = ('M30.3,231C30,188 29.7,141 30,100C30.2,61.2 61.5,29.8 100,30C138.7,30.2 170,61.6 170,100.2'
            'C170.2,141 169.8,188 170.1,231')
_AS_GROUND = 'M11,232.6C52,231.7 104,232.9 147,232.2C163,231.9 178,232.1 189,231.5'
_AS_FAR = 'M25,185C58,160 102,164.5 132,154C148,148.5 161,145 175,141.5V240H25Z'
_AS_NEAR = 'M25,205C70,184.5 118,203 148,191C158,187 166,183.6 175,182V240H25Z'
_AS_WAVE = 'M47.5,219.5q11.3,-6.4 22.6,0.1q11.2,6.1 22.4,-0.1q11.4,-6.2 22.5,0.2q11.1,6.3 22.4,-0.2q11.3,-6 22.6,0'


def arch_scene(cls='arch-scene', uid='a', line=BARK, sprig=BUSH_INK):
    """The logo's arch window at 200 x 250: Bark outline on a ground line, a warm sky, the sun (clipped inside,
    free to rise or set), two hills and the gulf, with a saltbush sprig at its foot. uid prefixes the clip and
    gradient ids. line colours the arch and the ground, sprig the sprig (on a dark ground: PAPER and FAR_HILL)."""
    g = f'as-{_slug(uid)}'
    body = (f'<defs><clipPath id="{g}-clip"><path d="{_AS_ARCH}Z"/></clipPath>'
            f'<linearGradient id="{g}-sky" x1="0" y1="0" x2="0" y2="1"><stop offset=".1" stop-color="{LIME}"/>'
            f'<stop offset=".7" stop-color="{WARM_SKY}"/></linearGradient></defs>'
            f'<g clip-path="url(#{g}-clip)"><rect x="20" y="20" width="160" height="220" fill="url(#{g}-sky)"/>'
            f'<circle class="sc-sun" cx="100" cy="162" r="37" fill="{PADDOCK}"/>'
            f'<path class="sc-hill-far" d="{_AS_FAR}" fill="{FAR_HILL}"/>'
            f'<path class="sc-hill-near" d="{_AS_NEAR}" fill="{SALTBUSH}"/>'
            f'{_draw(_AS_WAVE, 2, GULF, 3.6, "sc-wave")}</g>'
            f'{_draw(_AS_GROUND, 0, line, 3)}{_draw(_AS_ARCH, 1, line, 4, "sc-arch")}'
            f'{_sprig(182, 232, 3, escape(sprig), _SPRIG_LOOPS, 1.7, 1.7)}')
    return _svg(cls, 200, 250, body)


# --- menu_vignette: the foot of the phone menu ----------------------------------------------------------
_MV_FAR = 'M0,92C30,88 70,79 112,80C160,81 196,97 236,97C276,97 300,84 334,83C358,82.4 378,86 390,89V120H0Z'
_MV_NEAR = 'M0,111C26,107 58,102 94,103C140,104 168,111 206,110C250,109 272,100 312,100C346,100 372,104 390,106V120H0Z'
_MV_WAVE = 'M168,114q8,-4.2 16,0.1q8,4 16,-0.1q8.1,-4.1 16.1,0.1q7.9,4.2 15.9,-0.1q8,-4 16,0'


def menu_vignette(cls='menu-vignette'):
    """A light sun-and-hills strip, 390 x 120, for the bottom of the phone menu. Sliced from the bottom centre."""
    body = (f'<circle class="sc-sun" cx="236" cy="96" r="30" fill="{PADDOCK}"/>'
            f'<path class="sc-hill-far" d="{_MV_FAR}" fill="{PALE_HILL}"/>'
            f'<path class="sc-hill-near" d="{_MV_NEAR}" fill="{SOFT_BUSH}"/>'
            f'{_draw(_MV_WAVE, 0, GULF, 2.4, "sc-wave")}')
    return _svg(cls, 390, 120, body, slice_=True)


# --- tier_sun: how long the day runs, for the wedding package cards --------------------------------------
# A small window at the logo's proportion (34 x 45), centred in the 64 x 48 box.
_TS_ARCH = 'M15.3,46.4V18.6C15.2,9.3 22.8,1.7 32.1,1.6C41.4,1.6 48.9,9.2 48.8,18.5V46.4Z'
_TS_FAR = 'M14,37C20,34.2 26,35.6 33,34.4C40,33.2 45,31.2 50,30.8V48H14Z'
_TS_NEAR = 'M14,41.8C21,39.6 27,41.4 34,40.3C41,39.2 46,37.8 50,37.6V48H14Z'
_TS_WAVE = 'M20.5,44.4q2.9,-1.6 5.8,0q2.9,1.6 5.8,0q2.9,-1.6 5.8,0q2.9,1.6 5.8,0'
_TS_HEIGHT = {4: 35.5, 6: 29.5, 8: 23.5, 10: 17.5, 12: 11.5}


def tier_sun(hours, cls='tier-sun', uid=None, line=BARK):
    """A small arched window of sky, 64 x 48, with the sun as high as the package is long: 4 hours sits on the
    hills, 12 hours is high in the arch, other counts fall in between. hours may be an int, float or numeric str.
    The <svg> gets cls plus a modifier built from cls's first class, e.g. 'tier-sun tier-sun--7-5'.
    uid defaults to the hours."""
    h = float(hours)
    key = _slug(f'{h:g}')
    h = max(4.0, min(12.0, h))
    lo = max(k for k in _TS_HEIGHT if k <= h)
    hi = min(k for k in _TS_HEIGHT if k >= h)
    cy = _TS_HEIGHT[lo] if lo == hi else _TS_HEIGHT[lo] + (_TS_HEIGHT[hi] - _TS_HEIGHT[lo]) * (h - lo) / (hi - lo)
    g = f'ts-{_slug(uid if uid is not None else key)}'
    first = cls.split()[0] if cls.split() else ''
    body = (f'<defs><clipPath id="{g}"><path d="{_TS_ARCH}"/></clipPath></defs>'
            f'<g clip-path="url(#{g})"><rect x="12" y="0" width="40" height="48" fill="{LIME}"/>'
            f'<circle class="sc-sun" cx="32" cy="{round(cy, 1):g}" r="5.4" fill="{PADDOCK}"/>'
            f'<path class="sc-hill-far" d="{_TS_FAR}" fill="{FAR_HILL}"/>'
            f'<path class="sc-hill-near" d="{_TS_NEAR}" fill="{SALTBUSH}"/>'
            f'{_draw(_TS_WAVE, 1, GULF, 1.3, "sc-wave")}</g>'
            f'{_draw(_TS_ARCH, 0, escape(line), 1.5, "sc-arch")}')
    return _svg(f'{cls} {first}--{key}' if first else cls, 64, 48, body)


# --- placeholder_svg: images/placeholder.svg and images/placeholder-wide.svg ------------------------------
# Portrait 400 x 600: the window is 252 wide, its posts run off the bottom edge.
_PH_ARCH = 'M74,600V342C74,272.4 130.4,216 200,216C269.6,216 326,272.4 326,342V600'
_PH_FAR = ('M0,452C40,448.3 80.7,446.2 120,441C159.3,435.8 201,428.3 236,421C271,413.7 302.7,402.3 330,397'
           'C357.3,391.7 376.7,391.7 400,389V600H0Z')
_PH_MID = ('M0,506C36.7,499.3 73.3,487.7 110,486C146.7,484.3 185,497.3 220,496C255,494.7 290,482.3 320,478'
           'C350,473.7 373.3,472.7 400,470V600H0Z')
_PH_NEAR = ('M0,560C36.7,554.7 71.7,544.7 110,544C148.3,543.3 193.3,556.7 230,556C266.7,555.3 301.7,543.3 330,540'
            'C358.3,536.7 376.7,537.3 400,536V600H0Z')
_PH_WAVE = 'M130,576q12.2,-6.5 24.4,0.2q11.8,6 23.7,-0.1q12.1,-5.8 24.2,0.3q11.8,6.4 23.5,-0.2q12.2,-6.3 24.3,0q12.1,5.9 24.1,0.1'
# Landscape 640 x 360: the same picture at 0.81, the window 204 wide and centred, so a 16:9 hero, a square or
# a 3:4 slot all keep the whole arch.
_PW_ARCH = 'M218,360V166C218,109.7 263.7,64 320,64C376.3,64 422,109.7 422,166V360'
_PW_FAR = ('M158.1,240.2C190.5,237.2 223.4,235.5 255.2,231.3C287.1,227.1 320.8,221 349.1,215.1'
           'C377.5,209.2 403.1,200 425.2,195.7C447.3,191.4 463,191.4 481.9,189.2V360H158.1Z')
_PW_MID = ('M158.1,283.9C187.8,278.5 217.4,269.1 247.1,267.7C276.9,266.3 307.9,276.9 336.2,275.8'
           'C364.5,274.8 392.9,264.7 417.1,261.2C441.4,257.8 460.3,256.9 481.9,254.8V360H158.1Z')
_PW_NEAR = ('M158.1,327.6C187.8,323.3 216.1,315.2 247.1,314.7C278.1,314.1 314.6,324.9 344.3,324.4'
            'C374,323.8 402.3,314.1 425.2,311.4C448.1,308.8 463,309.2 481.9,308.2V360H158.1Z')
_PW_WAVE = 'M263.3,340.6q9.9,-5.3 19.8,0.2q9.6,4.9 19.2,-0.1q9.8,-4.7 19.6,0.2q9.6,5.2 19,-0.2q9.9,-5.1 19.7,0q9.8,4.8 19.5,0.1'


def placeholder_svg(wide=False):
    """The contents of images/placeholder.svg: an arch window onto a soft sundown, for photo slots whose picture
    has not arrived. Portrait 2:3, sliced from the bottom centre, so 4:5 and square crops keep the whole arch.
    wide=True gives the landscape file (images/placeholder-wide.svg, 16:9) for the .window slots, which keeps the
    whole arch from 16:9 down to 3:4. Both carry a whisper of paper grain."""
    if wide:
        w, h, p, sky, sun, sw, wsw, freq = 640, 360, 'pw', (158, 36, 324, 324), (349.1, 214.3, 40.5), 1.8, 2.8, 1.1
        arch, far, mid, near, wave = _PW_ARCH, _PW_FAR, _PW_MID, _PW_NEAR, _PW_WAVE
    else:
        w, h, p, sky, sun, sw, wsw, freq = 400, 600, 'ph', (0, 200, 400, 400), (236, 420, 50), 2.4, 3.4, .85
        arch, far, mid, near, wave = _PH_ARCH, _PH_FAR, _PH_MID, _PH_NEAR, _PH_WAVE
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice">'
            f'<defs><linearGradient id="{p}-sky" x1="0" y1="0" x2="0" y2="1"><stop offset=".2" stop-color="{PAPER}"/>'
            f'<stop offset=".72" stop-color="{DUSK_SKY}"/></linearGradient>'
            f'<clipPath id="{p}-win"><path d="{arch}Z"/></clipPath>'
            f'<filter id="{p}-grain" x="0" y="0" width="1" height="1"><feTurbulence type="fractalNoise" '
            f'baseFrequency="{freq}" numOctaves="2" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 .36 0 0 0 0 .3 0 0 0 0 .25 0 0 0 1 0"/></filter></defs>'
            f'<rect width="{w}" height="{h}" fill="{MAT}"/>'
            f'<g clip-path="url(#{p}-win)"><rect x="{sky[0]}" y="{sky[1]}" width="{sky[2]}" height="{sky[3]}" '
            f'fill="url(#{p}-sky)"/><circle cx="{sun[0]}" cy="{sun[1]}" r="{sun[2]}" fill="{PADDOCK}"/>'
            f'<path d="{far}" fill="{PALE_HILL}"/><path d="{mid}" fill="{FAR_HILL}"/><path d="{near}" fill="{SOFT_BUSH}"/>'
            f'<path d="{wave}" fill="none" stroke="{GULF}" stroke-width="{wsw}" stroke-linecap="round"/></g>'
            f'<path d="{arch}" fill="none" stroke="{PALE_BARK}" stroke-width="{sw}" stroke-linecap="round"/>'
            f'<rect width="{w}" height="{h}" filter="url(#{p}-grain)" opacity=".05"/></svg>\n')


SCENES = {
    'horizon': horizon,
    'arch_scene': arch_scene,
    'menu_vignette': menu_vignette,
    'tier_sun': lambda cls='tier-sun': ''.join(tier_sun(h, cls) for h in (4, 6, 8, 10, 12)),
    'placeholder_svg': placeholder_svg,
    'placeholder_svg-wide': lambda: placeholder_svg(wide=True),
}
