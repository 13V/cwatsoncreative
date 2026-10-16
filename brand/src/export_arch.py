# Writes the arch logo for each shortlisted name (stacked and one-line) into ../logos/arch
import os, sys
from page4 import NAMES, lockup, lockup_line
from pwc import B as P

FONT_CSS = ("@import url('https://fonts.googleapis.com/css2?family=Marcellus"
            "&family=Cormorant+Garamond:ital,wght@1,500&family=Jost:wght@400&display=swap');")


def standalone(svg):
    svg = svg.replace('<svg class="" ', '<svg ', 1)
    i = svg.index('>') + 1
    return ('<?xml version="1.0" encoding="UTF-8"?>\n' + svg[:i] + f'<style><![CDATA[{FONT_CSS}]]></style>'
            + svg[i:] + '\n')


out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logos', 'arch')
os.makedirs(out, exist_ok=True)
n_files = 0
for n in NAMES:
    slug = n['name'].lower().replace(' & ', '-and-').replace('.', '').replace(' ', '-')
    for fn, svg in ((f'{slug}.svg', lockup(n['mark'], P['bark'], P['paddock'], P['bark'], 's')),
                    (f'{slug}-line.svg', lockup_line(n['mark'], P['bark'], P['paddock'], 'l'))):
        with open(os.path.join(out, fn), 'w') as f:
            f.write(standalone(svg))
        n_files += 1
print(n_files, 'files ->', os.path.abspath(out))
