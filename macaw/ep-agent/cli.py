"""Rich CLI interface for the EDSL agent — markdown rendering, file upload, styled prompts."""

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule

_console = Console()
_err_console = Console(stderr=True)

_HISTORY_FILE = Path.home() / ".cache" / "ep-agent" / "history"
_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
_session = PromptSession(history=FileHistory(str(_HISTORY_FILE)))

_FILE_REF_RE = re.compile(r"@([\w./_~-][\w./_~-]*)")


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def print_assistant(text: str):
    """Render assistant text as rich Markdown."""
    _console.print()
    _console.print(Markdown(text))


# ---------------------------------------------------------------------------
# File @-references
# ---------------------------------------------------------------------------

def expand_file_refs(user_input: str, cwd: str | None = None) -> str:
    """Resolve ``@path/to/file`` references to absolute paths.

    Does NOT inline file contents — the agent has the ``Read`` tool for that.
    Instead, each ``@path`` is replaced with its resolved absolute path so the
    agent knows exactly which file the user means.

    Supports:
      - Relative paths resolved against *cwd* (or the current directory)
      - ``~/`` home-dir expansion
      - Quoted paths with spaces: ``@"path with spaces/file.txt"``
    """
    base = Path(cwd) if cwd else Path.cwd()

    def _replace(match: re.Match) -> str:
        raw = match.group(1).strip().strip('"').strip("'")
        p = Path(os.path.expanduser(raw))
        if not p.is_absolute():
            p = base / p
        p = p.resolve()
        if not p.exists():
            _err_console.print(f"[dim red]  warning: {raw} does not exist[/dim red]")
            return match.group(0)
        return str(p)

    # Handle quoted @"path with spaces"
    result = re.sub(r'@"([^"]+)"', _replace, user_input)
    result = re.sub(r"@'([^']+)'", _replace, result)
    # Handle unquoted @paths (no spaces)
    result = _FILE_REF_RE.sub(_replace, result)
    return result


# ---------------------------------------------------------------------------
# Styled input prompt
# ---------------------------------------------------------------------------

async def get_user_input(prompt_text: str = "> ") -> str:
    """Prompt the user with history and return their input.

    This is async-safe — it uses ``prompt_async`` so it works inside a
    running event loop (e.g. when called from ``asyncio.run(main())``).

    Returns the raw string (without file expansion).
    Use ``expand_file_refs()`` to process @-references afterwards.

    Returns empty string on EOF (Ctrl-D).
    """
    try:
        text = await _session.prompt_async(
            HTML(f"<b><ansibrightcyan>{prompt_text}</ansibrightcyan></b>"),
        )
        return text
    except (EOFError, KeyboardInterrupt):
        return ""


# ---------------------------------------------------------------------------
# Tool activity display
# ---------------------------------------------------------------------------

def print_tool_activity(tool_name: str, detail: str = ""):
    """Print a one-line tool activity indicator."""
    t = Text()
    t.append("  >> ", style="dim")
    t.append(tool_name, style="bold yellow")
    if detail:
        short = detail if len(detail) <= 60 else detail[:57] + "..."
        t.append(f"  {short}", style="dim")
    _err_console.print(t)


def print_tool_result_summary(tool_name: str, is_error: bool = False, chars: int = 0):
    """Print a brief tool result summary."""
    t = Text()
    t.append("  << ", style="dim")
    t.append(tool_name, style="bold green" if not is_error else "bold red")
    if is_error:
        t.append(" (error)", style="red")
    if chars:
        t.append(f"  {chars:,} chars", style="dim")
    _err_console.print(t)


# ---------------------------------------------------------------------------
# Cost display
# ---------------------------------------------------------------------------

def print_cost(cost_usd: float, usage: dict | None = None):
    """Print a styled cost line with optional token breakdown."""
    t = Text()
    t.append("\n  Cost: ", style="dim")
    t.append(f"${cost_usd:.4f}", style="bold green" if cost_usd < 0.05 else "bold yellow")
    if usage:
        parts = []
        for key, label in [
            ("input_tokens", "in"),
            ("cache_creation_input_tokens", "cache write"),
            ("cache_read_input_tokens", "cache read"),
            ("output_tokens", "out"),
            ("thinking_tokens", "thinking"),
        ]:
            val = usage.get(key)
            if val:
                parts.append(f"{label}: {val:,}")
        if parts:
            t.append(f"  [{' | '.join(parts)}]", style="dim")
    _console.print(t)


def print_total_cost(cost_usd: float):
    """Print the final session cost."""
    _console.print()
    _console.print(Rule(style="dim"))
    t = Text()
    t.append("Session total: ", style="bold")
    t.append(f"${cost_usd:.4f}", style="bold green" if cost_usd < 0.50 else "bold yellow")
    _console.print(t)


# ---------------------------------------------------------------------------
# Greeting
# ---------------------------------------------------------------------------

_GREETING_BASE = """\
[bold cyan]EDSL Agent[/bold cyan] — build surveys, agents, and studies.

[dim]Examples:[/dim]
  "Create a survey about workplace satisfaction"
  "Build an agent list of customer personas"
  "Analyze results from a previous study"

[dim]Tips:[/dim]
  Reference files with [bold]@path/to/file[/bold]
  Type [bold]\\\\quit[/bold] to exit.\
"""


def print_greeting():
    """Print the startup greeting panel."""
    _console.print()
    _console.print(Panel(_GREETING_BASE, border_style="bright_blue", padding=(1, 2)))
    _console.print()


# ---------------------------------------------------------------------------
# Delegation banner
# ---------------------------------------------------------------------------

def print_delegation(agent_name: str = ""):
    """Print a sub-agent delegation notice."""
    label = f" to {agent_name}" if agent_name else ""
    _console.print(f"\n[dim blue]  >>> Delegating{label}...[/dim blue]")


# ---------------------------------------------------------------------------
# Session persistence
# ---------------------------------------------------------------------------

_SESSIONS_DIR = Path.home() / ".cache" / "ep-agent" / "sessions"
_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def save_session(result: dict, initial_prompt: str) -> str:
    """Save a completed session to disk. Returns the session ID."""
    session_id = uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc).isoformat()
    preview = initial_prompt[:120] if initial_prompt else ""

    data = {
        "id": session_id,
        "created_at": now,
        "initial_prompt": initial_prompt,
        "prompt_preview": preview,
        "total_cost_usd": result.get("total_cost_usd", 0.0),
        "turns": len([e for e in result.get("events", []) if e.get("kind") == "turn_start"]),
        "conversation": result.get("conversation", []),
        "events": result.get("events", []),
    }

    path = _SESSIONS_DIR / f"{session_id}.json"
    path.write_text(json.dumps(data, indent=2, default=str))
    _console.print(f"[dim]Session saved: {session_id}[/dim]")
    return session_id


def load_session(session_id: str) -> dict | None:
    """Load a session by ID (or prefix match)."""
    # Exact match
    path = _SESSIONS_DIR / f"{session_id}.json"
    if path.exists():
        return json.loads(path.read_text())

    # Prefix match
    matches = sorted(_SESSIONS_DIR.glob(f"{session_id}*.json"))
    if len(matches) == 1:
        return json.loads(matches[0].read_text())
    if len(matches) > 1:
        _console.print(f"[red]Ambiguous session ID '{session_id}' — matches {len(matches)} sessions.[/red]")
        return None

    _console.print(f"[red]Session '{session_id}' not found.[/red]")
    return None


def list_sessions(limit: int = 20):
    """Print a table of recent sessions."""
    files = sorted(_SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        _console.print("[dim]No saved sessions.[/dim]")
        return

    table = Table(title="Recent Sessions", border_style="dim")
    table.add_column("ID", style="bold cyan", no_wrap=True)
    table.add_column("Date", style="dim")
    table.add_column("Turns", justify="right")
    table.add_column("Cost", justify="right")
    table.add_column("Prompt", max_width=50)

    for f in files[:limit]:
        try:
            data = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        created = data.get("created_at", "")[:16].replace("T", " ")
        table.add_row(
            data.get("id", f.stem),
            created,
            str(data.get("turns", "?")),
            f"${data.get('total_cost_usd', 0):.2f}",
            data.get("prompt_preview", "")[:50],
        )

    _console.print()
    _console.print(table)
    _console.print()


def build_resume_context(session_data: dict) -> str:
    """Build a context preamble from a saved session for resuming."""
    parts = ["You are resuming a previous session. Here is what happened:\n"]

    for entry in session_data.get("conversation", []):
        role = entry.get("role", "unknown").upper()
        content = entry.get("content", "")
        if len(content) > 500:
            content = content[:500] + "... (truncated)"
        parts.append(f"[{role}]: {content}\n")

    cost = session_data.get("total_cost_usd", 0)
    parts.append(f"\n[Prior session cost: ${cost:.4f}]")
    parts.append("\nThe user wants to continue from here. ")
    return "\n".join(parts)
