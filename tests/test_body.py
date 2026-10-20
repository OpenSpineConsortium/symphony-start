"""The pull request's text and the labels.

The body is what a person reads before they merge, so it must say what was
added, kept, replaced, merged or not written and why, that LICENSE was not
touched, what is shared and how to turn it off, and what is left to do in
each mode, all of it for the files that landed; it must never link the
template's private repository. The labels come from the template's own
list, all of them for mode new and all but team mode's for mode existing.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from trees import (METRICS, METRICS_BEFORE_BREAKDOWN, SETUP_SCRIPT_BEFORE_BOX, SPEC, THEIR_FILES, adopt, apply,
                   make_checkout, make_target, make_template, run, write)

PRIVATE_LINK = "github.com/OpenSpineConsortium/symphony-template"
NO_GIT = {rel: text for rel, text in THEIR_FILES.items() if not rel.startswith(".git/")}
RULES = "https://github.com/octo-org/widget/settings/rules"
ALL_DONE = {"ruleset": "done", "toggles": "done", "topic": "done", "secret_scanning": "done",
            "push_protection": "done", "actions_pull_requests": "done"}
TOPIC_WHY = ("so the repository page says it is adopted and the Symphony browser extension's button reads Ready for"
             " Symphony")
# The box that lets the whole template's two workflows open their pull
# requests with GitHub's own token, what it is for, and what they answer
# with while it is off.
ACTIONS = "- Allow GitHub Actions to create and approve pull requests"
ACTIONS_WHY = ("so `.github/workflows/protocol.yml` opens a pull request for each new release of the protocol, and"
               " `.github/workflows/add-worker.yml` one for each \"Add a worker\" issue")
ACTIONS_PAGE = "https://github.com/octo-org/widget/settings/actions"
MEANWHILE = ("Until it is on, `protocol.yml` brings each new release as an issue whose link opens the pull request in"
             " one press, and `add-worker.yml` answers each \"Add a worker\" issue with the link that opens its pull"
             " request.")
# The pull request's sentence on the counts of parallel work, which is true
# only of a landed script that counts by setting.
PARALLEL = "Some of those counts say how the work ran in parallel"
# The Setup App stays installed after the run (the owner, 2026-10-19).
STAYS = ("The Symphony Setup App stays installed, acting only during an adoption run. It holds"
         " Administration on this repository; you can uninstall it at any time, from the repository's Settings,"
         " GitHub Apps, at https://github.com/octo-org/widget/settings/installations, or from your account's at"
         " https://github.com/settings/installations. The Symphony App, which opened this pull request, stays too;"
         " uninstalling it undoes nothing here and only stops what is shared, above, from being read.")
# The check pinned to GitHub Actions in mode new's ruleset, and the two ways
# to pin it where the run could not.
PIN_DONE = ("- The check \"check\" in that ruleset: taken from GitHub Actions alone, so only a workflow run"
            " satisfies it, and a commit status named \"check\", which anyone with write access can post, does"
            " not.")
PIN_FIX = ("Until it is, a commit status named \"check\", which anyone with write access can post, satisfies the"
           " ruleset as well as GitHub Actions' run does. In the repository's Settings, Rules, open the ruleset"
           f" \"Protect the default branch\" at {RULES} and, beside \"check\", pick GitHub Actions as the source;"
           " or, once this pull request's check has run on the default branch after the merge, run"
           " `bash scripts/setup-repo.sh` from a clone, which pins it too.")

# The requester's own Claude tokens lent to an organization's repository.
LENDING = "- Your Claude tokens in the organization's pool:"
LEND_MORE = (" To lend more, an owner of the organization opens the secret at"
             " https://github.com/organizations/octo-org/settings/secrets/actions, and each of"
             " `SYMPHONY_CLAUDE_ACCOUNTS` and `SYMPHONY_CLAUDE_SETTINGS` at"
             " https://github.com/organizations/octo-org/settings/variables/actions, and adds this repository under"
             " Repository access; a token is lent only by its owner's word.")


def report(outcome="applied", states=ALL_DONE, details=None, mode="new", private=False, required_check=True):
    """A report as scripts/setup.py writes it."""
    details = details or {}
    return {
        "schema": adopt.SETUP_SCHEMA, "outcome": outcome, "mode": mode, "private": private,
        "ruleset_name": "Protect the default branch" if outcome == "applied" else None,
        "required_check": required_check if outcome == "applied" else False,
        "settings": {key: {"state": state, "detail": details.get(key, "")} for key, state in states.items()}
        if outcome == "applied" else {},
    }


class Body(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.template = make_template(self.root / "template")
        self.manifest = self.root / "manifest.json"

    def body(self, files=None, ignore=None, settings=None, links=None, **options):
        """The pull request's text for a target holding files, and links
        (path -> what it leads to) beside them."""
        if ignore is None:
            target = make_target(self.root / "target", files)
        else:
            target = make_checkout(self.root / "target", files, ignore)
        for rel, leads_to in (links or {}).items():
            (target / rel).symlink_to(leads_to)
        code, manifest, err = apply(self.template, target, self.manifest, **options)
        self.assertEqual(code, 0, err)
        argv = ["body", "--manifest", str(self.manifest)]
        if settings is not None:
            argv += ["--settings", str(write(self.root, "settings.json", json.dumps(settings) + "\n"))]
        code, out, err = run(argv)
        self.assertEqual(code, 0, err)
        out.encode("ascii")
        self.assertNotIn(PRIVATE_LINK, out)
        return out

    def test_new_mode(self):
        body = self.body()
        self.assertIn("the whole Symphony template into octo-org/widget", body)
        self.assertIn("Replaced", body)
        self.assertIn("- `README.md`", body)
        self.assertIn("LICENSE is not touched", body)
        self.assertIn("bash scripts/setup-repo.sh", body)
        self.assertIn("python3 scripts/crowd.py setup octo-org/widget --area AREA", body)
        self.assertIn("docs/setup/crowdsourcing.md", body)
        self.assertNotIn("CODEOWNERS` names", body)

    def test_new_mode_in_an_organization_names_the_code_owner(self):
        self.assertIn("`.github/CODEOWNERS` names `mona`", self.body(owner_type="Organization"))

    def test_existing_mode(self):
        body = self.body(THEIR_FILES, mode="existing")
        self.assertIn("No file of yours is overwritten", body)
        self.assertIn("gains the section \"How work is claimed\"", body)
        self.assertIn("gains `extraKnownMarketplaces`, which names the marketplace"
                      " OpenSpineConsortium/symphony-marketplace, and `enabledPlugins`, which enables its plugin"
                      " `symphony@symphony-marketplace`; every key it had stays.", body)
        self.assertIn("claude plugin install symphony@symphony-marketplace --scope project", body)
        self.assertIn("https://github.com/octo-org/widget/settings/rules", body)
        self.assertIn("Never target `board`, which the workflows force-push", body)
        self.assertIn("renders the board at https://github.com/octo-org/widget/blob/board/STATE.md", body)
        self.assertIn("as docs/agents/PROTOCOL.md says", body)
        self.assertIn("is the template's own text", body)
        self.assertIn("LICENSE is not touched", body)
        self.assertNotIn("setup-repo.sh", body)

    def test_existing_mode_lists_what_it_kept(self):
        files = dict(THEIR_FILES, **{"docs/agents/claims/README.md": "theirs\n"})
        self.assertIn("Kept as they are", self.body(files, mode="existing"))

    def test_the_settings_line_names_only_what_the_file_gained(self):
        files = dict(THEIR_FILES, **{".claude/settings.json": '{"enabledPlugins": {"symphony@symphony-marketplace": false}}\n'})
        body = self.body(files, mode="existing")
        self.assertIn("gains `extraKnownMarketplaces`, which names the marketplace"
                      " OpenSpineConsortium/symphony-marketplace; its plugin `symphony@symphony-marketplace` stays off in"
                      " `enabledPlugins`, as you set it; every key it had stays.", body)
        self.assertNotIn("which enables its plugin", body)
        files = dict(THEIR_FILES, **{".claude/settings.json": '{"enabledPlugins": {"other@market": true}}\n'})
        self.assertIn("and an entry in `enabledPlugins`, which enables its plugin", self.body(files, mode="existing"))

    def test_a_kept_protocol_is_said_so_and_imports_nothing(self):
        files = dict(THEIR_FILES, **{"docs/agents/PROTOCOL.md": "Agents must ask Bob before merging.\n"})
        body = self.body(files, mode="existing")
        self.assertNotIn("gains the section", body)
        self.assertNotIn("is the template's own text", body)
        self.assertIn("is this repository's own and is kept, so the claim protocol's text did not land and `CLAUDE.md`"
                      " gains no section importing it", body)
        self.assertIn("as the symphony plugin's claim protocol says", body)
        self.assertIn("```markdown\n## How work is claimed\n", body)

    def test_the_librarys_spec_gets_no_note_about_the_templates_text(self):
        spec = write(self.root, "spec/PROTOCOL.md", SPEC)
        body = self.body(THEIR_FILES, mode="existing", protocol_spec=spec)
        self.assertNotIn("is the template's own text", body)
        self.assertIn("gains the section \"How work is claimed\"", body)

    def test_a_held_back_workflow_changes_the_steps(self):
        files = dict(THEIR_FILES, **{"tools/board.py": "theirs\n"})
        body = self.body(files, mode="existing")
        self.assertIn("- `.github/workflows/board.yml`: `tools/board.py` is this repository's own, and the board's"
                      " workflow and its script are brought together or not at all", body)
        self.assertIn("was not written (above), so nothing renders the board", body)
        self.assertNotIn("Never target", body)
        self.assertNotIn("gh workflow run board.yml", body)

    def test_a_kept_board_workflow_goes_on_rendering_the_board(self):
        files = dict(THEIR_FILES, **{".github/workflows/board.yml": "theirs\n", "tools/board.py": "theirs\n"})
        body = self.body(files, mode="existing")
        self.assertIn("`.github/workflows/board.yml` is this repository's own and is kept, so your workflow goes on"
                      " rendering the board", body)
        self.assertNotIn("nothing renders the board", body)
        self.assertNotIn("gh workflow run board.yml", body)

    def test_a_held_back_library_is_listed_on_one_line(self):
        files = dict(THEIR_FILES, **{"tools/VENDORED": "theirs\n"})
        body = self.body(files, mode="existing")
        self.assertIn("- `tools/sdlc_protocol/__init__.py` and `tools/sdlc_protocol/board.py`: `tools/VENDORED` is"
                      " this repository's own, and the vendored library and its record are brought together or not"
                      " at all", body)

    def test_a_held_back_library_holds_back_the_workflows_that_import_it(self):
        make_template(self.template, metrics=True)
        body = self.body(dict(THEIR_FILES, **{"tools/VENDORED": "theirs\n"}), mode="existing")
        self.assertIn("- `.github/workflows/board.yml` and `tools/board.py`: `tools/VENDORED` is this repository's own,"
                      " so the vendored library is not brought, and the board's workflow and its script need it", body)
        self.assertIn("- `.github/workflows/metrics.yml`, `tools/economics.py`, `tools/metrics.py` and"
                      " `tools/usage.py`: `tools/VENDORED` is this repository's own, so the vendored library is not"
                      " brought, and the metrics workflow and the scripts it runs need it", body)
        self.assertIn("4. `.github/workflows/board.yml` was not written (above), so nothing renders the board until the"
                      " board's workflow, its script and the vendored library are brought together by hand.", body)
        self.assertIn("The metrics workflow was not written (above), so nothing is computed or shared today", body)
        self.assertNotIn("Never target", body)

    def test_the_added_files_name_every_module_the_metrics_script_imports(self):
        make_template(self.template, metrics=True)
        body = self.body(THEIR_FILES, mode="existing")
        for rel in METRICS:
            self.assertIn(f"- `{rel}`", body)
        self.assertIn("Never target `board` or `metrics`, which the workflows force-push.", body)

    def test_a_module_of_theirs_holds_the_metrics_workflow_back(self):
        make_template(self.template, metrics=True)
        body = self.body(dict(THEIR_FILES, **{"tools/usage.py": "theirs\n"}), mode="existing")
        self.assertIn("- `.github/workflows/metrics.yml`, `tools/economics.py` and `tools/metrics.py`: `tools/usage.py`"
                      " is this repository's own, and the metrics workflow and the scripts it runs are brought together"
                      " or not at all", body)
        self.assertIn("Kept as they are, because this repository has them already:\n\n- `tools/usage.py`", body)
        self.assertIn("The metrics workflow was not written (above), so nothing is computed or shared today", body)
        self.assertIn("Never target `board`, which the workflows force-push.", body)

    def test_an_ignored_switch_is_never_said_to_hold_the_forms_word(self):
        """The switch the form's choice goes to is ignored, so it is not in the
        pull request, and the metrics workflow, which would read its absence
        as on, stays out with it, whichever word the form gave; the body says
        so, and never that the switch says off or on."""
        make_template(self.template, metrics=True)
        for metrics in ("off", "on"):
            with self.subTest(metrics=metrics):
                shutil.rmtree(self.root / "target", ignore_errors=True)
                body = self.body(NO_GIT, ignore="*metrics\n", mode="existing", metrics=metrics)
                self.assertIn("- `.github/workflows/metrics.yml`, `tools/economics.py`, `tools/metrics.py` and"
                              " `tools/usage.py`: `.github/symphony-metrics` is ignored by this repository, and the"
                              " metrics workflow and the scripts it runs come only with the metrics switch, which says"
                              " whether they share", body)
                self.assertIn("## What is shared\n\nNothing is computed or shared today: `.github/symphony-metrics` was"
                              " not written (above), and this pull request brings no metrics workflow to read it.\n",
                              body)
                self.assertNotIn("says `off`", body)
                self.assertNotIn("says `on`", body)
                self.assertNotIn("Sharing of anonymous aggregates is on", body)
                self.assertIn("Never target `board`, which the workflows force-push.", body)

    def test_an_ignored_switch_beside_a_metrics_workflow_there_already_is_said_to_read_as_on(self):
        make_template(self.template, metrics=True)
        body = self.body(dict(NO_GIT, **METRICS), ignore="*metrics\n", mode="existing", metrics="off")
        self.assertIn("Sharing of anonymous aggregates is on: `.github/symphony-metrics` was not written (above), and a"
                      " missing switch is read as `on`. Once a day", body)
        self.assertIn("or set the repository variable SDLC_METRICS to `off`", body)
        self.assertNotIn("Nothing is shared", body)

    def test_a_kept_switch_says_what_is_shared_whatever_the_form_asked(self):
        make_template(self.template, metrics=True)
        body = self.body(dict(THEIR_FILES, **{".github/symphony-metrics": "on\n"}), mode="existing", metrics="off")
        self.assertIn("Sharing of anonymous aggregates is on: `.github/symphony-metrics`, which this repository had"
                      " already and keeps, is read as `on`. Once a day `.github/workflows/metrics.yml` writes", body)
        self.assertIn("says `on`, where the form asked for `off`; it is kept", body)
        self.assertNotIn("Nothing is shared", body)
        shutil.rmtree(self.root / "target")
        body = self.body(dict(THEIR_FILES, **{".github/symphony-metrics": "maybe\n"}), mode="existing")
        self.assertIn("Nothing is shared: `.github/symphony-metrics`, which this repository had already and keeps, is"
                      " read as `off`, so the metrics workflow, where there is one, writes only that sharing is off.",
                      body)
        self.assertNotIn("Sharing of anonymous aggregates is on", body)

    def test_a_switch_that_cannot_be_written_in_new_mode_is_said_to_read_as_off(self):
        make_template(self.template, metrics=True)
        body = self.body({"README.md": "# widget\n", ".github/symphony-metrics/notes.md": "their notes\n"})
        self.assertIn("Nothing is shared: `.github/symphony-metrics` was not written (above), and what stands in its"
                      " place is read as `off`, so the metrics workflow", body)
        self.assertNotIn("Sharing of anonymous aggregates is on", body)

    def test_an_old_opt_out_beside_what_stands_in_the_switchs_place_names_both(self):
        """Something of the repository's own stands where the switch goes,
        which the metrics workflow reads as off, and the switch under its
        old name says off: the body names both, so that writing on where it
        says turns sharing on, not the old switch alone."""
        make_template(self.template, metrics=True)
        body = self.body({"README.md": "# widget\n", ".github/symphony-metrics/notes.md": "their notes\n",
                          ".github/sdlc-metrics": "off\n"})
        self.assertIn("Nothing is shared: `.github/sdlc-metrics` says `off`, and `.github/symphony-metrics` was not"
                      " written (above), and what stands in its place is read as `off`, so the metrics workflow", body)
        self.assertIn("Write `on` in both to share", body)
        self.assertNotIn("Write `on` there", body)

    def test_a_kept_switch_that_is_a_link_to_nothing_is_said_to_read_as_missing(self):
        """The metrics workflow meets a missing file through a link to
        nothing, so a kept switch that is one shares unless the old switch
        says off, and the body says why; an old switch that is one says
        nothing beside a kept switch saying on."""
        make_template(self.template, metrics=True)
        body = self.body(THEIR_FILES, links={".github/symphony-metrics": "gone"}, mode="existing")
        self.assertIn("Sharing of anonymous aggregates is on: `.github/symphony-metrics`, which this repository had"
                      " already and keeps, is a link to nothing, which the metrics workflow reads as a missing switch,"
                      " and a missing switch is read as `on`. Once a day", body)
        self.assertNotIn("`None`", body)
        shutil.rmtree(self.root / "target")
        body = self.body(dict(THEIR_FILES, **{".github/sdlc-metrics": "off\n"}),
                         links={".github/symphony-metrics": "gone"}, mode="existing")
        self.assertIn("Nothing is shared: `.github/sdlc-metrics` says `off`, so the metrics workflow", body)
        self.assertIn("Write `on` there to share", body)
        shutil.rmtree(self.root / "target")
        body = self.body(dict(THEIR_FILES, **{".github/symphony-metrics": "on\n"}),
                         links={".github/sdlc-metrics": "gone"}, mode="existing")
        self.assertIn("Sharing of anonymous aggregates is on: `.github/symphony-metrics`, which this repository had"
                      " already and keeps, is read as `on`.", body)
        self.assertNotIn("Nothing is shared", body)

    def test_a_workflow_written_without_a_script_it_runs_is_said_not_to_run(self):
        make_template(self.template, metrics=True)
        body = self.body({"README.md": "# widget\n", "tools/usage.py/notes.md": "their folder\n"})
        self.assertIn("- `.github/workflows/metrics.yml`\n", body)
        self.assertIn("- `tools/usage.py`: a folder of yours stands where this file goes", body)
        self.assertIn("The metrics workflow was written, but not every script it runs was (above), so it cannot run and"
                      " nothing is computed or shared today; the switch records your choice for when it can.", body)
        self.assertNotIn("The metrics workflow was not written", body)

    def test_what_claude_spends_is_said_to_stay_at_zero_with_the_protocol_alone(self):
        """Mode existing brings neither the template's session hooks nor its
        Claude workflows, which record what Claude spends, so the figures of
        what the work cost stay at zero there."""
        make_template(self.template, metrics=True)
        zero = ("The tokens Claude used, their price and the time it was at work, which METRICS.json counts as what"
                " the work cost, stay at zero here: the template's session hooks and its Claude workflows record"
                " them, and the protocol alone brings neither.")
        self.assertIn(zero, self.body(THEIR_FILES, mode="existing"))
        shutil.rmtree(self.root / "target")
        self.assertNotIn(zero, self.body())

    def test_ignored_files_get_what_to_do_instead(self):
        """The form adopts a repository once, so the note gives the steps by
        hand and never sends the person back to it after the merge."""
        body = self.body({"README.md": "# widget\n"}, ignore=".claude/\nCLAUDE.md\n", mode="existing")
        self.assertIn("- `CLAUDE.md` and `.claude/settings.json`: " + adopt.IGNORED_WHY, body)
        self.assertIn("Files this repository ignores were not written", body)
        self.assertIn("the form adopts a repository once, so asking there again after the merge is refused. What to"
                      " do instead:", body)
        self.assertNotIn("Stop ignoring them and ask again on the form", body)
        self.assertIn("add this section to the `CLAUDE.md` each session reads", body)
        self.assertIn("```markdown\n## How work is claimed\n", body)
        self.assertIn("claude plugin marketplace add OpenSpineConsortium/symphony-marketplace", body)
        self.assertIn('"symphony@symphony-marketplace": true', body)
        self.assertNotIn("gains the section", body)

    def test_ignored_files_with_no_way_by_hand_come_only_with_an_adoption_made_again(self):
        body = self.body(NO_GIT, ignore="tools/\n", mode="existing")
        self.assertIn("- `tools/VENDORED`, `tools/board.py`, `tools/sdlc_protocol/__init__.py`,"
                      " `tools/sdlc_protocol/board.py`: their content is not in this pull request, and only an adoption"
                      " made again brings it: stop ignoring them, close this pull request, or revert its merge on the"
                      " default branch once it is merged, delete its branch `symphony/adopt` where it is still there,"
                      " and ask again on the form.", body)
        self.assertNotIn("ask again once they are no longer ignored", body)

    def test_invalid_settings_get_the_keys_to_add_by_hand(self):
        body = self.body({".claude/settings.json": "{"}, mode="existing")
        self.assertIn("does not parse", body)
        self.assertIn('"symphony@symphony-marketplace": true', body)

    def test_sharing_on_without_and_with_the_metrics_workflow(self):
        body = self.body()
        self.assertIn("Sharing of anonymous aggregates is on", body)
        self.assertIn("does not carry its metrics workflow yet", body)
        self.assertIn("write `off` in `.github/symphony-metrics`", body)
        self.assertNotIn(PARALLEL, body)
        make_template(self.template, metrics=True)
        body = self.body()
        self.assertIn("writes METRICS.json to the branch `metrics`: counts, durations and rates of the protocol at"
                      " work, and never code", body)
        self.assertIn("JUDGE.json, the failure-type frequencies that someone's own judge writes", body)
        self.assertIn(PARALLEL, body)

    def test_the_parallel_sentence_follows_the_script_that_landed(self):
        make_template(self.template, metrics=True)
        for script, said in ((METRICS["tools/metrics.py"], True), (METRICS_BEFORE_BREAKDOWN, False)):
            write(self.template, "tools/metrics.py", script)
            for mode, files in (("new", None), ("existing", THEIR_FILES)):
                with self.subTest(breakdown=said, mode=mode):
                    shutil.rmtree(self.root / "target", ignore_errors=True)
                    body = self.body(files, mode=mode)
                    self.assertIn("writes METRICS.json to the branch `metrics`", body)
                    if said:
                        self.assertIn(PARALLEL, body)
                    else:
                        self.assertNotIn(PARALLEL, body)

    def test_the_metrics_sentence_follows_what_landed(self):
        make_template(self.template, metrics=True)
        files = dict(THEIR_FILES, **{".github/workflows/metrics.yml": "theirs\n"})
        body = self.body(files, mode="existing")
        self.assertIn("The metrics workflow was not written (above), so nothing is computed or shared today", body)
        self.assertNotIn(PARALLEL, body)
        self.assertNotIn("does not carry its metrics workflow yet", body)
        self.assertNotIn("`metrics`, which the workflows", body)
        self.assertIn("Never target `board`, which", body)

    def test_sharing_off(self):
        body = self.body(metrics="off")
        self.assertIn("Nothing is shared", body)
        self.assertNotIn("Sharing of anonymous aggregates is on", body)

    def test_an_old_opt_out_is_what_the_body_says_whatever_the_form_left(self):
        """A repository adopted before the rename says off in
        .github/sdlc-metrics: the form's default leaves the new switch off
        too, and the body says nothing is shared, naming both files, never
        that sharing is on."""
        body = self.body(dict(NO_GIT, **{".github/sdlc-metrics": "off\n"}), mode="existing", kind_read=True)
        self.assertIn("Nothing is shared: `.github/symphony-metrics` and `.github/sdlc-metrics` say `off`", body)
        self.assertIn("Write `on` in both to share", body)
        self.assertIn("`.github/sdlc-metrics`, the switch under its name before the rename to Symphony, says `off`, so"
                      " `.github/symphony-metrics` says `off` too, though the form left sharing on", body)
        self.assertNotIn("Sharing of anonymous aggregates is on", body)

    def test_a_kept_switch_that_says_off_is_never_called_on(self):
        """The note says the kept switch says off; the section on sharing
        says the same, not what the form asked."""
        body = self.body(dict(NO_GIT, **{".github/symphony-metrics": "off\n"}), mode="existing")
        self.assertIn(".github/symphony-metrics was there already and says `off`, where the form asked for `on`", body)
        self.assertIn("Nothing is shared: `.github/symphony-metrics`, which this repository had already and keeps, is"
                      " read as `off`, so the metrics workflow", body)
        self.assertNotIn("Sharing of anonymous aggregates is on", body)

    def test_the_title_per_mode(self):
        self.body()
        self.assertEqual(run(["body", "--title", "--manifest", str(self.manifest)])[1],
                         "Adopt the Symphony template\n")
        self.body(THEIR_FILES, mode="existing")
        self.assertEqual(run(["body", "--title", "--manifest", str(self.manifest)])[1],
                         "Take up the Symphony claim protocol\n")

    def test_a_file_that_is_not_a_manifest(self):
        write(self.root, "other.json", '{"schema": "something else"}\n')
        self.assertEqual(run(["body", "--manifest", str(self.root / "other.json")])[0], 1)

    def test_the_body_fits_a_pull_request(self):
        for index in range(400):
            write(self.template, f"docs/many/page-{index:03d}-with-a-long-name.md", "a page\n")
        self.assertLess(len(self.body()), 65536)

    def test_without_a_report_the_body_says_nothing_of_the_settings(self):
        body = self.body()
        self.assertNotIn("## Settings", body)
        self.assertNotIn("Setup App", body)
        self.assertIn("2. From a clone", body)

    def test_the_settings_applied_in_new_mode(self):
        body = self.body(settings=report())
        self.assertIn("## Settings\n\nThe Symphony Setup App, which you installed on this repository, applied in"
                      " this run the settings `scripts/setup-repo.sh` applies", body)
        self.assertIn("- The ruleset \"Protect the default branch\" for the default branch: created. It requires a"
                      " pull request that passes the check named \"check\" and blocks force pushes and deletions, and"
                      " nobody can bypass it. This pull request brings that check and runs it where Actions is"
                      " enabled, so it can merge once that is green; if the check never reports, or you close this"
                      f" pull request instead, remove the check from the ruleset, or the ruleset, at {RULES}.", body)
        self.assertIn("- Delete head branches on merge and allow auto-merge: on.", body)
        self.assertIn(f"- The topic `symphony`: set, {TOPIC_WHY}; the topics you had stay.", body)
        self.assertIn("- Secret scanning and push protection: on.", body)
        self.assertIn(f"{ACTIONS}: on, {ACTIONS_WHY}.", body)
        self.assertIn("the topic symphony, secret scanning with push protection, and letting GitHub Actions create and"
                      " approve pull requests)", body)
        self.assertIn(f"\n\n{STAYS}", body)
        # A report from before the Setup App stayed installed may say it
        # uninstalled itself; the body still renders, and says it stays.
        body = self.body(settings=dict(report(), uninstalled=True))
        self.assertIn(STAYS, body)
        self.assertNotIn("uninstalled itself", body)
        self.assertIn("2. The GitHub side is set up (Settings above), so `bash scripts/setup-repo.sh` is not needed",
                      body)
        self.assertIn("is done but for GitHub's reading of `.github/CODEOWNERS`", body)
        self.assertIn(f"--area AREA`, which turns auto-merge and \"{adopt.ACTIONS_LABEL}\" off again, and, after"
                      " reading", body)
        self.assertNotIn("2. From a clone", body)
        self.assertNotIn("add the name of your own check", body)
        self.assertNotIn("written but not enforced", body)
        self.assertNotIn("was used in this run", body)
        self.assertLess(body.index("## Settings"), body.index("## Next steps"))
        self.assertLess(body.index("## What is shared"), body.index("## Settings"))

    def test_an_organization_uninstalls_from_its_own_page(self):
        body = self.body(settings=report(), owner_type="Organization")
        self.assertIn("It holds Administration on this repository and, where its installation accepted them,"
                      " Administration, Secrets and Variables on the organization; you can uninstall it at any time, from the repository's Settings, GitHub Apps,"
                      " at https://github.com/octo-org/widget/settings/installations, or from the organization's at"
                      " https://github.com/organizations/octo-org/settings/installations.", body)

    def test_the_token_store_says_what_became_of_it(self):
        store = "- The environment `token-store`: "
        body = self.body(settings=report(states=dict(ALL_DONE, token_store="done")))
        self.assertIn(store + "made, limited to the default branch, so only the default branch's Token workflow"
                      " ever holds the Symphony App's token.\n", body)
        self.assertNotIn("was used in this run", body)
        body = self.body(settings=report(states=dict(ALL_DONE, token_store="failed"),
                                         details={"token_store": "HTTP 403: Resource not accessible"}))
        self.assertIn(store + "not set up", body)
        self.assertIn("https://github.com/octo-org/widget/settings/environments and", body)
        self.assertIn("was used in this run", body)
        # A report from before the step says nothing of it.
        self.assertNotIn(store, self.body(settings=report()))

    def lending_report(self, state, lent=(), left=(), failed=(), detail="", mode="new", unreached=(), missing=()):
        settings = report(states=dict(ALL_DONE, token_lending=state), details={"token_lending": detail}, mode=mode)
        settings["lending"] = {"lent": list(lent), "left": list(left), "unreached": list(unreached),
                               "missing": list(missing), "failed": list(failed)}
        return settings

    def test_the_tokens_lent_are_named_with_how_to_lend_more(self):
        body = self.body(settings=self.lending_report("done", lent=("SYMPHONY_CLAUDE_3", "SYMPHONY_CLAUDE_ACCOUNTS"),
                                                      left=("CLAUDE_CODE_OAUTH_TOKEN",)),
                         owner_type="Organization")
        self.assertIn(f"{LENDING} lent to this repository: `SYMPHONY_CLAUDE_3` and `SYMPHONY_CLAUDE_ACCOUNTS`;"
                      " `CLAUDE_CODE_OAUTH_TOKEN` reaches this repository already, shared with all the"
                      " organization's repositories or its private ones, and is left as GitHub shares it. Only your"
                      " own tokens are lent, never another person's, and no value or visibility"
                      f" was changed.{LEND_MORE}\n", body)
        self.assertLess(body.index(ACTIONS), body.index(LENDING))

    def test_tokens_that_cannot_reach_the_repository_say_so(self):
        body = self.body(settings=self.lending_report("none-lent", unreached=("SYMPHONY_CLAUDE_3",),
                                                      missing=("CLAUDE_CODE_OAUTH_TOKEN",)),
                         owner_type="Organization")
        self.assertIn(f"{LENDING} `SYMPHONY_CLAUDE_3` does not reach this repository, shared only with the"
                      " organization's private and internal repositories or in another way than with selected ones,"
                      " and the run changes no visibility; an owner of the organization switches it to selected"
                      " repositories to lend it here; `CLAUDE_CODE_OAUTH_TOKEN` is not among the organization's"
                      " secrets and variables, and the run makes none.", body)

    def test_a_requester_with_no_token_is_told_how_to_lend_one(self):
        detail = "press Add Token on the control panel's Tokens page to lend one of yours"
        body = self.body(settings=self.lending_report("none-owned", detail=detail), owner_type="Organization")
        self.assertIn(f"gives each token's owner; {detail}.{LEND_MORE}", body)
        self.assertNotIn("GitHub said", body.split(LENDING)[1].split("\n")[0])

    def test_a_loan_refused_keeps_githubs_words(self):
        body = self.body(settings=self.lending_report("failed", lent=("SYMPHONY_CLAUDE_3",),
                                                      failed=("SYMPHONY_CLAUDE_SETTINGS",),
                                                      detail="SYMPHONY_CLAUDE_SETTINGS: HTTP 500: boom"),
                         owner_type="Organization")
        self.assertIn("not lent: `SYMPHONY_CLAUDE_SETTINGS` (GitHub said: SYMPHONY_CLAUDE_SETTINGS: HTTP 500: boom)",
                      body)

    def test_tokens_not_lent_say_why_and_how(self):
        body = self.body(settings=self.lending_report("not-granted"), owner_type="Organization")
        self.assertIn(f"{LENDING} not lent, since the run could not make a token with the organization permissions"
                      " Secrets and Variables (Read and write), most often because the Symphony Setup App's installation"
                      " on the organization has not granted them; an owner of the organization accepts them at"
                      f" https://github.com/organizations/octo-org/settings/installations.{LEND_MORE}", body)
        body = self.body(settings=self.lending_report("none-owned", mode="existing"), mode="existing",
                         files=THEIR_FILES, owner_type="Organization")
        self.assertIn(f"{LENDING} none lent, since no token in it names you as its owner", body)
        self.assertIn(LEND_MORE, body)

    def test_the_runs_own_reason_is_not_given_as_githubs(self):
        body = self.body(settings=self.lending_report("failed", detail="the repository's id could not be read"),
                         owner_type="Organization")
        self.assertIn(f"{LENDING} not lent (the repository's id could not be read).", body)
        body = self.body(settings=self.lending_report("not-granted", detail="HTTP 403: Resource not accessible"),
                         owner_type="Organization")
        self.assertIn("(Read and write) (GitHub said: HTTP 403: Resource not accessible), most often", body)

    def test_no_lending_line_for_a_personal_account_or_an_older_report(self):
        body = self.body(settings=self.lending_report("not-tried"))
        self.assertNotIn(LENDING, body)
        body = self.body(settings=self.lending_report("done", lent=("SYMPHONY_CLAUDE_3",)))
        self.assertNotIn(LENDING, body)
        self.assertNotIn(LENDING, self.body(settings=report(), owner_type="Organization"))
        body = self.body(settings=self.lending_report("not-tried"), owner_type="Organization")
        self.assertNotIn(LENDING, body)

    def test_a_private_repositorys_ruleset_is_said_to_be_unenforced_on_free(self):
        body = self.body(settings=report(private=True))
        self.assertIn(f"at {RULES}. On GitHub Free a private repository's ruleset is written but not enforced.", body)

    def test_the_settings_applied_in_existing_mode(self):
        body = self.body(THEIR_FILES, mode="existing", settings=report(mode="existing", required_check=False))
        self.assertIn("applied in this run the settings the template's setup script applies", body)
        self.assertIn("created. It requires a pull request and blocks force pushes and deletions; add the name of"
                      f" your own check to it at {RULES}, so the default branch takes only pull requests that pass"
                      " it.", body)
        self.assertIn("3. The default branch has the ruleset above (Settings), which targets it alone."
                      " Never target `board`, which the workflows force-push.", body)
        self.assertNotIn("3. Protect the default branch", body)
        self.assertNotIn("setup-repo.sh", body)
        self.assertNotIn("check named \"check\"", body)

    def test_a_ruleset_the_repository_had_is_left_and_checked(self):
        body = self.body(settings=report(states=dict(ALL_DONE, ruleset="exists")))
        self.assertIn(f"this repository has one of that name already, which was left as it is; check at {RULES}", body)
        self.assertIn("2. The GitHub side is set up", body)
        body = self.body(THEIR_FILES, mode="existing",
                         settings=report(mode="existing", required_check=False, states=dict(ALL_DONE, ruleset="exists")))
        self.assertIn(f"3. Check the ruleset you have (Settings above) at {RULES}: it should protect", body)

    def test_a_setting_github_refused_is_said_in_its_words_and_left_by_hand(self):
        failed = dict(ALL_DONE, ruleset="failed")
        body = self.body(settings=report(states=failed, details={"ruleset": "HTTP 403: Resource not accessible"}))
        self.assertIn("which you installed on this repository, was used in this run for the settings", body)
        self.assertNotIn("applied in this run", body)
        self.assertIn("- The ruleset \"Protect the default branch\": not created (GitHub said: HTTP 403: Resource not"
                      f" accessible). Protect the default branch, and only it, at {RULES}", body)
        self.assertIn("2. For what the Settings above could not do: from a clone", body)
        self.assertNotIn("2. The GitHub side is set up", body)
        self.assertIn(f"which turns auto-merge and \"{adopt.ACTIONS_LABEL}\" off again", body)
        body = self.body(THEIR_FILES, mode="existing",
                         settings=report(mode="existing", states=failed, details={"ruleset": "HTTP 403: no"}))
        self.assertIn(f"3. Protect the default branch, and only it, at {RULES}", body)
        failed = dict(ALL_DONE, toggles="failed")
        body = self.body(settings=report(states=failed, details={"toggles": "HTTP 403: no"}))
        self.assertIn("- Delete head branches on merge and allow auto-merge: not changed (GitHub said: HTTP 403: no);"
                      " tick both under https://github.com/octo-org/widget/settings.", body)
        self.assertIn("2. For what the Settings above could not do", body)
        self.assertIn(f"--area AREA`, which turns \"{adopt.ACTIONS_LABEL}\" off again, and", body)
        self.assertNotIn("auto-merge off again", body)
        self.assertNotIn("auto-merge and", body)

    def test_the_topic_there_already_or_refused(self):
        body = self.body(settings=report(details={"topic": "was there already"}))
        self.assertIn(f"- The topic `symphony`: was there already, {TOPIC_WHY}.", body)
        self.assertIn("applied in this run", body)
        self.assertIn("2. The GitHub side is set up", body)
        self.assertNotIn("the topics you had stay", body)
        failed = dict(ALL_DONE, topic="failed")
        body = self.body(settings=report(states=failed, details={"topic": "HTTP 403: no"}))
        self.assertIn("- The topic `symphony`: not set (GitHub said: HTTP 403: no); add it with the gear beside About"
                      f" on https://github.com/octo-org/widget, {TOPIC_WHY}.", body)
        self.assertIn("was used in this run for the settings", body)
        self.assertIn("2. For what the Settings above could not do", body)
        self.assertIn("delete-on-merge and auto-merge, the topic symphony, secret scanning, letting GitHub Actions"
                      " create and approve pull requests, the labels", body)
        # A report that says nothing of the topic, from an older setup.py,
        # reads as not set, with no words of GitHub's.
        without = {key: state for key, state in ALL_DONE.items() if key != "topic"}
        body = self.body(settings=report(states=without))
        self.assertIn("- The topic `symphony`: not set; add it with the gear beside About", body)
        self.assertNotIn("GitHub said", body)

    def test_secret_scanning_refused_is_usually_the_plan(self):
        states = dict(ALL_DONE, secret_scanning="failed", push_protection="not-tried")
        details = {"secret_scanning": "HTTP 422: Not available.", "push_protection": "secret scanning is not on"}
        body = self.body(settings=report(states=states, details=details))
        self.assertIn("- Secret scanning: not turned on (GitHub said: HTTP 422: Not available.). Usually that is the"
                      " plan or the visibility", body)
        self.assertIn("was used in this run for the settings", body)
        self.assertNotIn("applied in this run", body)
        self.assertIn("https://github.com/octo-org/widget/settings/security_analysis", body)
        self.assertIn("push protection was not tried, since it needs scanning on.", body)
        self.assertIn("2. The GitHub side is set up", body)
        self.assertIn("is done but for secret scanning or push protection, above, and GitHub's reading of"
                      " `.github/CODEOWNERS`", body)
        states = dict(ALL_DONE, push_protection="failed")
        body = self.body(settings=report(states=states, details={"push_protection": "HTTP 422: No."}))
        self.assertIn("- Secret scanning: on. Push protection: not turned on (GitHub said: HTTP 422: No.); turn it on"
                      " under https://github.com/octo-org/widget/settings/security_analysis", body)
        self.assertIn("is done but for secret scanning or push protection, above", body)

    def test_actions_on_or_on_already_says_what_the_box_is_for(self):
        """The box lets the template's two workflows open their pull
        requests; ticked by this run, the line says too that a workflow may
        now approve one."""
        body = self.body(settings=report())
        self.assertIn(f"{ACTIONS}: on, {ACTIONS_WHY}. It lets a workflow approve a pull request too, which matters only"
                      " where a ruleset requires a review.", body)
        self.assertIn("applied in this run", body)
        self.assertNotIn("Until it is on", body)
        self.assertIn("is done but for GitHub's reading of `.github/CODEOWNERS`", body)
        body = self.body(settings=report(details={"actions_pull_requests": "was on already"}))
        self.assertIn(f"{ACTIONS}: was on already, {ACTIONS_WHY}.", body)
        self.assertNotIn("It lets a workflow approve", body)
        self.assertIn("applied in this run", body)

    def test_actions_forbidden_by_policy_says_who_allows_it_and_where(self):
        """GitHub's 409 is the policy of the organization or its
        enterprise, which no setting of the repository's changes: the line
        names who allows the box and where, then where to tick it, and what
        the two workflows answer with meanwhile. The rest of the GitHub
        side is set up, so the setup script is not sent for. A personal
        account's repository has no organization, so its line keeps to
        GitHub's words and the repository's own page, and names no
        enterprise as the cause."""
        states = dict(ALL_DONE, actions_pull_requests="forbidden")
        body = self.body(settings=report(states=states, details={"actions_pull_requests": "HTTP 409: Conflict"}),
                         owner_type="Organization")
        self.assertIn(f"{ACTIONS}: not turned on, since the policy of the organization, or of its enterprise,"
                      " forbids it (GitHub said: HTTP 409: Conflict). An owner of the organization allows it under"
                      " Workflow permissions at https://github.com/organizations/octo-org/settings/actions, or, where"
                      " the enterprise forbids it there, an owner of the enterprise under the enterprise's Policies,"
                      f" Actions; then tick it under Workflow permissions at {ACTIONS_PAGE}. {MEANWHILE}", body)
        self.assertIn("was used in this run for the settings", body)
        self.assertIn("2. The GitHub side is set up", body)
        self.assertIn("is done but for letting GitHub Actions create and approve pull requests, above, and GitHub's"
                      " reading of `.github/CODEOWNERS`", body)
        body = self.body(settings=report(states=states, details={"actions_pull_requests": "HTTP 409"}))
        self.assertIn(f"{ACTIONS}: not turned on, since GitHub answered that a policy above this repository holds it"
                      f" (GitHub said: HTTP 409); tick it under Workflow permissions at {ACTIONS_PAGE} once that page"
                      f" allows it. {MEANWHILE}", body)
        self.assertNotIn("/organizations/octo-org/settings/actions", body)
        self.assertNotIn("enterprise", body)

    def test_actions_refused_otherwise_is_ticked_by_hand(self):
        states = dict(ALL_DONE, actions_pull_requests="failed")
        body = self.body(settings=report(states=states, details={"actions_pull_requests": "HTTP 403: no"}))
        self.assertIn(f"{ACTIONS}: not turned on (GitHub said: HTTP 403: no); tick it under Workflow permissions at"
                      f" {ACTIONS_PAGE}. {MEANWHILE}", body)
        self.assertNotIn("forbids it", body)
        self.assertIn("was used in this run for the settings", body)
        self.assertIn("is done but for letting GitHub Actions create and approve pull requests, above, and", body)
        # With push protection refused too, both are named once, in one list.
        states = dict(states, push_protection="failed")
        body = self.body(settings=report(states=states, details={"push_protection": "HTTP 422: No."}))
        self.assertIn("is done but for secret scanning or push protection and letting GitHub Actions create and approve"
                      " pull requests, above, and GitHub's reading of `.github/CODEOWNERS`", body)

    def test_the_box_is_the_setup_scripts_only_where_the_script_that_landed_ticks_it(self):
        """The run copies the template's default branch, whose setup script
        may be from before the box: the pull request then names the box
        nowhere among that script's steps, nor among what the setup issue's
        first box leaves, while the Setup App's own line for it stands."""
        write(self.template, adopt.SETUP_SCRIPT, SETUP_SCRIPT_BEFORE_BOX)
        body = self.body(settings=report(outcome="not-installed"))
        self.assertIn("so this run could not apply the settings `scripts/setup-repo.sh` applies (the default branch's"
                      " ruleset, delete-on-merge and auto-merge, the topic symphony, and secret scanning with push"
                      " protection). Step 2 of the next steps applies them by hand", body)
        self.assertIn("the topic symphony, secret scanning, the labels and a check of `.github/CODEOWNERS`.", body)
        self.assertNotIn("GitHub Actions", body)
        states = dict(ALL_DONE, actions_pull_requests="forbidden")
        body = self.body(settings=report(states=states, details={"actions_pull_requests": "HTTP 409"}))
        self.assertIn("was used in this run for the settings `scripts/setup-repo.sh` applies (the default branch's"
                      " ruleset, delete-on-merge and auto-merge, the topic symphony, and secret scanning with push"
                      " protection); what it could do", body)
        self.assertIn(f"{ACTIONS}: not turned on, since GitHub answered", body)
        self.assertIn("is done but for GitHub's reading of `.github/CODEOWNERS`", body)
        body = self.body(settings=report(states=dict(ALL_DONE, ruleset="failed"), details={"ruleset": "HTTP 403: no"}))
        self.assertIn("2. For what the Settings above could not do: from a clone", body)
        self.assertIn("the topic symphony, secret scanning, the labels", body)
        self.assertIn(f"{ACTIONS}: on, {ACTIONS_WHY}.", body)

    def test_crowd_mode_turns_off_again_what_the_settings_say_is_on(self):
        """crowd.py setup turns auto-merge off, and the box too, so the step
        names each one the Settings above say is on, and nothing when
        neither is."""
        box = f"\"{adopt.ACTIONS_LABEL}\""
        forbidden, refused = dict(ALL_DONE, actions_pull_requests="forbidden"), dict(ALL_DONE, toggles="failed")
        cases = ((ALL_DONE, f"--area AREA`, which turns auto-merge and {box} off again, and"),
                 (forbidden, "--area AREA`, which turns auto-merge off again, and"),
                 (refused, f"--area AREA`, which turns {box} off again, and"),
                 (dict(refused, actions_pull_requests="failed"), "--area AREA` and, after reading"))
        for states, said in cases:
            with self.subTest(states=states):
                self.assertIn(said, self.body(settings=report(states=states)))

    def test_an_older_report_without_the_actions_box_still_renders(self):
        """A report from before the box was a setting has no word on it: in
        mode new it reads as not turned on, with no words of GitHub's, and
        the schema it carries is still the one the body reads."""
        without = {key: state for key, state in ALL_DONE.items() if key != "actions_pull_requests"}
        body = self.body(settings=report(states=without))
        self.assertIn(f"{ACTIONS}: not turned on; tick it under Workflow permissions at {ACTIONS_PAGE}. {MEANWHILE}",
                      body)
        self.assertNotIn("GitHub said", body)
        self.assertIn("was used in this run for the settings", body)
        self.assertIn("- Secret scanning and push protection: on.", body)
        self.assertEqual(adopt.SETUP_SCHEMA, "sdlc-setup/1")

    def test_existing_mode_names_no_actions_box(self):
        """The protocol alone brings neither workflow, and scripts/setup.py
        does not try the box there: the section names it nowhere and counts
        the settings applied without it."""
        details = {"actions_pull_requests": "the protocol alone opens no pull request with GitHub Actions"}
        settings = report(mode="existing", required_check=False, details=details,
                          states=dict(ALL_DONE, actions_pull_requests="not-tried"))
        body = self.body(THEIR_FILES, mode="existing", settings=settings)
        self.assertIn("applied in this run the settings the template's setup script applies (the default branch's"
                      " ruleset, delete-on-merge and auto-merge, the topic symphony, and secret scanning with push"
                      " protection);", body)
        self.assertNotIn("GitHub Actions", body)
        body = self.body(THEIR_FILES, mode="existing", settings=report(outcome="not-installed", mode="existing"))
        self.assertNotIn("GitHub Actions", body)

    def test_the_check_pinned_to_github_actions_says_why_it_matters(self):
        body = self.body(settings=report(states=dict(ALL_DONE, check_source="done")))
        self.assertIn(f"at {RULES}.\n{PIN_DONE}\n- Delete head branches", body)
        self.assertIn("applied in this run the settings", body)
        self.assertIn("2. The GitHub side is set up (Settings above)", body)
        body = self.body(settings=report(states=dict(ALL_DONE, check_source="exists")))
        self.assertIn("- The check \"check\" in that ruleset: it named its source already, which was left as it is.",
                      body)
        self.assertIn("2. The GitHub side is set up (Settings above)", body)

    def test_a_check_not_pinned_says_how_to_pin_it(self):
        """Not yet, refused or not tried: why, in GitHub's words where they
        are GitHub's, what it leaves open, and the two ways to pin it; the
        setup script is then what step 2 runs for what is left."""
        cases = (
            ("not-yet", "GitHub Actions had not reported the check named \"check\" on the branch symphony/adopt"
             " within 10 minutes", "not pinned to GitHub Actions yet: GitHub Actions had not reported the check"
             " named \"check\" on the branch symphony/adopt within 10 minutes."),
            ("failed", "HTTP 422: Validation Failed", "not pinned to GitHub Actions (GitHub said: HTTP 422:"
             " Validation Failed)."),
            ("not-tried", "no token that reads check runs could be made for this run", "not pinned to GitHub"
             " Actions: no token that reads check runs could be made for this run."),
        )
        for state, detail, said in cases:
            with self.subTest(state=state):
                body = self.body(settings=report(states=dict(ALL_DONE, check_source=state),
                                                 details={"check_source": detail}))
                self.assertIn(f"- The check \"check\" in that ruleset: {said} {PIN_FIX}", body)
                self.assertIn("was used in this run for the settings", body)
                self.assertIn("2. For what the Settings above could not do: from a clone", body)
                self.assertNotIn("2. The GitHub side is set up", body)

    def test_no_pin_line_where_no_pin_was_expected(self):
        """A ruleset left as it was, one not created, one that requires no
        check, mode existing, and a report from before the pin: no line, and
        nothing of the pin keeps the settings from reading as applied."""
        left = dict(ALL_DONE, ruleset="exists", check_source="not-tried")
        body = self.body(settings=report(states=left, details={
            "check_source": "the ruleset of that name was there already and is left as it is"}))
        self.assertNotIn("in that ruleset", body)
        self.assertIn("2. The GitHub side is set up", body)
        body = self.body(settings=report(states=dict(ALL_DONE, ruleset="failed", check_source="not-tried")))
        self.assertNotIn("in that ruleset", body)
        details = {"actions_pull_requests": "the protocol alone opens no pull request with GitHub Actions",
                   "check_source": "the protocol alone brings no check, and its ruleset requires none"}
        settings = report(mode="existing", required_check=False, details=details,
                          states=dict(ALL_DONE, actions_pull_requests="not-tried", check_source="not-tried"))
        body = self.body(THEIR_FILES, mode="existing", settings=settings)
        self.assertNotIn("in that ruleset", body)
        self.assertNotIn("GitHub Actions", body)
        self.assertIn("applied in this run the settings", body)
        self.assertNotIn("in that ruleset", self.body(settings=report()))

    def test_the_setup_app_not_installed(self):
        body = self.body(settings=report(outcome="not-installed"))
        self.assertIn("## Settings\n\nNone of the settings was changed: no token for this repository could be made"
                      " from the Symphony Setup App, which means it is not installed on this repository, or its"
                      " installation does not include it, or GitHub did not answer; so this run could not apply the"
                      " settings `scripts/setup-repo.sh` applies", body)
        self.assertIn("Step 2 of the next steps applies them by hand, with `scripts/setup-repo.sh`.", body)
        self.assertIn("If you did install it, check that its installation includes this repository and say so on"
                      " your request's issue; it stays installed, and you can uninstall it at any time at"
                      " https://github.com/settings/installations.", body)
        self.assertIn("2. From a clone", body)
        self.assertNotIn("uninstall it now", body)
        self.assertNotIn("which turns auto-merge off again", body)
        self.assertNotIn("Nothing of the GitHub side", body)
        body = self.body(THEIR_FILES, mode="existing", settings=report(outcome="not-installed", mode="existing"))
        self.assertIn("the settings the template's setup script applies", body)
        self.assertIn("Step 3 of the next steps protects the default branch; the two toggles are under"
                      " https://github.com/octo-org/widget/settings, the topic symphony is added with the gear beside"
                      " About on https://github.com/octo-org/widget, and secret scanning with push protection under"
                      " https://github.com/octo-org/widget/settings/security_analysis, where the plan offers them.",
                      body)
        self.assertIn(f"3. Protect the default branch, and only it, at {RULES}", body)

    def test_the_front_door_without_a_setup_app(self):
        body = self.body(settings=report(outcome="not-set-up"))
        self.assertIn("None of the settings was changed: this front door has no Setup App yet", body)
        self.assertIn("Step 2 of the next steps applies them by hand", body)
        self.assertIn("2. From a clone", body)
        self.assertNotIn("uninstall", body.replace("uninstalling the App stops it too", ""))

    def test_the_front_doors_setup_app_broken(self):
        body = self.body(settings=report(outcome="front-door-broken"))
        self.assertIn("None of the settings was changed: this front door's Setup App is not working (its id or"
                      " private key there is wrong, it is not installed on the front door's own repository, or GitHub"
                      " did not answer), which is for the front door's owner to put right, and the run has told them",
                      body)
        self.assertIn("If you installed the Setup App, it stays installed, so a run made once the owner has put it"
                      " right can apply them; you can uninstall it at any time at"
                      " https://github.com/settings/installations.", body)
        self.assertIn("2. From a clone", body)

    def test_a_settings_step_that_died_before_its_report(self):
        body = self.body(settings=report(outcome="not-reported"), owner_type="Organization")
        self.assertIn("## Settings\n\nThe step that applies the settings stopped before it could say what it did. If"
                      " you installed the Setup App, some of the settings `scripts/setup-repo.sh` applies", body)
        # Mode new's box, which the step may have ticked, is on a page of
        # its own; mode existing does not try it.
        self.assertIn("check https://github.com/octo-org/widget/settings/rules,"
                      f" https://github.com/octo-org/widget/settings and {ACTIONS_PAGE}. Step 2 of the next steps"
                      " applies them by hand", body)
        self.assertIn("applies them by hand, with `scripts/setup-repo.sh`. The Symphony Setup App stays installed,"
                      " acting only during an adoption run.", body)
        self.assertIn("or from the organization's at https://github.com/organizations/octo-org/settings/installations",
                      body)
        self.assertIn("2. From a clone", body)
        self.assertNotIn("which turns auto-merge off again", body)
        body = self.body(THEIR_FILES, mode="existing", settings=report(outcome="not-reported", mode="existing"))
        self.assertIn("check https://github.com/octo-org/widget/settings/rules and"
                      " https://github.com/octo-org/widget/settings. Step 3 of the next steps protects", body)
        self.assertNotIn(ACTIONS_PAGE, body)

    def test_a_repository_the_run_began_says_so(self):
        """A repository with no commit got its first from the run, the README
        GitHub's own "Add a README file" makes, before the pull request
        opened: the text says so where it says what changes before the
        merge, and only then."""
        body = self.body(kind_read=True, began=True)
        self.assertIn("asked for it on the adoption form (https://github.com/OpenSpineConsortium/symphony-start)."
                      " The repository had no commit, so the run first made one, as GitHub's own \"Add a README"
                      " file\" does: a README.md holding the repository's name, on the default branch, which this"
                      " pull request goes into. Nothing else changes until you merge it.", body)
        self.assertNotIn("Nothing changes until you merge it.", body)
        self.assertIn("Nothing changes until you merge it.", self.body(kind_read=True))

    def test_a_form_that_left_the_kind_to_the_run(self):
        """The one-button form: the kind was read from the tree, and the
        note says so in the form's own terms, with the other kind one form
        away once this pull request is closed, or its merge reverted, since
        the form adopts a repository once."""
        body = self.body(kind_read=True)
        self.assertIn("asked for it on the adoption form", body)
        self.assertIn("The form left the kind to the run, which read this repository as a new repository, since its"
                      " default branch held nothing but what GitHub makes when it initializes one", body)
        self.assertIn("For the protocol alone instead, close this pull request, or revert its merge on the default"
                      " branch once it is merged, since the form adopts a repository once; then delete its branch"
                      " `symphony/adopt`, where it is still there, and open the form at"
                      " https://github.com/OpenSpineConsortium/symphony-start choosing the other kind.", body)
        self.assertIn("`.github/CODEOWNERS` names `mona`, who asked for this pull request, because GitHub",
                      self.body(owner_type="Organization", kind_read=True))
        body = self.body(THEIR_FILES, mode="existing", kind_read=True)
        self.assertIn("which read this repository as an existing repository, since its default branch holds files"
                      " of its own. For the whole template instead", body)

    def test_a_file_that_is_not_a_report(self):
        self.body()
        for bad in ('{"schema": "something else"}', '{"schema": "sdlc-setup/1", "outcome": "done", "settings": {}}',
                    '{"schema": "sdlc-setup/1", "outcome": "applied", "settings": []}',
                    '{"schema": "sdlc-setup/1", "outcome": "applied", "settings": {"ruleset": {"state": 1}}}',
                    '{"schema": "sdlc-setup/1", "outcome": "applied", "settings": {"ruleset": {"state": "done",'
                    ' "detail": "two\\nlines"}}}', "[]", "null", "{"):
            path = write(self.root, "bad.json", bad + "\n")
            with self.subTest(report=bad):
                code, _, err = run(["body", "--manifest", str(self.manifest), "--settings", str(path)])
                self.assertEqual(code, 1)
                self.assertEqual(len(err.splitlines()), 1)
                self.assertIn("bad.json", err)
                self.assertNotIn("manifest.json", err)
        code, _, err = run(["body", "--manifest", str(write(self.root, "list.json", "[]\n"))])
        self.assertEqual((code, len(err.splitlines())), (1, 1))


class Labels(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.template = make_template(Path(self.scratch.name) / "template")

    def labels(self, mode):
        code, out, err = run(["labels", "--template", str(self.template), "--mode", mode])
        self.assertEqual(code, 0, err)
        return [line.split("\t") for line in out.splitlines()]

    def test_new_mode_makes_every_label_of_the_template(self):
        labels = self.labels("new")
        self.assertEqual([name for name, _, _ in labels],
                         ["todo", "claimed", "in-review", "blocker", "account:main", "epic", "blocked"])
        self.assertTrue(all(len(colour) == 6 and description for _, colour, description in labels))

    def test_existing_mode_leaves_out_team_mode(self):
        self.assertEqual([label[0] for label in self.labels("existing")],
                         ["todo", "claimed", "in-review", "blocker", "account:main"])

    def test_a_template_without_the_list(self):
        write(self.template, adopt.INIT_SCRIPT, "print('no labels here')\n")
        self.assertEqual(run(["labels", "--template", str(self.template), "--mode", "new"])[0], 1)


if __name__ == "__main__":
    unittest.main()
