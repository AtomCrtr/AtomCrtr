"""Offline tests for the contribution SVG and README assets."""

import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'build_contributions.py'
spec = importlib.util.spec_from_file_location('contributions', SCRIPT)
contributions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contributions)
SVG = {'svg': 'http://www.w3.org/2000/svg'}


class DashboardTests(unittest.TestCase):
    def test_offline_never_invents_stats(self):
        root = ET.fromstring(contributions.render(None))
        labels = [node.text for node in root.findall('svg:text', SVG)]
        self.assertEqual(labels, ['En attente de la synchronisation GitHub'])
        self.assertEqual(len(root.findall('svg:rect', SVG)), 1)

    def test_real_values_derive_from_fixture(self):
        sample = {
            'totalContributions': 7,
            'weeks': [{'contributionDays': [
                {'date': '2026-11-15', 'contributionCount': 0, 'contributionLevel': 'NONE'},
                {'date': '2026-11-16', 'contributionCount': 2, 'contributionLevel': 'SECOND_QUARTILE'},
                {'date': '2026-11-17', 'contributionCount': 5, 'contributionLevel': 'FOURTH_QUARTILE'},
            ]}],
        }
        root = ET.fromstring(contributions.render(sample))
        labels = [node.text for node in root.findall('svg:text', SVG)]
        self.assertIn('7 contributions · 2 jours actifs', labels)
        self.assertIn('nov.', labels)
        cells = root.findall('svg:rect', SVG)[1:4]
        self.assertEqual([cell.get('y') for cell in cells], ['81', '99', '117'])
        self.assertEqual(cells[-1].get('fill'), contributions.COLORS['FOURTH_QUARTILE'])

    def test_no_token_is_rejected(self):
        with self.assertRaises(RuntimeError):
            contributions.fetch_calendar('')

    def test_readme_assets_exist(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for asset in ('assets/hero.jpg', 'assets/contributions.svg'):
            self.assertIn(f']({asset})', readme)
            self.assertGreater((ROOT / asset).stat().st_size, 0)


if __name__ == '__main__':
    unittest.main()
