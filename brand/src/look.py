# The chosen look ("coastal badge", round one option D), parameterised by name.
from logos import FONTS, svg, gum_sprig, waves

LOOK = dict(lime='#ECE6DB', bush='#8B937A', paddock='#C3964F', bark='#5C4D3F', gulf='#A7BBC3', paper='#F6F2EA')

# Marcellus advance widths at font-size 100, letter-spacing 14 (measured in Chromium)
ADV = {'CHARNE WATSON': 1023.2, 'CHARNE & CO.': 870.0, 'SALTBUSH': 567.8, 'PAPERBARK': 647.0,
       'KIN & COAST': 783.4, 'SALT & GUM': 740.6}


def _main_text(name, size, ink, accent, x, y):
    ls = round(size * 0.14, 2)
    if '&' in name:
        a, b = name.split('&')
        inner = (f'{a}<tspan font-family="{FONTS["corm"]}" font-style="italic" font-weight="500" '
                 f'font-size="{size * 1.1:.1f}" fill="{accent}">&amp;</tspan>{b}')
    else:
        inner = name
    return (f'<text x="{x + ls / 2:.1f}" y="{y}" text-anchor="middle" font-family="{FONTS["marc"]}" '
            f'font-size="{size:.1f}" letter-spacing="{ls}" fill="{ink}">{inner}</text>')


def wordmark(name, sub, ink, accent, subcolor=None, label=None):
    subcolor = subcolor or ink
    size = min(64, 552 * 100 / ADV[name])
    sub_svg = sub.replace('&', f'<tspan fill="{accent}">&amp;</tspan>')
    return svg('0 0 640 170', _main_text(name, size, ink, accent, 320, 98) +
               f'<text x="322.4" y="142" text-anchor="middle" font-family="{FONTS["jost"]}" font-size="12" '
               f'font-weight="400" letter-spacing="4.8" fill="{subcolor}">{sub_svg}</text>',
               label or name.title())


def wordmark_line(name, ink, accent, label=None):
    size = min(64, 552 * 100 / ADV[name])
    return svg('0 0 640 100', _main_text(name, size, ink, accent, 320, 72), label or name.title())


def emblem(top, bottom, ink, sea, bg='none', uid='x', label='badge'):
    top = top.replace('&', '&amp;')
    return svg('0 0 240 240', f'''
  <defs><path id="t{uid}" d="M27,120 A93,93 0 0 1 213,120"/><path id="b{uid}" d="M15,120 A105,105 0 0 0 225,120"/></defs>
  <circle cx="120" cy="120" r="114" fill="{bg}" stroke="{ink}" stroke-width="1.6"/>
  <circle cx="120" cy="120" r="80" fill="none" stroke="{ink}" stroke-width="1"/>
  <text font-family="{FONTS['marc']}" font-size="16" letter-spacing="5" fill="{ink}"><textPath href="#t{uid}" startOffset="50%" text-anchor="middle">{top}</textPath></text>
  <text font-family="{FONTS['marc']}" font-size="10.5" letter-spacing="3" fill="{ink}"><textPath href="#b{uid}" startOffset="50%" text-anchor="middle">{bottom}</textPath></text>
  <circle cx="22" cy="120" r="2.2" fill="{ink}"/><circle cx="218" cy="120" r="2.2" fill="{ink}"/>
  <g transform="translate(124,62)">{gum_sprig(ink, 2)}</g>
  <g transform="translate(120,166)">{waves(sea, 2.2)}</g>''', label)
