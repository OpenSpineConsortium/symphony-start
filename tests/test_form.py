"""The form, the workflows and scripts/adopt.py agree, and the workflows keep
their own rules.

parse matches the form's labels and options word for word, so a change to
one that the other does not follow fails here instead of refusing every
request. Every workflow passes values to its shell steps only through env:,
since an expression inside run: is pasted into the script before bash reads
it, and uses only GitHub's own actions and create-github-app-token, each on
a major tag.
"""

import re
import unittest
from pathlib import Path

from trees import adopt

ROOT = Path(__file__).resolve().parent.parent
FORM = ROOT / ".github/ISSUE_TEMPLATE/adopt.yml"
WORKFLOWS = sorted((ROOT / ".github/workflows").glob("*.yml"))
# GitHub's own actions on a major tag, and this repository's own reusable
# workflow, which the issue path calls.
ALLOWED_ACTIONS = re.compile(r"actions/(checkout|setup-python|create-github-app-token)@v\d+|\./\.github/workflows/adopt-run\.yml")
SETUP_APP_INSTALL = "https://github.com/apps/symphony-setup/installations/new"
RUN_KEY = re.compile(r"^(\s*)(?:- )?run:\s*(.*)$")


def run_blocks(text):
    """Each run: script of a workflow as (line number, its text)."""
    lines = text.split("\n")
    for index, line in enumerate(lines):
        found = RUN_KEY.match(line)
        if not found:
            continue
        indent, rest = len(found.group(1)), found.group(2)
        if not rest.startswith(("|", ">")):
            yield index + 1, rest
            continue
        body = []
        for following in lines[index + 1:]:
            if following.strip() and len(following) - len(following.lstrip(" ")) <= indent:
                break
            body.append(following)
        yield index + 1, "\n".join(body)


class TheForm(unittest.TestCase):
    def setUp(self):
        self.text = FORM.read_text(encoding="utf-8")

    def test_every_field_parse_reads_is_a_label_of_the_form(self):
        labels = re.findall(r"^      label: (.+)$", self.text, re.MULTILINE)
        self.assertEqual(labels, list(adopt.FIELDS))

    def test_every_kind_the_merge_choice_and_the_box_parse_reads_are_offered_and_nothing_needs_typing(self):
        """From the install the form is one press: the two dropdowns are
        required but preselected (Auto, and merge for me, since a checkbox
        has no default), nothing needs typing, and sharing is on unless the
        person ticks the box."""
        for option in (*adopt.KINDS, *adopt.MERGES):
            self.assertIn(f'        - "{option}"\n', self.text)
        for option in adopt.OPTIONS:
            self.assertIn(f"        - label: {option}\n", self.text)
        self.assertEqual(adopt.KINDS[list(adopt.KINDS)[0]], "read")
        self.assertEqual(adopt.MERGES[list(adopt.MERGES)[0]], "true")
        kind, merge, options = (self.text.index(f"    id: {name}\n") for name in ("kind", "merge", "options"))
        for block in (self.text[kind:merge], self.text[merge:options]):
            self.assertIn("      default: 0\n", block)
            self.assertIn("      required: true\n", block)
        self.assertEqual(self.text.count("required: true"), 2)
        self.assertLess(self.text.index("    id: installation_id\n"), self.text.index("    id: state\n"))
        run = (ROOT / ".github/workflows/adopt-run.yml").read_text(encoding="utf-8")
        self.assertIn('if [ "$mode" = read ]; then', run)
        self.assertIn("sweep.classify_tree", run)
        self.assertIn('echo "MODE=$mode" >> "$GITHUB_ENV"', run)
        self.assertIn("env.MODE == 'existing'", run)
        self.assertIn("env.MODE == 'new'", run)
        self.assertEqual(run.count("inputs.mode"), 1)
        self.assertIn("spec+=(--kind-read)", run)

    def test_the_repository_field_is_named_state(self):
        """GitHub returns the install link's state parameter in the Setup
        URL's query, and an issue form fills the field whose id matches a
        query parameter, so the repository the extension's button carries
        as state arrives filled in; the label stays Repository, which parse
        reads."""
        self.assertIn("    id: state\n    attributes:\n      label: Repository\n", self.text)
        self.assertNotIn("id: repository", self.text)
        self.assertIn("extension's button", self.text)

    def test_the_label_and_the_title(self):
        self.assertIn('labels: ["adopt"]\n', self.text)
        self.assertIn('title: "Adopt"\n', self.text)

    def test_the_form_is_short_and_says_what_matters(self):
        """The person is assumed to know what they are doing: a few
        sentences, which still say what is shared, where the switch is,
        that the issue is public and where the App is installed."""
        for words in ("never code, text or names", ".github/symphony-metrics", "This issue is public", "installations/new",
                      "Press Create", "the newest repository the installation reaches", "press Create again",
                      "is enough", "https://github.com/apps/symphonyboard/installations/new", "is optional",
                      "stays installed, acting only during an adoption run"):
            self.assertIn(words, self.text)
        self.assertNotIn("refused", self.text)
        prose = re.search(r"value: \|\n((?:        .*\n)+)", self.text).group(1)
        self.assertLess(len(prose.split()), 140)

    def test_the_form_and_the_readme_name_the_setup_app_and_its_one_use(self):
        """The Setup App is optional, the fallback where SymphonyBoard cannot
        have Administration (the owner, 2026-10-20), so the form says what
        it is for, where it is and that it stays installed afterwards,
        which the person may uninstall whenever they like (the owner,
        2026-10-19), and the README names the same App."""
        for text in (self.text, (ROOT / "README.md").read_text(encoding="utf-8")):
            self.assertIn(SETUP_APP_INSTALL, text)
            self.assertIn("Administration", text)
            self.assertIn("stays installed", text)
            self.assertNotIn("uninstalls itself", text)
            self.assertIn('"Only select repositories"', text)
        self.assertNotIn("Setup App", "\n".join(re.findall(r"^      label: (.+)$", self.text, re.MULTILINE)))

    def test_the_consent_names_every_setting_the_setup_app_applies(self):
        """Accepting the permissions of the App that applies the settings is
        the consent to them, so the README's first step names each one the
        pull request's text names, the box that lets GitHub Actions open
        pull requests among them, and so does the privacy statement."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        step = readme[readme.index("1. **Install SymphonyBoard**"):readme.index("2. **Press Create**")]
        for name in (*adopt.THE_SETTINGS, adopt.ACTIONS_SETTING):
            with self.subTest(setting=name):
                self.assertIn(name, step)
        privacy = " ".join((ROOT / "PRIVACY.md").read_text(encoding="utf-8").split())
        self.assertIn("applies up to eight settings", privacy)
        self.assertIn(f"ticks \"{adopt.ACTIONS_LABEL}\"", privacy)

    def test_blank_issues_are_off(self):
        config = (ROOT / ".github/ISSUE_TEMPLATE/config.yml").read_text(encoding="utf-8")
        self.assertIn("blank_issues_enabled: false\n", config)


class ThePrivacyStatement(unittest.TestCase):
    def test_its_version_is_the_newest_change_it_names(self):
        """The site renders PRIVACY.md at the address the Apps' descriptions
        link, and each version says under Changes what it changed, the
        newest first: the version the statement opens with is that newest
        one, so a change noted there raises the number with it."""
        privacy = (ROOT / "PRIVACY.md").read_text(encoding="utf-8")
        opened = re.match(r"# .+\n\nVersion (\d+), \d{4}-\d{2}-\d{2}\. This text is also at ", privacy)
        self.assertTrue(opened)
        changes = privacy[privacy.index("\n## Changes\n"):]
        noted = [int(number) for number in re.findall(r"^Version (\d+) (?:says|adds|removes)\b", changes, re.MULTILINE)]
        self.assertEqual(noted, list(range(int(opened.group(1)), 1, -1)))


class TheWorkflows(unittest.TestCase):
    def test_no_expression_inside_a_run_step(self):
        for workflow in WORKFLOWS:
            for line, script in run_blocks(workflow.read_text(encoding="utf-8")):
                with self.subTest(workflow=workflow.name, line=line):
                    self.assertNotIn("${{", script)

    def test_the_scan_sees_run_blocks(self):
        sample = "steps:\n  - run: |\n      echo ${{ github.token }}\n  - name: x\n    run: echo ok\n"
        self.assertEqual([script.strip() for _, script in run_blocks(sample)], ["echo ${{ github.token }}", "echo ok"])

    def test_only_allowed_actions_on_major_tags(self):
        for workflow in WORKFLOWS:
            for used in re.findall(r"uses:\s*(\S+)", workflow.read_text(encoding="utf-8")):
                with self.subTest(workflow=workflow.name, action=used):
                    self.assertRegex(used, ALLOWED_ACTIONS)
                    self.assertTrue(ALLOWED_ACTIONS.fullmatch(used))

    def test_adopt_runs_on_opened_issues_with_the_label(self):
        text = (ROOT / ".github/workflows/adopt.yml").read_text(encoding="utf-8")
        self.assertIn("  issues:\n    types: [opened, reopened]\n", text)
        self.assertIn("if: contains(github.event.issue.labels.*.name, 'adopt')", text)
        self.assertIn("permissions:\n  issues: write\n  contents: read\n", text)
        self.assertIn("group: adopt-${{ github.event.issue.number }}", text)

    def test_the_issue_path_checks_and_then_calls_the_shared_run(self):
        """The adoption itself is one workflow for both paths; the issue
        path hands it the name the form made public, or the ids of a form
        that came from the install, the author and the issue, and only
        after its own checks passed."""
        text = (ROOT / ".github/workflows/adopt.yml").read_text(encoding="utf-8")
        self.assertIn("uses: ./.github/workflows/adopt-run.yml", text)
        self.assertIn("if: needs.request.result == 'success' && needs.request.outputs.refused != 'true'", text)
        self.assertIn("requester: ${{ github.event.issue.user.login }}", text)
        self.assertEqual(text.count("requester_id: ${{ github.event.issue.user.id }}"), 2)
        self.assertIn("issue: ${{ github.event.issue.number }}", text)
        self.assertIn("installation_id: ${{ needs.request.outputs.installation_id }}", text)
        self.assertIn("repository_id: ${{ matrix.repository_id }}", text)
        self.assertIn("secrets: inherit", text)
        for word in ("target-token", "template-token", "gh pr create"):
            self.assertNotIn(word, text)

    def test_a_form_from_the_install_is_resolved_silently_and_answered_without_a_name(self):
        """The install fills in the installation's number and no name: the
        issue path hands it to resolve.py, which asks the API by id for
        every repository to adopt, gives every failure one answer at one
        moment, and passes ids on, one run per repository and one answer
        for them all; the run names the repository in its answers only
        when the form named it."""
        text = (ROOT / ".github/workflows/adopt.yml").read_text(encoding="utf-8")
        resolve = text.index("name: Resolve the installation to the repositories to adopt")
        self.assertIn("if: env.REFUSED != 'true' && steps.form.outputs.repository == ''", text[resolve:])
        self.assertIn("bash start/scripts/jwt.sh", text)
        self.assertIn("python3 start/scripts/resolve.py", text)
        self.assertIn('--installation "$INSTALLATION" --author "$AUTHOR" --out "$RUNNER_TEMP/resolved"', text)
        self.assertEqual(text.count("refuse_alike"), 2)
        self.assertIn("deadline=$((SECONDS + 25))", text)
        self.assertIn('0) cat "$RUNNER_TEMP/resolved" >> "$GITHUB_OUTPUT" ;;', text)
        # The request job never learns a name, so it registers no mask of
        # one and nothing it prints can differ between refusals.
        resolve_step = text[resolve:text.index("      - uses: actions/create-github-app-token@v1", resolve)]
        self.assertNotIn("full_name", resolve_step)
        self.assertEqual(resolve_step.count("::add-mask::"), 2)
        for step in ("id: account-token", "id: app-probe", "name: Check that the App reaches the repository"):
            start = text.index(step)
            self.assertIn("steps.form.outputs.repository != ''", text[start:start + 400])
        # One run per repository, side by side, and one answer.
        self.assertIn("repository_id: ${{ fromJson(needs.request.outputs.repository_ids || '[]') }}", text)
        self.assertIn("fail-fast: false", text)
        self.assertIn('answer: caller', text)
        self.assertIn("merge: ${{ needs.request.outputs.merge }}", text)
        self.assertIn("needs: [request, adopt_each]", text)
        self.assertIn("RESULT: ${{ needs.adopt_each.result }}", text)
        self.assertNotIn("github.event.issue.body", text[text.index("  answer:"):])
        run = (ROOT / ".github/workflows/adopt-run.yml").read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", run)
        call = run.split("\npermissions:\n")[0]
        for name in ("installation_id", "repository_id", "merge", "answer"):
            self.assertIn(f"      {name}:\n", call)
        self.assertIn("group: adopt-run-${{ inputs.issue }}-${{ inputs.repository_id || inputs.repository }}", run)
        self.assertIn('run: |\n          echo "KIND_READ=false" >> "$GITHUB_ENV"', run)
        self.assertIn('echo "NAMED=$named" >> "$GITHUB_ENV"', run)
        self.assertIn('if [ "$NAMED" = masked ]; then\n            echo "::add-mask::$branch"', run)
        self.assertIn('[ -n "$REQUESTER_GIVEN" ] && echo "::add-mask::$REQUESTER_GIVEN"', run)
        self.assertNotIn("AUTHOR: ${{ env.REQUESTER }}", run)
        self.assertIn('git/trees/$encoded?recursive=1', run)
        self.assertIn('echo "SAID=your repository" >> "$GITHUB_ENV"', run)
        self.assertIn('echo "SAID=$target" >> "$GITHUB_ENV"', run)
        self.assertNotIn('refuse.sh "Nothing was done: $TARGET', run)
        self.assertNotIn('"$refuse" "Nothing was done: $TARGET', run)
        self.assertIn("if: env.REFUSED != 'true' && inputs.answer != 'caller'", run)
        self.assertIn("if: failure() && env.REFUSED != 'true' && inputs.answer != 'caller'", run)

    def test_the_run_merges_when_asked_and_the_setup_app_stays_installed(self):
        """Merge for me: the run merges, or arms auto-merge where a ruleset
        requires the check, and says which; the Setup App stays installed,
        after an adoption and after a request refused because the
        repository is adopted already, acting only during an adoption run,
        and its token is still revoked after the settings."""
        run = (ROOT / ".github/workflows/adopt-run.yml").read_text(encoding="utf-8")
        merge = run.index("name: Merge the pull request when asked")
        self.assertIn("if: env.REFUSED != 'true' && inputs.merge == 'true'", run[merge:])
        self.assertIn('gh pr merge "$number" --repo "$TARGET" --merge --delete-branch', run)
        self.assertIn('gh pr merge "$number" --repo "$TARGET" --auto --merge --delete-branch', run)
        self.assertLess(run.index("name: Open the setup issue in a new repository"), merge)
        self.assertLess(merge, run.index("name: Answer the request and close it"))
        self.assertIn('merged) merged=" It is merged, as you asked." ;;', run)
        self.assertLess(run.index("name: Revoke the Setup App's token"), run.index("name: Write the pull request's text"))
        for words in ("Uninstall the Setup App", "/app/installations/$id", "SETUP_UNINSTALLED", '"uninstalled"'):
            self.assertNotIn(words, run)
        self.assertIn("the App stays installed, acting only during an adoption run, and you can uninstall it at"
                      " any time.", run)
        # The answer names the App that applied the settings.
        answer = run[run.index("name: Answer the request and close it"):]
        self.assertIn('if [ "${SETTINGS_BY:-}" = board ]; then', answer)
        self.assertIn("says what the Symphony App could do", answer)

    def test_the_symphony_app_asks_for_administration_first_and_the_setup_app_after(self):
        """SymphonyBoard first, the Setup App the fallback (the owner's rule
        of 2026-10-20): two mints ask for Administration, each for the one
        repository and each allowed to fail, the main App's first and the
        Setup App's only where it made none."""
        text = (ROOT / ".github/workflows/adopt-run.yml").read_text(encoding="utf-8")
        steps = re.split(r"\n      - (?=uses:|name:)", text)
        asking = [step for step in steps if "permission-administration" in step]
        self.assertEqual(len(asking), 2)
        board, fallback = asking
        self.assertIn("id: board-settings-token", board)
        self.assertIn("app-id: ${{ vars.SDLC_APP_ID }}", board)
        self.assertIn("id: setup-token", fallback)
        self.assertIn("steps.board-settings-token.outcome != 'success'", fallback)
        self.assertIn("app-id: ${{ vars.SDLC_SETUP_APP_ID }}", fallback)
        self.assertIn("private-key: ${{ secrets.SDLC_SETUP_APP_PRIVATE_KEY }}", fallback)
        for step in asking:
            self.assertIn("repositories: ${{ env.NAME }}", step)
            self.assertIn("permission-administration: write", step)
            self.assertIn("continue-on-error: true", step)
            self.assertNotIn("permission-contents", step)
        self.assertLess(text.index("id: board-settings-token"), text.index("id: setup-token"))
        # The key is minted for Administration once, for the organization's
        # Administration once, probed once, read as set-or-not once, and
        # signs the JWTs that mint the organization's Secrets and Variables
        # token and the repository's Pages and Variables token, once each;
        # the App no longer uninstalls itself.
        self.assertEqual(text.count("secrets.SDLC_SETUP_APP_PRIVATE_KEY"), 6)
        pages, = [step for step in steps if "id: pages-token" in step]
        self.assertIn("BOARD_ID: ${{ vars.SDLC_APP_ID }}", pages)
        self.assertIn("SETUP_ID: ${{ vars.SDLC_SETUP_APP_ID }}", pages)
        self.assertIn("for app in BOARD SETUP; do", pages)
        self.assertIn("continue-on-error: true", pages)
        self.assertIn("env.SETTINGS_BY != ''", pages)
        self.assertIn("env.MODE == 'new'", pages)
        self.assertIn('"repositories": [os.environ["NAME"]]', pages)
        self.assertIn('"permissions": {"pages": "write", "actions_variables": "write", "administration": "write",'
                      ' "metadata": "read"}', pages)
        self.assertIn('"https://api.github.com/repos/$OWNER/$NAME/installation"', pages)
        self.assertNotIn("echo \"the token", pages)
        lend, = [step for step in steps if "id: lend-token" in step]
        self.assertIn("BOARD_ID: ${{ vars.SDLC_APP_ID }}", lend)
        self.assertIn("for app in BOARD SETUP; do", lend)
        self.assertIn("continue-on-error: true", lend)
        self.assertIn("env.SETTINGS_BY != ''", lend)
        self.assertIn("steps.target.outputs.owner_type == 'Organization'", lend)
        self.assertIn('"permissions": {"organization_secrets": "write", "organization_actions_variables": "write",'
                      ' "metadata": "read"}', lend)
        # It prints nothing: the settings step's one line is the lending's.
        self.assertNotIn("echo \"the token", lend)
        self.assertIn('"repositories": [os.environ["NAME"]]', lend)
        self.assertNotIn("administration", lend)
        # Its answers stay out of the log: every curl and Python read is
        # silenced, and the step says one fixed line either way.
        for line in lend.splitlines():
            if "curl " in line or "python3 -c 'import json, sys" in line:
                self.assertTrue("2>/dev/null" in line or line.rstrip().endswith("\\"), line)
        self.assertIn('echo "::add-mask::$token"', lend)
        # The token goes to a file, never a step output, whose presence in
        # a later step's env would tell this log whether it was made.
        written = """(umask 077; printf '%s' "$token" > "$RUNNER_TEMP/lend-token")"""
        self.assertLess(lend.index('echo "::add-mask::$token"'), lend.index(written))
        self.assertNotIn("GITHUB_OUTPUT", lend)
        self.assertNotIn("steps.lend-token.outputs", text)
        revoke, = [step for step in steps if "name: Revoke the token that lends" in step]
        self.assertIn("if: always() && steps.lend-token.outcome != 'skipped'", revoke)
        self.assertNotIn("echo", revoke)
        self.assertIn("name: Revoke the token that lends the requester's Claude tokens", text)
        # The requester's account id reaches the shell only through env:,
        # digits or nothing, and setup.py lends only by login and id.
        self.assertIn("REQUESTER_ID_GIVEN: ${{ inputs.requester_id }}", text)
        self.assertIn('--requester-id="$REQUESTER_ID"', text)
        for line in text.splitlines():
            if "inputs.requester_id" in line:
                self.assertTrue(line.strip().startswith("REQUESTER_ID_GIVEN:") or "group:" in line, line)
        org, = [step for step in steps if "id: setup-org-token" in step]
        self.assertIn("app-id: ${{ vars.SDLC_SETUP_APP_ID }}", org)
        self.assertIn("repositories: ${{ env.NAME }}", org)
        self.assertIn("permission-organization-administration: write", org)
        self.assertIn("continue-on-error: true", org)
        self.assertIn("env.SETTINGS_BY != ''", org)
        self.assertIn("env.MODE == 'new'", org)
        self.assertIn("steps.target.outputs.owner_type == 'Organization'", org)
        for word in ("permission-contents", "permission-administration:", "permission-metadata"):
            self.assertNotIn(word, org)
        self.assertIn("secrets.SDLC_SETUP_APP_PRIVATE_KEY != ''", text)
        probe, = [step for step in steps if "id: setup-probe" in step]
        self.assertIn("owner: OpenSpineConsortium\n          repositories: symphony-start\n", probe)
        self.assertIn("permission-metadata: read", probe)
        self.assertNotIn("administration", probe)
        self.assertIn("steps.setup-token.outcome == 'failure'", probe)
        # The main App's tokens carry Administration in three mints alone,
        # each for the settings of this one repository: its settings token,
        # and the Pages and lending tokens it makes before the Setup App's.
        main_mints = [step for step in steps if "vars.SDLC_APP_ID" in step]
        self.assertTrue(main_mints)
        settings_mints = ("id: board-settings-token", "id: pages-token", "id: lend-token")
        for step in main_mints:
            if not any(mint in step for mint in settings_mints):
                self.assertNotIn("administration", step)
        # The issue path holds the Setup App's key only to sign the JWT
        # that tells its installation's number from the App's and asks
        # which candidates it reaches: it mints no token of the Setup App,
        # and none with Administration.
        issue_path = (ROOT / ".github/workflows/adopt.yml").read_text(encoding="utf-8")
        self.assertNotIn("administration", issue_path)
        self.assertEqual(issue_path.count("secrets.SDLC_SETUP_APP_PRIVATE_KEY"), 1)
        self.assertIn('setup_jwt="$(APP_ID="$SETUP_ID" APP_PRIVATE_KEY="$SETUP_KEY" bash start/scripts/jwt.sh)"', issue_path)
        for step in re.split(r"\n      - (?=uses:|name:)", issue_path):
            if "create-github-app-token" in step:
                self.assertNotIn("vars.SDLC_SETUP_APP_ID", step)

    def test_a_named_repository_needs_only_symphonyboard(self):
        """SymphonyBoard alone is enough (the owner's rule of 2026-10-20):
        the issue path asks nothing of Symphony Setup on a named repository
        and refuses no request for its absence, and the installation
        path's one refusal sends nobody to install it; the run reports a
        broken Setup App of the front door's by itself, so nothing here
        probes it. There is no third path, since the sweep is gone."""
        text = (ROOT / ".github/workflows/adopt.yml").read_text(encoding="utf-8")
        for words in ("name: Say whether this front door has the Setup App", "id: setup-token", "id: setup-probe",
                      "id: contents-token", "name: Check that the Setup App is installed on the repository",
                      "env.SETUP_APP", "Symphony Setup is not installed", "this front door's Setup App is not working"):
            self.assertNotIn(words, text)
        resolve = text.index("name: Resolve the installation to the repositories to adopt")
        refusal = text[text.index('refusal="', resolve):]
        refusal = refusal[:refusal.index("\n")]
        self.assertNotIn(SETUP_APP_INSTALL, refusal)
        self.assertNotIn("Symphony Setup", refusal)
        self.assertIn("https://github.com/apps/symphonyboard/installations/new", refusal)
        self.assertFalse((ROOT / ".github/workflows/sweep.yml").exists())
        # The run's own probe, which runs when neither App's token could be
        # made, tells a broken front-door Setup App from a missing one.
        run = (ROOT / ".github/workflows/adopt-run.yml").read_text(encoding="utf-8")
        steps = re.split(r"\n      - (?=uses:|name:)", run)
        probe, = [step for step in steps if "id: setup-probe" in step]
        self.assertIn("env.SETTINGS_BY == '' && steps.setup-token.outcome == 'failure'", probe)
        self.assertIn("why=front-door-broken", run)

    def test_the_settings_are_applied_after_the_push_and_before_the_pull_request(self):
        text = (ROOT / ".github/workflows/adopt-run.yml").read_text(encoding="utf-8")
        pushed = text.index("name: Commit on symphony/adopt and push it as the App")
        applied = text.index("name: Apply the repository's settings where the Setup App is installed")
        revoked = text.index("name: Revoke the Setup App's token")
        written = text.index("name: Write the pull request's text")
        opened = text.index("name: Open the pull request")
        self.assertLess(pushed, applied)
        self.assertLess(applied, revoked)
        self.assertLess(revoked, written)
        self.assertLess(written, opened)
        for why in ("not-granted", "not-installed", "front-door-broken"):
            self.assertIn(f"why={why}", text)
        self.assertIn("setup.py skip --why not-reported", text)
        self.assertIn("--ruleset template/docs/setup/ruleset-main.json", text)
        self.assertIn('--settings "$RUNNER_TEMP/settings.json"', text)
        self.assertIn('title="Setup App of this front door is not working"', text)
        self.assertIn("gh issue create", text)


if __name__ == "__main__":
    unittest.main()
