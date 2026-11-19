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
    'NONE': '#233746',
    'FIRST_QUARTILE': '#285963',
    'SECOND_QUARTILE': '#388581',
    'THIRD_QUARTILE': '#51b5a5',
    'FOURTH_QUARTILE': '#9de2cf',
}
MONTHS = ('janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin',
          'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.')


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


def label(x, y, value, size=17, color='#aac0c8', weight=400, anchor='start'):
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'
    )


def render(calendar: dict | None) -> str:
    width = 1120
    height = 251 if calendar else 91
    title = 'Contributions GitHub sur douze mois'
    description = ('Calendrier des contributions d’AtomCrtr fourni par GitHub.'
                   if calendar else 'En attente de la première synchronisation GitHub.')
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        'role="img" aria-labelledby="title description" font-family="system-ui, sans-serif">',
        f'<title id="title">{title}</title>',
        f'<desc id="description">{description}</desc>',
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" '
        'fill="#101e2c" stroke="#2b4453" stroke-width="2"/>',
    ]
    if not calendar:
        parts.extend((
            '<circle cx="35" cy="46" r="6" fill="#89d6c7"/>',
            label(58, 56, 'En attente de la synchronisation GitHub', 29),
            '</svg>',
        ))
        return '\n'.join(parts) + '\n'

    weeks = calendar['weeks']
    total = f"{calendar['totalContributions']:,}".replace(',', '\N{NARROW NO-BREAK SPACE}')
    active_days = sum(day['contributionCount'] > 0
                      for week in weeks for day in week['contributionDays'])
    parts.extend((
        label(31, 43, '12 derniers mois', 22, '#e3f1ef', 600),
        label(1089, 43, f'{total} contributions · {active_days} jours actifs', 20,
              '#a2dbd2', anchor='end'),
    ))

    columns = max(53, len(weeks))
    step = min(19, 1006 / (columns - 1))
    cell = 14
    left = 74
    top = 81
    months = {}
    for column, week in enumerate(weeks, start=columns - len(weeks)):
        x = left + column * step
        for day in week['contributionDays']:
            value = date.fromisoformat(day['date'])
            y = top + (value.weekday() + 1) % 7 * 18
            color = COLORS.get(day['contributionLevel'], COLORS['NONE'])
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{cell}" height="{cell}" '
                         f'rx="3" fill="{color}"/>')
            months.setdefault((value.year, value.month), x)

    month_starts = list(months.items())
    for index, ((_, month), x) in enumerate(month_starts):
        if index + 1 < len(month_starts) and month_starts[index + 1][1] - x < 57:
            continue
        parts.append(label(f'{x:.1f}', 72, MONTHS[month - 1], 15))

    for row, name in ((1, 'lun.'), (3, 'mer.'), (5, 'ven.')):
        parts.append(label(30, top + row * 18 + 12, name, 15))

    parts.append(label(925, 228, 'Moins', 15, anchor='end'))
    for index, color in enumerate(COLORS.values()):
        parts.append(f'<rect x="{935 + index * 21}" y="215" width="{cell}" '
                     f'height="{cell}" rx="3" fill="{color}"/>')
    parts.extend((label(1043, 228, 'Plus', 15), '</svg>'))
    return '\n'.join(parts) + '\n'


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--offline',action='store_true',help='Generate a placeholder before the first GitHub sync')
    args=parser.parse_args()
    calendar=None if args.offline else fetch_calendar(os.environ.get('GH_TOKEN',''))
    svg=render(calendar)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(svg,encoding='utf-8')
    print(f'{OUT}: {len(svg):,} bytes, {"real GitHub data" if calendar else "offline placeholder"}')

if __name__=='__main__':
    try: main()
    except Exception as e:
        print(f'ERROR: {e}',file=sys.stderr)
        sys.exit(1)
