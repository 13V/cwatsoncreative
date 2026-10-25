# Sunday Light icon set: bespoke 24x24 monoline icons, stroke 1.3, round caps and joins, drawn to sit
# beside Jost text and Cormorant headings. Lines carry a little hand in them (gentle bows, uneven corner radii,
# circles that are not quite round) so they read as pen marks, not UI-kit glyphs. Round forms (clock face,
# Instagram and camera lenses, the pin's head) close the way art_marks.ellipse does: the pencil crosses its
# start and runs on, lifting away. Chevrons, close, plus and minus stay clean.
# The arch is the logo's semicircle over straight posts with a slight hand wobble, as in art_scenes.arch_scene;
# only art_marks.arch_frame is machine-exact, because it has to sit concentric with arch-masked photos.
#
#   from art_icons import ICON_PATHS, sprite, icon, icon_inline, ARROW_INLINE
#   sprite()                      -> one hidden <svg> of <symbol id="i-NAME">; put it once, early in <body>
#   sprite(['arrow', 'close'])    -> the same holding only the icons a page uses (all of them by default)
#   icon('chevron-right')         -> <svg class="icon icon-chevron-right" ...><use href="#i-chevron-right"/></svg>
#   icon('close', label='Close')  -> the same with role="img" and aria-label
#   icon_inline('sun')            -> the icon as a full inline <svg>, for when its strokes should draw themselves
#   ARROW_INLINE                  -> the arrow inline, shaft and head as separate path.draw elements
#
# Every stroke is a <path class="draw" pathLength="1" style="--d:N">, N being its place in the drawing order.
# The markup itself is the finished, static drawing. To draw an icon on, use the recipe shared by all three art
# modules. Hidden state: stroke-dasharray: 1 2; stroke-dashoffset: 1.01. Animate stroke-dashoffset to 0.
# A plain dasharray of 1 leaves a round-cap dot on the path in Chromium; the 2-unit gap and the extra .01 hide it.
# The sprite leaves those draw hooks out: CSS matches <use> copies against the symbol's own elements, so a
# page-wide `.draw` rule would otherwise hide every sprite icon for good. Icons drawn through <use> are
# therefore static and take their colour from `color`; for strokes that draw themselves or move on hover, use
# icon_inline() or ARROW_INLINE.
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
    # two lines of unequal length, set a unit right so the pair sits optically centred in a round button
    'menu': (
        '<path class="draw" pathLength="1" style="--d:0" d="M5 9.1Q13 8.9 21 9"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M5 15Q10.1 14.8 15.2 14.9"/>'),
    # the sun icon's horizon and 90-degree ray, the ray carrying a small head
    'back-to-top': (
        '<path class="draw" pathLength="1" style="--d:0" d="M3.6 17.1Q12 16.8 20.4 16.9"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M7.1 17C7.7 14.7 9.7 13.3 12 13.3C14.2 13.2 16.3 14.7 16.9 16.9"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M12 11.9Q11.9 10.6 12.1 9.4"/>'
        '<path class="draw" pathLength="1" style="--d:3" d="M10.2 10.5Q11.2 9.9 12.1 9.4Q12.9 9.9 14 10.6"/>'),
    # rounded square, lens (closed with a pencil crossing), dot
    'instagram': (
        '<path class="draw" pathLength="1" style="--d:0" d="M8.6 3.5Q12.2 3.3 15.7 3.5C18.4 3.5 20.6 5.7 20.6 8.4Q20.7 11.9 20.6 15.4C20.6 18.2 18.3 20.5 15.5 20.5Q11.9 20.7 8.2 20.5C5.5 20.5 3.4 18.4 3.4 15.7Q3.2 12.2 3.4 8.7C3.4 5.8 5.7 3.5 8.6 3.5Z"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M9.8 8.8C11.6 7.6 14 7.8 15.4 9.6C16.8 11.4 16.1 14 14.2 15.2C12.4 16.4 9.9 16.3 8.6 14.4C7.3 12.5 7.5 9.9 9.4 8.3C9.7 8.1 10 8 10.2 7.9"/>'
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
    # the face closes as a pencil would: across its start at ten o'clock, lifting away
    'clock': (
        '<path class="draw" pathLength="1" style="--d:0" d="M7.8 4.7C11.9 2.6 17.1 3.5 19.6 7.6C22.1 11.8 20.3 17 16.2 19.3C12.2 21.7 6.9 20.4 4.5 16.3C2.1 12.2 3.2 6.6 7.5 4.2C7.8 4.1 8 3.9 8.3 3.8"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M12 7.2Q12.1 9.7 12 12.1Q13.6 13.2 15.3 14"/>'),
    # a soft teardrop, its head closed with the same pencil crossing
    'pin': (
        '<path class="draw" pathLength="1" style="--d:0" d="M8 5C9.8 3.4 12.4 2.9 14.7 4C17 5 18.4 7.3 18.4 9.8C18.4 14.6 13.4 19.6 12 21C10.6 19.6 5.6 14.6 5.6 9.8C5.6 7.6 6.4 5.3 8.3 4"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M11.2 7.6C12.4 7.1 13.8 7.7 14.3 9C14.8 10.2 14 11.6 12.8 12C11.6 12.5 10.2 11.9 9.7 10.6C9.2 9.4 10 8 11.2 7.6Z"/>'),
    # a little film SLR: raised prism, lens (pencil-closed), finder dot
    'camera': (
        '<path class="draw" pathLength="1" style="--d:0" d="M3.2 9.4C3.2 8.3 3.9 7.6 5 7.6Q6.6 7.5 8.3 7.5L9.5 5.3Q12 5.2 14.5 5.3L15.7 7.5Q17.4 7.5 19 7.6C20.1 7.6 20.8 8.3 20.8 9.4Q20.6 13.4 20.8 17.3C20.8 18.4 20.1 19.1 19 19.1Q12 19 5 19.1C3.9 19.1 3.2 18.4 3.2 17.3Q3.4 13.4 3.2 9.4Z"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M10 10.4C11.6 9.3 13.8 9.4 15 11.1C16.2 12.7 15.6 15 14 16.1C12.4 17.2 10.2 17 9 15.3C7.8 13.7 8 11.3 9.7 9.9C10 9.7 10.2 9.6 10.5 9.5"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M17.4 10.2L17.5 10.2"/>'),
    # two frames, the front one holding a hill and a sun
    'gallery': (
        '<path class="draw" pathLength="1" style="--d:0" d="M7.6 7.9L7.6 5.2C7.6 4.2 8.3 3.5 9.3 3.5Q14.1 3.4 18.9 3.5C19.9 3.5 20.6 4.2 20.6 5.2Q20.5 10 20.6 14.8C20.6 15.8 19.9 16.5 18.9 16.5L16.6 16.5"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M5 8Q10 7.9 15 8C15.8 8 16.5 8.7 16.5 9.5Q16.4 14.2 16.5 19C16.5 19.9 15.8 20.6 14.9 20.6Q9.9 20.7 4.9 20.6C4.1 20.6 3.4 19.9 3.4 19.1Q3.3 14.4 3.4 9.6C3.4 8.7 4.1 8 5 8Z"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M3.4 17.6C5.6 15.4 8.2 14.9 10.4 16.2C12.3 17.3 14.4 16.4 16.5 14.9"/>'
        '<path class="draw" pathLength="1" style="--d:3" d="M9.5 12.3C9.5 13 8.9 13.6 8.2 13.6C7.5 13.6 6.9 13 6.9 12.3C6.9 11.6 7.5 11 8.2 11C8.9 11 9.5 11.6 9.5 12.3Z"/>'),
    # a low sun, half set on the horizon, with three short rays (38, 90 and 142 degrees)
    'sun': (
        '<path class="draw" pathLength="1" style="--d:0" d="M2.8 17.1Q12 16.8 21.2 16.9"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M6.8 17C6.8 14.1 9.2 11.9 12 11.9C14.8 11.9 17.3 14.1 17.3 17"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M6.2 12.4L4.5 11.2"/>'
        '<path class="draw" pathLength="1" style="--d:3" d="M12 9.6L12.1 7.2"/>'
        '<path class="draw" pathLength="1" style="--d:4" d="M17.8 12.4L19.4 11.2"/>'),
    # the logo window: sun behind the hill line, the gulf wave in its foot
    'arch': (
        '<path class="draw" pathLength="1" style="--d:0" d="M6.1 21Q5.9 14.9 6.1 8.8C6 5.5 8.8 3 12 3C15.2 3 18 5.5 18 8.8Q18.1 14.9 17.9 21Q12 21.2 6.1 21Z"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M9.1 15.8C8.7 14.7 9.2 13.4 10.1 12.7C11 11.9 12.3 11.8 13.4 12.4C14.4 12.9 15.1 14 15 15.2"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M6.1 16.9C9.4 14.9 13.2 16.2 17.9 14.5"/>'
        '<path class="draw" pathLength="1" style="--d:3" d="M8.6 18.5q1.1-1.4 2.3 0t2.3 0t2.3 0"/>'),
    # the logo wave, with a shorter echo below
    'wave': (
        '<path class="draw" pathLength="1" style="--d:0" d="M2.8 13.2Q4.6 11.4 6.5 13.2Q8.3 15 10.2 13.2Q12 11.3 13.8 13.2Q15.7 15.1 17.5 13.2Q19.4 11.2 21.2 13.2"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M6.4 17.1Q8.3 15.7 10.1 17.1Q12 18.5 13.9 17.1Q15.7 15.7 17.6 17.1"/>'),
    # two long, low swells: the near hill crests left, the far one rises from behind it and crests right
    'hills': (
        '<path class="draw" pathLength="1" style="--d:0" d="M2.6 16C4.4 14.9 6 14.4 7.6 14.4C11.6 14.4 16.4 16.7 21.4 16.6"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M8.8 14.5C10.6 13 12.8 11.8 15.2 11.7C17.8 11.6 19.8 12.2 21.4 13.1"/>'),
    # a small art_marks sprig 2 (olive): S stem, three alternate slender leaves, then the terminal leaf
    'leaf': (
        '<path class="draw" pathLength="1" style="--d:0" d="M11.3 21.6C12.5 17.2 10.9 12.4 12.1 8.1"/>'
        '<path class="draw" pathLength="1" style="--d:1" d="M11.8 18.4C13.5 18.1 15.5 15.4 16 12.9C14.1 14.3 12.1 16.6 11.8 18.4"/>'
        '<path class="draw" pathLength="1" style="--d:2" d="M11.7 14.2C9.9 13.9 7.9 11.2 7.4 8.7C9.4 10.1 11.3 12.5 11.7 14.2"/>'
        '<path class="draw" pathLength="1" style="--d:3" d="M11.7 10C13.5 9.9 15.7 7.3 16.4 4.8C14.3 6.1 12.2 8.3 11.7 10"/>'
        '<path class="draw" pathLength="1" style="--d:4" d="M12.1 8.1C13.5 7.3 14.3 4.5 13.9 2.4C12.6 4.1 11.7 6.6 12.1 8.1"/>'),
    # one stroke from the cusp: round lobes easing in to a fine point
    'heart': '<path class="draw" pathLength="1" style="--d:0" d="M12 8.4C11.2 6 8.9 4.6 6.7 5.1C4.2 5.7 3.2 8.4 4.2 11C5.6 14.4 9.4 16.6 12 19.8C14.5 16.7 18.6 14.3 19.8 10.9C20.7 8.2 19.6 5.6 17.2 5.1C15 4.6 12.8 6 12 8.4Z"/>',
}


_DRAW_HOOKS = re.compile(r' class="draw" pathLength="1" style="--d:\d+"')


def sprite(names=None):
    """One hidden <svg> holding a <symbol id="i-NAME"> per icon. names limits it to the icons a page uses
    (an iterable of names, or one name); the default is every icon. Include it once per page, before any icon()."""
    if names is None:
        names = list(ICON_PATHS)
    else:
        names = list(dict.fromkeys([names] if isinstance(names, str) else names))
        unknown = [n for n in names if n not in ICON_PATHS]
        if unknown:
            raise KeyError(f'unknown icon(s) {unknown!r}')
    symbols = ''.join('<symbol id="i-%s" viewBox="0 0 24 24" %s>%s</symbol>' % (name, STROKE, _DRAW_HOOKS.sub('', ICON_PATHS[name]))
                      for name in names)
    return ('<svg class="icon-sprite" aria-hidden="true" focusable="false" '
            f'style="position:absolute;width:0;height:0;overflow:hidden">{symbols}</svg>')


def _open(name, cls, label):
    if name not in ICON_PATHS:
        raise KeyError(f'unknown icon {name!r}')
    classes = escape(' '.join(dict.fromkeys(['icon', f'icon-{name}'] + (cls or '').split())))
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
