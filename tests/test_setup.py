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
mode existing leaves the box alone.
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


class FakeGitHub:
    """A transport that answers from a table keyed (method, path) and keeps
    every call; the default answers are a public repository with no
    ruleset and GitHub's default workflow permissions that accepts every
    write. An answer of None is a body of nothing, as a 204 has."""

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
            status, answer = 200, {"private": False}
        elif (method, path) == ("GET", f"/repos/{REPO}/rulesets?includes_parents=false"):
            status, answer = 200, []
        elif (method, path) == ("GET", TOPICS):
            status, answer = 200, {"names": list(THEIR_TOPICS)}
        elif (method, path) == ("GET", WORKFLOW):
            status, answer = 200, dict(THEIR_WORKFLOW)
        elif (method, path) == ("PUT", WORKFLOW):
            status, answer = 204, None
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
        patcher = mock.patch.dict(os.environ, {"GH_TOKEN": "ghs_token_for_tests"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def apply(self, github, mode="new", ruleset=None, org_token=None):
        """Run apply; (exit code, the report or None, stdout, stderr)."""
        if org_token:
            patcher = mock.patch.dict(os.environ, {"GH_ORG_TOKEN": org_token})
            patcher.start()
            self.addCleanup(patcher.stop)
        out, err = io.StringIO(), io.StringIO()
        argv = ["apply", "--repo", REPO, "--mode", mode, "--ruleset", str(ruleset or self.ruleset),
                "--report", str(self.report)]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = setup.main(argv, transport=github)
        report = json.loads(self.report.read_text(encoding="utf-8")) if self.report.exists() else None
        return code, report, out.getvalue(), err.getvalue()

    def states(self, report):
        return {key: setting["state"] for key, setting in report["settings"].items()}

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
        ])
        self.assertEqual(report["schema"], setup.REPORT_SCHEMA)
        self.assertEqual((report["outcome"], report["mode"], report["private"]), ("applied", "new", False))
        self.assertEqual((report["ruleset_name"], report["required_check"]), ("Protect the default branch", True))
        self.assertEqual(self.states(report), {
            "ruleset": "done", "toggles": "done", "topic": "done", "secret_scanning": "done", "push_protection": "done",
            "actions_pull_requests": "done",
        })
        self.assertEqual(list(report["settings"]), list(setup.SETTINGS))
        self.assertEqual(out.splitlines(), [
            "settings: ruleset: created",
            "settings: delete head branches on merge, allow auto-merge: on",
            "settings: topic symphony: on",
            "settings: secret scanning: on",
            "settings: push protection: on",
            ACTIONS_LOG + "on",
        ])

    def test_every_call_carries_the_token_and_the_api_version(self):
        github = FakeGitHub()
        self.apply(github)
        for method, path, headers, body in github.calls:
            with self.subTest(call=(method, path)):
                self.assertEqual(headers["Authorization"], "Bearer ghs_token_for_tests")
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
        self.assertNotIn("POST", [method for method, _, _ in github.writes()])
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
            "push_protection": "not-tried", "actions_pull_requests": "failed",
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
            "push_protection": "not-tried", "actions_pull_requests": "done",
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
            "push_protection": "done", "actions_pull_requests": "done",
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
                         {"state": "done", "detail": setup.ORGANIZATION_FIRST})
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
        self.assertEqual(out.splitlines()[-1], ACTIONS_LOG + "not tried")

    def test_the_log_has_a_line_for_every_setting_done_or_refused(self):
        self.assertEqual(setup.SETTINGS, ("ruleset", "toggles", "topic", "secret_scanning", "push_protection",
                                          "actions_pull_requests"))
        for key in setup.SETTINGS:
            with self.subTest(setting=key):
                self.assertIn(setup.DONE, setup.LOG_LINES[key])
                self.assertIn(setup.FAILED, setup.LOG_LINES[key])
        # The box can be forbidden, or not tried in mode existing, and the
        # log tells the owner's policy from no other refusal.
        lines = setup.LOG_LINES[setup.ACTIONS_PULL_REQUESTS]
        self.assertEqual(set(lines), {setup.DONE, setup.FAILED, setup.FORBIDDEN, setup.NOT_TRIED})
        self.assertEqual(lines[setup.FORBIDDEN], lines[setup.FAILED])

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
            "push_protection": "not-tried", "actions_pull_requests": "failed",
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
        self.assertEqual([method for method, _, _ in github.writes()], ["PATCH", "PUT", "PATCH", "PATCH", "PUT"])
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

    def test_the_report_is_one_the_body_reads(self):
        self.apply(FakeGitHub())
        self.assertEqual(adopt.read_report(self.report)["outcome"], "applied")
        self.apply(FakeGitHub({("GET", f"/repos/{REPO}"): (401, {"message": "Bad credentials"})}))
        self.assertEqual(adopt.read_report(self.report)["settings"]["toggles"]["state"], "done")


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
                self.assertEqual(out.getvalue(), f"settings: none applied ({why})\n")
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
