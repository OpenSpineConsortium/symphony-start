#!/usr/bin/env python3
"""Apply the template's repository settings in the adoption run, as the Setup App.

.github/workflows/adopt.yml runs this after the branch symphony/adopt is
pushed and before the pull request opens, with the token of the OpenSpine
Symphony Setup App for the one repository (Administration: write, Metadata:
read), when the person installed that App on it; the App stays
installed after the run, acting only during an adoption run,
until the person uninstalls it. It does what the
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
     forbids it, GitHub's answer is kept and the run goes on;
  6. in mode new, once the ruleset of step 1 was created and requires the
     check, that check pinned to GitHub Actions (app 15368) as its source,
     so that a commit status named "check", which anyone with write access
     can post, no longer satisfies it. GitHub takes the pin only from an
     app that has reported the check already, so the ruleset is created
     without it, and this step waits, up to about ten minutes, for the
     check run that the template's CI starts on the branch symphony/adopt
     the run pushed (--head), then puts the ruleset back with the pin; a
     422, the app not yet counted as one that reported, is tried again
     within the same bound. Reading check runs needs the Checks
     permission, which the Setup App does not hold, so the read uses a
     token of the main App's with Checks read alone, GH_CHECKS_TOKEN, and
     the write the Setup App's. A ruleset of that name the repository had
     already is left as it is, unpinned, as step 1 says it is, and so is
     an organization's ruleset of that name, which only its owners edit;
  7. for an organization's repository, in either mode, the requester's
     own Claude tokens lent to it: the repository is added to the
     selected repositories of each organization secret of the token pool
     (SYMPHONY_CLAUDE_1 to SYMPHONY_CLAUDE_32, and CLAUDE_CODE_OAUTH_TOKEN
     as the slot main) whose owner in the organization variable
     SYMPHONY_CLAUDE_SETTINGS is the requester by login and by account
     id, since a login passes to whoever takes it after a rename, so a
     slot that kept no account id is never lent; and, only where one of
     those secrets was lent or reaches the repository already, of the two
     variables SYMPHONY_CLAUDE_ACCOUNTS and SYMPHONY_CLAUDE_SETTINGS, so
     the repository's workflows can read the pool. It runs with a third
     token, GH_LEND_TOKEN, with the organization permissions Secrets and
     Variables (write) and Metadata (read), minted only where the
     installation granted them; without it the step says so and nothing
     is touched. It reads the value of SYMPHONY_CLAUDE_SETTINGS, which
     holds the slots' owners, and the records of the requester's secrets
     and the two variables, and never a secret's value, which GitHub
     gives no one. Only a secret or a variable that exists and whose
     visibility is selected is written, and only its list of
     repositories: never a value, a visibility or another person's slot,
     and nothing is created. It comes before the pin, which may wait
     minutes.

settings.json at the repository's root is the list of every setting, in
this order, with its API call and the permission it needs; the tests hold
SETTINGS below to it.

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
GH_TOKEN, GH_ORG_TOKEN, GH_CHECKS_TOKEN and GH_LEND_TOKEN and never printed.
"""

import argparse
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
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
# The token lending only: the requester owns no token of the pool, the
# installation did not grant the organization permissions it needs, or the
# requester owns tokens and none of them could reach the repository.
NONE_OWNED = "none-owned"
NOT_GRANTED = "not-granted"
NONE_LENT = "none-lent"
# The check's pin only: no check run of GitHub Actions came within the
# bound, so the ruleset still takes the check from any source.
NOT_YET = "not-yet"
# The settings, in the order they are applied and reported.
RULESET = "ruleset"
TOGGLES = "toggles"
TOPIC = "topic"
SECRET_SCANNING = "secret_scanning"
PUSH_PROTECTION = "push_protection"
ACTIONS_PULL_REQUESTS = "actions_pull_requests"
CHECK_SOURCE = "check_source"
TOKEN_LENDING = "token_lending"
# The pin comes last, though it belongs to the ruleset, since it may wait
# minutes for the check run and every other setting is applied meanwhile.
SETTINGS = (RULESET, TOGGLES, TOPIC, SECRET_SCANNING, PUSH_PROTECTION, ACTIONS_PULL_REQUESTS, TOKEN_LENDING,
            CHECK_SOURCE)
# The topic an adopted repository carries, which the template's own
# scripts/setup-repo.sh adds too.
TOPIC_NAME = "symphony"
# What GitHub's answer on the workflow permissions may hold for the default
# token's permissions, which the PUT sends back as they were read.
TOKEN_PERMISSIONS = ("read", "write")
# GitHub's answer when the organization or its enterprise holds the setting.
POLICY_CONFLICT = 409
# The check the template's CI reports and its ruleset requires, and GitHub
# Actions' app id, the one source the pin allows for it.
CHECK_NAME = "check"
ACTIONS_APP = 15368
# What GitHub's answer to a ruleset carries that its PUT takes back; the
# rest (id, source, links, dates) is GitHub's own.
RULESET_KEYS = ("name", "target", "enforcement", "conditions", "rules", "bypass_actors")
# GitHub's answer to a pin from an app it does not yet count as one that
# reported the check, and to a request it would take later.
UNPROCESSABLE = 422
TOO_MANY = 429
HEAD = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
# The token pool, as the template's tools/pool.py reads it: the slots'
# secrets, main's among them, and the two variables that list the slots
# and say, per slot, whose token it is.
POOL_SLOTS = tuple(str(slot) for slot in range(1, 33)) + ("main",)
POOL_SECRET = "SYMPHONY_CLAUDE_"
MAIN_SECRET = "CLAUDE_CODE_OAUTH_TOKEN"
POOL_ACCOUNTS = "SYMPHONY_CLAUDE_ACCOUNTS"
POOL_SETTINGS = "SYMPHONY_CLAUDE_SETTINGS"
POOL_VARIABLES = (POOL_ACCOUNTS, POOL_SETTINGS)
LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}")
# A GitHub account id as the workflow passes it: ASCII digits, bounded,
# with no leading zero.
ACCOUNT_ID = re.compile(r"[1-9][0-9]{0,19}")
# What became of one secret or variable: lent here now; left as it is,
# since its visibility is not selected and it reaches this repository
# already (all repositories, or private ones where this one is private or
# internal); not reaching this repository, its visibility not selected and
# not covering it, which the run never changes; or not there.
LENT = "lent"
LEFT = "left"
UNREACHED = "unreached"
MISSING = "missing"


def organization_first(org):
    """The detail of a box ticked only after the organization allowed it:
    the organization's setting stays allowed, and the repositories it makes
    later inherit it, so the pull request says where it is turned off."""
    return ("turned on for the organization first, whose policy held it off, then for this repository; the"
            " organization's setting stays on and its new repositories inherit it, which an owner turns off"
            f" under Workflow permissions at https://github.com/organizations/{org}/settings/actions")
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
        "lending": {LENT: [], LEFT: [], UNREACHED: [], MISSING: [], FAILED: []},
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
    tried anyway. Returns the repository's id, which the token lending
    names it by, or None, and its visibility, which says whether a secret
    shared with the organization's private repositories reaches it, or an
    empty string."""
    try:
        answer = github.call("GET", f"/repos/{repo}")
    except GitHubError:
        report["private"] = None
        return None, ""
    answer = answer if isinstance(answer, dict) else {}
    visibility = answer.get("visibility") if isinstance(answer.get("visibility"), str) else ""
    report["private"] = visibility == "private"
    ident = answer.get("id")
    return (ident if isinstance(ident, int) and not isinstance(ident, bool) and ident > 0 else None), visibility


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
    enterprise did and nothing is written. A refusal from the organization
    keeps the first 409 as the setting's state, with both of GitHub's
    answers; a refusal of the repository's second try, after the
    organization was changed, says the organization was, and is forbidden
    only where it is a 409 again."""
    org = repo.split("/")[0]
    try:
        if tick_box(org_github, f"/orgs/{org}/actions/permissions/workflow"):
            raise GitHubError("the organization allows it already, so its enterprise holds it")
    except GitHubError as said:
        record(report, ACTIONS_PULL_REQUESTS, FORBIDDEN, f"{refused}; for the organization: {said}")
        return
    try:
        tick_box(github, f"/repos/{repo}/actions/permissions/workflow")
        record(report, ACTIONS_PULL_REQUESTS, DONE, organization_first(org))
    except GitHubError as said:
        record(report, ACTIONS_PULL_REQUESTS, FORBIDDEN if said.status == POLICY_CONFLICT else FAILED,
               f"{refused}; allowed for the organization, then for this repository: {said}")


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


@dataclass
class Waiting:
    """How the pin waits for the check run: a clock and a sleep the tests
    replace, so they run at once, the bound and the pause between reads."""
    clock: object = time.monotonic
    sleep: object = time.sleep
    bound: float = 600
    interval: float = 15


WAITING = Waiting()


def worth_waiting(said):
    """Whether a refusal may pass with time: GitHub out of reach or failing,
    a rate limit, or the 422 of an app GitHub does not yet count as one that
    reported the check. Any other 4xx is an answer that stays."""
    status = said.status
    return status is None or status in (UNPROCESSABLE, TOO_MANY) or status >= 500


def actions_reported_check(checks_github, repo, head):
    """Whether GitHub Actions has a check run named "check" on the head
    commit, in any status: a queued one is a report too. An answer with no
    list reads as none yet."""
    answer = checks_github.call("GET", f"/repos/{repo}/commits/{head}/check-runs?check_name={CHECK_NAME}&per_page=100")
    runs = answer.get("check_runs") if isinstance(answer, dict) else None
    return any(isinstance(run, dict) and run.get("name") == CHECK_NAME and isinstance(run.get("app"), dict)
               and run["app"].get("id") == ACTIONS_APP for run in runs or [])


def own_ruleset_id(github, repo, name):
    """The id of the repository's own ruleset of that name. includes_parents
    =false keeps an organization's out of the list, and a source other than
    the repository is passed over too: only its owners edit that one."""
    listed = github.call("GET", f"/repos/{repo}/rulesets?includes_parents=false&per_page=100")
    for item in listed if isinstance(listed, list) else []:
        if (isinstance(item, dict) and item.get("name") == name
                and item.get("source_type", "Repository") == "Repository" and item.get("id")):
            return item["id"]
    raise GitHubError(f"the repository's own rulesets include none named \"{name}\"", 404)


def required_checks_named(ruleset):
    """The ruleset's required checks named "check", as the dicts the PUT
    sends back, so setting a key on one sets it in the body."""
    rules = ruleset.get("rules") if isinstance(ruleset, dict) else None
    found = []
    for rule in rules if isinstance(rules, list) else []:
        if not isinstance(rule, dict) or rule.get("type") != REQUIRED_CHECKS_RULE:
            continue
        parameters = rule.get("parameters")
        checks = parameters.get("required_status_checks") if isinstance(parameters, dict) else None
        found += [check for check in checks if isinstance(check, dict) and check.get("context") == CHECK_NAME] \
            if isinstance(checks, list) else []
    return found


def pin_ruleset(github, repo, name):
    """Put the ruleset back with GitHub Actions as the source of each
    required "check" that names none; (state, detail). A check with a
    source already keeps it."""
    ident = own_ruleset_id(github, repo, name)
    ruleset = github.call("GET", f"/repos/{repo}/rulesets/{ident}")
    checks = required_checks_named(ruleset)
    if not checks:
        return NOT_TRIED, f"the ruleset requires no check named \"{CHECK_NAME}\" any more"
    unpinned = [check for check in checks if not check.get("integration_id")]
    if not unpinned:
        return EXISTS, ""
    for check in unpinned:
        check["integration_id"] = ACTIONS_APP
    github.call("PUT", f"/repos/{repo}/rulesets/{ident}", {key: ruleset[key] for key in RULESET_KEYS if key in ruleset})
    return DONE, ""


def try_pin(github, checks_github, repo, name, head):
    """One round: None while GitHub Actions has not reported the check on
    the head, else what the pin came to."""
    if not actions_reported_check(checks_github, repo, head):
        return None
    return pin_ruleset(github, repo, name)


def pin_check_source(github, checks_github, repo, name, head, report, waiting):
    """Wait within the bound for the check run, then pin; a refusal that may
    pass with time is tried again within the same bound, and the last one
    is what the report keeps when the bound passes, unless a later round
    went through and only found no check run yet. Nothing here stops the
    run: the report says what came of it."""
    deadline = waiting.clock() + waiting.bound
    refused = None
    while True:
        try:
            outcome = try_pin(github, checks_github, repo, name, head)
        except GitHubError as said:
            if not worth_waiting(said):
                record(report, CHECK_SOURCE, FAILED, str(said))
                return
            refused, outcome = said, None
        else:
            refused = None
        if outcome is not None:
            record(report, CHECK_SOURCE, *outcome)
            return
        if waiting.clock() + waiting.interval > deadline:
            break
        waiting.sleep(waiting.interval)
    if refused is not None:
        record(report, CHECK_SOURCE, FAILED, str(refused))
    else:
        minutes = round(waiting.bound / 60)
        record(report, CHECK_SOURCE, NOT_YET, f"GitHub Actions had not reported the check named \"{CHECK_NAME}\""
               f" on the branch symphony/adopt within {minutes} minutes")


def apply_check_source(github, checks_github, repo, head, report, waiting):
    """The pin, where this run created a ruleset that requires the check.
    One the repository had already is left unpinned: the run says it left
    that ruleset as it is, and it may be the person's own, or the template's
    from scripts/setup-repo.sh, which pins it itself."""
    ruleset_state = report["settings"].get(RULESET, {}).get("state")
    if ruleset_state == EXISTS:
        record(report, CHECK_SOURCE, NOT_TRIED, "the ruleset of that name was there already and is left as it is")
    elif ruleset_state != DONE:
        record(report, CHECK_SOURCE, NOT_TRIED, "no ruleset was created")
    elif not report["required_check"]:
        record(report, CHECK_SOURCE, NOT_TRIED, f"the ruleset requires no check named \"{CHECK_NAME}\"")
    elif checks_github is None:
        record(report, CHECK_SOURCE, NOT_TRIED, "no token that reads check runs could be made for this run")
    elif not HEAD.fullmatch(head or ""):
        # A head that is not a sha costs the pin alone, never the settings.
        record(report, CHECK_SOURCE, NOT_TRIED, "the run named no commit to read the check run on")
    else:
        pin_check_source(github, checks_github, repo, report["ruleset_name"], head, report, waiting)


# The run's own reason, for the pull request, where the requester's login
# names slots that kept no account id.
BY_LOGIN_ALONE = ("a token in it names you by login alone, from before the pool kept account ids, and is not lent"
                  " from an issue; press Add Token on the control panel's Tokens page once, which keeps yours")


def secret_of(slot):
    return MAIN_SECRET if slot == "main" else POOL_SECRET + slot


def pool_slots(settings_text):
    """The slots of SYMPHONY_CLAUDE_SETTINGS that are the settings' shape,
    in the pool's order, main last, as (slot, setting) pairs."""
    try:
        data = json.loads(settings_text or "")
    except (ValueError, TypeError):
        return []
    if not isinstance(data, dict):
        return []
    return [(slot, data[slot]) for slot in POOL_SLOTS if isinstance(data.get(slot), dict)]


def owned_by_login(setting, requester):
    """Whether the slot's owner is the requester's login; GitHub's logins
    compare without case."""
    owner = setting.get("owner")
    return isinstance(owner, str) and bool(LOGIN.fullmatch(owner)) and owner.casefold() == requester.casefold()


def kept_account_id(setting):
    """The account id the slot kept, as the template's tools/token_run.py
    writes it (an integer under uid), or None."""
    uid = setting.get("uid")
    return uid if isinstance(uid, int) and not isinstance(uid, bool) and uid > 0 else None


def owned_secrets(settings_text, requester, requester_id):
    """The secrets of the slots whose owner in SYMPHONY_CLAUDE_SETTINGS is
    the requester by login and by account id, in the pool's order, main
    last. A login passes to whoever takes it once an account is renamed or
    deleted, so a slot that kept no account id is never lent, as the
    template's Token run refuses it from an issue. A value that is not the
    settings' shape owns nothing, and neither does a requester whose login
    or account id is not one."""
    if not LOGIN.fullmatch(requester or "") or not ACCOUNT_ID.fullmatch(requester_id or ""):
        return []
    return [secret_of(slot) for slot, setting in pool_slots(settings_text)
            if owned_by_login(setting, requester) and str(kept_account_id(setting)) == requester_id]


def slots_by_login_alone(settings_text, requester):
    """How many slots name the requester's login and kept no account id,
    which the pull request tells the requester how to mend."""
    if not LOGIN.fullmatch(requester or ""):
        return 0
    return sum(1 for _, setting in pool_slots(settings_text)
               if owned_by_login(setting, requester) and kept_account_id(setting) is None)


def reaches(visibility, repo_visibility):
    """Whether an organization secret or variable of that visibility, other
    than selected, reaches a repository of that visibility: all does; private
    reaches the organization's private and internal repositories only, so not
    a public one, nor one whose visibility could not be read."""
    return visibility == "all" or (visibility == "private" and repo_visibility in ("private", "internal"))


def lend_one(lend_github, org, kind, name, repo_id, repo_visibility):
    """Add the repository to one organization secret's or variable's
    selected repositories (kind is secrets or variables): LENT; else, where
    its visibility is not selected, which the run never changes, LEFT where
    it reaches the repository already and UNREACHED where it does not; or
    MISSING where the organization has none of that name, which the run
    never creates. Any other refusal is raised."""
    try:
        item = lend_github.call("GET", f"/orgs/{org}/actions/{kind}/{name}")
    except GitHubError as said:
        if said.status == 404:
            return MISSING
        raise
    visibility = item.get("visibility") if isinstance(item, dict) else None
    if visibility != "selected":
        return LEFT if reaches(visibility, repo_visibility) else UNREACHED
    lend_github.call("PUT", f"/orgs/{org}/actions/{kind}/{name}/repositories/{repo_id}", {})
    return LENT


def lend_each(lend_github, org, kind, names, repo_id, repo_visibility, report):
    """lend_one over names, each on its own; the first refusal's words, or
    an empty string."""
    refused = ""
    for name in names:
        try:
            outcome = lend_one(lend_github, org, kind, name, repo_id, repo_visibility)
        except GitHubError as said:
            outcome, refused = FAILED, refused or f"{name}: {said}"
        report["lending"][outcome].append(name)
    return refused


def read_pool_settings(lend_github, org):
    """The value of the organization's SYMPHONY_CLAUDE_SETTINGS, or None
    where it has none. Any other refusal is raised."""
    try:
        answer = lend_github.call("GET", f"/orgs/{org}/actions/variables/{POOL_SETTINGS}")
    except GitHubError as said:
        if said.status == 404:
            return None
        raise
    value = answer.get("value") if isinstance(answer, dict) else None
    return value if isinstance(value, str) else ""


def secrets_reaching(report):
    """The requester's secrets that this run lent or found reaching the
    repository already: the variables are lent only beside one."""
    return [name for name in report["lending"][LENT] + report["lending"][LEFT] if name not in POOL_VARIABLES]


def apply_token_lending(lend_github, repo, repo_id, repo_visibility, owner_type, requester, requester_id, report):
    """Lend the requester's own tokens of the organization's pool to the
    repository, with the two variables that make the pool readable there.
    Nothing is tried for a personal account's repository, whose secrets are
    its own, or without the requester's account id, and nothing is touched
    without the organization's token; the variables are lent only where one
    of the requester's tokens was lent or reaches the repository already,
    since without one the pool's settings, which name every slot's owner,
    serve this repository nothing."""
    if owner_type != "Organization":
        record(report, TOKEN_LENDING, NOT_TRIED, "the repository belongs to a personal account")
        return
    if not ACCOUNT_ID.fullmatch(requester_id or ""):
        record(report, TOKEN_LENDING, NOT_TRIED, "the requester's account id was not given")
        return
    if lend_github is None:
        record(report, TOKEN_LENDING, NOT_GRANTED)
        return
    if repo_id is None:
        record(report, TOKEN_LENDING, FAILED, "the repository's id could not be read")
        return
    org = repo.split("/")[0]
    try:
        value = read_pool_settings(lend_github, org)
    except GitHubError as said:
        record(report, TOKEN_LENDING, NOT_GRANTED if said.status == 403 else FAILED, str(said))
        return
    owned = owned_secrets(value, requester, requester_id)
    if not owned:
        alone = slots_by_login_alone(value, requester)
        record(report, TOKEN_LENDING, NONE_OWNED, BY_LOGIN_ALONE if alone else "")
        return
    refused = lend_each(lend_github, org, "secrets", owned, repo_id, repo_visibility, report)
    if not secrets_reaching(report):
        record(report, TOKEN_LENDING, FAILED if refused else NONE_LENT, refused)
        return
    refused = lend_each(lend_github, org, "variables", POOL_VARIABLES, repo_id, repo_visibility, report) or refused
    record(report, TOKEN_LENDING, FAILED if refused else DONE, refused)


def apply_settings(github, repo, ruleset, mode, org_github=None, checks_github=None, head=None, waiting=None,
                   lending=None):
    """Every setting, each on its own: one that fails costs itself and
    nothing else. ruleset is the dict, or the one-line reason it could not
    be read. lending is (the organization's token or None, the owner's
    type, the requester's login, the requester's account id); without it
    the lending is not tried."""
    report = new_report(APPLIED, mode)
    repo_id, repo_visibility = read_visibility(github, repo, report)
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
    lend_github, owner_type, requester, requester_id = lending or (None, "", "", "")
    apply_token_lending(lend_github, repo, repo_id, repo_visibility, owner_type, requester, requester_id, report)
    # Only the whole template brings the CI job that reports the check (6).
    if mode == "new":
        apply_check_source(github, checks_github, repo, head, report, waiting or WAITING)
    else:
        record(report, CHECK_SOURCE, NOT_TRIED, "the protocol alone brings no check, and its ruleset requires none")
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
    CHECK_SOURCE: {DONE: "the check's source: GitHub Actions", EXISTS: "the check's source: set already",
                   FAILED: "the check's source: not set", NOT_YET: "the check's source: not set yet",
                   NOT_TRIED: "the check's source: not tried"},
}
# The token lending has one line of two, whatever happened and whoever
# asked: whose tokens, which, how many, whether the requester holds any
# and whether the installation granted the permissions stay out of the
# log, and the reasons go to the pull request alone.
TOKENS_LENT = "token lending: tokens lent"
NO_TOKENS_LENT = "token lending: no tokens lent"


def lending_line(report):
    lent = report.get("lending", {}).get(LENT, [])
    return TOKENS_LENT if any(name not in POOL_VARIABLES for name in lent) else NO_TOKENS_LENT


def log_lines(report):
    for key in SETTINGS:
        setting = report["settings"].get(key)
        if key == TOKEN_LENDING:
            yield lending_line(report)
        elif setting:
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
    # The main App's token with Checks read alone, minted only in mode new;
    # the Setup App holds no Checks permission to read the check run with.
    checks_token = os.environ.get("GH_CHECKS_TOKEN", "")
    checks_github = GitHub(checks_token, transport, options.api) if checks_token else None
    # The Setup App's token with the organization permissions Secrets and
    # Variables (write), minted only for an organization's repository
    # whose installation granted them.
    lend_token = os.environ.get("GH_LEND_TOKEN", "")
    lend_github = GitHub(lend_token, transport, options.api) if lend_token else None
    lending = (lend_github, options.owner_type, options.requester, options.requester_id)
    try:
        report = apply_settings(github, options.repo, ruleset, options.mode, org_github, checks_github, options.head,
                                lending=lending)
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
    print(NO_TOKENS_LENT)
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Apply the template's repository settings as the Setup App.")
    commands = parser.add_subparsers(dest="command", required=True)

    applying = commands.add_parser("apply", help="apply the settings with the token in GH_TOKEN and write a report")
    applying.add_argument("--repo", required=True, help="the repository as OWNER/NAME")
    applying.add_argument("--ruleset", required=True, help="the template's docs/setup/ruleset-main.json")
    applying.add_argument("--mode", required=True, choices=("new", "existing"))
    applying.add_argument("--report", required=True, help="where to write the report")
    applying.add_argument("--head", default="", help="the sha of the branch symphony/adopt the run pushed")
    applying.add_argument("--owner-type", default="", help="the repository owner's type, Organization or User")
    applying.add_argument("--requester", default="", help="the login of the administrator who asked")
    applying.add_argument("--requester-id", default="", help="the account id of the administrator who asked")
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
