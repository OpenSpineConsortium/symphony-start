#!/usr/bin/env python3
"""Adopt the Symphony template into a repository, from the form.

.github/workflows/adopt.yml runs parse; .github/workflows/adopt-run.yml,
which it calls, runs name, apply, body and labels, one subcommand per
step:

  parse  reads the issue the adoption form made and prints its fields as
         KEY=value lines for $GITHUB_OUTPUT. Anyone can open an issue, so
         anything the form would not have written is refused, with one
         line of reason that never quotes the issue back. The repository
         is named, or the installation GitHub filled in when the person
         came from installing the App is given, and the workflow resolves
         the installation's one repository itself.
  apply  copies the template into the checkout of the person's repository
         and writes a manifest of what it added, replaced, kept, merged
         and skipped. Mode new is the whole template, as "Use this
         template" makes it: the tree is staged, the template's own
         tools/template_init.py fills it there, so the fill has one
         source, and a file the repository has already is replaced. Mode
         existing is the protocol only, the files the template's guide
         for a repository it did not make has a person copy by hand, so
         the template's tests, checks and documents never meet the
         person's; nothing there is overwritten, a workflow and every
         script it runs, the modules of the template its script imports
         among them, come together or not at all, and stay out with the
         vendored library when they import it, the metrics workflow comes
         only with its switch, a file the repository ignores is never
         written, the protocol's text is the library's spec when
         --protocol-spec names it, CLAUDE.md gains one section once that
         text has landed, and .claude/settings.json the keys that enable
         the symphony plugin. In either mode the switch the adoption
         writes says off where one of the repository's own says off
         already, under its name or its old one, and an adoption that
         could not write docs/agents/PROTOCOL.md is refused before
         anything is written, with exit status 3: every session reads the
         protocol there, and the front door knows an adoption by that
         file.
  body   prints the pull request's text from the manifest, or with
         --title its title; with --settings, the report scripts/setup.py
         wrote is rendered into it, so the pull request says which of
         the repository's settings the Setup App applied in the same run,
         or why none was, and the next steps follow from that.
  labels prints the board's labels, read from the template's own list.
  name   checks a repository's name the way parse does, once the run
         holds it, typed on the form or resolved from the ids the form
         carried, and prints it as KEY=value lines.

LICENSE is never copied: licensing the person's project is their
decision. A link in the template is never followed and a path of the
target that a link would carry out of the repository, or into its .git,
is never written. Python 3.12 or later, standard library only.
"""

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path, PurePosixPath

MANIFEST_SCHEMA = "sdlc-adopt/1"

# The form as .github/ISSUE_TEMPLATE/adopt.yml words it: each field's
# label is a "### " heading of the issue's body, followed by its value.
# tests/test_form.py holds the two files to the same words.
FIELD_INSTALLATION = "Installation"
FIELD_REPOSITORY = "Repository"
FIELD_KIND = "Kind"
FIELD_MERGE = "Merge"
FIELD_OPTIONS = "Options"
FIELDS = (FIELD_INSTALLATION, FIELD_REPOSITORY, FIELD_KIND, FIELD_MERGE, FIELD_OPTIONS)
# What GitHub writes under an optional field left empty.
NO_RESPONSE = "_No response_"
# The kind: Auto, the default, is read from the repository by the run.
KINDS = {
    "Auto: read the repository (empty gets the whole template, one with files gets the protocol only)": "read",
    "Whole template: make this repository a Claude project": "new",
    "Protocol only: add the coordination protocol to the code I have": "existing",
}
# The merge choice is a dropdown with a default, since a checkbox has
# none: the run merges unless the person asks to review first. The one
# box: sharing is on unless the person says otherwise.
MERGE_FOR_ME = "Merge the pull request for me"
REVIEW_FIRST = "Leave the pull request open for me to review"
MERGES = {MERGE_FOR_ME: "true", REVIEW_FIRST: "false"}
OPT_OUT_OF_SHARING = ("Do not share anonymous aggregates (counts, durations and rates of the protocol at work, never"
                      " code, text or names; the switch is .github/symphony-metrics)")
OPTIONS = (OPT_OUT_OF_SHARING,)
HEADING = re.compile(r"### (.+)")
BOX = re.compile(r"- \[([ xX])\] (.+)")

REPOSITORY = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}")
INSTALLATION = re.compile(r"[0-9]{1,20}")
LOGIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}")
OWNER_TYPES = ("User", "Organization")
# The front door and the template take no adoption of themselves; their
# names before the Symphony rename stay here because GitHub redirects a
# typed old name to the renamed repository.
OWN_REPOSITORIES = ("openspineconsortium/symphony-template", "openspineconsortium/symphony-start",
                    "openspineconsortium/sdlc-template", "openspineconsortium/sdlc-start")

# Never copied from the template: git's own folder, Python's caches.
SKIPPED_NAMES = {".git", "__pycache__"}
INIT_SCRIPT = "tools/template_init.py"

# Mode existing: the protocol and nothing else.
PROTOCOL_TREE = "tools/sdlc_protocol"
# The vendored library's package, as a script imports it.
LIBRARY_PACKAGE = PurePosixPath(PROTOCOL_TREE).name
PROTOCOL_FILES = (
    "tools/VENDORED",
    "tools/board.py",
    ".github/workflows/board.yml",
    ".github/workflows/tidy.yml",
    "docs/agents/claims/README.md",
)
PROTOCOL_TEXT = "docs/agents/PROTOCOL.md"
VENDORED = "tools/VENDORED"
BOARD_WORKFLOW = ".github/workflows/board.yml"
BOARD_SCRIPT = "tools/board.py"
# The template's field metrics, copied in both modes once it carries the
# workflow and its script.
METRICS_WORKFLOW = ".github/workflows/metrics.yml"
METRICS_SCRIPT = "tools/metrics.py"
# A key of METRICS.json that the template's script writes since it counts
# the work by setting, and never wrote before. A repository keeps the script
# it was adopted with, since no later change of the template reaches it, so
# the pull request says the counts are sorted by who opened each pull request
# and which session made it only where the script that landed holds the key.
BREAKDOWN_KEY = b"by_setting"
SWITCH = ".github/symphony-metrics"
# The switch under its name before the rename to Symphony, which a
# repository adopted before it carries and the template's tools/metrics.py
# still reads: an off there is the person's word as much as one in SWITCH,
# and the form's default never lifts it.
OLD_SWITCH = ".github/sdlc-metrics"
SWITCHES = (SWITCH, OLD_SWITCH)
# Mode existing brings a workflow and the scripts it runs together or not
# at all: the template's workflow would run a script of theirs by the same
# name, with contents: write, and theirs would run the template's. Those
# scripts are the one the workflow runs and every module of the template
# that one imports, and theirs in turn, read from the template's files at
# run time (unit_files), since the template's script may come to import a
# module the front door has never heard of, and the workflow would then
# fail at its first run. A file of theirs holding the template's bytes, as
# a copy from the same release does, stands in the way of nothing. That
# reaches the template's modules alone: a file of theirs named like one of
# Python's own modules is still what the scripts import in its place. The
# vendored library and its record are one unit the same way, so a release's
# modules never lie next to an older copy's, and a workflow whose scripts
# import the library stays out with it; the metrics workflow stays out with
# its switch too, which it reads as on where there is none.
# The Token workflow mints a Claude token for the control panel's Tokens
# page in the repository itself, so a repository adopted for the protocol
# alone needs no other repository of its owner's to sign in through (the
# owner, 2026-10-19). Its script puts the template's scripts folder on its
# path after its own, so its modules are looked for in both (SEARCH).
TOKEN_WORKFLOW = ".github/workflows/token.yml"
TOKEN_SCRIPT = "tools/token_run.py"
UNITS = (
    ("the board's workflow and its script", BOARD_WORKFLOW, BOARD_SCRIPT),
    ("the metrics workflow and the scripts it runs", METRICS_WORKFLOW, METRICS_SCRIPT),
    ("the Token workflow and the scripts it runs", TOKEN_WORKFLOW, TOKEN_SCRIPT),
)
# Where a unit's script finds the template's modules, every one it imports
# and every one those import, in Python's order, for a script that puts
# more than its own folder on its path: tools/token_run.py adds scripts/.
SEARCH = {TOKEN_SCRIPT: ("tools", "scripts")}
LIBRARY_UNIT = "the vendored library and its record"
# A file the repository ignores is committed only by force, and git then
# replaces each person's own copy of it on their next pull without a word.
IGNORED_WHY = "ignored by this repository, so each person's own copy would be replaced on pull"
CLAUDE_MD = "CLAUDE.md"
SETTINGS = ".claude/settings.json"
# Team mode's labels need the template's other workflows, which mode
# existing does not bring.
TEAM_LABELS = ("epic", "blocked")

# The section a repository's CLAUDE.md gains, in the words of the
# template's guide: the @ line imports the protocol into every session.
CLAUDE_SECTION = (
    "## How work is claimed\n"
    "\n"
    "@docs/agents/PROTOCOL.md\n"
    "\n"
    "Before any work: fetch, read the board with `git fetch origin board && git show origin/board:STATE.md`,"
    " and check the claim on the issue you mean to take. One issue, one branch `claude/<issue>`, one pull"
    " request. Never push to the default branch or to another account's claim branch.\n"
)
CLAUDE_IMPORT = "@docs/agents/PROTOCOL.md"
# The project preset of OpenSpineConsortium/symphony-marketplace's README.
MARKETPLACE_NAME = "symphony-marketplace"
MARKETPLACE = {
    "source": {"source": "github", "repo": "OpenSpineConsortium/symphony-marketplace"},
    "autoUpdate": True,
}
PLUGIN = "symphony@symphony-marketplace"

FRONT_DOOR = "https://github.com/OpenSpineConsortium/symphony-start"

# The Setup App: a second App, holding Administration, which the person
# installs on the repository so the run applies the template's
# repository settings (scripts/setup.py), and which stays installed,
# acting only during an adoption run, until the person uninstalls it. Its
# report says what was done, and the pull request's text follows it.
SETUP_APP = "Symphony Setup"
SETUP_SCHEMA = "sdlc-setup/1"
SETUP_OUTCOMES = ("applied", "not-set-up", "not-installed", "front-door-broken", "not-reported")
SETUP_SCRIPT = "scripts/setup-repo.sh"
THE_SETTINGS = ("the default branch's ruleset", "delete-on-merge and auto-merge", "the topic symphony",
                "secret scanning with push protection")
# Mode new adds the box under Workflow permissions that lets the whole
# template's workflows open their pull requests with GitHub's own token;
# the protocol alone brings none of them, so scripts/setup.py leaves an
# existing repository's box as it is.
ACTIONS_SETTING = "letting GitHub Actions create and approve pull requests"
ACTIONS_LABEL = "Allow GitHub Actions to create and approve pull requests"
# Mode new's ruleset requires the check named "check"; scripts/setup.py
# then pins it to GitHub Actions, which GitHub takes only once GitHub
# Actions has reported it, so the pin may be left for the person.
CHECK_SOURCE = "check_source"
# For an organization's repository the Setup App lends it the requester's
# own Claude tokens of the organization's pool and the pool's two
# variables, where its installation granted the organization permissions
# Secrets and Variables.
TOKEN_LENDING = "token_lending"
POOL_VARIABLES = ("SYMPHONY_CLAUDE_ACCOUNTS", "SYMPHONY_CLAUDE_SETTINGS")
# The box's API path, which the template's scripts/setup-repo.sh calls since
# it ticks the box too, and never called before. The run copies the
# template's default branch and a repository keeps the script it was
# adopted with, so the pull request names the box among the script's steps
# only where the script that landed calls it.
ACTIONS_PATH = b"actions/permissions/workflow"
# apply's exit status for an adoption it refuses, which the run answers as
# a refusal on the request rather than as a failure of its own.
EXIT_REFUSED = 3


class FormError(Exception):
    """The issue is not one the form writes; one line that quotes nothing of it."""


class AdoptError(Exception):
    """Something apply or labels cannot do; one line."""


class Refusal(AdoptError):
    """An adoption apply will not make in this repository, refused before
    anything is written; one line that names nothing of the repository."""


# --- parse ------------------------------------------------------------------------


def form_sections(body):
    """Each "### " heading of the body with the text under it, stripped."""
    sections, current = {}, None
    for line in body.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        heading = HEADING.fullmatch(line.rstrip())
        if heading:
            current = heading.group(1).strip()
            if current in sections:
                raise FormError("a field appears twice, so the issue is not the adoption form's")
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def parse_repository(value):
    """OWNER/NAME as GitHub allows it, or FormError."""
    shape = "the repository must be written as OWNER/NAME, such as octo-org/my-project, with no link and no spaces"
    if not REPOSITORY.fullmatch(value):
        raise FormError(shape)
    owner, name = value.split("/")
    if owner.startswith("-") or name in (".", "..") or name.lower().endswith(".git"):
        raise FormError(shape)
    if value.lower() in OWN_REPOSITORIES:
        raise FormError("that repository is part of Symphony itself and takes no adoption")
    return owner, name


def parse_installation(value):
    """The installation's number as GitHub fills it in, or FormError."""
    if not INSTALLATION.fullmatch(value):
        raise FormError("the installation must be the number GitHub fills in when you come from installing the App;"
                        " leave it empty when you name the repository")
    return value


def given(value):
    """An optional field's value, empty when the person left it so."""
    return "" if value == NO_RESPONSE else value


def ticked_options(value):
    """The boxes ticked under Options, as the form's labels; a line that is
    not one of the form's boxes is a FormError, since GitHub writes each
    box, ticked or not, and nothing else."""
    ticked = set()
    for line in value.split("\n"):
        if not line.strip():
            continue
        found = BOX.fullmatch(line.strip())
        if not found or found.group(2).strip() not in OPTIONS:
            raise FormError("the field Options holds something the form does not offer")
        if found.group(1) != " ":
            ticked.add(found.group(2).strip())
    return ticked


def parse_form(body):
    """The form's fields: repository, owner and name (empty when only the
    installation was given), installation (empty when the repository was
    named without it), mode (read, the default, which the run reads from
    the tree), metrics (off when the opt-out box is ticked) and merge
    (true unless the person chose to review the pull request first)."""
    sections = form_sections(body)
    if set(sections) != set(FIELDS):
        raise FormError("the issue is not the adoption form's")
    named, installed = given(sections[FIELD_REPOSITORY]), given(sections[FIELD_INSTALLATION])
    if not named and not installed:
        raise FormError("the repository must be named as OWNER/NAME, unless you come to the form from installing the"
                        " App, which fills in the installation")
    installation = parse_installation(installed) if installed else ""
    owner, name = parse_repository(named) if named else ("", "")
    kind = given(sections[FIELD_KIND])
    if kind and kind not in KINDS:
        raise FormError("the field Kind holds none of the form's options")
    mode = KINDS[kind] if kind else "read"
    choice = given(sections[FIELD_MERGE])
    if choice and choice not in MERGES:
        raise FormError("the field Merge holds none of the form's options")
    merge = MERGES[choice] if choice else "true"
    ticked = ticked_options(sections[FIELD_OPTIONS])
    metrics = "off" if OPT_OUT_OF_SHARING in ticked else "on"
    repository = f"{owner}/{name}" if named else ""
    return {"repository": repository, "owner": owner, "name": name, "installation": installation,
            "mode": mode, "metrics": metrics, "merge": merge}


def command_name(options):
    """The repository's name, typed on the form or resolved from the ids
    it carried, checked as parse checks the form's and printed in parse's
    shape for the workflow's environment."""
    try:
        owner, name = parse_repository(options.repository)
    except FormError as problem:
        print(problem, file=sys.stderr)
        return 1
    for key, value in (("repository", f"{owner}/{name}"), ("owner", owner), ("name", name)):
        print(f"{key}={value}")
    return 0


def command_parse(options):
    try:
        if options.body in (None, "-"):
            body = sys.stdin.read()
        else:
            body = Path(options.body).read_text(encoding="utf-8")
        fields = parse_form(body)
    except (OSError, UnicodeDecodeError):
        print("the issue's body could not be read", file=sys.stderr)
        return 1
    except FormError as problem:
        print(problem, file=sys.stderr)
        return 1
    for key, value in fields.items():
        print(f"{key}={value}")
    return 0


# --- the template's tree ----------------------------------------------------------


def relative(path, root):
    return path.relative_to(root).as_posix()


def template_files(template):
    """The template's regular files and the links met on the way, both as
    relative paths. A link is never followed, whether it leads out of the
    template or not: the copy holds files only."""
    files, links = [], []
    for folder, dirs, names in os.walk(template):
        here = Path(folder)
        for name in list(dirs):
            if name in SKIPPED_NAMES or (here / name).is_symlink():
                dirs.remove(name)
                if name not in SKIPPED_NAMES:
                    links.append(relative(here / name, template))
        for name in names:
            path = here / name
            if name in SKIPPED_NAMES:
                continue
            if path.is_symlink():
                links.append(relative(path, template))
            elif path.is_file():
                files.append(relative(path, template))
    return sorted(files), sorted(links)


def is_license(rel):
    """A top-level LICENSE, LICENSE.md and the like."""
    parts = PurePosixPath(rel).parts
    return len(parts) == 1 and parts[0].upper().startswith("LICENSE")


def stage(template, staging, files):
    """Copy the files into staging, permission bits included, so a script
    stays executable."""
    for rel in files:
        if is_license(rel):
            continue
        destination = staging / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(template / rel, destination)


def write_event(path, repo, owner_type, creator):
    """The event a "Use this template" push would carry, as far as
    template_init reads it: whose repository it is and who made the copy,
    so .github/CODEOWNERS names the person in an organization's copy."""
    event = {
        "repository": {"full_name": repo, "owner": {"type": owner_type}},
        "sender": {"type": "User", "login": creator},
    }
    path.write_text(json.dumps(event) + "\n", encoding="utf-8")


def init_script(template):
    script = template / INIT_SCRIPT
    if script.is_symlink() or not script.is_file():
        raise AdoptError(f"the template has no {INIT_SCRIPT}")
    return script


def run_template_init(template, staging, event, repo, default_branch):
    """Fill the staged tree with the template's own init, which also removes
    its marker folder and blanks the checkpoint. It runs without a token, so
    it makes no label and opens no issue; its output stays out of the log."""
    command = [
        sys.executable, "-B", str(init_script(template)),
        "--repo", repo, "--default-branch", default_branch,
        "--root", str(staging), "--event", str(event),
    ]
    env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_EVENT_PATH")}
    done = subprocess.run(command, cwd=staging.parent, env=env, capture_output=True, text=True)
    if done.returncode != 0:
        last = (done.stderr.strip().splitlines() or ["no message"])[-1]
        raise AdoptError(f"the template's {INIT_SCRIPT} failed: {last}")


def read_plan(staging):
    """Every staged file as relative path -> (bytes, executable)."""
    files, _ = template_files(staging)
    return {rel: ((staging / rel).read_bytes(), bool((staging / rel).stat().st_mode & 0o111)) for rel in files}


def read_spec(options):
    """The library's spec/PROTOCOL.md as a plan entry when --protocol-spec
    names it, else None. The vendored copy never carries the spec, so the
    workflow clones the public library at the commit tools/VENDORED names
    and passes the file; without it mode existing falls back to the
    template's own page, which names files only a copy of the template
    has, and the body says so."""
    if options.protocol_spec is None:
        return None
    path = Path(options.protocol_spec)
    if path.is_symlink() or not path.is_file():
        raise AdoptError("--protocol-spec is not a file")
    return path.read_bytes(), False


# The call that loads a module from a file by its path, which a script uses
# for a module whose name the standard library holds, and the shape of the
# file name it is given.
PATH_LOADER = "spec_from_file_location"
PY_FILE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\.py")


def imported_modules(rel, data):
    """The top-level name of each module the Python file rel imports by an
    absolute name, wherever in the file the import stands, since one inside
    a function runs too once the function is called. A file that does not
    parse is refused in one line, which quotes nothing of it, as the log
    that would show it is public; for the same reason the warnings the
    parser writes on its own, such as one for an escape Python does not
    know, which name the file's line and may print it, are not let out."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(data, filename=rel)
    except (SyntaxError, ValueError):
        raise AdoptError(f"the template's {rel} does not parse as Python") from None
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.partition(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names.add(node.module.partition(".")[0])
        elif isinstance(node, ast.Call) and called_name(node) == PATH_LOADER:
            names.update(loaded_by_path(node))
    return names


def called_name(call):
    """The last name of what a call calls: spec_from_file_location for
    importlib.util.spec_from_file_location(...) as for the bare name."""
    func = call.func
    return func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")


def loaded_by_path(call):
    """The module a spec_from_file_location call loads by its path, as the
    file name in the path's literal, profile for TOOLS / "profile.py":
    the template loads tools/profile.py so, since the standard library has
    a module of that name, and an import statement never names it."""
    names = set()
    for argument in call.args[1:2] + [keyword.value for keyword in call.keywords if keyword.arg == "location"]:
        for node in ast.walk(argument):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                file_name = PurePosixPath(node.value).name
                if PY_FILE.fullmatch(file_name):
                    names.add(file_name.removesuffix(".py"))
    return names


def module_files(plan, folder, name, script=""):
    """The files of the template's module name where the unit's script, in
    folder, finds it, Python putting the script's folder first on its path,
    or the folders SEARCH gives for the script: name.py, or every file of
    the package name, in the first folder that has it; none for a module
    the template does not have, such as one of Python's own."""
    for place in SEARCH.get(script, (folder,)):
        found = sorted(r for r in plan if r == f"{place}/{name}.py" or r.startswith(f"{place}/{name}/"))
        if found:
            return found
    return []


def unit_files(plan, workflow, script):
    """A workflow's unit as the plan holds it, or nothing when the plan lacks
    the workflow or its script: the workflow, the script, every module of
    the template the script imports and every one those import in turn. The
    vendored library is left out, being a unit of its own."""
    if workflow not in plan or script not in plan:
        return []
    folder = PurePosixPath(script).parent.as_posix()
    files, waiting = [workflow], [script]
    while waiting:
        rel = waiting.pop(0)
        if rel in files:
            continue
        files.append(rel)
        if rel.endswith(".py"):
            for name in sorted(imported_modules(rel, plan[rel][0]) - {LIBRARY_PACKAGE}):
                waiting += module_files(plan, folder, name, script)
    return files


def needs_library(plan, files):
    """Whether a Python file among files imports the vendored library."""
    return any(LIBRARY_PACKAGE in imported_modules(rel, plan[rel][0]) for rel in files if rel.endswith(".py"))


def workflow_units(plan):
    """The units of UNITS that the plan holds, each as its name, its files and
    whether it needs the vendored library."""
    units = []
    for name, workflow, script in UNITS:
        files = unit_files(plan, workflow, script)
        if files:
            units.append((name, files, needs_library(plan, files)))
    return units


def metrics_files(plan):
    """The metrics workflow's unit in the plan, or nothing."""
    return unit_files(plan, METRICS_WORKFLOW, METRICS_SCRIPT)


def protocol_plan(staged, spec):
    """Mode existing's files out of the staged tree, and where the protocol's
    text came from: the library's spec when one was passed, the template's
    own filled page otherwise."""
    plan = {rel: entry for rel, entry in staged.items() if rel.startswith(PROTOCOL_TREE + "/")}
    for rel in PROTOCOL_FILES:
        if rel not in staged:
            raise AdoptError(f"the template has no {rel}")
        plan[rel] = staged[rel]
    if spec is None and PROTOCOL_TEXT not in staged:
        raise AdoptError(f"the template has no {PROTOCOL_TEXT}")
    plan[PROTOCOL_TEXT] = staged[PROTOCOL_TEXT] if spec is None else spec
    for _, workflow, script in UNITS:
        plan.update({rel: staged[rel] for rel in unit_files(staged, workflow, script)})
    plan[SWITCH] = staged[SWITCH]
    return plan, ("template" if spec is None else "spec")


def staged_plan(template, options, metrics):
    """What goes into the target, staged and filled in a scratch folder that
    lies in neither tree; the switch says metrics, the word the adoption
    writes."""
    spec = read_spec(options)
    files, links = template_files(template)
    with tempfile.TemporaryDirectory(prefix="sdlc-adopt-") as scratch:
        staging = Path(scratch) / "tree"
        staging.mkdir()
        stage(template, staging, files)
        event = Path(scratch) / "event.json"
        write_event(event, options.repo, options.owner_type, options.creator)
        run_template_init(template, staging, event, options.repo, options.default_branch)
        (staging / SWITCH).parent.mkdir(parents=True, exist_ok=True)
        (staging / SWITCH).write_text(metrics + "\n", encoding="ascii")
        staged = read_plan(staging)
    if options.mode == "new":
        return staged, links, "template"
    plan, text = protocol_plan(staged, spec)
    return plan, links, text


# --- the target -------------------------------------------------------------------


def inside(path, root):
    return os.path.commonpath([path, root]) == root


def safe_relative(rel):
    path = PurePosixPath(rel)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] == ".git":
        raise AdoptError(f"{rel}: not a path inside the repository; refused")
    return path


def blocked(target, rel):
    """Why the file rel of the target is not written, or None. A link may
    lead anywhere inside the repository but never out of it nor into its
    .git, where a hook would run at the commit."""
    path = safe_relative(rel)
    parent = os.path.realpath(target / path.parent)
    if not inside(parent, str(target)):
        return "a folder on its way is a link that leads out of the repository"
    if inside(parent, str(target / ".git")):
        return "a folder on its way is a link into .git"
    for depth in range(1, len(path.parts)):
        ancestor = target.joinpath(*path.parts[:depth])
        if (ancestor.is_symlink() or ancestor.exists()) and not ancestor.is_dir():
            return "a file of yours stands where a folder goes"
    destination = target / path
    if destination.is_dir() and not destination.is_symlink():
        return "a folder of yours stands where this file goes"
    return None


def write_file(destination, data, executable):
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    os.chmod(destination, 0o755 if executable else 0o644)


def place(target, rel, data, executable, overwrite):
    """Write one file; the outcome and, when skipped, why."""
    why = blocked(target, rel)
    if why:
        return "skipped", why
    destination = target / rel
    if exists(destination):
        if not overwrite:
            return "kept", None
        destination.unlink()  # a link is replaced, never written through
        write_file(destination, data, executable)
        return "replaced", None
    write_file(destination, data, executable)
    return "added", None


def record(manifest, rel, outcome, why=None):
    if outcome == "skipped":
        manifest["skipped"].append({"path": rel, "why": why})
    else:
        manifest[outcome].append(rel)


def existing_file(target, rel):
    """The file of theirs that rel names, as (path, None) when it may be
    read and rewritten in place, a regular file or a link that stays inside
    the repository, or (None, why) when it may not."""
    why = blocked(target, rel)
    if why:
        return None, why
    real = os.path.realpath(target / rel)
    if not inside(real, str(target)) or inside(real, str(target / ".git")):
        return None, "it is a link that leads out of the repository or into .git"
    if not Path(real).is_file():
        return None, "it is a link to something that is not a file"
    return Path(real), None


def exists(path):
    return path.is_symlink() or path.exists()


def is_checkout(target):
    """Whether target is the top of a git checkout, where ignore rules
    apply; a plain folder has none."""
    if not exists(target / ".git"):
        return False
    done = subprocess.run(["git", "-C", str(target), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return done.returncode == 0 and os.path.realpath(done.stdout.strip()) == os.path.realpath(target)


def ignored_paths(target, rels):
    """Those of rels that the target's ignore rules match; a file git tracks
    is never among them, whatever the rules say."""
    if not is_checkout(target):
        return set()
    done = subprocess.run(["git", "-C", str(target), "check-ignore", "-z", "--stdin"],
                          input="\0".join(rels), capture_output=True, text=True)
    if done.returncode not in (0, 1):  # 0 names some of them, 1 names none
        last = (done.stderr.strip().splitlines() or ["no message"])[-1]
        raise AdoptError(f"the repository's ignore rules could not be read: {last}")
    return {rel for rel in done.stdout.split("\0") if rel}


def in_the_way(target, rel, ignored):
    """Why rel would not be added, as a clause about it, or None."""
    if blocked(target, rel):
        return "cannot be written here"
    if exists(target / rel):
        return "is this repository's own"
    if rel in ignored:
        return "is ignored by this repository"
    return None


def first_in_the_way(target, files, ignored):
    """The first of files that stands in the way of its unit, said as "`rel`
    is ...", or None."""
    for rel in files:
        cause = in_the_way(target, rel, ignored)
        if cause:
            return f"`{rel}` {cause}"
    return None


def hold_back(held, target, files, ignored, why):
    """Hold back, for why, each of files that does not stand in the way
    itself; one that does keeps its own outcome."""
    for rel in files:
        if not in_the_way(target, rel, ignored):
            held[rel] = why


def holds_the_templates(target, rel, data):
    """Whether the repository's file rel holds the template's bytes already."""
    real, why = existing_file(target, rel)
    return why is None and real.read_bytes() == data


def first_unlike_the_templates(target, plan, files, ignored):
    """The first of files that stands in the way of its unit, said as "`rel`
    is ...", or None, passing over a file of theirs that holds the template's
    bytes already, copied by hand from the same template or left by an
    earlier adoption: it is the template's in all but name, so the unit
    comes around it and gains the modules it has come to hold since. The
    run itself refuses a repository whose default branch still holds the
    protocol's text (scripts/adopted.py), so an earlier adoption meets this
    only where that file has gone since."""
    for rel in files:
        cause = in_the_way(target, rel, ignored)
        if cause and not holds_the_templates(target, rel, plan[rel][0]):
            return f"`{rel}` {cause}"
    return None


def in_place(target, plan, manifest, rel):
    """Whether the template's rel is in the repository once the pull request
    is merged: written by it, or kept as a file of theirs that holds the
    template's bytes already."""
    if rel in manifest["added"] or rel in manifest["replaced"]:
        return True
    return rel in manifest["kept"] and holds_the_templates(target, rel, plan[rel][0])


def library_unlike_the_templates(target, plan, ignored, library, held):
    """Why the vendored library will not be the template's once the pull
    request is merged, said as "`rel` is ...", or None: a file of it is held
    back, or one of theirs differs from the template's."""
    if any(rel in held for rel in library):
        return first_in_the_way(target, library, ignored)
    return first_unlike_the_templates(target, plan, library, ignored)


def switch_left_out(target, ignored):
    """Why the metrics switch will not be in the pull request, said as "`rel`
    is ...", or None: the repository ignores it, or it cannot be written
    there. A switch of theirs is kept, and says what it says."""
    if SWITCH in ignored:
        return f"`{SWITCH}` is ignored by this repository"
    if blocked(target, SWITCH):
        return f"`{SWITCH}` cannot be written here"
    return None


def hold_back_library(held, target, plan, ignored):
    """Hold the vendored library back whole while a file of it stands in the
    way, and say why it will not be the template's once the pull request is
    merged, or None."""
    library = [rel for rel in plan if rel.startswith(PROTOCOL_TREE + "/") or rel == VENDORED]
    blocker = first_in_the_way(target, library, ignored)
    if blocker:
        hold_back(held, target, library, ignored, f"{blocker}, and {LIBRARY_UNIT} are brought together or not at all")
    return library_unlike_the_templates(target, plan, ignored, library, held)


def unit_holdbacks(target, plan, ignored):
    """rel -> why, for each file of a unit that would be added while another
    file of the unit is theirs, blocked or ignored: the unit is then left
    whole, and the file that stands in the way is named. A unit whose
    scripts import the vendored library is left whole too while the library
    will not be the template's, since they would fail at an import, or run
    a library of theirs; and the metrics workflow's while the switch will
    not be in the pull request, since the form's choice would then be in no
    file, and the workflow reads a missing switch as on."""
    held = {}
    unlike = hold_back_library(held, target, plan, ignored)
    switch = switch_left_out(target, ignored)
    landing = []
    for name, files, needs in workflow_units(plan):
        blocker = first_unlike_the_templates(target, plan, files, ignored)
        if blocker:
            hold_back(held, target, files, ignored, f"{blocker}, and {name} are brought together or not at all")
        elif needs and unlike:
            hold_back(held, target, files, ignored,
                      f"{unlike}, so the vendored library is not brought, and {name} need it")
        elif switch and METRICS_WORKFLOW in files:
            hold_back(held, target, files, ignored,
                      f"{switch}, and {name} come only with the metrics switch, which says whether they share")
        else:
            landing.append((name, files))
    hold_back_sharers(held, target, ignored, landing)
    return held


def hold_back_sharers(held, target, ignored, landing):
    """Hold back each unit of landing one of whose modules stays out with
    another workflow that shares it, since it would land without it; again
    until none is caught, as each one held back may catch another."""
    while True:
        caught = [(name, files) for name, files in landing if any(rel in held for rel in files)]
        if not caught:
            return
        for name, files in caught:
            shared = next(rel for rel in files if rel in held)
            hold_back(held, target, [rel for rel in files if rel not in held], ignored,
                      f"`{shared}` stays out with another workflow, and {name} are brought together or not at all")
            landing.remove((name, files))


def refuse_without_protocol(target, ignored):
    """Refuse, before anything is written, an adoption that could not write
    the protocol's text, which the repository ignores or a file or link of
    its own stands in the way of: every Claude Code session reads the
    protocol there, and the front door knows an adoption by that file alone
    (scripts/sweep.py, is_adopted), so one made without it would neither
    work from its first day nor be known for one by the next request."""
    if PROTOCOL_TEXT in ignored or blocked(target, PROTOCOL_TEXT):
        raise Refusal(f"{PROTOCOL_TEXT} cannot be written: the repository ignores it, or a file or link of its own"
                      " stands where it or its folder goes")


def with_section(text):
    """Their CLAUDE.md with the section after it, in their line endings."""
    section = CLAUDE_SECTION
    if b"\r\n" in text:
        section = section.replace("\n", "\r\n")
    newline = b"\r\n" if b"\r\n" in text else b"\n"
    if text and not text.endswith(newline):
        text += newline
    return text + newline + section.encode("utf-8")


def note_missing_protocol(manifest):
    """Say why CLAUDE.md gains no section: the protocol's text did not land,
    so there is nothing of the template's to import. It did not land because
    the repository's own file is kept, since an adoption that could not
    write it at all is refused (refuse_without_protocol)."""
    manifest["notes"].append(
        f"`{PROTOCOL_TEXT}` is this repository's own and is kept, so the claim protocol's text did not land and"
        f" `{CLAUDE_MD}` gains no section importing it. The text is spec/PROTOCOL.md in the public"
        f" OpenSpineConsortium/symphony-protocol; once it stands at `{PROTOCOL_TEXT}`, add this to `{CLAUDE_MD}`:"
        f"\n\n```markdown\n{CLAUDE_SECTION}```"
    )


def add_claude_section(target, manifest, ignored):
    """Append the section to their CLAUDE.md, or make one with it, once the
    protocol's text it imports has landed; an ignored CLAUDE.md is each
    person's own and is left alone."""
    if PROTOCOL_TEXT not in manifest["added"]:
        note_missing_protocol(manifest)
        return
    if CLAUDE_MD in ignored:
        record(manifest, CLAUDE_MD, "skipped", IGNORED_WHY)
        return
    if not exists(target / CLAUDE_MD):
        record(manifest, CLAUDE_MD, *place(target, CLAUDE_MD, CLAUDE_SECTION.encode("utf-8"), False, False))
        return
    real, why = existing_file(target, CLAUDE_MD)
    if why:
        record(manifest, CLAUDE_MD, "skipped", why)
        return
    text = real.read_bytes()
    if CLAUDE_IMPORT in text.decode("utf-8", "replace"):
        record(manifest, CLAUDE_MD, "kept")
        return
    real.write_bytes(with_section(text))
    manifest["merged"].append(CLAUDE_MD)


def json_indent(text):
    """The indent their JSON uses, so a merge keeps its look."""
    for line in text.splitlines()[1:]:
        stripped = line.lstrip(" \t")
        if stripped and len(stripped) < len(line):
            lead = line[: len(line) - len(stripped)]
            return "\t" if lead.startswith("\t") else len(lead)
    return 2


def keys_appended(text, additions, indent):
    """Their text with new top-level keys written before its closing brace,
    so every line they had stays as it was; None when the text does not end
    with that brace."""
    body = text.rstrip()
    if not body.endswith("}"):
        return None
    head = body[:-1].rstrip()
    newline = "\r\n" if "\r\n" in text else "\n"
    unit = "\t" if indent == "\t" else " " * indent
    members = []
    for key, value in additions.items():
        dumped = json.dumps(value, indent=indent, ensure_ascii=False).replace("\n", newline + unit)
        members.append(f"{unit}{json.dumps(key)}: {dumped}")
    separator = "" if head.endswith("{") else ","
    return head + separator + newline + ("," + newline).join(members) + newline + "}" + newline


def merged_settings(text):
    """Their settings with the marketplace and the plugin added: the text,
    what each key gained ("added" when the key is new, "extended" when it
    took one entry) and whether the plugin ends up enabled; None when
    nothing changes. ValueError when it is not a JSON object of the shape
    Claude Code reads. When the keys are new, they are written after their
    text, which stays as it was; otherwise, or when that would not read
    back as the merge, the whole file is written again, in its own line
    endings."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("not an object")
    markets = data.get("extraKnownMarketplaces", {})
    plugins = data.get("enabledPlugins", {})
    if not isinstance(markets, dict) or not isinstance(plugins, dict):
        raise ValueError("extraKnownMarketplaces or enabledPlugins is not an object")
    if MARKETPLACE_NAME in markets and PLUGIN in plugins:
        return None
    merged, changed = dict(data), {}
    if MARKETPLACE_NAME not in markets:
        merged["extraKnownMarketplaces"] = {**markets, MARKETPLACE_NAME: MARKETPLACE}
        changed["extraKnownMarketplaces"] = "extended" if "extraKnownMarketplaces" in data else "added"
    if PLUGIN not in plugins:
        merged["enabledPlugins"] = {**plugins, PLUGIN: True}
        changed["enabledPlugins"] = "extended" if "enabledPlugins" in data else "added"
    enabled = merged["enabledPlugins"].get(PLUGIN) is True
    indent = json_indent(text)
    newline = "\r\n" if "\r\n" in text else "\n"
    if all(state == "added" for state in changed.values()):
        appended = keys_appended(text, {key: merged[key] for key in changed}, indent)
        if appended is not None and json.loads(appended) == merged:
            return appended, changed, enabled
    return (json.dumps(merged, indent=indent, ensure_ascii=False) + "\n").replace("\n", newline), changed, enabled


def preset_settings():
    return json.dumps({"extraKnownMarketplaces": {MARKETPLACE_NAME: MARKETPLACE}, "enabledPlugins": {PLUGIN: True}},
                      indent=2) + "\n"


def merge_settings(target, manifest, ignored):
    """Add the keys to their .claude/settings.json, keeping every key it has;
    make the file when there is none; leave it when it does not parse or
    when the repository ignores it."""
    if SETTINGS in ignored:
        record(manifest, SETTINGS, "skipped", IGNORED_WHY)
        return
    if not exists(target / SETTINGS):
        outcome, why = place(target, SETTINGS, preset_settings().encode("ascii"), False, False)
        record(manifest, SETTINGS, outcome, why)
        if outcome == "added":
            manifest["settings_changed"] = {"extraKnownMarketplaces": "added", "enabledPlugins": "added"}
            manifest["plugin_enabled"] = True
        return
    real, why = existing_file(target, SETTINGS)
    if why:
        record(manifest, SETTINGS, "skipped", why)
        return
    try:
        text = real.read_bytes().decode("utf-8-sig")
        merged = merged_settings(text)
    except ValueError:  # UnicodeDecodeError and JSONDecodeError are both ValueErrors
        record(manifest, SETTINGS, "kept")
        manifest["settings_invalid"] = True
        return
    if merged is None:
        record(manifest, SETTINGS, "kept")
        return
    written, changed, enabled = merged
    real.write_bytes(written.encode("utf-8"))
    manifest["merged"].append(SETTINGS)
    manifest["settings_changed"] = changed
    manifest["plugin_enabled"] = enabled


def first_word(text):
    """The switch as the template's tools/metrics.py reads it: the first
    whitespace-separated word, lowercased; the rest of the file is prose."""
    words = (text or "").split()
    return words[0].lower() if words else ""


def switch_word(target, rel):
    """The first word of the switch file rel the repository has, as the
    template's tools/metrics.py reads it; nothing where it cannot be read,
    which that script reads as off."""
    real, _ = existing_file(target, rel)
    try:
        return first_word(real.read_text(encoding="utf-8")) if real else ""
    except (OSError, UnicodeDecodeError):
        return ""


def switch_says(target, rel):
    """What the switch file rel of the target says, as the template's
    tools/metrics.py reads it: on only with the word on first; off when it
    says anything else, cannot be read here, or is something of the
    repository's own that stands where the file goes; and None when there
    is no such file, which says nothing. Each doubt falls to off, since off
    shares nothing."""
    if not blocked(target, rel) and not exists(target / rel):
        return None
    return "on" if switch_word(target, rel) == "on" else "off"


def links_to_nothing(target, rel):
    """Whether rel of the target is a link, or a chain of them, that stays
    inside the repository and ends at nothing there: the template's
    tools/metrics.py, opening a switch through it, meets a missing file,
    which says nothing. A link out of the repository or into its .git, and
    one that cannot be followed for another reason, such as a loop, are
    not, and stay doubts."""
    path = target / rel
    if not path.is_symlink() or blocked(target, rel):
        return False
    real = os.path.realpath(path)
    if not inside(real, str(target)) or inside(real, str(target / ".git")):
        return False
    try:
        path.stat()
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return False


def switches_off(target):
    """The switch files of the target that say off, under the switch's name
    or its old one: an opt-out the adoption never turns back on. A doubt
    is one too, a link to nothing among them, since the owner's word may
    lie where this run cannot read it, and off shares nothing."""
    return [rel for rel in SWITCHES if switch_says(target, rel) == "off"]


def switches_after(target):
    """What each switch file of the target says to the metrics workflow once
    the files have landed, the new name first. A file that is not there
    says nothing and is left out, as one the repository ignores is, which
    is missing from every clone, and so is a link to nothing, which that
    workflow reads as a missing file: this says what it will read, where
    switches_off says what the adoption takes as an opt-out."""
    return {rel: said for rel in SWITCHES
            if not links_to_nothing(target, rel) and (said := switch_says(target, rel))}


def switch_reads(switches):
    """The switches as the template's metrics workflow reads them once the
    pull request is merged, on or off, from what each file says: off where
    either says off, since each is the owner's word and an on in the other
    never lifts it, and on where neither says anything, since a missing
    switch is read as on."""
    return "off" if "off" in switches.values() else "on"


def held_words(rel, unread, before=False):
    """What the switch file rel said before this request, as the held note
    words it: off, or, for a link to nothing, which this run cannot read,
    that the adoption takes it as off."""
    if rel not in unread:
        return "said `off` before this request" if before else "says `off`"
    link = "was a link to nothing before this request" if before else "is a link to nothing"
    return f"{link}, which this adoption takes as `off`"


def note_held_switch(manifest, said_off, unread, metrics):
    """Say why the switch this adoption wrote says off where the form left
    sharing on: a switch of the repository's own said off before it, and
    the form's default never lifts an opt-out made in the repository; or
    one was a link to nothing (unread), which the adoption takes for an
    opt-out, since off shares nothing, and which the metrics workflow
    reads as no switch at all."""
    if metrics != "on" or not said_off or SWITCH not in manifest["added"] + manifest["replaced"]:
        return
    still = "says `off` now" if SWITCH in unread else "still says `off`"
    if OLD_SWITCH in said_off:
        said = (f"`{OLD_SWITCH}`, the switch under its name before the rename to Symphony,"
                f" {held_words(OLD_SWITCH, unread)}")
        if SWITCH in said_off:
            said += f", and `{SWITCH}` {held_words(SWITCH, unread, before=True)}, so `{SWITCH}` {still}"
        else:
            said += f", so `{SWITCH}` says `off` too"
        if OLD_SWITCH in unread:
            lift = f"write `on` in `{SWITCH}`, since the metrics workflow reads a link to nothing as no switch at all"
        else:
            lift = f"write `on` in both files, or delete `{OLD_SWITCH}` and write `on` in `{SWITCH}`"
    else:
        said = f"`{SWITCH}` {held_words(SWITCH, unread, before=True)}, so it {still}"
        lift = "write `on` there"
    taken = ", and a switch this adoption cannot read counts as one" if unread & set(said_off) else ""
    manifest["notes"].append(f"{said}, though the form left sharing on: the form's default never lifts an opt-out made"
                             f" in the repository{taken}. To share, {lift}.")


def note_kept_switch(target, manifest, metrics):
    """Say so when mode existing kept a switch that says something else than
    the form asked, or that is a link to nothing, which the metrics workflow
    reads as no switch at all and so as the form's on, where no other
    switch says off."""
    if SWITCH not in manifest["kept"]:
        return
    if links_to_nothing(target, SWITCH):
        if metrics != "on":
            manifest["notes"].append(
                f"{SWITCH} was there already and is a link to nothing, which the metrics workflow reads as a missing"
                f" switch, where the form asked for `{metrics}`; it is kept, so edit it to change the choice."
            )
        return
    said = switch_word(target, SWITCH)
    if said != metrics:
        if said in ("on", "off"):
            shown = f"`{said}`"
        else:
            shown = "something other than on or off, which the metrics workflow reads as off"
        manifest["notes"].append(
            f"{SWITCH} was there already and says {shown}, where the form asked for `{metrics}`;"
            " it is kept, so edit it to change the choice."
        )


# --- apply ------------------------------------------------------------------------


def checked_options(options):
    """Refuse what the workflow could only pass by mistake."""
    try:
        parse_repository(options.repo)
    except FormError as problem:
        raise AdoptError(f"--repo: {problem}") from None
    if not LOGIN.fullmatch(options.creator):
        raise AdoptError("--creator must be a GitHub login")
    branch = options.default_branch
    if not branch or branch.startswith("-") or any(c.isspace() or ord(c) < 32 or c == "\x7f" for c in branch):
        raise AdoptError("--default-branch must be a branch name")


def checked_roots(options):
    template = Path(options.template).resolve()
    target = Path(options.target).resolve()
    manifest = Path(options.manifest).resolve()
    for name, root in (("--template", template), ("--target", target)):
        if not root.is_dir():
            raise AdoptError(f"{name} is not a folder")
    if inside(str(template), str(target)) or inside(str(target), str(template)):
        raise AdoptError("--template and --target must be two folders, neither inside the other")
    if inside(str(manifest), str(target)):
        raise AdoptError("--manifest must lie outside the target, or it would be committed")
    return template, target, manifest


def new_manifest(options, links, protocol_text, plan):
    return {
        "schema": MANIFEST_SCHEMA,
        "repository": options.repo,
        "mode": options.mode,
        "metrics": options.metrics,
        "default_branch": options.default_branch,
        "owner_type": options.owner_type,
        "creator": options.creator,
        "kind_read": options.kind_read,
        # The run made the repository's first commit, the README GitHub's
        # own "Add a README file" makes, since it had none.
        "began": options.began,
        # The workflow, whether its script counts by setting, what each
        # switch file says and so what the workflow will read in them, and
        # whether the setup script ticks the box are known once the files
        # have landed; metrics above is what the form asked.
        "metrics_workflow": False,
        "metrics_breakdown": False,
        "switches": {},
        "switch_reads": options.metrics,
        "setup_script_ticks_box": False,
        "metrics_in_template": bool(metrics_files(plan)),
        "protocol_text": protocol_text,
        "added": [], "replaced": [], "kept": [], "merged": [],
        "skipped": [{"path": rel, "why": "a link in the template, which is never followed"} for rel in links],
        "notes": [],
        "settings_invalid": False,
        "settings_changed": {},
        "plugin_enabled": None,
    }


def adopt(options):
    """Apply the adoption to the target and write the manifest; the manifest."""
    checked_options(options)
    template, target, manifest_path = checked_roots(options)
    # An off the repository says already, under either name, is read
    # before anything is written, and the switch the adoption writes says
    # off too: the form's default of on never lifts an opt-out. A link to
    # nothing is taken as one, and the note says it was a link.
    said_off = switches_off(target)
    unread = {rel for rel in said_off if links_to_nothing(target, rel)}
    plan, links, protocol_text = staged_plan(template, options, "off" if said_off else options.metrics)
    manifest = new_manifest(options, links, protocol_text, plan)
    ignored, held = set(), {}
    if options.mode == "existing":
        ignored = ignored_paths(target, sorted(plan) + [CLAUDE_MD, SETTINGS])
        held = unit_holdbacks(target, plan, ignored)
    refuse_without_protocol(target, ignored)
    for rel in sorted(plan):
        if rel in ignored:
            record(manifest, rel, "skipped", IGNORED_WHY)
        elif rel in held:
            record(manifest, rel, "skipped", held[rel])
        else:
            data, executable = plan[rel]
            record(manifest, rel, *place(target, rel, data, executable, options.mode == "new"))
    if options.mode == "existing":
        add_claude_section(target, manifest, ignored)
        merge_settings(target, manifest, ignored)
        note_kept_switch(target, manifest, options.metrics)
    note_held_switch(manifest, said_off, unread, options.metrics)
    landed = manifest["added"] + manifest["replaced"]
    metrics = metrics_files(plan)
    manifest["metrics_workflow"] = bool(metrics) and all(in_place(target, plan, manifest, rel) for rel in metrics)
    manifest["metrics_breakdown"] = manifest["metrics_workflow"] and BREAKDOWN_KEY in plan[METRICS_SCRIPT][0]
    # Off in either file wins, as the template's tools/metrics.py reads
    # them, and a link to nothing says nothing there, so the pull request
    # says what the switches it leaves will do.
    manifest["switches"] = switches_after(target)
    manifest["switch_reads"] = switch_reads(manifest["switches"])
    manifest["setup_script_ticks_box"] = SETUP_SCRIPT in landed and ACTIONS_PATH in plan[SETUP_SCRIPT][0]
    for key in ("added", "replaced", "kept", "merged"):
        manifest[key].sort()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def command_apply(options):
    try:
        manifest = adopt(options)
    except Refusal as refusal:
        print(f"adopt: refused: {refusal}", file=sys.stderr)
        return EXIT_REFUSED
    except (AdoptError, OSError) as problem:
        print(f"adopt: {problem}", file=sys.stderr)
        return 1
    counts = ", ".join(f"{len(manifest[key])} {key}" for key in ("added", "replaced", "kept", "merged", "skipped"))
    print(f"adopt: mode {manifest['mode']}: {counts}")
    return 0


# --- body -------------------------------------------------------------------------


def path_list(paths):
    return "\n".join(f"- `{path}`" for path in paths)


def folded(summary, paths):
    """A long list folded away, so the page opens on what matters."""
    return f"<details><summary>{summary}</summary>\n\n{path_list(paths)}\n\n</details>"


def title(manifest):
    if manifest["mode"] == "new":
        return "Adopt the Symphony template"
    return "Take up the Symphony claim protocol"


def opening(manifest):
    repo = manifest["repository"]
    if manifest.get("began"):
        until = (" The repository had no commit, so the run first made one, as GitHub's own \"Add a README"
                 " file\" does: a README.md holding the repository's name, on the default branch, which this pull"
                 " request goes into. Nothing else changes until you merge it.")
    else:
        until = " Nothing changes until you merge it."
    asked = (f"The Symphony App opened it because an administrator of {repo} asked for it on the adoption"
             f" form ({FRONT_DOOR}).{until}")
    if manifest["mode"] == "new":
        return (f"This pull request brings the whole Symphony template into {repo}, as \"Use this template\""
                f" would have made it, with this repository's names filled in. {asked}")
    return (f"This pull request brings the Symphony claim protocol into {repo}, beside your own files: the"
            " board, the claim files and the text every Claude Code session reads before it takes work. No file of"
            f" yours is overwritten. {asked}")


def key_phrase(key, changed):
    return f"`{key}`" if changed[key] == "added" else f"an entry in `{key}`"


def settings_line(manifest):
    """What .claude/settings.json gained, naming only the keys it did and
    the plugin's state when it stays off by their choice."""
    changed = manifest["settings_changed"]
    gained = []
    if "extraKnownMarketplaces" in changed:
        gained.append(f"{key_phrase('extraKnownMarketplaces', changed)}, which names the marketplace"
                      " OpenSpineConsortium/symphony-marketplace")
    if "enabledPlugins" in changed:
        gained.append(f"{key_phrase('enabledPlugins', changed)}, which enables its plugin `{PLUGIN}`")
    line = f"- `{SETTINGS}` gains " + ", and ".join(gained)
    if not manifest["plugin_enabled"]:
        line += f"; its plugin `{PLUGIN}` stays off in `enabledPlugins`, as you set it"
    return line + "; every key it had stays."


def merged_lines(manifest):
    lines = []
    if CLAUDE_MD in manifest["merged"]:
        lines.append(f"- `{CLAUDE_MD}` gains the section \"How work is claimed\" at its end, whose `{CLAUDE_IMPORT}`"
                     " line imports the protocol into every session.")
    if SETTINGS in manifest["merged"]:
        lines.append(settings_line(manifest))
    return lines


def by_reason(skipped):
    """The paths not written, grouped under each reason in the order the
    reasons first appear, as `a`, `b` and `c`."""
    groups = {}
    for item in skipped:
        groups.setdefault(item["why"], []).append(f"`{item['path']}`")
    listed = []
    for why, paths in groups.items():
        listed.append((", ".join(paths[:-1]) + " and " + paths[-1] if len(paths) > 1 else paths[0], why))
    return listed


def changes_section(manifest):
    parts = ["## What changes", ""]
    added = manifest["added"]
    if added:
        parts += [f"Added, {len(added)} files:", "", folded(f"The {len(added)} added files", added), ""]
    if manifest["replaced"]:
        parts += ["Replaced, files this repository had that the template's copy takes the place of; the diff shows"
                  " what they held:", "", path_list(manifest["replaced"]), ""]
    if manifest["mode"] == "new":
        parts += ["Files of yours that the template does not have are not touched.", ""]
    merged = merged_lines(manifest)
    if merged:
        parts += ["Changed by addition only:", "", *merged, ""]
    if manifest["kept"]:
        parts += ["Kept as they are, because this repository has them already:", "", path_list(manifest["kept"]), ""]
    if manifest["skipped"]:
        parts += ["Not written:", ""]
        parts += [f"- {paths}: {why}" for paths, why in by_reason(manifest["skipped"])]
        parts.append("")
    parts += ["LICENSE is not touched: licensing your project is your decision, so the template's is not copied; the files"
             " this pull request brings are offered under the MIT License, whose text is LICENSE in"
             f" {FRONT_DOOR}.", ""]
    return parts


def ignored_notes(ignored):
    """What to do about the files the repository ignores, which were not
    written, each with what this pull request would have put there. The
    form adopts a repository once, so a request made there after the merge
    is refused: a file with a way by hand is given it, and the rest comes
    only with an adoption made again, once this one is closed or reverted."""
    parts = ["Files this repository ignores were not written, since git replaces each person's own copy of an"
             " ignored file on their next pull without a word, and the form adopts a repository once, so asking"
             " there again after the merge is refused. What to do instead:", ""]
    if CLAUDE_MD in ignored:
        parts += [f"- `{CLAUDE_MD}`: add this section to the `{CLAUDE_MD}` each session reads.", "",
                  "```markdown", CLAUDE_SECTION.rstrip("\n"), "```", ""]
    if SETTINGS in ignored:
        parts += [f"- `{SETTINGS}`: each person adds the marketplace and installs the plugin once, with"
                  " `claude plugin marketplace add OpenSpineConsortium/symphony-marketplace` and"
                  f" `claude plugin install {PLUGIN}`, or adds these keys to the settings file they keep.", "",
                  "```json", preset_settings().rstrip("\n"), "```", ""]
    others = [rel for rel in ignored if rel not in (CLAUDE_MD, SETTINGS)]
    if others:
        their, them = ("its", "it") if len(others) == 1 else ("their", "them")
        parts += ["- " + ", ".join(f"`{rel}`" for rel in others) + f": {their} content is not in this pull request,"
                  f" and only an adoption made again brings it: stop ignoring {them}, close this pull request, or revert"
                  " its merge on the default branch once it is merged, delete its branch `symphony/adopt` where it is"
                  " still there, and ask again on the form.", ""]
    return parts


def notes_section(manifest):
    parts = []
    if manifest["settings_invalid"]:
        parts += [f"`{SETTINGS}` does not parse as a JSON object, so it was left as it was. Add these two keys to it"
                  " by hand once it does, beside the keys it has:", "", "```json", preset_settings().rstrip("\n"),
                  "```", ""]
    templates_page = manifest["protocol_text"] == "template" and PROTOCOL_TEXT in manifest["added"]
    if manifest["mode"] == "existing" and templates_page:
        parts += [f"`{PROTOCOL_TEXT}` is the template's own text, which also names files only a copy of the"
                  " template carries (its skills, routines and setup pages); the symphony plugin brings the skills.", ""]
    ignored = [item["path"] for item in manifest["skipped"] if item["why"] == IGNORED_WHY]
    if ignored:
        parts += ignored_notes(ignored)
    if manifest["mode"] == "new" and manifest["owner_type"] == "Organization":
        parts += [codeowners_note(manifest), ""]
    if manifest.get("kind_read"):
        parts += [kind_note(manifest), ""]
    parts += [f"{note}\n" for note in manifest["notes"]]
    return (["## Notes", "", *parts]) if parts else []


def codeowners_note(manifest):
    """Who `.github/CODEOWNERS` names in an organization's new copy, and
    why: the form's author."""
    creator = manifest["creator"]
    because = ("because GitHub asks a user or a team for review and never an organization; change it by pull"
               " request when someone else should review (docs/setup/github.md, section 7).")
    return f"`.github/CODEOWNERS` names `{creator}`, who asked for this pull request, {because}"


def kind_note(manifest):
    """The kind was read from the tree, because the form left it to the
    run; the other kind is one request away, once this adoption is closed,
    or reverted when it is merged, since the form adopts a repository
    once."""
    if manifest["mode"] == "new":
        read = ("as a new repository, since its default branch held nothing but what GitHub makes when it"
                " initializes one (a README, a LICENSE or COPYING, a .gitignore or .gitattributes)")
        other = "the protocol alone"
    else:
        read = "as an existing repository, since its default branch holds files of its own"
        other = "the whole template"
    reverted = "or revert its merge on the default branch once it is merged, since the form adopts a repository once"
    return (f"The form left the kind to the run, which read this repository {read}. For {other} instead, close this"
            f" pull request, {reverted}; then delete its branch `symphony/adopt`, where it is still there, and open the"
            f" form at {FRONT_DOOR} choosing the other kind.")


def switch_written(manifest):
    """Whether the switch is in the repository once the pull request is
    merged: written by it, or kept as the repository had it."""
    return any(SWITCH in manifest[key] for key in ("added", "replaced", "kept"))


def switch_said(manifest):
    """The switch as this pull request leaves it and as the metrics workflow
    will read it: written with the word this adoption wrote, kept with the
    repository's own, or not written, where its absence or what stands in
    its place decides; never the form's word where the switch does not hold
    it. A switch the repository keeps that says nothing is a link to
    nothing, which that workflow reads as a missing file."""
    said = manifest["switches"].get(SWITCH)
    if SWITCH in manifest["kept"]:
        if said is None:
            return (f"`{SWITCH}`, which this repository had already and keeps, is a link to nothing, which the metrics"
                    " workflow reads as a missing switch, and a missing switch is read as `on`")
        return f"`{SWITCH}`, which this repository had already and keeps, is read as `{said}`"
    if switch_written(manifest):
        return f"`{SWITCH}` says `{said}`"
    if said is None:
        return f"`{SWITCH}` was not written (above), and a missing switch is read as `on`"
    return f"`{SWITCH}` was not written (above), and what stands in its place is read as `off`"


def off_sentence(manifest):
    """Nothing is shared, and every switch file that says so, so that
    writing on where the sentence says turns sharing on: the switch this
    pull request writes or keeps, or what stands in its place, as
    switch_said tells it, with the switch under its old name beside it
    where that says off too, or the old one alone where only it does."""
    switches = manifest["switches"]
    if switches.get(OLD_SWITCH) != "off":
        said, where = switch_said(manifest), "there"
    elif switches.get(SWITCH) != "off":
        said, where = f"`{OLD_SWITCH}` says `off`", "there"
    elif switch_written(manifest):
        said, where = f"`{SWITCH}` and `{OLD_SWITCH}` say `off`", "in both"
    else:
        said, where = f"`{OLD_SWITCH}` says `off`, and {switch_said(manifest)}", "in both"
    return (f"Nothing is shared: {said}, so the metrics workflow, where there is one, writes only that sharing is off."
            f" Write `on` {where} to share anonymous aggregates later.")


def metrics_idle(manifest):
    """Why nothing is computed where sharing is on: the template carries no
    metrics workflow, or it did not land, or it landed without a script it
    runs."""
    if not manifest["metrics_in_template"]:
        return ("The template does not carry its metrics workflow yet, so nothing is computed or shared today; the"
                " switch records your choice for when it does.")
    if METRICS_WORKFLOW in manifest["added"] or METRICS_WORKFLOW in manifest["replaced"]:
        return ("The metrics workflow was written, but not every script it runs was (above), so it cannot run and"
                " nothing is computed or shared today; the switch records your choice for when it can.")
    return ("The metrics workflow was not written (above), so nothing is computed or shared today; the switch records"
            " your choice for when it is.")


def metrics_at_work(manifest):
    """What the metrics workflow computes and shares where sharing is on, in
    sentences: the counts of parallel work only where the script that landed
    makes them, and, in mode existing, that what Claude spends stays at zero,
    since nothing there records it."""
    if not manifest["metrics_workflow"]:
        return [metrics_idle(manifest)]
    said = ["Once a day `.github/workflows/metrics.yml` writes METRICS.json to the branch `metrics`: counts,"
            " durations and rates of the protocol at work, and never code, text, titles, logins, branch names or"
            " repository names. The Symphony App reads that branch's METRICS.json, and JUDGE.json, the failure-type"
            " frequencies that someone's own judge writes when they run it on their own machine and Claude account,"
            " and nothing else; the dataset names this repository only by a salted hash."]
    if manifest["metrics_breakdown"]:
        said.append("Some of those counts say how the work ran in parallel, so that one person's several Claude Code"
                    " sessions are counted apart from several people's work: the workflow sorts and counts the pull"
                    " requests in its memory by who opened each one, which Claude Code session made it and which"
                    " files it changed, and writes none of them.")
    if manifest["mode"] == "existing":
        said.append("The tokens Claude used, their price and the time it was at work, which METRICS.json counts as"
                    " what the work cost, stay at zero here: the template's session hooks and its Claude workflows"
                    " record them, and the protocol alone brings neither.")
    return said


def sharing_section(manifest):
    """What is shared, as the switches the pull request leaves will have
    it, which is not always what the form asked: a switch of the
    repository's own is kept, an off of its own in either file keeps the
    one this adoption writes off, and a switch that cannot be written
    leaves the metrics workflow out with it in mode existing."""
    parts = ["## What is shared", ""]
    if not switch_written(manifest) and not manifest["metrics_workflow"]:
        parts.append(f"Nothing is computed or shared today: `{SWITCH}` was not written (above), and this pull request"
                     " brings no metrics workflow to read it.")
    elif manifest["switch_reads"] == "on":
        parts.append(f"Sharing of anonymous aggregates is on: {switch_said(manifest)}.")
        parts += metrics_at_work(manifest)
        parts.append(f"To turn it off at any time, write `off` in `{SWITCH}` on the default branch, or set the"
                     " repository variable SDLC_METRICS to `off`; uninstalling the App stops it too.")
    else:
        parts.append(off_sentence(manifest))
    return parts[:2] + [" ".join(parts[2:]), ""]


def setting_state(report, key):
    """One setting's state in the Setup App's report, or None where the
    report has no such setting (none was applied)."""
    if report is None:
        return None
    return report["settings"].get(key, {}).get("state")


def github_said(report, key):
    detail = report["settings"].get(key, {}).get("detail")
    return f" (GitHub said: {detail})" if detail else ""


def pin_expected(report):
    """Whether the report's pin of the check to GitHub Actions is one the
    run tried to make: on a ruleset it created that requires the check. A
    report with no word on the pin, as one from before it, expects none."""
    return (setting_state(report, CHECK_SOURCE) is not None and setting_state(report, "ruleset") == "done"
            and bool(report.get("required_check")))


def pin_settled(report):
    return not pin_expected(report) or setting_state(report, CHECK_SOURCE) in ("done", "exists")


def settings_done(report):
    """Whether the Setup App left nothing of the settings to do by hand:
    secret scanning aside, which the plan or the visibility may refuse, and
    the box for GitHub Actions' pull requests, which the organization or
    its enterprise may forbid; the section says so of each. A check not
    pinned to GitHub Actions is left by hand, since setup-repo.sh pins it."""
    return (report is not None and report["outcome"] == "applied"
            and setting_state(report, "ruleset") in ("done", "exists") and setting_state(report, "toggles") == "done"
            and setting_state(report, "topic") == "done" and pin_settled(report))


def every_setting_done(manifest, report):
    """Whether every setting of this mode, secret scanning included, is
    done or was there already, so the section may say the settings were
    applied."""
    keys = ("secret_scanning", "push_protection") + (("actions_pull_requests",) if manifest["mode"] == "new" else ())
    return settings_done(report) and all(setting_state(report, key) == "done" for key in keys)


def the_settings(manifest):
    """What the setup script applies, as one phrase: the box among them only
    where the script that landed, which mode new alone brings, ticks it."""
    names = [*THE_SETTINGS, ACTIONS_SETTING] if manifest["setup_script_ticks_box"] else list(THE_SETTINGS)
    return ", ".join(names[:-1]) + ", and " + names[-1]


def installations_page(manifest):
    """Where the person may uninstall the Setup App: their own
    installations, or the organization's."""
    if manifest["owner_type"] == "Organization":
        return f"https://github.com/organizations/{manifest['repository'].split('/')[0]}/settings/installations"
    return "https://github.com/settings/installations"


def ruleset_line(manifest, report):
    repo = manifest["repository"]
    name = report.get("ruleset_name") or "Protect the default branch"
    rules = f"https://github.com/{repo}/settings/rules"
    state = setting_state(report, "ruleset")
    if state == "done":
        line = f"- The ruleset \"{name}\" for the default branch: created. It requires a pull request"
        if report.get("required_check"):
            line += (" that passes the check named \"check\" and blocks force pushes and deletions, and nobody can"
                     " bypass it. This pull request brings that check and runs it where Actions is enabled, so it can"
                     " merge once that is green; if the check never reports, or you close this pull request instead,"
                     f" remove the check from the ruleset, or the ruleset, at {rules}.")
        else:
            line += (f" and blocks force pushes and deletions; add the name of your own check to it at {rules}, so"
                     " the default branch takes only pull requests that pass it.")
        if report.get("private"):
            line += " On GitHub Free a private repository's ruleset is written but not enforced."
        return line
    if state == "exists":
        return (f"- The ruleset \"{name}\": this repository has one of that name already, which was left as it is;"
                f" check at {rules} that it requires a pull request and your checks and blocks force pushes and"
                " deletions.")
    return (f"- The ruleset \"{name}\": not created{github_said(report, 'ruleset')}. Protect the default branch, and"
            f" only it, at {rules}: require a pull request and your checks, and block force pushes and deletions.")


def check_source_line(manifest, report):
    """The check's source in the ruleset this run created, in mode new:
    pinned to GitHub Actions, and why that matters; else why not, and the
    two ways to pin it, on the ruleset's page or with the setup script."""
    if not pin_expected(report):
        return None
    state = setting_state(report, CHECK_SOURCE)
    if state == "done":
        return ("- The check \"check\" in that ruleset: taken from GitHub Actions alone, so only a workflow run"
                " satisfies it, and a commit status named \"check\", which anyone with write access can post, does"
                " not.")
    if state == "exists":
        return "- The check \"check\" in that ruleset: it named its source already, which was left as it is."
    detail = report["settings"][CHECK_SOURCE].get("detail")
    if state == "failed":
        why = f"not pinned to GitHub Actions{github_said(report, CHECK_SOURCE)}"
    else:
        why = "not pinned to GitHub Actions" + (" yet" if state == "not-yet" else "") + (f": {detail}" if detail else "")
    name = report.get("ruleset_name") or "Protect the default branch"
    return (f"- The check \"check\" in that ruleset: {why}. Until it is, a commit status named \"check\", which"
            " anyone with write access can post, satisfies the ruleset as well as GitHub Actions' run does. In the"
            f" repository's Settings, Rules, open the ruleset \"{name}\" at"
            f" https://github.com/{manifest['repository']}/settings/rules and, beside \"check\", pick GitHub Actions"
            " as the source; or, once this pull request's check has run on the default branch after the merge, run"
            f" `bash {SETUP_SCRIPT}` from a clone, which pins it too.")


def code_list(names):
    names = [f"`{name}`" for name in names]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def lend_by_hand(org):
    """How an owner of the organization lends a token by hand: the secret's
    and the variables' pages, Repository access."""
    return (f" To lend more, an owner of the organization opens the secret at"
            f" https://github.com/organizations/{org}/settings/secrets/actions, and each of {code_list(POOL_VARIABLES)}"
            f" at https://github.com/organizations/{org}/settings/variables/actions, and adds this repository under"
            " Repository access; a token is lent only by its owner's word.")


def token_lending_line(manifest, report):
    """The requester's own Claude tokens of the organization's pool, lent to
    the repository, in either mode: which were, which were left as they
    are, and how to lend more by hand; else why none was. Nothing for a
    personal account's repository, or a report from before the lending."""
    state = setting_state(report, TOKEN_LENDING)
    if manifest["owner_type"] != "Organization" or state in (None, "not-tried"):
        return None
    org = manifest["repository"].split("/")[0]
    lending = report.get("lending") if isinstance(report.get("lending"), dict) else {}
    lent, left, unreached, missing, failed = (
        [name for name in lending.get(key) if isinstance(name, str)] if isinstance(lending.get(key), list) else []
        for key in ("lent", "left", "unreached", "missing", "failed"))
    head = "- Your Claude tokens in the organization's pool:"
    by_hand = lend_by_hand(org)
    # GitHub's words where GitHub gave them, else the run's own reason.
    detail = report["settings"][TOKEN_LENDING].get("detail") or ""
    said = github_said(report, TOKEN_LENDING) if detail.startswith("HTTP ") or ": HTTP " in detail else (
        f" ({detail})" if detail else "")
    if state == "not-granted":
        return (f"{head} not lent, since the run could not make a token with the organization permissions Secrets and"
                f" Variables (Read and write){said}, most often because the {SETUP_APP} App's installation on the"
                f" organization has not granted them; an owner of the organization accepts them at"
                f" {installations_page(manifest)}.{by_hand}")
    if state == "none-owned":
        why = f"; {detail}" if detail else ""
        return (f"{head} none lent, since no token in it names you as its owner by your login and account id: the"
                " organization variable `SYMPHONY_CLAUDE_SETTINGS`, which the control panel's Tokens page writes,"
                f" gives each token's owner{why}.{by_hand}")
    parts = []
    if lent:
        parts.append(f"lent to this repository: {code_list(lent)}")
    if left:
        parts.append(f"{code_list(left)} {'reaches' if len(left) == 1 else 'reach'} this repository already, shared"
                     " with all the organization's repositories or its private ones, and"
                     f" {'is' if len(left) == 1 else 'are'} left as GitHub shares {'it' if len(left) == 1 else 'them'}")
    if unreached:
        parts.append(f"{code_list(unreached)} {'does' if len(unreached) == 1 else 'do'} not reach this repository,"
                     " shared only with the organization's private and internal repositories or in another way"
                     " than with selected ones, and the run changes no visibility; an owner of the organization"
                     " switches it to selected repositories to lend it here")
    if missing:
        parts.append(f"{code_list(missing)} {'is' if len(missing) == 1 else 'are'} not among the organization's"
                     " secrets and variables, and the run makes none")
    if failed:
        parts.append(f"not lent: {code_list(failed)}{said}")
    what = "; ".join(parts) if parts else f"not lent{said}"
    return (f"{head} {what}. Only your own tokens are lent, never another person's, and no value or visibility"
            f" was changed.{by_hand}")


def toggles_line(manifest, report):
    if setting_state(report, "toggles") == "done":
        return "- Delete head branches on merge and allow auto-merge: on."
    return (f"- Delete head branches on merge and allow auto-merge: not changed{github_said(report, 'toggles')}; tick"
            f" both under https://github.com/{manifest['repository']}/settings.")


def topic_line(manifest, report):
    """The topic is what the repository's page shows of the adoption, so
    the line says what it is for; when GitHub refused it, where to add it:
    the gear beside About on the repository's page."""
    why = ("so the repository page says it is adopted and the Symphony browser extension's button reads Ready for"
           " Symphony")
    if setting_state(report, "topic") == "done":
        was = report["settings"]["topic"].get("detail")
        if was:
            return f"- The topic `symphony`: {was}, {why}."
        return f"- The topic `symphony`: set, {why}; the topics you had stay."
    return (f"- The topic `symphony`: not set{github_said(report, 'topic')}; add it with the gear beside About on"
            f" https://github.com/{manifest['repository']}, {why}.")


def scanning_line(manifest, report):
    security = f"https://github.com/{manifest['repository']}/settings/security_analysis"
    if setting_state(report, "secret_scanning") != "done":
        return (f"- Secret scanning: not turned on{github_said(report, 'secret_scanning')}. Usually that is the plan"
                " or the visibility: a Free organization's private repository has no Secret Protection. Turn it on"
                f" under {security} if the plan offers it; push protection was not tried, since it needs scanning"
                " on.")
    if setting_state(report, "push_protection") == "done":
        return "- Secret scanning and push protection: on."
    return (f"- Secret scanning: on. Push protection: not turned on{github_said(report, 'push_protection')}; turn it"
            f" on under {security} if the plan offers it.")


def policy_words(manifest, report, tick):
    """Why GitHub's 409 keeps the box off, and what to do. GitHub gives the
    409 as the policy of the repository's owning organization, so an
    organization's repository names its owners, on its own settings page,
    or, where its enterprise forbids the box there too, the enterprise's;
    a personal account's repository has no organization, so it gets
    GitHub's words and its own settings page, and no cause GitHub did not
    give."""
    said = github_said(report, "actions_pull_requests")
    if manifest["owner_type"] != "Organization":
        return f"GitHub answered that a policy above this repository holds it{said}; {tick} once that page allows it."
    org = manifest["repository"].split("/")[0]
    return (f"the policy of the organization, or of its enterprise, forbids it{said}. An owner of the organization"
            f" allows it under Workflow permissions at https://github.com/organizations/{org}/settings/actions, or,"
            " where the enterprise forbids it there, an owner of the enterprise under the enterprise's Policies,"
            f" Actions; then {tick}.")


def actions_line(manifest, report):
    """The box under Workflow permissions, in mode new, which lets the
    template's two workflows that open pull requests with GitHub's own
    token do so: on, and what for; else why not, who may allow it, and
    what the two workflows answer with meanwhile, an issue or a link."""
    key = "actions_pull_requests"
    why = ("so `.github/workflows/protocol.yml` opens a pull request for each new release of the protocol, and"
           " `.github/workflows/add-worker.yml` one for each \"Add a worker\" issue")
    if setting_state(report, key) == "done":
        was = report["settings"][key].get("detail")
        if was:
            return f"- {ACTIONS_LABEL}: {was}, {why}."
        return (f"- {ACTIONS_LABEL}: on, {why}. It lets a workflow approve a pull request too, which matters only where"
                " a ruleset requires a review.")
    tick = f"tick it under Workflow permissions at https://github.com/{manifest['repository']}/settings/actions"
    meanwhile = ("Until it is on, `protocol.yml` brings each new release as an issue whose link opens the pull request"
                 " in one press, and `add-worker.yml` answers each \"Add a worker\" issue with the link that opens its"
                 " pull request.")
    if setting_state(report, key) == "forbidden":
        return f"- {ACTIONS_LABEL}: not turned on, since {policy_words(manifest, report, tick)} {meanwhile}"
    return f"- {ACTIONS_LABEL}: not turned on{github_said(report, key)}; {tick}. {meanwhile}"


def by_hand_pointer(manifest):
    """Where the settings are applied by hand: in mode new the setup script
    the pull request brings, in mode existing the settings pages, since the
    next steps there cover the ruleset alone."""
    repo = manifest["repository"]
    if manifest["mode"] == "new":
        return f"Step 2 of the next steps applies them by hand, with `{SETUP_SCRIPT}`."
    return ("Step 3 of the next steps protects the default branch; the two toggles are under"
            f" https://github.com/{repo}/settings, the topic symphony is added with the gear beside About on"
            f" https://github.com/{repo}, and secret scanning with push protection under"
            f" https://github.com/{repo}/settings/security_analysis, where the plan offers them.")


def stays_installed_sentence(manifest):
    """The Setup App stays installed after the run, by the owner's decision
    of 2026-10-19, acting only during an adoption run; the
    person may uninstall it whenever they like, and the sentence says
    where. A report from before that decision may carry "uninstalled",
    which nothing reads any more."""
    holds = ("Administration on this repository and, where its installation accepted them, Administration, Secrets"
             " and Variables on the organization"
             if manifest["owner_type"] == "Organization" else "Administration on this repository")
    owner = "the organization's" if manifest["owner_type"] == "Organization" else "your account's"
    return (f"The {SETUP_APP} App stays installed, acting only during an adoption run. It holds {holds};"
            " you can uninstall it at any time, from the repository's Settings, GitHub Apps, at"
            f" https://github.com/{manifest['repository']}/settings/installations, or from {owner} at"
            f" {installations_page(manifest)}. The Symphony App, which opened this pull request, stays too;"
            " uninstalling it undoes nothing here and only stops what is shared, above, from being read.")


def settings_section(manifest, report):
    """What the Setup App did in this run, or why nothing was done, so the
    person knows what is set before they merge and what is left by hand."""
    parts = ["## Settings", ""]
    named = f"`{SETUP_SCRIPT}`" if manifest["mode"] == "new" else "the template's setup script"
    what = f"the settings {named} applies ({the_settings(manifest)})"
    outcome = report["outcome"]
    if outcome == "applied":
        did = "applied in this run" if every_setting_done(manifest, report) else "was used in this run for"
        parts.append(f"The {SETUP_APP} App, which you installed on this repository, {did} {what}; what it could do"
                     " does not wait for the merge, and closing this pull request leaves it as it is:")
        parts.append("")
        pin = check_source_line(manifest, report) if manifest["mode"] == "new" else None
        parts += [ruleset_line(manifest, report), *([pin] if pin else []), toggles_line(manifest, report),
                  topic_line(manifest, report), scanning_line(manifest, report)]
        if manifest["mode"] == "new":
            parts.append(actions_line(manifest, report))
        lending = token_lending_line(manifest, report)
        if lending:
            parts.append(lending)
        parts.append("")
        parts.append(stays_installed_sentence(manifest))
    elif outcome == "not-installed":
        parts.append(f"None of the settings was changed: no token for this repository could be made from the"
                     f" {SETUP_APP} App, which means it is not installed on this repository, or its installation"
                     f" does not include it, or GitHub did not answer; so this run could not apply {what}."
                     f" {by_hand_pointer(manifest)} If you did install it, check that its installation includes this"
                     " repository and say so on your request's issue; it stays installed, and you can uninstall it at"
                     f" any time at {installations_page(manifest)}.")
    elif outcome == "front-door-broken":
        parts.append(f"None of the settings was changed: this front door's Setup App is not working (its id or"
                     " private key there is wrong, it is not installed on the front door's own repository, or GitHub"
                     " did not answer), which is for the front door's owner to put right, and the run has told them;"
                     f" so this run could not apply {what}."
                     f" {by_hand_pointer(manifest)} If you installed the Setup App, it stays installed, so a run made"
                     " once the owner has put it right can apply them; you can uninstall it at any time at"
                     f" {installations_page(manifest)}.")
    elif outcome == "not-reported":
        repo = manifest["repository"]
        # Mode new's box is under Actions, a page of its own.
        pages = [f"https://github.com/{repo}/settings/rules", f"https://github.com/{repo}/settings"]
        if manifest["mode"] == "new":
            pages.append(f"https://github.com/{repo}/settings/actions")
        parts.append("The step that applies the settings stopped before it could say what it did. If you installed"
                     f" the Setup App, some of {what} may be applied: check {', '.join(pages[:-1])} and {pages[-1]}."
                     f" {by_hand_pointer(manifest)} {stays_installed_sentence(manifest)}")
    else:
        parts.append(f"None of the settings was changed: this front door has no Setup App yet, so {what} are applied"
                     f" by hand. {by_hand_pointer(manifest)}")
    parts.append("")
    return parts


def crowd_note(report):
    """What crowd.py setup turns off again, which is worth a word only where
    the Settings above say it is on: auto-merge, which this run turned on
    with delete-on-merge, and the box for GitHub Actions' pull requests."""
    turned_on = [words for key, words in (("toggles", "auto-merge"), ("actions_pull_requests", f"\"{ACTIONS_LABEL}\""))
                 if setting_state(report, key) == "done"]
    return f", which turns {' and '.join(turned_on)} off again," if turned_on else ""


def next_steps_new(manifest, report=None):
    """The steps after the merge; with the settings applied by the Setup
    App, the setup script is not needed and the step says what is left.
    The box is named among the script's steps, and among what the setup
    issue's first box leaves, only where the script that landed ticks it:
    the issue comes from the same copy of the template, whose change that
    taught the script the box named it in that first box too."""
    repo = manifest["repository"]
    ticks = manifest["setup_script_ticks_box"]
    box = f" {ACTIONS_SETTING}," if ticks else ""
    by_hand = ("2. From a clone, on your own computer, with the GitHub CLI signed in as an administrator, run"
               " `bash scripts/setup-repo.sh`: the default branch's rules, delete-on-merge and auto-merge, the topic"
               f" symphony, secret scanning,{box} the labels and a check of `.github/CODEOWNERS`."
               " `docs/setup/owner-checklist.md` has the rest: the Claude GitHub App and its token, the Projects and"
               " the routines.")
    if settings_done(report):
        left = "GitHub's reading of `.github/CODEOWNERS`, which the file's own page shows after the merge"
        # What the plan, or the organization's policy, may refuse, and the
        # Settings above say.
        unset = ["secret scanning or push protection"] if setting_state(report, "push_protection") != "done" else []
        if ticks and setting_state(report, "actions_pull_requests") != "done":
            unset.append(ACTIONS_SETTING)
        if unset:
            left = " and ".join(unset) + ", above, and " + left
        setup = ("2. The GitHub side is set up (Settings above), so `bash scripts/setup-repo.sh` is not needed;"
                 " running it anyway changes nothing twice. `docs/setup/owner-checklist.md` has the rest: the Claude"
                 " GitHub App and its token, the Projects and the routines. The first box of the issue \"Set up this"
                 f" project\" is done but for {left}.")
    elif report is not None and report["outcome"] == "applied":
        setup = by_hand.replace("2. From a clone", "2. For what the Settings above could not do: from a clone", 1)
    else:
        setup = by_hand
    return [
        "1. Read this pull request, then merge it.",
        setup,
        "   For a project worked by volunteers on their own Claude accounts, run instead"
        f" `python3 scripts/crowd.py setup {repo} --area AREA`{crowd_note(report)} and, after reading the pull request"
        f" it opens, `python3 scripts/crowd.py finish {repo}`, as `docs/setup/crowdsourcing.md`, Part 1, says;"
        " setup-repo.sh refuses to run once crowd mode is on.",
        "3. Write the goal in `docs/project.md` and the owners in `docs/agents/OWNERSHIP.md`.",
        "4. Run `bash scripts/check.sh` once; CI runs the same as the check named \"check\".",
    ]


def next_steps_existing(manifest, report=None):
    """The steps after the merge, said for the files that landed: a workflow
    held back has no branch to protect against and renders no board, and a
    board workflow the repository had already goes on rendering it. With
    the ruleset made by the Setup App, the step says to keep it so."""
    repo = manifest["repository"]
    added = manifest["added"]
    forced = [name for rel, name in ((BOARD_WORKFLOW, "`board`"), (METRICS_WORKFLOW, "`metrics`")) if rel in added]
    rules = f"https://github.com/{repo}/settings/rules"
    if setting_state(report, "ruleset") == "done":
        protect = "3. The default branch has the ruleset above (Settings), which targets it alone."
    elif setting_state(report, "ruleset") == "exists":
        protect = (f"3. Check the ruleset you have (Settings above) at {rules}: it should protect the default"
                   " branch, and only it, require a pull request and your own checks, and block force pushes and"
                   " deletions.")
    else:
        protect = (f"3. Protect the default branch, and only it, at {rules}: require a pull request and your own"
                   " checks, and block force pushes and deletions.")
    if forced:
        protect += f" Never target {' or '.join(forced)}, which the workflows force-push."
    if BOARD_WORKFLOW in added:
        board = ("4. After the merge the next issue event renders the board at"
                 f" https://github.com/{repo}/blob/board/STATE.md; `gh workflow run board.yml --repo {repo}` renders"
                 " it now.")
    elif BOARD_WORKFLOW in manifest["kept"]:
        board = (f"4. `{BOARD_WORKFLOW}` is this repository's own and is kept, so your workflow goes on rendering"
                 f" the board at https://github.com/{repo}/blob/board/STATE.md as it does today.")
    else:
        board = (f"4. `{BOARD_WORKFLOW}` was not written (above), so nothing renders the board until the board's"
                 " workflow, its script and the vendored library are brought together by hand.")
    protocol = PROTOCOL_TEXT if PROTOCOL_TEXT in added else "the symphony plugin's claim protocol"
    return [
        "1. Read this pull request, then merge it.",
        "2. Each person who works here runs this once, after trusting the folder in Claude Code, since a project's"
        " settings name the plugin but do not download it: `claude plugin install symphony@symphony-marketplace --scope"
        " project`. `/symphony:board` in a new session then prints the board.",
        protect,
        board,
        "5. Claim the first issue: open one labelled todo, run `claude` in your clone and paste: \"Claim issue N with"
        f" /symphony:claim and carry it to a ready pull request, as {protocol} says. Where the skill names"
        " bash scripts/check.sh, run this repository's own checks instead. Do not merge.\"",
    ]


def next_steps_section(manifest, report=None):
    steps = next_steps_new(manifest, report) if manifest["mode"] == "new" else next_steps_existing(manifest, report)
    return [
        "## Next steps", "", *steps, "",
        "The same run makes the labels the board reads on this repository. Later releases of the protocol come from"
        " the public OpenSpineConsortium/symphony-protocol: from a clone of it beside yours,"
        " `python3 ../symphony-protocol/scripts/vendor.py . --consumer OpenSpineConsortium/symphony-template`, by pull"
        " request.",
    ]


def render_body(manifest, report=None):
    settings = settings_section(manifest, report) if report is not None else []
    lines = [opening(manifest), "", *changes_section(manifest), *notes_section(manifest),
             *sharing_section(manifest), *settings, *next_steps_section(manifest, report)]
    return "\n".join(lines).rstrip("\n") + "\n"


def is_report(report):
    """Whether a file's JSON is the Setup App's report: its outcome is known
    and each setting has a state and a detail of one line."""
    if not isinstance(report, dict) or report.get("schema") != SETUP_SCHEMA:
        return False
    if report.get("outcome") not in SETUP_OUTCOMES or not isinstance(report.get("settings"), dict):
        return False
    return all(isinstance(setting, dict) and isinstance(setting.get("state"), str)
               and isinstance(setting.get("detail", ""), str) and "\n" not in setting.get("detail", "")
               for setting in report["settings"].values())


def read_report(path):
    report = json.loads(Path(path).read_text(encoding="utf-8"))
    if not is_report(report):
        raise ValueError("not a report of scripts/setup.py")
    return report


def command_body(options):
    reading = options.manifest
    try:
        manifest = json.loads(Path(options.manifest).read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("schema") != MANIFEST_SCHEMA:
            raise ValueError("not a manifest of this script")
        report = None
        if options.settings:
            reading = options.settings
            report = read_report(options.settings)
            reading = options.manifest
        sys.stdout.write(title(manifest) + "\n" if options.title else render_body(manifest, report))
    except (OSError, ValueError, KeyError) as problem:
        print(f"adopt: {reading}: {problem}", file=sys.stderr)
        return 1
    return 0


# --- labels -----------------------------------------------------------------------


def template_labels(template):
    """LABELS from the template's tools/template_init.py, read without
    running it, so the board's labels have one list."""
    script = init_script(Path(template).resolve())
    for node in ast.parse(script.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "LABELS" for t in node.targets):
            labels = ast.literal_eval(node.value)
            if all(len(label) == 3 and all(isinstance(part, str) and "\t" not in part and "\n" not in part
                                           for part in label) for label in labels):
                return [tuple(label) for label in labels]
    raise AdoptError(f"{INIT_SCRIPT} holds no list LABELS of (name, colour, description)")


def labels_for(template, mode):
    labels = template_labels(template)
    return labels if mode == "new" else [label for label in labels if label[0] not in TEAM_LABELS]


def command_labels(options):
    try:
        for label in labels_for(options.template, options.mode):
            print("\t".join(label))
    except (AdoptError, OSError, ValueError, SyntaxError) as problem:
        print(f"adopt: {problem}", file=sys.stderr)
        return 1
    return 0


# --- the command line -------------------------------------------------------------


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Adopt the Symphony template into a repository.")
    commands = parser.add_subparsers(dest="command", required=True)

    reading = commands.add_parser("parse", help="the adoption form's fields as KEY=value lines")
    reading.add_argument("body", nargs="?", help="the issue's body in a file (default: standard input)")

    applying = commands.add_parser("apply", help="copy the template into the target and write a manifest")
    applying.add_argument("--template", required=True, help="a checkout of the template")
    applying.add_argument("--target", required=True, help="a checkout of the repository that adopts it")
    applying.add_argument("--repo", required=True, help="the target's OWNER/NAME")
    applying.add_argument("--creator", required=True, help="the login of the person who asked")
    applying.add_argument("--owner-type", required=True, choices=OWNER_TYPES, help="the target owner's type")
    applying.add_argument("--default-branch", required=True, help="the target's default branch")
    applying.add_argument("--mode", required=True, choices=("new", "existing"))
    applying.add_argument("--metrics", required=True, choices=("on", "off"))
    applying.add_argument("--kind-read", action="store_true",
                          help="the mode was read from the repository's tree, not chosen on a form")
    applying.add_argument("--began", action="store_true",
                          help="the run made the repository's first commit, a README, since it had none")
    applying.add_argument("--manifest", required=True, help="where to write the manifest, outside the target")
    applying.add_argument("--protocol-spec", help="symphony-protocol's spec/PROTOCOL.md, which mode existing writes as"
                          " docs/agents/PROTOCOL.md; without it, the template's own page")

    body = commands.add_parser("body", help="the pull request's text from a manifest")
    body.add_argument("--manifest", required=True)
    body.add_argument("--title", action="store_true", help="print the title instead of the body")
    body.add_argument("--settings", help="the report scripts/setup.py wrote, rendered as the section Settings")

    labels = commands.add_parser("labels", help="the board's labels as name<TAB>colour<TAB>description")
    labels.add_argument("--template", required=True)
    labels.add_argument("--mode", required=True, choices=("new", "existing"))

    naming = commands.add_parser("name", help="check a repository's name as parse would and print it")
    naming.add_argument("repository", help="OWNER/NAME")
    return parser.parse_args(argv)


COMMANDS = {"parse": command_parse, "apply": command_apply, "body": command_body, "labels": command_labels,
            "name": command_name}


def main(argv=None):
    options = parse_args(argv)
    return COMMANDS[options.command](options)


if __name__ == "__main__":
    sys.exit(main())
