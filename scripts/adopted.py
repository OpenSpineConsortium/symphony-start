#!/usr/bin/env python3
"""Say whether a repository has an adoption already, by the one rule.

The installation's path of the form passes over a repository whose
default branch holds docs/agents/PROTOCOL.md, which every adoption from
this front door brings, in either kind, and every copy made with "Use
this template" carries (sweep.unadopted, asked by scripts/resolve.py). A
repository named on the form reaches .github/workflows/adopt-run.yml by
no such check, and a second adoption would put the template's files over
the ones the repository has made its own since (its CLAUDE.md and
checkpoint, its README, its goal and memory, its metrics switch), or, for
the protocol alone, bring back what it has taken out, so the run asks
this before it reads the kind or stages a file, on both paths: one rule,
sweep.is_adopted itself, for the two ways a request arrives.
scripts/adopt.py apply refuses an adoption that could not write that
file, so no adoption is made that the rule misses.

Exit 0 when the repository has no adoption yet, 3 when it has one, which
the run answers with one message that names nothing of it, 1 when GitHub
could not be asked, and 2 when GH_TOKEN is not set or the name is missing
or not one scripts/adopt.py name would print. With --answer it asks
nothing and prints that message, ANSWER, the one place its words are
kept, which the run answers with on both of the form's paths. Nothing
printed names the repository, since the run's log is public and a
repository given by ids may be private. GH_TOKEN is an installation token
for the repository that reads its contents, and it is never printed.
Python 3.12 or later, standard library only.
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adopt  # noqa: E402
import sweep  # noqa: E402

ADOPTED = 3
# The answer to a request for a repository adopted already, on both paths:
# it names nothing of the repository, holds for either kind it took, and
# says what to do instead.
ANSWER = (
    "Nothing was done: the repository is adopted already. Its default branch holds docs/agents/PROTOCOL.md, which"
    " every adoption from this front door brings, of either kind, and every copy made with \"Use this template\""
    " carries, and the form adopts a repository once, since a second adoption would put the template's files over"
    " the ones the repository has made its own since, or, for the protocol alone, bring back what it has taken out."
    " Later releases of the claim protocol reach it by pull request, from its own .github/workflows/protocol.yml where"
    " it has one, or from a clone of the public OpenSpineConsortium/symphony-protocol with its scripts/vendor.py; what"
    " the adoption's pull request did not write, its notes say how to add. To adopt it again, as the other kind or"
    " with what was left out, first revert that adoption's merge on the default branch, so docs/agents/PROTOCOL.md is"
    " gone from it, or rename that file if it is one of your own and not this protocol, then ask again. Symphony"
    " Setup, if you installed it, did nothing here; it stays installed, acting only during an"
    " adoption run, and you can uninstall it at any time from the repository's or the"
    " organization's Settings, GitHub Apps. For the repository's page to"
    " say it is adopted, and the Symphony browser extension's button to read Ready for Symphony, add the topic"
    " symphony with the gear beside About there, where it is missing. To adopt another repository, open a new request"
    " with the form naming that one; this one is closed."
)


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Whether a repository has an adoption already, by the one rule.")
    parser.add_argument("repository", nargs="?", help="OWNER/NAME, as scripts/adopt.py name printed it")
    parser.add_argument("--answer", action="store_true",
                        help="print the answer to a request for a repository adopted already, and ask nothing")
    parser.add_argument("--api", default=sweep.API, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv=None, transport=sweep.urllib_transport):
    options = parse_args(argv)
    if options.answer:
        print(ANSWER)
        return 0
    if options.repository is None:
        print("adopted: the repository must be OWNER/NAME, as scripts/adopt.py name prints it", file=sys.stderr)
        return 2
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        print("adopted: GH_TOKEN is not set", file=sys.stderr)
        return 2
    try:
        adopt.parse_repository(options.repository)
    except adopt.FormError:
        print("adopted: the repository must be OWNER/NAME, as scripts/adopt.py name prints it", file=sys.stderr)
        return 2
    github = sweep.GitHub(token, transport, options.api)
    try:
        adopted = sweep.is_adopted(github, {"full_name": options.repository})
    except sweep.GitHubError as refusal:
        print(f"adopted: GitHub could not be asked ({refusal})", file=sys.stderr)
        return 1
    print("the repository is adopted already" if adopted else "the repository has no adoption yet")
    return ADOPTED if adopted else 0


if __name__ == "__main__":
    sys.exit(main())
