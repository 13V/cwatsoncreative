import math, random, sys
from logos import PAL, sig_primary, chap_primary, sun_primary, salt_primary
from look import LOOK as L, wordmark, wordmark_line, emblem

# ---------------------------------------------------------------- data
FRAMES = {
 1: ('wedding', 'Bride and groom lying in a green wheat field'),
 2: ('wedding', 'A dip outside a stone castle'),
 3: ('bump', 'Maternity on the beach below pale cliffs'),
 4: ('love', 'A lift at the water, shot into the light'),
 5: ('love', 'Couple among white and pink roses'),
 6: ('family', 'Parents and baby on a log under the gums'),
 7: ('family', 'Tiny figures under a sandstone portico'),
 8: ('family', 'Walking a golden paddock with a toddler'),
 9: ('love', 'A sunset dip at the water’s edge'),
 10: ('wedding', 'Hands: white dress, blush suit'),
 11: ('newborn', 'Newborn asleep in a parent’s arms'),
 12: ('milestone', 'Graduate by the river, Adelaide Oval behind'),
 13: ('family', 'Black-and-white family in the garden'),
 14: ('family', 'Mum and kids heading for the water'),
 15: ('newborn', 'New parents at home with their baby'),
 16: ('newborn', 'Newborn at the farm gate under a big gum'),
 17: ('bump', 'Golden hillside, ribbon in her hair'),
 18: ('family', 'Family walk on the beach'),
 19: ('family', 'Family of four on a log'),
 20: ('styling', 'A styled Christmas table'),
 21: ('family', 'Toddler walking to mum and dad on the sand'),
 22: ('wedding', 'Newlyweds by a vintage car'),
 23: ('milestone', 'Graduate holding her certificate'),
 24: ('milestone', 'Eighteenth birthday'),
 25: ('family', 'Studio portrait, baby lifted high'),
 26: ('love', 'Engagement portrait'),
 27: ('love', 'The proposal, in a rose garden'),
 28: ('bump', 'Baby shower cake and bump'),
 29: ('bump', 'Beach maternity, toddler on dad’s shoulders'),
 30: ('newborn', 'Newborn in a flower crown'),
 31: ('wedding', 'Reception dance floor'),
 32: ('wedding', 'Dried-flower bouquet'),
 33: ('family', 'Extended family in the park'),
 34: ('bump', 'Black-and-white pregnancy announcement'),
 35: ('family', 'In the park with their first baby'),
}
assert len(FRAMES) == 35
ROWS = [  # life order
 ('love', 'Love', 'proposals and couples', [27, 26, 4, 5, 9]),
 ('wedding', 'Weddings', '', [1, 2, 10, 22, 31, 32]),
 ('bump', 'Bump', 'announcements and maternity', [34, 28, 3, 17, 29]),
 ('newborn', 'Newborn', '', [11, 15, 16, 30]),
 ('family', 'Family', '', [35, 19, 6, 7, 8, 13, 14, 18, 21, 25, 33]),
 ('milestone', 'Milestones', 'graduations and an 18th', [12, 23, 24]),
 ('styling', 'Styling', 'events and tables', [20]),
]
for key, _, _, fr in ROWS:
    assert all(FRAMES[f][0] == key for f in fr), key
assert sum(len(r[3]) for r in ROWS) == 35
CIRCLED = {19, 29, 35}


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def img(n, cls='', alt=None, lazy=True):
    alt = esc(alt if alt is not None else f'Frame {n}: {FRAMES[n][1]}')
    return (f'<img class="{cls}" src="img/f{n:02d}.webp" alt="{alt}" width="242" height="291"'
            f'{" loading=\"lazy\"" if lazy else ""} decoding="async">')


# ---------------------------------------------------------------- grease pencil marks
def _smooth(pts):
    d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]; p1 = pts[i]; p2 = pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d


def grease_loop(seed, cls='gc'):
    rnd = random.Random(seed)
    start = rnd.uniform(0, 2 * math.pi)
    pts = []
    n = 26
    for i in range(n + 1):
        t = start + 2 * math.pi * 1.1 * i / n
        k = 1 + rnd.uniform(-0.03, 0.03) + 0.06 * i / n
        pts.append((50 + 46 * k * math.cos(t), 50 + 45 * k * math.sin(t)))
    return (f'<svg class="{cls}" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'
            f'<path d="{_smooth(pts)}" fill="none" stroke="currentColor" stroke-width="3" '
            f'stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>')


def grease_bracket():
    pts = [(17, 1), (9, 2.5), (7, 9), (7.6, 30), (6.8, 46), (2, 50), (7, 54), (7.4, 72), (6.6, 92), (9, 98), (17, 99)]
    return (f'<svg viewBox="0 0 20 100" preserveAspectRatio="none" aria-hidden="true">'
            f'<path d="{_smooth(pts)}" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" '
            f'stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>')


# ---------------------------------------------------------------- page parts
GF = ('https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400..700;1,400..700'
      '&family=IBM+Plex+Mono:wght@400;500&family=Covered+By+Your+Grace'
      '&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500'
      '&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,300'
      '&family=Jost:wght@300;400;500&family=Marcellus&family=Corinthia&display=swap')

CSS = r'''
:root{
  /* Layout: a photographer's light table. Her feed as a contact sheet first, then the chosen look and the name proofs pinned below it. */
  --bg:#F1F1EE; --surface:#FFFFFF; --fg:#1B1C1A; --muted:#5C5E59; --line:#D8D9D3; --soft:#E7E7E2;
  --film:#151514; --edge:#E2A240; --grease:#CC3B24;
  --sans:"Instrument Sans","Helvetica Neue",Arial,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --hand:"Covered By Your Grace","Marker Felt","Segoe Print","Comic Sans MS",cursive;
  --u:clamp(22px,4.4vw,54px);
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121311; --surface:#1A1B19; --fg:#ECEDE8; --muted:#A2A49D; --line:#2F312D; --soft:#22231F;
  --film:#050505; --edge:#E2A240; --grease:#FF6B4F; color-scheme:dark }}
:root[data-theme="dark"]{
  --bg:#121311; --surface:#1A1B19; --fg:#ECEDE8; --muted:#A2A49D; --line:#2F312D; --soft:#22231F;
  --film:#050505; --edge:#E2A240; --grease:#FF6B4F; color-scheme:dark }

*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:400 17px/1.6 var(--sans);-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
.wrap{max-width:1160px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
section.wrap{padding-block:72px}
section.wrap + section.wrap{border-top:1px solid var(--line)}
h1,h2,h3,h4{margin:0;text-wrap:balance}
h1{font-size:clamp(2.4rem,6vw,4.4rem);line-height:1.02;font-weight:600;letter-spacing:-.03em}
h2{font-size:clamp(1.65rem,3.4vw,2.4rem);line-height:1.12;font-weight:600;letter-spacing:-.02em}
h3{font-size:1.45rem;line-height:1.2;font-weight:600;letter-spacing:-.01em}
h4{font:500 .74rem/1.3 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
p{margin:0;max-width:66ch}
a{color:inherit;text-decoration-color:var(--muted);text-underline-offset:3px}
a:hover{text-decoration-color:currentColor}
a:focus-visible,button:focus-visible{outline:2px solid var(--grease);outline-offset:3px;border-radius:2px}
ul{margin:0;padding:0;list-style:none}
.eyebrow{font:500 .74rem/1.4 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.lead{font-size:clamp(1.12rem,2vw,1.3rem);line-height:1.55;max-width:60ch}
.muted{color:var(--muted)}
.note{font-family:var(--hand);color:var(--grease);font-size:clamp(1.15rem,2.3vw,1.45rem);line-height:1.15;display:inline-block;transform:rotate(-1.5deg)}
.sec-head{display:grid;gap:12px;margin-bottom:36px}
.sec-head p:not(.eyebrow){color:var(--muted)}

/* hero */
.hero{padding-block:clamp(48px,8vw,96px) 40px;display:grid;gap:22px}
.toc{display:flex;flex-wrap:wrap;gap:8px 18px;font:500 .8rem/1.4 var(--mono);text-transform:uppercase;letter-spacing:.06em;margin-top:6px}
.toc a{text-decoration:none;border-bottom:1px solid var(--line);padding-bottom:2px}
.toc a:hover{border-color:var(--fg)}

/* contact sheet */
.sheet{background:var(--film);padding:clamp(8px,1.6vw,18px);display:grid;gap:clamp(10px,1.6vw,16px);border-radius:3px}
.strip{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:clamp(3px,.9vw,10px)}
.frame{position:relative;margin:0}
.frame img{display:block;width:100%;height:auto;aspect-ratio:242/291;object-fit:cover;background:#2a2a28}
.frame figcaption{font:500 clamp(7px,1.25vw,11px)/1 var(--mono);color:var(--edge);margin-top:clamp(3px,.6vw,6px);letter-spacing:.08em;white-space:nowrap}
.frame figcaption span{opacity:.6}
.gc{position:absolute;left:-17%;top:-11%;width:134%;height:118%;color:var(--grease);pointer-events:none;overflow:visible}
.sheet-foot{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px 24px;margin-top:16px;align-items:baseline}

/* observations */
.obs-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,470px),1fr));gap:36px 44px}
.obs{display:grid;grid-template-columns:118px minmax(0,1fr);gap:20px;align-items:start}
.obs img{width:100%;height:auto;aspect-ratio:242/291;object-fit:cover;display:block}
.obs h3{font-size:1.2rem;margin-bottom:6px}
.obs p{color:var(--muted)}
@media (max-width:520px){.obs{grid-template-columns:84px minmax(0,1fr);gap:14px}}
.chips{display:grid;grid-template-columns:repeat(auto-fill,minmax(128px,1fr));gap:18px 14px;margin-top:44px}
.chip .sw{height:58px;border-radius:2px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)}
.chip b{display:block;font-size:.92rem;font-weight:600;margin-top:8px;line-height:1.3}
.chip code{font:400 .76rem/1.4 var(--mono);color:var(--muted)}
.chip small{display:block;font-size:.8rem;color:var(--muted);line-height:1.35}

/* sorted roll (unit chart: one photo = one post) */
.roll{display:grid;grid-template-columns:22px minmax(0,1fr);column-gap:12px;row-gap:14px}
.rrow{grid-column:2;display:grid;grid-template-columns:minmax(150px,220px) minmax(0,1fr);gap:16px;align-items:center}
.rrow .lab b{font-weight:600}
.rrow .lab small{display:block;color:var(--muted);font-size:.84rem;line-height:1.3}
.units{display:flex;align-items:center;gap:2px;min-width:0}
.units img{width:var(--u);height:auto;aspect-ratio:242/291;object-fit:cover;flex:none;display:block}
.units .n{font:500 .9rem/1 var(--mono);margin-left:10px;flex:none}
.units .note{margin-left:16px;font-size:clamp(1rem,2vw,1.35rem);white-space:nowrap}
.bracket{grid-column:1;color:var(--grease)}
.bracket svg{width:100%;height:100%;display:block;overflow:visible}
.roll-sum{margin-top:30px}
@media (max-width:640px){.rrow{grid-template-columns:minmax(0,1fr);gap:6px}}

/* brand today */
.kc{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,430px),1fr));gap:36px 56px}
.kc h3{margin-bottom:14px}
.kc li{padding:12px 0 12px 26px;border-top:1px solid var(--line);position:relative}
.kc li::before{content:"";position:absolute;left:2px;top:22px;width:10px;height:2px;background:var(--fg)}
.kc .keep li::before{height:10px;width:10px;top:18px;border-radius:50%;background:none;border:2px solid var(--fg)}

/* brief */
.brief{display:grid;grid-template-columns:minmax(120px,190px) minmax(0,1fr);gap:0 28px;margin:0}
.brief dt,.brief dd{padding:16px 0;border-top:1px solid var(--line);margin:0}
.brief dt{font:500 .74rem/1.9 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.brief dd ul{display:grid;gap:4px}
.brief dd li::before{content:"\2014\00a0";color:var(--muted)}
@media (max-width:560px){.brief{grid-template-columns:minmax(0,1fr)}.brief dd{border-top:0;padding-top:0}}

/* round one */
.r1{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
.r1 figure{margin:0;position:relative}
.r1 .card{aspect-ratio:16/10;display:grid;place-items:center;padding:8%;border-radius:2px}
.r1 .card svg{width:100%;height:auto}
.r1 figcaption{font:500 .74rem/1.4 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-top:8px}
.r1 .picked .gc{left:-7%;top:-12%;width:114%;height:124%}
.r1 .picked .note{position:absolute;right:-2%;bottom:-6px;transform:rotate(-4deg);background:var(--bg);padding:0 4px}
@media (max-width:720px){.r1{grid-template-columns:repeat(2,minmax(0,1fr))}}
.anat{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);gap:40px;align-items:center;margin-top:56px}
.anat .badge-big{background:#ECE6DB;border-radius:2px;padding:7%;display:grid;place-items:center}
.anat .badge-big svg{width:min(100%,380px);height:auto}
.anat ul{display:grid;gap:0}
.anat li{padding:13px 0;border-top:1px solid var(--line)}
.anat li b{font-weight:600}
.anat .chips{margin-top:26px;grid-template-columns:repeat(auto-fill,minmax(104px,1fr))}
@media (max-width:820px){.anat{grid-template-columns:minmax(0,1fr)}}

/* name proofs */
.names{display:grid;gap:64px}
.name{display:grid;gap:22px}
.name-head{display:grid;grid-template-columns:auto minmax(0,1fr);gap:4px 16px;align-items:baseline;position:relative}
.name-head .letter{font:500 .9rem/1 var(--mono);color:var(--muted);border:1px solid var(--line);border-radius:50%;width:2.1rem;height:2.1rem;display:grid;place-items:center;grid-row:span 2;align-self:start}
.name-head h3{font-size:clamp(1.5rem,3vw,2rem)}
.name-head p{color:var(--muted)}
.name-head .pickmark{position:relative;display:inline-block;margin-left:14px}
.name-head .pickmark .gc{left:-14%;top:-30%;width:128%;height:160%}
.proofs{display:grid;grid-template-columns:minmax(0,2.1fr) minmax(0,1fr) minmax(0,1fr);gap:10px}
.proof{display:grid;place-items:center;padding:5% 6%;border-radius:2px;min-height:0}
.proof svg{width:100%;height:auto}
.proof.badge svg{width:min(100%,220px)}
@media (max-width:760px){.proofs{grid-template-columns:repeat(2,minmax(0,1fr))}.proof.wide{grid-column:1/-1}}
.details{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px 36px}
.details ul{display:grid;gap:8px;margin-top:10px}
.details li{padding-left:16px;position:relative;font-size:.97rem;line-height:1.5}
.details li::before{content:"";position:absolute;left:0;top:.68em;width:7px;height:1.5px;background:var(--muted)}
.avail li::before{display:none}
.avail li{padding-left:0;font:400 .86rem/1.5 var(--mono)}
.ok{color:#2E7D4F}.no{color:#B23A2A}.chk{color:var(--muted)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .ok{color:#7BCB97}:root:not([data-theme="light"]) .no{color:#FF8A73}}
:root[data-theme="dark"] .ok{color:#7BCB97}:root[data-theme="dark"] .no{color:#FF8A73}
@media (max-width:860px){.details{grid-template-columns:minmax(0,1fr)}}

/* compare */
.tablewrap{overflow-x:auto}
table.cmp{border-collapse:collapse;width:100%;min-width:640px;font-size:.95rem}
.cmp th,.cmp td{padding:13px 12px;border-top:1px solid var(--line);text-align:left;vertical-align:middle}
.cmp thead th{font:500 .74rem/1.3 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted);border-top:0;position:relative}
.cmp thead th.pickcol{color:var(--fg)}
.cmp thead th.pickcol .gc{left:-8%;top:-20%;width:116%;height:140%}
.cmp td.dots{font-size:1.02rem;letter-spacing:.14em;white-space:nowrap}
.dots i{font-style:normal;color:var(--line)}
.cmp tbody th{font-weight:500;min-width:150px}

/* pick */
.pick-grid{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);gap:22px;align-items:start;margin-top:36px}
@media (max-width:900px){.pick-grid{grid-template-columns:minmax(0,1fr)}}
.site{background:#F6F2EA;color:#3F352B;border-radius:4px;overflow:hidden;box-shadow:0 1px 0 rgba(0,0,0,.04),0 12px 40px -18px rgba(0,0,0,.35)}
.site-url{font:400 .72rem/1 var(--mono);color:#7A6F63;background:#E9E3D8;padding:9px 14px}
.site-nav{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:14px 22px;border-bottom:1px solid #E3DCCF}
.site-nav .brand{display:flex;align-items:center;gap:10px;min-width:0}
.site-nav .brand svg{height:34px;width:auto;flex:none}
.site-nav .brand svg.wm{height:22px}
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
.ig-av{width:78px;height:78px;border-radius:50%;background:#ECE6DB;display:grid;place-items:center;flex:none;overflow:hidden}
.ig-av svg{width:88%;height:auto}
.ig-stats{display:flex;gap:14px;flex-wrap:wrap}
.ig-stats span{display:grid;text-align:center;font-size:12px;line-height:1.25}
.ig-stats b{font-size:15px}
.ig-handle{font-weight:700;font-size:14px;margin-top:12px}
.ig-name{font-weight:600}
.ig-cat{color:#737373}
.ig-bio{white-space:pre-line}
.ig-link{color:#00376B;font-weight:600}
.ig-hl{display:flex;gap:12px;margin-top:14px;overflow:hidden}
.ig-hl span{display:grid;justify-items:center;gap:4px;font-size:11px;flex:none}
.ig-hl img,.ig-hl .hl-badge{width:54px;height:54px;border-radius:50%;object-fit:cover;box-shadow:0 0 0 2px #fff,0 0 0 3.5px #8B937A}
.ig-hl .hl-badge{background:#ECE6DB;display:grid;place-items:center}
.ig-hl .hl-badge svg{width:46px;height:46px}
.ig-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:2px;margin:14px -16px -16px;border-radius:0 0 22px 22px;overflow:hidden}
.ig-grid img{width:100%;height:auto;aspect-ratio:3/4;object-fit:cover;display:block}
.bio{margin-top:28px;background:var(--surface);border:1px solid var(--line);border-radius:3px;padding:20px 22px;display:grid;gap:12px;max-width:640px}
.bio pre{margin:0;font:400 .95rem/1.55 var(--sans);white-space:pre-wrap}
.bio-bar{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.btn{font:500 .78rem/1 var(--mono);text-transform:uppercase;letter-spacing:.06em;background:var(--fg);color:var(--bg);border:0;border-radius:999px;padding:10px 16px;cursor:pointer}
.btn:hover{opacity:.88}
.runs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:20px 32px;margin-top:40px}
.runs div{border-top:1px solid var(--fg);padding-top:12px}
.runs p{color:var(--muted);font-size:.97rem;margin-top:6px}

/* also considered + next */
.also{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:0 40px}
.also div{padding:13px 0;border-top:1px solid var(--line)}
.also b{font-weight:600}
.also p{color:var(--muted);font-size:.95rem}
ol.next{margin:0;padding:0;list-style:none;counter-reset:n;display:grid;gap:0;max-width:760px}
ol.next li{counter-increment:n;display:grid;grid-template-columns:2.4rem minmax(0,1fr);padding:14px 0;border-top:1px solid var(--line)}
ol.next li::before{content:counter(n);font:500 .9rem/1.7 var(--mono);color:var(--muted)}
footer.wrap{padding-block:40px 64px;border-top:1px solid var(--line);color:var(--muted);font-size:.86rem;display:grid;gap:10px}
footer p{max-width:90ch}
@media (prefers-reduced-motion: reduce){*{transition:none!important;animation:none!important}}
'''


def section(id_, eyebrow, title, sub, body):
    sub_html = f'<p>{sub}</p>' if sub else ''
    return (f'<section class="wrap" id="{id_}"><div class="sec-head"><p class="eyebrow">{eyebrow}</p>'
            f'<h2>{title}</h2>{sub_html}</div>{body}</section>')


def contact_sheet():
    strips = []
    for s in range(5):
        cells = []
        for f in range(s * 7 + 1, s * 7 + 8):
            circ = grease_loop(f * 7) if f in CIRCLED else ''
            cap = FRAMES[f][1]
            cells.append(f'<figure class="frame" title="Frame {f}: {esc(cap)}">{img(f, lazy=False)}{circ}'
                         f'<figcaption>{f}<span> ▸</span></figcaption></figure>')
        strips.append(f'<div class="strip">{"".join(cells)}</div>')
    return (f'<div class="sheet" aria-label="All 35 posts from @cwatson.creative, newest first">{"".join(strips)}</div>'
            f'<div class="sheet-foot"><p class="eyebrow">@cwatson.creative · 35 posts · newest first</p>'
            f'<p class="note">Circled: looks like the same family, three shoots. First baby (35), '
            f'expecting again (29), family of four (19).</p></div>')


OBS = [
 (9, 'She shoots into the light.',
  'Backlit, golden and soft. Adelaide’s beaches face west, so the sun sets over the water, and she uses it '
  '(frames 4, 9 and 14). The edit stays clean and warm with true skin tones, and black and white is kept for the '
  'quieter moments (13 and 34).'),
 (3, 'Adelaide is in every frame.',
  'Pale cliffs and white sand, golden paddocks and gum trees, a rose garden, old sandstone, and Adelaide Oval '
  'behind a graduate (12). Clients see their own city in her work, and location pages (beaches, hills, gardens) are easy local search wins for the new site.'),
 (4, 'Movement over poses.',
  'Walking, lifting, dipping, running into the water. She prompts moments instead of lining people up. Clients '
  'mostly wear cream, white, linen and denim, which keeps the feed calm. A what-to-wear guide on the new site would '
  'make that part of the service.'),
 (29, 'Every chapter, and repeat clients.',
  'Proposals, weddings, pregnancy announcements, bumps, newborns, families, graduations and an 18th. At least one '
  'family has come back three times. Repeat clients are the most valuable thing in this feed, and the brand should '
  'make coming back feel natural.'),
]
FEED_PALETTE = [
 ('#EEEDEA', 'Salt white', 'the most common colour in the feed'),
 ('#BFB3A6', 'Limestone', 'the cliffs, frame 3'),
 ('#F1D4A2', 'Golden paddock', 'the hillside, frame 17'),
 ('#6B7049', 'Gum olive', 'the wheat field, frame 1'),
 ('#A7BBC3', 'Gulf blue', 'the sea, frame 21'),
 ('#8F7469', 'Dusty rose', 'the roses, frame 5'),
 ('#867665', 'Driftwood', 'the log, frame 19'),
 ('#131311', 'Night', 'the reception, frame 31'),
]


def chips(items):
    return '<div class="chips">' + ''.join(
        f'<div class="chip"><div class="sw" style="background:{h}"></div><b>{n}</b><code>{h}</code>'
        f'<small>{d}</small></div>' for h, n, d in items) + '</div>'


def observations():
    cards = ''.join(f'<div class="obs">{img(f)}<div><h3>{t}</h3><p>{p}</p></div></div>' for f, t, p in OBS)
    return (f'<div class="obs-grid">{cards}</div><h4 style="margin-top:56px">Colours sampled from her photos</h4>'
            + chips(FEED_PALETTE))


def roll():
    rows = []
    for i, (key, name, sub, frs) in enumerate(ROWS, 1):
        units = ''.join(img(f, alt=f'Frame {f}: {FRAMES[f][1]}') for f in frs)
        extra = '<span class="note">← 20 of 35 posts</span>' if key == 'newborn' else ''
        sub_html = f'<small>{sub}</small>' if sub else ''
        rows.append(f'<div class="rrow" style="grid-row:{i}"><div class="lab"><b>{name}</b>{sub_html}</div>'
                    f'<div class="units">{units}<span class="n">{len(frs)}</span>{extra}</div></div>')
    return (f'<div class="roll"><div class="bracket" style="grid-row:3 / span 3">{grease_bracket()}</div>'
            f'{"".join(rows)}</div>'
            '<p class="roll-sum">Bump, newborn and family make up 20 of the 35 posts. Couples and weddings make up 11. '
            'She is mainly a family photographer who also shoots weddings, so the name has to welcome both.</p>')


def brand_today():
    keep = [
     'Her eye and her edit. The light is consistent across very different shoots.',
     'Highlights already sorted by life stage: newborn, family, engagement, weddings. That is the website menu, ready made.',
     'A profile photo of her at work. People book people.',
     'The timing. With 213 followers and no domain registered, a new name costs almost nothing now.',
    ]
    change = [
     '“cwatson.creative” reads like a username and is awkward to say out loud. Word of mouth is how family photographers get booked.',
     '“Creative” sounds like an agency. <a href="https://www.g2.com/products/watson-creative/discuss" target="_blank" rel="noopener">Watson Creative</a> '
     'is already a branding agency, and searching “Watson” in Adelaide turns up '
     '<a href="https://all.accor.com/hotel/b3v6/index.en.shtml" target="_blank" rel="noopener">The Watson hotel</a>.',
     'Her first name, the most personal and distinctive part, is cut down to an initial.',
     'The bio says “Photographer” twice. It lists no services, no link and no next step.',
     'If “creative” is there because she also styles events (the Christmas table, frame 20), the bio can say '
     '“photography & styling” instead.'.replace('&', '&amp;'),
    ]
    li = lambda xs: ''.join(f'<li>{x}</li>' for x in xs)
    return (f'<div class="kc"><div class="keep"><h3>Keep</h3><ul>{li(keep)}</ul></div>'
            f'<div class="change"><h3>Change</h3><ul>{li(change)}</ul></div></div>')


def brief():
    must = ['sound like Charne, not a café or an agency',
            'be easy to say and spell when a friend passes it on',
            'work as a clean Instagram handle next to her personal @charne.watson',
            'have a domain that is free to register',
            'sit naturally inside the badge']
    return ('<dl class="brief">'
            '<dt>Position</dt><dd>Natural, light-filled photography for Adelaide couples and families, from the proposal to the graduation.</dd>'
            '<dt>For</dt><dd>Couples and young families around Adelaide who want photos that look like them on a good day. They find her through Instagram, friends and Google.</dd>'
            '<dt>Feels</dt><dd>Warm, unfussy, sun-lit, local. Never glossy, stiff or trendy.</dd>'
            '<dt>The name must</dt><dd><ul>' + ''.join(f'<li>{m}</li>' for m in must) + '</ul></dd></dl>')


def the_look():
    s, c, u, g = PAL['sig'], PAL['chap'], PAL['sun'], PAL['salt']
    cards = [
     (s['paper'], sig_primary(s['ink'], s['drift']), 'A · Editorial serif', False),
     (c['page'], chap_primary(c['ink'], c['gilt'], c['gum']), 'B · Storybook', False),
     (u['salt'], sun_primary(u['char'], u['honey'], u['deep']), 'C · Modern sun', False),
     (g['lime'], salt_primary(g['bark'], g['paddock'], g['bark']), 'D · Coastal badge', True),
    ]
    figs = ''
    for bg, logo, cap, picked in cards:
        mark = grease_loop(41) + '<span class="note">your pick</span>' if picked else ''
        figs += (f'<figure class="{"picked" if picked else ""}"><div class="card" style="background:{bg}">{logo}</div>'
                 f'<figcaption>{cap}</figcaption>{mark}</figure>')
    anat = [
     ('The ring', 'carries the name on top and “photography · adelaide” underneath, so it works on its own as an avatar or a stamp.'),
     ('Gum leaves', 'for the hills: the golden paddocks and the log-under-the-gums family sessions.'),
     ('Waves', 'for the coast, where most of her golden-hour sessions happen.'),
     ('The ampersand', 'in Cormorant italic and paddock gold. It is the warm, hand-made note in an otherwise calm logo.'),
     ('Type', 'Marcellus for the name, Cormorant Garamond for headlines, Jost for small labels.'),
    ]
    pal = [(L['lime'], 'Limestone', 'backgrounds'), (L['bush'], 'Saltbush', 'leaves, reverse badge'),
           (L['paddock'], 'Paddock', 'ampersand, accents'), (L['bark'], 'Bark', 'text and line work'),
           (L['gulf'], 'Gulf', 'waves, links')]
    big = emblem('SALT & GUM', 'PHOTOGRAPHY · ADELAIDE', L['bark'], L['bush'], uid='anat', label='The coastal badge from round one')
    return (f'<div class="r1">{figs}</div>'
            f'<div class="anat"><div class="badge-big">{big}</div><div><h3 style="margin-bottom:12px">What stays from round one</h3><ul>'
            + ''.join(f'<li><b>{a}</b> {b}</li>' for a, b in anat) + '</ul>' + chips(pal) + '</div></div>')


NAMES = [
 dict(key='a', letter='A', name='Charne Watson', mark='CHARNE WATSON', sub='PHOTOGRAPHY · COAST & HILLS',
      line='Her full name, in the look you picked.',
      why=['The most personal option. People book a person, and for newborns and weddings, trust in that person is the whole sale.',
           'A web search for “Charne Watson” photographer finds nothing, so her site would own the results for her name.',
           'Nothing to explain, and it suits every kind of shoot she does.'],
      watch=['It is a name more than a brand, so the badge and palette do the brand work.',
             'The handle needs a suffix (@charnewatson.photo) because @charne.watson is her personal account.'],
      avail=[('ok', 'charnewatson.com', 'unregistered'), ('ok', 'charnewatson.com.au', 'unregistered'),
             ('chk', '@charnewatson.photo', 'check in the app')]),
 dict(key='b', letter='B', name='Charne & Co.', mark='CHARNE & CO.', sub='PHOTOGRAPHY · ADELAIDE',
      line='Her first name, with the ampersand you liked.', pick=True,
      why=['Personal and brand-like at once. It sounds like a small studio that friends recommend to each other.',
           'Keeps the italic ampersand, the detail that made the Salt & Gum logo feel hand-made.',
           '“& Co.” can mean the families she photographs, and leaves room to grow: styling, a second shooter, prints.',
           'A clean handle, @charneandco, that will not get mixed up with her personal @charne.watson.'],
      watch=['“& Co.” is a familiar pattern, so the badge and the photos carry the distinctiveness.',
             'Some people will read “& Co.” as a team. A clear About page with her photo settles that.'],
      avail=[('ok', 'charneandco.com', 'unregistered'), ('chk', 'charneandco.com.au', 'check'),
             ('chk', '@charneandco', 'check in the app')]),
 dict(key='c', letter='C', name='Saltbush', mark='SALTBUSH', sub='PHOTOGRAPHY BY CHARNE WATSON',
      line='The Salt & Gum idea, in one real word.',
      why=['Saltbush is a silvery native shrub found across South Australia, and the word itself says salt and bush: coast and hills.',
           'One word is easy to remember and to say.',
           'Its silvery green is already the badge colour.'],
      watch=['Not personal on its own, so “photography by Charne Watson” has to sit under it everywhere.',
             'saltbushphotography.com is taken, and South Australians also know saltbush from restaurant menus and lamb.'],
      avail=[('no', 'saltbushphotography.com', 'taken'), ('chk', 'saltbush.com.au variants', 'check'),
             ('chk', '@saltbush.photo', 'check in the app')]),
 dict(key='d', letter='D', name='Paperbark', mark='PAPERBARK', sub='PHOTOGRAPHY BY CHARNE WATSON',
      line='Paper for the prints, bark for the trees she shoots under.',
      why=['A native tree with soft, layered bark: tactile, calm and Australian.',
           '“Paper” quietly points at prints and albums, which are worth selling.',
           'A web search found no Australian photographer using it.'],
      watch=['Not personal on its own; it needs “by Charne Watson” underneath.',
             'Common in other industries: cafés, stays and homewares.'],
      avail=[('ok', 'paperbarkphotography.com', 'unregistered'), ('chk', 'paperbark.com.au variants', 'check'),
             ('chk', '@paperbark.photo', 'check in the app')]),
 dict(key='e', letter='E', name='Kin & Coast', mark='KIN & COAST', sub='PHOTOGRAPHY BY CHARNE WATSON',
      line='Families and the beach, with the ampersand kept.',
      why=['Says who and where in three words: families (kin) on the Adelaide coast.',
           'Keeps the two-words-and-an-ampersand shape of Salt & Gum.'],
      watch=['The least personal option, and it leaves out the hills, the weddings and the studio work.',
             'kinandcoast.com is taken.'],
      avail=[('no', 'kinandcoast.com', 'taken'), ('ok', 'kinandcoastphotography.com', 'unregistered'),
             ('chk', '@kinandcoast', 'check in the app')]),
]


def name_board(n):
    wm = wordmark(n['mark'], n['sub'], L['bark'], L['paddock'], L['bark'], label=n['name'])
    e1 = emblem(n['mark'], 'PHOTOGRAPHY · ADELAIDE', L['bark'], L['bush'], uid=n['key'] + '1', label=f'{n["name"]} badge')
    e2 = emblem(n['mark'], 'PHOTOGRAPHY · ADELAIDE', L['lime'], L['lime'], uid=n['key'] + '2', label=f'{n["name"]} badge, reversed')
    pick = (f'<span class="pickmark"><span class="note">my pick</span>{grease_loop(97)}</span>' if n.get('pick') else '')
    li = lambda xs: ''.join(f'<li>{esc(x)}</li>' for x in xs)
    av = ''.join(f'<li><span class="{c}">{"✓" if c == "ok" else ("✗" if c == "no" else "?")}</span> {d} '
                 f'<span class="muted">{s}</span></li>' for c, d, s in n['avail'])
    return (f'<article class="name" id="name-{n["key"]}"><div class="name-head"><span class="letter">{n["letter"]}</span>'
            f'<h3>{esc(n["name"])}{pick}</h3><p>{esc(n["line"])}</p></div>'
            f'<div class="proofs"><div class="proof wide" style="background:{L["lime"]}">{wm}</div>'
            f'<div class="proof badge" style="background:{L["lime"]}">{e1}</div>'
            f'<div class="proof badge" style="background:{L["bush"]}">{e2}</div></div>'
            f'<div class="details"><div><h4>Why it fits</h4><ul>{li(n["why"])}</ul></div>'
            f'<div><h4>Watch for</h4><ul>{li(n["watch"])}</ul></div>'
            f'<div><h4>Availability</h4><ul class="avail">{av}</ul></div></div></article>')


def compare():
    crit = [('Sounds like Charne', [5, 4, 2, 2, 2]),
            ('Easy to say and spell', [3, 3, 5, 5, 5]),
            ('Feels like a brand', [3, 5, 4, 4, 4]),
            ('Free domain and handle', [4, 4, 2, 4, 3]),
            ('Fits the badge', [4, 5, 5, 4, 5])]
    head = ''.join(
        f'<th scope="col" class="{"pickcol" if n.get("pick") else ""}">{n["letter"]} · {esc(n["name"])}'
        f'{grease_loop(53) if n.get("pick") else ""}</th>' for n in NAMES)
    rows = ''
    for label, scores in crit:
        cells = ''.join(f'<td class="dots" aria-label="{v} of 5">{"●" * v}<i>{"●" * (5 - v)}</i></td>' for v in scores)
        rows += f'<tr><th scope="row">{label}</th>{cells}</tr>'
    return (f'<div class="tablewrap"><table class="cmp"><thead><tr><th scope="col">Scored 1 to 5</th>{head}</tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
            '<p class="muted" style="margin-top:14px;font-size:.92rem">My judgement, not a formula. Domains are from the registry checks above.</p>')


BIO = ('Natural, light-filled photos for Adelaide couples & families.\n'
       'Weddings · Bump · Newborn · Family\n'
       'Coast, hills & home. Enquire below ↓')


def pick():
    nav_badge = emblem('CHARNE & CO.', 'PHOTOGRAPHY · ADELAIDE', L['bark'], L['bush'], uid='nav', label='Charne & Co. badge')
    nav_wm = wordmark_line('CHARNE & CO.', L['bark'], L['paddock'], label='Charne & Co.').replace('<svg class=""', '<svg class="wm"')
    av = emblem('CHARNE & CO.', 'PHOTOGRAPHY · ADELAIDE', L['bark'], L['bush'], uid='av', label='Charne & Co. badge')
    hlb = emblem('CHARNE & CO.', 'PHOTOGRAPHY · ADELAIDE', L['bark'], L['bush'], uid='hl', label='Kind words')
    site = (f'<div class="site" aria-label="Homepage mock-up"><div class="site-url">charneandco.com.au</div>'
            f'<div class="site-nav"><div class="brand">{nav_badge}{nav_wm}</div>'
            f'<nav><span>Portfolio</span><span>About</span><span>Investment</span><span>Enquire</span></nav></div>'
            f'<div class="site-hero"><div class="site-copy"><span class="se">ADELAIDE PHOTOGRAPHER</span>'
            f'<span class="sh">Photographs of your people, by the sea and under the gums.</span>'
            f'<span class="ss">Natural, light-filled sessions for couples and families, from the proposal to the graduation.</span>'
            f'<span class="sb">Check my dates</span></div>{img(14, lazy=True)}</div></div>')
    hls = [(4, 'Couples'), (2, 'Weddings'), (3, 'Bump'), (16, 'Newborn'), (18, 'Family')]
    hl_html = ''.join(f'<span>{img(f, alt="")}{lab}</span>' for f, lab in hls[:4])
    hl_html += f'<span><span class="hl-badge">{hlb}</span>Kind words</span>'
    ig = (f'<div class="ig" aria-label="Instagram profile mock-up"><div class="ig-head"><div class="ig-av">{av}</div>'
          f'<div class="ig-stats"><span><b>35</b>posts</span><span><b>213</b>followers</span><span><b>39</b>following</span></div></div>'
          f'<div class="ig-handle">charneandco</div><div class="ig-name">Charne &amp; Co. · Photographer</div>'
          f'<div class="ig-bio">{esc(BIO)}</div>'
          f'<div class="ig-link">charneandco.com.au</div><div class="ig-hl">{hl_html}</div>'
          f'<div class="ig-grid">{img(21)}{img(17)}{img(16)}</div></div>')
    runs = [
     ('Website', 'Home, Portfolio (Love, Weddings, Bump, Newborn, Family, Milestones), About Charne, Investment, Enquire.'),
     ('Instagram', '@charneandco, with highlights renamed to match the website menu.'),
     ('Avatar', 'The badge works, and a warm portrait of Charne works even better, because people book people. Either way the badge goes on highlights, the site, the favicon and packaging.'),
     ('Watermark', 'The one-line wordmark in white at about 60% opacity, small, in a bottom corner.'),
    ]
    return (f'<p class="lead">It is the only option that is both her and a brand. Her first name stays up front, the '
            f'ampersand that made Salt &amp; Gum work stays in the logo, and the handle and domain are clean. If you '
            f'would rather it be her alone, Charne Watson uses the same badge and palette, so switching later costs '
            f'nothing.</p>'
            f'<div class="pick-grid">{site}{ig}</div>'
            f'<div class="bio"><div class="bio-bar"><h4>Instagram bio, ready to paste</h4>'
            f'<button class="btn" id="copy-bio" type="button">Copy bio</button></div><pre id="bio-text">{esc(BIO)}</pre>'
            f'<p class="muted" style="font-size:.86rem">Name field: Charne &amp; Co. · Photographer. Hide the category label so “Photographer” '
            f'does not appear twice. {len(BIO)} of 150 characters.</p></div>'
            f'<div class="runs">' + ''.join(f'<div><h4>{a}</h4><p>{b}</p></div>' for a, b in runs) + '</div>')


ALSO = [
 ('Linen & Light', 'Describes her look exactly, but linenandlight.com is taken and it is not personal.'),
 ('Golden Wattle', 'Golden-hour colour and Australia’s floral emblem. Sounds more like a plant nursery than a studio.'),
 ('Westerly', 'Adelaide’s beaches face west, so sunsets land on the water. Too subtle for most people to get.'),
 ('Sandstone', 'Adelaide’s old buildings and cliffs. Solid, but cold for newborns and families.'),
 ('First Light', 'Lovely for newborns, but generic.'),
 ('Charne Creative', 'Keeps a word from the old name, but still reads like an agency.'),
]
NEXT = [
 'Pick a name, or tell me what is missing and I will run a third round.',
 'Check it properly: the ASIC business names register and IP Australia’s trade mark search, then register the business name.',
 'Register the domain (.com.au needs an ABN) and claim the Instagram handle before announcing anything.',
 'Final logo files: outlined SVG and PNG, favicon, Instagram avatar and watermark.',
 'Build the website on the new brand.',
]

JS = r'''
<script>
(function(){
  var btn=document.getElementById('copy-bio'), pre=document.getElementById('bio-text');
  if(!btn||!pre) return;
  btn.addEventListener('click',function(){
    var text=pre.textContent;
    var done=function(msg){btn.textContent=msg;setTimeout(function(){btn.textContent='Copy bio';},2200);};
    var select=function(){var r=document.createRange();r.selectNodeContents(pre);var s=window.getSelection();s.removeAllRanges();s.addRange(r);done('Selected. Press Ctrl+C');};
    try{ navigator.clipboard.writeText(text).then(function(){done('Copied');},select); }catch(e){ select(); }
  });
})();
</script>'''


def build(standalone=False):
    hero = ('<header class="hero wrap"><p class="eyebrow">Brand exploration · @cwatson.creative · Round two · October 2026</p>'
            '<h1>Rebranding cwatson.creative</h1>'
            '<p class="lead">I read all 35 posts like a contact sheet. Charne’s work is warm, light-filled and very '
            'Adelaide, and it follows families from the proposal to the graduation. Round one settled the look, the '
            'coastal badge with gum leaves over the water. This round finds a name that sounds like her.</p>'
            '<nav class="toc" aria-label="On this page"><a href="#feed">The feed</a><a href="#today">Brand today</a>'
            '<a href="#brief">The brief</a><a href="#look">The look</a><a href="#names">Five names</a>'
            '<a href="#compare">Compare</a><a href="#pick">My pick</a><a href="#next">Next steps</a></nav></header>')
    parts = [
     hero,
     section('feed', 'The feed', 'Her whole feed, as a contact sheet',
             'All 35 posts, numbered the way frames are on a roll of film.', contact_sheet()),
     section('style', 'Her style', 'What her photos say', '', observations()),
     section('sorted', 'The mix', 'Sorted by stage of life',
             'In posting order the feed reads as a mix. Sorted, it is one story, and most of it is growing families. One photo is one post.', roll()),
     section('today', 'Brand today', 'What to keep, what to change', '', brand_today()),
     section('brief', 'The brief', 'What the new brand has to do', '', brief()),
     section('look', 'Round one', 'The coastal badge stays',
             'Round one showed four looks. You picked D, but none of the names fit. The badge, type and palette carry over, and only the name changes.', the_look()),
     section('names', 'Round two', 'Five names, set in that look',
             'Two built on her name, three built on the place with her name underneath. Each shows the wordmark, the badge, and the badge reversed.',
             '<div class="names">' + ''.join(name_board(n) for n in NAMES) + '</div>'),
     section('compare', 'Compare', 'Side by side', '', compare()),
     section('pick', 'My pick', 'Charne &amp; Co.', '', pick()),
     section('also', 'Also considered', 'Names I left out, and why', '',
             '<div class="also">' + ''.join(f'<div><b>{esc(a)}</b><p>{b}</p></div>' for a, b in ALSO) + '</div>'),
     section('next', 'Next steps', 'From here to launch', '',
             '<ol class="next">' + ''.join(f'<li><span>{x}</span></li>' for x in NEXT) + '</ol>'),
     ('<footer class="wrap"><p>Method: all 35 posts on @cwatson.creative, read from screenshots on 16 October 2026. '
      'Colours sampled from the photos. Domains checked against the .com and .au registries the same day; '
      '“check” means the .au registry rate-limited the lookup or the handle needs checking in the Instagram app. '
      'Confirm with a registrar before buying, and run a trade mark search before committing to a name.</p>'
      '<p>Name conflicts were checked with web searches only.</p></footer>'),
    ]
    head = (f'<title>cwatson.creative Rebrand</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{GF}">\n<style>{CSS}</style>\n')
    body = '\n'.join(parts) + JS
    if standalone:
        return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + head + '</head>\n<body>\n' + body + '\n</body>\n</html>\n')
    return head + body + '\n'


if __name__ == '__main__':
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w').write(build())
    open(os.path.join(out, 'standalone.html'), 'w').write(build(standalone=True))
    print('built', len(build()) // 1024, 'KB')
