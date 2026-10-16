# Builds the "Naming the Arch" page into ./site4/ : five names without her first name, each set in the arch.
import os
from logos import FONTS, svg
from page import esc, img, grease_loop
from page3 import CSS as BASE_CSS, GF
from pwc import B as P, arch_mark

MARC, CORM, JOST = FONTS['marc'], FONTS['corm'], FONTS['jost']
ADV = {'LOW SUN': 546.4, 'SUNDAY LIGHT': 858.8, 'GOLDEN WINDOW': 1062.3, 'C. WATSON': 665.2, 'WATSON & CO.': 886.8}


def _name(mark, size, ink, accent):
    if '&' in mark:
        a, b = mark.split('&')
        return (f'{a}<tspan font-family="{CORM}" font-style="italic" font-weight="500" font-size="{size * 1.1:.1f}" '
                f'letter-spacing="0" fill="{accent}">&amp;</tspan>{b}')
    if mark.startswith('C.'):
        return f'C<tspan fill="{accent}">.</tspan>{mark[2:]}'
    return mark


def _arch_inner(ink, uid, fill=None):
    s = arch_mark(ink, P['paddock'], P['bush'], P['gulf'], fill or P['lime'], uid=uid)
    return s[s.index('>') + 1:-6]


def lockup(mark, ink, accent, sub_color, uid, fill=None):
    size = min(54, 540 * 100 / ADV[mark])
    ls = size * 0.14
    return svg('0 0 640 370', f'''
  <g transform="translate(210,-6) scale(1.1)">{_arch_inner(ink, uid, fill)}</g>
  <text x="{320 + ls / 2:.1f}" y="302" text-anchor="middle" font-family="{MARC}" font-size="{size:.1f}" letter-spacing="{ls:.2f}" fill="{ink}">{_name(mark, size, ink, accent)}</text>
  <text x="322.4" y="346" text-anchor="middle" font-family="{JOST}" font-size="12" font-weight="400" letter-spacing="4.8" fill="{sub_color}">PHOTOGRAPHY · ADELAIDE</text>''',
               f'{mark.title()} photography, Adelaide')


def lockup_line(mark, ink, accent, uid, fill=None):
    size = min(48, 480 * 100 / ADV[mark])
    ls = size * 0.14
    w = ADV[mark] * size / 100
    vbw = round(100 + w + 6)
    return svg(f'0 0 {vbw} 140', f'''
  <g transform="translate(-14,0) scale(.58)">{_arch_inner(ink, uid, fill)}</g>
  <text x="100" y="88" font-family="{MARC}" font-size="{size:.1f}" letter-spacing="{ls:.2f}" fill="{ink}">{_name(mark, size, ink, accent)}</text>''',
               mark.title())


NAMES = [
 dict(key='lowsun', mark='LOW SUN', name='Low Sun', pick=True,
      line='The light she shoots in, and the sun in the arch.',
      why=['It names her signature: she shoots into a low sun, and Adelaide’s beaches face west, so it sets over the water.',
           'The logo already shows it: a low sun over the hills.',
           'Two short words, unusual for a photographer, and easy to say and spell.'],
      watch=['Nothing personal in the name itself, so her photo and voice on the About page do that job.'],
      tag='Photographs in the best light of the day.',
      avail=[('ok', 'lowsun.com.au', 'unregistered'), ('ok', 'lowsunphotography.com', 'unregistered'),
             ('no', 'lowsun.com', 'taken'), ('chk', '@lowsun.photo', 'check in the app')]),
 dict(key='sunday', mark='SUNDAY LIGHT', name='Sunday Light',
      line='Slow, sunny afternoons with the people you love.',
      why=['Sounds the way her sessions feel: relaxed, warm and unhurried.',
           'Friendly for families, and still soft enough for weddings.',
           'Easy to say and to remember.'],
      watch=['A London company sells a lamp called Sunday Light, and sundaylight.com is taken.'],
      tag='Relaxed family photos in golden light.',
      avail=[('ok', 'sundaylightphotography.com', 'unregistered'), ('no', 'sundaylight.com', 'taken'),
             ('chk', 'sundaylight.com.au', 'check'), ('chk', '@sundaylight.photo', 'check in the app')]),
 dict(key='golden', mark='GOLDEN WINDOW', name='Golden Window',
      line='The arch is a window, and it is full of golden light.',
      why=['Ties straight to the logo: the arch is the window and the sun is the gold.',
           'Photographers love window light for newborns at home and golden light outdoors. This name covers both.',
           'Warm and a little nostalgic.'],
      watch=['The longest of the five, and goldenwindow.com is taken.',
             'Keep “golden” and “arch” apart in copy. Golden arches belong to McDonald’s.'],
      tag='A window into your family, in golden light.',
      avail=[('ok', 'goldenwindowphotography.com', 'unregistered'), ('no', 'goldenwindow.com', 'taken'),
             ('chk', 'goldenwindow.com.au', 'check'), ('chk', '@goldenwindow.photo', 'check in the app')]),
 dict(key='cwatson', mark='C. WATSON', name='C. Watson Photography',
      line='Her surname, the way her current handle already uses it.',
      why=['Personal without the first name, which is how she named the business the first time.',
           'Past clients already know cwatson, so there is nothing to explain.',
           'Classic and honest, and it will not date.'],
      watch=['The least distinctive of the five, and “Watson” in Adelaide search brings up The Watson hotel.'],
      tag='Natural, light-filled photography in Adelaide.',
      avail=[('ok', 'cwatsonphotography.com', 'unregistered'), ('chk', 'cwatsonphotography.com.au', 'check'),
             ('chk', '@cwatson.creative', 'keep, or move to @cwatson.photography')]),
 dict(key='watsonco', mark='WATSON & CO.', name='Watson & Co.',
      line='Her surname as a small studio, keeping the gold ampersand.',
      why=['Personal through the surname, and it sounds established.',
           'Keeps the gold italic ampersand from the badge you first liked.',
           'John Watson & Co. ran a photography studio in Brisbane from the 1850s to the 1870s, so the name has history in Australian photography.'],
      watch=['“& Co.” names are common in every trade, and watsonandco.com is taken.'],
      tag='Photography for Adelaide couples and families.',
      avail=[('ok', 'watsonandcophotography.com', 'unregistered'), ('no', 'watsonandco.com', 'taken'),
             ('chk', 'watsonandco.com.au', 'check'), ('chk', '@watsonandco.photo', 'check in the app')]),
]

CSS = BASE_CSS + r'''
.lineup{display:flex;flex-wrap:wrap;justify-content:center;gap:14px 10px;margin-top:20px}
.lineup a{text-decoration:none;display:grid;gap:8px;position:relative;flex:0 1 calc((100% - 20px) / 3);min-width:0}
.lineup .card{background:#F6F2EA;border-radius:2px;padding:5% 8% 4%;display:grid;place-items:center}
.lineup .card svg{width:100%;height:auto}
.lineup span.lab{font:500 .74rem/1.3 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.lineup .gc{left:-4%;top:-8%;width:108%;height:112%}
@media (max-width:900px){.lineup a{flex-basis:calc((100% - 10px) / 2)}}
@media (max-width:520px){.lineup a{flex-basis:100%}}
.board{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:28px;align-items:start}
.board .vis{display:grid;gap:10px}
.board .vis .big{background:#F6F2EA;border-radius:2px;padding:6% 8%}
.board .vis .nav{background:#5C4D3F;border-radius:2px;padding:5% 7%;display:grid;place-items:center}
.board .vis svg{width:100%;height:auto;display:block}
.board .vis .nav svg{width:min(100%,360px)}
.board .tag{font:500 italic clamp(1.25rem,2.4vw,1.6rem)/1.3 "Cormorant Garamond",Garamond,serif;margin-top:14px}
.board .tag small{display:block;font:500 .74rem/1.3 var(--mono);font-style:normal;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:4px}
.board .notes{grid-template-columns:minmax(0,1fr);gap:18px;margin-top:20px}
@media (max-width:820px){.board{grid-template-columns:minmax(0,1fr)}}
.avail li{font:400 .86rem/1.6 var(--mono)}
.avail li::before{display:none}
.no{color:#B23A2A}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .no{color:#FF8A73}}
:root[data-theme="dark"] .no{color:#FF8A73}
.tablewrap{overflow-x:auto}
table.cmp{border-collapse:collapse;width:100%;min-width:640px;font-size:.95rem}
.cmp th,.cmp td{padding:13px 12px;border-top:1px solid var(--line);text-align:left;vertical-align:middle}
.cmp thead th{font:500 .74rem/1.3 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted);border-top:0;position:relative}
.cmp thead th.pickcol{color:var(--fg)}
.cmp thead th.pickcol .gc{left:-8%;top:-20%;width:116%;height:140%}
.cmp tbody th{font-weight:500;min-width:150px}
.cmp td.dots{font-size:1.02rem;letter-spacing:.14em;white-space:nowrap}
.dots i{font-style:normal;color:var(--line)}
.mocks{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);gap:22px;align-items:start;margin-top:28px}
@media (max-width:900px){.mocks{grid-template-columns:minmax(0,1fr)}}
.site{background:#F6F2EA;color:#3F352B;border-radius:4px;overflow:hidden;box-shadow:0 12px 40px -18px rgba(0,0,0,.35)}
.site-url{font:400 .72rem/1 var(--mono);color:#7A6F63;background:#E9E3D8;padding:9px 14px}
.site-nav{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:12px 22px;border-bottom:1px solid #E3DCCF}
.site-nav svg{height:40px;width:auto;display:block}
.site-nav nav{display:flex;gap:16px;font:500 .66rem/1 "Jost",sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#5C4D3F}
.site-hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,.82fr)}
.site-copy{padding:clamp(22px,4vw,44px);display:grid;gap:14px;align-content:center}
.site-copy .se{font:500 .66rem/1 "Jost",sans-serif;letter-spacing:.22em;color:#8B937A}
.site-copy .sh{font:500 clamp(1.6rem,3.2vw,2.35rem)/1.08 "Cormorant Garamond",Garamond,serif;color:#3F352B;text-wrap:balance}
.site-copy .ss{font:400 .9rem/1.55 "Jost",sans-serif;color:#5C4D3F}
.site-copy .sb{justify-self:start;font:500 .68rem/1 "Jost",sans-serif;letter-spacing:.18em;text-transform:uppercase;background:#5C4D3F;color:#F6F2EA;padding:12px 18px;border-radius:999px}
.site-hero img{width:100%;height:100%;object-fit:cover;display:block;min-height:300px}
@media (max-width:620px){.site-nav nav{display:none}.site-hero{grid-template-columns:minmax(0,1fr)}.site-hero img{order:-1;min-height:0;aspect-ratio:4/3}}
.ig{background:#FFFFFF;color:#111;border-radius:22px;padding:18px 16px 16px;max-width:360px;width:100%;justify-self:center;font:400 13px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;box-shadow:0 0 0 8px #1d1d1b,0 18px 40px -18px rgba(0,0,0,.5)}
.ig-head{display:flex;align-items:center;gap:18px}
.ig-av{width:78px;height:78px;border-radius:50%;background:#F6F2EA;display:grid;place-items:center;flex:none;overflow:hidden}
.ig-av svg{width:70%;height:auto}
.ig-stats{display:flex;gap:14px;flex-wrap:wrap}
.ig-stats span{display:grid;text-align:center;font-size:12px;line-height:1.25}
.ig-stats b{font-size:15px}
.ig-handle{font-weight:700;font-size:14px;margin-top:12px}
.ig-name{font-weight:600}
.ig-bio{white-space:pre-line}
.ig-link{color:#00376B;font-weight:600}
.ig-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:2px;margin:14px -16px -16px;border-radius:0 0 22px 22px;overflow:hidden}
.ig-grid img{width:100%;height:auto;aspect-ratio:3/4;object-fit:cover;display:block}
.bio{margin-top:24px;background:var(--surface);border:1px solid var(--line);border-radius:3px;padding:18px 20px;display:grid;gap:10px;max-width:640px}
.bio pre{margin:0;font:400 .95rem/1.55 var(--sans);white-space:pre-wrap}
.bio-bar{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.btn{font:500 .78rem/1 var(--mono);text-transform:uppercase;letter-spacing:.06em;background:var(--fg);color:var(--bg);border:0;border-radius:999px;padding:10px 16px;cursor:pointer}
.also{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:0 40px}
.also div{padding:13px 0;border-top:1px solid var(--line)}
.also b{font-weight:600}
.also p{color:var(--muted);font-size:.95rem}
'''

BIO = ('Natural, light-filled photos for Adelaide couples & families.\n'
       'Weddings · Bump · Newborn · Family\n'
       'In the best light of the day ↓')

ALSO = [
 ('Late Light', 'Same idea as Low Sun, softer. latelight.com is taken, and Low Sun is the stronger of the two.'),
 ('Field & Frame', 'Outdoors and photos in one, but fieldandframe.com and fieldandframephotography.com are both taken.'),
 ('Homeward', 'The feeling of family and home. homewardphotography.com is taken.'),
 ('Window Light', 'A photographer’s term for soft indoor light. Too generic to own.'),
 ('Little Arch', 'Cute for newborns, but littlearchphotography.com is taken and it undersells weddings.'),
 ('Golden Arch', 'Never. That one belongs to McDonald’s.'),
]
NEXT = [
 'Pick the name.',
 'Search the ASIC business names register and IP Australia trade marks, then register the business name.',
 'Register the domain (.com.au needs an ABN) and claim the Instagram handle before announcing.',
 'Final arch logo files: outlined SVG and PNG, favicon, Instagram avatar, highlight covers and watermark.',
 'Build the website on the new brand.',
]

JS = r'''<script>
(function(){var b=document.getElementById('copy-bio'),p=document.getElementById('bio-text');if(!b||!p)return;
b.addEventListener('click',function(){var t=p.textContent,d=function(m){b.textContent=m;setTimeout(function(){b.textContent='Copy bio';},2200);},
s=function(){var r=document.createRange();r.selectNodeContents(p);var x=window.getSelection();x.removeAllRanges();x.addRange(r);d('Selected. Press Ctrl+C');};
try{navigator.clipboard.writeText(t).then(function(){d('Copied');},s);}catch(e){s();}});})();
</script>'''


def li(xs):
    return ''.join(f'<li>{esc(x)}</li>' for x in xs)


def lineup():
    cards = ''
    for i, n in enumerate(NAMES, 1):
        circ = grease_loop(77) if n.get('pick') else ''
        cards += (f'<a href="#{n["key"]}"><div class="card">{lockup(n["mark"], P["bark"], P["paddock"], P["bark"], n["key"] + "L")}</div>'
                  f'<span class="lab">{i} · {esc(n["name"])}</span>{circ}</a>')
    return f'<div class="lineup">{cards}</div>'


def board(i, n):
    av = ''.join(f'<li><span class="{c}">{"✓" if c == "ok" else ("✗" if c == "no" else "?")}</span> {d} '
                 f'<span class="muted">{s}</span></li>' for c, d, s in n['avail'])
    return (f'<section class="wrap" id="{n["key"]}"><div class="concept-head"><span class="num">{i} of 5</span>'
            f'<h2>{esc(n["name"])}</h2><p class="muted">{esc(n["line"])}</p></div>'
            f'<div class="board"><div class="vis"><div class="big">{lockup(n["mark"], P["bark"], P["paddock"], P["bark"], n["key"] + "B")}</div>'
            f'<div class="nav">{lockup_line(n["mark"], P["paper"], P["paddock"], n["key"] + "N", fill=P["paper"])}</div></div>'
            f'<div><p class="tag"><small>How it talks</small>{esc(n["tag"])}</p>'
            f'<div class="notes"><div><h4>Why it fits</h4><ul>{li(n["why"])}</ul></div>'
            f'<div><h4>Watch for</h4><ul>{li(n["watch"])}</ul></div>'
            f'<div><h4>Availability</h4><ul class="avail">{av}</ul></div></div></div></div></section>')


def compare():
    crit = [('Feels personal', [2, 3, 2, 4, 4]), ('Memorable', [5, 4, 3, 2, 3]),
            ('Easy to own (domain, search)', [5, 3, 3, 3, 2]), ('Fits the arch', [5, 4, 5, 3, 3])]
    head = ''.join(f'<th scope="col" class="{"pickcol" if n.get("pick") else ""}">{i} · {esc(n["name"])}'
                   f'{grease_loop(53) if n.get("pick") else ""}</th>' for i, n in enumerate(NAMES, 1))
    rows = ''.join(f'<tr><th scope="row">{lab}</th>' + ''.join(
        f'<td class="dots" aria-label="{v} of 5">{"●" * v}<i>{"●" * (5 - v)}</i></td>' for v in sc) + '</tr>'
        for lab, sc in crit)
    return (f'<div class="tablewrap"><table class="cmp"><thead><tr><th scope="col">Scored 1 to 5</th>{head}</tr></thead>'
            f'<tbody>{rows}</tbody></table></div><p class="muted" style="margin-top:12px;font-size:.92rem">All five leave '
            f'out her first name. Scores are my judgement.</p>')


def pick():
    nav = lockup_line('LOW SUN', P['bark'], P['paddock'], 'pkN')
    av = arch_mark(P['bark'], P['paddock'], P['bush'], P['gulf'], P['lime'], uid='pkA')
    site = (f'<div class="site" aria-label="Homepage mock-up"><div class="site-url">lowsun.com.au</div>'
            f'<div class="site-nav">{nav}<nav><span>Portfolio</span><span>About</span><span>Investment</span><span>Enquire</span></nav></div>'
            f'<div class="site-hero"><div class="site-copy"><span class="se">ADELAIDE PHOTOGRAPHER</span>'
            f'<span class="sh">Photographs in the best light of the day.</span>'
            f'<span class="ss">Natural, light-filled sessions for couples and families, on the coast, in the hills and at home.</span>'
            f'<span class="sb">Check dates</span></div>{img(9, lazy=False)}</div></div>')
    ig = (f'<div class="ig" aria-label="Instagram profile mock-up"><div class="ig-head"><div class="ig-av">{av}</div>'
          f'<div class="ig-stats"><span><b>35</b>posts</span><span><b>213</b>followers</span><span><b>39</b>following</span></div></div>'
          f'<div class="ig-handle">lowsun.photo</div><div class="ig-name">Low Sun Photography</div>'
          f'<div class="ig-bio">{esc(BIO)}</div><div class="ig-link">lowsun.com.au</div>'
          f'<div class="ig-grid">{img(4, lazy=False)}{img(14, lazy=False)}{img(17, lazy=False)}</div></div>')
    return (f'<p class="lead">It is the only name that describes her work and her logo at once. She shoots into a low sun, '
            f'the arch shows a low sun over the hills, and lowsun.com.au is free. If she would rather the name '
            f'point to her, C. Watson Photography is the safe choice and uses the same arch.</p>'
            f'<div class="mocks">{site}{ig}</div>'
            f'<div class="bio"><div class="bio-bar"><h4>Instagram bio, ready to paste</h4>'
            f'<button class="btn" id="copy-bio" type="button">Copy bio</button></div><pre id="bio-text">{esc(BIO)}</pre>'
            f'<p class="muted" style="font-size:.86rem">Name field: Low Sun Photography. {len(BIO)} of 150 characters.</p></div>')


def build(standalone=False):
    hero = ('<header class="hero wrap"><p class="eyebrow">Name round · the arch · October 2026</p>'
            '<h1>Naming the arch</h1>'
            '<p class="lead">The arch is the logo. Charne doesn’t want her first name in the business name, so these '
            'five leave it out. Her current handle, cwatson.creative, already does, so two of them keep her surname. '
            'The other three come from the arch itself: the light, the time of day, the window.</p>'
            + lineup() + '</header>')
    parts = [hero] + [board(i, n) for i, n in enumerate(NAMES, 1)] + [
     ('<section class="wrap" id="compare"><div class="concept-head"><span class="num">Compare</span>'
      '<h2>Side by side</h2></div>' + compare() + '</section>'),
     ('<section class="wrap" id="pick"><div class="concept-head"><span class="num">My pick</span>'
      '<h2>Low Sun</h2></div>' + pick() + '</section>'),
     ('<section class="wrap" id="also"><div class="concept-head"><span class="num">Also considered</span>'
      '<h2>Names I left out, and why</h2></div><div class="also">'
      + ''.join(f'<div><b>{esc(a)}</b><p>{esc(b)}</p></div>' for a, b in ALSO) + '</div></section>'),
     ('<section class="wrap" id="next"><div class="concept-head"><span class="num">Next steps</span>'
      '<h2>From here to launch</h2></div><ol class="next">' + ''.join(f'<li><span>{esc(x)}</span></li>' for x in NEXT)
      + '</ol></section>'),
     ('<footer class="wrap"><p>Domains were checked against the .com and .au registries on 16 October 2026; '
      '“check” means the .au registry rate-limited the lookup. Confirm with a registrar before buying. '
      'Name conflicts were checked with web searches only, so run a trade mark search before committing. '
      'Photos are from @cwatson.creative.</p></footer>'),
    ]
    head = (f'<title>Naming the Arch</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{GF}">\n<style>{CSS}</style>\n')
    body = '\n'.join(parts) + JS
    if standalone:
        return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + head + '</head>\n<body>\n' + body + '\n</body>\n</html>\n')
    return head + body + '\n'


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site4')
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w').write(build())
    open(os.path.join(out, 'standalone.html'), 'w').write(build(standalone=True))
    print('built', len(build()) // 1024, 'KB')
