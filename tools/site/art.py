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


# ------------------------------------------------------------------ A2b the wordmark (the name, outlined)
# "SUNDAY LIGHT" as brand/README.md sets it: Marcellus caps, tracked .14em, with the font's own kerning, outlined to
# paths so no wordmark font loads. Font units (2048 per em), y down, baseline at 0; the box runs from the first
# glyph's origin to the last glyph's advance (no trailing tracking) and from the tallest overshoot to the lowest one.
# Made by outline_wordmark() below from Marcellus 400 (fonts/marcellus-400.woff2 up to commit ca9c16a; OFL 1.1).
# To redraw it: python3 tools/site/art.py <marcellus.woff2 or .ttf>, then paste what it prints here.
WORDMARK_BOX = (17302, 1464, 31)   # width, height above the baseline, depth below it
WORDMARK_D = ('m741-1206h-22q-8-23-25-52-18-29-46-54-29-26-70-43-40-17-95-17-49 0-87 15-38 15-64 42-25 27-38 64-13 37-13 82 0 7'
              '2 41 137 40 66 101 130 61 64 132 128 71 64 132 133 61 69 101 145 41 75 41 162 0 65-23 130-22 66-69 118-47 52-121'
              ' 84-74 33-176 33-57 0-108-11-52-10-96-26-43-15-78-33-34-18-56-33l23-221h25q11 47 36 89 25 43 62 76 36 32 83 52 4'
              '7 19 103 19 51 0 92-15 40-16 69-44 29-27 45-65 15-38 15-83 0-63-23-116-23-54-60-102-38-48-86-93-47-45-97-91-50-4'
              '5-97-93-48-48-86-103-37-54-60-116-23-63-23-138 0-79 31-142 30-64 80-109 51-45 115-69 64-24 132-24 50 0 92 8 42 8'
              ' 75 19 34 11 59 22 25 11 41 18zm1647 164q0-85-2-148-2-64-6-110-4-47-9-78-5-31-11-52v-4h178v4q-6 21-12 52-5 31-9 '
              '78-3 46-6 110-2 63-2 148v540q0 143-41 244-41 101-114 166-73 64-175 94-102 29-223 29-121 0-226-28-104-28-182-91-7'
              '7-62-121-162-44-99-44-242v-550q0-85-2-148-2-64-6-110-4-47-10-78-5-31-11-52v-4h240v4q-6 21-12 52-5 31-9 78-4 46-6'
              ' 110-2 63-2 148v561q0 119 35 197 36 77 94 122 58 46 132 64 74 18 151 18 77 0 151-18 74-18 131-64 58-45 93-122 36'
              '-78 36-197zm770-392l1030 1096v-704q0-85-2-148-2-64-6-110-4-47-9-78-6-31-12-52v-4h178v4q-6 21-11 52-5 31-9 78-4 4'
              '6-6 110-2 63-2 148v1062h-35l-1030-1095v684q0 85 2 149 2 63 6 109 4 46 9 77 5 31 11 52v4h-178v-4q6-21 12-52 5-31 '
              '9-77 4-46 6-109 2-64 2-149v-651q0-85-2-148-2-64-6-110-4-47-9-78-6-31-12-52v-4zm1963 86q-2 112-4 217-1 45-1 92-1 '
              '47-1 93-1 45-1 86-1 42-1 74 0 67 1 162 1 95 3 195 1 100 4 192 3 92 7 153 14 2 38 4 23 3 49 4 26 2 51 3 25 1 42 1'
              ' 70 0 144-10 73-9 142-35 68-26 129-71 60-46 106-118 45-72 71-174 26-101 26-239 0-153-37-273-37-119-108-201-72-82'
              '-177-125-106-42-243-42-27 0-61 2-34 1-67 2-34 2-63 4-30 3-49 4zm-219-90q23 1 43 2 17 1 35 2 18 0 29 0 19 0 64-2 '
              '44-2 101-4 57-2 119-4 61-2 115-2 145 0 276 36 131 36 230 118 99 82 157 215 58 133 58 327 0 139-30 250-31 111-86 '
              '196-55 85-131 146-77 60-169 99-93 39-198 57-105 18-217 18-40 0-96-2-57-3-114-6-57-3-107-6-51-2-79-2v-4q6-21 12-5'
              '2 5-31 9-77 4-46 6-109 2-64 2-149v-651q0-85-2-150-2-64-6-110-4-47-9-79-6-32-12-53zm2659 1438v-4q2-5 3-15 1-10 1-'
              '18 0-31-9-69-8-37-32-93l-121-272q-56-2-149-2-93 0-201 0-79 0-153 0-73 0-132 2l-115 264q-15 37-32 81-17 44-17 89 '
              '0 13 2 21 2 9 4 12v4h-204v-4q18-19 45-68 27-48 59-121l573-1271h80l543 1222q19 43 39 84 21 40 39 72 18 32 32 54 1'
              '4 22 19 28v4zm-648-559q58 0 119-1 61 0 119 0 59-1 113-2 54 0 98-1l-281-635-276 639zm1793-129v297q0 85 2 149 2 63'
              ' 6 109 4 46 9 77 6 31 12 52v4h-240v-4q6-21 11-52 6-31 9-77 4-46 6-109 3-64 3-149v-277l-447-608q-23-31-46-57-22-2'
              '6-42-45-20-20-36-33-16-13-25-19v-4h303q0 23 19 76 20 52 71 123l328 449 321-469q17-25 34-51 17-26 31-50 14-24 22-'
              '44 9-20 9-34h195v4q-22 19-59 56-37 38-80 100zm2086 600q118 0 217-10 99-10 173-23 86-14 157-33l-29 162q-12-1-36-2'
              '-24-1-53-2-30-1-62-2-33 0-62 0-29-1-51-2-23 0-33 0h-432v-4q6-21 12-52 5-31 9-77 4-46 6-109 2-64 2-149v-651q0-85-'
              '2-148-2-64-6-110-4-47-9-78-6-31-12-52v-4h240v4q-6 21-11 52-6 31-9 78-4 46-6 110-3 63-3 148zm1027 84q6-21 11-52 5'
              '-31 9-77 4-46 6-109 2-64 2-149v-651q0-85-2-148-2-64-6-110-4-47-9-78-5-31-11-52v-4h239v4q-6 21-12 52-5 31-9 78-3 '
              '46-6 110-2 63-2 148v651q0 85 2 149 3 63 6 109 4 46 9 77 6 31 12 52v4h-239zm2082-164q0 11-2 23-3 12-12 20-45 34-9'
              '7 63-53 28-114 49-61 21-131 33-71 11-152 11-182 0-332-53-150-54-257-152-108-98-167-236-59-137-59-305 0-95 25-187'
              ' 24-92 71-175 47-83 116-153 69-69 158-120 88-51 195-80 106-28 230-28 48 0 98 4 50 5 99 14 49 8 95 20 45 12 86 27'
              'l68 185-8 4q-39-35-90-65-51-30-109-52-58-22-121-35-64-12-129-12-126 0-231 40-105 39-180 114-76 75-118 184-42 109'
              '-42 248 0 153 40 284 40 131 119 227 79 96 198 151 118 54 276 54 70 0 125-11 55-11 93-27 38-17 58-36 19-20 19-36v'
              '-39q0-70-2-121-2-51-6-88-4-38-9-65-5-27-12-50v-4h240v4q-6 21-11 49-6 29-10 68-4 39-6 92-2 52-2 121zm1537-518q-40'
              '-1-100-2-60 0-130-1-71-1-147-1-77-1-150-2-73 0-139 1-66 1-115 3v297q0 85 3 149 2 63 6 109 3 46 9 77 5 31 11 52v4'
              'h-240v-4q6-21 12-52 5-31 9-77 4-46 6-109 2-64 2-149v-651q0-85-2-148-2-64-6-110-4-47-9-78-6-31-12-52v-4h240v4q-6 '
              '21-11 52-6 31-9 78-4 46-6 110-3 63-3 148v256q52 2 118 2 66 1 138 0 72 0 147-1 74-1 144-3 69-1 130-3 60-2 104-4v-'
              '247q0-85-2-148-3-64-6-110-4-47-9-78-6-31-12-52v-4h240v4q-6 21-11 52-6 31-10 78-4 46-6 110-2 63-2 148v651q0 85 2 '
              '149 2 63 6 109 4 46 10 77 5 31 11 52v4h-240v-4q6-21 12-52 5-31 9-77 3-46 6-109 2-64 2-149zm1161-660q-118 0-213 1'
              '0-95 11-164 23-80 15-143 33l29-162q12 1 36 2 24 1 53 2 30 1 62 2 33 0 62 0 29 1 51 2 23 0 33 0h571q10 0 32 0 23-'
              '1 52-2 29 0 61 0 33-1 62-2 30-1 54-2 24-1 36-2l29 162q-64-18-144-33-69-12-164-23-95-10-213-10v955q0 85 2 149 3 6'
              '3 6 109 4 46 9 77 6 31 12 52v4h-239v-4q6-21 11-52 5-31 9-77 4-46 6-109 2-64 2-149z')


def wordmark_svg():
    """wordmark.svg, painted through a CSS mask on the header's .brand-name and the footer's Sundown word (so it takes
    the text colour, and CanvasText in forced colours). Bark fill for anyone who opens the file itself."""
    w, up, down = WORDMARK_BOX
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -{up} {w} {up + down}">'
            f'<path fill="{BARK}" d="{WORDMARK_D}"/></svg>\n')


def outline_wordmark(font_path, text='SUNDAY LIGHT', track=.14):
    """(box, d): the text outlined in integer font units with relative commands, a repeated command letter left out.
    Needs fontTools (pip install fonttools brotli); the build itself does not."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.basePen import BasePen
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.transformPen import TransformPen
    f = TTFont(font_path)
    upm, gs, hm = f['head'].unitsPerEm, f.getGlyphSet(), f['hmtx']
    names = [f.getBestCmap()[ord(c)] for c in text]
    kern, g = {}, f['GPOS'].table   # pair kerning from the 'kern' feature (PairPos formats 1 and 2)
    for li in sorted({i for r in g.FeatureList.FeatureRecord if r.FeatureTag == 'kern' for i in r.Feature.LookupListIndex}):
        lk = g.LookupList.Lookup[li]
        for st in lk.SubTable:
            st = st.ExtSubTable if lk.LookupType == 9 else st
            if not hasattr(st, 'Coverage'):
                continue
            for a in names:
                if a not in st.Coverage.glyphs:
                    continue
                for b in names:
                    if st.Format == 1:
                        rec = next((r for r in st.PairSet[st.Coverage.glyphs.index(a)].PairValueRecord if r.SecondGlyph == b), None)
                        v = rec and rec.Value1 and getattr(rec.Value1, 'XAdvance', 0)
                    else:
                        r = st.Class1Record[st.ClassDef1.classDefs.get(a, 0)].Class2Record[st.ClassDef2.classDefs.get(b, 0)]
                        v = r.Value1 and getattr(r.Value1, 'XAdvance', 0)
                    if v:
                        kern.setdefault((a, b), v)

    class Pen(BasePen):
        def __init__(self):
            super().__init__(gs)
            self.x, self.out, self.cur, self.start, self.last = 0, [], (0, 0), (0, 0), ''

        def emit(self, cmd, *pts):
            nums, q = [], self.cur
            for px, py in pts:   # round on the absolute grid, relative to the segment's start: no drift
                q = (round(px + self.x), round(-py))
                nums += [q[0] - self.cur[0], q[1] - self.cur[1]]
            self.cur = q
            if cmd == 'v':
                nums = nums[1:]
            elif cmd == 'h':
                nums = nums[:1]
            text = ''
            for n in nums:
                text += (' ' if text and n >= 0 else '') + str(n)
            same = cmd == self.last and cmd not in 'mz'
            self.out.append(('' if not same else ' ' if text[0] != '-' else '') + ('' if same else cmd) + text)
            self.last = cmd

        def _moveTo(self, p):
            self.emit('m', p)
            self.start = self.cur

        def _lineTo(self, p):
            q = (round(p[0] + self.x), round(-p[1]))
            self.emit('v' if q[0] == self.cur[0] else 'h' if q[1] == self.cur[1] else 'l', p)

        def _qCurveToOne(self, p1, p2):
            self.emit('q', p1, p2)

        def _curveToOne(self, p1, p2, p3):
            self.emit('c', p1, p2, p3)

        def _closePath(self):
            self.out.append('z')
            self.cur, self.last = self.start, 'z'

    pen, bounds, x = Pen(), BoundsPen(gs), 0
    for i, n in enumerate(names):
        x += kern.get((names[i - 1], n), 0) if i else 0
        pen.x = x
        gs[n].draw(pen)
        gs[n].draw(TransformPen(bounds, (1, 0, 0, 1, x, 0)))
        x += hm[n][0] + (track * upm if i < len(names) - 1 else 0)
    _, y0, _, y1 = bounds.bounds
    return (round(x), round(y1), round(-y0)), ''.join(pen.out)


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


if __name__ == '__main__':   # redraw the wordmark from the font (see A2b)
    import sys
    box, d = outline_wordmark(sys.argv[1])
    print(f'WORDMARK_BOX = {box}   # width, height above the baseline, depth below it')
    print(f"WORDMARK_D = ({chr(10).join(repr(d[i:i + 112]) for i in range(0, len(d), 112))})".replace(chr(10), chr(10) + ' ' * 14))
