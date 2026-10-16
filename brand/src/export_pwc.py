# Writes standalone SVGs for the five "Photos with Charne" directions into ../logos/photos-with-charne
import os, sys
from pwc import (B, badge_mark, badge_primary, arch_mark, arch_primary, sun_mark, sun_primary,
                 sig_mark, sig_primary, rainbow_mark, rainbow_primary)

FONT_CSS = ("@import url('https://fonts.googleapis.com/css2?family=Marcellus&family=Cormorant+Garamond:ital,wght@1,500"
            "&family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,100..900,0..100,0..1;1,9..144,100..900,0..100,0..1"
            "&family=Jost:wght@300;400;500&family=Ephesis&display=swap');")


def standalone(svg):
    svg = svg.replace('<svg class="" ', '<svg ', 1)
    i = svg.index('>') + 1
    return ('<?xml version="1.0" encoding="UTF-8"?>\n' + svg[:i] + f'<style><![CDATA[{FONT_CSS}]]></style>'
            + svg[i:] + '\n')


P = B
RB = [P['bark'], P['paddock'], P['bush'], P['gulf']]
FILES = {
    '1-badge.svg': badge_primary(P['bark'], P['paddock'], P['bush']),
    '1-badge-mark.svg': badge_mark(P['bark'], P['paddock'], P['bush'], bg=P['lime'], uid='m'),
    '2-arch.svg': arch_primary(P['bark'], P['paddock'], P['bush'], P['gulf'], P['lime']),
    '2-arch-mark.svg': arch_mark(P['bark'], P['paddock'], P['bush'], P['gulf'], P['lime'], uid='m'),
    '3-sun.svg': sun_primary(P['bark'], P['paddock'], P['paddock']),
    '3-sun-mark.svg': sun_mark(P['bark'], P['paddock'], bg=P['lime']),
    '4-signature.svg': sig_primary(P['bark'], P['paddock'], P['bush']),
    '4-signature-mark.svg': sig_mark(P['bark'], P['paddock'], bg=P['lime']),
    '5-rainbow.svg': rainbow_primary(RB, P['bark'], P['bark']),
    '5-rainbow-mark.svg': rainbow_mark(RB, bg=P['lime']),
}

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logos', 'photos-with-charne')
os.makedirs(out, exist_ok=True)
for fn, svg in FILES.items():
    with open(os.path.join(out, fn), 'w') as f:
        f.write(standalone(svg))
print(len(FILES), 'files ->', os.path.abspath(out))
