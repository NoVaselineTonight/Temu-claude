# TEMU claude

A simple terminal for Claude free credit usage.

Claude Max and Team plans include monthly API credits. They don't pay for regular
Claude Code, but they do pay for the Claude Agent SDK when you use an API key from the
Claude Console organization linked to your plan. This is a small terminal agent built on
that SDK, so the credits can be used for coding.

Windows only.

## Setup
1. Download this repo (Code > Download ZIP) and unzip it anywhere.
2. On claude.ai go to Settings > Billing > API credits and link a Console organization.
   Then create an API key in the Claude Console.
3. Double-click one of the launchers. On first start it installs what is missing
   (uv, and for the agent also Git, GitHub CLI and Python), then asks you to start again.
4. When Notepad opens `API-KEY-GOES-HERE.txt`, paste your key on its own line, save,
   close, and start the launcher again.

## The two launchers
| Launcher | What it does |
|---|---|
| `TEMU Claude Chat.bat` | Plain Claude for questions and brainstorming. Web search only: it cannot touch files, run commands or use GitHub. |
| `TEMU Claude Agent (GitHub).bat` | A coding agent. It edits files, runs commands, and uses `git` and `gh` with your GitHub login. |

### Using the agent
- Drag a project folder onto the launcher, or start it and press Enter to use the
  `workspace` folder.
- It asks `Loop mode [y/N]`. Enter means you type each request yourself. `y` means you
  give one task and it keeps working unattended, waking every few minutes, until the
  spend cap is reached or you press Ctrl+C.
- Type `/exit` to quit.

**The agent runs every command without asking for approval.** That includes deleting
files, `git push` and merging pull requests. Only point it at folders where that is fine.

## Settings
Open a launcher in a text editor. The lines at the top set the model
(`claude-opus-5-5`, `claude-sonnet-5-5` at about half the price, `claude-haiku-5-5`
cheapest), the loop interval and the spend cap.

## Cost
Each reply ends with the cost of that turn and of the session so far. When the monthly
credits run out, requests stop unless your Console organization has bought more.

## Your API key
`API-KEY-GOES-HERE.txt` is in plain text and is ignored by git. Don't share it, and
remove the key before passing your copy of the folder to anyone.

## Multi-agent repos
If the folder you work in has `.agents/agentchat.py` (a coordination kit where several
agents share one repo through a GitHub issue), the agent also gets the rules in
`COMMS.md`, and loop mode only wakes it when a new chat message arrives.
