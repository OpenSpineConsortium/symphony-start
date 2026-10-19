# Symphony GitHub Apps privacy statement

Version 35, 2026-10-19. This text is also at https://openspineconsortium.com/symphony/apps-privacy.html.
The Symphony browser extension has a statement of its own, at https://openspineconsortium.com/symphony/privacy.html.

Who makes the Apps: Gregory Schwing, trading as OpenSpineConsortium ("the developer"). Questions:
the contact on https://openspineconsortium.com/symphony/.

Symphony is two GitHub Apps. **SymphonyBoard** (github.com/apps/symphonyboard) brings the Symphony
template, or its claim protocol, into a repository by pull request, afterwards reads one branch
of that repository once a day for anonymous aggregates and, where the repository holds the claim
protocol without the whole template, offers it, by another pull request, the newer versions the
template comes to hold of the files Symphony's board and control panel run on. **Symphony Setup**
(github.com/apps/symphony-setup) applies up to seven settings to a repository in the adoption run,
and stays installed, acting only
during an adoption run, until you uninstall it. Both work only through GitHub: nothing of yours goes
anywhere but to GitHub's own API, to your own repository and, as aggregates, to the developer, save
a Claude token you lend, with your login and account id, into the pool of the developer's own
organization, which that organization then holds (the control panel, below). This
statement says what each App can see, what it writes, what the developer receives and keeps, and
how to stop any of it.

## What each App asks for, and why

The unit of consent is the installation. Whatever repositories you give an App when you install it
("All repositories" or "Only select repositories"), the App can read what its permissions allow on
every one of them, and this statement applies to each.

SymphonyBoard asks for eleven repository permissions: Contents (read and write), to read your default
branch and push the branch `symphony/adopt` and, in a repository with no commit yet, to make its first
commit, a README, for the Sync run's reads of your default branch and of the branch `symphony/sync`
and its writes of that branch (the section on the Sync run), and for the control panel's writes of a
file, as you, which the section on the control panel lists; Pull requests (read and write), to open
the adoption pull request and, only when you asked for it on the form, merge it, and for the Sync run
to read the pull requests from the branch `symphony/sync` and to open its own or write its description
anew; Issues (read and write), to
make the board's labels and, in a new repository, open the issue "Set up this project"; Checks (read
and write), to post the protocol check as a check run where the developer runs the App's server;
Workflows (read and write), because the adoption's pull request and the Sync run's bring files under
`.github/workflows`, which GitHub lets no token write without it; Codespaces (read and write), which
the control panel's Tokens page used up to version 13 of this statement to make a Codespace and no
longer uses, and which stays
on the App until the developer takes it off; Actions (read and write), for the control panel's buttons
that start a workflow run by hand, such as the Tokens page's "Read use now" and "Add Token" and the
presses of its box "Your token", and its reads
of the repository's workflow runs, their jobs and a job's log (the control panel, below); Administration (read and write), for the
control panel's Share tab and its Notebooks tab's "Make private", each as you (the control panel, below): the Share tab
reads the invitations waiting for an answer and, when you press the button that says so, invites a person you name by
their GitHub username, or one who asked to join, as a collaborator on the repository, gives a collaborator or a waiting
invitation a new role, removes a collaborator or withdraws an invitation, and the Notebooks tab makes a notebook's public
or internal repository private when you press "Make private" and confirm; no adoption run, workflow or other page uses it;
Secrets (read and write), for the control panel's Folders tab, which reads whether the repository's
secret SYMPHONY_DRIVE_REFRESH is set and, when you press Track, saves a drive's refresh token as
that secret, and for the Tokens page on a personal account's repository, which holds its Claude
tokens as secrets of its own, each as you (the control panel, below); Variables (read and write), for
the Tokens page on a personal account's repository, which holds a Claude slot's settings and the list
of accounts (SYMPHONY_CLAUDE_SETTINGS and SYMPHONY_CLAUDE_ACCOUNTS) as that repository's own Actions
variables, each as you (the control panel, below); and Metadata (read), which
every App has, to list the
repositories it reaches. It subscribes to five event types (issues, issue comments, pull requests,
pushes and check suites), which GitHub delivers only while the App's webhook is turned on; as this
statement is written, it is turned off, and the section on the server below applies from the day
it is turned on.

When it adopts the whole template into a new repository, SymphonyBoard makes a second token for
that repository alone with Checks read-only. With it, the run reads the check runs named "check" on
the commit it pushed to the branch symphony/adopt, only to see whether GitHub Actions has reported
that check, for up to ten minutes. It keeps nothing it reads and revokes the token when the
settings step ends.

On an organization, SymphonyBoard also asks for two organization permissions: Secrets (read and
write) and Variables (read and write), for the control panel's Tokens page, which saves a Claude
account's token as one of the organization's Actions secrets (the control panel, below). A page you
are signed in to makes those writes, as you, where you are an owner of the organization. What the
App itself writes is in the organization's pool of Claude tokens, and only there: where someone
lends a token through the Token workflow, from the Tokens page where they are not an owner of the
organization or from an issue whoever they are (the control panel, below), the organization's own
Token workflow makes the writes for them, on SymphonyBoard's installation token: one organization
secret, the next free slot SYMPHONY_CLAUDE_n, and two organization variables, the list
SYMPHONY_CLAUDE_ACCOUNTS and SYMPHONY_CLAUDE_SETTINGS, which holds the settings of every slot (for
this one, a random id, the login and the account id of the person who lent it and, for a token lent
with no say, the word organization). The workflow adds each repository the token is lent to to the
lists of repositories that may read the secret and the two variables, and takes a repository off
the variables' lists only when a lender asks to take their own token back from it, whether or not
their token reached it, or deletes their token (the control panel, below), and no other of the
numbered slots SYMPHONY_CLAUDE_1 to SYMPHONY_CLAUDE_32 reaches it, none of them being on in every
repository or in every private one, the workflow not counting the slot main, CLAUDE_CODE_OAUTH_TOKEN,
whose reach it does not read, so that a repository only that secret still reaches loses the two
variables too. So every lender's login and account id reach every repository a token was ever lent
to and every repository an owner's Tokens page showed while it saved a token's settings or removed
a slot (the control panel, below), save one the workflow took off so or an owner took off by hand,
or every repository, or every private one, where an owner set the variables so.
The repository's Claude workflows pass those settings to their steps, and GitHub prints a step's
settings in its run's log, which anyone can read on a public repository; the one that answers a
mention of @claude starts its job only where GitHub marks whoever wrote the comment, the review or
the issue that mentions it as the repository's owner, a member of its organization or a
collaborator, so for anyone else's mention GitHub still lists a run but marks its job skipped: no
runner starts, no step runs or prints the settings, and the Claude token is not used. The Token
workflow itself, on SymphonyBoard's token, reads the names and records of the organization's
Actions secrets, never a value, which GitHub gives no one, to find a free slot and which slots hold
a token; the public key GitHub gives for sealing them; the records of the two variables
SYMPHONY_CLAUDE_ACCOUNTS and SYMPHONY_CLAUDE_SETTINGS, which hold their values, the second with
the login of each slot's owner and, where it holds one, their account id; and the public GitHub
record of the person it acts for,
for their account id. For a lend with no say it reads the organization variable SYMPHONY_LEND_TO,
where the owners list the repositories such a token runs on; where the control panel names another
of the organization's repositories to lend the token to (below), it reads that repository's record
and the person's permission on it; and, for the person's own token alone, it lists the repositories
the token reaches, takes it off one or deletes it, reading for the last two which repositories each
other numbered slot of the pool, SYMPHONY_CLAUDE_1 to SYMPHONY_CLAUDE_32, reaches, never which the
slot main reaches, in the run's memory alone, to know whether to take the two variables off. The
Claude token is held on the runner, in a file only the runner's
user can read, from the sign-in to the step that seals it and writes the sealed box to GitHub and
then deletes the file; it is never printed, posted or readable from GitHub. The App writes no other
secret or variable of its own. GitHub never gives a secret's value back to anyone, the App
included.

The Token workflow can mint SymphonyBoard's token only where the App's private key is, which, as
the section on keys says, is the developer's own repositories. So, as this statement is written,
the only pool the App writes is the one of the developer's own organization, OpenSpineConsortium:
a token lent there, from the page or from an issue, is held by the developer's organization as an
Actions secret its workflows run on, which its owners, the developer among them, place and delete
and which GitHub never shows them, beside the lender's login and account id, which they see; as with
any Actions secret, whoever may write to a repository it is lent to, the developer among them, can
have a workflow there use the token or send it elsewhere. The developer's collector receives nothing
of it. Anywhere else, where the repository has no Actions variable SDLC_APP_ID, which names the App
beside its key, the Token workflow's two jobs that would use the key, the one that stores a token into
the organization's pool for its lender and the one that manages a token there, do not run, in the Token
workflow as the template holds it since version 34 of this statement, which an adoption of either kind
brings from then on and the Sync run offers a repository that holds the claim protocol alone: a run
asked for either, by the control panel's Tokens page or by an issue, outside crowd mode reads the
issue's comments, so as to say it once, says on the issue, with the repository's own GitHub token,
that the repository does not hold the App's settings and so stores no token into a pool, and that an
owner of the organization adds one with Add Token, and, where an issue started the run, closes that
issue as not planned, as a run in crowd mode does too, saying on the issue only that the repository
holds no Claude token (the control panel, below). A copy of the whole template made before then keeps
the Token workflow it was
made with, which neither the Sync run nor the protocol's releases replace, and where that workflow has
those jobs, the store job in a copy made since 00:13 UTC on 2026-10-19 and the manage job too in one
made since 02:26 UTC that day, they start there outside crowd mode without the variable, GitHub
recording each such run as a deployment to their environment token-store, which it makes in the
repository the first time one runs where the repository's plan lets it have environments, and store
and manage nothing:
each stops at the first step that needs the App's token, which in a copy made before 02:26 UTC that day
comes after the Claude sign-in, the token then held on the runner and deleted unsaved, and the run then
reads the issue's comments, says on the issue only that it stopped and closes an issue that started it
as not planned. The job that makes a token for a page that stores it itself runs there as anywhere (the
control panel, below).

SymphonyBoard also asks for one account permission, Codespaces user secrets (read and write), which
GitHub asks each person for when they sign in with GitHub on the control panel. The Tokens page used
it up to version 13 of this statement to hand its GitHub sign-in to a Codespace; it no longer uses
it, and it stays on the App until the developer takes it off.

Symphony Setup asks for two repository permissions, Administration (read and write), for the seven
settings below, and Metadata (read), and, on an organization, three organization permissions:
Administration (read and write), Secrets (read and write) and Variables (read and write). It uses
Administration for one thing only: where the organization holds
off "Allow GitHub Actions to create and approve pull requests" for its repositories, as a new
organization does, and the repository takes the whole template, the run allows that box for the
organization, leaving the default permissions of GitHub Actions' token as they were, and then ticks
it on the repository. With Administration it reads and changes no other setting of the organization. That setting of
the organization stays allowed after the run, and repositories the organization makes later inherit
it; an owner turns it off under the organization's Settings, Actions, General, Workflow permissions.

It uses Secrets and Variables for one thing only, lending the person who asked for the adoption their own Claude tokens of the organization's pool,
never one they lent with no say, which only the organization's owners place, and only where the installation on the
organization has them, which GitHub asks an owner of the organization to accept. In the adoption run
of one of the organization's repositories, of either kind, the run first reads, with the Setup App's
own key, its installation on the organization, to make a token with the organization permissions
Secrets and Variables (write), which reach every secret and variable of the organization though the
run touches only those named here, and the repository permission Metadata (read) on the one
repository; the token is kept in a file in the run's temporary directory and never in its log, and
is revoked once the settings are applied or, where GitHub refuses the revocation, which the run
does not say, runs out within the hour. With it, before the pull request is opened, the run reads
the value of the organization variable SYMPHONY_CLAUDE_SETTINGS, which gives each slot's owner by
login and account id, and keeps the slots whose owner is the person who asked by both: the login of
the account that opened the request's issue, compared without case, and that account's id, which the
run takes from the issue. A slot that kept no account id is never lent, since a login passes to
whoever takes it once an account is renamed or deleted, and a run given no account id reads none of
the organization's secrets or variables. Nor is a slot ever lent whose settings carry the word
organization, a token its owner lent with no say: the run counts it as none of the person's, reads
no record of its secret and names it nowhere, so where the person has no other token in the pool
that the run may lend, the pull request says, as below, that no token in it names them as its owner
by their login and account id, and the log reads "token lending: no tokens lent". For each slot it
keeps it reads the record of the slot's organization secret
(SYMPHONY_CLAUDE_1 to SYMPHONY_CLAUDE_32, and CLAUDE_CODE_OAUTH_TOKEN for the slot main), its name, when it was made and last changed, and whether it is shared with all
the organization's repositories, its private ones or selected ones, never which ones and never its
value, which GitHub gives no one, and adds the repository to the repositories that may read it.
Where one of those secrets was lent so, or reaches the repository already, shared with all the organization's
repositories or, for a private or internal repository, with its private ones, it does the same for
the two variables SYMPHONY_CLAUDE_ACCOUNTS and SYMPHONY_CLAUDE_SETTINGS, whose records hold their
values, so it reads the value of SYMPHONY_CLAUDE_ACCOUNTS, the list of the pool's slots, and the
settings again. The repository's Claude workflows can then run on those tokens, except in a private repository of
an organization on GitHub Free, which GitHub lets read no organization secret or variable, though
the run, which reads no plan, lends them all the same and calls them lent or left as they were; and, as with any
Actions secret, whoever may write to that repository can have a workflow there use your token or
send it elsewhere. It adds a repository only to the list of a secret or a variable that exists and
is shared with selected repositories: it changes no visibility, creates nothing and lends no one
else's slot. The two variables' values stay in the run's memory. The run's public log has one line
for this, "token lending: tokens lent" or "token lending: no tokens lent", and says neither which
nor how many, nor why none was lent; since only the asker's own tokens are lent, "tokens lent" does
tell anyone who reads it that the person who opened the request holds a token of the organization's
pool and that the installation has the two permissions. The pull request in your repository, which
anyone who can read the repository reads, everyone where it is public, names each of your secrets and, where one of them was lent or reaches the repository already, each
of the two variables, with what became of it (lent, left as it was, not reaching the repository,
missing, or not lent because GitHub refused it or could not be reached, quoting one reason: GitHub's
answer, or the run's word that GitHub was out of reach, for the first of the two variables not
lent, else for the first of your secrets not lent), and says why where none was lent. Where none
of the pool's tokens is yours, it says so with the same hint every time, to press Add Token on the
control panel's Tokens page, so it never says whether a slot names your login. Once the two
variables are lent, the settings variable, with every slot owner's login and account id, reaches the
repository too, even where the log says "no tokens lent", as the section on SymphonyBoard's pool
says of every repository a token is lent to. What is lent stays lent whatever becomes of the pull
request, closed without merging or never opened; where the run stops after lending and before it
opens the pull request, nothing the run writes names what it lent; where the settings step itself failed after lending,
the log reads "token lending: no tokens lent" and the pull request, opened all the same, says only
that some settings may be applied and names nothing lent; and where the run is cancelled or runs
out of time in that step, its log has no line for the lending. Where the installation has not
these two permissions, the run still reads the installation and asks GitHub for the token, lends
nothing, and the pull request says your tokens were not lent and where an owner accepts the
permissions; for a person's own repository none of this runs; either way the log reads "token
lending: no tokens lent" and the adoption otherwise runs as before. An owner of the organization
sees each secret's and variable's list, and takes a repository off it, under the organization's
Settings, Secrets and variables, Actions, Repository access; a token's owner may take their own
token off a repository from the control panel's Tokens page, unless they lent it with no say, which
they may only delete, as the section on the control panel says.

It has no webhook and receives no event. It is meant to be
installed on the repository being adopted. It stays installed after the run, after an adoption or
after a request refused because the repository is adopted already, acting only during an adoption
run. Its token is made only during a run and revoked when the run's settings are applied. You can uninstall it at any time from the repository's or the organization's Settings,
GitHub Apps; the pull request and the run's answer say so.

In that same run, once GitHub Actions has reported the check, Symphony Setup reads the repository's
own rulesets and writes back the ruleset "Protect the default branch" it created earlier in the run.
The only change is GitHub Actions as the source of its required check "check". It never reads or
changes an organization's ruleset or a ruleset the repository already had.

## The adoption

Installing SymphonyBoard sends you on to Symphony Setup's install page, and that install
sends you to a public form on the front door repository,
github.com/OpenSpineConsortium/symphony-start. Pressing Create there opens a public issue in your
GitHub name; the issue carries what the form held (your installation's number, or a repository name
you typed, the kind, the merge choice and one box) and the run's answers, and it is closed when the run is done,
never deleted. A repository the run learns only by its number is never named on the front door: its
name, its owner's, its default branch's, your login and your account's id are masked in the adoption job's public log after the step that names the repository, whose settings
show your login and your account's id as the issue you opened gives them (the request job's step
that resolves the installation, before it, shows your login too), and the issue is answered with "your repository". A name you typed into the form is public already, and the
run names it in its answers, and its public log shows your login in the settings of the request job's step that checks you
administer it, and your login and your account's id in the settings of each step of the adoption
job from the one that names the repository on. The front door's public logs do show the installation's number, the repository's
numeric id, whether the repository belongs to an organization, which the steps of the token lending
run for or skip, the kind the run read (whether the repository was empty), how many files
it added, replaced, kept or skipped, and the commit ids of your default branch and of the template.

To do its work the run reads, from the repository being adopted: the default branch and the commit
on it or, where the default branch is not there yet, whether the repository has any branch at all,
whether a branch `symphony/adopt` exists and has a pull request, whether `docs/agents/PROTOCOL.md`
exists, the one word in `.github/symphony-adopt` and `.github/symphony-metrics` and in each under
its name before the rename to Symphony, `.github/sdlc-adopt` and `.github/sdlc-metrics`, the full
listing of the default branch's tree (to decide the kind), a checkout of that branch at depth one (to add the
files) and whether you administer the repository. With Symphony Setup installed, the run also reads the repository's record, keeping its id, to name
it when lending, and whether it is public, private or internal, to say in the pull request whether
GitHub enforces its ruleset and, in an organization's repository, which of the organization's
secrets reach it already; and its rulesets, its topics and its workflow permissions for GitHub
Actions, to leave what is there as it is. When the
form carries an installation's number and no name, the run reads that installation's record and,
when the number is Symphony Setup's, SymphonyBoard's own list of its installations, to find the one
on the same account; then it asks the same of each repository both Apps reach, and whether you
administer it, to choose the newest one with no adoption yet. Everything
read lives on GitHub's runner for the length of the run and goes with it; nothing of it is kept or
sent elsewhere.

What the run writes to your repository, as the App's bot: the board's labels, one commit on the
branch `symphony/adopt`, one pull request from it, and, in a repository that held nothing yet, the
issue "Set up this project". In a repository with no commit at all, the run first makes one, as
GitHub's own "Add a README file" does: a `README.md` holding the repository's name, on the default
branch, which the pull request goes into; the whole template's README takes its place when you merge. The pull request's body lists every file it brings, names the GitHub
login of the person who asked, says whether the
repository is private and, where the Setup App was installed, quotes GitHub's own answer for each
setting, which may name your account's plan; in an organization's new repository, the pull request
also writes that login into `.github/CODEOWNERS`. With Symphony Setup installed, the run creates the
default branch's ruleset, turns on delete-head-branches and auto-merge, adds the topic `symphony` to
the repository's topics (the sign on the repository's page that it is adopted, which anyone can see
there and the Symphony browser extension reads from the page; your other topics stay), turns on secret scanning and push protection where your plan and visibility allow it, in a
repository that takes the whole template ticks "Allow GitHub Actions to create and approve pull requests" where
your organization and its enterprise allow it, in an organization's repository lends it your own
Claude tokens of the organization's pool, but none you lent with no say, and, beside one of them, the pool's two variables (as the
section on what each App asks for says), and, in a repository that takes the whole template,
once GitHub Actions has reported the check named "check" on the branch symphony/adopt, sets GitHub
Actions as that check's only source in the ruleset it created, then revokes the Setup App's token;
the Setup App stays installed. Unless you chose on the form to review the pull request first, the
run merges it or arms auto-merge. Everything else lands only when you merge. Closing the pull
request instead leaves the labels, the README the run made in a
repository that had no commit, the branch, the settings, the topic and the issue for you to undo, and, in an organization's
repository, the tokens and the two variables lent to it (as the section on what each App asks for
says), which an owner of the organization takes off, as a token's owner may take their own unless they
lent it with no say.

The protocol alone brings, among its files, these workflows: the board's and the one that tidies a
closed issue's claim branch, the metrics workflow only beside a switch it could write (the section on
sharing) and, since version 34 of this statement, the Token workflow, which the control panel's Tokens
page starts to make a Claude token on your repository's own runner (the section on the control panel)
and which every issue opened in your repository starts as well, its jobs skipping unless the issue's
description begins with the line that asks it to lend or manage a token. A workflow that runs a script
comes with that script and every module of the template it imports, or not at all: it stays out where
anything of yours, a file, a link or a folder, stands where one of them goes, unless it is a file, or a
link to a file in the repository outside its `.git`, that holds the template's version byte for byte;
where a file of yours, or a link of yours to anything but a folder in the repository outside its
`.git`, stands where one of their folders goes; where your repository ignores one of them; where Python
would import a file of yours in place of one of them; where one of its modules stays out with another
of these workflows that imports it too; or, for the board's workflow and the metrics workflow, whose
scripts import the protocol's library, which the adoption brings under `tools/sdlc_protocol`, where
that library will not be the template's once the pull request is merged. The pull request names the
file that held it back. Once adopted for the protocol alone, a repository is offered the template's
newer versions of these files by the Sync run (the next section), which offers nothing to a copy of the
whole template that keeps its `.github/workflows/protocol.yml`.

The adoption's files come from the developer's private template repository, read with a token that
holds Contents read on that one repository and is revoked right after the checkout; only the files
in the pull request reach you.

## The Sync run

An adoption copies the template's files once. So that a repository keeps up with the template's later
versions of the files Symphony's board and the control panel run on, the developer runs a workflow in
the template's own repository, the Sync run (the template's `.github/workflows/sync.yml` and
`tools/sync_adopted.py`), whenever the board's, tidy, metrics or Token workflow, `scripts/tokens.py` or
any file under `tools/` changes on the template's default branch, once a week, on Tuesdays at 07:29
UTC, and when someone who may write to the template's repository starts it by hand. It runs nowhere but
there, on GitHub Actions, where SymphonyBoard's private key is kept: with the key, which it hands to
openssl through a pipe and never writes to a file, the run signs the App's own credential, which lasts
less than ten minutes; the template's own GitHub token there only reads the template. With that
credential it reads the App's own record, for the name its pull requests and commits carry, by which it
tells them from anyone else's, and the list of SymphonyBoard's installations, the first five thousand
where there are more, with the account each is on. For each installation in turn, or, in a run started
by hand that names one account, for that
account's alone, it asks GitHub for an installation token with Contents, Pull requests and Workflows
(write), Workflows because the files it brings include workflows, which GitHub lets no token write
without it, and Metadata (read); reads the list of the repositories that installation reaches, the
first five thousand where it reaches more, with the record GitHub gives of each; offers each repository
what this section says or, where GitHub fails to
give that list whole, offers none of them and counts that installation; and then revokes the token and
goes on to the next installation whatever GitHub answers, so a token GitHub did not revoke, which the
run does not say, runs out within the hour. An installation for which GitHub answers the request for a
token with the status 403, 404 or 422, as it does for a suspended one, is counted and passed over;
where GitHub answers that request with any other status from 300 up, with an answer the run cannot
read, or not at all, the run stops there, and the installations after it wait for its next run.

It passes over, reading nothing more of it, the template's and the front door's own repositories and
any repository that is archived, disabled or a fork. Of every other it reads, with that token, the
default branch's newest commit as git records it (its author's and committer's names, e-mail addresses
and dates, its message, its parents, its signature where it has one and its tree, of which the run uses
the tree) and the full listing of that tree: each file's path, its mode, its size and the id git gives
its contents, never the contents. It passes over a repository with no commit, one whose listing GitHub
gives cut short, as it does for a very large tree, and one whose default branch holds no file
`docs/agents/PROTOCOL.md`, which every adoption from the front door brings and every copy of the
template carries. It then reads, in turn, the text of each of `.github/symphony-sync`, the Sync run's
own switch, `.github/symphony-adopt`, the adoption's, and `.github/sdlc-adopt`, that switch's name
before the rename to Symphony, that the default branch holds, until one holds the word `off`, in
capitals or not, with nothing beside it but white space (a byte-order mark before it, which the
adoption's own reading of `.github/symphony-adopt` passes over, keeps it from counting here): such a
repository has opted out, and the run does nothing more there, writing nothing and leaving as they are
any branch and pull request an earlier offer left. Where none says `off`, it passes over too, writing
nothing there, a repository whose default branch holds `.github/workflows/protocol.yml`, as every copy
of the whole template does unless its owner has removed that workflow, whether the front door adopted
the whole template into it or it was made
with "Use this template": such a copy takes the protocol's releases by that workflow and runs the
template's own tests on these scripts, tests the files alone would leave behind, so the Sync run offers
files only to a repository that holds the claim protocol without that workflow, as one adopted for the
protocol alone does. A copy of the whole template made since the template holds the Sync run carries
`.github/workflows/sync.yml` too, whose runs there skip its one job, so nothing of the Sync run runs
outside the template's own repository. It reads no other file of yours, beyond the lines of changed
files that GitHub's comparison of your default branch with the branch `symphony/sync` shows (below): it
compares your files with the template's by the ids in the listing alone.

What it offers comes in units, as the adoption of the protocol alone brings them: the vendored library
with its record (`tools/sdlc_protocol` and `tools/VENDORED`), the board's workflow with its script, the
workflow that tidies closed claims, the metrics workflow with the scripts it runs and the Token
workflow with the scripts it runs, each script with every module of the template it imports and every
one it loads by its path, as the metrics workflow's `tools/usage.py` loads `tools/profile.py`, all as
the template holds them at its newest commit. A unit is offered whole or not at all. A file of yours is
replaced only where it holds, by that id, a version that some commit in the history of the template's
default branch, the commits of each branch merged into it among them, has held at that path; where one
of a unit's files is anything else, a file of your own, a link, a submodule or
a folder, where a file, a link or a submodule of yours stands where a folder of the unit's goes, or
where Python would import a file of yours in place of one of the unit's modules, the unit is held back,
and a pull request the run opens or writes anew for the other units names that file. Whether your
default branch has a unit is read from one file of it alone, the unit's workflow or, for the library,
`tools/VENDORED`. A unit your default branch does not have is not added, since you removed it or never
took it, with one exception, the Token workflow and its scripts, which are added where they are
missing; a unit you have gains every file of it that your default branch lacks, whether a module its
newer scripts import or load by its path, a file the newer library holds that yours does not, a script
or module of the unit you deleted while keeping its workflow or, where `tools/VENDORED` stands without
`tools/sdlc_protocol`, the whole library. So the metrics workflow, which shares aggregates,
is offered only to a repository that has it already, whose switch `.github/symphony-metrics` still
decides whether anything is shared (the section on sharing). A unit whose scripts import the library is
offered only where the library is the template's already or comes in the same pull request, and the
library is held back where a unit that imports it is. Where nothing needs changing, or every unit that
would change is held back, the run writes nothing: it opens no pull request, names no file and leaves
as it is any pull request an earlier run opened.

Where something does, it works out one value from the files it would bring, each one's path with the
mode and the id git gives the template's version of it, and reads the twenty newest pull requests from
the branch `symphony/sync`, with the record GitHub gives of each (its title, its description, its
author, its state and its two branches among them). Of these it uses only those SymphonyBoard opened
into your default branch: whether each is open, the number and the description of the open one or,
where none is open, the description of the newest, and whether that newest one was merged. Where none
of them is open and the newest was closed without its merge and its description holds that same value,
as it does where that pull request offered those same files, each at the same version, it stops there,
writing nothing. Otherwise it reads whether the branch `symphony/sync` exists and, where it does,
GitHub's comparison of your default branch with it, which gives the records of your default branch's
newest commit, of the newest commit the two share and of every commit the branch holds beyond your
default branch, as many as GitHub lists in one answer, each with its author's and committer's names,
e-mail addresses, dates and accounts, its message, its signature where it has one, its tree and its
parents; how many such commits there are;
and the files the branch changes since the commit the two share, with lines of each change. Of it the
run uses how many commits the branch holds beyond your default branch and, of each one listed, its
author's account and how many parents it has. Where one of those commits is neither SymphonyBoard's, by
its author's account, nor a merge, because someone pushed a commit of their own to the branch, or where
the branch holds more of them than GitHub lists, the run leaves the branch and any pull request from it
as they are, writing nothing, and offers that repository nothing more while the branch holds such a
commit, or more commits than GitHub lists, beyond your default branch. A merge made on the branch, such
as GitHub's Update branch makes,
holds nothing back by itself, whoever made it, and the run's next offer drops it from the branch with
whatever it brought; but a commit the merge brought in that your default branch does not hold is one of
the commits the branch holds beyond your default branch, so where such a commit is neither
SymphonyBoard's nor a merge, as a commit of another branch of yours merged in may be, the run leaves
the branch and any pull request from it as they are, as it does for a commit pushed to the branch.
Where the branch exists and one of SymphonyBoard's pull requests from it is open and its
description holds that same value, the run also reads the branch's newest commit as git records it (its
author's and committer's names, e-mail addresses and dates, its message, its parents, its signature
where it has one and its tree, of which the run uses the parents), and it stops there, writing nothing,
where that commit stands straight on your default branch's newest commit, its one parent, as the run's
own commit does. Otherwise it writes, as SymphonyBoard, each file it brings as a git object in your
repository, a file that is not UTF-8 text in a call of its own and the rest in the call that writes the
tree; one tree, your default branch's tree with those files in place; and one commit, whose message is
"Bring Symphony's board files up to date" followed by a blank line and the line "Offered by the
Symphony template's sync.", on your default branch's newest commit, with SymphonyBoard as its author
and committer. It sets the branch `symphony/sync` to that commit, making the branch or moving it by
force,
so the branch holds the newest offer alone and an earlier offer's commit, and any merge made on the
branch, is dropped from it. It then opens one pull request from that branch into your default branch,
titled "Bring Symphony's board files up to date", or, where one SymphonyBoard opened from that branch
into your default branch is open already, writes that pull request's description anew. Where GitHub
refuses to open it, as it does while a pull request someone else opened from that branch into your
default branch stands open, the branch keeps the commit the run moved it to, with no pull request of
SymphonyBoard's from it, and the repository is counted refused; and since no open pull request of
SymphonyBoard's then holds that value, each later run that gets this far writes the offer again, as a
new commit on your default branch's newest commit, moves the branch to it by force and asks again to
open the pull request, so that the other pull request shows each move, with the offer as its changes.
The description
lists every file the pull request brings, names each unit held back and why, by the file of yours that
held it or, for the library and a unit that imports it, by the unit or the library it waits on, says
how to stop the offers, and begins with a hidden line holding the value worked out from the files
offered, a digest (SHA-256) of each one's path with the mode and the id git gives the template's
version of it. So a pull request you close without merging is not offered again while the files it
would bring, each at the template's version, stay the same, whatever else changes on your default
branch; once they differ, because the template changed, added or dropped one of them or because a
change on your default branch makes one of them current, holds a unit back or lets one through, the
next run offers them again, in a new pull request. An open one is built again whenever a run finds the
files offered changed, that hidden line gone from its description, or the branch's newest commit
anything but one commit straight on your default branch's newest commit, as it is once anything is
committed to your default branch or a merge is made on the branch: the run then writes the offer again
on your default branch's newest commit, moves the branch to it and writes the description anew. Where
a call fails, or the run stops, after the run has written the files, the tree or the commit and before
the branch `symphony/sync` points to that commit, as one fails where a rule of your repository refuses
SymphonyBoard the branch, the objects it wrote stay in your repository's storage with no branch pointing
to them, holding the
template's files, your own tree's listing with those files in place and, where it got that far, the
commit described above, with its message, SymphonyBoard as its author and committer and your default
branch's newest commit as its parent, and nothing else.

Like any branch and pull request an App makes, and as the adoption's do, the branch and the pull
request start, on your repository's own token and Actions allowance, the workflows your repository runs
on a push, a new branch or a pull request, the offered ones among them, each in the version the branch
holds, save one that runs on `pull_request_target`, which GitHub runs in your default branch's version.
Nothing on your default branch changes until you merge the pull request. The run keeps
nothing it reads beyond the run, holding it in its memory on GitHub's runner, sends nothing anywhere
but GitHub's API, and the developer's collector receives nothing from it. Its log, which whoever may
read the template's repository can read, every member of the developer's enterprise while the template
is internal, says only how many repositories met each outcome (offered, updated, offered already, up to
date, declined, opted out, not adopted, whole template, for a repository that holds
`.github/workflows/protocol.yml` and is offered nothing, skipped, branch theirs, refused, for a call
GitHub answered with a status from 400 to 499 other than 429, and failed), for how many installations
GitHub gave no token and for how many it failed to give the list of the repositories they reach, with
those two counts and the count refused repeated as warnings on the run's page, or, where the run
stops, in place of all those counts, the method of the call GitHub refused and the status it answered
with or, where GitHub gave no answer or one the run could not read, or something else stopped it, the
error Python met, with the lines of code, the run's own and Python's, where it met it; it names no
repository, account or file, save that a run started by hand for one account shows that account's login
as whoever started it typed it. A repository where a call fails is counted and the run goes on to the
next, starting that one over in its next run. Uninstalling SymphonyBoard stops the Sync run's reads and
offers, and so does taking a repository off the installation's list, for that repository; an offer's
branch and pull
request stay until you close and delete them.

## Field metrics: what the developer receives

A repository Symphony set up runs its own workflow once a day, with GitHub's own token, which writes
one file, `METRICS.json`, to a branch named `metrics` of your repository: eleven counts (claims,
pull requests opened, merged, closed unmerged, reviews, changes requested, check runs passed and
failed, conflicts seen, released claims, contributors), the median and 90th percentile of three
waits in seconds, two rates, the time it was made, the number of days it covers (30), the protocol's
release number and the short id of its commit, and the words that name the schema and the switch.
Since version 2 of this statement the file also holds counts of how the work ran in parallel, so
that failure can be compared between one person running several Claude Code sessions at once and
several people working at once: seventeen counts of the people who opened pull requests, the Claude
Code sessions named on them, how many named one, the most pull requests, people and sessions of one
person at work at the same moment, the conflicts the board marked or GitHub reports on open pull
requests, and the pull requests the run could not read in full; for each of eight work settings
(nothing else at work beside it; one session's several pull requests; one person's several sessions;
several people; several people beside one person's several sessions; not known; the repository's own
Claude workflows; other apps and bots), thirteen counts and sums for the pull requests that ended in
the 30 days and those still open, such as how many merged, met a conflict or shared a changed file
with work beside them, and how long they were at work; and, for four kinds of pairs of pull requests
at work at the same time, seven counts of how many pairs there were and how many worked at once,
shared a file, had one land while the other was open, or met in conflict when it did. Since version
3 it also holds what the work cost, so that the cost of coordination can be measured: the date of
the price list the estimate uses; counts of the pull requests that ended in the 30 days, of those
merged and of those with any usage recorded against them, of the Claude Code sessions and the runs
of the repository's Claude workflows that recorded usage, and of the records left for a later run;
the tokens Claude used, by kind (input, cache writes, cache reads, output, in all, and those of a
model the price list does not know) and by model family (the fixed words fable, opus, sonnet, haiku
and other, never a model's name); what those tokens would cost at Anthropic's API list prices, in
dollars, and the part of it the coordinator workflow spent; the seconds Claude was at work; the
commits, failed checks and reverts of those pull requests; four of these per merged pull request;
and, for the pull requests done alone and those done with other work beside them, thirteen counts
and sums each (pull requests, merged, measured, measured and merged, tokens, dollars, seconds,
commits, failed checks, first checks passed and judged, the median wait from opening to merge, and
the time at work), with seven ratios between the two. To make the
file the workflow reads from GitHub's API, in its memory only and for the length of the run, the
pull requests changed in the 30 days and in the 30 before them, their commits, reviews, check runs
and changed files, the comments made or edited on the repository's issues and pull requests in
those 60 days, its branches and, for each claim branch with no pull request changed in the 30 days,
its newest commit; to sort the pull requests it uses the login of the person who opened each one, the
name of its branch, the Claude Code session link a cloud session writes into its commit messages and
pull request descriptions (and a line `Symphony-Session:` where a session writes one) and the times
of its commits, and to see whose files meet, the names of the files each changed; it writes none of
them. For what the work cost it reads two records the template's own tools leave in your
repository, never anything from the App: the line `Symphony-Usage:` that a Claude Code session of
the repository adds to each of its commit messages, holding token counts by model, the seconds the
session was at work and the first eight characters of the session's id, and no word of its
conversation; and the usage record each run of the repository's Claude workflows keeps as an
artifact of that run, holding token counts by model, seconds, turns, the workflow, the job and the
worker's name, and the issue and pull request the run was for, and nothing of the conversation.
It lists and downloads those artifacts with the repository's own token, from the last 60 days, and
keeps the records it has read in the repository's own Actions cache, so the next day's run reads
only the new ones. The file holds no name, login, session link or session id, title, branch name,
file name, link, issue number, model name, worker name, text or code; a test in the template fails
if any of those reaches the file.
Where a repository has few pull requests a count can describe a single one, and the counts say how a
project works, for instance that one person had three sessions' work going at once. The branch is as
visible as your repository. A maintainer of your project who chooses to run the template's judge on
their own computer, with their own Claude Code account, adds a second file, `JUDGE.json`, holding
counts of communication failure types, of the conversations it judged and of those that had two or
more people, in all and for each work setting, the totals of the failure types' three groups, the
number of pull requests it covered that ended in the 30 days, in each work setting, the number of
days it covered and any limit it ran under, the time it was made, which model and which version of its prompt it used, and the
word that names its schema; the App never runs that judge and only reads that file.

Once a day, at 04:17 UTC, the developer's collector lists the repositories every installation of
SymphonyBoard reaches (receiving from GitHub their names, owners and visibility, which it holds in
memory and never writes) and asks each for exactly those two files at the ref `metrics`, and for no
other path. It keeps a project's `METRICS.json` only when the file says sharing is on; otherwise
nothing of that project is stored and `JUDGE.json` is not read. Of each file it keeps a fixed list
of numbers, the time the file was made, the date of the price list and the few identifier-shaped
words named above; a value of another shape is dropped. The names of the work settings, of the kinds
of pairs, of the model families and of the two sides of the comparison are fixed words of the
template, the same in every repository's file, never words of your project. The developer
therefore learns, per repository and day, how the protocol performed in numbers, and nothing of what
the work was.

Each kept line names the repository only as a keyed hash (HMAC-SHA256) of its GitHub node id under a
secret the developer alone holds, derived from the App's private key or set separately, so the
developer can follow one repository's numbers from day to day, and across a rename or transfer,
without the dataset naming it; a reader of the dataset without that secret cannot tell which
repository a line is. Rotating the key or the secret gives every repository a new hash and ends the
thread. The dataset is a private branch of the developer's repository, one JSON line per repository
and day, with no expiry: lines are added beside earlier days', a second run on the same day replaces
that day's, and the branch's git history keeps every earlier version for as long as the branch
exists. It is read by the developer and by the collaborators on that private repository, for
research on how coordination fails and succeeds among Claude Code sessions; it is never sold and
never given to anyone else. The developer runs the collector on GitHub Actions; it talks to
api.github.com and nowhere else.

## Sharing is on by default, with three ways off

Sharing is on unless you turn it off: the adoption writes `on` into `.github/symphony-metrics`
unless you ticked the form's box "Do not share anonymous aggregates" or a switch of the repository's
own says `off` already, under that name or under `.github/sdlc-metrics`, its name before the rename
to Symphony, which the adoption never turns on.
Where the switch cannot be written, because the repository ignores it or something of its own
stands where it goes, nothing the adoption brings shares: the protocol alone then brings no metrics
workflow, and the whole template's reads what stands in the switch's place as off. To turn
it off at any time: write `off` as the first word of `.github/symphony-metrics` on your default
branch (in a repository adopted before the rename, whose workflow reads only `.github/sdlc-metrics`,
write it there), or set the repository Actions variable `SDLC_METRICS` to `off` (and run the
workflow once, so the record on the branch says off), or uninstall SymphonyBoard, after which the
collector reaches nothing of yours. Disabling the workflow alone does not stop sharing, because the
branch keeps its last record and the collector reads it as that day's; turn the switch off first.
With the switch off the template's sessions also stop adding the `Symphony-Usage:` line to their
commits and its Claude workflows stop keeping usage records, and a person who wants no usage of
theirs on their commits whatever the repository says sets `SDLC_METRICS` to `off` in their own
environment. Lines already collected stay in the dataset under the hash; they carry nothing that
names you.

## The control panel

The control panel is a page of the developer's site, https://openspineconsortium.com/symphony/control/,
and the cost page beside it, https://openspineconsortium.com/symphony/cost.html. Both are static
files that work in your browser with a GitHub token you give them, and they talk to GitHub's own API
as you and, only when you sign in with GitHub or open the Folders tab, to the sign-in service
described below, and, for a drive you connect there, to Microsoft (the Folders tab, below); and
each time your browser loads either of them, the control panel as the installed app (below) among
them, the page links the site's typefaces from Google Fonts, which your browser asks Google for
(below). They read
your own account's login (to say who is signed in), your repository's board (the file STATE.md on
the branch `board`), its open issues and their labels, for its Dependencies tab (below) the
sub-issues of each open issue labelled epic or goal and the issues blocking each of an epic's
sub-issues, the worker files under `.github/symphony/workers/`, the agents' list
`.github/symphony/agents.json` and the agent files under `.claude/agents/` it names, for an agent's
tokens the file `.github/symphony/accounts.json`, which names the token slots each agent may use,
and the default branch's `tools/pool.py`, to see that it takes such a list before one is proposed,
on the Tokens page the records on the branch `pool` of each slot's latest use (how much of its
five-hour and seven-day windows, and of any weekly limit of a single model, named by that model, it
had used, when they reset, for a reading taken from a worker's run or a probe whether Claude's
answer it was read from allowed or refused the request, and when and by what it was read),
its open pull requests and the check
runs on their heads, its Actions runs, the repository's own record (its default branch, whether it
is private, its topics and, for one you name, its numeric id and its owner's, to build the App's
install link with that repository selected), on the cost page the file METRICS.json on the branch
`metrics`, and, when you press "Find my Symphony repositories", the names and topics of the
repositories your token reaches, up to three hundred of the most recently pushed, to keep the ones
carrying the topic symphony, and, in the dialog "Add repository", the repositories SymphonyBoard is
installed on that you can reach, installation by installation, or, with a pasted token, the
repositories that token reaches, to choose one to add to your list; on the Share tab, who has access
to the repository (its direct collaborators in an organization's repository, all of them in a
person's) with their roles, the invitations waiting for an answer and, among its open issues, the
requests to join, each an issue whose description begins with the line
`<!-- symphony-access: request -->`, one row for each person who asked; and, before it opens a
request to join for you, your own open issues there, so that it opens no second one. On the Tokens
page they also read, as you, the names and records of the organization's Actions secrets (for a
personal account's repository, the repository's own), never a value, which GitHub gives no one, to
show which slots hold a token and to find a free one; the name and value of every Actions variable
there, read to find each slot's label, of which the page keeps the labels alone; the variable
SYMPHONY_CLAUDE_SETTINGS and, for an owner of the organization, SYMPHONY_LEND_TO; and, when you
press Add Token, the variable CLAUDE_CROWD of the organization and of the repository, to refuse a
repository in crowd mode. Only when you
press the button that says so, they write what GitHub's own pages would: an issue (a task, an "Add a
worker" issue, one that mentions @claude, the assistant's, below, or a request to join, which the
page opens as you, titled "Access request: " and your login, with a description that names your
login and the repository and says that you ask to join it as a collaborator, when you press "Ask to
join" on the Share tab of a repository where GitHub will not show you who has access, or in the
Tokens page's Add dialog for an organization's repository you may not write to, and which anyone who
can read the repository can read, everyone where it is public), a comment (a question to the
assistant among them, and, on a request to join that someone answers on the Share tab, with
Invite, which only an administrator may, or with its X to decline and confirm, which anyone GitHub
shows the repository's collaborators to may, every collaborator in a person's repository and, in an
organization's, a member of the organization who may write to it, one saying that they invited you,
that you have access already or, whoever declined, that an administrator declined), a label on an
issue (and the label itself when it is not
there yet), a workflow run started by hand, a merge, an issue closed as not planned or, for a request
to join answered with Invite, as completed, a pull request closed, a
pull request that changes or deletes a worker's file or deletes an agent's file and its line in
agents.json, made as GitHub's own pages would make it (a branch of its own from the default branch's
head, the files written or deleted on that branch, and the pull request opened, or the one already
open from that branch found), never a push to the default branch, a pull request from the Agents
tab that gives an agent the token slots you picked, by their names in .github/symphony/accounts.json,
written on the branch symphony/tokens-<the agent's name in lower case>, which is first set to the
default branch's head, so whatever that branch held is replaced, and set to merge itself once its checks
pass where the repository allows auto-merge (the Notebooks tab, below, writes a file too, and makes a
notebook's repository private when you ask), or, on
the Share tab, an
invitation to the GitHub user you
name, with the role you pick, or, when you answer their request to join with Invite, to the person
who asked, with Write in an organization's repository and a collaborator's access in a person's, to
collaborate on the repository, a new role for a collaborator or
for an invitation waiting, a collaborator removed or an invitation withdrawn (the Folders tab,
below, says what else). To find that user from an email address you type, the Share tab asks GitHub's user search
for an account showing that address publicly; the
address goes to GitHub alone. The Share tab's mail buttons open Gmail, Outlook, your email app or
your device's share sheet with a note you send yourself; the page sends nothing there.

The token is one of two kinds, and either way it stays in your browser. A fine-grained personal
access token you make on GitHub and paste into the page is first sent to GitHub alone, to ask whose
it is, and kept only once GitHub accepts it: in the browser's storage until you press "Forget the
token", or, when you did not tick "Keep me signed in", in the tab's own storage, which the browser
clears when the tab closes and brings back with the tab when it reopens or restores it. With "Sign
in with GitHub", GitHub issues, after you allow it on GitHub's own page, a token of SymphonyBoard's
that acts as you within the App's permissions and your own access on the repositories it is
installed on, and expires in eight hours; beside it GitHub issues a refresh token, valid six months,
with which the page renews the token. Pressed in a browser's tab, "Sign in with GitHub" leaves for
GitHub's page, and GitHub sends your browser back to the page with a one-time code (the installed
app, below, is another matter); the page sends that code, with a one-time secret it made for this
sign-in, to the sign-in service, a small program of the developer's run on Cloudflare's Workers
platform, which adds the App's client secret, asks GitHub for the token and hands back the token and
the refresh token; the page renews the token by sending the service the refresh token the same way.
With "Keep me signed in" ticked, the page keeps both in the browser's storage until you press
"Forget the token".
Unticked, it keeps the token in the tab's own storage, as it keeps a pasted token, and the refresh
token in the open page's memory alone, never in the browser's storage, so that the renewals end once
that page is gone, closed, reloaded or replaced by another page such as the cost page, and the
sign-in then ends with its eight-hour token. When a new sign-in, or a token you paste that GitHub
accepts, takes the place of a sign-in's token, the page has the service ask GitHub to revoke the one
it replaced, as "Forget the token" does. The service keeps nothing: no store, no cookie, and no log
of its own of the code, the tokens or you; it answers no origin but the site's (the Folders tab,
below, says what else); and its host's own request logs are turned off, though Cloudflare, which
carries the request, sees its address and
timing under Cloudflare's own privacy policy. The developer receives nothing from the pages but what
that service passes through in the moment: never a token to keep, never a name, never a count.
Beside the token, the page keeps in your browser the names of the repositories you listed, the plan
you chose on the cost page, the number of the assistant issue it uses in each repository (below),
and the layout you set: the widths and heights of the panels you resized and the text size, numbers
alone, holding nothing of your repositories or of GitHub and sent nowhere.

The control panel can also be installed from the browser as an app, on a phone's Home Screen or
among a computer's apps; its manifest is
https://openspineconsortium.com/symphony/control/manifest.webmanifest. The app is the same page in a
window of its own, with no code of its own: it reads, sends and keeps what the page does, as this
section says, its window standing for the tab, save for its sign-in. While sign-in by code, below,
is switched off, the app's "Sign in with GitHub" leaves for GitHub's page as a tab's does, but
GitHub's return may land in your browser rather than in the app. The page there did not start that
sign-in and holds no secret for it, so it takes the code out of its address and sends it nowhere,
and the code signs nobody in; the app is then not signed in by that press, and a token pasted into
it is the way in.

Each time your browser loads the control panel, in a tab or as the installed app, or the cost page,
the page's head, as on the developer's site's other Symphony pages, links a stylesheet of Google
Fonts, https://fonts.googleapis.com/css2, asking for three typefaces: Newsreader (upright at the
weights 400, 500 and 600 and italic at 400 and 500, across its optical sizes 6 to 72), IBM Plex Sans
(400, 500 and 600) and IBM Plex Mono (400 and 500); and it asks the browser to open a connection to
fonts.googleapis.com and fonts.gstatic.com as it loads. Your browser asks fonts.googleapis.com for
that stylesheet and fonts.gstatic.com for the font files it names, as the page's text comes to need
them, unless it holds them from an earlier load. Google receives those requests as it receives any,
with your network address and the headers your browser sends with every request, under Google's own
privacy policy; the page puts nothing of its own into them, no token, no repository's name and
nothing you type, and the developer receives nothing of them.

Sign-in by code, GitHub's device flow, is built into both pages for the installed app and switched
off: a setting in the page's script, CODE_SIGNIN, holds it off until the developer turns it on, and
while it is off no page offers a code and the page never asks the sign-in service for one. GitHub
gives a SymphonyBoard code only while "Enable Device Flow" is ticked in the App's settings, which
the developer ticks only to turn sign-in by code on. Once it is on, the installed app's "Sign in
with GitHub" signs in by code in place of leaving for GitHub's page, and in a browser's tab a second
button beside it, "Sign in with a code instead", does the same. On that press the page sends the
sign-in service's route /device a request that holds nothing of yours, an empty object, which your
browser sends with the page's origin; the service asks GitHub, at
https://github.com/login/device/code, for a code, with SymphonyBoard's client id alone, which is
public, and no client secret, and hands back the short code you type, the address of GitHub's page
where you type it, the device code that goes with it, how long the two live, an hour at most, and
how often the page may ask after them. The page shows the short code, with the warning below, and
holds the device code in the open page's memory alone, never in the browser's storage, the page's
address or a log. The link beside the code, "Copy it and open GitHub", puts the short code on your
device's clipboard and opens https://github.com/login/device in a new tab, handing that page
nothing; you type the code there, where GitHub names SymphonyBoard and asks whether it may act as
you. Meanwhile the page sends the device code alone to the service's route /device/token, at most
once every five seconds and more slowly where GitHub or the service asks, and the service passes it
to GitHub, at https://github.com/login/oauth/access_token, with the client id and no client secret,
and hands back GitHub's word that the code is not typed yet, GitHub's refusal or, once you have
typed it and allowed SymphonyBoard, the token and the refresh token, the same kinds the sign-in by
GitHub's page gives, which the page renews and revokes through the service in the same way. The page
stops asking when GitHub gives the token or refuses, when the code runs out, or when you press
Cancel, sign in another way, paste a token GitHub accepts or press "Forget the token"; a token
GitHub gives after that, for a code the page has let go of, goes once more to the service, so that
GitHub revokes it. Once you are signed in by code, the page keeps what the sign-in by GitHub's page
keeps, as above, by "Keep me signed in" as it stands when the token comes: ticked, the token and the
refresh token in the browser's storage until you press "Forget the token"; unticked, the token in
the tab's own storage and the refresh token in the open page's memory alone. Save where the browser
refuses to store the token, as it can for a sign-in by code, which, unlike the sign-in by GitHub's
page, needs no storage to finish: the page then holds the token and the refresh token in the open
page's memory alone, never renews them, and drops them once that page is gone or you press "Forget
the token", which in that case asks GitHub to revoke nothing, so the token stays good at GitHub
until it runs out within eight hours, or until Revoke at
https://github.com/settings/apps/authorizations, below, ends it. The service keeps nothing of a
sign-in by code either: no store, no cookie and no log of its own, and its two device routes answer
the site's origin alone.

Ticking "Enable Device Flow" opens a way in that no page can close: anyone, not only this page, may
then ask GitHub for a SymphonyBoard code with the App's public client id, and whoever asked for a
code gets the token it earns once a person types it on GitHub's page and allows SymphonyBoard there,
a page that names SymphonyBoard alike for every code. A person talked into typing someone else's
code so hands that someone a token that acts as them, within SymphonyBoard's permissions and their
own access, on every repository the App is installed on that they can reach. So beside every code it
shows, the page says: "Type a code only there, on github.com/login/device, and only one you started
on this page a moment ago. A code someone sends you, by mail, chat or another page, would sign them
in as you." The developer never sends anyone a code. And whoever holds the refresh token of a
sign-in by code can keep that sign-in going without end: GitHub renews such a refresh token with the
client id alone, with no client secret and without the sign-in service, each renewal giving a new
refresh token good for six months more, so the sign-in ends only when it is revoked or goes six
months without a renewal. "Forget the token" drops the token and the refresh token that tab and that
browser hold and, where the browser's storage holds that token, asks GitHub through the service to
revoke it, and no other; whether GitHub then refuses that sign-in's refresh token too is not
established, though the page no longer holds it. Revoke beside SymphonyBoard under your GitHub
Settings, Applications, Authorized GitHub Apps, https://github.com/settings/apps/authorizations,
ends every token SymphonyBoard holds for you, refresh tokens and one from a code someone else
started among them.

The control panel's Assistant section asks the repository's own Claude workflow a question, through
GitHub and nothing else. Once per repository and person, on your press, the page opens an issue of
yours titled `Assistant: <your login>` and labelled assistant, and makes that label when the
repository lacks it; each question you press Ask on is one comment of yours on that issue, which
mentions @claude and ends with a short block of the page's state (the repository's name, the task
the page centres, the filter it shows and the board section it is at), and the repository's Claude
workflow answers it there, on the Claude token the repository holds, reading the repository only, as
a comment the page shows you. While it waits, the page reads that issue's comments every few
seconds, then every half minute, for at most forty-five minutes or until you press "Stop watching",
each read made conditional on the last so that GitHub answers "nothing new" at no cost against your
rate limit. The page offers the box only where GitHub, asked, says you may write to the repository,
since the workflow answers nobody else, and only where the repository's default branch carries the
assistant's file, .github/symphony/assistant.md, which the page reads to tell. The number of the
assistant issue it uses in each repository, one it opened or found, is kept in your browser beside
the token, so that it opens no second one; close the issue on GitHub and the page opens another at
your next question. The question, its block and the answer are on the issue, where GitHub keeps them
as it keeps any issue's comments, and are sent to nobody else: the developer receives none of it.

The bar's button "Ask in claude.ai" opens claude.ai in a new browser tab, signed in as whoever you are
there, with your question and a line or two naming what the page shows (the repository and the tab,
and the task, the OneDrive folder and item, or the Explore level you are at, each with its GitHub or
OneDrive link) carried in that tab's address, as the question claude.ai starts with. The page itself
sends nothing to claude.ai, reads nothing from it and writes nothing for it, asks no write access to
the repository for it, and cuts the whole to 2,000 characters, which an address carries. What you and
Claude do there is on your own claude.ai account, under Anthropic's terms, with whatever you connected
to that account; the developer receives none of it.

The control panel's Dependencies tab,
https://openspineconsortium.com/symphony/control/#dependencies, draws the work of each open epic as
a chart: its tasks, which are the epic's sub-issues on GitHub, an arrow from each issue that blocks
one of them to the issue it blocks, which is GitHub's own blocked-by relation, and the goals above
their epics, the chart the repository's own board draws into STATE.md once its protocol is new
enough to draw it. To draw it the page reads, as you, with the GitHub token you gave it, what
GitHub's own issue pages show under Sub-issues and Relationships: the sub-issues of each open issue
labelled epic or goal, unless GitHub's summary of that issue says it has none, and, for each
sub-issue of an epic whose summary counts an issue blocking it, the issues blocking it. It makes
these reads whenever it reads the repository's open issues, which it does each time it opens a
repository, when you press Refresh, and after you queue a task, give an issue to a worker, mention
@claude or merge a pull request on the page, whether or not the Dependencies tab is open, and never
on a timer of its own; it makes at most sixty for one drawing, each page of a list counting as one,
and none once GitHub says your token has fewer than a hundred calls left in its hour. GitHub answers
each read with the issues it names as its API describes any issue, and the page keeps for the chart
their number, title, state, labels and link, the counts GitHub's two summaries give for each (its
sub-issues, done and in all, and the issues blocking it, open and in all), and which of them an open
pull request from its claim branch in the repository itself names, from the pull requests the page
already shows; it reads whether each is a pull request and which repository it belongs to, to leave
out pull requests and the issues of another repository, and keeps nothing else, in the open page's
memory alone, until it draws again or the page is gone. The chart is drawn in your browser by a copy
of Mermaid, an open-source drawing library (MIT) that the developer's site carries and the page
loads from the site, as it loads its own files, only when there is a chart to draw, and the Board
tab draws the same way the charts the board's own STATE.md holds, which the page already reads, each
only where every line of it is one the board writes, showing any other block there as text and never
drawing it; beside the drawing library's file from the developer's site, and the site's typefaces
from Google Fonts, which the page asks for as its text needs them (above), the tab asks nothing of
anyone but GitHub. Pressing a node, here or in the Board tab, or a row's "Centre its row", opens the
Tasks tab at that task's row, where the task tables hold it, and asks GitHub nothing; that task is
then the one the page centres, which the assistant's next question names, as above. The tab writes
nothing: not to GitHub, whose issues it only reads, and not to your browser's storage; the chart is
gone with the page, and the developer receives none of it.

The control panel's Explore tab, https://openspineconsortium.com/symphony/control/#explore, shows
the same work as a map you go into one level at a time: the repository, its goals and epics, each
epic's tasks, a task's open pull requests (or, where it has none, its claim branch), the GitHub
Actions runs on that branch, each run's jobs and steps and, at the bottom, the lines of a job's log,
cut to one step's lines by the times GitHub gives each step. Down to the tasks it draws only what the
page has already read, as above, and makes no read of its own. Below a task it reads, as you, with
the GitHub token you gave it, only when you go into a level and once for each: the runs on that
branch (the latest twenty), a run's jobs and their steps, and a job's log, which GitHub hands over
from its own storage, the address GitHub's answer names, and your browser asks that storage for the
log with no token of yours, since a browser drops the token when GitHub sends it elsewhere; where your browser may not read it from there, the tab says so and links
the log on GitHub. It reads none of these once GitHub says your token has fewer than a hundred calls
left in its hour. A job's log is what GitHub shows anyone who may read the repository's Actions, and
it may hold whatever the job printed, a Claude run's conversation among it. The tab keeps what it
reads in the open page's memory alone, the lines of the last three jobs' logs you opened and no
more, until you choose another repository or the page is gone, and reads a level again only when you
press Read again; it writes nothing, not to GitHub and not to your
browser's storage, and the developer receives none of it.

The control panel's Notebooks tab, https://openspineconsortium.com/symphony/control/#notebooks,
shows the notebooks the drive organizer proposes for a private repository (not public, and not
internal, which every member of its enterprise can read): groups of a few of your
drive's files, each meant to become a private repository of its own that points at those files where
they are and never moves them. It reads, as you, with the GitHub token you gave it, two files on the
repository's branch drive-catalog: notebooks.json, the proposal (each notebook's title, summary,
repository name and the paths of its files), and catalog.json, the names, kinds, sizes, dates and
OneDrive links of the drive's files, as the Folders tab reads it; and, for each notebook, whether a
repository of that name exists under the same owner, whether it is private, internal or public, and
whether GitHub counts you its administrator, which GitHub gives in the same answer.
On a public or internal repository it reads none of these, since a notebook names your files. When
you propose a notebook,
change one or take one out, it asks for catalog.json's version once more and writes notebooks.json on
that branch, as you, over the version it read, so that a change the organizer made meanwhile is
never written over; when you take out the last notebook it deletes the file, and whatever else the
organizer wrote in it goes with it. Where a notebook's repository is public or internal and GitHub
does not say you are not its administrator, the side panel offers Make private: once you confirm, after
a question that says what GitHub erases with the change (its stars and watchers), what becomes of its
forks and, for a public repository, what stops with it (on a free plan its GitHub Pages site and the
enforcement of its rulesets and branch protection, its code scanning unless its owner has GitHub Code
Security, and its secret scanning and push protection unless its owner has GitHub Secret Protection),
the page asks GitHub, as you, to make that repository private, which takes SymphonyBoard's
Administration permission (or, with a pasted token, the token's), and shows what GitHub answers; it
changes nothing else about the repository. It writes nothing else: in your browser's storage only the width
of its side panel, kept with the layout (above), and nothing to the drive, of which Microsoft is
asked nothing. The
repository a notebook names is made by the notebook skill in a Claude session, not by the page. The
file the tab writes stays on the private repository's branch, where GitHub keeps it as it keeps any
file, readable by whoever may read that repository, and Make private changes only the visibility
GitHub keeps for a notebook's repository; the developer receives none of either.

The aggregates the collector reads are as the section on field metrics says, whether or not you use
the pages. The pages never show a repository's Claude secret, which GitHub never gives back, and they
take no Claude token. The Tokens page has no box to paste one into. Its "+ Add Token" has the
repository's workflow Token make the token on a runner instead, as the next paragraph says, so the
most the page ever holds of it is the sealed box the run posts, which GitHub alone can open. Where
the page makes the writes itself, it saves that box, as you, as the secret SYMPHONY_CLAUDE_1 to
SYMPHONY_CLAUDE_32, or CLAUDE_CODE_OAUTH_TOKEN for the slot main. For an organization's repository
that is an organization secret, seen by the repository the page shows beside the repositories it
reached already; for a personal account's repository it is that repository's own secret. It then
writes, as you, for any slot but main, as an organization (or repository) variable, the list
SYMPHONY_CLAUDE_ACCOUNTS, and in an organization adds the repository the page shows to the
repositories that may read that list where it is shared with selected repositories, or shares a list
it makes with that repository alone, as a tile's save does (below); the slot's label, if you gave
one, is written with the slot's settings, as below. The token goes nowhere
else: not to the sign-in service, not to the developer, not into the browser's storage, a log or the
page.

"+ Add Token" on the same page makes the token where it is needed, through a run of the repository's
workflow Token, so no Claude token is ever pasted into the page. On your press, the page opens an
issue on the repository, as you, and starts the
repository's workflow Token (the template's .github/workflows/token.yml) with the issue's number and,
where the page makes the writes itself (below), the public key GitHub gives for your organization's
secrets (for a personal account's repository, the repository's), or, where the Token workflow makes
them for you (below), the word pool and, where the run is on another of the organization's
repositories, the id of the repository the token is for. The run is on GitHub Actions, on the
repository's owner's Actions allowance: it
installs Claude Code, runs `claude setup-token`, and posts on the issue the claude.ai sign-in link
that prints. Where the page makes the writes itself (below), the run holds no secret; where the
Token workflow makes them for you (below), the run also holds SymphonyBoard's private key, from
which it mints the App's installation token once before Claude Code is installed, to look for a
token of yours in the pool and lend it where it finds one, and revokes that token before the
sign-in starts, and, where it found none, once more after Claude Code has gone, to make the writes.
The page shows that link as a button. You sign in to claude.ai as
the account to add and press Authorize, and claude.ai shows a code; you paste it into the page, which
posts it on the issue as a comment of yours. The run reads it, deletes that comment, and hands it to
`claude setup-token`; the code is good only once and only to that run, which holds the other half of
the sign-in. The run takes the Claude token out of what Claude Code prints before anything is
written to its log and, where the page makes the writes itself, seals it there with the public key
the page gave and posts only the sealed box on the issue, which GitHub alone can open. The page
saves that box as the next free slot and, while
CLAUDE_CODE_OAUTH_TOKEN is not set, as that secret too, writes the list SYMPHONY_CLAUDE_ACCOUNTS as
above, and closes the issue. On an organization's repository, where you are an owner of the
organization the page makes those writes as you; where you are a collaborator but not an owner,
GitHub refuses you the write, so the Token workflow itself makes it on SymphonyBoard's installation
token (the section above): the same sealed slot, marked in the settings variable
SYMPHONY_CLAUDE_SETTINGS as yours by your GitHub login and account id, the list
SYMPHONY_CLAUDE_ACCOUNTS, and the repository on the lists of repositories that may read the three;
where you have a token in the pool already, that one is lent to the repository instead, unless it
is in the organization's keeping (below), which such a lend lends nowhere more, and no sign-in is
asked, the run recording your account id in that token's settings where they named you by your
login alone, as those of a token stored before the pool kept account ids do and those of a token an
owner of the organization added or marked as yours on the Tokens page do, since the page writes a
login and no account id; and nothing else. Where the repository the page shows is an organization's
and has no
workflow Token of its own, as one adopted for the claim protocol alone before the adoption brought
that workflow has none until it merges a pull request the Sync run offers it, where that run offers
one (the section on the Sync run says where it offers none, as to a repository that opted out of it),
or one where a file of its own kept that workflow out, the page reads, as
you, the records of up to a hundred of the organization's repositories you can see, the most
recently pushed, and, one by one, whether each that is not archived, carries the topic symphony and
takes your pushes has its workflow Token turned on, keeps the first such repository in the open
page's memory, and opens the issue and starts the run there instead, the issue's text naming the repository the token is for. The token
then goes to that repository and not to the one the run is on: through the page's own writes where
you are an owner, and otherwise through the run, which the page gives that repository's id and
which first reads, on SymphonyBoard's token, that repository's record, to see that it is the
organization's, and your permission on it, to see that you may write to it, and lends nothing where
either is not so. Only a run started by hand, as the page starts it, is given another repository; a
run an issue starts lends only to the repository the issue is on or, for a lend with no say (below),
only to the repositories the organization variable SYMPHONY_LEND_TO names. The Claude token is never
on the page, in the issue, in the run's log, at the sign-in service or shown to the developer by
GitHub, though on that path it is held in the developer's own organization, with what that allows
(the section above). The issue and its comments stay on the repository the page opened it on, as
any issue does, and anyone who can read that repository can read them, everyone where it is public:
the link, the sealed box or the slot's number with, where your token was in the pool already, the
ids of every repository it is lent to or, for a token in the organization's keeping, the word
organization in their place, until the run deletes it, the code, and, where the page opened the
issue on another of the organization's repositories, the name of the repository the token is for,
which they read there even where that repository is private and they may not read it, none of which
gives a Claude token to anyone else. Delete
the issue on GitHub if you want it gone. Beside the button, the page links the Claude GitHub App's
install page on GitHub, opened for the one repository, unless the page can see that App installed
on all of the organization's repositories already; installing it is your own press on GitHub.

Where you are not an owner of the organization, the page also shows a box "Your token", with "Where
is my token lent?", "Delete my token" and, beside each repository it lists, "Take back". Each press
opens an issue on the repository, as you, and starts the Token workflow's manage job, which runs on
SymphonyBoard's installation token for the one token in the pool whose settings name you, by your
GitHub login and your account's id or, for a token whose settings name you by your login alone, as
those of one stored before the pool kept account ids or of one an owner of the organization added or
marked as yours on the Tokens page do, by that login, after which the run records your account id on
it, and for no other: it posts on the
issue the slot's number and
the ids of the repositories the slot's secret reaches, never their names, since the issue's readers
may not be allowed to see them; or takes the secret off the one repository you named and, whether
or not your token reached it, the two variables SYMPHONY_CLAUDE_ACCOUNTS and SYMPHONY_CLAUDE_SETTINGS
with it where no other of the numbered slots SYMPHONY_CLAUDE_1 to SYMPHONY_CLAUDE_32 reaches that
repository, none of them being on in every repository or in every private one, whatever the slot
main, CLAUDE_CODE_OAUTH_TOKEN, reaches (the section above), and then posts on the issue, as a list
does, the slot's number and the ids of the repositories the secret still reaches, unless your token
is in the organization's keeping (below), which the run refuses to take off a repository, saying
that you may still delete it; or deletes the slot's secret first and then its settings and its
place in SYMPHONY_CLAUDE_ACCOUNTS, leaving those of another token stored in the freed slot
meanwhile, and, where the secret was on in selected repositories and none of the other numbered
slots is on in every repository or in every private one, takes the two variables off each repository
it was lent to that no other of the numbered slots reaches, whatever the slot main reaches (the
section above). The page closes the
issue when the run has answered, and shows a listed repository by name only where your own token
can read it. Deleting the secret does not revoke the token, which you revoke on claude.ai; a
deletion that stops partway, after the secret is gone but before its settings, leaves your mark on
a slot with no token, which the next store into that slot writes over.

Both runs can also be started without the page, by an issue, since GitHub lets a workflow be started
by hand only by someone who may write to the repository, while anyone who may open an issue there,
on a public repository anyone with a GitHub account, may lend a token or manage their own. An issue
whose first line is `<!-- symphony-token: lend -->` starts the sign-in run above for the issue's
author: the run posts the claude.ai sign-in link as a comment on the issue, takes the code only
from a comment of the author's, bare or under the page's mark, deletes that comment, seals the
token and stores it in a free slot of the organization's pool as the author's, marked by login and
account id and lent to the repository the issue is on; where the author has a token in the pool
already, that one is lent instead, unless it is in the organization's keeping (below), and no
sign-in is asked. An issue whose first line is
`<!-- symphony-token: manage -->` and whose second line says `list`, `revoke` and a repository's
id, or `delete` does for the author's own token what the box above does; a token whose settings name
its owner by login alone, as those of one stored before the pool kept account ids or of one an owner
of the organization added or marked on the Tokens page do, is refused from an issue, since a login
can pass to someone else once an
account is renamed or deleted, and the author is told to press Add Token on the page once. The run
closes the issue when it is done, whether or not it succeeded, unless the run is cancelled or runs
out of time; a code posted after the run has stopped stays until you delete it. Such an issue holds
what the page's issues hold: the link, the code until the run deletes it, and the run's answers, the
slot's number, with the ids of the repositories it reaches when the run lends or lists it or takes
it back from one, or a word
that the run stopped and why, which may quote the last words Claude Code printed with any token and
the code taken out; never the Claude token, and no repository's name. In crowd mode the run reads the
issue's comments, so as to say it once, says on the issue only that the repository holds no Claude
token, and closes it as not planned. Outside crowd mode, where the repository has no Actions variable
SDLC_APP_ID, which names the App beside its key (the section on what each App asks for), a lend asks
for no sign-in and a manage touches no token: the run reads the issue's comments, so as to say it once,
says on the issue, with the repository's own GitHub token, why it stopped, and closes the issue as not
planned. In the Token workflow as the template holds it since version 34 of this statement, it says
that the repository does not hold the App's settings and so stores no token into a pool, and that an
owner of the organization adds one with Add Token. In a copy of the whole template made before then,
which keeps the Token workflow it was made with, an issue starts such a run only where the copy was
made since 03:38 UTC on 2026-10-19, when the template's Token workflow came to start on an issue, and
there the job the issue asks for starts in the environment token-store, as the section on what each
App asks for says, stops at the App's token, and the run says only that it stopped.

A lend whose second line says `organization` is a lend with no say: the token is stored the same
way, its settings also marked with the word organization, and lent not to the issue's repository
but to the repositories the organization variable SYMPHONY_LEND_TO names, a list of repository ids
the organization's owners keep on the Tokens page under "Tokens lent with no say run on", which the
page writes as them, readable by no repository's workflows, since the run reads it with the App's
token (a list an earlier page wrote readable by the private repositories' workflows, or by every
repository's, is closed so when an owner next opens the Tokens tab, its value kept); or to none while that list is empty, for
an owner to place from the slot's tile. Such a lender is told
the slot's number when the token is stored and, when they list it or when a lend touches a token of
theirs already in the pool, that it is in the organization's keeping, and learns no repository's
name or id from the run. A lend with no say from someone who has a token in the pool already puts
that token in the organization's keeping: it stays where it was lent, goes also where
SYMPHONY_LEND_TO says, and from then on the run names no repository to them. The owners see the
slot on the Tokens page with the lender's login, lend it to more repositories or take it off one,
and delete it; the lender can delete it at any time and lends it to more repositories only with
another lend with no say, to the repositories SYMPHONY_LEND_TO names, though the run names none to
them; only the owners take it off a repository.
Since anyone with a GitHub account may do this on a public repository, the pool fills with what is
offered: an owner deletes a slot from its tile, and GitHub's own limits bound the issues and the
runs. A store that stops partway, after the slot is marked as the lender's but before the secret is
written, leaves that mark on a slot with no token, which the next store takes over.

The page shows each token set as a tile, and on your press a tile's settings: a name, the model and
thinking strength its runs take, a lesser model for when the model's weekly limit runs out, whether
it comes back by itself when its limit resets, and Pause. The page writes them, as you, to the
organization (or repository) variable SYMPHONY_CLAUDE_SETTINGS, which the repository's workers read,
and the name to the slot's label variable, and, in an organization, adds the repository the page
shows to the repositories that may read each variable it writes where that variable is shared with
selected repositories, or shares a variable it makes with that repository alone, whether or not any
token is lent there; neither holds a token, and anyone who can read the workflows of a repository
that may read them can read them, the settings giving the login of every token's owner and the
account id of everyone whose token the Token run stored, or later lent or managed for them from the
page where the settings named them by their login alone. A tile's X, after you confirm, deletes the
slot's secret, its label, its settings and its place in SYMPHONY_CLAUDE_ACCOUNTS, as you, adding the
repository the page shows, in the same way, to the repositories that may read each of
SYMPHONY_CLAUDE_ACCOUNTS and SYMPHONY_CLAUDE_SETTINGS it rewrites rather than deletes, and taking no
repository off them; deleting the secret does not revoke the token, which you revoke on claude.ai. A slot can also be removed on GitHub under the
organization's Settings, Secrets and variables, Actions. Each token's settings also hold an id,
eight random hexadecimal digits the page or the Token run makes, and the GitHub login of the person
it belongs to; a token the Token run stores also holds that person's account id (since a login can
pass to someone else once an account is renamed or deleted), as does one whose settings named its
owner by login alone once the Token run has lent or managed it for them from the page, and, for a
token lent with no say, the
word organization, which a save of the tile's settings keeps, the account id while the token still
belongs to the same login. So an organization's tokens pool in one place while each stays its
owner's: to show who may change
which token, the page asks GitHub for your role in the organization, and it offers a token's
settings, its X and its repositories only to the token's owner and to an owner of the organization.
A tile's dialog lists the repositories the token's secret is on, from GitHub, and a tick adds or
removes one, as you. A worker's run in Actions labels the issue it worked `token:<id>`, with the
repository's own token, so the panel can credit each token, and its owner, with the issues it
closed; the label holds no token, name or e-mail address. What
they start, a worker's run or the Claude workflow's answer to a mention, runs on the token the
repository holds, as the repository's own workflows do. To stop: press "Forget the token", which
drops the token and the refresh token from the browser and, for a token from "Sign in with
GitHub", by GitHub's page or by a code, asks GitHub through the service to revoke the token, save
one the browser refused to store, which the page held in its memory alone and which runs out within
eight hours, as above; a personal access token is revoked on GitHub under Settings, Developer
settings, Personal access tokens, and the App's authorization, which covers every token and refresh
token it issued you, under Settings, Applications, Authorized GitHub Apps.

## The control panel's Folders tab

The control panel's Folders tab, https://openspineconsortium.com/symphony/control/#folders, makes a
repository of yours track files and folders of your OneDrive, which the repository's own workflow,
drive-sync.yml, then keeps in step with the drive. It is a tab of the control panel's one page: it
uses the panel's sign-in, whichever way you signed in, and works on the repository the panel's bar
has chosen. It reads nothing until you open it, or until it opens itself on Microsoft's return
(below). Once open, it reads with your GitHub token, for the chosen repository, the file
`.github/symphony/drive.json`, whether the repository's secret `SYMPHONY_DRIVE_REFRESH` is set and
when it was last updated (never the secret itself, which GitHub gives nobody back) and whether its
workflow `.github/workflows/drive-sync.yml` is there. When you press "Find the repository I just
made", it reads GitHub's list of the ten repositories your token reaches that were made last and,
for each one not on the bar's list yet whose entry there shows neither the template nor the topic
symphony, that repository's own record, to add to the list those made from the Symphony template or
carrying the topic symphony and choose the newest, which the control panel then reads as it reads
any repository you choose. Its link "Create a repository from the template" opens GitHub's own form
in a new tab, where you name the repository and create it on GitHub; while the template is internal
to the developer's enterprise, only the enterprise's members can use that form, and anyone else
adopts a repository through the front door, as the section on the adoption says. The page sends
nothing there. Where GitHub refuses the tab even to say whether the repository's secret is set, the
tab says so as it opens, before you connect a drive, and offers no Track.

Where the chosen repository holds the branch drive-catalog, which the drive organizer writes (a
workflow of the repository with the drive's own access, or a Claude session with your own connector;
in a private repository only, since the catalog names your files), and no drive is connected in the
tab, the tab shows that catalog in place of the drive: it reads, with your GitHub token, when that
branch was last written and its file catalog.json, the names, sizes, dates and OneDrive links of the
folders and files the organizer listed, and draws them in the same explorer, read from the
repository alone, with no Microsoft sign-in and nothing asked of Microsoft. A double-click opens a
file in its Office app or in OneDrive through the link the catalog holds, as it does from the drive;
Track is not offered, since the page holds no token for the drive. Connecting the drive puts the
drive itself in the catalog's place. The developer receives none of it.

When you press Track it reads the repository's record (its default branch and whether it is public),
the names of what its default branch holds at its top, to refuse a folder the repository already
holds there, such as one its checks run, unless it is the folder the repository tracks already, and
its public key for secrets. Where the repository is public, Track writes nothing until you tick
the box beside it that says what you tick will be readable by anyone, a box the tab shows for a
public repository and never ticks for you. It then writes three things, as you, in this order: the
secret `SYMPHONY_DRIVE_REFRESH`, the drive's refresh token sealed in your browser with that key the
way GitHub's own secrets page seals one, so that GitHub alone can open it; the file drive.json,
which names the provider, the folder in the repository, the name, the id and the drive's id of each
item you ticked and the day you connected, committed over the one already there, whose version it
reads first, on the default branch or, where that branch takes only pull requests, on the branch
`symphony/drive`, which it makes from the default branch's head, or sets back to that head where a
branch of that name is there already, so that it holds this one commit and nothing else, with a pull
request for you to merge, or the one already open from that branch; and, only where the file went to
the default branch, one run of drive-sync.yml started by hand. Where your token may not save the
secret, the page says so and writes nothing else; where the file cannot be written, the secret stays
saved, and the page says so and starts no run; where the run cannot be started, the page says so and
links the workflow's page on GitHub, where you press "Run workflow". "Sync now", which the tab shows
once the repository tracks a drive, reads the default branch and starts one run of drive-sync.yml on
it.

The drive's side goes through Microsoft and the sign-in service. When you first open the tab, it
asks the sign-in service which drives it is set up for, and the service answers with the public
client id of the developer's Microsoft app registration, or that OneDrive is not set up yet. When
you press "Connect OneDrive", the page keeps in the tab's own storage a one-time value, a one-time
secret it made for this connection, the panel's query (the repository it showed) and the GitHub
login the panel names, and sends your
browser to Microsoft, which asks you on its own page whether Symphony may read and write your files
(Files.ReadWrite) and keep that access when you are away (offline_access); for a work or school
account, the organization's settings may require its administrator's approval first. Microsoft sends
your browser back with a one-time code to the control panel's own address,
https://openspineconsortium.com/symphony/control/, the page GitHub's sign-in returns to as well; the
page tells the two apart by which of the one-time values it kept the returned one matches, takes the
code out of the address before anything else, forgets what it kept, and the other one-time values
where a sign-in or a connection was left pending beside it, puts the panel's query back as it was
and, whatever came of the return, opens the Folders tab. A code that comes back with any other value
is never sent for a drive's tokens. The page sends the code, with the one-time secret, to the
sign-in service, which adds the client secret of the developer's Microsoft app registration, asks
Microsoft for the drive's access token and refresh token, and hands both back. Leaving the page for
Microsoft ends the renewals of a GitHub sign-in made for one tab alone, as leaving it for any other
page does (the control panel, above), and that sign-in's token serves out its eight hours.

The page keeps the drive's two tokens in its memory alone, never in the browser's storage, the
address or a log, and only for the GitHub account the panel named when you pressed "Connect
OneDrive" (or, pressed while it named nobody, the first it names on the return): reloading or
leaving the page, any sign-out, pressing "Forget the token" among them, or a sign-in as another
GitHub account forgets them, and you press "Connect OneDrive" again; Track drops them once the
secret and the file are written. With the access token the page reads, from your browser and as you,
through Microsoft Graph, the drive's type and its owner's display name, to say which drive is
connected, and its id, to refuse at Track an item the repository tracked from another drive, and the
names, kinds, sizes, dates, ids, paths in the drive and web addresses of the files and folders in the
folders you open, to draw the list you tick in, laid out as a file explorer with a tree of the
folders you open in it; nothing of that list leaves your browser but the name, the id and the
drive's id of what you tick, which go into drive.json. When you open a file from the list, by a
double click, Enter or its menu, the page hands your browser the file's address and nothing else: a
Word, Excel, PowerPoint or Visio file goes to that program on your computer through Office's own
address scheme (`ms-word:` and the like), at the file's address on your drive (for a personal
OneDrive, d.docs.live.net, your drive's id and the file's path; for a work or school drive, the
address OneDrive gave), so that the program opens it from the drive, signs in to Microsoft itself
and saves your edits there; any other file, or one you choose to open in the browser, opens on
OneDrive's own page in a new tab. Your browser may ask first whether to open the program. Nothing is
sent to the developer, the sign-in service or GitHub when you open a file, and the page never
downloads it. When the access token runs out during
a sitting, the page sends the refresh token to the service, which answers with a new access token.

The repository's workflow does the same at the start of every sync: on GitHub's runners it sends the
secret, your refresh token, to the service, or to the address the repository's variable
`SYMPHONY_DRIVE_TOKEN_URL` names instead, and with the access token it gets back it reads at
Microsoft the items the default branch's drive.json names and what a ticked folder holds, six levels
down (until a pull request carrying a new list merges, the newly saved secret is used with the list
already there), brings what changed in the drive into the repository by pull request, sends up what
changed in the repository and, where a file changed on both sides, puts the repository's copy beside
the drive's in the same folder; it touches nothing else in the drive. What comes down, and
drive.json with the names of what you ticked, can be read by whoever can read the repository, and by
anyone where it is public, and the new review comments in its Word documents become tasks, issues of
the repository, readable the same way. The route of the service that trades a refresh token for an
access token answers whoever sends it one, the workflow's request, which comes from no page, among
them. The access Microsoft grants reaches every file of your OneDrive, not only what you ticked, so
whoever can run a workflow on the repository, anyone who may write to it, can read the secret and,
through that route, reach the whole drive until the token lapses or you withdraw the access;
deleting the secret withdraws nothing at Microsoft. You withdraw it at
https://account.live.com/consent/Manage for a personal account, or in My Apps,
https://myapps.microsoft.com, for a work or school account, where its administrator may have to. The
service's word on which drives it is set up for, a public client id, is given to whoever asks; every
other route answers the site's pages alone, as the control panel section says. The service keeps
nothing of any of it: no store, no cookie and no log of its own of the code, the tokens or you, and
its host's request logs are off, as that section says; the refresh token passes through it on
Connect and on every sync and rests only in your repository's secret, and the newer refresh token
Microsoft issues with each access token is dropped there. A Microsoft refresh token lasts 90 days,
and the workflow cannot keep the newer one, so the tab shows the day you connected, which drive.json
records, and the day by which to press "Connect OneDrive" again and then Track, which replaces the
secret and that day, and once that day has passed it says that the connection has run out and that
every sync since stops before it reaches the drive. Google Drive is not offered: Google's own picker
takes a browser API key, which the developer has declined, so the page connects no other drive and
the service refuses any provider but OneDrive. The developer receives nothing from the tab, the
service or the workflow.

## The App's server, where it is run

SymphonyBoard's webhook server, when the developer turns the webhook on, receives from GitHub each
event the App subscribes to, acts on pull request events only (opened, synchronize, reopened, ready
for review, converted to draft, edited) and logs and ignores the rest. For a pull request event it
reads the action, the installation's id, the repository's full name and the pull request's number
from the delivery, then reads the pull request from the API (its head and base, its body, whether
it is a draft and its head commit) and whether the claim file for its issue exists at that commit,
and writes one thing: the check run `sdlc/protocol` on that commit, with a title and a summary that
lists each protocol problem in one line. It posts no comment. It verifies every delivery's signature
before reading it, keeps installation tokens in memory for at most an hour and stores nothing on
disk; its log holds one line per delivery with the time, the delivery's id, the event, the action,
the repository's full name, the duration and a short outcome, and never a token, a payload or a
person's words.

## Keys and tokens

Each App's private key is the developer's and is never given to anyone: it lives in the Actions
secrets of the developer's own repositories and in the server's environment, outside any
repository; the Sync run signs the App's credential with SymphonyBoard's key itself, with openssl,
which it hands the key through a pipe and never in a file. Every token minted from it is an
installation token that lives one hour, asked with the
fewest permissions the step needs (metadata alone to resolve a number, contents read to read, the
four write permissions only for the adoption itself, Contents, Pull requests and Workflows (write)
and Metadata (read) for the Sync run, one installation at a time, Symphony Setup's Secrets and
Variables only for lending the requester's own tokens) and revoked as soon as the step is done where
the code can, except in the Token workflow of the developer's own organization, which mints it with
every permission the installation has, for all the organization's repositories the App reaches, in
a job that runs only the default branch's script and that anyone who may open an issue there can
start; the token for the look at the pool is revoked before Claude Code starts, the others when the
job ends. The client secrets the sign-in service holds, SymphonyBoard's and the developer's
Microsoft app registration's, live in that service's settings on Cloudflare, outside any repository,
and go from there only to GitHub's and Microsoft's endpoints that issue tokens and, for
SymphonyBoard's, to GitHub's that revokes one; the two device routes of sign-in by code send no
client secret, asking GitHub with the client id alone. No token, key or signature is ever printed to
a log.

## What the Apps never do

They send nothing to any service but GitHub's own API. They have no analytics, no error reporting
and no third party. SymphonyBoard holds Administration only for the control panel's Share tab, which
reads the invitations waiting and, when you ask, invites a collaborator, changes a collaborator's or an
invitation's role, removes a collaborator or withdraws an invitation, and for its Notebooks tab's Make
private, which makes a notebook's repository private when you press it and confirm, each as you, and uses
it for nothing else; Symphony Setup holds it where you
installed it, uses it only during an adoption run, and stays installed until you uninstall it. They
read your repository's code only as the
adoption and the Sync run above say (the tree listing, in the adoption a one-commit checkout of the
default branch, in the Sync run the lines of changed files that GitHub's comparison of your default
branch with the branch `symphony/sync` shows, and the few files named), never to keep or send it.
Apart from what the control panel writes as you, with
SymphonyBoard's token, when you press the button that says so, as the section on the control panel
says, of which a repository made private on the Notebooks tab is not wholly yours to undo, since
GitHub erases its stars and watchers with the change and leaves a public repository's forks public
and detached from it, or makes an internal repository's forks private and removes those of people
without access to it, none of which making it public again brings back, they never write to a
repository but the adoption's branch, pull request, labels, issue and settings and the Sync run's
branch `symphony/sync` and pull request, each of them yours to undo, the git objects in which the Sync
run writes the files, the tree and the commit it offers, and the README that begins a repository with
no commit, and, in an organization whose
Symphony Setup installation has Secrets and Variables, the lists of repositories that read the
requester's own token slots and the pool's two variables, as the section on what each App asks for
says; in the pool of Claude tokens of the
developer's own organization, the
only one holding SymphonyBoard's key, the Token workflow writes with SymphonyBoard's token only what
the section on the control panel says, a slot, the two variables and the lists of repositories that
read them, for the person who lends or manages the token.
They never read a Claude credential (the control panel's pages never see one, only, where a page
saves the token itself, the sealed box the Token workflow posts, which GitHub alone can open; a
token the Token workflow makes is plain only on the runner until it is sealed, beside
SymphonyBoard's token where the run stores it for a lender, as the section on organization
permissions says), and nothing here runs on
anyone's Claude account but the one a project's own maintainer chooses to run the judge with. The
control panel's Folders tab and the sign-in service, neither of them an App, talk to Microsoft for
the OneDrive you connect, as the section on the Folders tab says; the Apps themselves send Microsoft
nothing. Nor is the control panel an App: its pages link the site's typefaces from Google Fonts,
which your browser asks Google for as they load, as the section on the control panel says, and the
Apps themselves send Google nothing.

## Uninstalling

Uninstalling SymphonyBoard stops the collector from reading anything of yours and the Sync run from
reading anything of yours or offering you anything, as taking a repository off the installation's list
does for that repository, and undoes nothing in your repository: the files, labels, branch, settings
and issues the adoption
made, and the branch `symphony/sync` and the pull request of an offer, stay yours. Symphony Setup
stays installed after the run, acting only during an adoption run;
uninstalling it, at any time, from the repository's or the organization's Settings, GitHub Apps,
also undoes nothing in your repository.

## Children

Symphony is for people who administer GitHub repositories. It is not directed at children.

## Changes

A new version of this statement is published at https://openspineconsortium.com/symphony/apps-privacy.html
and in the front door repository, github.com/OpenSpineConsortium/symphony-start, whose PRIVACY.md is
this text.

Version 35 adds sign-in by code, GitHub's device flow, built for the control panel installed as an
app and switched off until the developer turns it on, as the section on the control panel says:
while it is off no page offers a code; once it is on, a press of the installed app's "Sign in with
GitHub", or in a browser's tab of "Sign in with a code instead", has the sign-in service's route
/device ask GitHub for a code with SymphonyBoard's client id alone and no client secret, and the
page holds the device code in the open page's memory alone and sends it to the service's route
/device/token, at most once every five seconds, which passes it to GitHub with the client id and no
client secret until you have typed the short code at https://github.com/login/device and allowed
SymphonyBoard; the page then keeps what the sign-in by GitHub's page keeps, save where the browser
refuses to store the token, which a sign-in by code, needing no storage to finish, can meet: there
the page holds it in its memory alone, never renews it, and "Forget the token" drops it without
asking GitHub to revoke it, so it runs out within eight hours; and the service keeps nothing of it.
It says that "Enable Device Flow", which sign-in by code needs ticked on SymphonyBoard, lets anyone
ask GitHub for a SymphonyBoard code and talk a person into typing it, which hands whoever asked a
token that acts as that person, so the page warns beside every code to type only one started on
that page a moment ago; and that such a sign-in's refresh token renews at GitHub with the client id
alone, each renewal good for six months more, so that it lasts until it is revoked or goes six
months unrenewed, and where you revoke it; and that "Forget the token" asks GitHub to revoke the
token it drops, while whether GitHub then refuses that sign-in's refresh token too is not
established. It names, as no earlier version did, the stylesheet of Google Fonts that the control
panel and the cost page link for the site's typefaces, Newsreader, IBM Plex Sans and IBM Plex Mono,
as the site's other Symphony pages do, which your browser asks Google for, with the font files it
names, as the pages load, with nothing of the page's own in those requests. And it says that the control panel installs as an app, the same page
in a window of its own, whose "Sign in with GitHub" may come back from GitHub's page to your browser
rather than to the app, where the page sends the code nowhere and the code signs nobody in; earlier
versions said that GitHub sends your browser back to the page, which holds in a browser's tab alone.
Nothing the developer receives or keeps changed.

Version 34 adds the Sync run, symphony-template#257, as the section of that name says: a workflow of
the developer's in the template's own repository that, whenever the board's, tidy, metrics or Token
workflow, `scripts/tokens.py` or any file under `tools/` changes there, once a week and by hand, walks
every installation of SymphonyBoard on the App's own key
and, in each repository an installation reaches but the template's and the front door's own, a fork and
one archived or disabled, reads the default branch's newest commit and the listing of its tree, and,
where that branch holds `docs/agents/PROTOCOL.md`, the text of the switches `.github/symphony-sync`,
`.github/symphony-adopt` and `.github/sdlc-adopt`, and, where the repository has not opted out with
`off` in one of them, holds no `.github/workflows/protocol.yml`, which every copy of the whole template
holds unless its owner has removed it and none adopted for the protocol alone does, so that a copy of
the whole template, the front door's or one made with "Use this template", is passed over with nothing
written while it keeps that workflow, and a file needs changing, the twenty newest pull requests from
the branch `symphony/sync` and, unless none of the App's among them is open and the newest of the
App's was closed unmerged offering the same files, GitHub's
comparison of the default branch with that branch, where it exists, with lines of the files changed on
it, and, where every commit the branch holds beyond the default branch is the App's own or a merge and
an open pull request of the App's offers the same files, the record of the branch's newest commit; it
writes nothing where none of the App's pull requests among them is open and the newest of the App's was
closed unmerged offering the same files, where a commit the branch holds beyond the default branch is
neither the App's own nor a merge or the branch holds more commits beyond the default branch than
GitHub's comparison lists,
or where an open pull request of the App's offers the same files and its branch already holds one
commit straight on the default branch's newest commit; otherwise it writes the files it offers, a tree
and a commit on the default branch's newest commit as git objects in the repository, the branch
`symphony/sync`, which it makes or moves by force, and one pull request, or a new description for the
one open, writing the offer and moving the branch again on each later run that gets that far while
GitHub refuses to open that pull request, as it does while one someone else opened from the branch stands open, offering the newer
versions of the vendored library and
of the board's, tidy, metrics and Token workflows with their scripts, replacing only files that hold a
version the template once held, adding only the Token workflow with its scripts and, to a unit the
repository has by its workflow or, for the library, by `tools/VENDORED`, every file of that unit the
repository lacks, and never offering again a pull request closed unmerged while the
files it would bring, each path with the template's version of it, are the same; it does so on an
installation token with Contents, Pull requests and Workflows (write) and Metadata (read), revoked
after each installation's repositories whatever GitHub answers, and its log, which whoever may read the
template reads, counts outcomes and names no repository. SymphonyBoard asks for no new permission for
it: the list of what SymphonyBoard asks for now names the Sync run under Contents, Pull requests and
Workflows, and the sections on keys and tokens, on what the Apps never do and on uninstalling name it
too. The introduction and the section on the adoption say that only a repository that holds the claim
protocol without the whole template is offered newer files, and the section on the Sync run says that a
copy of the whole template made since the template holds that run carries `.github/workflows/sync.yml`,
whose runs there skip its one job. The section on the Sync run also says, as earlier versions did not,
that a branch and a pull request an App makes, the adoption's as well as the Sync run's, start the
workflows the repository runs on a push, a new branch or a pull request, in the versions the branch
holds, save one that runs on `pull_request_target`, which runs in the default branch's version. From
symphony-start#76, the section on the adoption says that the protocol alone brings, beside
the board's, tidy and metrics workflows, the Token workflow with the scripts it runs,
tools/token_run.py and the modules of the template it imports, today tools/sealbox.py,
scripts/tokens.py and tools/pool.py, held back, as that section now says in full for each workflow it
brings with a script, where something of the repository's own, a file, a link or a folder, stands where
one of them goes and is not a file, or a link to a file in the repository outside its `.git`, that
holds the template's version byte for byte, where a file of the repository's own, or a link of its own
to anything but a folder in the repository outside its `.git`, stands where one of their folders goes,
where the repository ignores one of them, where Python would import a file
of the repository's own in place of one of them, or where one of them stays out with another workflow
that imports it too, the board's and the metrics workflows being held back also where the vendored
library will not be the template's, and that every issue opened starts it, its jobs skipping unless the
issue asks it to lend or manage a token; so the section on the control panel no longer says that a
repository adopted for the claim protocol alone has no workflow Token of its own, and says that one
adopted for it before the adoption brought that workflow has none until it merges a pull request the
Sync run offers it, where that run offers one, and that one where a file of its own kept that workflow
out has none either. And from symphony-template#257 the section on what each App asks for, and the
control panel's
passage on the runs an issue starts, say that where a repository has no variable SDLC_APP_ID, which
names the App beside its key, the Token workflow's two jobs that store a token into the pool and manage
one there do not run, in the Token workflow as the template holds it from this version on, and a run
asked for either outside crowd mode only says so on the issue, with the repository's own token, and
closes an issue that started it, where until then those jobs started there, GitHub recording each such
run as a deployment to their environment token-store, which it made in the repository the first time
one ran where the repository's plan let it have environments, and stopped at the App's token, in a
copy made before 02:26 UTC on 2026-10-19 only after the Claude sign-in, the token then held on the
runner and deleted unsaved, as they still do in a copy of the whole template made before then, which
keeps the Token workflow it was made with, as the section on what each App asks for now says. That
passage on the runs an issue starts also says, as version 33 did not, that a run in crowd mode reads
the issue's comments, so as to say it once, and closes the issue as not planned. Nothing the developer
receives or keeps changed.

Version 33 adds the Notebooks tab's Make private, the owner's choice of 2026-10-19: where a notebook's
repository is public or internal, a button in its side panel makes it private on GitHub, as you, once
you confirm, which SymphonyBoard's repository permission Administration allows, as it allows the Share
tab's changes; the tab also reads, from the answer it already asked for, whether GitHub counts you the
repository's administrator, and offers the button only where GitHub does not say you are not. So the
section on what the Apps never do no longer says that SymphonyBoard changes no setting with
Administration, and the list of what SymphonyBoard asks for no longer says that it holds
Administration for one thing only: Make private changes a repository's visibility, when you press it
and confirm. That section now also sets what the control panel writes as you, with SymphonyBoard's
token, apart from the writes it says the Apps never make, and says that a repository made private is
not wholly yours to undo, since GitHub erases its stars and watchers and changes or removes its
forks, none of which making it public again brings back. The list
of what SymphonyBoard asks for, and the section on what the Apps never do, now name in full what the
Share tab does with Administration (it reads the invitations waiting, invites, changes a role, removes
a collaborator and withdraws an invitation), where earlier versions named only the invitation, and
the section on the control panel names, as no earlier version did, the request to join that the
Share tab and the Tokens page's Add dialog open as an issue, as you, titled with your login and
naming the repository, which anyone who can read the repository can read, which the Share tab lists
from the repository's open issues, and which an administrator answers there with Invite, or anyone
the Share tab shows the repository's collaborators to with a decline, each a comment on the issue and
its close; the Share tab otherwise does what it did. It
corrects version 32, which said that an adoption lends the
person who asked a token they lent with no say: as symphony-start#72 was merged, the adoption never
lends a token in the organization's keeping, which only the organization's owners place, counts it
as none of the person's and names it nowhere, so that where the person has no other token the run
may lend, the pull request says that no token in the pool names them as its owner and the log says
that no tokens were lent. The Version 32 entry below now names symphony-template#254, not #253, as
the pull request that brought the Token workflow its rule for a token in the organization's
keeping, and this version says so too where it describes the Token workflow's lends and take-backs:
a lend that is not one with no say lends such a token nowhere more, and a take-back of it is
refused. From symphony-template#253, it says that the Token workflow's take-back and deletion take
the two variables SYMPHONY_CLAUDE_ACCOUNTS and SYMPHONY_CLAUDE_SETTINGS off a repository no other of
the numbered slots SYMPHONY_CLAUDE_1 to SYMPHONY_CLAUDE_32 reaches, none of them being on in every
repository or in every private one, whatever the slot main, CLAUDE_CODE_OAUTH_TOKEN, reaches, a
take-back whether or not the token reached that repository and a deletion only where the token was
on in selected repositories, reading for that which repositories each of those other slots reaches,
where earlier versions said
the workflow never took a repository off them; that a deletion removes the secret first and its
settings after, so that one stopped partway leaves a mark on an empty slot and no longer a token
marked as no one's; and that a deletion leaves the settings and the place in
SYMPHONY_CLAUDE_ACCOUNTS of another token stored in the freed slot meanwhile. Until
symphony-template#253 a deletion, or the recording of an account id on a slot stored before the
pool kept them, also put the repository the run was on onto the lists of repositories that may read
the variables it changed, which earlier versions did not say; the workflow no longer does, so what
the text says the workflow adds to those lists, the repositories a token is lent to, needed no
change for it. From symphony-template#249, it says that where the repository the
control panel shows has no workflow Token of its own, the page reads the organization's repositories
to find one that has it, opens the issue and starts the run there, the issue's text naming the
repository the token is for, which anyone who can read the repository the issue is on can read,
even where the repository the token is for is private, and lends the token to the
repository it shows, or has the run lend it there once the run has read that repository's record
and the person's permission on it. From symphony-template#251, it says that the template's Claude
workflow starts its job for a mention of @claude only by the repository's owner, a member of its
organization or a collaborator, so for anyone else's mention GitHub marks the job skipped and no
step runs. It also corrects what earlier versions said of the Tokens page and the Token workflow.
The page has no box "Add or renew a slot" to paste a Claude token into, as earlier versions said,
and seals nothing in your browser: its "+ Add Token", which earlier versions called "Add a Claude
account", has the Token workflow make the token, the page holds at most the sealed box the run
posts, the slots run to SYMPHONY_CLAUDE_32, and a secret the page saves is seen by the repository it
shows, not by repositories you tick; the Actions permission names the page's buttons by the names
they have, "Read use now" and "Add Token", and the box "Your token"; and a run that makes the writes
for you holds SymphonyBoard's private key, where earlier versions said the run holds no secret. The
Token workflow's reads are now named in full: the names and records of all the organization's
Actions secrets, the public key GitHub gives for sealing them, the records of SYMPHONY_CLAUDE_ACCOUNTS
and SYMPHONY_CLAUDE_SETTINGS with their values, the second with the login of each slot's owner and,
where it holds one, their account id, and the GitHub record of the person it acts for, and
SYMPHONY_LEND_TO only for a lend with no say;
a lend from the page of a token already in the pool records its lender's account id where its
settings named them by login alone; and the issue of a token in the organization's keeping carries
the word organization in place of the repositories' ids. The records on the branch pool the page
reads also hold each single model's weekly limit and whether Claude's answer allowed the request.
And a tile's save and its X, in an organization, add the repository the page shows to the
repositories that may read the variables they write, so the login of every token's owner, and their
account id where the settings hold one, reach that repository too, which earlier versions did not
say. The section on the control panel now names the Tokens page's own reads, as you, which earlier
versions did not: the names and records of the Actions secrets where the tokens live, the name and
value of every Actions variable there, SYMPHONY_CLAUDE_SETTINGS, SYMPHONY_LEND_TO for an owner of
the organization, and CLAUDE_CROWD when you press Add Token. It says that the page gives the Token
workflow the public key, and the run seals the token with it and posts the sealed box, only where
the page makes the writes itself, and that where the run makes them the page gives it the word pool
and, for a run on another repository, the id of the repository the token is for, where earlier
versions said the page always gave the key. It says that a token's settings name its owner by login
alone not only where the token was stored before the pool kept account ids but also where an owner
of the organization added it or marked it as someone's on the Tokens page, which writes a login and
no account id, so that such a token too is refused from an issue and, when the person presses for it
on the page, given their account id, where earlier versions named only the older tokens. And it says
that a take-back posts on the issue, as a list does, the slot's number and the ids of the
repositories the token still reaches, which earlier versions did not say. Nothing the developer
receives or keeps changed.

Version 32 adds Symphony Setup's two organization permissions Secrets and Variables (read and
write), used only in an adoption run to add the adopted repository to the lists of repositories that
read the token slots of the organization's pool owned by the person who asked, by their login and
account id, one they lent with no say among them, and, beside one of them, the pool's two variables, as the section on what each App asks
for says; it reads Symphony Setup's installation on the organization, the settings variable, which
names each slot's owner, and the records of those secrets and of the two variables, the variables'
values among them, and no secret's value. It says what the public log and the pull request then say,
and that the lending stays whatever becomes of the pull request. It says what the run's public log shows, now with your account id beside your login: both in the
settings of the step that names the repository (your login also in the request job's step that resolves an installation or, for a repository
you named, that checks you administer it) and of every later step for a repository you named, and whether the repository
belongs to an organization. It also says that the
Tokens page writes the organization variable SYMPHONY_LEND_TO readable by no repository's workflows,
where version 31 said the private repositories' workflows could read it, and closes a list an
earlier page left readable by them or by every repository. It says too that a token in the
organization's keeping, one lent with no say, is placed by the organization's owners alone, as the
Token workflow has done since symphony-template#254: its lender may delete it, and no longer takes
it off a repository or lends it further with an ordinary lend. Nothing the developer receives or
keeps changed.

Version 31 adds the control panel's Notebooks tab, as the section on the control panel says: it reads
the drive organizer's proposal of notebooks and its catalog from the branch drive-catalog of a private
repository, and whether each notebook's repository exists and whether it is private, internal or
public, and writes the proposal there, as you, when you propose, change or take out a notebook. It
also names the pull request the Agents tab opens to give an agent its token slots and the files it
reads for it, accounts.json and tools/pool.py, and the Tokens page's read of the branch pool, which
earlier versions left out, and says, under SymphonyBoard's Contents permission, that the control panel
writes files with it, as you, as the section on the control panel lists: the pull requests it opens,
Track on the Folders tab since version 21, and now the Notebooks tab. Nothing the developer receives
or keeps changed.

Version 30 adds the control panel's "Your token" box and the Token workflow's manage job, which
lists, takes back or deletes the one token in an organization's pool whose settings name you, by
your GitHub login and account id, on SymphonyBoard's installation token; and the two kinds of issue
that start the Token workflow without the page, a lend and a manage, which anyone who may open an
issue on a repository carrying the workflow may use, the issue's author being the person the run
acts for and the run closing the issue; among them the lend with no say, whose token goes to the
repositories the organization variable SYMPHONY_LEND_TO names, or nowhere yet, and whose lender is
told the slot's number and that the token is in the organization's keeping. The settings variable
also keeps each token's account id beside its login and, for such a token, the word organization, which a save on
the page now keeps; a token a collaborator adds is lent to the repository it was added on, and where
they have a token in the pool already that one is lent and no second one is made. It says that the
pool the App writes can only be the developer's own organization's, where the App's key is, whose
owners, the developer among them, hold the tokens lent there with each lender's login and account
id; that the Token workflow mints SymphonyBoard's token with every permission the installation has;
that the settings variable reaches every repository a token was ever lent to and is printed in
runs' logs; and that the token is held on the runner in a file until it is sealed. The developer's
collector receives nothing new.

Version 29 says that Symphony Setup no longer uninstalls itself after an adoption or after a request
refused because the repository is adopted already: it stays installed, acting only during an
adoption run, until you uninstall it. In a repository that takes the whole template, the run also
sets GitHub Actions as the only source of the check named "check" in the ruleset it created; to see
GitHub Actions report that check, it reads the check runs on the branch symphony/adopt with a
SymphonyBoard token limited to Checks read-only for that one repository, revoked when the settings
step ends. Nothing the developer receives or keeps changed.

Version 28 adds the one write SymphonyBoard makes of its own: where a collaborator who is not an
owner of the organization presses "Add a Claude account", the organization's own Token workflow,
on the App's installation token, writes the minted slot as an organization secret and writes the
organization variables SYMPHONY_CLAUDE_ACCOUNTS and SYMPHONY_CLAUDE_SETTINGS, so a collaborator can
add a Claude slot GitHub would otherwise let only an owner add; the Claude token is sealed before it
is written and the App reads and writes no other secret or variable of its own. Nothing the
developer receives or keeps changed.

Version 27 adds SymphonyBoard's repository permission Variables (read and write), for the control
panel's Tokens page on a personal account's repository, which holds a Claude slot's settings and the
list of accounts as that repository's own Actions variables, each as you; until the permission is
accepted on the App's installation such a repository takes one Claude token, its main one. Nothing
the developer receives or keeps changed.

Version 26 adds the Folders tab's read of the drive organizer's catalog, as the section on the Folders
tab says: where the repository holds the branch drive-catalog and no drive is connected, the tab reads
catalog.json from that branch, with your GitHub token, and shows the folders and files it names;
nothing is asked of Microsoft. Nothing the developer receives or keeps changed.

Version 25 adds the Ask Claude bar's button "Ask in claude.ai", as the section on the control panel
says: it opens claude.ai in a new tab, on your own account, with your question and what the page shows
in that tab's address; the page itself sends nothing. Nothing the developer receives or keeps changed.

Version 24 adds the control panel's Explore tab, as the section on the control panel says: a map
of the repository's work from its goals and epics down to the runs on a task's branch, their jobs and
steps and a job's log, read as you only when you go into a level, kept in the open page's memory and
written nowhere. Nothing the developer receives or keeps changed.

Version 23 adds the Folders tab's list drawn as a file explorer, its read of each item's path in the
drive and web address, and the opening of a file from it, in its Office program on your computer or
on OneDrive's own page, which hands your browser the file's address and nothing else. Nothing the
developer receives or keeps changed.

Version 22 adds the control panel's reads of the agents' list `.github/symphony/agents.json` and
the agent files it names, of the repositories its "Add repository" dialog offers, and of the Share
tab's collaborators and waiting invitations, and the writes its cards and the Share tab make on your
press, as you: closing an issue as not planned, closing a pull request, a pull request, from a
branch of its own, that changes or deletes a worker's file or deletes an agent's file and its line
in agents.json, and a collaborator's or an invitation's new role, removal or withdrawal. The page
keeps nothing new. Nothing the developer receives or keeps changed.

Version 21 adds the control panel's Folders tab, as the section of that name says: a tab of the
control panel's one page, on its sign-in and the repository its bar chooses, that makes a repository
of yours track files and folders of your OneDrive; the box Track asks you to tick before it tracks
into a public repository, where what comes down and drive.json's names can be read by anyone; that
whoever can run a workflow on the repository can use its secret to reach your whole drive, and how
to withdraw the access at Microsoft; SymphonyBoard's repository permission Secrets (read and write),
for the tab and for the Tokens page on a personal account's repository; the tab's reads of the
repository's drive.json, of whether its secret SYMPHONY_DRIVE_REFRESH is set and of whether it has
drive-sync.yml, and of your newest repositories when you ask it to find the one you just made;
Track's three writes, as you: the secret sealed in your browser, the file drive.json, on a branch
with a pull request where the default branch takes only those, and a run of drive-sync.yml; the
drive's consent at Microsoft, which returns to the control panel's own address, and the sign-in
service, which adds the client secret of the developer's Microsoft app registration, kept on
Cloudflare, answers with the drive's access token and refresh token and keeps nothing; the tokens in
the page's memory alone, for one sitting and one GitHub account; the page's reads of your drive's
folders through Microsoft Graph, from your browser; the refresh token passing through the service on
Connect and, from the repository's workflow, on every sync, the one exchange the service answers
for any caller; and the 90 days a Microsoft refresh token lasts. It also says that the control panel
talks to the sign-in service and Microsoft for the Folders tab. Nothing the developer receives or
keeps changed.

Version 20 adds the layout the control panel keeps in your browser: the sizes of the panels you
resized and the text size you chose, numbers alone, sent nowhere. Nothing the developer receives or
keeps changed.

Version 19 adds the control panel's Dependencies tab, which draws each open epic's tasks and the
issues blocking them, and the goals above their epics: the page's reads, as you, of the sub-issues
of each open issue labelled epic or goal and of the issues blocking each of an epic's sub-issues,
what GitHub's own issue pages show, made whenever the page reads the repository's open issues,
whether or not the tab is open, at most sixty for one drawing and none once your token has fewer
than a hundred calls left in its hour; and the copy of Mermaid that the developer's site carries,
which the page loads only when there is a chart to draw and which also draws the charts of the
board's STATE.md in the Board tab, only those written as the board writes them. The tab keeps what
it reads in the open page alone and writes nothing, to GitHub or to your browser. Nothing the
developer receives or keeps changed.

Version 18 adds each token's id and owner in its settings, the page's read of your role in the
organization, the dialog's list of the repositories a token is on, and the `token:<id>` label a
worker's run puts on the issue it worked.

Version 17 adds SymphonyBoard's repository permission Administration (read and write), used only by
the control panel's Share tab to invite a collaborator you name, as you, and the Share tab's lookup of
an email address in GitHub's user search. Nothing the developer receives or keeps changed.

Version 16 adds the Tokens page's tiles: the settings each token's tile writes to the variable
SYMPHONY_CLAUDE_SETTINGS and its label variable, and the X that deletes a slot's secret, label,
settings and place in SYMPHONY_CLAUDE_ACCOUNTS. Nothing the developer receives or keeps changed.

Version 15 says that the Tokens page's "Add a Claude account" starts the workflow Token on the
repository in place of "Add with one press", which made a Codespace: the issue it opens, the sign-in
link, the code and the sealed token on that issue, the page saving the sealed box as the next slot
and as CLAUDE_CODE_OAUTH_TOKEN while that is not set, and the link to the Claude GitHub App's install
page. The page no longer makes a Codespace or saves a Codespaces secret, and the permissions
Codespaces and Codespaces user secrets go unused. Nothing the developer receives or keeps changed.

Version 14 adds Symphony Setup's organization permission Administration (read and write), used only
to allow "Allow GitHub Actions to create and approve pull requests" for an organization whose policy
holds it off, so the sixth setting needs no step by hand there; the run reads the organization's
workflow permissions to leave the token's default permissions as they were. Nothing the developer
receives or keeps changed.

Version 13 adds SymphonyBoard's repository permission Actions (read and write), which the control
panel's buttons that start a workflow run by hand, and its reads of the runs, use as you. What the
pages do is unchanged, and nothing the developer receives or keeps changed.

Version 12 adds the Tokens page's "Add with one press": SymphonyBoard's repository permission
Codespaces and account permission Codespaces user secrets; the Codespace the page makes and deletes
on your press; the page's GitHub token handed to it as your Codespaces secret
SYMPHONY_GITHUB_HANDOVER, seen by your own Codespaces on that repository alone and deleted once the
slot is saved; the Claude token going from claude to GitHub inside the Codespace, never to the page;
and the page's reads of the organization's secret names while it waits. Nothing the developer
receives or keeps changed.

Version 11 adds the control panel's Assistant section: an issue of yours, `Assistant: <your login>`
labelled assistant, that the page opens once per repository on your press, each question a comment
of yours on it that mentions @claude and ends with a short block of the page's state, the answer the
repository's Claude workflow writes there, reading only, the page's reads of that issue's comments
every few seconds while it waits, its reads of whether you may write to the repository and of the
assistant's file on the default branch, and the number of that issue kept in your browser for each
repository. Nothing the developer receives or keeps changed.

Version 10 adds SymphonyBoard's two organization permissions, Secrets and Variables (read and
write), and the Tokens page's "Add or renew a slot", which seals a Claude token you paste in your
browser and saves it, as you, as one of your organization's Actions secrets, with its label and
the list of slots as variables. Nothing the developer receives or keeps changed.

Version 9 says where a sign-in for one tab keeps its refresh token: in the open page's memory alone,
never in the browser's storage, so that the renewals end once that page is closed, reloaded or
replaced by another page, and the sign-in then ends with its eight-hour token; that the tab's own
storage comes back with a tab the browser reopens or restores; that a pasted token is asked about at
GitHub before the page keeps it; and that a sign-in's token that a new sign-in or an accepted pasted
token replaces is revoked through the service, as "Forget the token" revokes one. Nothing the
developer receives or keeps changed.

Version 8 adds the control panel and the cost page of the developer's site, as the section of that
name says: pages that work in your browser with a GitHub token you give them, talk to GitHub's API
as you, and, with "Sign in with GitHub", send GitHub's one-time code to a stateless service of the
developer's on Cloudflare that answers with the token and a refresh token and keeps nothing. Nothing
the developer receives or keeps changed.

Version 7 removes the sweep: no workflow on the front door lists SymphonyBoard's installations
every ten minutes and reads each repository they reach to decide whether to offer an adoption,
since installing the App alone is no longer a request, the install sending you to the form, where
the press is; the run reads an installation only when a form carries its number, as the adoption
section now says, and the collector's daily read of the branch `metrics` is as it was. With the
sweep go two things the run did on its path only: it no longer reads a repository's direct
collaborators to find an administrator, since every request names the person who asked, and it no
longer opens an issue in your repository when it could not open its pull request, since the form's
own issue is answered instead. Nothing the developer receives or keeps changed.

Version 6 says that the run, asked for a repository with no commit yet, first makes its first
commit, as GitHub's own "Add a README file" does: a `README.md` holding the repository's name, on the
default branch, which Contents write allows; that it reads whether such a repository has any branch
at all; that closing the pull request leaves that README; and, as it did already, that when the form
carries an installation's number the run asks of each repository both Apps reach what it asks of the
one it adopts. Nothing the developer receives or keeps changed.

Version 5 says that the run also reads the two switches under their names before the rename to
Symphony, `.github/sdlc-adopt` and `.github/sdlc-metrics`; that an adoption never turns on a switch
of the repository's own that says off already, under either name, and brings nothing that shares
where it cannot write the switch; that a repository adopted before the rename turns sharing off in
`.github/sdlc-metrics`, the switch its workflow reads; and that Symphony Setup also uninstalls
itself after a request refused because the repository is adopted already. Nothing the developer
receives or keeps changed.

Version 4 adds the sixth setting Symphony Setup applies: in a repository that takes the whole
template, it ticks "Allow GitHub Actions to create and approve pull requests" where your
organization and its enterprise allow it. It also names what the run reads to leave your settings as
they are: the repository's rulesets, its topics and its workflow permissions for GitHub Actions.
Nothing the developer receives or keeps changed.

Version 3 adds to `METRICS.json` what the work cost, as the section on field metrics describes: the
tokens Claude used, by kind and by model family, their price at Anthropic's API list prices and the
date of that list, the seconds Claude was at work, the counts and rates per merge they are set
against, and the comparison of work done alone with work done in parallel; and it says which
records in your repository the workflow reads to make them, and that the switch stops those records
too. Nothing else changed.

Version 2 adds to `METRICS.json` and `JUDGE.json` the counts of how the work ran in parallel that
the section on field metrics describes, and to `JUDGE.json` how many of its conversations had two or
more people, the number of days it covered and any limit it ran under. It also says what the
workflow reads to make `METRICS.json`, and names what the two files held already and version 1 left
out: the time each was made, the number of days `METRICS.json` covers and the short id of the
protocol's commit, and, in `JUDGE.json`, how many conversations were judged, the totals of the
failure types' three groups, the model, the version of the prompt and the word that names its
schema. Nothing else changed.

Symphony is not a GitHub or Anthropic product. "GitHub" is GitHub's mark; "Claude" and "Claude Code"
are Anthropic's marks, used here to say what Symphony works with.
