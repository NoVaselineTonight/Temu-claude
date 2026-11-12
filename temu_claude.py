# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk"]
# ///
"""TEMU Claude: a small coding-agent CLI on the Claude Agent SDK, billed to an API key.

Run from the project you want to work on:
    uv run path\\to\\temu_claude.py [--model claude-opus-5-5] [--yolo] [--loop MINUTES] [--max-usd N]
    uv run path\\to\\temu_claude.py --chat

The API key is read from API-KEY-GOES-HERE.txt next to this file (or ANTHROPIC_API_KEY).
Type /exit to quit. --yolo skips the y/n prompt before shell commands.

--loop MINUTES: unattended mode. You type one task; after each turn the script
waits MINUTES, then wakes the agent to check the coordination chat and carry on.
It stops at --max-usd (default 10 in loop mode) or on Ctrl+C. See AGENT_NOTES.md.
"""
import argparse
import asyncio
import contextlib
import os
import subprocess
import sys
import time
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)

os.system("")  # turns on ANSI colours in the Windows console
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RED, BOLD, DIM, OFF = "\033[91m", "\033[1m", "\033[2m", "\033[0m"
YELLOW = "\033[38;5;220m"
FIRE = [196, 202, 208, 214, 220, 226]  # banner gradient, red to yellow, one colour per line
BANNER = r"""
████████╗███████╗███╗   ███╗██╗   ██╗     ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗
╚══██╔══╝██╔════╝████╗ ████║██║   ██║    ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝
   ██║   █████╗  ██╔████╔██║██║   ██║    ██║     ██║     ███████║██║   ██║██║  ██║█████╗
   ██║   ██╔══╝  ██║╚██╔╝██║██║   ██║    ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝
   ██║   ███████╗██║ ╚═╝ ██║╚██████╔╝    ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗
   ╚═╝   ╚══════╝╚═╝     ╚═╝ ╚═════╝      ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
""".strip("\n").splitlines()
TAGLINE = "same Claude, 90% off, ships in 4-6 weeks"
RULE = "━" * 92

HERE = Path(__file__).resolve().parent
COMMS_FILE = HERE / "COMMS.md"
KEY_FILE = HERE / "API-KEY-GOES-HERE.txt"

LOOP_RULES = (
    "\n\nYou are running unattended in a loop: nobody will answer questions, so make "
    "reasonable decisions yourself. When you have nothing left to do right now (task "
    "finished, or blocked waiting on someone else), end your reply with the single word "
    "IDLE on its own line. You will be woken again later."
)
WAKE = (
    "Wake-up check. Run `python .agents/agentchat.py new` if this repo has it, answer "
    "anything addressed to you, then continue your task from where you stopped. "
    "If there is nothing to do, reply with just IDLE."
)


def load_key():
    """Use ANTHROPIC_API_KEY if set, else the first sk-ant-... line in the key file."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return
    if KEY_FILE.exists():
        for line in KEY_FILE.read_text(encoding="utf-8-sig").splitlines():
            if line.strip().startswith("sk-ant-"):
                os.environ["ANTHROPIC_API_KEY"] = line.strip()
                return


class Spinner:
    """A one-line 'working' animation, only when output is a real terminal."""

    FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self):
        self.task = None
        self.enabled = sys.stdout.isatty()

    def start(self, label="cooking"):
        if self.enabled and self.task is None:
            self.task = asyncio.create_task(self._run(label))

    async def _run(self, label):
        t0, i = time.time(), 0
        while True:
            frame = self.FRAMES[i % len(self.FRAMES)]
            sys.stdout.write(f"\r{YELLOW}{frame}{OFF}{DIM} {label} {time.time() - t0:.0f}s{OFF}{RED}")
            sys.stdout.flush()
            i += 1
            await asyncio.sleep(0.1)

    async def stop(self):
        if self.task is not None:
            self.task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.task
            self.task = None
            sys.stdout.write("\r\033[2K")
            sys.stdout.flush()


SPINNER = Spinner()


def show_header(rows):
    print()
    for colour, line in zip(FIRE, BANNER):
        print(f"\033[38;5;{colour}m{BOLD}{line}{OFF}")
    print(f"{DIM}{TAGLINE:>92}{OFF}")
    print(f"{RED}{RULE}")
    for name, value in rows:
        print(f" {YELLOW}▸{RED} {BOLD}{name:<7}{OFF}{RED}{value}")
    print(RULE)


async def ask_permission(tool_name, tool_input, context):
    await SPINNER.stop()
    detail = tool_input.get("command") or tool_input.get("file_path") or tool_input
    answer = await asyncio.to_thread(input, f"\n {YELLOW}?{RED} allow {BOLD}{tool_name}{OFF}{RED}: {detail} ? [Y/n] ")
    if answer.strip().lower() in ("", "y", "yes"):
        return PermissionResultAllow()
    return PermissionResultDeny(message="User declined this action.")


def new_chat_messages():
    """Unread coordination-chat messages, '' if none, None if the repo has no usable agentchat.

    Costs no credits. `agentchat.py new` marks messages as seen, so whatever it
    returns must be handed to the agent.
    """
    script = Path(".agents/agentchat.py")
    if not script.exists():
        return None
    try:
        p = subprocess.run([sys.executable, str(script), "new"], capture_output=True, text=True, timeout=60)
    except Exception:
        return None
    if p.returncode != 0:
        return None
    out = p.stdout.strip()
    return "" if out == "(no new messages)" else out


async def run_turn(client, prompt, state):
    """Send one prompt, print the reply, return the final text of the turn."""
    await client.query(prompt)
    final = ""
    SPINNER.start()
    try:
        async for message in client.receive_response():
            await SPINNER.stop()
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
                        final = block.text
                    elif isinstance(block, ToolUseBlock):
                        brief = block.input.get("command") or block.input.get("file_path") or ""
                        print(f" {YELLOW}▸{OFF}{DIM} {block.name}  {brief}{OFF}{RED}")
            if isinstance(message, ResultMessage):
                # total_cost_usd is a running total for the whole session, not per turn.
                total = message.total_cost_usd or state["total"]
                print(f"{DIM}{'─' * 40}{OFF}")
                print(f" {YELLOW}${RED}{BOLD} turn ${total - state['total']:.3f}   session ${total:.2f}{OFF}{RED}")
                state["total"] = total
            else:
                SPINNER.start()
    finally:
        await SPINNER.stop()
    return final


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="claude-opus-5-5")
    parser.add_argument("--yolo", action="store_true", help="never ask before running tools")
    parser.add_argument("--loop", type=float, metavar="MINUTES", help="unattended: wake every MINUTES")
    parser.add_argument("--max-usd", type=float, help="stop when the session has cost this much")
    parser.add_argument("--task", help="first prompt (otherwise you are asked)")
    parser.add_argument("--chat", action="store_true", help="plain chat: no files, no shell, web search only")
    args = parser.parse_args()
    if args.chat and (args.loop or args.yolo):
        sys.exit("--chat cannot be combined with --loop or --yolo.")
    if args.loop and not args.yolo:
        sys.exit("--loop needs --yolo: nobody is there to answer the y/n prompts.")
    if args.loop and args.max_usd is None:
        args.max_usd = 10.0

    load_key()
    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("HACK_ALLOW_PLAN"):
        sys.exit(
            f"No API key found.\nOpen {KEY_FILE.name} (next to this script), paste your key "
            "on its own line (it starts with sk-ant-), save, and start again."
        )

    system_prompt = {"type": "preset", "preset": "claude_code"}
    comms = Path(".agents/agentchat.py").exists() and COMMS_FILE.exists()
    if comms:
        system_prompt["append"] = COMMS_FILE.read_text(encoding="utf-8")

    options = ClaudeAgentOptions(
        model=args.model,
        cwd=os.getcwd(),
        system_prompt=system_prompt,
        setting_sources=["project"],
        permission_mode="bypassPermissions" if args.yolo else "acceptEdits",
        can_use_tool=None if args.yolo else ask_permission,
    )
    if args.chat:
        # Plain Claude for talking: cannot touch files, the shell, git or GitHub.
        comms = False
        web = ["WebSearch", "WebFetch"]
        options = ClaudeAgentOptions(
            model=args.model,
            cwd=os.getcwd(),
            system_prompt=(
                "You are Claude, talking with the user in a terminal chat: brainstorming, "
                "questions, planning, writing. You cannot read or change files or run "
                "commands here; you can search the web. Plain text only, the terminal "
                "does not render markdown."
            ),
            setting_sources=[],
            tools=web,
            allowed_tools=web,
            permission_mode="dontAsk",
        )

    state = {"total": 0.0}
    if args.chat:
        rows = [("mode", "chat only: no files, no shell, no GitHub")]
    elif args.loop:
        rows = [("mode", f"agent, loop every {args.loop:g} min, cap ${args.max_usd:g}")]
    else:
        rows = [("mode", "agent" + (", no approval prompts" if args.yolo else ""))]
    rows.append(("model", args.model))
    if not args.chat:
        rows.append(("folder", os.getcwd()))
    if comms:
        rows.append(("comms", f"coordination repo detected, {COMMS_FILE.name} loaded"))
    rows.append(("quit", "Ctrl+C" if args.loop else "/exit"))
    show_header(rows)

    async with ClaudeSDKClient(options=options) as client:
        if args.loop:
            task = args.task or (await asyncio.to_thread(input, f"\n{YELLOW}{BOLD}task ❯ {OFF}{RED}")).strip()
            if not task:
                return
            idle = "IDLE" in (await run_turn(client, task + LOOP_RULES, state))[-40:]
            while state["total"] < args.max_usd:
                note = " (idle)" if idle else ""
                print(f"{DIM} zz [{time.strftime('%H:%M')}] sleeping {args.loop:g} min{note}{OFF}{RED}")
                await asyncio.sleep(args.loop * 60)
                news = new_chat_messages()
                if idle and news == "":
                    continue  # nothing new and nothing to do: do not spend credits
                prompt = WAKE if not news else f"New coordination chat messages:\n{news}\n\n{WAKE}"
                idle = "IDLE" in (await run_turn(client, prompt, state))[-40:]
            print(f"{BOLD}Stopped: session cost reached the ${args.max_usd:g} cap.{OFF}{RED}")
            return

        while True:
            try:
                prompt = args.task or (await asyncio.to_thread(input, f"\n{YELLOW}{BOLD}❯ {OFF}{RED}")).strip()
                args.task = None
            except (EOFError, KeyboardInterrupt):
                break
            if not prompt:
                continue
            if prompt in ("/exit", "/quit"):
                break
            await run_turn(client, prompt, state)
            if args.max_usd and state["total"] >= args.max_usd:
                print(f"{BOLD}Stopped: session cost reached the ${args.max_usd:g} cap.{OFF}{RED}")
                break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\nStopped.")
    finally:
        print(OFF, end="")
