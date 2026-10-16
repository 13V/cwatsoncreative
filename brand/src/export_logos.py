# Writes standalone SVGs for each shortlisted name into ../logos (relative to this file's folder by default).
import os, sys
from look import LOOK as L, wordmark, emblem
from page import NAMES

FONT_CSS = ("@import url('https://fonts.googleapis.com/css2?family=Marcellus"
            "&family=Cormorant+Garamond:ital,wght@1,500&family=Jost:wght@400&display=swap');")


def standalone(svg):
    svg = svg.replace('<svg class="" ', '<svg ', 1)
    i = svg.index('>') + 1
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + svg[:i] + f'<style><![CDATA[{FONT_CSS}]]></style>' + svg[i:] + '\n'


out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logos')
os.makedirs(out, exist_ok=True)
for n in NAMES:
    slug = n['name'].lower().replace(' & ', '-and-').replace('.', '').replace(' ', '-')
    files = {
        f'{slug}-wordmark.svg': wordmark(n['mark'], n['sub'], L['bark'], L['paddock'], L['bark'], label=n['name']),
        f'{slug}-badge.svg': emblem(n['mark'], 'PHOTOGRAPHY · ADELAIDE', L['bark'], L['bush'], bg=L['lime'], uid='a', label=f'{n["name"]} badge'),
        f'{slug}-badge-reversed.svg': emblem(n['mark'], 'PHOTOGRAPHY · ADELAIDE', L['lime'], L['lime'], bg=L['bush'], uid='b', label=f'{n["name"]} badge, reversed'),
    }
    for fn, svg in files.items():
        with open(os.path.join(out, fn), 'w') as f:
            f.write(standalone(svg))
        print(fn)
