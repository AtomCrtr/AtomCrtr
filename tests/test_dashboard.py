"""Fast offline tests for deterministic SVG generation and data provenance."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'build_contributions.py'
spec = importlib.util.spec_from_file_location('contributions', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DashboardTests(unittest.TestCase):
    def test_offline_never_invents_stats(self):
        svg = module.render(None)
        ET.fromstring(svg)
        self.assertIn('AWAITING INITIAL SYNC',svg)
        self.assertIn('—',svg)
        self.assertNotIn('149',svg)

    def test_real_values_derive_from_fixture(self):
        sample={'totalContributions':7, 'weeks': [
            {'firstDay':'2026-11-15','contributionDays':[
                {'date':'2026-11-15','contributionCount':0,'contributionLevel':'NONE'},
                {'date':'2026-11-16','contributionCount':2,'contributionLevel':'SECOND_QUARTILE'},
                {'date':'2026-11-17','contributionCount':5,'contributionLevel':'FOURTH_QUARTILE'},
            ]}
        ]}
        svg=module.render(sample)
        ET.fromstring(svg)
        self.assertIn('>7</text>',svg)
        self.assertIn('>2</text>',svg)
        self.assertIn('>5</text>',svg)
        self.assertIn('2026-11-17',svg)
        self.assertNotIn('AWAITING INITIAL SYNC',svg)

    def test_no_token_does_not_fetch_fabricate(self):
        with self.assertRaises(RuntimeError):
            module.fetch_calendar('')

    def test_svg_hero_is_valid(self):
        hero=Path(__file__).resolve().parents[1] / 'assets' / 'hero.svg'
        ET.parse(hero)


if __name__=='__main__':
    unittest.main()