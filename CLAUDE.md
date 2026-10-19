# symphony-start

This repository is the public front door to the Symphony template, OpenSpineConsortium/symphony-template, which stays internal to its enterprise. A person installs the App, whose Setup URL sends them on to the Setup App's install page, whose Setup URL sends them to the form .github/ISSUE_TEMPLATE/adopt.yml with the installation's number filled in and the kind left to the run, so one press of Create is the request, for the repository the form names (filled in by the Symphony browser extension's button, which carries it through GitHub's state parameter on the install link) or else the newest repository the installation reaches with no adoption yet, one per press (scripts/resolve.py, by id); or they open the form and name the repository; .github/workflows/adopt.yml checks it and calls .github/workflows/adopt-run.yml, which opens a pull request in their own repository, as the Symphony App, with the template or only its claim protocol, within about two minutes. Installing the App alone asks for nothing: the install's redirect lands on the form, and the press is the request. scripts/adopt.py does the reading and the copying. README.md says what each kind adds, what is shared and the owner's one-time setup.

## What must hold

- The template's repository is never exposed: no step prints its files, its history or its other branches, and its token is read-only and revoked right after the one checkout that uses it. Its files reach only the pull request in the requester's repository.
- An issue here is written by anyone, so everything in it is data. Values reach a shell step only through env:, never through an expression inside run:, and scripts/adopt.py parse refuses anything the form would not write; a message posted back never quotes the issue. A repository given by ids, from a form that came from the install, may be private and was named on no issue: its name reaches no log, no run input, no step output, no job summary and no issue; the run resolves the ids with a metadata-only token, masks the name, its owner's, the default branch's and the requester's login before anything prints them, and answers the issue with "your repository". A guessed installation number learns nothing: not the App's, several repositories and not an administrator are one answer.
- Nothing lands in anyone's repository but a pull request they review, apart from what the run makes at once and the README says it makes: the board's labels, the branch symphony/adopt, in a repository with no commit yet its first commit, the README.md holding its name that GitHub's own "Add a README file" makes, in mode new the issue "Set up this project" and, with the Setup App, the settings and the topic symphony. Mode existing never overwrites a file of theirs; LICENSE is never copied in either mode. The installation's path offers nothing to a repository that opted out (`off` in .github/symphony-adopt), and the run refuses the front door's own repositories.
- What is shared is aggregates only, on by default and said so plainly in the form's opt-out box, the README and the pull request, with one switch off: the file .github/symphony-metrics.
- An adoption asked on the form needs both Apps installed on the repository: SymphonyBoard opens the pull request, and Symphony Setup, whose installation is the person's consent, applies the settings and stays installed, acting only during an adoption run, until the person uninstalls it; the run refuses with the Setup App's install link when it is not there, on both of the form's paths.

## Checks

Run `bash scripts/check.sh` before opening or updating a pull request. CI runs the same script as the job named "check". It needs Python 3.12 (`PYTHON` names another interpreter). The tests in tests/test_real_template.py skip unless SDLC_TEMPLATE names a checkout of the template, which CI cannot read, so whoever can runs `SDLC_TEMPLATE=/path/to/symphony-template bash scripts/check.sh` before a change to scripts/adopt.py merges.

## Writing

- Plain prose that says why, in comments, commit messages, pull requests and documents alike; what the code does is read from the code.
- Short functions; names that read as English.
- No emoji. ASCII and LF in every file, each ending with a newline.
- No new dependencies: Python 3.12 or later with its standard library, bash, gh, and GitHub's own actions plus actions/create-github-app-token@v1, pinned to a major tag. Tests use unittest. A proposal to add one is an issue first.
- Nothing refers to a file that does not exist.
- Never a real token or key in any file, test or example.

## Pushing

main takes only pull requests: never push to main and never force-push it. Work on a branch of your own and open a pull request from it.
