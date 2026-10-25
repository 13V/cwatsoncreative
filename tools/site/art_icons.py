# Sunday Light icon set: bespoke 24x24 monoline icons, stroke 1.3, round caps and joins, drawn to sit
# beside Jost text and Cormorant headings. Lines carry a little hand in them (gentle bows, uneven corner radii,
# circles that are not quite round) so they read as pen marks, not UI-kit glyphs.
#
#   from art_icons import ICON_PATHS, sprite, icon, icon_inline, ARROW_INLINE
#   sprite()                      -> one hidden <svg> of <symbol id="i-NAME">; put it once, early in <body>
#   icon('chevron-right')         -> <svg class="icon icon-chevron-right" ...><use href="#i-chevron-right"/></svg>
#   icon('close', label='Close')  -> the same with role="img" and aria-label
#   icon_inline('sun')            -> the icon as a full inline <svg>, for when its strokes should draw themselves
#   ARROW_INLINE                  -> the arrow inline, shaft and head as separate path.draw elements
#
# Every stroke is a <path class="draw" pathLength="1" style="--d:N">, N being its place in the drawing order,
# so CSS can draw any icon on (stroke-dasharray: 1; stroke-dashoffset: 1 -> 0). The markup itself is the
# finished, static drawing. The sprite leaves those draw hooks out: CSS matches <use> copies against the
# symbol's own elements, so a page-wide `.draw` rule would otherwise hide every sprite icon for good. Icons
# drawn through <use> are therefore static and take their colour from `color`; for strokes that draw
# themselves or move on hover, use icon_inline() or ARROW_INLINE.
#
# ARROW_INLINE hover, for example (the head slides out as the shaft grows; the svg has overflow="visible"):
#   .arrow-shaft, .arrow-head { transform-box: fill-box; transition: transform .5s cubic-bezier(.2,.7,.2,1); }
#   .arrow-shaft { transform-origin: 0 50%; }
#   a:hover .arrow-shaft { transform: scaleX(1.3); }      /* the shaft is 18 units: 1.3 adds 5.4 */
#   a:hover .arrow-head  { transform: translateX(5.4px); }  /* px inside an svg are user units */
import re
from html import escape

STROKE = 'fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"'

ICON_PATHS = {
    # long-tailed editorial arrow: an 18-unit shaft and a small, swept open head
    'arrow': (
        '<path class="draw" pathLength="1" style="--d:0" d="M3 12.1Q12 11.8 21 12"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M17.4 8.8Q19.5 11 21 12Q19.5 13 17.4 15.1"/>'),
    # the arrow, shorter and turned 45 degrees, for links that leave the site
    'arrow-up-right': (
        '<path class="draw" pathLength="1" style="--d:0" d="M7.3 16.9Q12.1 11.7 17.2 6.8"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M12.2 6.7Q15.4 7 17.2 6.8Q17 8.6 17.3 11.7"/>'),
    # chevrons share the arrow head's gentle sweep
    'chevron-left': '<path class="draw" pathLength="1" style="--d:0" d="M14.4 5.3Q11.2 9.5 8.8 12Q11.2 14.5 14.5 18.6"/>',
    'chevron-right': '<path class="draw" pathLength="1" style="--d:0" d="M9.6 5.3Q12.8 9.5 15.2 12Q12.8 14.5 9.7 18.6"/>',
    'chevron-down': '<path class="draw" pathLength="1" style="--d:0" d="M5.3 9.6Q9.5 12.8 12 15.2Q14.5 12.8 18.6 9.5"/>',
    # two strokes that bow very slightly, as a pen would cross them
    'close': (
        '<path class="draw" pathLength="1" style="--d:0" d="M6.3 6.2Q12.4 11.6 17.8 17.7"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M17.7 6.3Q11.7 11.8 6.2 17.8"/>'),
    'plus': (
        '<path class="draw" pathLength="1" style="--d:0" d="M12 5Q12.4 12 12.1 19"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M5 12.1Q12 11.7 19 11.9"/>'),
    'minus': '<path class="draw" pathLength="1" style="--d:0" d="M5 12.1Q12 11.7 19 11.9"/>',
    # two lines of unequal length
    'menu': (
        '<path class="draw" pathLength="1" style="--d:0" d="M4 9.1Q12 8.9 20 9"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M4 15Q9.1 14.8 14.2 14.9"/>'),
    # a small sun rising over a line, with an up tick
    'back-to-top': (
        '<path class="draw" pathLength="1" style="--d:0" d="M3.6 18.8Q12 18.6 20.4 18.7"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M7.5 18.8C7.5 16.3 9.6 14.4 12 14.4C14.4 14.4 16.6 16.2 16.6 18.8"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M9.1 9.9Q11 8.3 12 7.2Q13 8.3 14.9 9.9"/>'),
    # rounded square, lens, dot
    'instagram': (
        '<path class="draw" pathLength="1" style="--d:0" d="M8.6 3.5Q12.2 3.3 15.7 3.5C18.4 3.5 20.6 5.7 20.6 8.4Q20.7 11.9 20.6 15.4C20.6 18.2 18.3 20.5 15.5 20.5Q11.9 20.7 8.2 20.5C5.5 20.5 3.4 18.4 3.4 15.7Q3.2 12.2 3.4 8.7C3.4 5.8 5.7 3.5 8.6 3.5Z"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M10 8.5C11.9 7.4 14.4 7.9 15.6 9.9C16.7 11.9 15.8 14.3 14 15.4C12.1 16.5 9.6 16 8.4 14.1C7.3 12.1 8.1 9.6 10 8.5Z"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M16.9 7L17 7"/>'),
    'envelope': (
        '<path class="draw" pathLength="1" style="--d:0" d="M4.8 5.6Q12.1 5.4 19.3 5.6C20.2 5.6 21 6.4 21 7.3Q20.9 12.1 21 16.8C21 17.8 20.2 18.6 19.2 18.6Q11.9 18.8 4.7 18.6C3.8 18.6 3 17.8 3 16.9Q2.9 12.2 3 7.4C3 6.4 3.8 5.6 4.8 5.6Z"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M3.7 7.3Q8.4 11.2 12 13Q15.6 11.2 20.3 7.2"/>'),
    # with one day marked
    'calendar': (
        '<path class="draw" pathLength="1" style="--d:0" d="M5.6 5.6Q12.1 5.4 18.5 5.6C19.6 5.6 20.5 6.5 20.5 7.6Q20.4 13.1 20.5 18.5C20.5 19.7 19.6 20.6 18.4 20.6Q11.9 20.8 5.4 20.6C4.4 20.6 3.5 19.7 3.5 18.7Q3.4 13.2 3.5 7.7C3.5 6.5 4.4 5.6 5.6 5.6Z"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M8 3.4Q8.1 5.5 8 7.6"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M16 3.4Q15.9 5.5 16 7.6"/>'
        '<path class="draw" pathLength="1" style="--d:3" d="M3.6 10.4Q12 10.2 20.4 10.3"/>'
        '<path class="draw" pathLength="1" style="--d:4" d="M16 15.4C16 15.7 15.7 16 15.4 16C15.1 16 14.8 15.7 14.8 15.4C14.8 15.1 15.1 14.8 15.4 14.8C15.7 14.8 16 15.1 16 15.4Z"/>'),
    'clock': (
        '<path class="draw" pathLength="1" style="--d:0" d="M11.3 3.6C15.9 3.2 20.3 6.4 20.7 11.2C21.1 16.1 17.4 20.1 12.7 20.5C8 20.9 3.8 17.5 3.3 12.8C2.9 8 6.6 4 11.3 3.6Z"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M12 7.2Q12.1 9.7 12 12.1Q13.6 13.2 15.3 14"/>'),
    # a soft teardrop
    'pin': (
        '<path class="draw" pathLength="1" style="--d:0" d="M12 21C10.6 19.6 5.6 14.6 5.6 9.8C5.5 6.2 8.5 3.5 12 3.5C15.5 3.4 18.4 6.2 18.4 9.8C18.4 14.6 13.4 19.6 12 21Z"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M11.2 7.6C12.4 7.1 13.8 7.7 14.3 9C14.8 10.2 14 11.6 12.8 12C11.6 12.5 10.2 11.9 9.7 10.6C9.2 9.4 10 8 11.2 7.6Z"/>'),
    # a little film SLR: raised prism, lens, finder dot
    'camera': (
        '<path class="draw" pathLength="1" style="--d:0" d="M3.2 9.4C3.2 8.3 3.9 7.6 5 7.6Q6.6 7.5 8.3 7.5L9.5 5.3Q12 5.2 14.5 5.3L15.7 7.5Q17.4 7.5 19 7.6C20.1 7.6 20.8 8.3 20.8 9.4Q20.6 13.4 20.8 17.3C20.8 18.4 20.1 19.1 19 19.1Q12 19 5 19.1C3.9 19.1 3.2 18.4 3.2 17.3Q3.4 13.4 3.2 9.4Z"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M11.4 9.7C13.3 9.4 15.3 10.6 15.6 12.6C16 14.6 14.5 16.3 12.6 16.7C10.7 17 8.7 15.8 8.4 13.8C8 11.8 9.5 10.1 11.4 9.7Z"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M17.4 10.2L17.5 10.2"/>'),
    # two frames, the front one holding a hill and a sun
    'gallery': (
        '<path class="draw" pathLength="1" style="--d:0" d="M7.6 7.9L7.6 5.2C7.6 4.2 8.3 3.5 9.3 3.5Q14.1 3.4 18.9 3.5C19.9 3.5 20.6 4.2 20.6 5.2Q20.5 10 20.6 14.8C20.6 15.8 19.9 16.5 18.9 16.5L16.6 16.5"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M5 8Q10 7.9 15 8C15.8 8 16.5 8.7 16.5 9.5Q16.4 14.2 16.5 19C16.5 19.9 15.8 20.6 14.9 20.6Q9.9 20.7 4.9 20.6C4.1 20.6 3.4 19.9 3.4 19.1Q3.3 14.4 3.4 9.6C3.4 8.7 4.1 8 5 8Z"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M3.4 17.6C5.6 15.4 8.2 14.9 10.4 16.2C12.3 17.3 14.4 16.4 16.5 14.9"/>'
        '<path class="draw" pathLength="1" style="--d:3" d="M9.5 12.3C9.5 13 8.9 13.6 8.2 13.6C7.5 13.6 6.9 13 6.9 12.3C6.9 11.6 7.5 11 8.2 11C8.9 11 9.5 11.6 9.5 12.3Z"/>'),
    # a low sun, half set on the horizon, with three short rays
    'sun': (
        '<path class="draw" pathLength="1" style="--d:0" d="M2.8 17.1Q12 16.8 21.2 16.9"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M6.8 17C6.8 14.1 9.2 11.9 12 11.9C14.8 11.9 17.3 14.1 17.3 17"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M6.2 12.4L4.5 11.2"/>'
        '<path class="draw" pathLength="1" style="--d:3" d="M12 9.6L12.1 7.2"/>'
        '<path class="draw" pathLength="1" style="--d:4" d="M17.8 12.4L19.4 11.2"/>'),
    # the logo window with the sun inside
    'arch': (
        '<path class="draw" pathLength="1" style="--d:0" d="M6.1 21Q5.9 14.9 6.1 8.8C6 5.5 8.8 3 12 3C15.2 3 18 5.5 18 8.8Q18.1 14.9 17.9 21Q12 21.2 6.1 21Z"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M9.1 16.2C8.7 15 9.2 13.8 10.1 13.1C11.1 12.3 12.3 12.2 13.4 12.8C14.4 13.3 15.1 14.4 15 15.6"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M6.1 17.3C9.4 15.2 13.2 16.6 17.9 14.9"/>'),
    # the logo wave, with a shorter echo below
    'wave': (
        '<path class="draw" pathLength="1" style="--d:0" d="M2.8 13.2Q4.6 11.4 6.5 13.2Q8.3 15 10.2 13.2Q12 11.3 13.8 13.2Q15.7 15.1 17.5 13.2Q19.4 11.2 21.2 13.2"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M6.4 17.1Q8.3 15.7 10.1 17.1Q12 18.5 13.9 17.1Q15.7 15.7 17.6 17.1"/>'),
    # the logo's far and near hills
    'hills': (
        '<path class="draw" pathLength="1" style="--d:0" d="M2.6 12.8C5.4 9.4 8.6 7.6 11.4 7.8C14.2 8 16.3 10.4 17.7 13.7"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M2.6 18.4C6.4 15.4 10.6 13.6 14.8 13.4C17.6 13.3 19.8 14.4 21.4 15.8"/>'),
    # an olive / saltbush sprig: stem and five leaves
    'leaf': (
        '<path class="draw" pathLength="1" style="--d:0" d="M6.4 20.8C8.6 16.8 11.6 11 16.4 6.2"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M7.8 18.2C9.6 19.6 12.2 17.9 12.9 15.4C10.9 15 8.1 16 7.8 18.2Z"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M9.3 15.6C11.2 14.4 10.7 11.5 9.1 9.9C7.6 11.7 7.3 14.7 9.3 15.6Z"/>'
        '<path class="draw" pathLength="1" style="--d:3" d="M11.2 12.6C12.9 13.9 15.3 12.4 16 10.1C14.2 9.6 11.5 10.5 11.2 12.6Z"/>'
        '<path class="draw" pathLength="1" style="--d:4" d="M13.2 9.8C15.2 9.1 15.3 6.3 14.1 4.6C12.3 5.9 11.6 8.6 13.2 9.8Z"/>'
        '<path class="draw" pathLength="1" style="--d:5" d="M16.4 6.2C18.4 6.8 19.7 4.6 19.4 2.4C17.6 2.7 15.7 4.3 16.4 6.2Z"/>'),
    # one stroke from the cusp: round lobes easing in to a fine point
    'heart': '<path class="draw" pathLength="1" style="--d:0" d="M12 8.4C11.2 6 8.9 4.6 6.7 5.1C4.2 5.7 3.2 8.4 4.2 11C5.6 14.4 9.4 16.6 12 19.8C14.5 16.7 18.6 14.3 19.8 10.9C20.7 8.2 19.6 5.6 17.2 5.1C15 4.6 12.8 6 12 8.4Z"/>',
}


_DRAW_HOOKS = re.compile(r' class="draw" pathLength="1" style="--d:\d+"')


def sprite():
    """One hidden <svg> holding a <symbol id="i-NAME"> per icon. Include it once per page, before any icon()."""
    symbols = ''.join('<symbol id="i-%s" viewBox="0 0 24 24" %s>%s</symbol>' % (name, STROKE, _DRAW_HOOKS.sub('', inner))
                      for name, inner in ICON_PATHS.items())
    return ('<svg class="icon-sprite" aria-hidden="true" focusable="false" '
            f'style="position:absolute;width:0;height:0;overflow:hidden">{symbols}</svg>')


def _open(name, cls, label):
    if name not in ICON_PATHS:
        raise KeyError(f'unknown icon {name!r}')
    classes = ' '.join(dict.fromkeys(['icon', f'icon-{name}'] + (cls or '').split()))
    aria = f'role="img" aria-label="{escape(label)}"' if label else 'aria-hidden="true" focusable="false"'
    return f'<svg class="{classes}" viewBox="0 0 24 24" {aria}'


def icon(name, cls='icon', label=None):
    """<svg class="icon icon-NAME [cls]"><use href="#i-NAME"/></svg>, decorative unless label is given."""
    return f'{_open(name, cls, label)}><use href="#i-{name}"/></svg>'


def icon_inline(name, cls='icon', label=None):
    """The icon as a self-contained inline <svg>, its strokes reachable by CSS (for draw-on and hover motion)."""
    return f'{_open(name, cls, label)} {STROKE}>{ICON_PATHS[name]}</svg>'


# The arrow for links whose arrow line extends on hover: shaft and head are separate, classed strokes.
ARROW_INLINE = ('<svg class="icon icon-arrow arrow-inline" viewBox="0 0 24 24" overflow="visible" '
                f'aria-hidden="true" focusable="false" {STROKE}>'
                '<path class="draw arrow-shaft" pathLength="1" style="--d:0" d="M3 12.1Q12 11.8 21 12"/>'
                '<path class="draw arrow-head" pathLength="1" style="--d:1" d="M17.4 8.8Q19.5 11 21 12Q19.5 13 17.4 15.1"/></svg>')
