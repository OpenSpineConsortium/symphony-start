"""apply against a real checkout of the template, when one is named.

The other tests run on a fake template, since this repository is public and
the template is not, and CI here cannot read it. Whoever can, runs these
too: SDLC_TEMPLATE=/path/to/symphony-template bash scripts/check.sh. Mode new
must leave no placeholder outside the workflows, no marker folder and,
once the template's init empties it, an empty checkpoint block, and read a
setup script that ticks the box for GitHub Actions' pull requests as one;
mode existing must leave a vendored copy that the library's own check
accepts, and workflows whose scripts import only what landed with them and
run there: the template's scripts come to import modules of their own,
which no fake template here can foresee. In both, what the pull request
says is shared must be what the adopted tools/metrics.py reads in the
switches it leaves, and writing on where the pull request says must turn
sharing on: the front door reads the switches by its own code, which the
template's may outgrow.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from trees import (EMPTY_LISTS, P, REPO, THEIR_FILES, WORKFLOWS, adopt, apply, checkpoint_lists, make_target,
                   run_script, snapshot, unmet_imports)

# A command of a workflow that runs a Python script, and the script.
RUNS_A_SCRIPT = re.compile(r"\bpython3?\s+(?:-\S+\s+)*(\S+\.py)\b")
# What the adopted scripts see when they run here: no switch in the
# environment, so the file the adoption wrote decides, and a proxy that
# answers nothing, so a call to GitHub would fail at once and the test with it.
OFFLINE = {"SDLC_METRICS": "", "HTTPS_PROXY": "http://127.0.0.1:9", "https_proxy": "http://127.0.0.1:9"}

TEMPLATE = os.environ.get("SDLC_TEMPLATE", "")
# What the adopted copy's own tools/metrics.py says of the switches, run as
# the metrics workflow runs it, from the top of the checkout.
READ_SHARING = "import sys; sys.path.insert(0, 'tools'); import metrics; print(metrics.sharing('.', {}))"


def put_switch(target, rel, state):
    """A switch file of the repository's own in one of the states a person
    can leave it in, or none."""
    path = Path(target) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if state in ("on", "off"):
        path.write_text(f"{state}\n", encoding="utf-8")
    elif state == "a folder":
        path.mkdir()
        (path / "notes.md").write_text("their notes\n", encoding="utf-8")
    elif state == "a link to nothing":
        path.symlink_to(f"gone-{path.name}")


def pull_request_text(manifest_path):
    """The pull request's text for the manifest apply wrote."""
    return adopt.render_body(json.loads(Path(manifest_path).read_text(encoding="utf-8")))


def what_is_shared(body):
    """What the pull request's section What is shared says, on, off or None
    where nothing is computed, and its sentence."""
    sentence = body.split("## What is shared\n\n", 1)[1].split("\n", 1)[0]
    if sentence.startswith("Sharing of anonymous aggregates is on"):
        return "on", sentence
    if sentence.startswith("Nothing is shared:"):
        return "off", sentence
    return None, sentence


def write_on_where_it_says(target, said):
    """Write on in each switch file the off sentence names, in place of
    whatever stands there."""
    where = re.search(r"Write `on` (there|in both) to share", said).group(1)
    named = re.findall(r"`(\.github/[a-z-]+)`", said.split(", so the metrics workflow")[0])
    for rel in named[:1] if where == "there" else named:
        path = Path(target) / rel
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        elif path.is_symlink() or path.exists():
            path.unlink()
        path.write_text("on\n", encoding="utf-8")


@unittest.skipUnless(TEMPLATE, "SDLC_TEMPLATE names no checkout of the template")
class RealTemplate(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.manifest = self.root / "manifest.json"

    def test_new_mode_fills_everything(self):
        target = make_target(self.root / "target")
        code, manifest, err = apply(TEMPLATE, target, self.manifest)
        self.assertEqual(code, 0, err)
        self.assertEqual(manifest["replaced"], ["README.md"])
        self.assertFalse((target / ".template").exists())
        self.assertFalse((target / "LICENSE").exists())
        for rel, data in snapshot(target).items():
            if not rel.startswith(".github/workflows/"):
                with self.subTest(rel=rel):
                    self.assertFalse(any(marker.encode() in data for marker in P.values()))

    def test_new_mode_empties_the_checkpoint_block(self):
        init = (Path(TEMPLATE) / adopt.INIT_SCRIPT).read_text(encoding="utf-8")
        if "reset_checkpoint_block" not in init:
            self.skipTest("the template's tools/template_init.py has no reset_checkpoint_block yet")
        target = make_target(self.root / "target")
        code, _, err = apply(TEMPLATE, target, self.manifest)
        self.assertEqual(code, 0, err)
        self.assertEqual(checkpoint_lists((target / "CLAUDE.md").read_text(encoding="utf-8")), EMPTY_LISTS)

    def test_a_setup_script_that_ticks_the_box_is_read_as_one(self):
        """The pull request names the box among the setup script's steps by
        the API path the script calls, so the real script that ticks it
        must be read as one."""
        script = (Path(TEMPLATE) / adopt.SETUP_SCRIPT).read_text(encoding="utf-8")
        if "can_approve_pull_request_reviews" not in script:
            self.skipTest("the template's scripts/setup-repo.sh does not tick the box yet")
        target = make_target(self.root / "target")
        code, manifest, err = apply(TEMPLATE, target, self.manifest)
        self.assertEqual(code, 0, err)
        self.assertTrue(manifest["setup_script_ticks_box"])

    def test_what_the_pull_request_says_is_shared_is_what_the_workflow_reads(self):
        """Over the switch states a repository may hold, under the switch's
        name and its old one: where the metrics workflow lands, the section
        What is shared says what the adopted tools/metrics.py reads, and
        where it says nothing is shared, writing on where it says makes the
        workflow share. A link to nothing is a missing file to that script,
        and something standing in the switch's place reads off."""
        # (mode, the switch, the switch under its old name)
        states = (
            ("existing", "missing", "missing"), ("existing", "on", "off"), ("existing", "off", "on"),
            ("existing", "on", "a link to nothing"), ("existing", "missing", "a link to nothing"),
            ("existing", "a link to nothing", "missing"), ("existing", "a link to nothing", "off"),
            ("new", "missing", "off"), ("new", "a folder", "missing"), ("new", "a folder", "off"),
            ("new", "a link to nothing", "missing"), ("new", "off", "a link to nothing"),
        )
        for mode, new, old in states:
            with self.subTest(mode=mode, new=new, old=old):
                target = self.root / "target"
                shutil.rmtree(target, ignore_errors=True)
                make_target(target, THEIR_FILES if mode == "existing" else None)
                put_switch(target, adopt.SWITCH, new)
                put_switch(target, adopt.OLD_SWITCH, old)
                code, manifest, err = apply(TEMPLATE, target, self.manifest, mode=mode)
                self.assertEqual(code, 0, err)
                self.assertTrue(manifest["metrics_workflow"])
                done = run_script(target, "-c", READ_SHARING, environ=OFFLINE)
                self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                said, sentence = what_is_shared(pull_request_text(self.manifest))
                self.assertEqual(said, done.stdout.strip(), sentence)
                if said == "off":
                    write_on_where_it_says(target, sentence)
                    done = run_script(target, "-c", READ_SHARING, environ=OFFLINE)
                    self.assertEqual(done.stdout.strip(), "on", sentence)

    def test_existing_mode_leaves_a_copy_the_library_accepts(self):
        target = make_target(self.root / "target", THEIR_FILES)
        code, _, err = apply(TEMPLATE, target, self.manifest, mode="existing")
        self.assertEqual(code, 0, err)
        verified = subprocess.run([sys.executable, "tools/sdlc_protocol/vendoring.py", "verify", "tools"],
                                  cwd=target, capture_output=True, text=True)
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)

    def test_existing_mode_brings_everything_its_workflows_scripts_import(self):
        """What the metrics workflow lacked in a repository with files of its
        own: every script a workflow of mode existing runs, and every module
        of the template it reaches, imports only what landed with it, the
        library among them, and Python's own modules."""
        target = make_target(self.root / "target", THEIR_FILES)
        code, manifest, err = apply(TEMPLATE, target, self.manifest, mode="existing")
        self.assertEqual(code, 0, err)
        self.assertTrue(manifest["metrics_workflow"])
        for workflow, script in WORKFLOWS.items():
            with self.subTest(workflow=workflow):
                self.assertIn(workflow, manifest["added"])
                self.assertEqual(unmet_imports(target, script, manifest["added"]), [])

    def test_a_module_of_theirs_python_finds_first_holds_the_token_unit_back(self):
        """tools/token_run.py finds its modules in tools/ before scripts/, so
        a tools/tokens.py of theirs would be imported in place of the
        template's scripts/tokens.py: the unit stays out whole."""
        for shadow in ("tools/tokens.py", "tools/tokens/__init__.py"):
            with self.subTest(shadow=shadow):
                target = make_target(self.root / shadow.replace("/", "_"), {**THEIR_FILES, shadow: "x = 1\n"})
                code, manifest, err = apply(TEMPLATE, target, self.root / (shadow.replace("/", "_") + ".json"),
                                            mode="existing")
                self.assertEqual(code, 0, err)
                self.assertNotIn(".github/workflows/token.yml", manifest["added"])
                self.assertFalse((target / "scripts" / "tokens.py").exists())

    def test_each_workflow_runs_only_the_script_it_comes_with(self):
        """A workflow comes with the one script adopt.py names for it and that
        script's imports, so another script it came to run would be left
        behind; this says so before an adoption does, for every workflow mode
        existing brings, and of one that comes with no script, that it runs
        none."""
        target = make_target(self.root / "target", THEIR_FILES)
        code, manifest, err = apply(TEMPLATE, target, self.manifest, mode="existing")
        self.assertEqual(code, 0, err)
        workflows = sorted(rel for rel in manifest["added"] if rel.startswith(".github/workflows/"))
        self.assertLessEqual(set(WORKFLOWS), set(workflows))
        for workflow in workflows:
            lines = (target / workflow).read_text(encoding="utf-8").splitlines()
            commands = [line for line in lines if not line.lstrip().startswith("#")]
            run = {found for line in commands for found in RUNS_A_SCRIPT.findall(line)}
            self.assertEqual(run, {WORKFLOWS[workflow]} if workflow in WORKFLOWS else set(), workflow)

    def test_existing_mode_runs_the_metrics_workflows_commands(self):
        """The metrics workflow's two commands, as it runs them, where the
        switch the adoption wrote says off, which calls no API: the record is
        written and the comparison answers. The board's script answers too."""
        target = make_target(self.root / "target", THEIR_FILES)
        code, _, err = apply(TEMPLATE, target, self.manifest, mode="existing", metrics="off")
        self.assertEqual(code, 0, err)
        record = self.root / "METRICS.json"
        done = run_script(target, "tools/metrics.py", "collect", "--repo", REPO, "--out", str(record),
                          "--usage-cache", str(self.root / "usage-records.json"), environ=OFFLINE)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("off", json.loads(record.read_text(encoding="utf-8")).values())
        done = run_script(target, "tools/metrics.py", "unchanged", str(record), str(record), environ=OFFLINE)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        done = run_script(target, "tools/board.py", "--help", environ=OFFLINE)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
