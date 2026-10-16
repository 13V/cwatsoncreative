# Builds the "Photos with Charne" logo round page into ./site3/
import os
from page import esc, img, grease_loop, FRAMES
from pwc import (B, badge_mark, badge_primary, arch_mark, arch_primary, sun_mark, sun_primary,
                 sig_mark, sig_primary, rainbow_mark, rainbow_primary)

GF = ('https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400..700;1,400..700'
      '&family=IBM+Plex+Mono:wght@400;500&family=Covered+By+Your+Grace&family=Marcellus'
      '&family=Cormorant+Garamond:ital,wght@1,500'
      '&family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,100..900,0..100,0..1;1,9..144,100..900,0..100,0..1'
      '&family=Jost:wght@300;400;500&family=Ephesis&display=swap')

CSS = r'''
:root{
  /* Layout: proof boards on a light table. Five logos up top as an overview, then one board per logo, then the size test and the pick. */
  --bg:#F1F1EE; --surface:#FFFFFF; --fg:#1B1C1A; --muted:#5C5E59; --line:#D8D9D3;
  --grease:#CC3B24;
  --sans:"Instrument Sans","Helvetica Neue",Arial,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --hand:"Covered By Your Grace","Marker Felt","Segoe Print","Comic Sans MS",cursive;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121311; --surface:#1A1B19; --fg:#ECEDE8; --muted:#A2A49D; --line:#2F312D; --grease:#FF6B4F; color-scheme:dark }}
:root[data-theme="dark"]{
  --bg:#121311; --surface:#1A1B19; --fg:#ECEDE8; --muted:#A2A49D; --line:#2F312D; --grease:#FF6B4F; color-scheme:dark }
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:400 17px/1.6 var(--sans);-webkit-font-smoothing:antialiased}
.wrap{max-width:1160px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
section.wrap{padding-block:64px}
section.wrap + section.wrap{border-top:1px solid var(--line)}
h1,h2,h3,h4{margin:0;text-wrap:balance}
h1{font-size:clamp(2.4rem,6vw,4.4rem);line-height:1.02;font-weight:600;letter-spacing:-.03em}
h2{font-size:clamp(1.6rem,3.2vw,2.3rem);line-height:1.12;font-weight:600;letter-spacing:-.02em}
h4{font:500 .74rem/1.3 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
p{margin:0;max-width:66ch}
ul{margin:0;padding:0;list-style:none}
a{color:inherit;text-underline-offset:3px;text-decoration-color:var(--muted)}
a:focus-visible{outline:2px solid var(--grease);outline-offset:3px;border-radius:2px}
.eyebrow{font:500 .74rem/1.4 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.lead{font-size:clamp(1.12rem,2vw,1.3rem);line-height:1.55;max-width:62ch}
.muted{color:var(--muted)}
.note{font-family:var(--hand);color:var(--grease);font-size:clamp(1.15rem,2.3vw,1.45rem);line-height:1.15;display:inline-block;transform:rotate(-2deg)}
.gc{position:absolute;left:-8%;top:-10%;width:116%;height:120%;color:var(--grease);pointer-events:none;overflow:visible}

.hero{padding-block:clamp(48px,8vw,88px) 48px;display:grid;gap:22px}
.overview{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-top:18px}
.overview a{text-decoration:none;display:grid;gap:8px}
.overview .card{aspect-ratio:1/1;background:#F6F2EA;border-radius:2px;display:grid;place-items:center;padding:12%;transition:transform .2s ease}
.overview a:hover .card{transform:translateY(-3px)}
.overview .card svg{width:100%;height:auto;max-height:100%}
.overview span{font:500 .74rem/1.3 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
@media (max-width:760px){.overview{grid-template-columns:repeat(3,minmax(0,1fr))}}
.palette{display:flex;flex-wrap:wrap;gap:10px 22px;margin-top:6px}
.palette div{display:flex;align-items:center;gap:8px;font-size:.88rem}
.palette i{width:22px;height:22px;border-radius:50%;box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)}
.palette code{font:400 .76rem var(--mono);color:var(--muted)}

.concept-head{display:grid;gap:8px;margin-bottom:26px;position:relative}
.concept-head .num{font:500 .8rem/1 var(--mono);color:var(--muted)}
.proofs{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr) minmax(0,1fr);gap:10px}
.proof{border-radius:2px;display:grid;place-items:center;padding:6%;aspect-ratio:1/1;min-width:0}
.proof.main{aspect-ratio:auto;padding:5% 7%}
.proof svg{width:100%;height:auto;max-height:100%}
.proof.mark svg{width:78%}
.photo{position:relative;border-radius:2px;overflow:hidden;aspect-ratio:1/1;min-width:0}
.photo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.photo::after{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(32,25,19,.8),rgba(32,25,19,.2) 60%,rgba(32,25,19,0))}
.photo .logo{position:absolute;left:12%;right:12%;bottom:7%;z-index:1}
.photo .logo svg{width:100%;height:auto;display:block}
.photo .logo.badge{left:30%;right:30%}
@media (max-width:760px){.proofs{grid-template-columns:repeat(2,minmax(0,1fr))}.proof.main{grid-column:1/-1}}
.notes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px 36px;margin-top:26px}
.notes ul{display:grid;gap:8px;margin-top:10px}
.notes li{padding-left:16px;position:relative;font-size:.97rem;line-height:1.5}
.notes li::before{content:"";position:absolute;left:0;top:.68em;width:7px;height:1.5px;background:var(--muted)}
.notes p{margin-top:10px;font-size:.97rem}
@media (max-width:860px){.notes{grid-template-columns:minmax(0,1fr)}}

.sizes{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px}
.size-col{display:grid;justify-items:center;gap:14px;background:#FFFFFF;border-radius:4px;padding:22px 10px 18px;color:#262626}
.size-col .av{width:110px;height:110px;border-radius:50%;overflow:hidden;display:grid;place-items:center}
.size-col .av.s{width:44px;height:44px}
.size-col .av svg{width:100%;height:100%}
.size-col .fav{display:flex;align-items:center;gap:10px}
.size-col .fav span{border-radius:3px;overflow:hidden;display:grid;place-items:center}
.size-col .fav svg{width:100%;height:100%}
.size-col b{font:500 .74rem/1.3 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:#5C5E59}
.size-legend{display:flex;flex-wrap:wrap;gap:6px 24px;margin-top:14px;font:400 .82rem/1.4 var(--mono);color:var(--muted)}
@media (max-width:760px){.sizes{grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:148px;overflow-x:auto;padding-bottom:8px}}

.pick{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:center;margin-top:28px}
@media (max-width:820px){.pick{grid-template-columns:minmax(0,1fr)}}
.pair{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px}
.pair .proof{aspect-ratio:1/1}
.pair .photo{aspect-ratio:1/1}
.check{display:grid;gap:6px;margin-top:20px}
.check li{font:400 .88rem/1.5 var(--mono)}
.ok{color:#2E7D4F}.chk{color:var(--muted)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .ok{color:#7BCB97}}
:root[data-theme="dark"] .ok{color:#7BCB97}
ol.next{margin:0;padding:0;list-style:none;counter-reset:n;display:grid;max-width:760px}
ol.next li{counter-increment:n;display:grid;grid-template-columns:2.4rem minmax(0,1fr);padding:14px 0;border-top:1px solid var(--line)}
ol.next li::before{content:counter(n);font:500 .9rem/1.7 var(--mono);color:var(--muted)}
footer.wrap{padding-block:36px 60px;border-top:1px solid var(--line);color:var(--muted);font-size:.86rem;display:grid;gap:8px}
@media (prefers-reduced-motion: reduce){*{transition:none!important;animation:none!important}}
'''

P = B
RB_LIGHT = [P['bark'], P['paddock'], P['bush'], P['gulf']]
RB_DARK = [P['paddock'], P['lime'], P['bush'], P['gulf']]

CONCEPTS = [
 dict(id='badge', n=1, name='The badge',
      line='The coastal badge you picked, now with the right name around the ring.',
      main=lambda: badge_primary(P['bark'], P['paddock'], P['bush']),
      rev_bg=P['bush'], rev=lambda u: badge_mark(P['lime'], P['paddock'], P['lime'], uid=u),
      photo=6, on=lambda u: badge_mark(P['paper'], P['paddock'], P['paper'], uid=u), on_cls='badge',
      av=lambda u: badge_mark(P['bark'], P['paddock'], P['bush'], bg=P['lime'], uid=u), av_bg=P['lime'],
      why=['Keeps the look you already chose: gum leaves for the hills, waves for the coast.',
           '“with” sits in gold italic where the ampersand used to be.',
           'Works as a stamp, a sticker on prints, and a mark on packaging.'],
      watch=['Below about 80 px the ring text turns to texture. The leaves and waves still read.'],
      best='Print, packaging and the website footer.'),
 dict(id='arch', n=2, name='The arch',
      line='A window onto her landscapes: sun over the hills, water at the bottom.',
      main=lambda: arch_primary(P['bark'], P['paddock'], P['bush'], P['gulf'], P['lime']),
      rev_bg=P['bark'], rev=lambda u: arch_mark(P['lime'], P['paddock'], P['bush'], P['gulf'], P['paper'], uid=u),
      photo=1, on=lambda u: arch_primary(P['paper'], P['paddock'], P['bush'], P['gulf'], P['paper'], uid=u).replace('fill="#5C4D3F"', 'fill="#F6F2EA"'), on_cls='',
      av=lambda u: arch_mark(P['bark'], P['paddock'], P['bush'], P['gulf'], P['lime'], uid=u), av_bg=P['paper'],
      why=['The most boho shape of the five, and an arch frames a view the way a photo does.',
           'The mark is a tiny version of her work: golden light, the hills, the coast.',
           'Reads clearly as an Instagram avatar.'],
      watch=['Arches are everywhere in boho branding right now, so this one may date sooner.'],
      best='Instagram, highlight covers and gift vouchers.'),
 dict(id='sun', n=3, name='The sun',
      line='Golden hour, her signature light, with her name in a soft 70s serif.',
      main=lambda: sun_primary(P['bark'], P['paddock'], P['paddock']),
      rev_bg=P['bark'], rev=lambda u: sun_mark(P['lime'], P['paddock']),
      photo=9, on=lambda u: sun_primary(P['paper'], P['paddock'], P['paper']), on_cls='',
      av=lambda u: sun_mark(P['bark'], P['paddock'], bg=P['lime']), av_bg=P['lime'],
      why=['Her name is the biggest thing in the logo, so it is the easiest to read and remember.',
           'The soft serif feels warm and friendly, which suits families and newborns.',
           'The sun mark is clear at every size, down to a 16 px browser tab.'],
      watch=['Sunset suns are common in coastal brands. The soft serif carries the personality.'],
      best='The website header and anywhere her name needs to be big.'),
 dict(id='signature', n=4, name='The signature',
      line='Her name in her own hand, with a gum leaf on the underline.',
      main=lambda: sig_primary(P['bark'], P['paddock'], P['bush']),
      rev_bg=P['bush'], rev=lambda u: sig_mark(P['paper'], P['paddock']),
      photo=11, on=lambda u: sig_primary(P['paper'], P['paddock'], P['paper']), on_cls='',
      av=lambda u: sig_mark(P['bark'], P['paddock'], bg=P['lime']), av_bg=P['lime'],
      why=['The most personal option. In Charne’s real handwriting it is one of a kind.',
           'Elegant enough for weddings, gentle enough for newborns.',
           'The best watermark of the five: light, and it signs the photo like a painting.'],
      watch=['This uses a stand-in script. The real version needs her to write it a few times on paper.'],
      best='Watermarks, thank-you cards and email signatures.'),
 dict(id='rainbow', n=5, name='The rainbow',
      line='Four soft stripes in every colour of the palette, for the family and newborn side.',
      main=lambda: rainbow_primary(RB_LIGHT, P['bark'], P['bark']),
      rev_bg=P['bark'], rev=lambda u: rainbow_mark(RB_DARK),
      photo=19, on=lambda u: rainbow_primary(RB_DARK, P['paper'], P['paper']), on_cls='',
      av=lambda u: rainbow_mark(RB_LIGHT, bg=P['lime']), av_bg=P['lime'],
      why=['Uses all the boho colours at once, so the palette is the logo.',
           'Warm and child-friendly, which fits the 20 of 35 posts that are bumps, newborns and families.',
           'Simple, bold and easy to read at any size.'],
      watch=['Leans towards nursery decor, so it suits weddings least.'],
      best='Newborn and family sessions, mini-session promos.'),
]


def li(xs):
    return ''.join(f'<li>{esc(x)}</li>' for x in xs)


def concept(c):
    u = c['id']
    photo = (f'<div class="photo">{img(c["photo"], alt="", lazy=False)}<div class="logo {c["on_cls"]}">{c["on"](u + "o")}</div></div>')
    return (f'<section class="wrap" id="{u}"><div class="concept-head"><span class="num">{c["n"]} of 5</span>'
            f'<h2>{esc(c["name"])}</h2><p class="muted">{esc(c["line"])}</p></div>'
            f'<div class="proofs"><div class="proof main" style="background:{P["paper"]}">{c["main"]()}</div>'
            f'<div class="proof mark" style="background:{c["rev_bg"]}">{c["rev"](u + "r")}</div>{photo}</div>'
            f'<div class="notes"><div><h4>Why it works</h4><ul>{li(c["why"])}</ul></div>'
            f'<div><h4>Watch for</h4><ul>{li(c["watch"])}</ul></div>'
            f'<div><h4>Best for</h4><p>{esc(c["best"])}</p></div></div></section>')


def overview():
    cards = ''
    for c in CONCEPTS:
        cards += (f'<a href="#{c["id"]}"><div class="card">{c["av"](c["id"] + "v")}</div>'
                  f'<span>{c["n"]} · {esc(c["name"])}</span></a>')
    pal = [('Paper', P['paper']), ('Limestone', P['lime']), ('Saltbush', P['bush']), ('Paddock', P['paddock']),
           ('Bark', P['bark']), ('Gulf', P['gulf'])]
    chips = ''.join(f'<div><i style="background:{h}"></i>{n} <code>{h}</code></div>' for n, h in pal)
    return f'<div class="overview">{cards}</div><div class="palette" aria-label="Palette">{chips}</div>'


def sizes():
    cols = ''
    for c in CONCEPTS:
        mk = lambda s: c['av'](f'{c["id"]}{s}')
        cols += (f'<div class="size-col"><div class="av" style="background:{c["av_bg"]}">{mk("a")}</div>'
                 f'<div class="av s" style="background:{c["av_bg"]}">{mk("b")}</div>'
                 f'<div class="fav"><span style="width:32px;height:32px;background:{c["av_bg"]}">{mk("c")}</span>'
                 f'<span style="width:16px;height:16px;background:{c["av_bg"]}">{mk("d")}</span></div>'
                 f'<b>{c["n"]} · {esc(c["name"])}</b></div>')
    return (f'<div class="sizes">{cols}</div><div class="size-legend"><span>110 px: Instagram profile</span>'
            f'<span>44 px: stories and comments</span><span>32 and 16 px: browser tab</span></div>')


def pick():
    b = CONCEPTS[0]; s = CONCEPTS[3]
    pair = (f'<div class="pair"><div class="proof" style="background:{P["lime"]};position:relative">{b["av"]("pk1")}'
            f'{grease_loop(311)}</div>'
            f'<div class="photo">{img(11, alt="", lazy=False)}<div class="logo">{s["on"]("pk2")}</div></div></div>')
    return (f'<div class="pick">{pair}<div><p class="lead">The badge as the logo, and her signature on the photos.</p>'
            f'<p class="muted" style="margin-top:14px">The badge carries the look you already chose, and now the name '
            f'fits it. It goes on the website, packaging, prints and stickers. A badge is heavy on a photo, so the '
            f'signature does that job: it signs each image lightly, the way a painter signs a canvas. If you only want '
            f'one logo, take the sun. It is the clearest at every size and puts her name first.</p>'
            f'<ul class="check"><li><span class="ok">✓</span> photoswithcharne.com <span class="muted">unregistered</span></li>'
            f'<li><span class="chk">?</span> photoswithcharne.com.au <span class="muted">check (registry rate-limited)</span></li>'
            f'<li><span class="chk">?</span> @photoswithcharne <span class="muted">check in the app</span></li>'
            f'<li><span class="ok">✓</span> web search <span class="muted">no business using the name</span></li></ul></div></div>')


NEXT = [
 'Pick one, or a pair like the badge with the signature.',
 'Charne writes “Charne” 20 or so times with a fine felt-tip. The best one gets vectorised for the signature.',
 'Register photoswithcharne.com.au (it needs an ABN) and the .com, and claim @photoswithcharne before announcing.',
 'Final files: outlined SVG and PNG, favicon, Instagram avatar, highlight covers and watermark.',
 'Build the website on the new brand.',
]


def build(standalone=False):
    hero = ('<header class="hero wrap"><p class="eyebrow">Logo round · Photos with Charne · October 2026</p>'
            '<h1>Photos with Charne</h1>'
            '<p class="lead">Five logo directions for the new name, all in the boho palette from the coastal badge. In '
            'each one, “with” takes over from the ampersand as the warm, gold, hand-made note.</p>'
            + overview() + '</header>')
    parts = [hero] + [concept(c) for c in CONCEPTS] + [
     ('<section class="wrap" id="sizes"><div class="concept-head"><span class="num">Size test</span>'
      '<h2>All five at Instagram and browser-tab size</h2><p class="muted">Most people meet the logo as a small circle '
      'first. This is that circle, at real size.</p></div>' + sizes() + '</section>'),
     ('<section class="wrap" id="pick"><div class="concept-head"><span class="num">My pick</span>'
      '<h2>The badge, signed</h2></div>' + pick() + '</section>'),
     ('<section class="wrap" id="next"><div class="concept-head"><span class="num">Next steps</span>'
      '<h2>From here to launch</h2></div><ol class="next">' + ''.join(f'<li><span>{esc(x)}</span></li>' for x in NEXT)
      + '</ol></section>'),
     ('<footer class="wrap"><p>The script in the signature direction is a stand-in until Charne writes her own. '
      'Domains were checked against the .com and .au registries on 16 October 2026; confirm with a registrar before buying. '
      'Photos are from @cwatson.creative.</p></footer>'),
    ]
    head = (f'<title>Photos with Charne Logos</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{GF}">\n<style>{CSS}</style>\n')
    body = '\n'.join(parts)
    if standalone:
        return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + head + '</head>\n<body>\n' + body + '\n</body>\n</html>\n')
    return head + body + '\n'


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site3')
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w').write(build())
    open(os.path.join(out, 'standalone.html'), 'w').write(build(standalone=True))
    print('built', len(build()) // 1024, 'KB')
