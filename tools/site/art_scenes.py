"""Sunday Light: illustrated scenes in the logo's style. Flat palette shapes, a few monoline accents.

Every function returns one inline <svg> string (placeholder_svg() returns a whole .svg file). All of it is
decorative: aria-hidden, no <title>. The markup is the finished, fully drawn, still state. Motion is added by CSS.

Hooks for the motion layer:
- path.draw has pathLength="1" and style="--d:n", n being its place in the drawing order (0 first; paths that
  share an n draw together). Strokes are round-capped and round-joined from the <svg> down.
- Pieces that move as a unit carry a class: .sc-sun (a <g> in horizon(), so the sun and its pencil ring sink
  together; a <circle> elsewhere), .sc-hill-far, .sc-hill-mid, .sc-hill-near, .sc-wave, .sc-arch, .sc-sprig.
  Hills are closed bands that run to the bottom edge, so transform-box: fill-box with transform-origin 50% 100%
  lifts them from the ground. The sun's box is the sun itself.
- arch_scene() and tier_sun() clip the sun inside the arch, so it can rise or set without leaving the window.

    from art_scenes import horizon, arch_scene, menu_vignette, tier_sun, placeholder_svg, SCENES
"""
from html import escape

PAPER, LIME, PADDOCK, BARK, GULF = '#F6F2EA', '#ECE6DB', '#C3964F', '#5C4D3F', '#A7BBC3'
FAR_HILL, SALTBUSH, DEEP_BUSH, BUSH_INK = '#C1C3B2', '#8B937A', '#737C64', '#5F6752'

_ATTRS = ('aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" '
          'stroke-linecap="round" stroke-linejoin="round"')


def _svg(cls, w, h, body, slice_=False):
    par = ' preserveAspectRatio="xMidYMax slice"' if slice_ else ''
    return (f'<svg class="{escape(cls)}" viewBox="0 0 {w} {h}" width="{w}" height="{h}"{par} {_ATTRS}>'
            f'{body}</svg>')


def _draw(d, n, stroke, sw, cls=''):
    c = f'draw {cls}' if cls else 'draw'
    return (f'<path class="{c}" pathLength="1" style="--d:{n}" d="{d}" fill="none" stroke="{stroke}" '
            f'stroke-width="{sw}"/>')


def _sprig(x, y, n, stroke, sw=1.3, leaf=2.6, scale=1, flip=False, rot=0):
    """A tiny saltbush sprig standing at (x, y): the stem draws, then its leaves (short round dabs) together."""
    t = (f'translate({x} {y})' + (f' rotate({rot})' if rot else '')
         + (f' scale({-scale if flip else scale} {scale})' if scale != 1 or flip else ''))
    stems = ''.join(_draw(d, n, stroke, sw) for d in _SPRIG_STEMS)
    leaves = ''.join(_draw(d, n + 1, stroke, leaf) for d in _SPRIG_LEAVES)
    return f'<g class="sc-sprig" transform="{t}">{stems}{leaves}</g>'


# A sprig drawn standing on (0, 0), about 27 units tall: one stem arching a little to the right, and the
# saltbush's small rounded leaves as grease-pencil dabs, alternating up the stem and getting smaller.
_SPRIG_STEMS = ('M0,0C-0.5,-8.2 0.7,-16.4 3.1,-25.2',)
_SPRIG_LEAVES = (
    'M-0.2,-4.4q-1.7,-0.5 -3.6,-3.5', 'M0.1,-8.4q1.9,-0.4 3.7,-3.5', 'M0.4,-12.4q-1.6,-0.6 -3.1,-3.5',
    'M1,-15.9q1.6,-0.3 3.1,-3.1', 'M1.6,-19.3q-1.3,-0.6 -2.4,-3.1', 'M2.3,-22.3q1.2,-0.3 2.2,-2.5',
    'M3.1,-25.2q0.3,-1.4 0.2,-2.6',
)


# --- horizon: the footer scene --------------------------------------------------------------------------
_HZ_FAR = ('M0,150C50,143.7 100,135.7 150,131C200,126.3 246.7,120.5 300,122C353.3,123.5 410,131.7 470,140'
           'C530,148.3 595,163.8 660,172C725,180.2 796.7,189.3 860,189C923.3,188.7 976.7,178.7 1040,170'
           'C1103.3,161.3 1173.3,139.7 1240,137C1306.7,134.3 1373.3,148.3 1440,154V260H0Z')
_HZ_MID = ('M0,213C80,208.3 161.7,198.8 240,199C318.3,199.2 390,209.7 470,214C550,218.3 640,226 720,225'
           'C800,224 873.3,216.2 950,208C1026.7,199.8 1116.7,182.3 1180,176C1243.3,169.7 1286.7,169.8 1330,170'
           'C1373.3,170.2 1403.3,174.7 1440,177V260H0Z')
_HZ_NEAR = ('M0,200C43.3,198 80,192.7 130,194C180,195.3 238.3,201.7 300,208C361.7,214.3 433.3,226.2 500,232'
            'C566.7,237.8 625,240.7 700,243C775,245.3 870,246.5 950,246C1030,245.5 1116.7,242.3 1180,240'
            'C1243.3,237.7 1286.7,232.7 1330,232C1373.3,231.3 1403.3,234.7 1440,236V260H0Z')
# a pencil ring round the top of the sun, not quite concentric, open at both ends
_HZ_RING = ('M768.2,165.2C777,147.9 781.6,126.5 794.6,113.4C807.7,100.3 828.1,90.2 846.6,86.4'
            'C865.1,82.5 888,83.6 905.6,90.5C923.2,97.4 936.7,115.4 952.2,127.8')
_HZ_WAVES = (
    'M708,253q14.2,-6.7 28.4,0.2q13.8,6.2 27.7,-0.1q14.1,-6 28.2,0.3q13.8,6.6 27.5,-0.2q14.2,-6.5 28.3,0'
    'q14.1,6.1 28.1,0.1q14.2,-6.7 28.4,0.2q13.8,6.2 27.7,-0.1',
    'M1236,248q12.8,-5.6 25.7,-0.1q13.1,5.4 26.2,0.3q12.8,-6 25.5,-0.2q13.2,5.9 26.3,0q13.1,-5.5 26.1,0.1'
    'q13.2,6.1 26.4,0.2',
)


def horizon(cls='horizon', uid='ft'):
    """The footer scene, 1440 x 260, sliced from the bottom centre. The sun sits 60% from the left so a phone's
    centre crop keeps it. uid prefixes the two gradient ids (pass another one if the scene appears twice)."""
    g = f'hz-{escape(uid)}'
    body = (f'<defs><linearGradient id="{g}-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{LIME}"/>'
            f'<stop offset=".78" stop-color="{PAPER}"/></linearGradient>'
            f'<radialGradient id="{g}-glow" cx="866" cy="186" r="340" gradientUnits="userSpaceOnUse" '
            f'gradientTransform="matrix(1 0 0 .5 0 93)"><stop offset="0" stop-color="#E7C38C" stop-opacity=".6"/>'
            f'<stop offset="1" stop-color="#E7C38C" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="1440" height="260" fill="url(#{g}-sky)"/><rect width="1440" height="260" fill="url(#{g}-glow)"/>'
            f'<g class="sc-sun"><circle cx="866" cy="186" r="88" fill="{PADDOCK}"/>'
            f'{_draw(_HZ_RING, 0, PADDOCK, 2.2)}</g>'
            f'<path class="sc-hill-far" d="{_HZ_FAR}" fill="{FAR_HILL}"/>'
            f'<path class="sc-hill-mid" d="{_HZ_MID}" fill="{SALTBUSH}"/>'
            f'<path class="sc-hill-near" d="{_HZ_NEAR}" fill="{DEEP_BUSH}"/>'
            + ''.join(_draw(d, i + 1, GULF, 3, 'sc-wave') for i, d in enumerate(_HZ_WAVES))
            + _sprig(146, 196, 3, BUSH_INK, scale=1.15, rot=-4) + _sprig(156, 196.5, 3, BUSH_INK, scale=.75, flip=True, rot=14)
            + _sprig(176, 197, 3, BUSH_INK, scale=.6, rot=10) + _sprig(560, 238, 5, BUSH_INK, rot=-3))
    return _svg(cls, 1440, 260, body, slice_=True)


# --- arch_scene: the logo's window, large, for the form's thank-you and the 404 ---------------------------
_AS_ARCH = ('M30.3,232C30,188 29.7,141 30,100C30.2,61.2 61.5,29.8 100,30C138.7,30.2 170,61.6 170,100.2'
            'C170.2,141 169.8,188 170.1,232')
_AS_GROUND = 'M11,232.6C52,231.7 104,232.9 147,232.2C163,231.9 178,232.1 189,231.5'
_AS_FAR = 'M25,185C58,160 102,164.5 132,154C148,148.5 161,145 175,141.5V240H25Z'
_AS_NEAR = 'M25,205C70,184.5 118,203 148,191C158,187 166,183.6 175,182V240H25Z'
_AS_WAVE = 'M47.5,219.5q11.3,-6.4 22.6,0.1q11.2,6.1 22.4,-0.1q11.4,-6.2 22.5,0.2q11.1,6.3 22.4,-0.2q11.3,-6 22.6,0'


def arch_scene(cls='arch-scene', uid='a'):
    """The logo's arch window at 200 x 250: Bark outline on a ground line, a warm sky, the sun (clipped inside,
    free to rise or set), two hills and the gulf. uid prefixes the clip and gradient ids."""
    g = f'as-{escape(uid)}'
    body = (f'<defs><clipPath id="{g}-clip"><path d="{_AS_ARCH}Z"/></clipPath>'
            f'<linearGradient id="{g}-sky" x1="0" y1="0" x2="0" y2="1"><stop offset=".1" stop-color="{LIME}"/>'
            f'<stop offset=".7" stop-color="#F3E6D3"/></linearGradient></defs>'
            f'<g clip-path="url(#{g}-clip)"><rect x="20" y="20" width="160" height="220" fill="url(#{g}-sky)"/>'
            f'<circle class="sc-sun" cx="100" cy="162" r="37" fill="{PADDOCK}"/>'
            f'<path class="sc-hill-far" d="{_AS_FAR}" fill="{FAR_HILL}"/>'
            f'<path class="sc-hill-near" d="{_AS_NEAR}" fill="{SALTBUSH}"/>'
            f'{_draw(_AS_WAVE, 2, GULF, 3.6, "sc-wave")}</g>'
            f'{_draw(_AS_GROUND, 0, BARK, 3)}{_draw(_AS_ARCH, 1, BARK, 4, "sc-arch")}')
    return _svg(cls, 200, 250, body)


# --- menu_vignette: the foot of the phone menu ----------------------------------------------------------
_MV_FAR = 'M0,92C30,88 70,79 112,80C160,81 196,97 236,97C276,97 300,84 334,83C358,82.4 378,86 390,89V120H0Z'
_MV_NEAR = 'M0,111C26,107 58,102 94,103C140,104 168,111 206,110C250,109 272,100 312,100C346,100 372,104 390,106V120H0Z'
_MV_WAVE = 'M168,114q8,-4.2 16,0.1q8,4 16,-0.1q8.1,-4.1 16.1,0.1q7.9,4.2 15.9,-0.1q8,-4 16,0'


def menu_vignette(cls='menu-vignette'):
    """A light sun-and-hills strip, 390 x 120, for the bottom of the phone menu. Sliced from the bottom centre."""
    body = (f'<circle class="sc-sun" cx="236" cy="96" r="30" fill="{PADDOCK}"/>'
            f'<path class="sc-hill-far" d="{_MV_FAR}" fill="#D6D6C9"/>'
            f'<path class="sc-hill-near" d="{_MV_NEAR}" fill="#B5BAA5"/>'
            f'{_draw(_MV_WAVE, 0, GULF, 2.2, "sc-wave")}')
    return _svg(cls, 390, 120, body, slice_=True)


# --- tier_sun: how long the day runs, for the wedding package cards --------------------------------------
_TS_ARCH = 'M4.2,46V30C4,14.6 16.6,2.1 32,2C47.5,2 60,14.5 59.9,30V46Z'
_TS_FAR = 'M4,37.5C14,33.5 24,35.8 35,34.2C45,32.8 53,30.8 60,30.6V48H4Z'
_TS_NEAR = 'M4,42C14,39.2 23,41.6 34,40.2C44,38.9 52,37.6 60,37.4V48H4Z'
_TS_WAVE = 'M14,44.2q3,-1.7 6,0q3,1.7 6,0q3,-1.7 6,0q3,1.7 6,0'
_TS_HEIGHT = {4: 35, 6: 29.5, 8: 24, 10: 18.5, 12: 13}


def tier_sun(hours, cls='tier-sun', uid=None):
    """A small arch of sky, 64 x 48, with the sun as high as the package is long: 4 hours sits on the hills,
    12 hours is high in the arch. Other hour counts fall in between. uid defaults to the hours."""
    h = max(4, min(12, float(hours)))
    lo = max(k for k in _TS_HEIGHT if k <= h)
    hi = min(k for k in _TS_HEIGHT if k >= h)
    cy = _TS_HEIGHT[lo] if lo == hi else _TS_HEIGHT[lo] + (_TS_HEIGHT[hi] - _TS_HEIGHT[lo]) * (h - lo) / (hi - lo)
    g = f'ts-{escape(str(uid if uid is not None else hours))}'
    body = (f'<defs><clipPath id="{g}"><path d="{_TS_ARCH}"/></clipPath></defs>'
            f'<g clip-path="url(#{g})"><rect x="2" y="0" width="60" height="48" fill="{LIME}"/>'
            f'<circle class="sc-sun" cx="32" cy="{cy:g}" r="6" fill="{PADDOCK}"/>'
            f'<path class="sc-hill-far" d="{_TS_FAR}" fill="{FAR_HILL}"/>'
            f'<path class="sc-hill-near" d="{_TS_NEAR}" fill="{SALTBUSH}"/>'
            f'{_draw(_TS_WAVE, 1, GULF, 1.3, "sc-wave")}</g>'
            f'{_draw(_TS_ARCH, 0, BARK, 1.5, "sc-arch")}')
    return _svg(f'{cls} {cls}--{hours:g}' if isinstance(hours, (int, float)) else cls, 64, 48, body)


# --- placeholder_svg: images/placeholder.svg ------------------------------------------------------------
_PH_ARCH = 'M86,600V330C86,267 137,216 200,216C263,216 314,267 314,330V600'
_PH_FAR = 'M0,436C40,424 84,410 130,410C176,410 204,428 240,428C278,428 300,406 340,404C364,403 384,407 400,411V600H0Z'
_PH_MID = 'M0,480C44,468 96,458 150,459C214,460 246,481 296,481C336,481 370,468 400,463V600H0Z'
_PH_NEAR = 'M0,538C34,528 76,520 118,521C170,522 206,540 256,540C310,540 356,524 400,518V600H0Z'
_PH_WAVE = 'M120,566q12,-6.5 24,0.1q12,6.3 24,-0.1q12.1,-6.4 24.1,0.2q11.9,6.4 23.9,-0.2q12,-6.2 24,0q12,6.4 24,0'


def placeholder_svg():
    """The contents of images/placeholder.svg: an arch window onto a soft sundown, for photo slots whose picture
    has not arrived. Portrait 2:3, sliced from the bottom centre, so square and 4:5 crops keep the whole arch."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" preserveAspectRatio="xMidYMax slice">'
            '<defs><linearGradient id="ph-sky" x1="0" y1="0" x2="0" y2="1"><stop offset=".2" stop-color="#F3EDE3"/>'
            '<stop offset=".72" stop-color="#EFDCC3"/></linearGradient>'
            f'<clipPath id="ph-win"><path d="{_PH_ARCH}Z"/></clipPath>'
            '<filter id="ph-grain" x="0" y="0" width="1" height="1"><feTurbulence type="fractalNoise" baseFrequency=".85" '
            'numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .36 0 0 0 0 .3 0 0 0 0 .25 0 0 0 1 0"/>'
            '</filter></defs>'
            '<rect width="400" height="600" fill="#EEE6D8"/>'
            '<g clip-path="url(#ph-win)"><rect y="200" width="400" height="400" fill="url(#ph-sky)"/>'
            f'<circle cx="236" cy="420" r="50" fill="{PADDOCK}" fill-opacity=".8"/>'
            f'<path d="{_PH_FAR}" fill="#D3D2C1"/><path d="{_PH_MID}" fill="{FAR_HILL}"/>'
            f'<path d="{_PH_NEAR}" fill="#A9AE98"/>'
            f'<path d="{_PH_WAVE}" fill="none" stroke="{GULF}" stroke-width="3.4" stroke-linecap="round"/></g>'
            f'<path d="{_PH_ARCH}" fill="none" stroke="#B9A88F" stroke-width="2.4" stroke-linecap="round"/>'
            '<rect width="400" height="600" filter="url(#ph-grain)" opacity=".05"/></svg>\n')


SCENES = {
    'horizon': horizon,
    'arch_scene': arch_scene,
    'menu_vignette': menu_vignette,
    'tier_sun': lambda cls='tier-sun': ''.join(tier_sun(h, cls) for h in (4, 6, 8, 10, 12)),
    'placeholder_svg': placeholder_svg,
}
