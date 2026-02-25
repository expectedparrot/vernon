# EP-Agent

A multi-agent system built on the **Claude Agent SDK** (`claude-agent-sdk`) that orchestrates research studies using EDSL. We are actively developing and improving this agent system.

## Architecture

### Core Files

- **`agent.py`** — Main orchestrator. Sets up `ClaudeSDKClient`, defines hooks, manages the async conversation loop. This is the most important file.
- **`cli.py`** — Rich terminal UI layer (prompt_toolkit + rich). Renders markdown, manages session persistence to `~/.cache/ep-agent/sessions/`, handles `@file` reference expansion.
- **`driver.py`** — Non-interactive driver for automated runs. Has `ScriptedAnswerer`, `LLMAnswerer`, and `ComboAnswerer` classes for simulating user input.
- **`system_prompt.md`** — The system prompt injected into the main agent. Defines constraints and workflow.

### Agent System Design

The system uses a **main agent + sub-agents + skills** pattern:

**Main agent** (`agent.py`):
- Uses `ClaudeSDKClient` with `ClaudeAgentOptions`
- Tools: Read, Write, Edit, Glob, Bash, WebSearch, WebFetch, AskUserQuestion, Task
- Permission mode: `acceptEdits`
- Hooks: `PostToolUse` (error detection in Bash output) and `PostToolUseFailure` (always fires on tool failure)
- Both hooks inject an error-logging reminder into the conversation

**Sub-agents** (`sub-agents/`):
- `create-survey` — Survey design specialist
- `create-agent-list` — Agent persona builder
- `analyze-results` — Results analysis and visualization

Each sub-agent directory contains:
- `prompt.md` (required) — system prompt
- `description.md` (required) — one-line description for the main agent
- `tools.txt` (optional) — tool list override
- `model.txt` (optional) — model override (default: sonnet)

Sub-agents are auto-discovered by `_load_sub_agents()` and passed as `AgentDefinition` objects to the SDK.

**Skills** (`skills/`):
- Reusable knowledge modules, each a directory with `SKILL.md` + `description.md`
- Auto-catalogued by `_build_skills_catalog()` and appended to every sub-agent's prompt
- Agents read skills on demand via the Read tool

### Key Patterns

**Conversation loop** (`run_agent()` in agent.py):
1. Send prompt via `client.query()`
2. Stream responses via `async for msg in client.receive_response()`
3. Process `AssistantMessage` blocks (text, thinking, tool use, tool result)
4. If `AskUserQuestion` detected, break to collect answer, then loop
5. If no questions, prompt user for follow-up

**Planning phase** — Before any study work, the agent must create `plan.md` in the study root, present it to the user via `AskUserQuestion`, iterate on feedback, and only begin execution after the user approves.

**StatusLine** — Threaded spinner that updates in-place using `\r` + ANSI clear. Shows current tool activity without advancing the terminal.

**Error hooks** — `_looks_like_error()` pattern-matches tool output against `_ERROR_PATTERNS` list and injects a reminder to log errors to `errors.jsonl` before fixing them.

**Session persistence** — Conversations saved as JSON to `~/.cache/ep-agent/sessions/` with ID, cost, events, and conversation history. Supports resume via `--resume`.

## Running

```bash
python agent.py "prompt"                    # Interactive mode
python agent.py --resume <session-id>       # Resume prior session
python agent.py --sessions                  # List saved sessions
python driver.py --prompt "..." --persona "..."  # Automated driver
```

## Dependencies

- `claude-agent-sdk` — Agent orchestration (ClaudeSDKClient, AgentDefinition, HookMatcher, etc.)
- `edsl` — Domain-specific language for surveys/experiments (used by the agent, not by the framework)
- `rich` — Terminal rendering
- `prompt_toolkit` — Interactive input with history

## Sessions as Development Data

The `sessions/` directory contains **real runs of the agent** — complete study projects that the agent produced end-to-end. Each `sessions/topic_<name>/study_<letter>/` directory is the output of one agent session, including the files it created, errors it hit, and results it produced.

These sessions are our primary source of insight for improving the agent. When working on the agent system, inspect sessions to understand:
- Where the agent gets stuck or loops
- What kinds of errors recur (check `errors.jsonl` files)
- How well the agent follows its skills and constraints
- Whether the output quality (reports, analysis) meets expectations
- How the agent uses (or misuses) sub-agents and tools

## Development Notes

- The default model is `sonnet` (set in `_DEFAULT_MODEL`)
- Default tools for sub-agents: `_DEFAULT_TOOLS = ["Read", "Glob", "Bash", "WebSearch", "WebFetch", "Write", "Edit"]`
- Max turns: 25
- Max buffer size: 5MB
