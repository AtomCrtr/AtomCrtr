#!/usr/bin/env python3
"""Fetch AtomCrtr's GitHub contribution calendar and render a first-party SVG.

Usage:
  GH_TOKEN=<GitHub Actions GITHUB_TOKEN> python scripts/build_contributions.py
  python scripts/build_contributions.py --offline  # visually honest skeleton

Only public profile contributions exposed by GitHub's GraphQL endpoint are used.
No third-party badge services, user secrets or fabricated contribution counts.
"""
import argparse
from datetime import date
from html import escape
import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen

USER = 'AtomCrtr'
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'contributions.svg'
API = 'https://api.github.com/graphql'
QUERY = '''query ProfileContributions($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          firstDay
          contributionDays { date contributionCount contributionLevel }
        }
      }
    }
  }
}'''
COLORS = {
    'NONE': '#17282f',
    'FIRST_QUARTILE': '#155d49',
    'SECOND_QUARTILE': '#1b9665',
    'THIRD_QUARTILE': '#28c184',
    'FOURTH_QUARTILE': '#82f7bd',
}

def fetch_calendar(token: str) -> dict:
    if not token:
        raise RuntimeError('GH_TOKEN non défini : génération réelle impossible (pas de chiffres fictifs).')
    payload = json.dumps({'query': QUERY, 'variables': {'login': USER}}).encode()
    request = Request(API, data=payload, headers={
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'AtomCrtr-GitHub-Profile-Readme',
    }, method='POST')
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError(f'GraphQL: {result["errors"]}')
    user = result.get('data', {}).get('user')
    if not user:
        raise RuntimeError(f'Profil GitHub {USER!r} inaccessible.')
    calendar = user['contributionsCollection']['contributionCalendar']
    if not calendar.get('weeks'):
        raise RuntimeError('Le calendrier GitHub est vide : aucune valeur ne sera inventée.')
    return calendar


def text(x, y, value, size=14, color='#a5c3c9', weight='normal', anchor='start', family='Consolas, monospace', **extra):
    attr = ' '.join(f'{escape(str(k).replace("_", "-"))}="{escape(str(v))}"' for k,v in extra.items())
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" font-family="{family}" {attr}>{escape(str(value))}</text>'


def render(calendar: dict | None) -> str:
    weeks = (calendar or {}).get('weeks', [])
    days = [d for w in weeks for d in w.get('contributionDays', [])]
    count = calendar.get('totalContributions') if calendar else None
    active = sum(d['contributionCount'] > 0 for d in days) if calendar else None
    maximum = max((d['contributionCount'] for d in days), default=0) if calendar else None
    peak = max((d for d in days if d['contributionCount'] > 0), key=lambda d:(d['contributionCount'],d['date']), default=None) if calendar else None
    W,H=1200,366
    p=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">Historique GitHub : 12 mois de contributions de {USER}</title>
<desc id="desc">{escape('Calendrier de contributions GitHub réelles sur douze mois.' if calendar else 'En attente de la première synchronisation automatique des données GitHub.')}</desc>
<defs><linearGradient id="background" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0a151d"/><stop offset="1" stop-color="#0b2025"/></linearGradient></defs>
<rect x="1" y="1" width="1198" height="364" rx="22" fill="url(#background)" stroke="#2b5057" stroke-width="2"/>
<circle cx="32" cy="32" r="5" fill="#60efb0"/>
''']
    p += [text(48,37,'atomcrtr@github:~$ ./contributions.sh',16,'#7af1bb'),
          text(1157,36, 'LIVE · GITHUB GRAPHQL' if calendar else 'PENDING · FIRST WORKFLOW',11,'#8eabb4',anchor='end'),
          '<path d="M25 57 H1175" stroke="#24424c" stroke-width="1"/>',
          text(38,88,'CONTRIBUTION CALENDAR / LAST 12 MONTHS',11,'#84a4ae'),
          text(827,88,'ACTIVITY INTELLIGENCE',11,'#84a4ae')]
    p.append('<path d="M794 76 V338" stroke="#2c5359" stroke-dasharray="3 7"/>')
    x0,y0 = 52,132
    cell=10; sep=3
    # week cells: use 53 columns, consistently right-aligned if fewer
    if calendar:
        offset = max(0, 53-len(weeks))
        dates=[]
        for wi,week in enumerate(weeks):
            for day in week.get('contributionDays',[]):
                # GraphQL calendar weeks use Sunday-Saturday; date weekday() maps Monday=0.
                week_day = (date.fromisoformat(day['date']).weekday()+1)%7
                x=x0+(wi+offset)*(cell+sep)
                y=y0+week_day*(cell+sep)
                color=COLORS.get(day.get('contributionLevel'), '#17282f')
                p.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.3" fill="{color}"/>')
                dates.append((wi,day['date']))
        months={}
        for wi,ds in dates:
            ym=ds[:7]
            if ym not in months: months[ym]=wi+offset
        if len(months)>12:
            months=dict(list(months.items())[-12:])
        names=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        for ym,wi in months.items():
            p.append(text(x0+wi*(cell+sep),118,names[int(ym[5:7])-1],10,'#7fa7ad'))
    else:
        # Skeleton is intentionally neutral. It never suggests invented contributions.
        for wi in range(53):
            for day in range(7):
                p.append(f'<rect x="{x0+wi*(cell+sep)}" y="{y0+day*(cell+sep)}" width="{cell}" height="{cell}" rx="2.3" fill="#1c2f36"/>')
        p += [text(400,248,'AWAITING INITIAL SYNC',16,'#83abb2',weight='bold',anchor='middle'),
              text(400,266,'No contribution statistics are shown yet',11,'#658c98',anchor='middle')]
    for wd,yy in [('S',140),('T',166),('T',192),('S',218)]:
        p.append(text(33,yy,wd,10,'#61818a'))
    p += [text(52,275,'LESS',10,'#7798a1')]
    for i,c in enumerate(COLORS.values()):
        p.append(f'<rect x="{92+i*16}" y="265" width="11" height="11" rx="2" fill="{c}"/>')
    p.append(text(184,275,'MORE',10,'#7798a1'))
    p.append(text(52,323,'PUBLIC PROFILE ACTIVITY  •  AUTOMATIC DAILY REFRESH',11,'#6c929a'))
    # Metrics panel. Values from GitHub only; placeholders show a dash.
    def metric(x,y,label,value):
        p.append(text(x,y,label,11,'#88a9b2'))
        p.append(text(x,y+45,value,35,'#d7ffec',weight='bold'))
    metric(826,128,'TOTAL CONTRIBUTIONS',f'{count:,}'.replace(',',' ') if calendar else '—')
    metric(1006,128,'ACTIVE DAYS',str(active) if calendar else '—')
    metric(826,234,'PEAK / DAY',str(maximum) if calendar else '—')
    metric(1006,234,'LAST UPDATE',date.today().strftime('%d %b %Y').upper() if calendar else '—')
    if peak:
        p.append(text(825,333,f'MOST ACTIVE DAY   {peak["date"]}',11,'#77cba8'))
    else:
        p.append(text(825,333,'SOURCE: GITHUB CONTRIBUTIONS CALENDAR',11,'#6c929a'))
    p.append('</svg>')
    return '\n'.join(p)+'\n'


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--offline',action='store_true',help='Generate a clearly labelled empty skeleton only')
    args=parser.parse_args()
    calendar=None if args.offline else fetch_calendar(os.environ.get('GH_TOKEN',''))
    svg=render(calendar)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(svg,encoding='utf-8')
    print(f'{OUT}: {len(svg):,} bytes, {"real GitHub data" if calendar else "honest skeleton"}')

if __name__=='__main__':
    try: main()
    except Exception as e:
        print(f'ERROR: {e}',file=sys.stderr)
        sys.exit(1)