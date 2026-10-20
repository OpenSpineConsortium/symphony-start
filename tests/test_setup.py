"""scripts/setup.py applies the template's settings as the Setup App and
reports each one.

The report is what the pull request renders, so it carries GitHub's words;
the log is public, so it carries none. Each setting stands on its own: one
GitHub refuses costs itself and nothing else. Mode existing drops the rule
that requires the check, which a repository the template did not make has
no job for, and a ruleset of the template's name that the repository has
already is left as it is. The topic symphony joins the topics the
repository has and never replaces them. In mode new the box that lets
GitHub Actions create and approve pull requests is ticked with the
token's permissions sent back as they were, and a 409, the policy of
the organization or its enterprise, is kept apart from other refusals;
mode existing leaves the box alone. In mode new the ruleset this run
created has its check pinned to GitHub Actions once GitHub Actions has
reported it on the pushed head, read with the main App's Checks token and
written with the Setup App's, within a bound the tests pass on a clock of
their own; nothing else is pinned, and nothing stops the run.
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS.parent / "scripts"))

import adopt  # noqa: E402
import setup  # noqa: E402

REPO = "octo-org/widget"
# The shape of the template's docs/setup/ruleset-main.json, with the rule
# mode existing drops and two it keeps.
RULESET = {
    "name": "Protect the default branch",
    "target": "branch",
    "enforcement": "active",
    "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
    "rules": [
        {"type": "deletion"},
        {"type": "pull_request", "parameters": {"required_approving_review_count": 0}},
        {"type": "required_status_checks",
         "parameters": {"strict_required_status_checks_policy": True,
                        "required_status_checks": [{"context": "check"}]}},
    ],
    "bypass_actors": [],
}
TOGGLES = {"delete_branch_on_merge": True, "allow_auto_merge": True}
SCANNING = {"security_and_analysis": {"secret_scanning": {"status": "enabled"}}}
PUSH_PROTECTION = {"security_and_analysis": {"secret_scanning_push_protection": {"status": "enabled"}}}
TOPICS = f"/repos/{REPO}/topics"
# The topics the repository has before the run, which the PUT carries back.
THEIR_TOPICS = ["tools"]
WORKFLOW = f"/repos/{REPO}/actions/permissions/workflow"
# GitHub's default for a repository: the token reads, and GitHub Actions
# may not create or approve pull requests; the PUT ticks the box alone.
THEIR_WORKFLOW = {"default_workflow_permissions": "read", "can_approve_pull_request_reviews": False}
ORG_WORKFLOW = "/orgs/octo-org/actions/permissions/workflow"
ORG_TOKEN = "ghs_org_token_for_tests"
ACTIONS_ON = {"default_workflow_permissions": "read", "can_approve_pull_request_reviews": True}
ACTIONS_LOG = "settings: allow GitHub Actions to create and approve pull requests: "
NOT_TRIED_IN_EXISTING = "the protocol alone opens no pull request with GitHub Actions"
REFUSED = (422, {"message": "Secret scanning is not available for this repository.",
                 "errors": [{"message": "Upgrade the plan."}]})
# The check's pin: the main App's token that reads the check runs, the head
# the run pushed, the repository's own ruleset as GitHub lists and gives it
# back, and the body the PUT sends, the check now from GitHub Actions.
CHECKS_TOKEN = "ghs_checks_token_for_tests"
HEAD = "a" * 40
CHECK_RUNS = f"/repos/{REPO}/commits/{HEAD}/check-runs?check_name=check&per_page=100"
ACTIONS_RUN = {"name": "check", "status": "queued", "app": {"id": 15368, "slug": "github-actions"}}
OWN_RULESETS = f"/repos/{REPO}/rulesets?includes_parents=false&per_page=100"
RULESET_ID = 7
RULESET_PATH = f"/repos/{REPO}/rulesets/{RULESET_ID}"
LISTED = {"id": RULESET_ID, "name": RULESET["name"], "source_type": "Repository", "source": REPO}
GIVEN_BACK = dict(json.loads(json.dumps(RULESET)), id=RULESET_ID, source_type="Repository", source=REPO,
                  node_id="RRS_x", created_at="2026-10-19T00:00:00Z", _links={"self": {"href": "x"}})
PINNED = json.loads(json.dumps(RULESET))
PINNED["rules"][2]["parameters"]["required_status_checks"] = [{"context": "check", "integration_id": 15368}]
PIN_LOG = "settings: the check's source: "
# The Token workflow's environment, limited to the default branch.
ENVIRONMENT = f"/repos/{REPO}/environments/token-store"
# Administration reads this; the environment's own read needs Actions.
ENVIRONMENT_PROBE = ENVIRONMENT + "/deployment_protection_rules/apps"
ENVIRONMENT_BODY = {"deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}}
STORE_LOG = "settings: environment token-store: "
# GitHub Pages for the documentation site; the default answer is a site
# there already, which the run leaves as it is, so the class Pages tests
# the site's making on its own.
PAGES = f"/repos/{REPO}/pages"
PAGES_LOG = "settings: GitHub Pages: "
# The token lending's one line of two, the same for every requester.
LENT_LOG = "token lending: tokens lent"
NOT_LENT_LOG = "token lending: no tokens lent"


class FakeClock:
    """The pin's clock: sleeping moves it on at once, and it keeps every
    pause, so a test of ten minutes' waiting runs in no time."""

    def __init__(self):
        self.now = 0.0
        self.pauses = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.pauses.append(seconds)
        self.now += seconds

    def waiting(self):
        return setup.Waiting(clock=self.clock, sleep=self.sleep, bound=600, interval=15)


class FakeGitHub:
    """A transport that answers from a table keyed (method, path) and keeps
    every call; the default answers are a public repository with no
    ruleset and GitHub's default workflow permissions that accepts every
    write, on whose head GitHub Actions has queued the check, and whose
    ruleset, once created, is listed and given back as GitHub would. An
    answer of None is a body of nothing, as a 204 has."""

    def __init__(self, answers=None, raising=None):
        self.answers = answers or {}
        self.raising = raising
        self.calls = []

    def __call__(self, method, url, headers, body):
        path = url.removeprefix(setup.API)
        self.calls.append((method, path, headers, body))
        if self.raising:
            raise setup.GitHubError(self.raising)
        if (method, path) in self.answers:
            # A list is a sequence of answers to the same call, the last
            # one standing for every later call.
            answers = self.answers[(method, path)]
            status, answer = answers.pop(0) if isinstance(answers, list) and len(answers) > 1 else (
                answers[0] if isinstance(answers, list) else answers)
        elif (method, path) == ("GET", f"/repos/{REPO}"):
            status, answer = 200, {"private": False, "default_branch": "main"}
        elif (method, path) == ("GET", ENVIRONMENT_PROBE):
            status, answer = 404, {"message": "Not Found"}
        elif (method, path) == ("GET", PAGES):
            status, answer = 200, {"build_type": "legacy"}
        elif (method, path) == ("GET", f"/repos/{REPO}/rulesets?includes_parents=false"):
            status, answer = 200, []
        elif (method, path) == ("GET", TOPICS):
            status, answer = 200, {"names": list(THEIR_TOPICS)}
        elif (method, path) == ("GET", WORKFLOW):
            status, answer = 200, dict(THEIR_WORKFLOW)
        elif (method, path) == ("PUT", WORKFLOW):
            status, answer = 204, None
        elif (method, path) == ("GET", CHECK_RUNS):
            status, answer = 200, {"total_count": 1, "check_runs": [ACTIONS_RUN]}
        elif (method, path) == ("GET", OWN_RULESETS):
            status, answer = 200, [LISTED]
        elif (method, path) == ("GET", RULESET_PATH):
            status, answer = 200, json.loads(json.dumps(GIVEN_BACK))
        elif method == "POST":
            status, answer = 201, {"id": 1}
        else:
            status, answer = 200, {}
        return status, b"" if answer is None else json.dumps(answer).encode("utf-8")

    def writes(self):
        return [(method, path, body) for method, path, _, body in self.calls if method in ("POST", "PATCH", "PUT")]


class Apply(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.ruleset = self.root / "ruleset-main.json"
        self.ruleset.write_text(json.dumps(RULESET, indent=2) + "\n", encoding="utf-8")
        self.report = self.root / "settings.json"
        # The run's own environment in mode new: the tokens are there.
        patcher = mock.patch.dict(os.environ, {"GH_TOKEN": "ghs_token_for_tests", "GH_CHECKS_TOKEN": CHECKS_TOKEN,
                                               "GH_PAGES_TOKEN": "ghs_pages_token_for_tests"})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.clock = FakeClock()
        patcher = mock.patch.object(setup, "WAITING", self.clock.waiting())
        patcher.start()
        self.addCleanup(patcher.stop)

    def apply(self, github, mode="new", ruleset=None, org_token=None, head=HEAD):
        """Run apply; (exit code, the report or None, stdout, stderr)."""
        if org_token:
            patcher = mock.patch.dict(os.environ, {"GH_ORG_TOKEN": org_token})
            patcher.start()
            self.addCleanup(patcher.stop)
        out, err = io.StringIO(), io.StringIO()
        argv = ["apply", "--repo", REPO, "--mode", mode, "--ruleset", str(ruleset or self.ruleset),
                "--report", str(self.report)] + (["--head", head] if head is not None else [])
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = setup.main(argv, transport=github)
        report = json.loads(self.report.read_text(encoding="utf-8")) if self.report.exists() else None
        return code, report, out.getvalue(), err.getvalue()

    def states(self, report):
        """Each setting's state but the token lending's, which these tests
        leave untried, as a run for a personal account's repository does,
        and the class Lending tests on its own, and the token store's and
        the Pages site's, which the classes TokenStore and Pages test on
        their own."""
        return {key: setting["state"] for key, setting in report["settings"].items()
                if key not in ("token_lending", "token_store", "pages")}

    def test_new_mode_applies_every_setting_in_order(self):
        github = FakeGitHub()
        code, report, out, err = self.apply(github)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(github.writes(), [
            ("POST", f"/repos/{REPO}/rulesets", RULESET),
            ("PATCH", f"/repos/{REPO}", TOGGLES),
            ("PUT", TOPICS, {"names": ["tools", "symphony"]}),
            ("PATCH", f"/repos/{REPO}", SCANNING),
            ("PATCH", f"/repos/{REPO}", PUSH_PROTECTION),
            ("PUT", WORKFLOW, ACTIONS_ON),
            ("PUT", ENVIRONMENT, ENVIRONMENT_BODY),
            ("POST", ENVIRONMENT + "/deployment-branch-policies", {"name": "main", "type": "branch"}),
            ("PUT", RULESET_PATH, PINNED),
        ])
        self.assertEqual(report["schema"], setup.REPORT_SCHEMA)
        self.assertEqual((report["outcome"], report["mode"], report["private"]), ("applied", "new", False))
        self.assertEqual((report["ruleset_name"], report["required_check"]), ("Protect the default branch", True))
        self.assertEqual(self.states(report), {
            "ruleset": "done", "toggles": "done", "topic": "done", "secret_scanning": "done", "push_protection": "done",
            "actions_pull_requests": "done", "check_source": "done",
        })
        self.assertEqual(list(report["settings"]), list(setup.SETTINGS))
        self.assertEqual(out.splitlines(), [
            "settings: ruleset: created",
            "settings: delete head branches on merge, allow auto-merge: on",
            "settings: topic symphony: on",
            "settings: secret scanning: on",
            "settings: push protection: on",
            ACTIONS_LOG + "on",
            NOT_LENT_LOG,
            STORE_LOG + "made, default branch only",
            PAGES_LOG + "a site is there, left as it is",
            PIN_LOG + "GitHub Actions",
        ])

    def test_every_call_carries_the_token_and_the_api_version(self):
        """The Setup App's token for everything but the check runs, which
        only the main App's Checks token reads, and the Pages site, which
        its own token with Pages and Variables makes."""
        github = FakeGitHub()
        self.apply(github)
        for method, path, headers, body in github.calls:
            with self.subTest(call=(method, path)):
                token = (CHECKS_TOKEN if path == CHECK_RUNS else "ghs_pages_token_for_tests" if path == PAGES
                         else "ghs_token_for_tests")
                self.assertEqual(headers["Authorization"], f"Bearer {token}")
                self.assertEqual(headers["X-GitHub-Api-Version"], setup.API_VERSION)
                self.assertEqual(headers["Accept"], "application/vnd.github+json")
                self.assertEqual("Content-Type" in headers, body is not None)

    def test_existing_mode_drops_the_rule_that_requires_the_check(self):
        github = FakeGitHub()
        code, report, _, _ = self.apply(github, mode="existing")
        self.assertEqual(code, 0)
        posted = github.writes()[0][2]
        self.assertEqual([rule["type"] for rule in posted["rules"]], ["deletion", "pull_request"])
        self.assertEqual(posted["name"], RULESET["name"])
        self.assertFalse(report["required_check"])
        self.assertEqual(report["mode"], "existing")
        self.assertEqual(json.loads(self.ruleset.read_text())["rules"], RULESET["rules"])

    def test_a_ruleset_of_that_name_is_left_as_it_is(self):
        listed = {("GET", f"/repos/{REPO}/rulesets?includes_parents=false"): (200, [{"name": RULESET["name"]}])}
        github = FakeGitHub(listed)
        code, report, out, _ = self.apply(github)
        self.assertEqual(code, 0)
        self.assertNotIn(("POST", f"/repos/{REPO}/rulesets"), [(method, path) for method, path, _ in github.writes()])
        self.assertEqual(self.states(report)["ruleset"], "exists")
        self.assertIn("settings: ruleset: exists, left as it is", out)

    def test_an_organizations_ruleset_of_that_name_is_not_this_repositorys(self):
        """The list is asked without parents: a ruleset the organization set
        is not the repository's own, so the repository gets one."""
        github = FakeGitHub()
        self.apply(github)
        self.assertIn(("GET", f"/repos/{REPO}/rulesets?includes_parents=false"),
                      [(method, path) for method, path, _, _ in github.calls])
        self.assertEqual(github.writes()[0][0], "POST")

    def test_a_private_repository_is_noted_and_an_internal_one_is_not(self):
        """The note about GitHub Free is for a private repository; an
        internal one, which GitHub flags private too, is an enterprise's."""
        github = FakeGitHub({("GET", f"/repos/{REPO}"): (200, {"private": True, "visibility": "private"})})
        _, report, _, _ = self.apply(github)
        self.assertTrue(report["private"])
        github = FakeGitHub({("GET", f"/repos/{REPO}"): (200, {"private": True, "visibility": "internal"})})
        _, report, _, _ = self.apply(github)
        self.assertFalse(report["private"])

    def test_a_redirect_is_a_refusal_not_a_setting_done(self):
        """urllib would repeat a redirected POST as a GET of the new place
        and report its 200; the transport hands every 3xx back as it is,
        and a 3xx is not done."""
        class Github(FakeGitHub):
            def __call__(self, method, url, headers, body):
                if method in ("POST", "PATCH", "PUT"):
                    self.calls.append((method, url.removeprefix(setup.API), headers, body))
                    return 307, b'{"message": "Temporary Redirect"}'
                return super().__call__(method, url, headers, body)

        _, report, out, _ = self.apply(Github())
        self.assertEqual(self.states(report), {
            "ruleset": "failed", "toggles": "failed", "topic": "failed", "secret_scanning": "failed",
            "push_protection": "not-tried", "actions_pull_requests": "failed", "check_source": "not-tried",
        })
        self.assertEqual(report["settings"]["toggles"]["detail"], "HTTP 307: Temporary Redirect")
        self.assertEqual(report["settings"]["actions_pull_requests"]["detail"], "HTTP 307: Temporary Redirect")
        self.assertNotIn("on", out.splitlines()[1].split(": ")[-1])
        self.assertIsNone(setup.NoRedirect().redirect_request(None, None, 301, "", {}, "https://elsewhere.example"))
        self.assertTrue(any(isinstance(handler, setup.NoRedirect) for handler in setup.OPENER.handlers))

    def test_an_answer_that_is_not_json_is_a_refusal_with_the_report_still_written(self):
        class Github(FakeGitHub):
            def __call__(self, method, url, headers, body):
                if method == "POST":
                    self.calls.append((method, url.removeprefix(setup.API), headers, body))
                    return 201, b"<html>created, says a proxy</html>"
                return super().__call__(method, url, headers, body)

        code, report, _, err = self.apply(Github())
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(report["settings"]["ruleset"]["detail"], "HTTP 201: GitHub's answer was not JSON")
        self.assertEqual(self.states(report)["toggles"], "done")

    def test_a_validation_error_without_a_message_keeps_its_field_and_code(self):
        class Github(FakeGitHub):
            def __call__(self, method, url, headers, body):
                if method == "POST":
                    self.calls.append((method, url.removeprefix(setup.API), headers, body))
                    return 422, json.dumps({"message": "Validation Failed", "errors": [
                        {"resource": "Ruleset", "field": "name", "code": "already_exists"}]}).encode("utf-8")
                return super().__call__(method, url, headers, body)

        _, report, _, _ = self.apply(Github())
        self.assertEqual(report["settings"]["ruleset"]["detail"],
                         "HTTP 422: Validation Failed Ruleset name already_exists")

    def test_secret_scanning_refused_costs_itself_and_push_protection_only(self):
        class Github(FakeGitHub):
            def __call__(self, method, url, headers, body):
                if method == "PATCH" and body == SCANNING:
                    self.calls.append((method, url.removeprefix(setup.API), headers, body))
                    return REFUSED[0], json.dumps(REFUSED[1]).encode("utf-8")
                return super().__call__(method, url, headers, body)

        github = Github()
        code, report, out, _ = self.apply(github)
        self.assertEqual(code, 0)
        self.assertEqual(self.states(report), {
            "ruleset": "done", "toggles": "done", "topic": "done", "secret_scanning": "failed",
            "push_protection": "not-tried", "actions_pull_requests": "done", "check_source": "done",
        })
        self.assertEqual(report["settings"]["secret_scanning"]["detail"],
                         "HTTP 422: Secret scanning is not available for this repository. Upgrade the plan.")
        self.assertEqual(report["settings"]["push_protection"]["detail"], "secret scanning is not on")
        self.assertNotIn(PUSH_PROTECTION, [body for _, _, body in github.writes()])
        self.assertIn("settings: secret scanning: not turned on", out)
        self.assertIn("settings: push protection: not tried", out)
        self.assertNotIn("Upgrade", out)
        self.assertNotIn("422", out)

    def test_push_protection_refused_after_scanning(self):
        class Github(FakeGitHub):
            def __call__(self, method, url, headers, body):
                if method == "PATCH" and body == PUSH_PROTECTION:
                    self.calls.append((method, url.removeprefix(setup.API), headers, body))
                    return 422, b'{"message": "Push protection is not available."}'
                return super().__call__(method, url, headers, body)

        _, report, out, _ = self.apply(Github())
        self.assertEqual(self.states(report)["secret_scanning"], "done")
        self.assertEqual(self.states(report)["push_protection"], "failed")
        self.assertEqual(report["settings"]["push_protection"]["detail"], "HTTP 422: Push protection is not available.")
        self.assertIn("settings: push protection: not turned on", out)

    def test_the_topic_joins_the_ones_the_repository_has(self):
        """The PUT replaces the whole list, so the list is read first and
        theirs go back with the topic; a topic added carries no detail."""
        github = FakeGitHub()
        _, report, out, _ = self.apply(github)
        calls = [(method, path) for method, path, _, _ in github.calls]
        self.assertLess(calls.index(("GET", TOPICS)), calls.index(("PUT", TOPICS)))
        self.assertIn(("PUT", TOPICS, {"names": ["tools", "symphony"]}), github.writes())
        self.assertEqual(report["settings"]["topic"], {"state": "done", "detail": ""})
        self.assertIn("settings: topic symphony: on", out)

    def test_a_topic_there_already_is_recorded_and_not_written_again(self):
        github = FakeGitHub({("GET", TOPICS): (200, {"names": ["symphony", "tools"]})})
        _, report, out, _ = self.apply(github)
        self.assertNotIn(("PUT", TOPICS), [(method, path) for method, path, _ in github.writes()])
        self.assertEqual(report["settings"]["topic"], {"state": "done", "detail": "was there already"})
        self.assertIn("settings: topic symphony: on", out)

    def test_the_topic_refused_costs_itself_and_keeps_githubs_words(self):
        class Github(FakeGitHub):
            def __call__(self, method, url, headers, body):
                if method == "PUT" and url.endswith(TOPICS):
                    self.calls.append((method, url.removeprefix(setup.API), headers, body))
                    return 403, b'{"message": "Resource not accessible by integration"}'
                return super().__call__(method, url, headers, body)

        code, report, out, _ = self.apply(Github())
        self.assertEqual(code, 0)
        self.assertEqual(self.states(report), {
            "ruleset": "done", "toggles": "done", "topic": "failed", "secret_scanning": "done",
            "push_protection": "done", "actions_pull_requests": "done", "check_source": "done",
        })
        self.assertEqual(report["settings"]["topic"]["detail"], "HTTP 403: Resource not accessible by integration")
        self.assertIn("settings: topic symphony: not set", out)
        self.assertNotIn("integration", out)

    def test_topics_that_cannot_be_read_are_not_written(self):
        """Writing without the list would drop theirs, so a list that
        cannot be read, or an answer without one, is a refusal and no PUT."""
        for answer in ((403, {"message": "no"}), (200, {}), (200, {"names": "symphony"}), (200, [])):
            with self.subTest(answer=answer):
                github = FakeGitHub({("GET", TOPICS): answer})
                _, report, out, _ = self.apply(github)
                self.assertNotIn(("PUT", TOPICS), [(method, path) for method, path, _ in github.writes()])
                self.assertEqual(self.states(report)["topic"], "failed")
                self.assertIn("settings: topic symphony: not set", out)
        _, report, _, _ = self.apply(FakeGitHub({("GET", TOPICS): (200, {})}))
        self.assertEqual(report["settings"]["topic"]["detail"], "GitHub's answer listed no topics")

    def test_actions_may_open_pull_requests_with_the_tokens_permissions_as_they_were(self):
        """The PUT sets the default token's permissions too, so they go
        back as GitHub read them, read or write, and only the box changes;
        a box this run ticked carries no detail, and GitHub's 204 is done."""
        for permissions in ("read", "write"):
            with self.subTest(permissions=permissions):
                read = {"default_workflow_permissions": permissions, "can_approve_pull_request_reviews": False}
                github = FakeGitHub({("GET", WORKFLOW): (200, read)})
                code, report, out, err = self.apply(github)
                self.assertEqual((code, err), (0, ""))
                calls = [(method, path) for method, path, _, _ in github.calls]
                self.assertLess(calls.index(("GET", WORKFLOW)), calls.index(("PUT", WORKFLOW)))
                self.assertIn(("PUT", WORKFLOW, {"default_workflow_permissions": permissions,
                                                 "can_approve_pull_request_reviews": True}), github.writes())
                self.assertEqual(report["settings"]["actions_pull_requests"], {"state": "done", "detail": ""})
                self.assertIn(ACTIONS_LOG + "on", out.splitlines())

    def test_actions_on_already_is_recorded_and_not_written_again(self):
        """A box ticked already needs no write, and so no reading of the
        token's permissions either."""
        for answer in ({"default_workflow_permissions": "write", "can_approve_pull_request_reviews": True},
                       {"can_approve_pull_request_reviews": True}):
            with self.subTest(answer=answer):
                github = FakeGitHub({("GET", WORKFLOW): (200, answer)})
                _, report, out, _ = self.apply(github)
                self.assertNotIn(WORKFLOW, [path for _, path, _ in github.writes()])
                self.assertEqual(report["settings"]["actions_pull_requests"],
                                 {"state": "done", "detail": "was on already"})
                self.assertIn(ACTIONS_LOG + "on", out.splitlines())

    def test_only_true_reads_as_a_box_on_already(self):
        """GitHub's answer says the box with a boolean; one of another kind,
        such as the string "false", is not taken as on for being truthy,
        and the PUT ticks the box."""
        read = {"default_workflow_permissions": "read", "can_approve_pull_request_reviews": "false"}
        github = FakeGitHub({("GET", WORKFLOW): (200, read)})
        _, report, _, _ = self.apply(github)
        self.assertIn(("PUT", WORKFLOW, ACTIONS_ON), github.writes())
        self.assertEqual(report["settings"]["actions_pull_requests"], {"state": "done", "detail": ""})

    def test_actions_forbidden_by_the_owners_policy_is_kept_apart_and_out_of_the_log(self):
        """GitHub answers 409 where the organization, or its enterprise,
        holds the box: the report says forbidden, in GitHub's words, so the
        pull request can say who allows it; the public log says only that
        the box is not on, as for any refusal, and every other setting
        stands."""
        for answer, said in (((409, {"message": "Conflict"}), "HTTP 409: Conflict"), ((409, None), "HTTP 409")):
            with self.subTest(answer=answer):
                code, report, out, err = self.apply(FakeGitHub({("PUT", WORKFLOW): answer}))
                self.assertEqual((code, err), (0, ""))
                self.assertEqual(report["settings"]["actions_pull_requests"], {"state": "forbidden", "detail": said})
                others = {key: state for key, state in self.states(report).items() if key != "actions_pull_requests"}
                self.assertEqual(set(others.values()), {"done"})
                self.assertIn(ACTIONS_LOG + "not turned on", out.splitlines())
                for word in ("409", "Conflict", "forbidden", "policy"):
                    self.assertNotIn(word, out)

    def test_the_organizations_token_allows_the_box_for_the_organization_then_ticks_the_repository(self):
        """A new organization holds the box off: with the organization's
        token the run allows it there, the default token's permissions sent
        back as the organization had them, and ticks the repository's box
        again with the repository's token; only those two calls carry the
        organization's token."""
        github = FakeGitHub({
            ("PUT", WORKFLOW): [(409, {"message": "Conflict"}), (204, None)],
            ("GET", ORG_WORKFLOW): (200, {"default_workflow_permissions": "write",
                                          "can_approve_pull_request_reviews": False}),
            ("PUT", ORG_WORKFLOW): (204, None),
        })
        code, report, out, err = self.apply(github, org_token=ORG_TOKEN)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(report["settings"]["actions_pull_requests"],
                         {"state": "done", "detail": setup.organization_first("octo-org")})
        self.assertIn(("PUT", ORG_WORKFLOW, {"default_workflow_permissions": "write",
                                             "can_approve_pull_request_reviews": True}), github.writes())
        self.assertEqual([w for w in github.writes() if w[1] == WORKFLOW][-1], ("PUT", WORKFLOW, ACTIONS_ON))
        with_org = [path for _, path, headers, _ in github.calls if ORG_TOKEN in headers["Authorization"]]
        self.assertEqual(with_org, [ORG_WORKFLOW, ORG_WORKFLOW])
        self.assertIn(ACTIONS_LOG + "on", out.splitlines())
        self.assertNotIn(ORG_TOKEN, out)

    def test_an_organization_that_allows_the_box_already_leaves_it_forbidden(self):
        """The organization had the box on, so its enterprise held it: the
        organization is not written and the setting stays forbidden, with
        both answers."""
        github = FakeGitHub({
            ("PUT", WORKFLOW): (409, {"message": "Conflict"}),
            ("GET", ORG_WORKFLOW): (200, {"default_workflow_permissions": "read",
                                          "can_approve_pull_request_reviews": True}),
        })
        code, report, out, err = self.apply(github, org_token=ORG_TOKEN)
        setting = report["settings"]["actions_pull_requests"]
        self.assertEqual(setting["state"], "forbidden")
        self.assertTrue(setting["detail"].startswith("HTTP 409: Conflict; for the organization: "))
        self.assertIn("enterprise", setting["detail"])
        self.assertNotIn(("PUT", ORG_WORKFLOW), [(m, p) for m, p, _ in github.writes()])

    def test_an_organization_github_refuses_keeps_the_409_with_both_answers(self):
        """An installation that did not grant the organization permission,
        or an enterprise that forbids it, answers the organization's change
        with a refusal: the setting stays forbidden and the repository is
        not tried again."""
        for answer, said in (((403, {"message": "Resource not accessible by integration"}),
                              "HTTP 403: Resource not accessible by integration"),
                             ((409, None), "HTTP 409")):
            with self.subTest(answer=answer):
                github = FakeGitHub({("PUT", WORKFLOW): (409, {"message": "Conflict"}),
                                     ("GET", ORG_WORKFLOW): (200, dict(THEIR_WORKFLOW)), ("PUT", ORG_WORKFLOW): answer})
                code, report, out, err = self.apply(github, org_token=ORG_TOKEN)
                self.assertEqual(report["settings"]["actions_pull_requests"],
                                 {"state": "forbidden", "detail": f"HTTP 409: Conflict; for the organization: {said}"})
                self.assertEqual(len([w for w in github.writes() if w[1] == WORKFLOW]), 1)
                self.assertIn(ACTIONS_LOG + "not turned on", out.splitlines())

    def test_a_repository_refused_again_after_the_organization_changed_says_so(self):
        """The organization was changed but the repository's second try is
        refused: the detail says the organization was allowed, and only a
        409 is forbidden, any other refusal a failure."""
        for second, state in (((409, None), "forbidden"), ((502, {"message": "Bad Gateway"}), "failed")):
            with self.subTest(second=second):
                github = FakeGitHub({("PUT", WORKFLOW): [(409, {"message": "Conflict"}), second],
                                     ("GET", ORG_WORKFLOW): (200, dict(THEIR_WORKFLOW)),
                                     ("PUT", ORG_WORKFLOW): (204, None)})
                code, report, out, err = self.apply(github, org_token=ORG_TOKEN)
                setting = report["settings"]["actions_pull_requests"]
                self.assertEqual(setting["state"], state)
                self.assertIn("; allowed for the organization, then for this repository: HTTP ", setting["detail"])

    def test_the_organizations_token_is_not_used_where_the_repository_takes_the_box(self):
        github = FakeGitHub()
        code, report, out, err = self.apply(github, org_token=ORG_TOKEN)
        self.assertEqual(report["settings"]["actions_pull_requests"], {"state": "done", "detail": ""})
        self.assertFalse([path for _, path, headers, _ in github.calls if ORG_TOKEN in headers["Authorization"]])

    def test_actions_refused_otherwise_is_a_failure_in_githubs_words(self):
        """Any other refusal of the write, or of the read before it, is a
        failure, and a read refused writes nothing."""
        refused = (403, {"message": "Resource not accessible by integration"})
        _, report, out, _ = self.apply(FakeGitHub({("PUT", WORKFLOW): refused}))
        self.assertEqual(report["settings"]["actions_pull_requests"],
                         {"state": "failed", "detail": "HTTP 403: Resource not accessible by integration"})
        self.assertIn(ACTIONS_LOG + "not turned on", out.splitlines())
        self.assertNotIn("integration", out)
        github = FakeGitHub({("GET", WORKFLOW): (404, {"message": "Not Found"})})
        _, report, _, _ = self.apply(github)
        self.assertNotIn(WORKFLOW, [path for _, path, _ in github.writes()])
        self.assertEqual(report["settings"]["actions_pull_requests"],
                         {"state": "failed", "detail": "HTTP 404: Not Found"})

    def test_workflow_permissions_that_cannot_be_read_are_not_written(self):
        """The PUT sends the token's permissions back, so an answer that
        does not say them, or says one GitHub does not document, is a
        refusal and no PUT: a guess could widen the token."""
        for answer in ((200, {}), (200, []), (200, {"default_workflow_permissions": None}),
                       (200, {"default_workflow_permissions": "admin", "can_approve_pull_request_reviews": False})):
            with self.subTest(answer=answer):
                github = FakeGitHub({("GET", WORKFLOW): answer})
                _, report, out, _ = self.apply(github)
                self.assertNotIn(WORKFLOW, [path for _, path, _ in github.writes()])
                self.assertEqual(report["settings"]["actions_pull_requests"],
                                 {"state": "failed", "detail": "GitHub's answer did not say the workflow permissions"})
                self.assertIn(ACTIONS_LOG + "not turned on", out.splitlines())

    def test_existing_mode_leaves_the_actions_box_as_it_is(self):
        """The protocol alone brings no workflow that opens a pull request,
        so the box is neither read nor written there, and the report and
        the log say it was not tried."""
        github = FakeGitHub()
        code, report, out, _ = self.apply(github, mode="existing")
        self.assertEqual(code, 0)
        self.assertNotIn(WORKFLOW, [path for _, path, _, _ in github.calls])
        self.assertEqual(report["settings"]["actions_pull_requests"],
                         {"state": "not-tried", "detail": NOT_TRIED_IN_EXISTING})
        self.assertEqual(list(report["settings"]), list(setup.SETTINGS))
        self.assertEqual(out.splitlines()[-5:], [ACTIONS_LOG + "not tried", NOT_LENT_LOG,
                                                 STORE_LOG + "made, default branch only", PAGES_LOG + "not tried",
                                                 PIN_LOG + "not tried"])
        self.assertNotIn(PAGES, [path for _, path, _, _ in github.calls])

    def test_the_log_has_a_line_for_every_setting_done_or_refused(self):
        self.assertEqual(setup.SETTINGS, ("ruleset", "toggles", "topic", "secret_scanning", "push_protection",
                                          "actions_pull_requests", "token_lending", "token_store", "pages", "check_source"))
        for key in setup.SETTINGS:
            if key == setup.TOKEN_LENDING:
                continue
            with self.subTest(setting=key):
                self.assertIn(setup.DONE, setup.LOG_LINES[key])
                self.assertIn(setup.FAILED, setup.LOG_LINES[key])
        # The token lending has one line of two, whatever its state.
        self.assertNotIn(setup.TOKEN_LENDING, setup.LOG_LINES)
        self.assertEqual((setup.TOKENS_LENT, setup.NO_TOKENS_LENT), (LENT_LOG, NOT_LENT_LOG))
        # The box can be forbidden, or not tried in mode existing, and the
        # log tells the owner's policy from no other refusal.
        lines = setup.LOG_LINES[setup.ACTIONS_PULL_REQUESTS]
        self.assertEqual(set(lines), {setup.DONE, setup.FAILED, setup.FORBIDDEN, setup.NOT_TRIED})
        self.assertEqual(lines[setup.FORBIDDEN], lines[setup.FAILED])
        # The pin may wait out its bound, which the log tells from a refusal.
        lines = setup.LOG_LINES[setup.CHECK_SOURCE]
        self.assertEqual(set(lines), {setup.DONE, setup.EXISTS, setup.FAILED, setup.NOT_YET, setup.NOT_TRIED})
        # The token store may be there already, which the log says.
        self.assertEqual(set(setup.LOG_LINES[setup.TOKEN_STORE]), {setup.DONE, setup.EXISTS, setup.FAILED})

    def test_a_token_github_refuses_fails_each_setting_and_nothing_else(self):
        class Github(FakeGitHub):
            def __call__(self, method, url, headers, body):
                self.calls.append((method, url.removeprefix(setup.API), headers, body))
                return 403, b'{"message": "Resource not accessible by integration"}'

        github = Github()
        code, report, out, err = self.apply(github)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.states(report), {
            "ruleset": "failed", "toggles": "failed", "topic": "failed", "secret_scanning": "failed",
            "push_protection": "not-tried", "actions_pull_requests": "failed", "check_source": "not-tried",
        })
        self.assertIsNone(report["private"])
        for key in ("ruleset", "toggles", "topic", "secret_scanning", "actions_pull_requests"):
            self.assertEqual(report["settings"][key]["detail"], "HTTP 403: Resource not accessible by integration")
        self.assertEqual(out.splitlines(), [
            "settings: ruleset: not created",
            "settings: the two toggles: not changed",
            "settings: topic symphony: not set",
            "settings: secret scanning: not turned on",
            "settings: push protection: not tried",
            ACTIONS_LOG + "not turned on",
            NOT_LENT_LOG,
            STORE_LOG + "not made",
            PAGES_LOG + "not turned on",
            PIN_LOG + "not tried",
        ])
        self.assertNotIn("integration", out)

    def test_github_out_of_reach_is_a_failure_with_a_reason(self):
        code, report, out, _ = self.apply(FakeGitHub(raising="GitHub could not be reached (URLError)"))
        self.assertEqual(code, 0)
        self.assertEqual(report["settings"]["ruleset"]["detail"], "GitHub could not be reached (URLError)")
        # No answer is no status, so no owner's policy either.
        self.assertEqual(report["settings"]["actions_pull_requests"],
                         {"state": "failed", "detail": "GitHub could not be reached (URLError)"})
        self.assertNotIn("URLError", out)

    def test_a_refusal_with_no_json_body_keeps_the_status(self):
        class Github(FakeGitHub):
            def __call__(self, method, url, headers, body):
                self.calls.append((method, url.removeprefix(setup.API), headers, body))
                return 502, b"<html>bad gateway</html>"

        _, report, _, _ = self.apply(Github())
        self.assertEqual(report["settings"]["ruleset"]["detail"], "HTTP 502")

    def test_githubs_words_are_one_line_and_bounded(self):
        class Github(FakeGitHub):
            def __call__(self, method, url, headers, body):
                self.calls.append((method, url.removeprefix(setup.API), headers, body))
                return 422, json.dumps({"message": "first line\nsecond line " + "x" * 1000}).encode("utf-8")

        _, report, _, _ = self.apply(Github())
        detail = report["settings"]["ruleset"]["detail"]
        self.assertNotIn("\n", detail)
        self.assertLessEqual(len(detail), setup.DETAIL_LENGTH)
        self.assertTrue(detail.startswith("HTTP 422: first line second line x"))
        self.assertTrue(detail.endswith("..."))

    def test_a_ruleset_file_that_cannot_be_read_costs_the_ruleset_only(self):
        github = FakeGitHub()
        code, report, out, _ = self.apply(github, ruleset=self.root / "missing.json")
        self.assertEqual(code, 0)
        self.assertEqual(self.states(report)["ruleset"], "failed")
        self.assertEqual(report["settings"]["ruleset"]["detail"],
                         "the template's ruleset file could not be read, so no ruleset was made")
        self.assertIsNone(report["ruleset_name"])
        self.assertEqual([method for method, _, _ in github.writes()], ["PATCH", "PUT", "PATCH", "PATCH", "PUT", "PUT", "POST"])
        self.assertIn("settings: ruleset: not created", out)
        self.ruleset.write_text('{"name": "x"}\n', encoding="utf-8")
        code, report, _, _ = self.apply(FakeGitHub())
        self.assertEqual((code, self.states(report)["ruleset"]), (0, "failed"))

    def test_no_token_is_an_error_and_writes_no_report(self):
        with mock.patch.dict(os.environ, {"GH_TOKEN": ""}):
            code, report, _, err = self.apply(FakeGitHub())
        self.assertEqual((code, report), (2, None))
        self.assertIn("GH_TOKEN", err)

    def test_a_repository_name_that_is_not_one_is_an_error(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = setup.main(["apply", "--repo", "a/b; rm -rf /", "--mode", "new", "--ruleset", str(self.ruleset),
                               "--report", str(self.report)], transport=FakeGitHub())
        self.assertEqual(code, 2)
        self.assertFalse(self.report.exists())

    # --- the check's pin -------------------------------------------------------

    def pin(self, report):
        return report["settings"]["check_source"]

    def test_the_pin_puts_back_the_rulesets_own_keys_with_the_check_from_github_actions(self):
        """Once GitHub Actions has queued the check on the head, the
        repository's own ruleset is read by id and put back with the keys a
        PUT takes and nothing of GitHub's own, the check pinned to app 15368
        and every other rule as it was; the PUT carries the Setup App's
        token, and the check runs alone the main App's."""
        github = FakeGitHub()
        code, report, out, err = self.apply(github)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.pin(report), {"state": "done", "detail": ""})
        put = [body for method, path, body in github.writes() if (method, path) == ("PUT", RULESET_PATH)]
        self.assertEqual(put, [PINNED])
        self.assertEqual(list(put[0]), list(setup.RULESET_KEYS))
        calls = [(method, path) for method, path, _, _ in github.calls]
        self.assertLess(calls.index(("GET", CHECK_RUNS)), calls.index(("GET", OWN_RULESETS)))
        self.assertLess(calls.index(("GET", RULESET_PATH)), calls.index(("PUT", RULESET_PATH)))
        self.assertEqual(self.clock.pauses, [])
        self.assertIn(PIN_LOG + "GitHub Actions", out.splitlines())

    def test_the_pin_waits_for_the_check_run_and_takes_any_status(self):
        """No check run yet, then one of another app's, which never counts,
        then GitHub Actions' in progress: two pauses of 15 s and the pin."""
        other = {"name": "check", "status": "completed", "app": {"id": 99, "slug": "someone-else"}}
        running = dict(ACTIONS_RUN, status="in_progress")
        github = FakeGitHub({("GET", CHECK_RUNS): [(200, {"check_runs": []}), (200, {"check_runs": [other]}),
                                                   (200, {"check_runs": [other, running]})]})
        _, report, _, _ = self.apply(github)
        self.assertEqual(self.pin(report)["state"], "done")
        self.assertEqual(self.clock.pauses, [15, 15])
        self.assertIn(("PUT", RULESET_PATH, PINNED), github.writes())

    def test_a_422_from_the_put_is_tried_again_within_the_bound(self):
        """GitHub may not count the app as one that reported the check yet:
        its 422 is waited out, and the next PUT pins."""
        refused = (422, {"message": "Validation Failed",
                         "errors": ["Invalid rule 'required_status_checks': integration 15368 has not reported"]})
        github = FakeGitHub({("PUT", RULESET_PATH): [refused, (200, {"id": RULESET_ID})]})
        _, report, out, _ = self.apply(github)
        self.assertEqual(self.pin(report), {"state": "done", "detail": ""})
        self.assertEqual([path for method, path, _ in github.writes() if path == RULESET_PATH], [RULESET_PATH] * 2)
        self.assertEqual(self.clock.pauses, [15])
        self.assertIn(PIN_LOG + "GitHub Actions", out.splitlines())

    def test_a_422_to_the_end_of_the_bound_is_a_failure_in_githubs_words(self):
        github = FakeGitHub({("PUT", RULESET_PATH): (422, {"message": "Validation Failed", "errors": ["not reported"]})})
        _, report, out, _ = self.apply(github)
        self.assertEqual(self.pin(report), {"state": "failed", "detail": "HTTP 422: Validation Failed not reported"})
        self.assertLessEqual(sum(self.clock.pauses), 600)
        self.assertGreaterEqual(sum(self.clock.pauses), 600 - 15)
        self.assertIn(PIN_LOG + "not set", out.splitlines())
        self.assertNotIn("Validation", out)

    def test_no_check_run_within_the_bound_is_not_yet(self):
        """GitHub Actions never reported: the ruleset stays as created, the
        report says not yet, and the run goes on; about ten minutes passed
        on the clock, in pauses of 15 s."""
        github = FakeGitHub({("GET", CHECK_RUNS): (200, {"total_count": 0, "check_runs": []})})
        code, report, out, err = self.apply(github)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.pin(report), {"state": "not-yet", "detail": "GitHub Actions had not reported the check"
                                            " named \"check\" on the branch symphony/adopt within 10 minutes"})
        self.assertNotIn(RULESET_PATH, [path for _, path, _ in github.writes()])
        self.assertEqual(set(self.clock.pauses), {15})
        self.assertLessEqual(sum(self.clock.pauses), 600)
        self.assertEqual(len(self.clock.pauses), 40)
        self.assertEqual(out.splitlines()[-1], PIN_LOG + "not set yet")
        others = {key: state for key, state in self.states(report).items() if key != "check_source"}
        self.assertEqual(set(others.values()), {"done"})

    def test_a_server_error_while_waiting_is_waited_out_and_a_refusal_is_not(self):
        """A 502 may pass, so the wait goes on, and a round that went through
        afterwards finding nothing is not yet, not the 502; a 403, as from a
        token without Checks, stays, and is a failure at once."""
        github = FakeGitHub({("GET", CHECK_RUNS): [(502, {"message": "Bad Gateway"}), (200, {"check_runs": []})]})
        _, report, _, _ = self.apply(github)
        self.assertEqual(self.pin(report)["state"], "not-yet")
        github = FakeGitHub({("GET", CHECK_RUNS): [(502, None), (200, {"check_runs": [ACTIONS_RUN]})]})
        _, report, _, _ = self.apply(github)
        self.assertEqual(self.pin(report)["state"], "done")
        self.clock.pauses.clear()
        github = FakeGitHub({("GET", CHECK_RUNS): (403, {"message": "Resource not accessible by integration"})})
        _, report, out, _ = self.apply(github)
        self.assertEqual(self.pin(report),
                         {"state": "failed", "detail": "HTTP 403: Resource not accessible by integration"})
        self.assertEqual(self.clock.pauses, [])
        self.assertIn(PIN_LOG + "not set", out.splitlines())

    def test_a_check_with_a_source_already_is_left_as_it_is(self):
        """A check already pinned, to GitHub Actions or another app, keeps its
        source and nothing is written; a ruleset that no longer requires the
        check by the time it is read is not tried."""
        for pinned_to in (15368, 99):
            with self.subTest(pinned_to=pinned_to):
                given = json.loads(json.dumps(GIVEN_BACK))
                given["rules"][2]["parameters"]["required_status_checks"] = [
                    {"context": "check", "integration_id": pinned_to}]
                github = FakeGitHub({("GET", RULESET_PATH): (200, given)})
                _, report, out, _ = self.apply(github)
                self.assertEqual(self.pin(report), {"state": "exists", "detail": ""})
                self.assertNotIn(RULESET_PATH, [path for _, path, _ in github.writes()])
                self.assertIn(PIN_LOG + "set already", out.splitlines())
        given = dict(json.loads(json.dumps(GIVEN_BACK)), rules=[{"type": "deletion"}])
        github = FakeGitHub({("GET", RULESET_PATH): (200, given)})
        _, report, _, _ = self.apply(github)
        self.assertEqual(self.pin(report), {"state": "not-tried",
                                            "detail": "the ruleset requires no check named \"check\" any more"})
        self.assertNotIn(RULESET_PATH, [path for _, path, _ in github.writes()])

    def test_an_organizations_ruleset_of_that_name_is_never_touched(self):
        """The list is the repository's own (includes_parents=false), and an
        entry whose source is the organization is passed over even if GitHub
        listed it: with no ruleset of its own by that name the pin fails at
        once, and the organization's is neither read nor written."""
        org_ruleset = {"id": 3, "name": RULESET["name"], "source_type": "Organization", "source": "octo-org"}
        github = FakeGitHub({("GET", OWN_RULESETS): (200, [org_ruleset])})
        _, report, _, _ = self.apply(github)
        self.assertIn(("GET", OWN_RULESETS), [(method, path) for method, path, _, _ in github.calls])
        self.assertNotIn(f"/repos/{REPO}/rulesets/3", [path for _, path, _, _ in github.calls])
        self.assertEqual(self.pin(report), {"state": "failed",
                                            "detail": "the repository's own rulesets include none named"
                                            " \"Protect the default branch\""})
        self.assertEqual(self.clock.pauses, [])
        github = FakeGitHub({("GET", OWN_RULESETS): (200, [org_ruleset, LISTED])})
        _, report, _, _ = self.apply(github)
        self.assertEqual(self.pin(report)["state"], "done")
        self.assertIn(("PUT", RULESET_PATH, PINNED), github.writes())

    def test_existing_mode_does_not_try_the_pin(self):
        github = FakeGitHub()
        _, report, out, _ = self.apply(github, mode="existing")
        self.assertEqual(self.pin(report), {"state": "not-tried", "detail":
                                            "the protocol alone brings no check, and its ruleset requires none"})
        paths = [path for _, path, _, _ in github.calls]
        self.assertNotIn(CHECK_RUNS, paths)
        self.assertNotIn(OWN_RULESETS, paths)
        self.assertEqual(out.splitlines()[-1], PIN_LOG + "not tried")

    def test_without_the_checks_token_the_pin_is_not_tried(self):
        """The Setup App cannot read check runs, so without the main App's
        Checks token nothing is read or written for the pin."""
        with mock.patch.dict(os.environ, {"GH_CHECKS_TOKEN": ""}):
            github = FakeGitHub()
            code, report, out, _ = self.apply(github)
        self.assertEqual(code, 0)
        self.assertEqual(self.pin(report), {"state": "not-tried",
                                            "detail": "no token that reads check runs could be made for this run"})
        self.assertNotIn(CHECK_RUNS, [path for _, path, _, _ in github.calls])
        self.assertNotIn(RULESET_PATH, [path for _, path, _ in github.writes()])
        self.assertEqual(self.states(report)["ruleset"], "done")

    def test_without_a_head_that_is_a_sha_the_pin_alone_is_not_tried(self):
        """No head, or one that is not a commit's full sha, costs the pin and
        nothing else: no check run is read and every other setting stands."""
        for head in (None, "", "main", "A" * 40):
            with self.subTest(head=head):
                github = FakeGitHub()
                code, report, _, err = self.apply(github, head=head)
                self.assertEqual((code, err), (0, ""))
                self.assertEqual(self.pin(report), {"state": "not-tried",
                                                    "detail": "the run named no commit to read the check run on"})
                self.assertNotIn("check-runs", " ".join(path for _, path, _, _ in github.calls))
                others = {key: state for key, state in self.states(report).items() if key != "check_source"}
                self.assertEqual(set(others.values()), {"done"})

    def test_a_ruleset_left_as_it_was_or_not_created_is_not_pinned(self):
        """A ruleset of that name the repository had is left as it is, as the
        pull request says, so it is not pinned either; with no ruleset
        created there is nothing to pin."""
        listed = {("GET", f"/repos/{REPO}/rulesets?includes_parents=false"): (200, [{"name": RULESET["name"]}])}
        github = FakeGitHub(listed)
        _, report, _, _ = self.apply(github)
        self.assertEqual(self.pin(report), {"state": "not-tried",
                                            "detail": "the ruleset of that name was there already and is left as it is"})
        self.assertNotIn(CHECK_RUNS, [path for _, path, _, _ in github.calls])
        _, report, _, _ = self.apply(FakeGitHub({("POST", f"/repos/{REPO}/rulesets"): (403, {"message": "no"})}))
        self.assertEqual(self.pin(report), {"state": "not-tried", "detail": "no ruleset was created"})
        _, report, _, _ = self.apply(FakeGitHub(), ruleset=self.root / "missing.json")
        self.assertEqual(self.pin(report), {"state": "not-tried", "detail": "no ruleset was created"})

    def test_the_report_is_one_the_body_reads(self):
        self.apply(FakeGitHub())
        self.assertEqual(adopt.read_report(self.report)["outcome"], "applied")
        self.apply(FakeGitHub({("GET", f"/repos/{REPO}"): (401, {"message": "Bad credentials"})}))
        self.assertEqual(adopt.read_report(self.report)["settings"]["toggles"]["state"], "done")


# The token lending: the organization's pool as the template's tools/pool.py
# reads it, the requester's login, which matches its owner without case,
# and the token with the organization permissions Secrets and Variables.
LEND_TOKEN = "ghs_lend_token_for_tests"
REQUESTER = "Mona"
REQUESTER_ID = "583231"
REPO_ID = 4242
ORG = "/orgs/octo-org/actions"
POOL_SETTINGS = {"3": {"owner": "mona", "uid": 583231, "model": "claude-opus-5-5"}, "4": {"owner": "hubot", "uid": 1},
                 "main": {"owner": "MONA", "uid": 583231}, "7": {"id": "0a1b2c3d"}, "9": "not a setting"}


def secret(name):
    return f"{ORG}/secrets/{name}"


def variable(name):
    return f"{ORG}/variables/{name}"


def lent(path):
    return f"{path}/repositories/{REPO_ID}"


def pool_answers(settings=None, visibility="selected", extra=None, repo_visibility="public"):
    """GitHub's answers for an organization whose pool holds the slots 3, 4
    and main, every secret and both variables of selected visibility."""
    answers = {
        ("GET", f"/repos/{REPO}"): (200, {"id": REPO_ID, "visibility": repo_visibility}),
        ("GET", variable("SYMPHONY_CLAUDE_SETTINGS")): (200, {
            "name": "SYMPHONY_CLAUDE_SETTINGS", "visibility": visibility,
            "value": json.dumps(POOL_SETTINGS if settings is None else settings)}),
        ("GET", variable("SYMPHONY_CLAUDE_ACCOUNTS")): (200, {"name": "SYMPHONY_CLAUDE_ACCOUNTS", "value": "3,4",
                                                               "visibility": visibility}),
    }
    for name in ("SYMPHONY_CLAUDE_3", "SYMPHONY_CLAUDE_4", "CLAUDE_CODE_OAUTH_TOKEN"):
        answers[("GET", secret(name))] = (200, {"name": name, "visibility": visibility})
    for path in [secret(name) for name in ("SYMPHONY_CLAUDE_3", "SYMPHONY_CLAUDE_4", "CLAUDE_CODE_OAUTH_TOKEN")] + [
            variable(name) for name in ("SYMPHONY_CLAUDE_ACCOUNTS", "SYMPHONY_CLAUDE_SETTINGS")]:
        answers[("PUT", lent(path))] = (204, None)
    answers.update(extra or {})
    return answers


class Lending(unittest.TestCase):
    """For an organization's repository, the requester's own tokens of the
    pool and the two variables that make it readable are lent to the
    repository: its id added to each one's selected repositories, and
    nothing else written. Another person's slot, a secret of another
    visibility and one that is not there are left as they are; the log
    says the same fixed words for every requester."""

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.ruleset = self.root / "ruleset-main.json"
        self.ruleset.write_text(json.dumps(RULESET) + "\n", encoding="utf-8")
        self.report = self.root / "settings.json"
        patcher = mock.patch.dict(os.environ, {"GH_TOKEN": "ghs_token_for_tests"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def lend(self, github, owner_type="Organization", requester=REQUESTER, token=LEND_TOKEN, mode="existing",
             requester_id=REQUESTER_ID):
        environment = {"GH_LEND_TOKEN": token} if token else {}
        out = io.StringIO()
        with mock.patch.dict(os.environ, environment), contextlib.redirect_stdout(out):
            code = setup.main(["apply", "--repo", REPO, "--mode", mode, "--ruleset", str(self.ruleset),
                               "--report", str(self.report), "--owner-type", owner_type, f"--requester={requester}",
                               f"--requester-id={requester_id}"],
                              transport=github)
        self.assertEqual(code, 0)
        return json.loads(self.report.read_text(encoding="utf-8")), out.getvalue()

    def organization_writes(self, github):
        return [(method, path) for method, path, _ in github.writes() if path.startswith("/orgs/")]

    def test_the_requesters_own_tokens_and_the_two_variables_are_lent(self):
        github = FakeGitHub(pool_answers())
        report, out = self.lend(github)
        self.assertEqual(report["settings"]["token_lending"], {"state": "done", "detail": ""})
        self.assertEqual(self.organization_writes(github), [
            ("PUT", lent(secret("SYMPHONY_CLAUDE_3"))),
            ("PUT", lent(secret("CLAUDE_CODE_OAUTH_TOKEN"))),
            ("PUT", lent(variable("SYMPHONY_CLAUDE_ACCOUNTS"))),
            ("PUT", lent(variable("SYMPHONY_CLAUDE_SETTINGS"))),
        ])
        self.assertEqual(report["lending"], {
            "lent": ["SYMPHONY_CLAUDE_3", "CLAUDE_CODE_OAUTH_TOKEN", "SYMPHONY_CLAUDE_ACCOUNTS",
                     "SYMPHONY_CLAUDE_SETTINGS"], "left": [], "unreached": [], "missing": [], "failed": []})
        self.assertEqual([line for line in out.splitlines() if "token lending" in line], [LENT_LOG])

    def test_another_persons_slot_is_never_read_or_touched(self):
        github = FakeGitHub(pool_answers())
        self.lend(github)
        touched = " ".join(path for _, path, _, _ in github.calls)
        self.assertNotIn("SYMPHONY_CLAUDE_4", touched)
        self.assertNotIn("SYMPHONY_CLAUDE_7", touched)

    def test_the_organization_calls_carry_the_lending_token(self):
        github = FakeGitHub(pool_answers())
        self.lend(github)
        for method, path, headers, _ in github.calls:
            with self.subTest(call=(method, path)):
                token = LEND_TOKEN if path.startswith("/orgs/") else "ghs_token_for_tests"
                self.assertEqual(headers["Authorization"], f"Bearer {token}")

    def test_the_log_names_no_one_and_no_slot(self):
        github = FakeGitHub(pool_answers(extra={("PUT", lent(secret("SYMPHONY_CLAUDE_3"))): (500, {"message": "boom"})}))
        report, out = self.lend(github)
        self.assertEqual(report["settings"]["token_lending"]["state"], "failed")
        for word in ("SYMPHONY_CLAUDE", "CLAUDE_CODE_OAUTH_TOKEN", "mona", "Mona", "octo-org", str(REPO_ID), "boom",
                     REQUESTER_ID, "granted", "pool"):
            self.assertNotIn(word, out)
        # main was lent, so tokens were lent, though not all.
        self.assertEqual([line for line in out.splitlines() if "token lending" in line], [LENT_LOG])

    def test_a_refused_loan_costs_itself_and_the_others_are_still_lent(self):
        github = FakeGitHub(pool_answers(extra={("PUT", lent(secret("SYMPHONY_CLAUDE_3"))): (500, {"message": "boom"})}))
        report, _ = self.lend(github)
        self.assertEqual(report["settings"]["token_lending"],
                         {"state": "failed", "detail": "SYMPHONY_CLAUDE_3: HTTP 500: boom"})
        self.assertEqual(report["lending"]["failed"], ["SYMPHONY_CLAUDE_3"])
        self.assertEqual(report["lending"]["lent"], ["CLAUDE_CODE_OAUTH_TOKEN", "SYMPHONY_CLAUDE_ACCOUNTS",
                                                     "SYMPHONY_CLAUDE_SETTINGS"])

    def test_a_visibility_other_than_selected_is_left_as_it_is(self):
        github = FakeGitHub(pool_answers(visibility="all"))
        report, out = self.lend(github)
        self.assertEqual(self.organization_writes(github), [])
        self.assertEqual(report["settings"]["token_lending"]["state"], "done")
        self.assertEqual(report["lending"]["left"], ["SYMPHONY_CLAUDE_3", "CLAUDE_CODE_OAUTH_TOKEN",
                                                     "SYMPHONY_CLAUDE_ACCOUNTS", "SYMPHONY_CLAUDE_SETTINGS"])
        # The run lent nothing itself, so the log says so.
        self.assertIn(NOT_LENT_LOG, out.splitlines())

    def secrets_private_variables_selected(self):
        extra = {("GET", secret(name)): (200, {"name": name, "visibility": "private"})
                 for name in ("SYMPHONY_CLAUDE_3", "CLAUDE_CODE_OAUTH_TOKEN")}
        return extra

    def test_a_private_secret_never_reaches_a_public_repository_nor_lends_the_variables(self):
        github = FakeGitHub(pool_answers(extra=self.secrets_private_variables_selected()))
        report, out = self.lend(github)
        self.assertEqual(self.organization_writes(github), [])
        self.assertEqual(report["settings"]["token_lending"]["state"], "none-lent")
        self.assertEqual(report["lending"]["unreached"], ["SYMPHONY_CLAUDE_3", "CLAUDE_CODE_OAUTH_TOKEN"])
        self.assertEqual(report["lending"]["left"], [])
        self.assertFalse([path for _, path, _, _ in github.calls if path == variable("SYMPHONY_CLAUDE_ACCOUNTS")])
        self.assertIn(NOT_LENT_LOG, out.splitlines())

    def test_a_private_secret_reaches_a_private_or_internal_repository_and_the_variables_follow(self):
        for visibility in ("private", "internal"):
            with self.subTest(visibility=visibility):
                github = FakeGitHub(pool_answers(extra=self.secrets_private_variables_selected(),
                                                 repo_visibility=visibility))
                report, out = self.lend(github)
                self.assertEqual(report["settings"]["token_lending"]["state"], "done")
                self.assertEqual(report["lending"]["left"], ["SYMPHONY_CLAUDE_3", "CLAUDE_CODE_OAUTH_TOKEN"])
                self.assertEqual(self.organization_writes(github), [
                    ("PUT", lent(variable("SYMPHONY_CLAUDE_ACCOUNTS"))),
                    ("PUT", lent(variable("SYMPHONY_CLAUDE_SETTINGS"))),
                ])
                self.assertIn(NOT_LENT_LOG, out.splitlines())

    def test_a_private_secret_beside_an_unknown_repository_visibility_does_not_reach_it(self):
        self.assertFalse(setup.reaches("private", ""))
        self.assertFalse(setup.reaches("private", "public"))
        self.assertFalse(setup.reaches("selected", "private"))
        self.assertFalse(setup.reaches(None, "private"))
        self.assertTrue(setup.reaches("all", "public"))

    def test_one_secret_lent_lends_the_variables_whatever_the_others(self):
        extra = {("GET", secret("CLAUDE_CODE_OAUTH_TOKEN")): (200, {"name": "x", "visibility": "private"})}
        github = FakeGitHub(pool_answers(extra=extra))
        report, out = self.lend(github)
        self.assertEqual(report["settings"]["token_lending"]["state"], "done")
        self.assertEqual(report["lending"]["unreached"], ["CLAUDE_CODE_OAUTH_TOKEN"])
        self.assertEqual(self.organization_writes(github), [
            ("PUT", lent(secret("SYMPHONY_CLAUDE_3"))),
            ("PUT", lent(variable("SYMPHONY_CLAUDE_ACCOUNTS"))),
            ("PUT", lent(variable("SYMPHONY_CLAUDE_SETTINGS"))),
        ])
        self.assertIn(LENT_LOG, out.splitlines())

    def test_a_secret_that_is_not_there_is_never_made(self):
        github = FakeGitHub(pool_answers(extra={("GET", secret("CLAUDE_CODE_OAUTH_TOKEN")): (404, {"message": "Not Found"})}))
        report, _ = self.lend(github)
        self.assertEqual(report["lending"]["missing"], ["CLAUDE_CODE_OAUTH_TOKEN"])
        self.assertNotIn(("PUT", lent(secret("CLAUDE_CODE_OAUTH_TOKEN"))), self.organization_writes(github))
        self.assertFalse([call for call in github.writes() if call[0] in ("POST", "PATCH") and "/orgs/" in call[1]])

    def test_a_requester_whose_secrets_are_all_gone_lends_nothing(self):
        missing = (404, {"message": "Not Found"})
        github = FakeGitHub(pool_answers(extra={("GET", secret("SYMPHONY_CLAUDE_3")): missing,
                                            ("GET", secret("CLAUDE_CODE_OAUTH_TOKEN")): missing}))
        report, out = self.lend(github)
        self.assertEqual(report["settings"]["token_lending"]["state"], "none-lent")
        self.assertEqual(report["lending"]["missing"], ["SYMPHONY_CLAUDE_3", "CLAUDE_CODE_OAUTH_TOKEN"])
        self.assertEqual(self.organization_writes(github), [])
        self.assertIn(NOT_LENT_LOG, out.splitlines())

    def test_a_requester_who_owns_no_slot_lends_nothing_not_even_the_variables(self):
        for requester in ("octocat", "", "-bad-"):
            with self.subTest(requester=requester):
                github = FakeGitHub(pool_answers())
                report, _ = self.lend(github, requester=requester)
                self.assertEqual(report["settings"]["token_lending"]["state"], "none-owned")
                self.assertEqual(self.organization_writes(github), [])

    def test_an_organization_with_no_pool_settings_has_none_owned(self):
        for answer in ((404, {"message": "Not Found"}), (200, {"value": "not json"}), (200, {"value": "[1]"})):
            with self.subTest(answer=answer):
                github = FakeGitHub(pool_answers(extra={("GET", variable("SYMPHONY_CLAUDE_SETTINGS")): answer}))
                report, _ = self.lend(github)
                self.assertEqual(report["settings"]["token_lending"]["state"], "none-owned")
                self.assertEqual(self.organization_writes(github), [])

    def test_a_missing_permission_is_not_granted_and_quiet(self):
        github = FakeGitHub(pool_answers(extra={("GET", variable("SYMPHONY_CLAUDE_SETTINGS")): (
            403, {"message": "Resource not accessible by integration"})}))
        report, out = self.lend(github)
        self.assertEqual(report["settings"]["token_lending"]["state"], "not-granted")
        self.assertEqual(self.organization_writes(github), [])
        self.assertIn(NOT_LENT_LOG, out.splitlines())

    def test_without_the_lending_token_nothing_of_the_organizations_is_touched(self):
        github = FakeGitHub(pool_answers())
        report, out = self.lend(github, token="")
        self.assertEqual(report["settings"]["token_lending"]["state"], "not-granted")
        self.assertFalse([path for _, path, _, _ in github.calls if path.startswith("/orgs/")])

    def test_a_personal_accounts_repository_is_not_tried(self):
        github = FakeGitHub(pool_answers())
        report, out = self.lend(github, owner_type="User")
        self.assertEqual(report["settings"]["token_lending"]["state"], "not-tried")
        self.assertFalse([path for _, path, _, _ in github.calls if path.startswith("/orgs/")])
        self.assertIn(NOT_LENT_LOG, out.splitlines())

    def test_a_slot_whose_account_id_differs_is_not_lent(self):
        """A login passes to whoever takes it after a rename: the new holder
        of mona's login, with another account id, gets none of her slots."""
        github = FakeGitHub(pool_answers())
        report, out = self.lend(github, requester_id="99")
        self.assertEqual(report["settings"]["token_lending"], {"state": "none-owned", "detail": setup.NONE_OWNED_HINT})
        self.assertEqual(self.organization_writes(github), [])
        self.assertFalse([path for _, path, _, _ in github.calls if "/secrets/" in path])
        self.assertIn(NOT_LENT_LOG, out.splitlines())

    def test_a_slot_that_kept_no_account_id_is_not_lent(self):
        for uid in (None, "583231", True, 0, -583231):
            with self.subTest(uid=uid):
                settings = {"3": {"owner": "mona"}, "main": {"owner": "mona"}}
                if uid is not None:
                    settings["3"]["uid"] = settings["main"]["uid"] = uid
                github = FakeGitHub(pool_answers(settings=settings))
                report, _ = self.lend(github)
                self.assertEqual(report["settings"]["token_lending"],
                                 {"state": "none-owned", "detail": setup.NONE_OWNED_HINT})
                self.assertEqual(self.organization_writes(github), [])

    def test_a_slot_in_the_organizations_keeping_is_not_lent(self):
        # symphony-template#254: a token lent with no say is placed by the
        # organization's owners alone, never by its lender's adoption.
        settings = {"3": {"owner": "mona", "uid": 583231, "keeping": "organization"}}
        github = FakeGitHub(pool_answers(settings=settings))
        report, _ = self.lend(github)
        self.assertEqual(report["settings"]["token_lending"],
                         {"state": "none-owned", "detail": setup.NONE_OWNED_HINT})
        self.assertEqual(self.organization_writes(github), [])

    def test_a_slot_whose_login_and_account_id_match_is_lent(self):
        settings = {"3": {"owner": "MONA", "uid": 583231}, "5": {"owner": "mona", "uid": 7}, "6": {"owner": "mona"}}
        github = FakeGitHub(pool_answers(settings=settings))
        report, _ = self.lend(github)
        self.assertEqual(report["settings"]["token_lending"]["state"], "done")
        self.assertEqual(report["lending"]["lent"][0], "SYMPHONY_CLAUDE_3")
        self.assertEqual(setup.owned_secrets(json.dumps(settings), "mona", REQUESTER_ID), ["SYMPHONY_CLAUDE_3"])
        # Another login with the same account id owns nothing either.
        self.assertEqual(setup.owned_secrets(json.dumps(settings), "hubot", REQUESTER_ID), [])

    def test_without_the_requesters_account_id_nothing_is_lent(self):
        for requester_id in ("", "0", "0583231", "58a", "1" * 21, "+5"):
            with self.subTest(requester_id=requester_id):
                github = FakeGitHub(pool_answers())
                report, out = self.lend(github, requester_id=requester_id)
                self.assertEqual(report["settings"]["token_lending"],
                                 {"state": "not-tried", "detail": "the requester's account id was not given"})
                self.assertFalse([path for _, path, _, _ in github.calls if path.startswith("/orgs/")])
                self.assertIn(NOT_LENT_LOG, out.splitlines())

    def test_a_repository_whose_id_is_unknown_lends_nothing(self):
        github = FakeGitHub(pool_answers(extra={("GET", f"/repos/{REPO}"): (200, {"visibility": "public"})}))
        report, _ = self.lend(github)
        self.assertEqual(report["settings"]["token_lending"]["state"], "failed")
        self.assertFalse([path for _, path, _, _ in github.calls if path.startswith("/orgs/")])

    def test_the_whole_template_lends_too_and_the_body_reads_the_report(self):
        github = FakeGitHub(pool_answers())
        report, _ = self.lend(github, mode="new")
        self.assertEqual(report["settings"]["token_lending"]["state"], "done")
        self.assertEqual(adopt.read_report(self.report)["lending"]["lent"][0], "SYMPHONY_CLAUDE_3")

    def test_the_owned_slots_follow_the_pool_main_last(self):
        settings = {"main": {"owner": "mona"}, "12": {"owner": "mona"}, "2": {"owner": "mona"},
                    "33": {"owner": "mona"}, "5": {"owner": "mona-"}}
        settings = {slot: dict(setting, uid=583231) for slot, setting in settings.items()}
        self.assertEqual(setup.owned_secrets(json.dumps(settings), "mona", REQUESTER_ID),
                         ["SYMPHONY_CLAUDE_2", "SYMPHONY_CLAUDE_12", "CLAUDE_CODE_OAUTH_TOKEN"])
        self.assertEqual(setup.owned_secrets(None, "mona", REQUESTER_ID), [])


class TokenStore(unittest.TestCase):
    """The environment token-store, made limited to the repository's
    default branch, so a workflow pushed to another branch never runs the
    Token workflow's job that holds SymphonyBoard's token; one of that name
    the repository has already is left as it is."""

    def store(self, answers=None):
        github = FakeGitHub(answers)
        report = setup.new_report(setup.APPLIED, "existing")
        report["default_branch"] = "trunk"
        setup.apply_token_store(setup.GitHub("ghs_token_for_tests", transport=github), REPO, report)
        return github, report["settings"][setup.TOKEN_STORE]

    def test_it_is_made_for_the_default_branch_alone(self):
        github, setting = self.store()
        self.assertEqual(setting["state"], setup.DONE)
        self.assertEqual(github.writes(), [
            ("PUT", ENVIRONMENT, ENVIRONMENT_BODY),
            ("POST", ENVIRONMENT + "/deployment-branch-policies", {"name": "trunk", "type": "branch"}),
        ])

    def test_one_there_already_is_left_as_it_is(self):
        github, setting = self.store({("GET", ENVIRONMENT_PROBE): (200, {"total_count": 0, "available_custom_deployment_protection_rule_integrations": []})})
        self.assertEqual(setting["state"], setup.EXISTS)
        self.assertEqual(github.writes(), [])

    def test_a_read_github_refuses_writes_nothing(self):
        github, setting = self.store({("GET", ENVIRONMENT_PROBE): (403, {"message": "Resource not accessible"})})
        self.assertEqual(setting, {"state": setup.FAILED, "detail": "HTTP 403: Resource not accessible"})
        self.assertEqual(github.writes(), [])

    def test_a_refused_branch_rule_is_a_failure_with_githubs_words(self):
        rule = ("POST", ENVIRONMENT + "/deployment-branch-policies")
        github, setting = self.store({rule: (422, {"message": "Validation Failed"})})
        self.assertEqual(setting, {"state": setup.FAILED, "detail": "made with no branch allowed, since the rule"
                                                                   " for trunk was refused: HTTP 422: Validation Failed"})
        self.assertEqual([path for _, path, _ in github.writes()], [ENVIRONMENT, rule[1]])

    def test_the_environment_is_never_read_with_a_permission_the_app_lacks(self):
        github, _ = self.store()
        self.assertNotIn(("GET", ENVIRONMENT), [(method, path) for method, path, _, _ in github.calls])

    def test_an_unknown_default_branch_makes_nothing(self):
        github = FakeGitHub()
        report = setup.new_report(setup.APPLIED, "new")
        report["default_branch"] = None
        setup.apply_token_store(setup.GitHub("ghs_token_for_tests", transport=github), REPO, report)
        self.assertEqual(report["settings"][setup.TOKEN_STORE]["state"], setup.FAILED)
        self.assertEqual(github.calls, [])


class Pages(unittest.TestCase):
    """GitHub Pages built by GitHub Actions and the variable SYMPHONY_DOCS,
    for the whole template's documentation site; a site there already is
    left as it is, and one GitHub will not limit to the readers of a
    repository that is not public is deleted again."""

    NONE = {("GET", PAGES): (404, {"message": "Not Found"})}
    @staticmethod
    def read_back(public):
        """The site's read before it is made, then its read back once
        limited; a fresh list each time, since the fake pops from it."""
        return {("GET", PAGES): [(404, {"message": "Not Found"}), (200, {"public": public})]}

    VARIABLE = ("POST", f"/repos/{REPO}/actions/variables", {"name": "SYMPHONY_DOCS", "value": "pages"})

    def pages(self, answers=None, visibility="public", base=None):
        github = FakeGitHub({**(base or self.NONE), **(answers or {})})
        report = setup.new_report(setup.APPLIED, "new")
        setup.apply_pages(setup.GitHub("ghs_token_for_tests", transport=github), REPO, visibility, report)
        return github, report["settings"][setup.PAGES]

    def calls(self, github):
        return [(method, path) for method, path, _, _ in github.calls]

    def test_a_public_repository_gets_a_site_built_by_actions_and_the_variable(self):
        github, setting = self.pages()
        self.assertEqual(setting["state"], setup.DONE)
        self.assertEqual(github.writes(), [("POST", PAGES, {"build_type": "workflow"}), self.VARIABLE])

    def test_a_private_or_internal_repositorys_site_is_limited_to_its_readers(self):
        for visibility in ("private", "internal", ""):
            with self.subTest(visibility=visibility):
                github, setting = self.pages(visibility=visibility, base=self.read_back(False))
                self.assertEqual(setting["state"], setup.DONE)
                self.assertEqual(github.writes(), [("POST", PAGES, {"build_type": "workflow"}),
                                                   ("PUT", PAGES, {"public": False}), self.VARIABLE])

    def test_a_site_github_will_not_limit_is_deleted_and_no_variable_set(self):
        github, setting = self.pages({("PUT", PAGES): (422, {"message": "Upgrade the plan"})}, visibility="private")
        self.assertEqual(setting["state"], setup.FORBIDDEN)
        self.assertIn(("DELETE", PAGES), self.calls(github))
        self.assertIn("was deleted again", setting["detail"])
        self.assertNotIn(self.VARIABLE, github.writes())

    def test_a_limit_github_accepted_but_did_not_keep_is_deleted(self):
        github, setting = self.pages(visibility="private",
                                     base=self.read_back(True))
        self.assertEqual(setting["state"], setup.FORBIDDEN)
        self.assertIn("still reads as public", setting["detail"])
        self.assertIn(("DELETE", PAGES), self.calls(github))
        self.assertNotIn(self.VARIABLE, github.writes())

    def test_a_site_that_could_not_be_deleted_again_says_so(self):
        github, setting = self.pages({("PUT", PAGES): (422, {"message": "Upgrade the plan"}),
                                      ("DELETE", PAGES): (500, {"message": "Server Error"})}, visibility="private")
        self.assertEqual(setting["state"], setup.FORBIDDEN)
        self.assertIn("could not be deleted again", setting["detail"])

    def test_a_site_there_already_is_left_as_it_is(self):
        github, setting = self.pages({("GET", PAGES): (200, {"build_type": "legacy"})})
        self.assertEqual(setting["state"], setup.EXISTS)
        self.assertEqual(github.writes(), [])

    def test_a_variable_there_already_is_updated(self):
        github, setting = self.pages({("POST", f"/repos/{REPO}/actions/variables"): (409, {"message": "Already exists"})})
        self.assertEqual(setting["state"], setup.DONE)
        self.assertEqual(github.writes()[-1], ("PATCH", f"/repos/{REPO}/actions/variables/SYMPHONY_DOCS",
                                               {"name": "SYMPHONY_DOCS", "value": "pages"}))

    def test_a_refused_site_is_a_failure_and_sets_no_variable(self):
        github, setting = self.pages({("POST", PAGES): (403, {"message": "Resource not accessible by integration"})})
        self.assertEqual(setting, {"state": setup.FAILED, "detail": "HTTP 403: Resource not accessible by integration"})
        self.assertNotIn(self.VARIABLE, github.writes())

    def test_a_refused_variable_says_the_site_is_on(self):
        github, setting = self.pages({("POST", f"/repos/{REPO}/actions/variables"): (403, {"message": "Resource not accessible by integration"})})
        self.assertEqual(setting, {"state": setup.SITE_ONLY, "detail": "HTTP 403: Resource not accessible by integration"})

    def test_no_token_for_pages_is_not_granted_and_calls_nothing(self):
        report = setup.new_report(setup.APPLIED, "new")
        setup.apply_pages(None, REPO, "public", report)
        self.assertEqual(report["settings"][setup.PAGES]["state"], setup.NOT_GRANTED)

    def test_the_run_without_a_pages_token_leaves_the_site_and_adopts(self):
        github = FakeGitHub(self.NONE)
        with mock.patch.dict(os.environ, {"GH_TOKEN": "ghs_token_for_tests"}, clear=True):
            report = setup.apply_settings(setup.GitHub("ghs_token_for_tests", transport=github), REPO, RULESET, "new",
                                          waiting=FakeClock().waiting())
        self.assertEqual(report["settings"][setup.PAGES]["state"], setup.NOT_GRANTED)
        self.assertNotIn(("POST", PAGES), self.calls(github))


class Transport(unittest.TestCase):
    def test_a_body_cut_short_is_a_failure_to_get_an_answer(self):
        """http.client's own errors are not OSErrors; one escaping the
        transport would end the run before the report."""
        import http.client

        def opening(request, timeout):
            raise http.client.IncompleteRead(b"partial")

        with mock.patch.object(setup.OPENER, "open", opening):
            with self.assertRaises(setup.GitHubError) as caught:
                setup.urllib_transport("GET", "https://api.github.com/repos/o/r", {}, None)
        self.assertIn("IncompleteRead", str(caught.exception))

    def test_a_refusal_whose_body_is_cut_short_is_the_same_failure(self):
        import http.client
        import urllib.error

        class CutShort:
            def read(self):
                raise http.client.IncompleteRead(b"par")

        def opening(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 502, "Bad Gateway", {}, CutShort())

        with mock.patch.object(setup.OPENER, "open", opening):
            with self.assertRaises(setup.GitHubError):
                setup.urllib_transport("GET", "https://api.github.com/repos/o/r", {}, None)


class Skip(unittest.TestCase):
    def test_skip_writes_why_nothing_was_applied(self):
        self.assertEqual(setup.WHYS, ("not-set-up", "not-installed", "front-door-broken", "not-reported"))
        with tempfile.TemporaryDirectory() as scratch:
            report = Path(scratch) / "settings.json"
            for why in setup.WHYS:
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = setup.main(["skip", "--why", why, "--mode", "existing", "--report", str(report)])
                self.assertEqual(code, 0)
                written = json.loads(report.read_text(encoding="utf-8"))
                self.assertEqual((written["schema"], written["outcome"], written["mode"], written["settings"]),
                                 (setup.REPORT_SCHEMA, why, "existing", {}))
                self.assertEqual(out.getvalue(), f"settings: none applied ({why})\n{NOT_LENT_LOG}\n")
                self.assertEqual(adopt.read_report(report)["outcome"], why)

    def test_a_reason_that_is_not_one_is_refused(self):
        with self.assertRaises(SystemExit):
            setup.parse_args(["skip", "--why", "applied", "--mode", "new", "--report", "x"])


class Messages(unittest.TestCase):
    def test_githubs_message_and_errors_become_one_line(self):
        data = json.dumps({"message": "Validation  Failed", "errors": [{"message": "a\nb"}, "plain", {"code": "x"}]})
        self.assertEqual(setup.github_message(data.encode("utf-8")), "Validation Failed a b plain x")
        self.assertEqual(setup.github_message(b"not json"), "")
        self.assertEqual(setup.github_message(b"[1, 2]"), "")
        self.assertEqual(setup.github_message(b'{"message": ""}'), "")


if __name__ == "__main__":
    unittest.main()
