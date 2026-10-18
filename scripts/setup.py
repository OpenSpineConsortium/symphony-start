#!/usr/bin/env python3
"""Apply the template's repository settings in the adoption run, as the Setup App.

.github/workflows/adopt.yml runs this after the branch symphony/adopt is
pushed and before the pull request opens, with the token of the OpenSpine
Symphony Setup App for the one repository (Administration: write, Metadata:
read), when the person installed that App on it. It does what the
template's scripts/setup-repo.sh does from a clone, through the REST API
with the standard library, so the repository's settings need no step by
hand:

  1. the ruleset of the template's docs/setup/ruleset-main.json for the
     default branch, unless the repository has one of that name already;
     in mode existing without the rule that requires the check named
     "check", which the template's own CI job carries and a repository
     the template did not make may not have, so that rule would hold
     its default branch to a check that never runs;
  2. "Automatically delete head branches" and "Allow auto-merge";
  3. the repository topic symphony, the sign on the repository's page
     that it is adopted: the About sidebar shows it to anyone, and the
     Symphony browser extension reads it from the page to show "Ready
     for Symphony" in place of "Migrate to Symphony" with no call to
     GitHub; the topics the repository has stay;
  4. secret scanning, then push protection, which GitHub accepts only
     once scanning is on; where the plan or the visibility offers
     neither, GitHub's answer is kept and the run goes on;
  5. in mode new, "Allow GitHub Actions to create and approve pull
     requests", under Workflow permissions: the whole template's weekly
     protocol update (.github/workflows/protocol.yml) and its "Add a
     worker" form (.github/workflows/add-worker.yml) open their pull
     requests with GITHUB_TOKEN, which GitHub allows only with it, and
     without it answer with an issue or a link. It lets a workflow
     approve a pull request too, which matters only where a ruleset
     requires a review: the one this run applies requires none, and
     crowd mode's, which requires one, comes with the template's
     scripts/crowd.py setup, which turns the box off again. The
     protocol alone brings neither workflow, so mode existing leaves the
     box as it is, since the approvals would then serve nothing of the
     adoption's and might stand in for a review the repository's own
     rules require. A new organization holds the box off for its
     repositories, and GitHub answers the repository's change with 409;
     where the run was given a second token, GH_ORG_TOKEN, with the
     organization permission Administration (write), it allows the box
     for the organization, the default token's permissions sent back as
     the organization had them, and ticks the repository's box again.
     Where the organization cannot be changed, or its enterprise
     forbids it, GitHub's answer is kept and the run goes on.

The labels are the workflow's, made with the main App's token; the
template's variables are optional and none is set here; the Claude token
is the person's own and never asked for; and GitHub's reading of
.github/CODEOWNERS is shown on the file's own page once it is merged.

  apply  does the above and writes a report of each setting's outcome. It
         exits 0 whatever GitHub answered, since the pull request is
         where the person reads what happened: GitHub's words go to the
         report, which scripts/adopt.py body --settings renders into the
         pull request in their repository, and this public log gets one
         fixed line per setting.
  skip   writes a report that says why nothing was applied: this front
         door has no Setup App yet; the App is not installed on the
         repository; the front door's own Setup App is not working, which
         a probe on the owner's installation tells from the first; or the
         step that applies them stopped before it could report. The pull
         request's text has one source for all of it.

Python 3.12 or later, standard library only. The tokens are read from
GH_TOKEN and GH_ORG_TOKEN and never printed.
"""

import argparse
import http.client
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPORT_SCHEMA = "sdlc-setup/1"
API = "https://api.github.com"
API_VERSION = "2022-11-28"
USER_AGENT = "symphony-start-setup"
REPOSITORY = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}")
REQUIRED_CHECKS_RULE = "required_status_checks"

# A report's outcome: the settings were applied (each with its own state
# below), or nothing was, for one of two reasons.
APPLIED = "applied"
NOT_SET_UP = "not-set-up"
NOT_INSTALLED = "not-installed"
FRONT_DOOR_BROKEN = "front-door-broken"
NOT_REPORTED = "not-reported"
WHYS = (NOT_SET_UP, NOT_INSTALLED, FRONT_DOOR_BROKEN, NOT_REPORTED)
# One setting's state. Forbidden is a setting the policy of the
# repository's organization, or of its enterprise, keeps off, which no
# repository setting overrides: GitHub answers 409 to it.
DONE = "done"
EXISTS = "exists"
FAILED = "failed"
FORBIDDEN = "forbidden"
NOT_TRIED = "not-tried"
# The settings, in the order they are applied and reported.
RULESET = "ruleset"
TOGGLES = "toggles"
TOPIC = "topic"
SECRET_SCANNING = "secret_scanning"
PUSH_PROTECTION = "push_protection"
ACTIONS_PULL_REQUESTS = "actions_pull_requests"
SETTINGS = (RULESET, TOGGLES, TOPIC, SECRET_SCANNING, PUSH_PROTECTION, ACTIONS_PULL_REQUESTS)
# The topic an adopted repository carries, which the template's own
# scripts/setup-repo.sh adds too.
TOPIC_NAME = "symphony"
# What GitHub's answer on the workflow permissions may hold for the default
# token's permissions, which the PUT sends back as they were read.
TOKEN_PERMISSIONS = ("read", "write")
# GitHub's answer when the organization or its enterprise holds the setting.
POLICY_CONFLICT = 409
# The detail of a box ticked only after the organization allowed it, which
# the pull request renders after the setting's name.
ORGANIZATION_FIRST = "turned on for the organization first, whose policy held it off, then for this repository"
# GitHub's message lands in the pull request, so it is one line and short.
DETAIL_LENGTH = 300


class GitHubError(Exception):
    """GitHub said no, or could not be reached: one line that says which,
    and the HTTP status when there was one, as scripts/sweep.py keeps it,
    since a 409 tells the owner's policy from any other refusal."""

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def error_words(error):
    """One of GitHub's errors as words: its message, or, as a validation
    error is documented, its resource, field and code."""
    if isinstance(error, str):
        return error
    if not isinstance(error, dict):
        return ""
    if error.get("message"):
        return str(error["message"])
    return " ".join(str(error[key]) for key in ("resource", "field", "code") if error.get(key))


def github_message(data):
    """What GitHub's error body says, as one line: its message and each of
    its errors, where the body is JSON, else nothing."""
    try:
        body = json.loads(data)
    except (ValueError, TypeError):
        return ""
    if not isinstance(body, dict):
        return ""
    parts = [str(body.get("message") or "")] + [error_words(error) for error in body.get("errors") or []]
    return " ".join(" ".join(part.split()) for part in parts if part).strip()


def one_line(text, length=DETAIL_LENGTH):
    text = " ".join(str(text).split())
    return text if len(text) <= length else text[:length - 3].rstrip() + "..."


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect is an answer, not a request to repeat: urllib would turn
    a redirected POST into a GET of the new place and report its 200, so
    every 3xx is handed back as the status it is."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def urllib_transport(method, url, headers, body):
    """(status, bytes) for one request; an HTTP error is an answer too, and
    only a failure to get one raises."""
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        try:
            with OPENER.open(request, timeout=30) as reply:
                return reply.status, reply.read()
        except urllib.error.HTTPError as error:
            # Reading the refusal's body can fail the same ways as the
            # request, so it stays inside the outer try.
            return error.code, error.read()
    except (urllib.error.URLError, OSError, http.client.HTTPException) as error:
        raise GitHubError(f"GitHub could not be reached ({type(error).__name__})") from error


class GitHub:
    """The REST API with the token, through a transport the tests replace."""

    def __init__(self, token, transport=urllib_transport, api=API):
        self.token = token
        self.transport = transport
        self.api = api

    def call(self, method, path, body=None):
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": API_VERSION,
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        status, data = self.transport(method, f"{self.api}{path}", headers, body)
        if not 200 <= status < 300:
            said = github_message(data)
            raise GitHubError(f"HTTP {status}" + (f": {said}" if said else ""), status)
        try:
            return json.loads(data) if data and data.strip() else {}
        except ValueError:
            raise GitHubError(f"HTTP {status}: GitHub's answer was not JSON", status) from None


# --- the report -------------------------------------------------------------------


def new_report(outcome, mode):
    return {
        "schema": REPORT_SCHEMA,
        "outcome": outcome,
        "mode": mode,
        "private": None,
        "ruleset_name": None,
        "required_check": False,
        "settings": {},
    }


def record(report, key, state, detail=""):
    report["settings"][key] = {"state": state, "detail": one_line(detail) if detail else ""}


def write_report(path, report):
    Path(path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


# --- the settings -----------------------------------------------------------------


def ruleset_for(path, mode):
    """The template's ruleset as a dict; in mode existing without the rule
    that requires a check. ValueError when the file is not a ruleset."""
    ruleset = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(ruleset, dict) or not ruleset.get("name") or not isinstance(ruleset.get("rules"), list):
        raise ValueError("not a ruleset: no name or no list of rules")
    if mode == "existing":
        ruleset["rules"] = [rule for rule in ruleset["rules"] if rule.get("type") != REQUIRED_CHECKS_RULE]
    return ruleset


def requires_check(ruleset):
    return any(rule.get("type") == REQUIRED_CHECKS_RULE for rule in ruleset["rules"])


def read_visibility(github, repo, report):
    """Whether the repository is private, which the pull request's text
    needs: GitHub Free writes a private repository's ruleset but does not
    enforce it. The visibility, not the flag private, which an internal
    repository carries too. Unknown when the read fails; the settings are
    tried anyway."""
    try:
        report["private"] = github.call("GET", f"/repos/{repo}").get("visibility") == "private"
    except GitHubError:
        report["private"] = None


def apply_ruleset(github, repo, ruleset, report):
    """Create the ruleset unless the repository has one of that name. GitHub
    would make a second one of the same name, so the check is this script's.
    includes_parents=false keeps an organization's rulesets out of the
    list: they are not this repository's."""
    name = ruleset["name"]
    try:
        listed = github.call("GET", f"/repos/{repo}/rulesets?includes_parents=false")
        if any(isinstance(item, dict) and item.get("name") == name for item in listed):
            record(report, RULESET, EXISTS)
            return
        github.call("POST", f"/repos/{repo}/rulesets", ruleset)
        record(report, RULESET, DONE)
    except GitHubError as said:
        record(report, RULESET, FAILED, str(said))


def apply_toggles(github, repo, report):
    """The two toggles under General, one idempotent PATCH."""
    try:
        github.call("PATCH", f"/repos/{repo}", {"delete_branch_on_merge": True, "allow_auto_merge": True})
        record(report, TOGGLES, DONE)
    except GitHubError as said:
        record(report, TOGGLES, FAILED, str(said))


def apply_topic(github, repo, report):
    """Add the topic symphony to the repository's topics. The PUT replaces
    the whole list, so the list is read first and theirs go back with it;
    a list that cannot be read is a refusal, since writing without it
    would drop them. The topic is the page-visible sign of an adoption:
    the About sidebar shows it to anyone, and the Symphony browser
    extension reads it from the page to say "Ready for Symphony" without
    a call to GitHub."""
    try:
        answer = github.call("GET", f"/repos/{repo}/topics")
        names = answer.get("names") if isinstance(answer, dict) else None
        if not isinstance(names, list):
            raise GitHubError("GitHub's answer listed no topics")
        if TOPIC_NAME in names:
            record(report, TOPIC, DONE, "was there already")
            return
        github.call("PUT", f"/repos/{repo}/topics", {"names": [*names, TOPIC_NAME]})
        record(report, TOPIC, DONE)
    except GitHubError as said:
        record(report, TOPIC, FAILED, str(said))


def apply_scanning(github, repo, report):
    """Secret scanning, then push protection, which GitHub accepts only once
    scanning is on. A refusal is the plan or the visibility, not the
    script: GitHub's words are kept for the pull request and the run goes
    on; push protection is not tried after scanning was refused."""
    try:
        github.call("PATCH", f"/repos/{repo}",
                    {"security_and_analysis": {"secret_scanning": {"status": "enabled"}}})
        record(report, SECRET_SCANNING, DONE)
    except GitHubError as said:
        record(report, SECRET_SCANNING, FAILED, str(said))
        record(report, PUSH_PROTECTION, NOT_TRIED, "secret scanning is not on")
        return
    try:
        github.call("PATCH", f"/repos/{repo}",
                    {"security_and_analysis": {"secret_scanning_push_protection": {"status": "enabled"}}})
        record(report, PUSH_PROTECTION, DONE)
    except GitHubError as said:
        record(report, PUSH_PROTECTION, FAILED, str(said))


def tick_box(github, path):
    """Tick "Allow GitHub Actions to create and approve pull requests" at
    path, a repository's or an organization's workflow permissions. The
    PUT sets the default token's permissions too, so they go back as
    GitHub read them and only the box changes; an answer that does not
    say them is a refusal and no PUT, since a guess could widen the token.
    True when the box was on already and nothing was written."""
    answer = github.call("GET", path)
    answer = answer if isinstance(answer, dict) else {}
    if answer.get("can_approve_pull_request_reviews") is True:
        return True
    permissions = answer.get("default_workflow_permissions")
    if permissions not in TOKEN_PERMISSIONS:
        raise GitHubError("GitHub's answer did not say the workflow permissions")
    github.call("PUT", path, {"default_workflow_permissions": permissions, "can_approve_pull_request_reviews": True})
    return False


def allow_for_organization(github, org_github, repo, report, refused):
    """After the repository's 409: allow the box for the organization with
    the organization's token, then tick the repository's again. An
    organization whose box is on already was not what held it, so its
    enterprise did and nothing is written; any refusal here keeps the
    first 409 as the setting's state, with both of GitHub's answers."""
    org = repo.split("/")[0]
    try:
        if tick_box(org_github, f"/orgs/{org}/actions/permissions/workflow"):
            raise GitHubError("the organization allows it already, so its enterprise holds it")
        tick_box(github, f"/repos/{repo}/actions/permissions/workflow")
        record(report, ACTIONS_PULL_REQUESTS, DONE, ORGANIZATION_FIRST)
    except GitHubError as said:
        record(report, ACTIONS_PULL_REQUESTS, FORBIDDEN, f"{refused}; for the organization: {said}")


def apply_actions_pull_requests(github, repo, report, org_github=None):
    """Tick the repository's box; a box ticked already is recorded and not
    written again. A 409 is the policy of the organization or its
    enterprise, kept apart from other refusals so the pull request can say
    who may change it, and where; with the organization's token the run
    first tries to allow it for the organization."""
    try:
        if tick_box(github, f"/repos/{repo}/actions/permissions/workflow"):
            record(report, ACTIONS_PULL_REQUESTS, DONE, "was on already")
        else:
            record(report, ACTIONS_PULL_REQUESTS, DONE)
    except GitHubError as said:
        if said.status == POLICY_CONFLICT and org_github is not None:
            allow_for_organization(github, org_github, repo, report, str(said))
        else:
            record(report, ACTIONS_PULL_REQUESTS, FORBIDDEN if said.status == POLICY_CONFLICT else FAILED, str(said))


def apply_settings(github, repo, ruleset, mode, org_github=None):
    """Every setting, each on its own: one that fails costs itself and
    nothing else. ruleset is the dict, or the one-line reason it could not
    be read."""
    report = new_report(APPLIED, mode)
    read_visibility(github, repo, report)
    if isinstance(ruleset, dict):
        report["ruleset_name"] = ruleset["name"]
        report["required_check"] = requires_check(ruleset)
        apply_ruleset(github, repo, ruleset, report)
    else:
        record(report, RULESET, FAILED, ruleset)
    apply_toggles(github, repo, report)
    apply_topic(github, repo, report)
    apply_scanning(github, repo, report)
    # Only the whole template brings the workflows that need the box (5).
    if mode == "new":
        apply_actions_pull_requests(github, repo, report, org_github)
    else:
        record(report, ACTIONS_PULL_REQUESTS, NOT_TRIED, "the protocol alone opens no pull request with GitHub Actions")
    return report


# The log is public: one fixed line per setting, never GitHub's words,
# which may name the plan, and never the repository's state beyond this.
LOG_LINES = {
    RULESET: {DONE: "ruleset: created", EXISTS: "ruleset: exists, left as it is", FAILED: "ruleset: not created"},
    TOGGLES: {DONE: "delete head branches on merge, allow auto-merge: on", FAILED: "the two toggles: not changed"},
    TOPIC: {DONE: "topic symphony: on", FAILED: "topic symphony: not set"},
    SECRET_SCANNING: {DONE: "secret scanning: on", FAILED: "secret scanning: not turned on"},
    PUSH_PROTECTION: {DONE: "push protection: on", FAILED: "push protection: not turned on",
                      NOT_TRIED: "push protection: not tried"},
    # The organization's policy is a refusal like any other here: the log
    # says whether the box was ticked and nothing of the owner's settings.
    ACTIONS_PULL_REQUESTS: {DONE: "allow GitHub Actions to create and approve pull requests: on",
                            FAILED: "allow GitHub Actions to create and approve pull requests: not turned on",
                            FORBIDDEN: "allow GitHub Actions to create and approve pull requests: not turned on",
                            NOT_TRIED: "allow GitHub Actions to create and approve pull requests: not tried"},
}


def log_lines(report):
    for key in SETTINGS:
        setting = report["settings"].get(key)
        if setting:
            yield "settings: " + LOG_LINES[key][setting["state"]]


# --- the command line -------------------------------------------------------------


def command_apply(options, transport=urllib_transport):
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        print("setup: GH_TOKEN is not set", file=sys.stderr)
        return 2
    if not REPOSITORY.fullmatch(options.repo):
        print("setup: --repo must be OWNER/NAME", file=sys.stderr)
        return 2
    try:
        ruleset = ruleset_for(options.ruleset, options.mode)
    except (OSError, ValueError, UnicodeDecodeError):
        ruleset = "the template's ruleset file could not be read, so no ruleset was made"
    github = GitHub(token, transport, options.api)
    # The organization's token is minted only for an organization's
    # repository in mode new, and only where the installation granted the
    # organization permission; without it a 409 stays a 409.
    org_token = os.environ.get("GH_ORG_TOKEN", "")
    org_github = GitHub(org_token, transport, options.api) if org_token else None
    try:
        report = apply_settings(github, options.repo, ruleset, options.mode, org_github)
        write_report(options.report, report)
    except OSError as problem:
        print(f"setup: {problem}", file=sys.stderr)
        return 1
    for line in log_lines(report):
        print(line)
    return 0


def command_skip(options, transport=None):
    try:
        write_report(options.report, new_report(options.why, options.mode))
    except OSError as problem:
        print(f"setup: {problem}", file=sys.stderr)
        return 1
    print(f"settings: none applied ({options.why})")
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Apply the template's repository settings as the Setup App.")
    commands = parser.add_subparsers(dest="command", required=True)

    applying = commands.add_parser("apply", help="apply the settings with the token in GH_TOKEN and write a report")
    applying.add_argument("--repo", required=True, help="the repository as OWNER/NAME")
    applying.add_argument("--ruleset", required=True, help="the template's docs/setup/ruleset-main.json")
    applying.add_argument("--mode", required=True, choices=("new", "existing"))
    applying.add_argument("--report", required=True, help="where to write the report")
    applying.add_argument("--api", default=API, help=argparse.SUPPRESS)

    skipping = commands.add_parser("skip", help="write a report that says why nothing was applied")
    skipping.add_argument("--why", required=True, choices=WHYS)
    skipping.add_argument("--mode", required=True, choices=("new", "existing"))
    skipping.add_argument("--report", required=True, help="where to write the report")
    return parser.parse_args(argv)


COMMANDS = {"apply": command_apply, "skip": command_skip}


def main(argv=None, transport=urllib_transport):
    options = parse_args(argv)
    return COMMANDS[options.command](options, transport)


if __name__ == "__main__":
    sys.exit(main())
