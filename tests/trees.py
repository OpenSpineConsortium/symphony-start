"""Small trees for the tests: a fake template and the repositories that adopt it.

The fake template carries tests/fixtures/fake_init.py as its
tools/template_init.py: a stand-in written here, since this public
repository holds no file of the private template, so apply's subprocess
path runs for real while the real init is tested only behind SDLC_TEMPLATE
(tests/test_real_template.py). The placeholders are assembled at run time, as the
template's own tests do, so no file here carries one. Every file's content
stands in for the template's and quotes none of it: a test checks that a
file is there, filled, kept or gone, never the template's own words.
"""

import ast
import io
import json
import os
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path, PurePosixPath

TESTS = Path(__file__).resolve().parent
FIXTURES = TESTS / "fixtures"
sys.path.insert(0, str(TESTS.parent / "scripts"))

import adopt  # noqa: E402

REPO = "octo-org/widget"
CREATOR = "mona"
MARK_BEGIN = "<!-- cswap:checkpoint:begin -->"
MARK_END = "<!-- cswap:checkpoint:end -->"
# What both lists of the checkpoint block read once the init has emptied them.
EMPTY_LISTS = {"Durable decisions": ["- (none recorded)"], "Constraints": ["- (none recorded)"]}


def placeholder(name):
    return "{{" + name + "}}"


P = {name: placeholder(name) for name in ("PROJECT_NAME", "REPO", "OWNER", "CODE_OWNER", "DEFAULT_BRANCH", "YEAR")}

# The template's CLAUDE.md ends in the checkpoint block, holding its own lists.
TEMPLATE_CLAUDE = (
    f"# {P['PROJECT_NAME']}\n\nThe template's instructions.\n\n"
    f"{MARK_BEGIN}\n## Session checkpoint (kept by cswap)\n\nRead `.claude/session.md` at the start of a session.\n\n"
    "### Durable decisions\n- The template's own decision.\n### Constraints\n- The template's own constraint.\n"
    f"{MARK_END}\n"
)

TEMPLATE_FILES = {
    ".template/PENDING": "marker\n",
    ".claude/session.md": "# Session checkpoint\n\nThe template's own work in progress.\n",
    ".claude/settings.json": '{\n  "extraKnownMarketplaces": {}\n}\n',
    ".github/CODEOWNERS": f"* @{P['CODE_OWNER']}\n",
    ".github/workflows/board.yml": "name: Board\non:\n  push:\n",
    ".github/workflows/tidy.yml": "name: Tidy\non:\n  issues:\n",
    ".github/workflows/ci.yml": "name: Checks\non:\n  pull_request:\n",
    ".github/workflows/template-init.yml": "name: Template init\non:\n  push:\n",
    "CLAUDE.md": TEMPLATE_CLAUDE,
    "README.md": f"# {P['PROJECT_NAME']}\n\nClone {P['REPO']}; the default branch is {P['DEFAULT_BRANCH']}.\n",
    "LICENSE": "a license file the adoption never copies\n",
    "docs/agents/PROTOCOL.md": f"# How work is claimed\n\nThe queue is on {P['REPO']}; pushes to {P['DEFAULT_BRANCH']}.\n",
    "docs/agents/claims/README.md": f"# Claim files\n\n- Issue: https://github.com/{P['REPO']}/issues/N\n",
    "docs/setup/github.md": "# GitHub settings\n",
    "tools/VENDORED": "sdlc-protocol 0.0.0 0000000000000000000000000000000000000000\n",
    # The board's script runs the library, as the template's does.
    "tools/board.py": "from sdlc_protocol import board\n\nprint('the board', board.render())\n",
    "tools/sdlc_protocol/__init__.py": "__version__ = '0.0.0'\n",
    "tools/sdlc_protocol/board.py": "def render():\n    return ''\n",
    "tools/sdlc_protocol/__pycache__/board.cpython-312.pyc": "not a real cache\n",
    "tests/test_template.py": "import unittest\n",
    "scripts/check.sh": "#!/usr/bin/env bash\necho ok\n",
    # The one call adopt.py reads the setup script for: the template's
    # script makes it since it ticks the box that lets GitHub Actions open
    # pull requests, and never made it before.
    "scripts/setup-repo.sh": "#!/usr/bin/env bash\necho settings actions/permissions/workflow\n",
    ".git/config": "[core]\n\tbare = false\n",
}
EXECUTABLE = ("scripts/check.sh",)
METRICS = {
    ".github/workflows/metrics.yml": "name: Metrics\non:\n  schedule:\n",
    # The one key adopt.py reads the script for: the template's script writes
    # it since it counts the work by setting, and never wrote it before. Like
    # the template's, the script imports a module beside it, which imports
    # another, which imports the library inside a function, so the workflow
    # runs only where all of them landed.
    "tools/metrics.py": "import economics\n\nprint('metrics', 'by_setting', economics.priced())\n",
    "tools/economics.py": "import usage\n\n\ndef priced():\n    return usage.counted()\n",
    "tools/usage.py": "def counted():\n    from sdlc_protocol import board\n    return board.render()\n",
}
# The modules the metrics script imports, as the template's own files.
METRICS_MODULES = ("tools/economics.py", "tools/usage.py")
# Each workflow mode existing may bring, with the script it runs.
WORKFLOWS = {".github/workflows/board.yml": "tools/board.py", ".github/workflows/metrics.yml": "tools/metrics.py",
             ".github/workflows/token.yml": "tools/token_run.py"}
# The folders a script puts on its path beyond its own.
SEARCHED = adopt.SEARCH
# The script of a template from before the breakdown, which a repository
# adopted from it keeps, since no later change of the template reaches it.
METRICS_BEFORE_BREAKDOWN = "print('metrics')\n"
# The setup script of a template from before the box, kept the same way.
SETUP_SCRIPT_BEFORE_BOX = "#!/usr/bin/env bash\necho settings\n"
# The library's spec/PROTOCOL.md, which the workflow passes as --protocol-spec.
SPEC = "# The claim protocol\n\nThe library's own text, with no placeholder.\n"
LIBRARY = ("tools/VENDORED", "tools/sdlc_protocol/__init__.py", "tools/sdlc_protocol/board.py")
# The library's package, as a script imports it.
LIBRARY_PACKAGE = "sdlc_protocol"

# The protocol's files mode existing adds to a repository that has none of them.
PROTOCOL_ADDED = {
    ".github/symphony-metrics",
    ".github/workflows/board.yml",
    ".github/workflows/tidy.yml",
    "docs/agents/PROTOCOL.md",
    "docs/agents/claims/README.md",
    *LIBRARY,
    "tools/board.py",
}

THEIR_CLAUDE = "# Widget\n\nOur own rules for sessions.\n"
THEIR_SETTINGS = {"permissions": {"allow": ["Bash(make test)"]}, "model": "opus"}
# Written by hand, as a person would, so a merge that reflowed it would show.
THEIR_SETTINGS_TEXT = '{\n    "permissions": {"allow": ["Bash(make test)"]},\n    "model": "opus"\n}\n'
THEIR_FILES = {
    "CLAUDE.md": THEIR_CLAUDE,
    ".claude/settings.json": THEIR_SETTINGS_TEXT,
    "README.md": "# Widget\n\nIt makes widgets.\n",
    "tests/test_widget.py": "import unittest\n\n\nclass Widget(unittest.TestCase):\n    pass\n",
    ".github/workflows/ci.yml": "name: CI\non:\n  push:\n",
    ".git/HEAD": "ref: refs/heads/main\n",
}


def write(root, rel, data):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def make_template(root, metrics=False, only=None):
    """The fake template under root; with only, just those of its files. Its
    vendored copy carries no spec, as the real one does not."""
    root = Path(root)
    for rel, text in TEMPLATE_FILES.items():
        if only is None or rel in only:
            write(root, rel, text)
    for rel in EXECUTABLE:
        if (root / rel).exists():
            os.chmod(root / rel, 0o755)
    write(root, adopt.INIT_SCRIPT, (FIXTURES / "fake_init.py").read_bytes())
    for rel in (METRICS if metrics is True else metrics or ()):
        write(root, rel, METRICS[rel])
    return root


def make_target(root, files=None):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in (files if files is not None else {"README.md": "# widget\n"}).items():
        write(root, rel, text)
    return root


def make_checkout(root, files, ignore):
    """A git checkout under root with files and these ignore rules, so what
    the repository ignores is read for real; a plain folder ignores nothing."""
    make_target(root, dict(files, **{".gitignore": ignore}))
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    return root


def track(root, rel):
    """Put rel in the checkout's index, as a committed file of theirs is."""
    subprocess.run(["git", "-C", str(root), "add", "-f", rel], check=True, capture_output=True)


def snapshot(root):
    """Every regular file under root, .git included, as relative path -> bytes."""
    root = Path(root)
    found = {}
    for folder, dirs, names in os.walk(root):
        for name in names:
            path = Path(folder) / name
            if not path.is_symlink():
                found[path.relative_to(root).as_posix()] = path.read_bytes()
    return found


def imported_names(data):
    """The top-level name of each module a Python file imports by an absolute
    name, anywhere in it. Read here apart from adopt.py, so a test of what an
    adoption brought never takes adopt.py's word for it."""
    names = set()
    for node in ast.walk(ast.parse(data)):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


def local_module(root, folder, name):
    """The files of the tree under root by which Python finds the module name
    in folder, which it searches first for a script there."""
    return [rel for rel in (f"{folder}/{name}.py", f"{folder}/{name}/__init__.py") if (Path(root) / rel).exists()]


def unmet_imports(root, script, brought):
    """Each import of the script under root, and of every module of the tree
    it reaches in turn, that the files brought do not meet, as "file: name":
    a module found in the script's folder must be one of them, and is
    followed but for the library, which is brought whole and checked by its
    own record; any other must be one of Python's own."""
    folders = SEARCHED.get(script, (PurePosixPath(script).parent.as_posix(),))
    unmet, seen, waiting = [], set(), [script]
    while waiting:
        rel = waiting.pop()
        if rel in seen:
            continue
        seen.add(rel)
        for name in sorted(imported_names((Path(root) / rel).read_bytes())):
            found = next((hit for hit in (local_module(root, f, name) for f in folders) if hit), [])
            if not found and name in sys.stdlib_module_names:
                continue
            if not found or not set(found) <= set(brought):
                unmet.append(f"{rel}: {name}")
            elif name != LIBRARY_PACKAGE:
                waiting += found
    return unmet


def run_script(root, *argv, environ=None):
    """Run a Python script of the tree under root as a workflow does, from the
    top of the checkout, with none of this process's own Python variables, so
    nothing but the tree and Python's own modules is imported, and no token."""
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("PYTHON") and key not in ("GITHUB_TOKEN", "GH_TOKEN")}
    env.update(environ or {})
    return subprocess.run([sys.executable, "-B", *argv], cwd=root, env=env, capture_output=True, text=True)


def checkpoint_lists(text):
    """The lists of CLAUDE.md's checkpoint block, heading -> its lines; None
    when the file has no block."""
    begin, end = text.find(MARK_BEGIN), text.find(MARK_END)
    if begin == -1 or end == -1:
        return None
    lists, current = {}, None
    for line in text[begin:end].replace("\r\n", "\n").split("\n"):
        if line.startswith("### "):
            current = line[4:].strip()
            lists[current] = []
        elif current is not None and line.strip():
            lists[current].append(line.rstrip())
    return lists


def run(argv, stdin=None):
    """adopt.main with its output caught: (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    saved = sys.stdin
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        with redirect_stdout(out), redirect_stderr(err):
            code = adopt.main(argv)
    finally:
        sys.stdin = saved
    return code, out.getvalue(), err.getvalue()


def apply(template, target, manifest, mode="new", metrics="on", owner_type="User", repo=REPO, protocol_spec=None,
          creator=CREATOR, kind_read=False, began=False):
    """Run apply; (exit code, the manifest or None, stderr)."""
    argv = [
        "apply", "--template", str(template), "--target", str(target), "--repo", repo,
        "--creator", creator, "--owner-type", owner_type, "--default-branch", "main",
        "--mode", mode, "--metrics", metrics, "--manifest", str(manifest),
    ]
    if protocol_spec is not None:
        argv += ["--protocol-spec", str(protocol_spec)]
    if kind_read:
        argv.append("--kind-read")
    if began:
        argv.append("--began")
    code, _, err = run(argv)
    written = json.loads(Path(manifest).read_text()) if code == 0 else None
    return code, written, err
