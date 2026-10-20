#!/usr/bin/env python3
"""Turn the installation a form carried into the repositories to adopt.

The install ends on the adoption form with the installation's number
filled in, and the person presses Create: .github/workflows/adopt.yml runs
this to learn which repositories that means, all by id, so that the public
run never holds a name it could print. The number may be the App's own
installation or the Setup App's, since both Apps send the person to the
form; a Setup App installation stands for the App's installation on the
same account, narrowed to the repositories the Setup App was given.

Of the installation's repositories, those with no adoption yet (the
rules in sweep.py: a commit, no branch symphony/adopt, no
docs/agents/PROTOCOL.md, no opt-out; or no commit at all, an empty
repository, whose first commit the run makes) that the issue's author
administers are the ones to adopt, newest first, at most LIMIT of them:
one, the newest, so that one press never reaches further than one
repository (on 2026-10-11 an installation on all of an account's
repositories, with "Merge the pull request for me" ticked, merged the
adoption into eight before the run was cancelled); the person presses
Create again for the next, or names a repository on the form. With
SETUP_JWT set, the Setup App is a preference among those candidates and
never a requirement: SymphonyBoard alone adopts and applies the settings
(the owner's rule of 2026-10-20), and Symphony Setup is only the fallback
for an installation of SymphonyBoard that cannot accept Administration.
Where the Setup App is installed on some of the candidates, asked by id
with that App's JWT, the newest of those is chosen, since installing it
there was the person's choice of repository, so an account with the App
on all its repositories and the Setup App on one gets that one; where it
is on none of them, the newest candidate is chosen. Without SETUP_JWT
there is no preference. The file --out
gets installation_id, repository_ids (a JSON list) and count, as KEY=value
lines for $GITHUB_OUTPUT; stdout says how many and nothing else.

Exit 0 with something to adopt; 3 when there is nothing (an installation
that is neither App's, no repository with no adoption yet, or none the
author administers), which the workflow
answers with one message whatever the reason; 4 when the App's own record
cannot be read, which is the front door's owner's problem; 1 when GitHub
could not be asked. APP_JWT is the App's JWT (scripts/jwt.sh); SETUP_JWT,
when set, the Setup App's. Python 3.12 or later, standard library only.
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sweep  # noqa: E402

NOTHING = 3
BROKEN = 4
LIMIT = 1


class Nothing(Exception):
    """No repository to adopt from this number, for one of the reasons the
    workflow answers alike."""


def mint(app, installation_id, permissions):
    """A client on the installation's token, with these permissions."""
    answer = app.call("POST", f"/app/installations/{installation_id}/access_tokens", {"permissions": permissions})
    token = answer.get("token") if isinstance(answer, dict) else None
    if not token:
        raise sweep.GitHubError("GitHub's answer held no token")
    return app.with_token(token)


def installation_of(app, installation_id):
    """This App's installation of that id, or None when GitHub does not
    know the id as this App's."""
    try:
        answer = app.call("GET", f"/app/installations/{installation_id}")
    except sweep.GitHubError as refusal:
        if refusal.status == 404:
            return None
        raise
    return answer if isinstance(answer, dict) and "id" in answer else None


def repositories_of(github):
    """The repositories the installation's token reaches, marked for the
    checks by id."""
    found = github.pages(f"/installation/repositories?per_page={sweep.PER_PAGE}", key="repositories")
    return [dict(item, by_id=True) for item in found if isinstance(item, dict) and "id" in item]


def installation_on_account(app, account_id):
    """The App's installation on the account of that id, or None."""
    for installation in app.pages(f"/app/installations?per_page={sweep.PER_PAGE}"):
        account = installation.get("account") if isinstance(installation, dict) else None
        if isinstance(account, dict) and account.get("id") == account_id:
            return installation
    return None


def administered(github, repositories, author):
    """The repositories among these the author administers; a repository
    that refuses the question is not theirs."""
    kept = []
    for repository in repositories:
        try:
            answer = github.call("GET", f"/repositories/{repository['id']}/collaborators/{author}/permission")
        except sweep.GitHubError as refusal:
            if refusal.status in (403, 404):
                continue
            raise
        if isinstance(answer, dict) and answer.get("permission") == "admin":
            kept.append(repository)
    return kept


def reached_by_the_setup_app(setup, repositories):
    """The repositories among these the Setup App is installed on, asked
    by id with its JWT: 200 is its installation there, 404 that it has
    none, and any other answer is GitHub's to explain."""
    kept = []
    for repository in repositories:
        try:
            setup.call("GET", f"/repositories/{repository['id']}/installation")
        except sweep.GitHubError as refusal:
            if refusal.status == 404:
                continue
            raise
        kept.append(repository)
    return kept


def preferred(setup, candidates):
    """The candidates the Setup App is installed on where it is on any of
    them, else all of them: a preference, never a filter, so a person who
    never installed the Setup App still adopts."""
    if setup is None or not candidates:
        return candidates
    return reached_by_the_setup_app(setup, candidates) or candidates


def only_the_setup_apps(setup, installation):
    """The ids of the repositories a Setup App installation was given, or
    None when it was given them all."""
    if installation.get("repository_selection") != "selected":
        return None
    github = mint(setup, installation["id"], {"metadata": "read"})
    try:
        return {repository["id"] for repository in repositories_of(github)}
    finally:
        sweep.revoke(github)


def resolve(app, setup, installation_id, author):
    """(the App's installation id, the repositories to adopt), or Nothing."""
    found, only = installation_of(app, installation_id), None
    if found is None and setup is not None:
        theirs = installation_of(setup, installation_id)
        if theirs is None:
            raise Nothing
        account = theirs.get("account") if isinstance(theirs.get("account"), dict) else {}
        found = installation_on_account(app, account.get("id"))
        if found is None:
            raise Nothing
        only = only_the_setup_apps(setup, theirs)
    if found is None:
        raise Nothing
    github = mint(app, found["id"], {"contents": "read"})
    try:
        repositories = repositories_of(github)
        if only is not None:
            repositories = [repository for repository in repositories if repository["id"] in only]
        mine = preferred(setup, administered(github, sweep.unadopted(github, repositories), author))
    finally:
        sweep.revoke(github)
    if not mine:
        raise Nothing
    mine.sort(key=sweep.created_at, reverse=True)
    return found["id"], mine[:LIMIT]


def parse_args(argv):
    parser = argparse.ArgumentParser(description="The repositories an installation's number means.")
    parser.add_argument("--installation", required=True, help="the number the form carried")
    parser.add_argument("--author", required=True, help="the issue's author, who must administer a repository")
    parser.add_argument("--out", required=True, help="where to write the KEY=value lines")
    parser.add_argument("--api", default=sweep.API, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv=None, transport=sweep.urllib_transport):
    options = parse_args(argv)
    if not options.installation.isdigit():
        print("resolve: the installation must be a number", file=sys.stderr)
        return 2
    jwt = os.environ.get("APP_JWT", "")
    if not jwt:
        print("resolve: APP_JWT is not set", file=sys.stderr)
        return 2
    app = sweep.GitHub(jwt, transport, options.api)
    setup_jwt = os.environ.get("SETUP_JWT", "")
    setup = sweep.GitHub(setup_jwt, transport, options.api) if setup_jwt else None
    try:
        app.call("GET", "/app")
    except sweep.GitHubError as refusal:
        print(f"resolve: the App could not be read ({refusal})", file=sys.stderr)
        return BROKEN
    try:
        installation_id, repositories = resolve(app, setup, options.installation, options.author)
    except Nothing:
        return NOTHING
    except sweep.GitHubError as refusal:
        print(f"resolve: GitHub could not be asked ({refusal})", file=sys.stderr)
        return 1
    ids = [repository["id"] for repository in repositories]
    Path(options.out).write_text(
        f"installation_id={installation_id}\nrepository_ids={json.dumps(ids)}\ncount={len(ids)}\n", encoding="utf-8")
    print(f"the installation reaches {len(ids)} {'repository' if len(ids) == 1 else 'repositories'} to adopt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
