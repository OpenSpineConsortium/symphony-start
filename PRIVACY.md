# Symphony GitHub Apps privacy statement

Version 31, 2026-10-19. This text is also at https://openspineconsortium.com/symphony/apps-privacy.html.
The Symphony browser extension has a statement of its own, at https://openspineconsortium.com/symphony/privacy.html.

Who makes the Apps: Gregory Schwing, trading as OpenSpineConsortium ("the developer"). Questions:
the contact on https://openspineconsortium.com/symphony/.

Symphony is two GitHub Apps. **SymphonyBoard** (github.com/apps/symphonyboard) brings the Symphony
template, or its claim protocol, into a repository by pull request, and afterwards reads one branch
of that repository once a day for anonymous aggregates. **Symphony Setup** (github.com/apps/symphony-setup)
applies up to seven settings to a repository in the adoption run, and stays installed, acting only
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
commit, a README, and for the control panel's writes of a file, as you, which the section on the
control panel lists; Pull requests (read and write), to open the adoption
pull request and, only when you asked for it on the form, merge it; Issues (read and write), to
make the board's labels and, in a new repository, open the issue "Set up this project"; Checks (read
and write), to post the protocol check as a check run where the developer runs the App's server;
Workflows (read and write), because the pull request brings files under `.github/workflows`, which
GitHub lets no token write without it; Codespaces (read and write), which the control panel's Tokens
page used up to version 13 of this statement to make a Codespace and no longer uses, and which stays
on the App until the developer takes it off; Actions (read and write), for the control panel's buttons
that start a workflow run by hand, such as the Tokens page's "Read every slot now" and "Add a Claude
account", and its reads
of the repository's workflow runs, their jobs and a job's log (the control panel, below); Administration (read and write), for one thing only: the
control panel's Share tab invites a person you name by their GitHub username as a collaborator on the repository, as
you, when you press "Invite" (the control panel, below), and no adoption run, workflow or other page uses it;
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
lists of repositories that may read the secret and the two variables, and never takes a repository
off the variables' lists, so every lender's login and account id reach every repository a token
was ever lent to, or every repository, or every private one, where an owner set the variables so.
The repository's Claude workflows pass those settings to their steps, and GitHub prints a step's
settings in its run's log, which anyone can read on a public repository. The same workflow reads
the organization variable SYMPHONY_LEND_TO, where the owners list the repositories a token lent
with no say runs on, and, for the person's own token alone, lists the repositories it reaches,
takes it off one or deletes it. The Claude token is held on the runner, in a file only the runner's
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
of it.

SymphonyBoard also asks for one account permission, Codespaces user secrets (read and write), which
GitHub asks each person for when they sign in with GitHub on the control panel. The Tokens page used
it up to version 13 of this statement to hand its GitHub sign-in to a Codespace; it no longer uses
it, and it stays on the App until the developer takes it off.

Symphony Setup asks for two repository permissions, Administration (read and write), for the seven
settings below, and Metadata (read), and, on an organization, one organization permission,
Administration (read and write). It uses that one for one thing only: where the organization holds
off "Allow GitHub Actions to create and approve pull requests" for its repositories, as a new
organization does, and the repository takes the whole template, the run allows that box for the
organization, leaving the default permissions of GitHub Actions' token as they were, and then ticks
it on the repository. It reads and changes no other setting of the organization. That setting of
the organization stays allowed after the run, and repositories the organization makes later inherit
it; an owner turns it off under the organization's Settings, Actions, General, Workflow permissions. It has no webhook and receives no event. It is meant to be
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
name, its owner's, its default branch's and your login are masked in the run's public log, and the
issue is answered with "your repository". A name you typed into the form is public already, and the
run names it in its answers. The front door's public logs do show the installation's number, the
repository's numeric id, the kind the run read (whether the repository was empty), how many files
it added, replaced, kept or skipped, and the commit ids of your default branch and of the template.

To do its work the run reads, from the repository being adopted: the default branch and the commit
on it or, where the default branch is not there yet, whether the repository has any branch at all,
whether a branch `symphony/adopt` exists and has a pull request, whether `docs/agents/PROTOCOL.md`
exists, the one word in `.github/symphony-adopt` and `.github/symphony-metrics` and in each under
its name before the rename to Symphony, `.github/sdlc-adopt` and `.github/sdlc-metrics`, the full
listing of the default branch's tree (to decide the kind), a checkout of that branch at depth one (to add the
files) and whether you administer the repository. With Symphony Setup installed, the run also reads the repository's rulesets, its
topics and its workflow permissions for GitHub Actions, to leave what is there as it is. When the
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
there and the Symphony browser extension reads from the page; your other topics stay), turns on
secret scanning and push protection where your plan and visibility allow it, and, in a repository
that takes the whole template, ticks "Allow GitHub Actions to create and approve pull requests" where
your organization and its enterprise allow it, and, in a repository that takes the whole template,
once GitHub Actions has reported the check named "check" on the branch symphony/adopt, sets GitHub
Actions as that check's only source in the ruleset it created, then revokes the Setup App's token;
the Setup App stays installed. Unless you chose on the form to review the pull request first, the
run merges it or arms auto-merge. Everything else lands only when you merge. Closing the pull
request instead leaves the labels, the README the run made in a
repository that had no commit, the branch, the settings, the topic and the issue for you to undo.

The adoption's files come from the developer's private template repository, read with a token that
holds Contents read on that one repository and is revoked right after the checkout; only the files
in the pull request reach you.

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
described below, and, for a drive you connect there, to Microsoft (the Folders tab, below). They read
your own account's login (to say who is signed in), your repository's board (the file STATE.md on
the branch `board`), its open issues and their labels, for its Dependencies tab (below) the
sub-issues of each open issue labelled epic or goal and the issues blocking each of an epic's
sub-issues, the worker files under `.github/symphony/workers/`, the agents' list
`.github/symphony/agents.json` and the agent files under `.claude/agents/` it names, its open pull
requests and the check
runs on their heads, its Actions runs, the repository's own record (its default branch, whether it
is private, its topics and, for one you name, its numeric id and its owner's, to build the App's
install link with that repository selected), on the cost page the file METRICS.json on the branch
`metrics`, and, when you press "Find my Symphony repositories", the names and topics of the
repositories your token reaches, up to three hundred of the most recently pushed, to keep the ones
carrying the topic symphony, and, in the dialog "Add repository", the repositories SymphonyBoard is
installed on that you can reach, installation by installation, or, with a pasted token, the
repositories that token reaches, to choose one to add to your list; on the Share tab, who has access
to the repository (its direct collaborators in an organization's repository, all of them in a
person's) with their roles, and the invitations waiting for an answer. Only when you
press the button that says so, they write what GitHub's own pages would: an issue (a task, an "Add a
worker" issue, one that mentions @claude, or the assistant's, below), a comment (a question to the
assistant among them), a label on an issue (and the label itself when it is not there yet), a
workflow run started by hand, a merge, an issue closed as not planned, a pull request closed, a
pull request that changes or deletes a worker's file or deletes an agent's file and its line in
agents.json, made as GitHub's own pages would make it (a branch of its own from the default branch's
head, the files written or deleted on that branch, and the pull request opened, or the one already
open from that branch found), never a push to the default branch, a pull request from the Agents
tab that gives an agent the token slots you picked, by their names in .github/symphony/accounts.json,
written on the branch symphony/tokens-<agent>, which is first set to the default branch's head, so
an earlier such pull request's change on it is replaced, and set to merge itself once its checks
pass where the repository allows auto-merge (the Notebooks tab, below, writes a file too), or, on
the Share tab, an
invitation to the GitHub user you
name, with the role you pick, to collaborate on the repository, a new role for a collaborator or
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
with which the page renews the token. GitHub sends your browser back to the page with a one-time
code; the page sends that code, with a one-time secret it made for this sign-in, to the sign-in
service, a small program of the developer's run on Cloudflare's Workers platform, which adds the
App's client secret, asks GitHub for the token and hands back the token and the refresh token; the
page renews the token by sending the service the refresh token the same way. With "Keep me signed
in" ticked, the page keeps both in the browser's storage until you press "Forget the token".
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
drawing it; beside the drawing library's file from the developer's site, the tab asks nothing of
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
repository of that name exists under the same owner and whether it is private, internal or public.
On a public or internal repository it reads none of these, since a notebook names your files. When
you propose a notebook,
change one or take one out, it asks for catalog.json's version once more and writes notebooks.json on
that branch, as you, over the version it read, so that a change the organizer made meanwhile is
never written over; when you take out the last notebook it deletes the file, and whatever else the
organizer wrote in it goes with it. It writes nothing else: in your browser's storage only the width
of its side panel, kept with the layout (above), and nothing to the drive, of which Microsoft is
asked nothing. The
repository a notebook names is made by the notebook skill in a Claude session, not by the page. What
the tab writes stays on the private repository's branch, where GitHub keeps it as it keeps any file,
readable by whoever may read that repository; the developer receives none of it.

The aggregates the collector reads are as the section on field metrics says, whether or not you use
the pages. The pages never show a repository's Claude secret, which GitHub never gives back. The
one Claude token they take is one you paste into the Tokens page's "Add or renew a slot": the page
seals it in your browser with your organization's public key from GitHub (for a personal account's
repository, the repository's), the way GitHub's own secrets page does, and sends GitHub only that
sealed box, which GitHub alone can open, as the secret SYMPHONY_CLAUDE_1 to SYMPHONY_CLAUDE_8 or
CLAUDE_CODE_OAUTH_TOKEN, seen by the repositories you tick. It then writes, as organization (or
repository) variables, the slot's label if you gave one and the list SYMPHONY_CLAUDE_ACCOUNTS. The
token goes nowhere else: not to the sign-in service, not to the developer, not into the browser's
storage, a log or the page; the page empties its box once the token is sealed.

"Add a Claude account" on the same page makes the token where it is needed instead of asking you to
paste it. On your press, the page opens an issue on the repository, as you, and starts the
repository's workflow Token (the template's .github/workflows/token.yml) with the issue's number and
the public key GitHub gives for your organization's secrets (for a personal account's repository,
the repository's). The run is on GitHub Actions, on the repository's owner's Actions allowance, and
holds no secret: it installs Claude Code, runs `claude setup-token`, and posts on the issue the
claude.ai sign-in link that prints. The page shows that link as a button. You sign in to claude.ai as
the account to add and press Authorize, and claude.ai shows a code; you paste it into the page, which
posts it on the issue as a comment of yours. The run reads it, deletes that comment, and hands it to
`claude setup-token`; the code is good only once and only to that run, which holds the other half of
the sign-in. The run takes the Claude token out of what Claude Code prints before anything is
written to its log, seals it there with the public key the page gave, and posts only the sealed box
on the issue, which GitHub alone can open. The page saves that box as the next free slot and, while
CLAUDE_CODE_OAUTH_TOKEN is not set, as that secret too, writes the list SYMPHONY_CLAUDE_ACCOUNTS as
above, and closes the issue. On an organization's repository, where you are an owner of the
organization the page makes those writes as you; where you are a collaborator but not an owner,
GitHub refuses you the write, so the Token workflow itself makes it on SymphonyBoard's installation
token (the section above): the same sealed slot, marked in the settings variable
SYMPHONY_CLAUDE_SETTINGS as yours by your GitHub login and account id, the list
SYMPHONY_CLAUDE_ACCOUNTS, and the repository on the lists of repositories that may read the three;
where you have a token in the pool already, that one is lent to the repository instead and no
sign-in is asked; and nothing else. The Claude token is never on the page, in the issue, in the run's log,
at the sign-in service or shown to the developer by GitHub, though on that path it is held in the
developer's own organization, with what that allows (the section above). The issue and its comments stay on your repository,
as any issue does, and anyone who can read the repository can read them: the link, the sealed box
or the slot's number with, where your token was in the pool already, the ids of every repository it
is lent to, and, until the run deletes it, the code, none of which gives a Claude token to anyone else. Delete
the issue on GitHub if you want it gone. Beside the button, the page links the Claude GitHub App's
install page on GitHub, opened for the one repository, unless the page can see that App installed
on all of the organization's repositories already; installing it is your own press on GitHub.

Where you are not an owner of the organization, the page also shows a box "Your token", with "Where
is my token lent?", "Delete my token" and, beside each repository it lists, "Take back". Each press
opens an issue on the repository, as you, and starts the Token workflow's manage job, which runs on
SymphonyBoard's installation token for the one token in the pool whose settings name you, by your
GitHub login and your account's id or, for a token stored before the pool kept account ids, by your
login alone, after which the run records your account id on it, and for no other: it posts on the
issue the slot's number and
the ids of the repositories the slot's secret reaches, never their names, since the issue's readers
may not be allowed to see them; or takes the secret off the one repository you named; or deletes
the slot's secret, its settings and its place in SYMPHONY_CLAUDE_ACCOUNTS. The page closes the
issue when the run has answered, and shows a listed repository by name only where your own token
can read it. Deleting the secret does not revoke the token, which you revoke on claude.ai; a
deletion that stops partway, after the settings are gone but before the secret, leaves the token in
the pool marked as no one's, so revoke it on claude.ai then too.

Both runs can also be started without the page, by an issue, since GitHub lets a workflow be started
by hand only by someone who may write to the repository, while anyone who may open an issue there,
on a public repository anyone with a GitHub account, may lend a token or manage their own. An issue
whose first line is `<!-- symphony-token: lend -->` starts the sign-in run above for the issue's
author: the run posts the claude.ai sign-in link as a comment on the issue, takes the code only
from a comment of the author's, bare or under the page's mark, deletes that comment, seals the
token and stores it in a free slot of the organization's pool as the author's, marked by login and
account id and lent to the repository the issue is on; where the author has a token in the pool
already, that one is lent instead and no sign-in is asked. An issue whose first line is
`<!-- symphony-token: manage -->` and whose second line says `list`, `revoke` and a repository's
id, or `delete` does for the author's own token what the box above does; a token stored before the
pool kept account ids is refused from an issue, since a login can pass to someone else once an
account is renamed or deleted, and the author is told to press Add Token on the page once. The run
closes the issue when it is done, whether or not it succeeded, unless the run is cancelled or runs
out of time; a code posted after the run has stopped stays until you delete it. Such an issue holds
what the page's issues hold: the link, the code until the run deletes it, and the run's answers, the
slot's number, with the ids of the repositories it reaches when the run lends or lists it, or a word
that the run stopped and why, which may quote the last words Claude Code printed with any token and
the code taken out; never the Claude token, and no repository's name. In crowd mode the run only
says on the issue that the repository holds no Claude token, and closes it.

A lend whose second line says `organization` is a lend with no say: the token is stored the same
way, its settings also marked with the word organization, and lent not to the issue's repository
but to the repositories the organization variable SYMPHONY_LEND_TO names, a list of repository ids
the organization's owners keep on the Tokens page under "Tokens lent with no say run on", which the
page writes as them, readable by the workflows of the organization's private repositories; or to
none while that list is empty, for an owner to place from the slot's tile. Such a lender is told
the slot's number when the token is stored and, when they list it or when a lend touches a token of
theirs already in the pool, that it is in the organization's keeping, and learns no repository's
name or id from the run. A lend with no say from someone who has a token in the pool already puts
that token in the organization's keeping: it stays where it was lent, goes also where
SYMPHONY_LEND_TO says, and from then on the run names no repository to them. The owners see the
slot on the Tokens page with the lender's login, lend it to more repositories or take it off one,
and delete it; the lender can delete it at any time, can take it off a repository whose id they
know, and lends it to more repositories with any later lend, though the run names none to them.
Since anyone with a GitHub account may do this on a public repository, the pool fills with what is
offered: an owner deletes a slot from its tile, and GitHub's own limits bound the issues and the
runs. A store that stops partway, after the slot is marked as the lender's but before the secret is
written, leaves that mark on a slot with no token, which the next store takes over.

The page shows each token set as a tile, and on your press a tile's settings: a name, the model and
thinking strength its runs take, a lesser model for when the model's weekly limit runs out, whether
it comes back by itself when its limit resets, and Pause. The page writes them, as you, to the
organization (or repository) variable SYMPHONY_CLAUDE_SETTINGS, which the repository's workers read,
and the name to the slot's label variable; neither holds a token, and anyone who can read the
repository's workflows can read them. A tile's X, after you confirm, deletes the slot's secret, its
label, its settings and its place in SYMPHONY_CLAUDE_ACCOUNTS, as you; deleting the secret does not
revoke the token, which you revoke on claude.ai. A slot can also be removed on GitHub under the
organization's Settings, Secrets and variables, Actions. Each token's settings also hold an id,
eight random hexadecimal digits the page or the Token run makes, and the GitHub login of the person
it belongs to; a token the Token run stores also holds that person's account id (since a login can
pass to someone else once an account is renamed or deleted) and, for a token lent with no say, the
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
GitHub", asks GitHub through the service to revoke the token; a personal access token is revoked
on GitHub under Settings, Developer settings, Personal access tokens, and the App's authorization,
which covers every token and refresh token it issued you, under Settings, Applications, Authorized
GitHub Apps.

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
repository. Every token minted from it is an installation token that lives one hour, asked with the
fewest permissions the step needs (metadata alone to resolve a number, contents read to read, the
four write permissions only for the adoption itself) and revoked as soon as the step is done where
the code can, except in the Token workflow of the developer's own organization, which mints it with
every permission the installation has, for all the organization's repositories the App reaches, in
a job that runs only the default branch's script and that anyone who may open an issue there can
start; the token for the look at the pool is revoked before Claude Code starts, the others when the
job ends. The client secrets the sign-in service holds, SymphonyBoard's and the developer's
Microsoft app registration's, live in that service's settings on Cloudflare, outside any repository,
and go from there only to GitHub's and Microsoft's endpoints that issue tokens and, for
SymphonyBoard's, to GitHub's that revokes one. No token, key or signature is ever printed to a log.

## What the Apps never do

They send nothing to any service but GitHub's own API. They have no analytics, no error reporting
and no third party. SymphonyBoard holds Administration only to send the invitation you ask for on the
control panel's Share tab, as you, and changes no setting with it; Symphony Setup holds it where you
installed it, uses it only during an adoption run, and stays installed until you uninstall it. They
read your repository's code only as the
adoption above says (the tree listing, a one-commit checkout of the default branch, and the few
files named), never to keep or send it. They never write to a repository but the adoption's branch,
pull request, labels, issue and settings, each of them yours to undo, and the README that begins a
repository with no commit; in the pool of Claude tokens of the developer's own organization, the
only one holding SymphonyBoard's key, the Token workflow writes with SymphonyBoard's token only what
the section on the control panel says, a slot, the two variables and the lists of repositories that
read them, for the person who lends or manages the token.
They never read a Claude credential (a token you paste into the Tokens page is sealed in your browser
for GitHub, and neither App nor the developer can read it; a token the Token workflow stores for a
lender is plain only on the runner, beside SymphonyBoard's token, until it is sealed, as the section
on organization permissions says), and nothing here runs on
anyone's Claude account but the one a project's own maintainer chooses to run the judge with. The
control panel's Folders tab and the sign-in service, neither of them an App, talk to Microsoft for
the OneDrive you connect, as the section on the Folders tab says; the Apps themselves send Microsoft
nothing.

## Uninstalling

Uninstalling SymphonyBoard stops the collector from reading anything of yours and
undoes nothing in your repository: the files, labels, branch, settings and issues the adoption made
stay yours. Symphony Setup stays installed after the run, acting only during an adoption run;
uninstalling it, at any time, from the repository's or the organization's Settings, GitHub Apps,
also undoes nothing in your repository.

## Children

Symphony is for people who administer GitHub repositories. It is not directed at children.

## Changes

A new version of this statement is published at https://openspineconsortium.com/symphony/apps-privacy.html
and in the front door repository, github.com/OpenSpineConsortium/symphony-start, whose PRIVACY.md is
this text.

Version 31 adds the control panel's Notebooks tab, as the section on the control panel says: it reads
the drive organizer's proposal of notebooks and its catalog from the branch drive-catalog of a private
repository, and whether each notebook's repository exists and whether it is private, internal or
public, and writes the proposal there, as you, when you propose, change or take out a notebook. It
also names the pull request the Agents tab opens to give an agent its token slots, which earlier
versions left out, and says, under SymphonyBoard's Contents permission, that the control panel
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
