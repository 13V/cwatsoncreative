# Logo SVG builders for the four brand directions. Each returns an <svg> string.
# Text is set in Google Fonts loaded by the host page.
FONTS = {
 'corm': "'Cormorant Garamond', 'Cormorant', Garamond, 'Times New Roman', serif",
 'fraun': "'Fraunces', 'Iowan Old Style', Georgia, serif",
 'jost': "'Jost', 'Futura', 'Avenir Next', 'Century Gothic', sans-serif",
 'marc': "'Marcellus', 'Optima', 'Candara', serif",
 'corinthia': "'Corinthia', 'Snell Roundhand', 'Apple Chancery', cursive",
 'mrs': "'Mrs Saint Delafield', 'Snell Roundhand', 'Apple Chancery', cursive",
}
PAL = {
 'sig':  dict(paper='#F3F0EA', ink='#1F1C19', stone='#BFB3A6', drift='#867665'),
 'chap': dict(page='#F2EDE4', gum='#4A5436', gilt='#9E7F47', rose='#C9A79C', ink='#27241F'),
 'sun':  dict(salt='#F7F5F0', deep='#35505C', gulf='#A7BBC3', honey='#E09F45', char='#2A2C2D'),
 'salt': dict(lime='#ECE6DB', bush='#8B937A', paddock='#C3964F', bark='#5C4D3F', gulf='#A7BBC3'),
}
def svg(vb, body, label, cls=''):
    label = label.replace('&', '&amp;').replace('"', '&quot;')
    return f'<svg class="{cls}" viewBox="{vb}" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'

# ---------- 01 Signature: Charne Watson ----------
def sig_primary(ink, sub=None):
    sub = sub or ink
    return svg('0 0 640 170', f'''
  <text x="320" y="98" text-anchor="middle" font-family="{FONTS['corm']}" font-size="86" font-weight="500" fill="{ink}"><tspan font-style="italic">Charne</tspan> Watson</text>
  <text x="322.2" y="146" text-anchor="middle" font-family="{FONTS['jost']}" font-size="13" font-weight="400" letter-spacing="4.4" fill="{sub}">PHOTOGRAPHER · ADELAIDE</text>''', 'Charne Watson, Photographer, Adelaide')

def sig_mono(ink, bg='none', ring=True):
    r = f'<circle cx="100" cy="100" r="92" fill="{bg}" stroke="{ink if ring else "none"}" stroke-width="1.4"/>'
    return svg('0 0 200 200', f'''{r}
  <text x="42" y="143" font-family="{FONTS['corm']}" font-size="158" font-style="italic" font-weight="400" fill="{ink}">C</text>
  <text x="82" y="121" font-family="{FONTS['corm']}" font-size="58" font-weight="500" fill="{ink}">W</text>''', 'CW monogram')

def sig_signature(ink):
    return svg('0 0 420 170', f'''
  <text x="210" y="108" text-anchor="middle" font-family="{FONTS['mrs']}" font-size="120" fill="{ink}">Charne</text>''', 'Signature stand-in')

# ---------- 02 Chapters by Charne ----------
def chap_primary(ink, accent, sub=None):
    sub = sub or ink
    return svg('0 0 640 250', f'''
  <text x="320" y="122" text-anchor="middle" font-family="{FONTS['fraun']}" font-size="116" font-weight="300" fill="{ink}" style="font-variation-settings:'opsz' 144">Chapters</text>
  <text x="524" y="180" text-anchor="end" font-family="{FONTS['corinthia']}" font-size="70" fill="{accent}">by Charne</text>
  <text x="322" y="234" text-anchor="middle" font-family="{FONTS['jost']}" font-size="12" font-weight="400" letter-spacing="4" fill="{sub}">PHOTOGRAPHY · ADELAIDE</text>''', 'Chapters by Charne, photography, Adelaide')

def chap_line(ink, accent):
    return svg('0 0 520 120', f'''
  <text x="18" y="84" font-family="{FONTS['fraun']}" font-size="92" font-weight="300" fill="{ink}" style="font-variation-settings:'opsz' 144">Chapters</text>
  <text x="352" y="94" font-family="{FONTS['corinthia']}" font-size="60" fill="{accent}">by Charne</text>''', 'Chapters by Charne')

def label_path(x0, y0, x1, y1, r):
    # rectangle with concave (inward) corners, like a book label
    return (f'M{x0+r},{y0} H{x1-r} A{r},{r} 0 0 0 {x1},{y0+r} V{y1-r} A{r},{r} 0 0 0 {x1-r},{y1} '
            f'H{x0+r} A{r},{r} 0 0 0 {x0},{y1-r} V{y0+r} A{r},{r} 0 0 0 {x0+r},{y0} Z')

def chap_mono(ink, fill='none', text=None):
    text = text or ink
    return svg('0 0 200 200', f'''
  <path d="{label_path(18,42,182,158,16)}" fill="{fill}" stroke="{ink}" stroke-width="1.6"/>
  <path d="{label_path(26,50,174,150,12)}" fill="none" stroke="{ink}" stroke-width="0.9"/>
  <text x="100" y="124" text-anchor="middle" font-family="{FONTS['fraun']}" font-size="70" font-weight="300" font-style="italic" fill="{text}" style="font-variation-settings:'opsz' 144">Ch.</text>''', 'Ch. monogram')

# ---------- 03 c.watson ----------
def sun_primary(ink, honey, sub=None):
    sub = sub or ink
    # Jost 300 @100: c adv 48.2, watson adv 279.7; sun r=10 at mid x-height, 6px gaps
    x0 = 152
    return svg('0 0 640 190', f'''
  <text x="{x0}" y="112" font-family="{FONTS['jost']}" font-size="100" font-weight="300" fill="{ink}">c</text>
  <circle cx="{x0+48.2+6+10}" cy="89" r="10" fill="{honey}"/>
  <text x="{x0+48.2+6+20+6}" y="112" font-family="{FONTS['jost']}" font-size="100" font-weight="300" fill="{ink}">watson</text>
  <text x="322.2" y="160" text-anchor="middle" font-family="{FONTS['jost']}" font-size="15" font-weight="400" letter-spacing="4.4" fill="{sub}">photography · adelaide</text>''', 'c·watson photography, Adelaide')

def sun_mark(ink, honey, bg='none'):
    return svg('0 0 200 200', f'''
  <circle cx="100" cy="100" r="92" fill="{bg}"/>
  <text x="100" y="148" text-anchor="middle" font-family="{FONTS['jost']}" font-size="190" font-weight="300" fill="{ink}">c</text>
  <circle cx="112" cy="104" r="17" fill="{honey}"/>''', 'c with the sun inside')

# ---------- 04 Salt & Gum ----------
def leaf(length, bend=0.16, width=0.085):
    L=length; b=L*bend; w=L*width
    outline = (f'M0,0 C{-w*1.1:.1f},{L*0.28:.1f} {-w*0.9+b*0.3:.1f},{L*0.74:.1f} {b:.1f},{L:.1f} '
               f'C{w*0.55+b*0.6:.1f},{L*0.7:.1f} {w*0.8:.1f},{L*0.26:.1f} 0,0 Z')
    rib = f'M0,0 C{-w*0.15:.1f},{L*0.3:.1f} {b*0.2:.1f},{L*0.7:.1f} {b:.1f},{L:.1f}'
    return outline, rib
def gum_sprig(stroke, sw=2):
    out = [f'<g fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">',
           '<path d="M0,0 C-2,-8 -8,-14 -14,-18"/>']
    for ang, ln in ((-30, 64), (-2, 82), (25, 60)):
        o, r = leaf(ln)
        out.append(f'<g transform="rotate({ang})"><path d="{o}"/><path d="{r}" stroke-width="{sw*0.55:.2f}"/></g>')
    out.append('</g>')
    return ''.join(out)
def waves(stroke, sw=2):
    return f'''<g fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round">
    <path d="M-44,0 q11,-6 22,0 t22,0 t22,0 t22,0"/>
    <path d="M-30,11 q10,-5 20,0 t20,0 t20,0"/>
  </g>'''
def salt_emblem(ink, accent, sea, bg='none', uid='a'):
    return svg('0 0 240 240', f'''
  <defs><path id="sgTop{uid}" d="M27,120 A93,93 0 0 1 213,120"/><path id="sgBot{uid}" d="M15,120 A105,105 0 0 0 225,120"/></defs>
  <circle cx="120" cy="120" r="114" fill="{bg}" stroke="{ink}" stroke-width="1.6"/>
  <circle cx="120" cy="120" r="80" fill="none" stroke="{ink}" stroke-width="1"/>
  <text font-family="{FONTS['marc']}" font-size="16" letter-spacing="5" fill="{ink}"><textPath href="#sgTop{uid}" startOffset="50%" text-anchor="middle">SALT &amp; GUM</textPath></text>
  <text font-family="{FONTS['marc']}" font-size="10.5" letter-spacing="3" fill="{ink}"><textPath href="#sgBot{uid}" startOffset="50%" text-anchor="middle">PHOTOGRAPHY · ADELAIDE</textPath></text>
  <circle cx="22" cy="120" r="2.2" fill="{ink}"/><circle cx="218" cy="120" r="2.2" fill="{ink}"/>
  <g transform="translate(124,62)">{gum_sprig(ink, 2)}</g>
  <g transform="translate(120,166)">{waves(sea, 2.2)}</g>''', 'Salt & Gum emblem')

def salt_primary(ink, accent, sub=None):
    sub = sub or ink
    return svg('0 0 640 170', f'''
  <text x="327" y="98" text-anchor="middle" font-family="{FONTS['marc']}" font-size="64" letter-spacing="9" fill="{ink}">SALT <tspan font-family="{FONTS['corm']}" font-style="italic" font-weight="500" font-size="70" fill="{accent}">&amp;</tspan> GUM</text>
  <text x="322.4" y="142" text-anchor="middle" font-family="{FONTS['jost']}" font-size="12" font-weight="400" letter-spacing="4.8" fill="{sub}">PHOTOGRAPHY BY CHARNE WATSON</text>''', 'Salt & Gum, photography by Charne Watson')

# ---------- one-line lockups for website nav bars ----------
def sig_line(ink):
    return svg('0 0 520 110', f'''<text x="260" y="80" text-anchor="middle" font-family="{FONTS['corm']}" font-size="84" font-weight="500" fill="{ink}"><tspan font-style="italic">Charne</tspan> Watson</text>''', 'Charne Watson')
def sun_line(ink, honey):
    x0 = 20
    return svg('0 0 400 130', f'''<text x="{x0}" y="100" font-family="{FONTS['jost']}" font-size="100" font-weight="300" fill="{ink}">c</text>
  <circle cx="{x0+48.2+6+10}" cy="77" r="10" fill="{honey}"/>
  <text x="{x0+48.2+6+20+6}" y="100" font-family="{FONTS['jost']}" font-size="100" font-weight="300" fill="{ink}">watson</text>''', 'c·watson')
def salt_line(ink, accent):
    return svg('0 0 560 100', f'''<text x="284.5" y="74" text-anchor="middle" font-family="{FONTS['marc']}" font-size="64" letter-spacing="9" fill="{ink}">SALT <tspan font-family="{FONTS['corm']}" font-style="italic" font-weight="500" font-size="70" fill="{accent}">&amp;</tspan> GUM</text>''', 'Salt & Gum')
def numeral(n, bg, fg):
    return svg('0 0 100 100', f'''<circle cx="50" cy="50" r="50" fill="{bg}"/><text x="50" y="62" text-anchor="middle" font-family="{FONTS['fraun']}" font-size="36" font-weight="300" font-style="italic" fill="{fg}">{n}</text>''', f'Chapter {n}')
