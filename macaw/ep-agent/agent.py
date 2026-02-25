#!/usr/bin/env python3
"""Agent List Builder - A Claude Agent SDK sub-agent for creating EDSL AgentLists."""

import asyncio
import itertools
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AgentDefinition,
    HookMatcher,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

import cli as _cli


class VerboseLogger:
    """Coloured diagnostic logger, active only when ``--verbose`` is set."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self._console = Console(stderr=True)
        self._t0: float = time.monotonic()

    def _elapsed(self) -> str:
        return f"{time.monotonic() - self._t0:>8.2f}s"

    def _ts(self) -> str:
        return datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]

    def _prefix(self) -> Text:
        txt = Text()
        txt.append(f"[{self._ts()}]", style="dim cyan")
        txt.append(f" +{self._elapsed()}", style="dim")
        return txt

    # -- public helpers -------------------------------------------------------

    def turn_start(self, turn: int, prompt: str):
        if not self.enabled:
            return
        preview = prompt if len(prompt) <= 120 else prompt[:117] + "..."
        panel = Panel(
            f"[bold]Prompt:[/bold] {preview}",
            title=f"Turn {turn}",
            border_style="bright_blue",
            subtitle=self._ts(),
        )
        self._console.print(panel)

    def msg_received(self, msg_type: str, **fields):
        if not self.enabled:
            return
        prefix = self._prefix()
        prefix.append(f"  MSG ", style="bold yellow")
        prefix.append(msg_type, style="bold white")
        for k, v in fields.items():
            prefix.append(f"  {k}=", style="dim")
            prefix.append(str(v), style="green")
        self._console.print(prefix)

    def block(self, block_type: str, detail: str = ""):
        if not self.enabled:
            return
        prefix = self._prefix()
        prefix.append(f"    BLOCK ", style="dim magenta")
        prefix.append(block_type, style="bold magenta")
        if detail:
            prefix.append(f"  {detail}", style="dim")
        self._console.print(prefix)

    def tool_use(self, name: str, tool_id: str, input_preview: str):
        if not self.enabled:
            return
        prefix = self._prefix()
        prefix.append(f"    TOOL ", style="bold red")
        prefix.append(name, style="bold white")
        prefix.append(f"  id={tool_id}", style="dim")
        if input_preview:
            short = input_preview if len(input_preview) <= 100 else input_preview[:97] + "..."
            prefix.append(f"\n             {short}", style="dim yellow")
        self._console.print(prefix)

    def result(self, **fields):
        if not self.enabled:
            return
        tbl = Table(title="ResultMessage", border_style="green", show_lines=False)
        tbl.add_column("field", style="cyan")
        tbl.add_column("value", style="white")
        for k, v in fields.items():
            tbl.add_row(k, str(v))
        self._console.print(tbl)

    def flow(self, msg: str, style: str = "bold bright_black"):
        """Log a control-flow decision (break / continue / prompt)."""
        if not self.enabled:
            return
        prefix = self._prefix()
        prefix.append(f"  FLOW ", style="bold blue")
        prefix.append(msg, style=style)
        self._console.print(prefix)

    def info(self, msg: str):
        if not self.enabled:
            return
        prefix = self._prefix()
        prefix.append(f"  INFO ", style="bold green")
        prefix.append(msg)
        self._console.print(prefix)


_BASE_DIR = Path(__file__).resolve().parent
_SUB_AGENTS_DIR = _BASE_DIR / "sub-agents"
_SKILLS_DIR = _BASE_DIR / "skills"

_DEFAULT_TOOLS = ["Read", "Glob", "Bash", "WebSearch", "WebFetch", "Write", "Edit"]
_DEFAULT_MODEL = "sonnet"


class StatusLine:
    """Persistent single-line spinner that shows agent activity.

    Renders a "Thinking..." message with an animated spinner and optional
    tool-call detail, all on one line using \\r + ANSI clear-to-EOL so the
    cursor never advances.  Call :meth:`print` to emit real output (the
    status line is temporarily cleared, the text printed, then the spinner
    resumes).
    """

    _SPINNER = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    _CLEAR = "\r\033[K"

    def __init__(self):
        self._detail: str = ""
        self._lock = threading.Lock()
        self._active = False
        self._thread: threading.Thread | None = None

    # -- public API -----------------------------------------------------------

    def start(self):
        """Begin the spinner."""
        with self._lock:
            self._active = True
            self._detail = ""
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the spinner and clear the line."""
        with self._lock:
            self._active = False
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None
        sys.stderr.write(self._CLEAR)
        sys.stderr.flush()

    def set_detail(self, detail: str):
        """Update the tool-call detail shown after 'Thinking...'."""
        with self._lock:
            self._detail = detail

    def print(self, text: str):
        """Print *text* on its own line(s), preserving the spinner."""
        with self._lock:
            sys.stderr.write(self._CLEAR)
            sys.stderr.flush()
        print(text)
        # spinner thread will redraw on next tick

    # -- internals ------------------------------------------------------------

    def _spin(self):
        while True:
            with self._lock:
                if not self._active:
                    return
                frame = next(self._SPINNER)
                detail = f"  [{self._detail}]" if self._detail else ""
                line = f"{self._CLEAR}{frame} Thinking...{detail}"
            sys.stderr.write(line)
            sys.stderr.flush()
            time.sleep(0.08)


def _parse_skill_description(skill_file: Path) -> str | None:
    """Extract the description from YAML frontmatter in a SKILL.md file."""
    text = skill_file.read_text()
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end == -1:
        return None
    for line in text[3:end].splitlines():
        if line.startswith("description:"):
            desc = line[len("description:"):].strip()
            # Strip optional quotes
            if len(desc) >= 2 and desc[0] in ('"', "'") and desc[-1] == desc[0]:
                desc = desc[1:-1]
            return desc
    return None


def _build_skills_catalog() -> str:
    """Build a short catalog of available skills from skills/ directory.

    Each skill is a subdirectory containing:
      - SKILL.md (required) — full skill content with YAML frontmatter
        (name, description fields in frontmatter)

    Returns a brief index that gets appended to each sub-agent's prompt.
    Agents can then Read the full SKILL.md on demand.
    """
    if not _SKILLS_DIR.is_dir():
        return ""

    entries = []
    for entry in sorted(_SKILLS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        skill_file = entry / "SKILL.md"
        if not skill_file.exists():
            continue
        description = _parse_skill_description(skill_file)
        if not description:
            continue
        entries.append(f"- `skills/{entry.name}/SKILL.md` — {description}")

    if not entries:
        return ""

    return (
        "\n## Available skills\n\n"
        "The following skills are in `skills/`. "
        "Use the Read tool to load any skill you need before using it.\n\n"
        + "\n".join(entries)
    )


def _load_sub_agents() -> dict[str, AgentDefinition]:
    """Auto-discover sub-agents from sub-agents/ directory.

    Each sub-directory becomes a sub-agent. Expected files:
      - prompt.md       (required) — the sub-agent's system prompt
      - description.md  (required) — short description for the main agent
      - tools.txt       (optional) — one tool name per line, overrides defaults
      - model.txt       (optional) — model name, overrides default

    Shared skills from skills/*/SKILL.md are automatically cataloged and
    appended to every sub-agent's prompt.
    """
    agents: dict[str, AgentDefinition] = {}
    if not _SUB_AGENTS_DIR.is_dir():
        return agents

    skills_catalog = _build_skills_catalog()

    for entry in sorted(_SUB_AGENTS_DIR.iterdir()):
        if not entry.is_dir():
            continue

        prompt_file = entry / "prompt.md"
        desc_file = entry / "description.md"
        if not prompt_file.exists() or not desc_file.exists():
            continue

        name = entry.name
        agent_prompt = prompt_file.read_text().strip()
        description = desc_file.read_text().strip()

        # Append skills catalog so the agent knows what's available
        if skills_catalog:
            prompt = f"{agent_prompt}\n\n{skills_catalog}"
        else:
            prompt = agent_prompt

        tools_file = entry / "tools.txt"
        if tools_file.exists():
            tools = [t.strip() for t in tools_file.read_text().splitlines() if t.strip()]
        else:
            tools = list(_DEFAULT_TOOLS)

        model_file = entry / "model.txt"
        model = model_file.read_text().strip() if model_file.exists() else _DEFAULT_MODEL

        agents[name] = AgentDefinition(
            description=description,
            tools=tools,
            model=model,
            prompt=prompt,
        )

    Console(stderr=True).print(
        f"[dim]Loaded {len(agents)} sub-agents: {', '.join(agents.keys())}[/dim]"
    )

    return agents


MAIN_AGENT_SYSTEM_PROMPT = (_BASE_DIR / "system_prompt.md").read_text().strip()

_ERROR_LOG_REMINDER = (
    "REMINDER: You just encountered an error or unexpected result. "
    "Your BLOCKING REQUIREMENT says you MUST append a JSONL entry to errors.jsonl "
    "BEFORE attempting any fix. Read skills/error-logging/SKILL.md for the format. "
    "Include: (1) the exact command or code that failed, "
    "(2) the FULL traceback / output verbatim — never summarize, "
    "(3) what you were trying to do. Do that now."
)

_ERROR_PATTERNS = [
    "Traceback (most recent call last)",
    "Error:", "ERROR:",
    "FileNotFoundError", "ModuleNotFoundError", "ImportError",
    "PermissionError", "IsADirectoryError", "NotADirectoryError",
    "No such file or directory",
    "command not found",
    "not found",
    "is empty",
    "are empty",
    "not there",
    "directory is empty",
    "actually went",
    "actually saved",
    "wrong directory",
    "fatal:",
    "pathspec",
    "did not match any files",
    "mock",
    "fake data",
    "synthetic data",
    "placeholder",
]


def _looks_like_error(text: str) -> bool:
    """Heuristic check for error-like content in tool output."""
    if not isinstance(text, str):
        return False
    lower = text.lower()
    for pat in _ERROR_PATTERNS:
        if pat.lower() in lower:
            return True
    return False


async def _post_tool_use_hook(input_data, tool_use_id, context):
    """Fires after every tool use. Injects a reminder if output looks like an error."""
    response = input_data.get("tool_response", "") if isinstance(input_data, dict) else ""
    response_str = str(response) if response else ""

    if _looks_like_error(response_str):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": _ERROR_LOG_REMINDER,
            }
        }
    return {}


async def _post_tool_failure_hook(input_data, tool_use_id, context):
    """Fires when a tool fails entirely. Always injects a reminder."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUseFailure",
            "additionalContext": _ERROR_LOG_REMINDER,
        }
    }


async def _collect_answers(questions):
    """Present questions to the user and collect answers via styled prompt."""
    answers = []
    for q in questions:
        question_text = q.get("question", "")
        header = q.get("header")
        options = q.get("options", [])

        if header:
            _console.print(f"\n[bold cyan][{header}][/bold cyan]")
        _console.print(f"\n{question_text}")

        if options:
            for i, opt in enumerate(options, 1):
                label = opt.get("label", "")
                desc = opt.get("description", "")
                _console.print(f"  [bold]{i}.[/bold] {label}" + (f" [dim]— {desc}[/dim]" if desc else ""))
            raw = await _cli.get_user_input()
            if raw.strip().isdigit():
                idx = int(raw.strip()) - 1
                if 0 <= idx < len(options):
                    answers.append(options[idx].get("label", raw))
                else:
                    answers.append(raw)
            else:
                raw = _cli.expand_file_refs(raw, cwd=str(_BASE_DIR))
                answers.append(raw)
        else:
            raw = await _cli.get_user_input()
            raw = _cli.expand_file_refs(raw, cwd=str(_BASE_DIR))
            answers.append(raw)

    return answers


def _format_usage(usage: dict | None) -> str:
    """Format a ResultMessage usage dict into a readable token breakdown."""
    if not usage:
        return ""
    parts = []
    for key in [
        "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
        "output_tokens", "thinking_tokens",
    ]:
        val = usage.get(key)
        if val:
            label = key.replace("_", " ").replace("tokens", "").strip()
            parts.append(f"{label}: {val:,}")
    return "  |  ".join(parts) if parts else str(usage)


def _ts() -> str:
    """Return an ISO-8601 UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()


def _event(kind: str, **data) -> dict:
    """Create a timestamped event dict."""
    return {"ts": _ts(), "kind": kind, **data}


def _process_message_blocks(msg, turn_number, status, assistant_texts, events,
                            vlog: VerboseLogger | None = None):
    """Process content blocks from an AssistantMessage.

    Returns a list of AskUserQuestion question dicts if one was found,
    or None otherwise.
    """
    if vlog is None:
        vlog = VerboseLogger(enabled=False)

    ask_questions = None
    model = msg.model
    parent = msg.parent_tool_use_id
    vlog.msg_received("AssistantMessage", model=model,
                      parent_tool_use_id=parent,
                      blocks=len(msg.content))

    for block in msg.content:
        if isinstance(block, TextBlock):
            text = block.text.strip()
            if text:
                preview = text if len(text) <= 80 else text[:77] + "..."
                vlog.block("TextBlock", preview)
                status.stop()
                _cli.print_assistant(text)
                status.start()
                assistant_texts.append(text)
                events.append(_event(
                    "assistant_text",
                    turn=turn_number,
                    model=model,
                    parent_tool_use_id=parent,
                    text=text,
                ))
        elif isinstance(block, ThinkingBlock):
            thinking_len = len(block.thinking) if block.thinking else 0
            vlog.block("ThinkingBlock", f"{thinking_len} chars")
            status.set_detail("thinking")
            events.append(_event(
                "thinking",
                turn=turn_number,
                model=model,
                text=block.thinking,
            ))
        elif isinstance(block, ToolUseBlock):
            import json
            input_str = json.dumps(block.input, default=str) if block.input else ""
            vlog.tool_use(block.name, block.id, input_str)

            detail = block.name
            hint_str = ""
            if isinstance(block.input, dict):
                hint = (
                    block.input.get("file_path")
                    or block.input.get("pattern")
                    or block.input.get("command")
                    or block.input.get("query")
                    or block.input.get("url")
                    or ""
                )
                if isinstance(hint, str) and hint:
                    hint_str = " ".join(hint.split())
                    short = hint_str if len(hint_str) <= 40 else "…" + hint_str[-39:]
                    detail = f"{block.name}: {short}"
            status.set_detail(detail)
            _cli.print_tool_activity(block.name, hint_str)

            events.append(_event(
                "tool_use",
                turn=turn_number,
                model=model,
                parent_tool_use_id=parent,
                tool_name=block.name,
                tool_id=block.id,
                tool_input=block.input,
            ))
            if block.name == "AskUserQuestion":
                questions = (
                    block.input.get("questions", [])
                    if isinstance(block.input, dict)
                    else []
                )
                vlog.info(f"AskUserQuestion detected: {len(questions)} question(s)")
                ask_questions = questions
            elif block.name == "Task":
                agent_name = block.input.get("agent", "") if isinstance(block.input, dict) else ""
                _cli.print_delegation(agent_name)
        elif isinstance(block, ToolResultBlock):
            content = block.content
            content_len = len(content) if isinstance(content, str) else 0
            vlog.block("ToolResultBlock",
                       f"tool_use_id={block.tool_use_id}  is_error={block.is_error}  len={content_len}")
            status.set_detail("processing result")
            _cli.print_tool_result_summary(
                block.tool_use_id, is_error=block.is_error,
                chars=content_len if isinstance(content_len, int) else 0,
            )
            if isinstance(content, str) and len(content) > 2000:
                content = content[:2000] + "... (truncated)"
            events.append(_event(
                "tool_result",
                turn=turn_number,
                tool_use_id=block.tool_use_id,
                is_error=block.is_error,
                content=content,
            ))

    return ask_questions


async def run_agent(initial_prompt, answer_fn=None, interactive=True, verbose=False):
    """Run the agent conversation loop using a stateful ClaudeSDKClient.

    Args:
        initial_prompt: The user's initial request / description.
        answer_fn: Optional callable ``(questions) -> list[str]``.
            Defaults to :func:`_collect_answers` (interactive stdin).
        interactive: If True, prompt the user for follow-ups instead of exiting.
        verbose: If True, emit detailed coloured diagnostic logs to stderr.

    Returns:
        dict with ``conversation``, ``total_cost_usd``, and ``events``.
    """
    if answer_fn is None:
        answer_fn = _collect_answers

    vlog = VerboseLogger(enabled=verbose)

    conversation = []
    events: list[dict] = []
    total_cost_usd = 0.0
    system_prompt = MAIN_AGENT_SYSTEM_PROMPT + _build_skills_catalog()
    turn_number = 0

    sub_agents = _load_sub_agents()
    vlog.info(f"Loaded {len(sub_agents)} sub-agents: {list(sub_agents.keys())}")
    vlog.info(f"interactive={interactive}")

    options = ClaudeAgentOptions(
        cwd=str(_BASE_DIR),
        allowed_tools=[
            "Read",
            "Write",
            "Edit",
            "Glob",
            "Bash",
            "WebSearch",
            "WebFetch",
            "AskUserQuestion",
            "Task",
        ],
        system_prompt=system_prompt,
        permission_mode="acceptEdits",
        max_turns=25,
        agents=sub_agents,
        max_buffer_size=5 * 1024 * 1024,  # 5MB buffer (safety margin)
        hooks={
            "PostToolUse": [
                HookMatcher(matcher="Bash", hooks=[_post_tool_use_hook]),
            ],
            "PostToolUseFailure": [
                HookMatcher(hooks=[_post_tool_failure_hook]),
            ],
        },
    )

    async with ClaudeSDKClient(options=options) as client:
        prompt = initial_prompt

        while True:
            turn_number += 1
            vlog.turn_start(turn_number, prompt)

            events.append(_event(
                "turn_start",
                turn=turn_number,
                prompt=prompt,
                system_prompt=system_prompt if turn_number == 1 else "(same)",
            ))

            await client.query(prompt)
            vlog.info(f"client.query() returned, awaiting response stream...")

            ask_questions = None
            assistant_texts = []
            status = StatusLine()
            status.start()
            msg_count = 0

            async for msg in client.receive_response():
                msg_count += 1

                if isinstance(msg, AssistantMessage):
                    ask_questions = _process_message_blocks(
                        msg, turn_number, status, assistant_texts, events, vlog,
                    )
                    # AskUserQuestion needs user input — break immediately so
                    # we can present the questions. The SDK won't send
                    # ResultMessage until the answer is provided, so waiting
                    # here would deadlock.
                    if ask_questions is not None:
                        status.stop()
                        break

                elif isinstance(msg, UserMessage):
                    vlog.msg_received("UserMessage",
                                     parent_tool_use_id=msg.parent_tool_use_id)
                    events.append(_event(
                        "user_message",
                        turn=turn_number,
                        parent_tool_use_id=msg.parent_tool_use_id,
                    ))

                elif isinstance(msg, SystemMessage):
                    vlog.msg_received("SystemMessage",
                                     subtype=msg.subtype, data=str(msg.data)[:80])
                    events.append(_event(
                        "system_message",
                        turn=turn_number,
                        subtype=msg.subtype,
                        data=msg.data,
                    ))

                elif isinstance(msg, ResultMessage):
                    status.stop()
                    vlog.result(
                        session_id=msg.session_id,
                        is_error=msg.is_error,
                        num_turns=msg.num_turns,
                        duration_ms=msg.duration_ms,
                        duration_api_ms=msg.duration_api_ms,
                        total_cost_usd=msg.total_cost_usd,
                        usage=msg.usage,
                    )
                    if msg.total_cost_usd:
                        total_cost_usd += msg.total_cost_usd
                        _cli.print_cost(msg.total_cost_usd, msg.usage)
                    events.append(_event(
                            "result",
                            turn=turn_number,
                            session_id=msg.session_id,
                            is_error=msg.is_error,
                            num_turns=msg.num_turns,
                            duration_ms=msg.duration_ms,
                            duration_api_ms=msg.duration_api_ms,
                            total_cost_usd=msg.total_cost_usd,
                            usage=msg.usage,
                        ))

            status.stop()
            vlog.info(f"Response stream ended: {msg_count} messages received")
            vlog.info(f"ask_questions={'set (' + str(len(ask_questions)) + ' q)' if ask_questions is not None else 'None'}  "
                      f"assistant_texts={len(assistant_texts)} chunks")

            # Record what the assistant said
            if assistant_texts:
                conversation.append({"role": "assistant", "content": "\n".join(assistant_texts)})

            # If no questions, the agent finished (delegated or completed)
            if ask_questions is None:
                if not interactive:
                    vlog.flow("No questions & non-interactive -> breaking loop", style="bold red")
                    break

                vlog.flow("No questions -> prompting user for follow-up", style="bold yellow")
                _console.print()
                user_text = await _cli.get_user_input("What next? > ")
                if not user_text or user_text.strip() == "\\quit":
                    vlog.flow("User typed \\quit or EOF -> breaking loop", style="bold red")
                    break
                user_text = _cli.expand_file_refs(user_text, cwd=str(_BASE_DIR))

                vlog.flow(f"Next prompt: {user_text[:80]}", style="bold green")
                conversation.append({"role": "user", "content": user_text})
                events.append(_event(
                    "user_answer",
                    turn=turn_number,
                    questions=[{"question": "follow-up"}],
                    answers=[user_text],
                ))
                prompt = user_text
                continue

            # Present questions and collect answers
            vlog.flow(f"Presenting {len(ask_questions)} question(s) to user", style="bold green")
            answers = await answer_fn(ask_questions)
            answer_text = "; ".join(answers) if len(answers) > 1 else (answers[0] if answers else "")
            vlog.flow(f"Answer: {answer_text[:80]}", style="bold green")
            conversation.append({"role": "user", "content": answer_text})
            events.append(_event(
                "user_answer",
                turn=turn_number,
                questions=ask_questions,
                answers=answers,
            ))
            prompt = answer_text

    vlog.info(f"Session complete. Total cost: ${total_cost_usd:.4f}")
    return {
        "conversation": conversation,
        "total_cost_usd": total_cost_usd,
        "events": events,
    }


_console = Console()

async def main():
    import argparse

    parser = argparse.ArgumentParser(description="EDSL study builder agent")
    parser.add_argument("description", nargs="*", help="Task description for the agent")
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Exit after the agent finishes instead of prompting for follow-ups.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Emit detailed coloured diagnostic logs to stderr.",
    )
    parser.add_argument(
        "--sessions",
        action="store_true",
        help="List recent saved sessions and exit.",
    )
    parser.add_argument(
        "--resume",
        metavar="ID",
        help="Resume a previous session by ID (or unique prefix).",
    )
    args = parser.parse_args()

    if args.sessions:
        _cli.list_sessions()
        return

    # Resume a prior session
    if args.resume:
        session_data = _cli.load_session(args.resume)
        if session_data is not None:
            _console.print(f"[bold cyan]Resuming session {session_data['id']}[/bold cyan]")
            _console.print(f"[dim]Original prompt: {session_data.get('prompt_preview', '')}[/dim]")
            _console.print(f"[dim]Prior cost: ${session_data.get('total_cost_usd', 0):.4f}  |  "
                           f"Turns: {session_data.get('turns', '?')}[/dim]\n")
            resume_context = _cli.build_resume_context(session_data)
            follow_up = await _cli.get_user_input("Continue with > ")
            if not follow_up or follow_up.strip() == "\\quit":
                return
            follow_up = _cli.expand_file_refs(follow_up, cwd=str(_BASE_DIR))
            user_description = resume_context + follow_up
        else:
            return
    else:
        user_description = " ".join(args.description) if args.description else None
        if not user_description:
            _cli.print_greeting()
            user_description = await _cli.get_user_input()
            if not user_description or user_description.strip() == "\\quit":
                return
            user_description = _cli.expand_file_refs(user_description, cwd=str(_BASE_DIR))

    initial_prompt = user_description
    result = await run_agent(
        user_description,
        interactive=not args.no_interactive,
        verbose=args.verbose,
    )
    _cli.save_session(result, initial_prompt=initial_prompt)
    _cli.print_total_cost(result["total_cost_usd"])


if __name__ == "__main__":
    asyncio.run(main())
