# Coordination rules for this repo

temu_claude.py adds this file to your instructions whenever the folder you work in contains
`.agents/agentchat.py`. The repo's own `AGENTS.md` is the full protocol and wins if the
two disagree. This is the short version plus what is specific to this Windows PC.

## This machine
- Use `python`, never `python3`. `python3` here is a Microsoft Store stub that does nothing.
- Your shell is PowerShell. `&&` does not work in it; run commands one at a time or use `;`.
- `git` and `gh` are already logged in to the repo owner's GitHub account. Use them as is.
- Nobody approves your commands. Do not delete things outside the repo, do not force-push,
  do not touch other repos.

## Every session, first
1. `python .agents/agentchat.py status`
2. If it says no agent name is set: stop and ask the human for a name. Do not invent one.
3. `python .agents/agentchat.py read` and `python .agents/agentchat.py claims`

## Before changing any file
1. `git fetch origin` then `git switch -c <your-name>/<task> origin/main`
2. `python .agents/agentchat.py claim <paths> --task "<what you will do>"`
   - `CLAIM GRANTED`: edit those paths and nothing else.
   - `CLAIM REFUSED` or `CLAIM LOST`: do not edit them. Pick other work or post a REQUEST.
3. Need another file later? Claim it first.

Use the Write/Edit tools for file changes, not shell redirection. The edit hook only
guards those tools, and going around it gets the PR rejected.

## Talking
All through `python .agents/agentchat.py`. Never comment on the GitHub issue by hand.
- `new` before every commit, and whenever you are woken up.
- If a message mentions `@<your-name>`, answer it with `say INFO "..."` before anything else.
- `say INFO` before merging anything others depend on (API shape, schema, dependency, moved file).
- `say PROGRESS` for milestones, `say BLOCKED` when stuck, `say QUESTION "@agent ..."` to ask.
- Commits and pushes are posted automatically. Do not repeat them.
- Short messages, one per event.

## Finishing a task
1. `git fetch origin` then `git rebase origin/main`. Conflict in a file you do not own: stop, `say QUESTION`.
2. Run the tests.
3. `git push -u origin HEAD`
4. `gh pr create --fill`
5. `gh pr checks --watch`, then `gh pr merge --squash --delete-branch` only if every check passed.
   GitHub does not enforce this on this repo (no branch protection), so it is on you.
6. `python .agents/agentchat.py done --summary "<1-3 lines>" --pr <url>`

Never push to `main`. Abandoning a task: `python .agents/agentchat.py release --all` and `say INFO` why.

## Loop mode
When started with `--loop`, you are woken every few minutes. Finish with the single word
`IDLE` on its own line when you have nothing to do right now. While you are idle, the
script only wakes you when a new chat message arrives.
