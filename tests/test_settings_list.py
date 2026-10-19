"""settings.json is the one list of every setting an adoption applies, and
scripts/setup.py applies them: the two must agree, so a setting is added in
both places or in neither.

Each entry with a report key is one of setup.py's SETTINGS, and the
entries name them in SETTINGS' order, once each, though two entries may
report under one key, as the organization's box reports under the
repository's; each entry says its scope, its App, its permission, its API
call, its value and the modes that apply it; and the README points to the
list as the record of what a new repository gets.
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import setup  # noqa: E402

LIST = ROOT / "settings.json"
FIELDS = ("key", "report", "scope", "app", "permission", "api", "value", "modes", "when")
SCOPES = ("repository", "organization")
APPS = ("SymphonyBoard", "Symphony Setup")
MODES = ("new", "existing")
CALL = re.compile(r"(GET|POST|PATCH|PUT|DELETE) /(repos|orgs)/\S+")


def entries():
    data = json.loads(LIST.read_text(encoding="utf-8"))
    return data["settings"]


def in_order_once(keys):
    seen = []
    for key in keys:
        if key is not None and key not in seen:
            seen.append(key)
    return seen


class SettingsList(unittest.TestCase):
    def test_the_list_and_setup_py_name_the_same_settings_in_the_same_order(self):
        reported = [entry["report"] for entry in entries()]
        self.assertEqual(in_order_once(reported), list(setup.SETTINGS))

    def test_a_key_reported_twice_is_reported_by_neighbours(self):
        """Two entries under one report key, the repository's box and the
        organization's, sit side by side, so the order above means one
        thing."""
        reported = [entry["report"] for entry in entries() if entry["report"] is not None]
        runs = [key for index, key in enumerate(reported) if index == 0 or reported[index - 1] != key]
        self.assertEqual(len(runs), len(set(runs)))

    def test_every_entry_says_what_it_is(self):
        keys = []
        for entry in entries():
            with self.subTest(setting=entry.get("key")):
                self.assertEqual(tuple(entry), FIELDS)
                self.assertIn(entry["scope"], SCOPES)
                self.assertIn(entry["app"], APPS)
                self.assertTrue(entry["permission"])
                self.assertRegex(entry["api"], CALL)
                self.assertTrue(entry["modes"])
                self.assertLessEqual(set(entry["modes"]), set(MODES))
                keys.append(entry["key"])
        self.assertEqual(len(keys), len(set(keys)))

    def test_the_scope_agrees_with_the_call(self):
        for entry in entries():
            with self.subTest(setting=entry["key"]):
                organization = entry["api"].split()[1].startswith("/orgs/")
                self.assertEqual(entry["scope"], "organization" if organization else "repository")
                self.assertIn(f"({entry['scope']})", entry["permission"])

    def test_the_organizations_settings_are_on_the_list(self):
        scoped = {entry["key"]: entry["scope"] for entry in entries()}
        self.assertEqual(scoped["actions_pull_requests_organization"], "organization")
        self.assertEqual(scoped["token_lending"], "organization")

    def test_every_setting_has_its_log_lines(self):
        # The token lending has one line of two of its own, the same for
        # every state, so the log tells nothing of why.
        self.assertEqual(set(setup.LOG_LINES) | {setup.TOKEN_LENDING}, set(setup.SETTINGS))
        self.assertEqual(setup.lending_line({"lending": {"lent": []}}), "token lending: no tokens lent")

    def test_the_readme_points_to_the_list(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("`settings.json`", readme)


if __name__ == "__main__":
    unittest.main()
