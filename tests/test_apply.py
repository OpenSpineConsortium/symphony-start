"""apply in both modes, on fake trees and the template's real init script.

Mode new must leave what "Use this template" would: every file filled, the
marker folder gone, a blank checkpoint and an empty checkpoint block, a
file of theirs the template also has replaced and listed. Mode existing
must change nothing of theirs but CLAUDE.md, which gains one section once
the protocol's text landed, and .claude/settings.json, which gains the
keys it lacks; a workflow and every script it runs come together or not
at all, and with the library they import, so every module of the
template that a script which lands imports landed with it, or was there
already with the template's bytes, and the metrics workflow comes only
with its switch; and a file the repository ignores is never written.
Neither copies LICENSE, follows a link out of the template, or writes
through a link out of the target or into its .git; in either, an off the
repository says already, in the switch or under its old name, keeps the
switch the adoption writes off, and an adoption that could not write the
protocol's text, by which the front door knows an adoption, is refused
before anything is written.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from trees import (CREATOR, EMPTY_LISTS, LIBRARY, METRICS, METRICS_BEFORE_BREAKDOWN, METRICS_MODULES, P,
                   PROTOCOL_ADDED, SETUP_SCRIPT_BEFORE_BOX, SPEC, THEIR_CLAUDE, THEIR_FILES, THEIR_SETTINGS,
                   THEIR_SETTINGS_TEXT, WORKFLOWS, adopt, apply, checkpoint_lists, make_checkout, make_target,
                   make_template, run_script, snapshot, track, unmet_imports, write)

PLACEHOLDERS = tuple(P.values())
BOARD = (".github/workflows/board.yml", "tools/board.py")
NO_GIT = {rel: text for rel, text in THEIR_FILES.items() if not rel.startswith(".git/")}
HELD_WITH_THE_LIBRARY = "`tools/VENDORED` is this repository's own, so the vendored library is not brought, and"


class Scratch(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.template = self.root / "template"
        self.target = self.root / "target"
        self.manifest = self.root / "manifest.json"

    def skipped(self, manifest):
        return {item["path"]: item["why"] for item in manifest["skipped"]}


class NewMode(Scratch):
    def setUp(self):
        super().setUp()
        make_template(self.template)
        make_target(self.target, {"README.md": "# widget\n", ".git/HEAD": "ref: refs/heads/main\n"})

    def test_a_readme_only_repository_gets_the_whole_template(self):
        code, manifest, err = apply(self.template, self.target, self.manifest)
        self.assertEqual(code, 0, err)
        self.assertEqual(manifest["replaced"], ["README.md"])
        self.assertEqual(manifest["kept"], [])
        self.assertIn("docs/setup/github.md", manifest["added"])
        self.assertEqual((self.target / "README.md").read_text(),
                         "# widget\n\nClone octo-org/widget; the default branch is main.\n")

    def test_the_placeholders_are_filled_outside_the_workflows(self):
        apply(self.template, self.target, self.manifest)
        for rel, data in snapshot(self.target).items():
            with self.subTest(rel=rel):
                text = data.decode("utf-8")
                self.assertFalse(any(marker in text for marker in PLACEHOLDERS))
        self.assertEqual((self.target / "docs/agents/claims/README.md").read_text(),
                         "# Claim files\n\n- Issue: https://github.com/octo-org/widget/issues/N\n")

    def test_the_marker_goes_and_the_checkpoint_is_blank(self):
        apply(self.template, self.target, self.manifest)
        self.assertFalse((self.target / ".template").exists())
        self.assertIn("Nothing has been checkpointed yet", (self.target / ".claude/session.md").read_text())

    def test_the_checkpoint_block_is_emptied_and_the_rest_kept(self):
        apply(self.template, self.target, self.manifest)
        text = (self.target / "CLAUDE.md").read_text()
        self.assertEqual(checkpoint_lists(text), EMPTY_LISTS)
        self.assertNotIn("The template's own", text)
        self.assertTrue(text.startswith("# widget\n\nThe template's instructions.\n\n<!-- cswap:checkpoint:begin -->\n"
                                        "## Session checkpoint (kept by cswap)\n\nRead `.claude/session.md`"))

    def test_the_code_owner_is_the_owner_or_in_an_organization_the_creator(self):
        apply(self.template, self.target, self.manifest, owner_type="User")
        self.assertEqual((self.target / ".github/CODEOWNERS").read_text(), "* @octo-org\n")
        apply(self.template, self.target, self.manifest, owner_type="Organization")
        self.assertEqual((self.target / ".github/CODEOWNERS").read_text(), f"* @{CREATOR}\n")

    def test_no_license_no_git_no_cache(self):
        _, manifest, _ = apply(self.template, self.target, self.manifest)
        self.assertFalse((self.target / "LICENSE").exists())
        self.assertNotIn("LICENSE", manifest["added"] + manifest["replaced"])
        self.assertFalse((self.target / ".git/config").exists())
        self.assertEqual((self.target / ".git/HEAD").read_text(), "ref: refs/heads/main\n")
        self.assertFalse((self.target / "tools/sdlc_protocol/__pycache__").exists())

    def test_a_script_stays_executable(self):
        apply(self.template, self.target, self.manifest)
        self.assertTrue(os.stat(self.target / "scripts/check.sh").st_mode & 0o111)
        self.assertFalse(os.stat(self.target / "README.md").st_mode & 0o111)

    def test_the_metrics_switch_follows_the_form(self):
        for metrics in ("on", "off"):
            with self.subTest(metrics=metrics):
                apply(self.template, self.target, self.manifest, metrics=metrics)
                self.assertEqual((self.target / ".github/symphony-metrics").read_text(), metrics + "\n")

    def test_a_template_without_metrics_brings_none(self):
        _, manifest, _ = apply(self.template, self.target, self.manifest)
        self.assertFalse(manifest["metrics_workflow"])
        self.assertFalse(manifest["metrics_breakdown"])
        self.assertFalse((self.target / ".github/workflows/metrics.yml").exists())

    def test_a_template_with_metrics_brings_them(self):
        make_template(self.template, metrics=True)
        _, manifest, _ = apply(self.template, self.target, self.manifest)
        self.assertTrue(manifest["metrics_workflow"])
        self.assertTrue(manifest["metrics_breakdown"])
        for rel in METRICS:
            self.assertIn(rel, manifest["added"])
        self.assertEqual(unmet_imports(self.target, "tools/metrics.py", manifest["added"]), [])

    def test_a_script_from_before_the_breakdown_lands_without_it(self):
        make_template(self.template, metrics=True)
        write(self.template, "tools/metrics.py", METRICS_BEFORE_BREAKDOWN)
        _, manifest, _ = apply(self.template, self.target, self.manifest)
        self.assertTrue(manifest["metrics_workflow"])
        self.assertFalse(manifest["metrics_breakdown"])

    def test_a_workflow_written_without_a_module_it_runs_is_not_at_work(self):
        """Mode new holds no unit back: where a module the metrics script
        imports cannot be written, the workflow lands without it, and the
        manifest says it will not run."""
        make_template(self.template, metrics=True)
        write(self.target, "tools/usage.py/notes.md", "their folder\n")
        code, manifest, err = apply(self.template, self.target, self.manifest)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.skipped(manifest)["tools/usage.py"], "a folder of yours stands where this file goes")
        for rel in (".github/workflows/metrics.yml", "tools/metrics.py", "tools/economics.py"):
            self.assertIn(rel, manifest["added"])
        self.assertFalse(manifest["metrics_workflow"])
        self.assertFalse(manifest["metrics_breakdown"])

    def test_a_switch_that_cannot_be_written_is_read_as_off(self):
        """Where a folder of theirs stands in the switch's place, the metrics
        workflow still lands in mode new, and the template's script reads
        what it cannot read as off, whatever the form said."""
        make_template(self.template, metrics=True)
        write(self.target, ".github/symphony-metrics/notes.md", "their notes\n")
        code, manifest, err = apply(self.template, self.target, self.manifest, metrics="on")
        self.assertEqual(code, 0, err)
        self.assertIn(".github/symphony-metrics", self.skipped(manifest))
        self.assertTrue(manifest["metrics_workflow"])
        self.assertEqual(manifest["switch_reads"], "off")

    def test_a_setup_script_that_ticks_the_box_is_recorded(self):
        _, manifest, _ = apply(self.template, self.target, self.manifest)
        self.assertIn(adopt.SETUP_SCRIPT, manifest["added"])
        self.assertTrue(manifest["setup_script_ticks_box"])

    def test_a_setup_script_from_before_the_box_lands_without_it(self):
        """The run copies the template's default branch, and the repository
        keeps the script it was adopted with; a template with no setup
        script at all records no box either."""
        write(self.template, adopt.SETUP_SCRIPT, SETUP_SCRIPT_BEFORE_BOX)
        _, manifest, _ = apply(self.template, self.target, self.manifest)
        self.assertIn(adopt.SETUP_SCRIPT, manifest["added"])
        self.assertFalse(manifest["setup_script_ticks_box"])
        (self.template / adopt.SETUP_SCRIPT).unlink()
        (self.target / adopt.SETUP_SCRIPT).unlink()
        code, manifest, err = apply(self.template, self.target, self.manifest)
        self.assertEqual(code, 0, err)
        self.assertNotIn(adopt.SETUP_SCRIPT, manifest["added"] + manifest["replaced"])
        self.assertFalse(manifest["setup_script_ticks_box"])

    def test_the_whole_template_takes_no_spec(self):
        spec = write(self.root, "spec/PROTOCOL.md", SPEC)
        _, manifest, _ = apply(self.template, self.target, self.manifest, protocol_spec=spec)
        self.assertEqual(manifest["protocol_text"], "template")
        self.assertEqual((self.target / "docs/agents/PROTOCOL.md").read_text(),
                         "# How work is claimed\n\nThe queue is on octo-org/widget; pushes to main.\n")

    def test_a_link_of_theirs_is_replaced_never_written_through(self):
        outside = write(self.root, "outside/notes.md", "their notes\n")
        (self.target / "README.md").unlink()
        (self.target / "README.md").symlink_to(outside)
        _, manifest, _ = apply(self.template, self.target, self.manifest)
        self.assertIn("README.md", manifest["replaced"])
        self.assertFalse((self.target / "README.md").is_symlink())
        self.assertEqual(outside.read_text(), "their notes\n")


class ExistingMode(Scratch):
    def setUp(self):
        super().setUp()
        make_template(self.template)
        make_target(self.target, THEIR_FILES)
        self.before = snapshot(self.target)

    def adopt_existing(self, **options):
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing", **options)
        self.assertEqual(code, 0, err)
        return manifest

    def test_nothing_of_theirs_changes_but_claude_md_and_the_settings(self):
        manifest = self.adopt_existing()
        after = snapshot(self.target)
        for rel, data in self.before.items():
            if rel not in (adopt.CLAUDE_MD, adopt.SETTINGS):
                self.assertEqual(after[rel], data, rel)
        self.assertEqual(set(after) - set(self.before), PROTOCOL_ADDED)
        self.assertEqual(set(manifest["added"]), PROTOCOL_ADDED)
        self.assertEqual(manifest["merged"], sorted([adopt.CLAUDE_MD, adopt.SETTINGS]))
        self.assertEqual((manifest["replaced"], manifest["kept"]), ([], []))

    def test_the_protocol_brings_no_setup_script_and_so_no_box(self):
        self.assertFalse(self.adopt_existing()["setup_script_ticks_box"])
        self.assertFalse((self.target / adopt.SETUP_SCRIPT).exists())

    def test_claude_md_gains_the_section(self):
        self.adopt_existing()
        self.assertEqual((self.target / "CLAUDE.md").read_text(), THEIR_CLAUDE + "\n" + adopt.CLAUDE_SECTION)

    def test_the_settings_gain_two_keys_and_keep_theirs(self):
        manifest = self.adopt_existing()
        text = (self.target / ".claude/settings.json").read_text()
        settings = json.loads(text)
        self.assertEqual(list(settings), ["permissions", "model", "extraKnownMarketplaces", "enabledPlugins"])
        self.assertEqual({k: settings[k] for k in THEIR_SETTINGS}, THEIR_SETTINGS)
        self.assertEqual(settings["extraKnownMarketplaces"], {"symphony-marketplace": adopt.MARKETPLACE})
        self.assertEqual(settings["enabledPlugins"], {"symphony@symphony-marketplace": True})
        self.assertTrue(text.startswith(THEIR_SETTINGS_TEXT.rstrip()[:-1].rstrip() + ",\n"), "their lines stay")
        self.assertIn('\n    "enabledPlugins": {\n        "symphony@symphony-marketplace": true\n    }\n}\n', text)
        self.assertEqual(manifest["settings_changed"], {"extraKnownMarketplaces": "added", "enabledPlugins": "added"})
        self.assertTrue(manifest["plugin_enabled"])

    def test_a_merge_into_keys_they_have_writes_the_file_again(self):
        write(self.target, ".claude/settings.json", '{"enabledPlugins": {"other@market": true}}\n')
        manifest = self.adopt_existing()
        settings = json.loads((self.target / ".claude/settings.json").read_text())
        self.assertEqual(settings["enabledPlugins"], {"other@market": True, "symphony@symphony-marketplace": True})
        self.assertIn("symphony-marketplace", settings["extraKnownMarketplaces"])
        self.assertEqual(manifest["settings_changed"],
                         {"extraKnownMarketplaces": "added", "enabledPlugins": "extended"})

    def test_a_plugin_they_turned_off_stays_off_when_the_marketplace_is_added(self):
        write(self.target, ".claude/settings.json", '{"enabledPlugins": {"symphony@symphony-marketplace": false}}\n')
        manifest = self.adopt_existing()
        settings = json.loads((self.target / ".claude/settings.json").read_text())
        self.assertEqual(settings["enabledPlugins"], {"symphony@symphony-marketplace": False})
        self.assertEqual(manifest["settings_changed"], {"extraKnownMarketplaces": "added"})
        self.assertFalse(manifest["plugin_enabled"])

    def test_carriage_returns_in_the_settings_are_kept_on_both_paths(self):
        write(self.target, ".claude/settings.json", '{\r\n  "model": "opus"\r\n}\r\n')
        self.adopt_existing()
        appended = (self.target / ".claude/settings.json").read_bytes()
        write(self.target, ".claude/settings.json", '{\r\n  "enabledPlugins": {"other@market": true}\r\n}\r\n')
        self.adopt_existing()
        rewritten = (self.target / ".claude/settings.json").read_bytes()
        for data in (appended, rewritten):
            self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
            self.assertIn("symphony-marketplace", json.loads(data)["extraKnownMarketplaces"])

    def test_an_empty_object_takes_the_keys(self):
        write(self.target, ".claude/settings.json", "{}\n")
        self.adopt_existing()
        self.assertEqual(json.loads((self.target / ".claude/settings.json").read_text()), {
            "extraKnownMarketplaces": {"symphony-marketplace": adopt.MARKETPLACE},
            "enabledPlugins": {"symphony@symphony-marketplace": True},
        })

    def test_none_of_the_templates_tests_checks_or_documents(self):
        self.adopt_existing()
        for rel in ("tests/test_template.py", "scripts/check.sh", "docs/setup/github.md", "LICENSE",
                    ".github/workflows/template-init.yml", ".github/CODEOWNERS", "tools/template_init.py"):
            self.assertFalse((self.target / rel).exists(), rel)
        self.assertEqual((self.target / ".github/workflows/ci.yml").read_text(), "name: CI\non:\n  push:\n")

    def test_without_a_spec_the_templates_own_page_is_filled(self):
        self.assertFalse((self.template / "tools/sdlc_protocol/spec").exists(), "the vendored copy has no spec")
        manifest = self.adopt_existing()
        self.assertEqual(manifest["protocol_text"], "template")
        self.assertEqual((self.target / "docs/agents/PROTOCOL.md").read_text(),
                         "# How work is claimed\n\nThe queue is on octo-org/widget; pushes to main.\n")

    def test_the_librarys_spec_when_the_workflow_passes_it(self):
        spec = write(self.root, "protocol/spec/PROTOCOL.md", SPEC)
        manifest = self.adopt_existing(protocol_spec=spec)
        self.assertEqual(manifest["protocol_text"], "spec")
        self.assertEqual((self.target / "docs/agents/PROTOCOL.md").read_text(), SPEC)
        self.assertIn("docs/agents/PROTOCOL.md", manifest["added"])

    def test_a_file_that_is_there_is_kept(self):
        write(self.target, "tools/board.py", "their board\n")
        write(self.target, "docs/agents/claims/README.md", "their claims\n")
        manifest = self.adopt_existing()
        self.assertEqual(manifest["kept"], ["docs/agents/claims/README.md", "tools/board.py"])
        self.assertEqual((self.target / "tools/board.py").read_text(), "their board\n")

    def test_a_workflow_and_its_script_come_together_or_not_at_all(self):
        write(self.target, "tools/board.py", "their board\n")
        manifest = self.adopt_existing()
        self.assertFalse((self.target / ".github/workflows/board.yml").exists())
        self.assertEqual(self.skipped(manifest)[".github/workflows/board.yml"],
                         "`tools/board.py` is this repository's own, and the board's workflow and its script are"
                         " brought together or not at all")
        self.assertNotIn(".github/workflows/board.yml", manifest["added"])

    def test_their_metrics_workflow_keeps_the_templates_script_out(self):
        make_template(self.template, metrics=True)
        write(self.target, ".github/workflows/metrics.yml", "name: Their metrics\n")
        manifest = self.adopt_existing()
        self.assertFalse(manifest["metrics_workflow"])
        self.assertTrue(manifest["metrics_in_template"])
        # The template's script counts by setting, but it did not land.
        self.assertFalse(manifest["metrics_breakdown"])
        for rel in ("tools/metrics.py", *METRICS_MODULES):
            self.assertFalse((self.target / rel).exists(), rel)
            self.assertIn(rel, self.skipped(manifest))
        self.assertIn(".github/workflows/metrics.yml", manifest["kept"])

    def test_their_vendored_record_keeps_the_whole_library_out(self):
        write(self.target, "tools/VENDORED", "sdlc-protocol 0.0.0 their copy\n")
        manifest = self.adopt_existing()
        self.assertEqual(manifest["kept"], ["tools/VENDORED"])
        self.assertFalse((self.target / "tools/sdlc_protocol").exists())
        for rel in LIBRARY[1:]:
            self.assertIn("`tools/VENDORED` is this repository's own", self.skipped(manifest)[rel])

    def test_the_workflows_whose_scripts_import_the_library_stay_out_with_it(self):
        make_template(self.template, metrics=True)
        write(self.target, "tools/VENDORED", "sdlc-protocol 0.0.0 their copy\n")
        manifest = self.adopt_existing()
        skipped = self.skipped(manifest)
        for rel in BOARD:
            self.assertEqual(skipped.get(rel), HELD_WITH_THE_LIBRARY + " the board's workflow and its script need it")
        # The metrics script reaches the library through two modules, the
        # last importing it inside a function.
        for rel in METRICS:
            self.assertEqual(skipped.get(rel),
                             HELD_WITH_THE_LIBRARY + " the metrics workflow and the scripts it runs need it")
        self.assertFalse(manifest["metrics_workflow"])
        for rel in (".github/workflows/tidy.yml", "docs/agents/PROTOCOL.md", "docs/agents/claims/README.md"):
            self.assertIn(rel, manifest["added"])
        self.assertIn("CLAUDE.md", manifest["merged"])

    def test_the_metrics_workflow_brings_every_module_its_script_imports(self):
        make_template(self.template, metrics=True)
        manifest = self.adopt_existing()
        self.assertTrue(manifest["metrics_workflow"])
        self.assertEqual(set(manifest["added"]) - PROTOCOL_ADDED, set(METRICS))
        self.assertFalse((self.target / adopt.INIT_SCRIPT).exists(), "a module the scripts do not import stays out")

    def test_every_script_that_lands_imports_only_what_came_with_it(self):
        """What would have shown that the metrics workflow came without the
        modules its script imports: each workflow that lands runs a script
        whose imports, and its modules' in turn, are met by the files that
        landed with it, the library among them, and Python's own modules,
        never by a file of theirs in a module of the template's place and
        never by nothing. A file of theirs named like one of Python's own
        modules is not caught, as the README says."""
        make_template(self.template, metrics=True)
        theirs = {"none": {}, "their board": {"tools/board.py": "theirs\n"},
                  "their record": {"tools/VENDORED": "theirs\n"},
                  **{f"their {rel}": {rel: "theirs\n"} for rel in METRICS_MODULES}}
        for case, files in theirs.items():
            for mode in ("existing", "new"):
                with self.subTest(case=case, mode=mode):
                    target = make_target(self.root / f"{case}-{mode}".replace(" ", "-").replace("/", "-"),
                                         dict(THEIR_FILES, **files))
                    code, manifest, err = apply(self.template, target, self.manifest, mode=mode)
                    self.assertEqual(code, 0, err)
                    landed = manifest["added"] + manifest["replaced"]
                    for workflow, script in WORKFLOWS.items():
                        if workflow in landed:
                            self.assertEqual(unmet_imports(target, script, landed), [], workflow)

    def test_the_workflows_scripts_run_where_they_landed(self):
        make_template(self.template, metrics=True)
        self.adopt_existing()
        for script in ("tools/metrics.py", "tools/board.py"):
            done = run_script(self.target, script)
            self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(run_script(self.target, "tools/metrics.py").stdout, "metrics by_setting \n")

    def test_a_module_of_theirs_keeps_the_metrics_workflow_out(self):
        make_template(self.template, metrics=True)
        for module in METRICS_MODULES:
            with self.subTest(module=module):
                target = make_target(self.root / module.replace("/", "-"), dict(THEIR_FILES, **{module: "theirs\n"}))
                code, manifest, err = apply(self.template, target, self.manifest, mode="existing")
                self.assertEqual(code, 0, err)
                self.assertIn(module, manifest["kept"])
                self.assertEqual((target / module).read_text(), "theirs\n")
                skipped = self.skipped(manifest)
                for rel in sorted(set(METRICS) - {module}):
                    self.assertEqual(skipped.get(rel), f"`{module}` is this repository's own, and the metrics workflow"
                                                       " and the scripts it runs are brought together or not at all")
                    self.assertFalse((target / rel).exists(), rel)
                self.assertFalse(manifest["metrics_workflow"])
                self.assertIn("tools/board.py", manifest["added"])

    def test_a_library_of_theirs_counts_only_when_it_is_the_templates(self):
        """A copy that holds the template's bytes, from an earlier adoption
        or copied by hand at the same release, lets the workflows come; one
        that differs keeps them out, as a missing one does."""
        make_template(self.template, metrics=True)
        library = {rel: (self.template / rel).read_text() for rel in LIBRARY}
        unlike = dict(library, **{"tools/sdlc_protocol/board.py": "def render():\n    pass\n"})
        for case, files in (("like", library), ("unlike", unlike)):
            with self.subTest(library=case):
                target = make_target(self.root / case, dict(THEIR_FILES, **files))
                code, manifest, err = apply(self.template, target, self.manifest, mode="existing")
                self.assertEqual(code, 0, err)
                self.assertTrue(set(LIBRARY) <= set(manifest["kept"]))
                skipped = self.skipped(manifest)
                if case == "like":
                    self.assertTrue(set(BOARD) | set(METRICS) <= set(manifest["added"]), skipped)
                    self.assertEqual(run_script(target, "tools/metrics.py").returncode, 0)
                else:
                    self.assertEqual(skipped.get("tools/board.py"),
                                     "`tools/sdlc_protocol/board.py` is this repository's own, so the vendored library"
                                     " is not brought, and the board's workflow and its script need it")
                    self.assertTrue(set(METRICS) <= set(skipped))

    def test_a_module_two_workflows_share_keeps_both_out_with_either(self):
        make_template(self.template, metrics=True)
        write(self.template, "tools/board.py", "import usage\n\nprint('the board', usage.counted())\n")
        for theirs, shut in (("tools/board.py", (".github/workflows/metrics.yml", "tools/metrics.py")),
                             ("tools/economics.py", (".github/workflows/board.yml",))):
            with self.subTest(theirs=theirs):
                target = make_target(self.root / theirs.replace("/", "-"), dict(THEIR_FILES, **{theirs: "theirs\n"}))
                code, manifest, err = apply(self.template, target, self.manifest, mode="existing")
                self.assertEqual(code, 0, err)
                skipped = self.skipped(manifest)
                self.assertIn(f"`{theirs}` is this repository's own", skipped.get("tools/usage.py", ""))
                for rel in shut:
                    self.assertIn("`tools/usage.py` stays out with another workflow", skipped.get(rel, ""))
                for workflow in WORKFLOWS:
                    self.assertNotIn(workflow, manifest["added"])

    def test_a_package_the_script_imports_comes_whole(self):
        make_template(self.template, metrics=True)
        write(self.template, "tools/economics.py", "import prices\n\n\ndef priced():\n    return prices.TABLE\n")
        write(self.template, "tools/prices/__init__.py", "from .table import TABLE\n")
        write(self.template, "tools/prices/table.py", "TABLE = 'priced'\n")
        manifest = self.adopt_existing()
        self.assertTrue({"tools/prices/__init__.py", "tools/prices/table.py"} <= set(manifest["added"]))
        self.assertNotIn("tools/usage.py", manifest["added"], "nothing imports it now")
        self.assertEqual(run_script(self.target, "tools/metrics.py").stdout, "metrics by_setting priced\n")

    def test_a_module_the_script_loads_by_its_path_comes_with_it(self):
        """The template's tools/usage.py loads tools/profile.py by its path,
        since the standard library has a module named profile, so no import
        statement names it; it comes with the script all the same, and
        what it imports comes with it."""
        make_template(self.template, metrics=True)
        write(self.template, "tools/economics.py",
              "import importlib.util\nfrom pathlib import Path\n\n\ndef priced():\n"
              "    spec = importlib.util.spec_from_file_location(\"symphony_profile\", Path(__file__).parent / \"profile.py\")\n"
              "    module = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(module)\n    return module.TABLE\n")
        write(self.template, "tools/profile.py", "import prices\n\nTABLE = prices.TABLE\n")
        write(self.template, "tools/prices.py", "TABLE = 'priced'\n")
        manifest = self.adopt_existing()
        self.assertTrue({"tools/profile.py", "tools/prices.py"} <= set(manifest["added"]))
        self.assertEqual(run_script(self.target, "tools/metrics.py").stdout, "metrics by_setting priced\n")

    def test_an_earlier_adoption_gains_the_modules_its_script_came_to_import(self):
        """A tree adopted while the front door brought the metrics workflow
        and its script alone holds the template's bytes of both; apply run
        on it again gains the modules the script imports, and the workflow
        runs. The run itself refuses a repository whose default branch
        still holds the protocol's text (scripts/adopted.py), so apply meets
        such a tree where that file has gone since."""
        make_template(self.template, metrics=(".github/workflows/metrics.yml", "tools/metrics.py"))
        first = self.adopt_existing()
        self.assertEqual(set(first["added"]) & set(METRICS), {".github/workflows/metrics.yml", "tools/metrics.py"})
        make_template(self.template, metrics=True)
        manifest = self.adopt_existing()
        self.assertEqual(sorted(set(manifest["added"]) & set(METRICS)), list(METRICS_MODULES))
        self.assertTrue({".github/workflows/metrics.yml", "tools/metrics.py"} <= set(manifest["kept"]))
        self.assertTrue(manifest["metrics_workflow"])
        self.assertTrue(manifest["metrics_breakdown"])
        self.assertEqual(run_script(self.target, "tools/metrics.py").returncode, 0)
        again = self.adopt_existing()
        self.assertEqual(again["added"], [])
        self.assertTrue(again["metrics_workflow"])

    def test_a_switch_that_cannot_be_written_keeps_the_metrics_workflow_out(self):
        make_template(self.template, metrics=True)
        write(self.target, ".github/symphony-metrics/notes.md", "their notes\n")
        manifest = self.adopt_existing(metrics="off")
        skipped = self.skipped(manifest)
        self.assertEqual(skipped[".github/symphony-metrics"], "a folder of yours stands where this file goes")
        for rel in METRICS:
            self.assertEqual(skipped.get(rel), "`.github/symphony-metrics` cannot be written here, and the metrics"
                                               " workflow and the scripts it runs come only with the metrics switch,"
                                               " which says whether they share")
            self.assertFalse((self.target / rel).exists(), rel)
        self.assertFalse(manifest["metrics_workflow"])
        self.assertIn(".github/workflows/board.yml", manifest["added"])

    def test_the_manifest_says_what_the_workflow_will_read_in_the_switch(self):
        """The form's word where the switch is written, and the repository's
        own where it is kept, read as the template's script reads it: on only
        when the first word is on."""
        make_template(self.template, metrics=True)
        cases = ((None, "off", "off"), (None, "on", "on"), ("on\n", "off", "on"), ("Off\n", "on", "off"),
                 ("maybe\n", "on", "off"), (b"on \xff\n", "on", "off"))
        for theirs, metrics, reads in cases:
            with self.subTest(theirs=theirs, metrics=metrics):
                (self.target / ".github/symphony-metrics").unlink(missing_ok=True)
                if theirs is not None:
                    write(self.target, ".github/symphony-metrics", theirs)
                manifest = self.adopt_existing(metrics=metrics)
                self.assertEqual(manifest["switch_reads"], reads)
                self.assertTrue(manifest["metrics_workflow"])

    def test_a_kept_protocol_leaves_claude_md_alone(self):
        write(self.target, "docs/agents/PROTOCOL.md", "Agents must ask Bob before merging.\n")
        manifest = self.adopt_existing()
        self.assertEqual((self.target / "CLAUDE.md").read_text(), THEIR_CLAUDE)
        self.assertNotIn("CLAUDE.md", manifest["merged"] + manifest["added"])
        self.assertIn("docs/agents/PROTOCOL.md", manifest["kept"])
        self.assertEqual(len(manifest["notes"]), 1)
        self.assertIn("gains no section importing it", manifest["notes"][0])
        self.assertIn(adopt.CLAUDE_SECTION, manifest["notes"][0])

    def test_metrics_on_and_off(self):
        for metrics in ("on", "off"):
            with self.subTest(metrics=metrics):
                (self.target / ".github/symphony-metrics").unlink(missing_ok=True)
                self.adopt_existing(metrics=metrics)
                self.assertEqual((self.target / ".github/symphony-metrics").read_text(), metrics + "\n")

    def test_a_switch_that_is_there_is_kept_and_the_difference_noted(self):
        write(self.target, ".github/symphony-metrics", "off\n")
        manifest = self.adopt_existing(metrics="on")
        self.assertEqual((self.target / ".github/symphony-metrics").read_text(), "off\n")
        self.assertIn(".github/symphony-metrics", manifest["kept"])
        self.assertEqual(len(manifest["notes"]), 1)

    def test_a_kept_switch_is_read_by_its_first_word_as_the_workflow_reads_it(self):
        write(self.target, ".github/symphony-metrics", "On\n\nThe first word of this file is the switch.\n")
        self.assertEqual(self.adopt_existing(metrics="on")["notes"], [])
        write(self.target, ".github/symphony-metrics", "maybe\n")
        notes = [note for note in self.adopt_existing(metrics="on")["notes"] if ".github/symphony-metrics" in note]
        self.assertEqual(len(notes), 1)
        self.assertIn("something other than on or off, which the metrics workflow reads as off", notes[0])

    def test_metrics_come_only_with_both_files(self):
        make_template(self.template, metrics=(".github/workflows/metrics.yml",))
        self.assertFalse(self.adopt_existing()["metrics_workflow"])
        self.assertFalse((self.target / ".github/workflows/metrics.yml").exists())
        make_template(self.template, metrics=True)
        manifest = self.adopt_existing()
        self.assertTrue(manifest["metrics_workflow"])
        self.assertTrue(manifest["metrics_breakdown"])
        self.assertTrue((self.target / "tools/metrics.py").exists())

    def test_a_script_from_before_the_breakdown_lands_without_it(self):
        make_template(self.template, metrics=True)
        write(self.template, "tools/metrics.py", METRICS_BEFORE_BREAKDOWN)
        manifest = self.adopt_existing()
        self.assertTrue(manifest["metrics_workflow"])
        self.assertFalse(manifest["metrics_breakdown"])


class ExistingModeEdges(Scratch):
    def setUp(self):
        super().setUp()
        make_template(self.template)

    def adopt_existing(self, files):
        make_target(self.target, files)
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing")
        self.assertEqual(code, 0, err)
        return manifest

    def test_no_claude_md_and_no_settings_are_made(self):
        manifest = self.adopt_existing({"README.md": "# widget\n"})
        self.assertEqual((self.target / "CLAUDE.md").read_text(), adopt.CLAUDE_SECTION)
        self.assertEqual(json.loads((self.target / ".claude/settings.json").read_text()), {
            "extraKnownMarketplaces": {"symphony-marketplace": adopt.MARKETPLACE},
            "enabledPlugins": {"symphony@symphony-marketplace": True},
        })
        self.assertIn("CLAUDE.md", manifest["added"])
        self.assertIn(".claude/settings.json", manifest["added"])
        self.assertTrue(manifest["plugin_enabled"])

    def test_invalid_settings_are_left_as_they_were(self):
        manifest = self.adopt_existing({".claude/settings.json": '{"permissions": [,]\n'})
        self.assertEqual((self.target / ".claude/settings.json").read_text(), '{"permissions": [,]\n')
        self.assertTrue(manifest["settings_invalid"])
        self.assertIn(".claude/settings.json", manifest["kept"])

    def test_settings_of_another_shape_are_left_too(self):
        manifest = self.adopt_existing({".claude/settings.json": '{"enabledPlugins": []}\n'})
        self.assertTrue(manifest["settings_invalid"])
        self.assertEqual((self.target / ".claude/settings.json").read_text(), '{"enabledPlugins": []}\n')

    def test_a_plugin_they_turned_off_stays_off(self):
        theirs = json.dumps({"extraKnownMarketplaces": {"symphony-marketplace": {"source": {}}},
                             "enabledPlugins": {"symphony@symphony-marketplace": False}}) + "\n"
        manifest = self.adopt_existing({".claude/settings.json": theirs})
        self.assertEqual((self.target / ".claude/settings.json").read_text(), theirs)
        self.assertIn(".claude/settings.json", manifest["kept"])

    def test_a_claude_md_that_imports_the_protocol_already_is_kept(self):
        theirs = "# Widget\n\n@docs/agents/PROTOCOL.md\n"
        manifest = self.adopt_existing({"CLAUDE.md": theirs})
        self.assertEqual((self.target / "CLAUDE.md").read_text(), theirs)
        self.assertIn("CLAUDE.md", manifest["kept"])

    def test_carriage_returns_in_claude_md_are_kept(self):
        self.adopt_existing({"CLAUDE.md": "# Widget\r\nrules\r\n"})
        data = (self.target / "CLAUDE.md").read_bytes()
        self.assertTrue(data.startswith(b"# Widget\r\nrules\r\n\r\n## How work is claimed\r\n"))
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))


class Ignored(Scratch):
    """A checkout whose ignore rules match a planned path: git would commit
    it only by force and then replace each person's own copy on pull."""

    def setUp(self):
        super().setUp()
        make_template(self.template)

    def adopt_checkout(self, ignore, files=NO_GIT):
        make_checkout(self.target, files, ignore)
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing")
        self.assertEqual(code, 0, err)
        return manifest

    def test_an_ignored_claude_md_and_settings_are_not_written(self):
        manifest = self.adopt_checkout(".claude/\nCLAUDE.md\n", {"README.md": "# widget\n"})
        self.assertFalse((self.target / "CLAUDE.md").exists())
        self.assertFalse((self.target / ".claude").exists())
        skipped = self.skipped(manifest)
        self.assertEqual(skipped["CLAUDE.md"], adopt.IGNORED_WHY)
        self.assertEqual(skipped[".claude/settings.json"], adopt.IGNORED_WHY)
        self.assertIn("docs/agents/PROTOCOL.md", manifest["added"])

    def test_an_ignored_folder_holds_its_units_back(self):
        manifest = self.adopt_checkout("tools/\n")
        skipped = self.skipped(manifest)
        for rel in LIBRARY + ("tools/board.py",):
            self.assertEqual(skipped[rel], adopt.IGNORED_WHY, rel)
        self.assertIn("`tools/board.py` is ignored by this repository", skipped[".github/workflows/board.yml"])
        self.assertFalse((self.target / "tools").exists())
        self.assertIn(".github/workflows/tidy.yml", manifest["added"])

    def test_an_ignored_protocol_page_refuses_the_whole_adoption(self):
        """The front door knows an adoption by docs/agents/PROTOCOL.md alone,
        and every session reads the protocol there, so a repository that
        ignores it is refused before anything is written, rather than
        adopted where the next request could not tell."""
        make_checkout(self.target, NO_GIT, "docs/\n")
        before = snapshot(self.target)
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing")
        self.assertEqual((code, manifest), (adopt.EXIT_REFUSED, None))
        self.assertTrue(err.startswith("adopt: refused: docs/agents/PROTOCOL.md cannot be written: the repository"
                                       " ignores it, or a file or link of its own stands where it or its folder goes"),
                        err)
        self.assertEqual(err.count("\n"), 1)
        self.assertEqual(snapshot(self.target), before)
        self.assertFalse(self.manifest.exists())

    def test_an_ignored_switch_keeps_the_metrics_workflow_out(self):
        """The template's metrics script reads a missing switch as on, and an
        ignored one is missing from every clone, so the workflow would share
        where the form said off, and share whatever the form said: it comes
        only with its switch, whichever word the form gave."""
        make_template(self.template, metrics=True)
        for metrics in ("off", "on"):
            with self.subTest(metrics=metrics):
                shutil.rmtree(self.target, ignore_errors=True)
                make_checkout(self.target, NO_GIT, "*metrics\n")
                code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing",
                                            metrics=metrics)
                self.assertEqual(code, 0, err)
                skipped = self.skipped(manifest)
                self.assertEqual(skipped[".github/symphony-metrics"], adopt.IGNORED_WHY)
                for rel in METRICS:
                    self.assertEqual(skipped.get(rel), "`.github/symphony-metrics` is ignored by this repository, and"
                                                       " the metrics workflow and the scripts it runs come only with"
                                                       " the metrics switch, which says whether they share")
                    self.assertFalse((self.target / rel).exists(), rel)
                self.assertFalse(manifest["metrics_workflow"])
                self.assertEqual(manifest["switches"], {})
                self.assertIn(".github/workflows/board.yml", manifest["added"])

    def test_a_metrics_workflow_there_already_reads_an_ignored_switch_as_on(self):
        """Where the template's metrics workflow is there already, as an
        earlier adoption left it, and the switch is ignored, nothing this
        pull request writes changes what the workflow reads: no switch, so
        on, whatever the form said; the manifest says so."""
        make_template(self.template, metrics=True)
        make_checkout(self.target, dict(NO_GIT, **METRICS), "*metrics\n")
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing", metrics="off")
        self.assertEqual(code, 0, err)
        self.assertTrue(set(METRICS) <= set(manifest["kept"]))
        self.assertTrue(manifest["metrics_workflow"])
        self.assertEqual(manifest["switch_reads"], "on")

    def test_a_tracked_file_the_rules_match_is_still_merged(self):
        make_checkout(self.target, NO_GIT, "CLAUDE.md\n")
        track(self.target, "CLAUDE.md")
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing")
        self.assertEqual(code, 0, err)
        self.assertIn("CLAUDE.md", manifest["merged"])
        self.assertTrue((self.target / "CLAUDE.md").read_text().endswith(adopt.CLAUDE_SECTION))

    def test_a_plain_folder_ignores_nothing(self):
        make_target(self.target, dict(NO_GIT, **{".gitignore": "CLAUDE.md\n.claude/\n"}))
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing")
        self.assertEqual(code, 0, err)
        self.assertEqual(manifest["merged"], sorted([adopt.CLAUDE_MD, adopt.SETTINGS]))


class Links(Scratch):
    def setUp(self):
        super().setUp()
        make_template(self.template)
        self.outside = self.root / "outside"
        write(self.outside, "secret.md", "a secret outside the template\n")

    def test_a_link_in_the_template_that_leads_out_is_not_followed(self):
        (self.template / "docs/leak.md").symlink_to(self.outside / "secret.md")
        (self.template / "linked").symlink_to(self.outside, target_is_directory=True)
        make_target(self.target)
        code, manifest, err = apply(self.template, self.target, self.manifest)
        self.assertEqual(code, 0, err)
        self.assertFalse((self.target / "docs/leak.md").exists())
        self.assertFalse((self.target / "linked").exists())
        self.assertEqual({item["path"] for item in manifest["skipped"]}, {"docs/leak.md", "linked"})
        for data in snapshot(self.target).values():
            self.assertNotIn(b"a secret outside", data)

    def test_a_link_of_theirs_that_leads_out_is_never_written_through(self):
        make_target(self.target)
        (self.target / "tools").symlink_to(self.outside, target_is_directory=True)
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing")
        self.assertEqual(code, 0, err)
        skipped = self.skipped(manifest)
        self.assertIn("tools/board.py", skipped)
        self.assertIn("leads out of the repository", skipped["tools/board.py"])
        self.assertEqual(sorted(p.name for p in self.outside.iterdir()), ["secret.md"])
        self.assertIn("docs/agents/PROTOCOL.md", manifest["added"])

    def test_a_protocol_page_that_cannot_be_written_refuses_the_adoption_in_either_mode(self):
        """A link out where its folder goes, or a file of theirs there,
        leaves no place for docs/agents/PROTOCOL.md, so nothing is written,
        through the link or beside it, in either mode."""
        cases = (("a link out", "existing"), ("a file where the folder goes", "new"),
                 ("a file where the folder's folder goes", "existing"))
        for case, mode in cases:
            with self.subTest(case=case, mode=mode):
                shutil.rmtree(self.target, ignore_errors=True)
                make_target(self.target)
                if case == "a link out":
                    (self.target / "docs").symlink_to(self.outside, target_is_directory=True)
                elif case == "a file where the folder goes":
                    write(self.target, "docs", "their docs file\n")
                else:
                    write(self.target, "docs/agents", "their agents file\n")
                before = snapshot(self.target)
                code, manifest, err = apply(self.template, self.target, self.manifest, mode=mode)
                self.assertEqual((code, manifest), (adopt.EXIT_REFUSED, None), err)
                self.assertTrue(err.startswith("adopt: refused: docs/agents/PROTOCOL.md cannot be written"), err)
                self.assertEqual(snapshot(self.target), before)
                self.assertEqual(sorted(p.name for p in self.outside.iterdir()), ["secret.md"])

    def test_a_link_of_theirs_into_git_is_never_written_through(self):
        make_target(self.target, {".git/hooks/README": "hooks\n"})
        (self.target / "tools").symlink_to(self.target / ".git/hooks", target_is_directory=True)
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing")
        self.assertEqual(code, 0, err)
        skipped = self.skipped(manifest)
        self.assertIn("tools/board.py", skipped)
        self.assertIn("`tools/board.py` cannot be written here", skipped[".github/workflows/board.yml"])
        self.assertEqual(sorted(p.name for p in (self.target / ".git/hooks").iterdir()), ["README"])

    def test_a_claude_md_link_that_leads_out_is_left_alone(self):
        make_target(self.target)
        (self.target / "CLAUDE.md").symlink_to(self.outside / "secret.md")
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing")
        self.assertEqual(code, 0, err)
        self.assertIn("CLAUDE.md", {item["path"] for item in manifest["skipped"]})
        self.assertEqual((self.outside / "secret.md").read_text(), "a secret outside the template\n")

    def test_a_file_where_a_folder_goes_is_left_alone(self):
        make_target(self.target, {"tools": "their tools file\n"})
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="new")
        self.assertEqual(code, 0, err)
        self.assertEqual((self.target / "tools").read_text(), "their tools file\n")
        self.assertIn("tools/board.py", {item["path"] for item in manifest["skipped"]})


class OptOuts(Scratch):
    """An off the repository says already, in .github/symphony-metrics or
    under the switch's name before the rename, .github/sdlc-metrics, is
    never turned on by the form's default: the switch the adoption writes
    says off too, in either mode, the pull request says why, and the
    manifest says what the switches will do once merged, off in either file
    winning."""

    def setUp(self):
        super().setUp()
        make_template(self.template)

    def adoption(self, files, mode, metrics="on"):
        """Apply to a fresh target holding files; the manifest."""
        shutil.rmtree(self.target, ignore_errors=True)
        make_target(self.target, files)
        code, manifest, err = apply(self.template, self.target, self.manifest, mode=mode, metrics=metrics)
        self.assertEqual(code, 0, err)
        return manifest

    def switch(self, rel=adopt.SWITCH):
        return (self.target / rel).read_text()

    def held_notes(self, manifest):
        return [note for note in manifest["notes"] if "never lifts an opt-out" in note]

    def test_an_old_switch_saying_off_keeps_the_new_one_off(self):
        for mode in ("existing", "new"):
            with self.subTest(mode=mode):
                manifest = self.adoption(dict(NO_GIT, **{adopt.OLD_SWITCH: "off\n"}), mode)
                self.assertEqual(self.switch(), "off\n")
                self.assertEqual(self.switch(adopt.OLD_SWITCH), "off\n")
                self.assertEqual(manifest["metrics"], "on")
                self.assertEqual(manifest["switch_reads"], "off")
                self.assertEqual(manifest["switches"], {adopt.SWITCH: "off", adopt.OLD_SWITCH: "off"})
                note, = self.held_notes(manifest)
                self.assertIn(f"`{adopt.OLD_SWITCH}`, the switch under its name before the rename", note)
                self.assertIn(f"write `on` in both files, or delete `{adopt.OLD_SWITCH}`", note)

    def test_an_old_switch_is_read_by_its_first_word_as_the_workflow_reads_it(self):
        for text, said in (("maybe\n", "off"), ("", "off"), ("OFF because we said so\n", "off"),
                           ("On\n\nprose\n", "on")):
            with self.subTest(text=text):
                manifest = self.adoption(dict(NO_GIT, **{adopt.OLD_SWITCH: text}), "existing")
                self.assertEqual(self.switch(), said + "\n")
                self.assertEqual(manifest["switch_reads"], said)
                self.assertEqual(len(self.held_notes(manifest)), 1 if said == "off" else 0)

    def test_the_whole_template_keeps_a_later_opt_out_off(self):
        """An owner who wrote off in the switch the documented way, before
        a request whose box was left empty, keeps it off."""
        manifest = self.adoption({"README.md": "# widget\n", adopt.SWITCH: "off\n\nWe share nothing.\n"}, "new")
        self.assertIn(adopt.SWITCH, manifest["replaced"])
        self.assertEqual(self.switch(), "off\n")
        self.assertEqual((manifest["switch_reads"], manifest["switches"]), ("off", {adopt.SWITCH: "off"}))
        note, = self.held_notes(manifest)
        self.assertTrue(note.startswith(f"`{adopt.SWITCH}` said `off` before this request, so it still says `off`"))

    def test_a_kept_switch_that_says_off_is_what_the_manifest_shares(self):
        manifest = self.adoption(dict(NO_GIT, **{adopt.SWITCH: "off\n"}), "existing")
        self.assertIn(adopt.SWITCH, manifest["kept"])
        self.assertEqual(manifest["switch_reads"], "off")
        self.assertEqual(self.held_notes(manifest), [], "the kept switch has its own note")

    def test_a_switch_that_says_on_or_none_at_all_follows_the_form(self):
        for files, metrics in ((NO_GIT, "on"), (NO_GIT, "off"), (dict(NO_GIT, **{adopt.OLD_SWITCH: "on\n"}), "on")):
            for mode in ("existing", "new"):
                with self.subTest(files=sorted(files), metrics=metrics, mode=mode):
                    manifest = self.adoption(files, mode, metrics)
                    self.assertEqual(self.switch(), metrics + "\n")
                    self.assertEqual(manifest["switch_reads"], metrics)
                    self.assertEqual(self.held_notes(manifest), [])

    def test_a_switch_that_cannot_be_read_here_reads_as_off(self):
        """Each doubt falls to off before anything is written: an old switch
        that is a link out of the repository, a link to nothing, a link that
        loops or bytes that are not text, each saying on or nothing, keeps
        the new switch off, in either mode; one that is a link inside the
        repository reads as the file it leads to. Once the files have
        landed, the manifest says what the metrics workflow will read: a
        link to nothing is a missing file to it, which says nothing, and the
        others read as they did."""
        outside = write(self.root, "outside/switch", "on\n")
        makers = {
            "a link out": lambda path: path.symlink_to(outside),
            "a link to nothing": lambda path: path.symlink_to(path.parent / "missing"),
            "a link that loops": lambda path: path.symlink_to(path.name),
            "bytes that are not text": lambda path: path.write_bytes(b"on \xff\n"),
            "a link inside": lambda path: path.symlink_to(self.target / "docs/switch-word"),
        }
        for case, make in makers.items():
            for mode in ("existing", "new"):
                with self.subTest(case=case, mode=mode):
                    shutil.rmtree(self.target, ignore_errors=True)
                    make_target(self.target, dict(NO_GIT, **{"docs/switch-word": "on\n"}))
                    make(self.target / adopt.OLD_SWITCH)
                    code, manifest, err = apply(self.template, self.target, self.manifest, mode=mode)
                    self.assertEqual(code, 0, err)
                    said = "on" if case == "a link inside" else "off"
                    old = None if case == "a link to nothing" else said
                    self.assertEqual(self.switch(), said + "\n")
                    self.assertEqual((manifest["switch_reads"], manifest["switches"].get(adopt.OLD_SWITCH)), (said, old))
                    self.assertEqual(outside.read_text(), "on\n")

    def test_a_link_to_nothing_says_nothing_once_the_files_have_landed(self):
        """The template's tools/metrics.py opens a switch through a link and
        meets a missing file where the link leads to nothing, which says
        nothing there: mode existing keeps such a link, so a switch of the
        repository's own saying on beside an old switch that is one shares,
        and a kept switch that is one is read as a missing switch, which
        is on; only the form asking off then needs a note."""
        for new, old, metrics, switches, reads in (("on\n", "link", "on", {adopt.SWITCH: "on"}, "on"),
                                                  ("link", None, "on", {}, "on"),
                                                  ("link", "link", "off", {}, "on"),
                                                  ("link", "off\n", "on", {adopt.OLD_SWITCH: "off"}, "off")):
            with self.subTest(new=new, old=old, metrics=metrics):
                files = dict(NO_GIT, **{rel: text for rel, text in ((adopt.SWITCH, new), (adopt.OLD_SWITCH, old))
                                        if text not in (None, "link")})
                shutil.rmtree(self.target, ignore_errors=True)
                make_target(self.target, files)
                for rel, text in ((adopt.SWITCH, new), (adopt.OLD_SWITCH, old)):
                    if text == "link":
                        (self.target / rel).symlink_to(f"gone-{Path(rel).name}")
                code, manifest, err = apply(self.template, self.target, self.manifest, mode="existing", metrics=metrics)
                self.assertEqual(code, 0, err)
                self.assertIn(adopt.SWITCH, manifest["kept"])
                self.assertEqual((manifest["switches"], manifest["switch_reads"]), (switches, reads))
                self.assertEqual(self.held_notes(manifest), [], "the kept switch is theirs, and has its own note")
                kept = [note for note in manifest["notes"] if note.startswith(f"{adopt.SWITCH} was there already")]
                if new == "link" and metrics == "off":
                    self.assertEqual(kept, [f"{adopt.SWITCH} was there already and is a link to nothing, which the"
                                            " metrics workflow reads as a missing switch, where the form asked for"
                                            " `off`; it is kept, so edit it to change the choice."])
                elif new == "link":
                    self.assertEqual(kept, [])

    def test_a_link_to_nothing_is_taken_as_off_and_the_note_says_it_was_a_link(self):
        """Before anything is written a link to nothing is a doubt, and the
        switch the adoption writes says off, in either mode; the note says
        the old switch is a link, which the workflow reads as no switch,
        so writing on in the new one is enough to share."""
        for mode in ("existing", "new"):
            with self.subTest(mode=mode):
                shutil.rmtree(self.target, ignore_errors=True)
                make_target(self.target, NO_GIT)
                (self.target / adopt.OLD_SWITCH).symlink_to("gone")
                code, manifest, err = apply(self.template, self.target, self.manifest, mode=mode)
                self.assertEqual(code, 0, err)
                self.assertEqual(self.switch(), "off\n")
                self.assertEqual((manifest["switches"], manifest["switch_reads"]), ({adopt.SWITCH: "off"}, "off"))
                note, = self.held_notes(manifest)
                self.assertTrue(note.startswith(f"`{adopt.OLD_SWITCH}`, the switch under its name before the rename to"
                                                f" Symphony, is a link to nothing, which this adoption takes as `off`, so"
                                                f" `{adopt.SWITCH}` says `off` too, though the form left sharing on"), note)
                self.assertIn("a switch this adoption cannot read counts as one", note)
                self.assertTrue(note.endswith(f"To share, write `on` in `{adopt.SWITCH}`, since the metrics workflow"
                                              " reads a link to nothing as no switch at all."), note)
        shutil.rmtree(self.target, ignore_errors=True)
        make_target(self.target, {"README.md": "# widget\n", ".github/workflows/ci.yml": "name: CI\n"})
        (self.target / adopt.SWITCH).symlink_to("gone")
        code, manifest, err = apply(self.template, self.target, self.manifest, mode="new")
        self.assertEqual(code, 0, err)
        self.assertIn(adopt.SWITCH, manifest["replaced"])
        note, = self.held_notes(manifest)
        self.assertTrue(note.startswith(f"`{adopt.SWITCH}` was a link to nothing before this request, which this"
                                        " adoption takes as `off`, so it says `off` now"), note)

    def test_the_form_asking_off_needs_no_note(self):
        manifest = self.adoption(dict(NO_GIT, **{adopt.OLD_SWITCH: "off\n"}), "existing", metrics="off")
        self.assertEqual(self.switch(), "off\n")
        self.assertEqual((manifest["metrics"], manifest["switch_reads"]), ("off", "off"))
        self.assertEqual(self.held_notes(manifest), [])


class Refusals(Scratch):
    def setUp(self):
        super().setUp()
        make_template(self.template)
        make_target(self.target)

    def test_a_bad_repository_or_creator(self):
        self.assertEqual(apply(self.template, self.target, self.manifest, repo="a/b; rm -rf /")[0], 1)
        code, _, err = apply(self.template, self.target, self.manifest, repo="OpenSpineConsortium/symphony-template")
        self.assertEqual(code, 1, err)

    def test_a_manifest_inside_the_target(self):
        code, _, err = apply(self.template, self.target, self.target / "manifest.json")
        self.assertEqual(code, 1)
        self.assertIn("outside the target", err)

    def test_nested_trees(self):
        code, _, _ = apply(self.template, self.template / "docs", self.manifest)
        self.assertEqual(code, 1)

    def test_a_template_without_its_init(self):
        (self.template / adopt.INIT_SCRIPT).unlink()
        code, _, err = apply(self.template, self.target, self.manifest)
        self.assertEqual(code, 1)
        self.assertIn("template_init.py", err)
        self.assertEqual(snapshot(self.target), {"README.md": b"# widget\n"})

    def test_an_init_that_fails(self):
        write(self.template, adopt.INIT_SCRIPT, "import sys\nsys.exit('init broke')\n")
        code, _, err = apply(self.template, self.target, self.manifest)
        self.assertEqual(code, 1)
        self.assertIn("init broke", err)
        self.assertEqual(snapshot(self.target), {"README.md": b"# widget\n"})

    def test_existing_mode_needs_the_protocol(self):
        (self.template / "tools/VENDORED").unlink()
        code, _, err = apply(self.template, self.target, self.manifest, mode="existing")
        self.assertEqual(code, 1)
        self.assertIn("tools/VENDORED", err)

    def test_a_script_that_does_not_parse_is_refused_without_a_word_of_it(self):
        """Its imports say which files come with the workflow, so a script
        that does not parse leaves nothing to go by; the line says which
        file, since the log is public, and nothing of what it holds."""
        make_template(self.template, metrics=True)
        write(self.template, "tools/usage.py", "def counted(:\n    return 'the template's own line'\n")
        for mode in ("existing", "new"):
            with self.subTest(mode=mode):
                code, _, err = apply(self.template, self.target, self.manifest, mode=mode)
                self.assertEqual(code, 1)
                self.assertEqual(err, "adopt: the template's tools/usage.py does not parse as Python\n")
                self.assertEqual(snapshot(self.target), {"README.md": b"# widget\n"})

    def test_a_warning_of_the_parser_never_reaches_the_log(self):
        """The parser warns of an escape Python does not know, naming the
        template's file and line, and with the file at hand printing the
        line itself; the public log shows none of it, and the run goes on."""
        make_template(self.template, metrics=True)
        write(self.template, "tools/usage.py", "PATTERN = '\\d+'\n\n\ndef counted():\n    return PATTERN\n")
        for mode in ("existing", "new"):
            with self.subTest(mode=mode):
                code, _, err = apply(self.template, self.target, self.manifest, mode=mode)
                self.assertEqual((code, err), (0, ""))

    def test_a_spec_that_is_not_a_file(self):
        code, _, err = apply(self.template, self.target, self.manifest, mode="existing",
                             protocol_spec=self.root / "none")
        self.assertEqual(code, 1)
        self.assertIn("--protocol-spec", err)
        self.assertEqual(snapshot(self.target), {"README.md": b"# widget\n"})


if __name__ == "__main__":
    unittest.main()
