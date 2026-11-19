#!/usr/bin/env python3
"""Generate the self-contained, accessible profile header (stdlib only)."""
from pathlib import Path
from html import escape
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'hero.svg'

parts = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 355" width="1200" height="355" role="img" aria-labelledby="title desc">
<title id="title">Emeline Cartier — Data Engineering et Open Source Intelligence</title>
<desc id="desc">En-tête sombre de style terminal, avec un réseau de points lumineux vert émeraude, une carte d'identité technique et un monogramme EC.</desc>
<defs>
  <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#09131d"/><stop offset="0.58" stop-color="#0a171d"/><stop offset="1" stop-color="#071015"/></linearGradient>
  <linearGradient id="accent" x1="0" x2="1"><stop stop-color="#6dfac2"/><stop offset="1" stop-color="#2ea8cb"/></linearGradient>
  <linearGradient id="panel" x1="0" x2="1"><stop stop-color="#0c202a"/><stop offset="1" stop-color="#0a171f"/></linearGradient>
  <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0 H0 V28" fill="none" stroke="#2a5360" stroke-width="0.6" opacity="0.28"/></pattern>
  <filter id="glow" x="-75%" y="-75%" width="250%" height="250%"><feGaussianBlur stdDeviation="4"/></filter>
  <style>
    .mono{font-family:'Consolas','Liberation Mono',monospace}
    .sans{font-family:'Segoe UI',Arial,sans-serif}
    .fine{fill:#8eafb9;font-size:13px;letter-spacing:1.4px}
    .code{fill:#70e6b8;font-size:14px}
    @keyframes blink {0%,49%{opacity:1}50%,100%{opacity:.15}}
    @keyframes fadein {0%{opacity:.45}50%{opacity:1}100%{opacity:.45}}
    @media (prefers-reduced-motion:reduce){*{animation:none!important}}
    .cursor{animation:blink 1.4s steps(1,end) infinite}
    .pulse{animation:fadein 3.4s ease-in-out infinite}
  </style>
</defs>
<rect x="1" y="1" width="1198" height="353" rx="24" fill="url(#bg)" stroke="#28434d" stroke-width="2"/>
<path d="M1 48 H1199" stroke="#28434d"/>
<circle cx="29" cy="25" r="5.5" fill="#fa6e69"/><circle cx="49" cy="25" r="5.5" fill="#f2c266"/><circle cx="69" cy="25" r="5.5" fill="#5ed5a0"/>
<text x="97" y="30" class="mono" fill="#9cbcc4" font-size="12" letter-spacing="1">/home/atomcrtr/profile/overview.sh</text>
<text x="1170" y="30" class="mono" fill="#64dcae" font-size="11" text-anchor="end">●  SYSTEM ONLINE</text>
<rect x="724" y="49" width="474" height="304" fill="url(#grid)" opacity="0.85"/>
<path d="M697 81 V327" stroke="#294451" stroke-dasharray="3 8"/>
<text x="47" y="91" class="mono code">atomcrtr@github:~$ whoami <tspan class="cursor">▌</tspan></text>
<text x="45" y="155" class="sans" font-weight="750" letter-spacing="1.5" font-size="47" fill="#f0f7f8">EMELINE CARTIER</text>
<rect x="47" y="176" width="400" height="3" rx="1.5" fill="url(#accent)"/>
<text x="48" y="211" class="mono" fill="#b6d9df" font-size="18">DATA ENGINEER  /  OSINT  /  GEOINT</text>
<text x="48" y="244" class="sans" fill="#89aab6" font-size="15">From raw data to traceable decisions.</text>
<rect x="47" y="276" width="155" height="33" rx="7" fill="#102f2b" stroke="#237e68"/>
<text x="124" y="298" font-family="Consolas,monospace" text-anchor="middle" font-size="12" fill="#87f4bd">●  PYTHON + SQL</text>
<rect x="214" y="276" width="184" height="33" rx="7" fill="#112a35" stroke="#24677a"/>
<text x="306" y="298" font-family="Consolas,monospace" text-anchor="middle" font-size="12" fill="#99cce4">⌘  INTELLIGENCE</text>
<text x="47" y="337" class="mono" fill="#6e8e9b" font-size="11">FRANCE  •  ENGINEERING / ANALYSIS / EVIDENCE</text>
<text x="746" y="82" class="mono fine">OPEN INTELLIGENCE / FIELD NOTES</text>
''']
# ambient radial/radar display at right
cx,cy=973,215
for radius in [46,86,126]:
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#296473" opacity="{0.58 if radius==126 else 0.44}" stroke-width="1.1"/>')
parts.append(f'<circle cx="{cx}" cy="{cy}" r="132" fill="none" stroke="#236a6a" stroke-dasharray="2 14" opacity=".4"/>')
parts.append(f'<path d="M{cx-145} {cy} H{cx+145} M{cx} {cy-139} V{cy+139}" stroke="#1f5764" stroke-width="1" stroke-dasharray="4 6" opacity=".44"/>')
# deterministic analytical graph (not data)
nodes = [(-115,-37),(-80,-96),(-33,-112),(48,-109),(112,-44),(89,32),(46,92),(-46,91),(-107,52),(-14,-38),(34,-27),(-43,18),(15,48)]
edges = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,0),(0,11),(1,9),(2,9),(3,10),(4,10),(5,12),(6,12),(7,11),(8,11),(9,10),(9,11),(10,12),(11,12),(9,12)]
for a,b in edges:
 x1,y1=nodes[a];x2,y2=nodes[b]
 parts.append(f'<path d="M{cx+x1} {cy+y1} L{cx+x2} {cy+y2}" stroke="#37bca0" stroke-width="1.5" opacity=".48"/>')
for i,(x,y) in enumerate(nodes):
 color='#78ffbf' if i in [9,10,11,12] else '#388f9d'
 r=4.8 if i in [9,10,11,12] else 3.4
 parts.append(f'<circle cx="{cx+x}" cy="{cy+y}" r="{r+6}" fill="{color}" opacity=".15" filter="url(#glow)"/>')
 parts.append(f'<circle cx="{cx+x}" cy="{cy+y}" r="{r}" fill="{color}" class="{"pulse" if i in [9,12] else ""}"/>')
parts.extend([f'<circle cx="{cx}" cy="{cy}" r="31" fill="#0b2225" stroke="#75e8b4" stroke-width="2"/>',
              f'<text x="{cx}" y="{cy+9}" class="mono" text-anchor="middle" fill="#b4ffe2" font-size="28" font-weight="bold">EC</text>',
              '<rect x="751" y="318" width="415" height="19" rx="4" fill="#0b222a"/>',
              '<text x="760" y="332" class="mono" fill="#6fabb5" font-size="10">DATA INTEGRITY   /   SOURCE EVALUATION   /   HUMAN REVIEW</text>',
              '</svg>'])
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text('\n'.join(parts),encoding='utf-8')
print(OUT)