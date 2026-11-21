"""Observable syntax cases, including markup that must stay literal in code."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/nexus-description/skills/nexus-description/scripts/check_bbcode.py"
)
SPEC = importlib.util.spec_from_file_location("check_bbcode", SCRIPT)
BBCODE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BBCODE)


class BBCodeTests(unittest.TestCase):
    def test_nested_notice_and_link(self):
        report = BBCODE.check(
            '[quote][center][size=5][color=#E7BD75][b]维护招募[/b]'
            '[/color][/size][/center][url=https://example.com/issues]'
            'Apply[/url][/quote][line]'
        )
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["links"], 1)

    def test_both_list_item_closing_styles(self):
        for source in (
            '[list][*]One[*]Two[/list]',
            '[list=1][*][b]One[/b][/*][*]Two[/*][/list]',
        ):
            with self.subTest(source=source):
                self.assertEqual(BBCODE.check(source)["errors"], [])

    def test_literal_markup_inside_code(self):
        source = '[code][b]unclosed example\n[*]literal[/code][b]Real[/b]'
        self.assertEqual(BBCODE.check(source)["errors"], [])

    def test_crossed_tags_are_rejected(self):
        errors = BBCODE.check('[quote]\n[b]Text[/quote][/b]')["errors"]
        self.assertTrue(any(e["line"] == 2 and "crosses" in e["message"] for e in errors))

    def test_unclosed_and_unexpected_tags(self):
        for source in ('[spoiler]Hidden', '[/b]', '[*]No list', '[/line]', '[url=]X[/url]'):
            with self.subTest(source=source):
                self.assertTrue(BBCODE.check(source)["errors"])

    def test_utf8_and_unrecognized_brackets(self):
        self.assertEqual(BBCODE.check('[Experimental] 中文 [b]安装[/b]')["errors"], [])

    def test_cli_exit_status_and_bom_input(self):
        with tempfile.TemporaryDirectory(prefix="nexus-bbcode-") as directory:
            source = Path(directory) / "description.bbcode"
            for text, expected_status in (("[b]中文[/b]", 0), ("[b]Missing close", 1)):
                with self.subTest(text=text):
                    source.write_text(text, encoding="utf-8-sig")
                    result = subprocess.run(
                        [sys.executable, str(SCRIPT), str(source), "--json"],
                        capture_output=True, text=True, encoding="utf-8",
                    )
                    self.assertEqual(result.returncode, expected_status, result.stderr)
                    self.assertEqual(bool(json.loads(result.stdout)["errors"]), bool(expected_status))


if __name__ == "__main__":
    unittest.main()
