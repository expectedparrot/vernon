#!/usr/bin/env python3
"""Driver script for agent.py — simulates a user with pre-scripted and/or LLM-generated answers."""

import argparse
import asyncio
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

from agent import run_agent


# ---------------------------------------------------------------------------
# Answer strategies
# ---------------------------------------------------------------------------

class ScriptedAnswerer:
    """Return pre-defined answers, one per question round.

    If the agent asks more rounds of questions than answers were provided,
    raises ``StopIteration`` (which the combo answerer catches).
    """

    def __init__(self, answers: list[str]):
        self._answers = list(answers)
        self._idx = 0

    @property
    def exhausted(self) -> bool:
        return self._idx >= len(self._answers)

    def __call__(self, questions: list[dict]) -> list[str]:
        if self.exhausted:
            raise StopIteration("No more scripted answers available")
        # Use one scripted answer for the whole round (all questions get the same answer).
        # If there are multiple questions in one round, split on ';' if possible.
        answer = self._answers[self._idx]
        self._idx += 1
        parts = [a.strip() for a in answer.split(";")] if ";" in answer else [answer]
        # Pad or truncate to match number of questions
        while len(parts) < len(questions):
            parts.append(parts[-1] if parts else "")
        return parts[: len(questions)]


class LLMAnswerer:
    """Use the ``claude`` CLI to generate plausible user answers given a persona."""

    def __init__(self, persona: str, model: str = "sonnet"):
        self._persona = persona
        self._model = model
        self._history: list[dict] = []  # track Q&A for context

    def __call__(self, questions: list[dict]) -> list[str]:
        formatted = self._format_questions(questions)
        self._history.append({"role": "questions", "content": formatted})

        history_ctx = ""
        if len(self._history) > 1:
            history_ctx = "\nPrevious Q&A rounds:\n"
            for i, entry in enumerate(self._history[:-1]):
                history_ctx += f"  Round {i + 1}: {entry['content']}\n"
                if "answers" in entry:
                    history_ctx += f"  Your answers: {entry['answers']}\n"

        prompt = (
            f"You are role-playing as a user with the following persona:\n\n"
            f"{self._persona}\n\n"
            f"The assistant is asking you questions to understand your requirements. "
            f"Answer each question concisely and naturally, staying in character. "
            f"Return ONLY a JSON array of strings, one answer per question. "
            f"Do not include any other text.\n\n"
            f"{history_ctx}\n"
            f"Now answer these questions:\n\n{formatted}\n\n"
            f"Respond with a JSON array of {len(questions)} answer string(s)."
        )

        result = subprocess.run(
            ["claude", "-p", "--model", self._model, "--output-format", "text"],
            input=prompt,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"  [LLM answerer] claude CLI error: {result.stderr.strip()}", file=sys.stderr)
            # Fall back to a generic answer
            answers = ["yes"] * len(questions)
            print(f"  [LLM answerer] falling back to: {answers}")
            return answers

        raw = result.stdout.strip()
        # Extract JSON array from the response
        try:
            answers = json.loads(raw)
            if not isinstance(answers, list):
                answers = [str(answers)]
        except json.JSONDecodeError:
            # Try to find a JSON array embedded in the text
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                try:
                    answers = json.loads(match.group())
                    if not isinstance(answers, list):
                        answers = [str(answers)]
                except json.JSONDecodeError:
                    answers = [raw]
            else:
                answers = [raw]

        # Pad or truncate
        while len(answers) < len(questions):
            answers.append(answers[-1] if answers else "")
        answers = answers[: len(questions)]

        # Record for future context
        self._history[-1]["answers"] = answers
        answers = [str(a) for a in answers]

        print(f"  [LLM answerer] {answers}")
        return answers

    @staticmethod
    def _format_questions(questions: list[dict]) -> str:
        parts = []
        for i, q in enumerate(questions, 1):
            text = q.get("question", "")
            options = q.get("options", [])
            header = q.get("header", "")
            line = f"Q{i}"
            if header:
                line += f" [{header}]"
            line += f": {text}"
            if options:
                for j, opt in enumerate(options, 1):
                    label = opt.get("label", "")
                    desc = opt.get("description", "")
                    line += f"\n    {j}. {label}" + (f" — {desc}" if desc else "")
            parts.append(line)
        return "\n".join(parts)


class ComboAnswerer:
    """Use scripted answers first; fall back to LLM when they run out."""

    def __init__(self, scripted: ScriptedAnswerer, llm: LLMAnswerer):
        self._scripted = scripted
        self._llm = llm

    def __call__(self, questions: list[dict]) -> list[str]:
        if not self._scripted.exhausted:
            try:
                answers = self._scripted(questions)
                print(f"  [Scripted answerer] {answers}")
                return answers
            except StopIteration:
                pass
        return self._llm(questions)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Drive agent.py non-interactively with scripted and/or LLM-generated answers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  # Pre-scripted answers only
  python driver.py --prompt "Create a survey about cats" \\
    --answers "pet owners" "5 questions" "multiple choice"

  # LLM-generated answers with a persona
  python driver.py --prompt "Create a survey about cats" \\
    --persona "A marketing researcher interested in cat food preferences"

  # Combo: scripted first, LLM fallback
  python driver.py --prompt "Create a survey about cats" \\
    --answers "pet owners" "5 questions" \\
    --persona "A marketing researcher"

  # Save conversation log to JSON
  python driver.py --prompt "Create a survey" --persona "A researcher" --output run.json
""",
    )
    p.add_argument(
        "--prompt", required=True, help="Initial prompt / task description for the agent."
    )
    p.add_argument(
        "--answers",
        nargs="+",
        default=[],
        help="Pre-scripted answers, one per question round. Separate multiple answers within a round with semicolons.",
    )
    p.add_argument(
        "--persona",
        default=None,
        help="Persona description for LLM-generated answers. Required if --answers is not provided or may not cover all rounds.",
    )
    p.add_argument(
        "--output", "-o", default=None, help="Optional path to write the conversation log as JSON."
    )
    return p


def _print_summary(result: dict) -> None:
    """Print a human-readable summary of the run from the events log."""
    events = result.get("events", [])
    if not events:
        return

    print("\n" + "=" * 60)
    print("TRANSCRIPT SUMMARY")
    print("=" * 60)

    for ev in events:
        ts = ev["ts"]
        kind = ev["kind"]
        # Short timestamp (HH:MM:SS.mmm)
        try:
            t = datetime.fromisoformat(ts)
            short_ts = t.strftime("%H:%M:%S.") + f"{t.microsecond // 1000:03d}"
        except ValueError:
            short_ts = ts

        if kind == "turn_start":
            turn = ev["turn"]
            prompt_preview = ev["prompt"][:200].replace("\n", " ")
            print(f"\n[{short_ts}] --- Turn {turn} ---")
            print(f"  Prompt: {prompt_preview}{'...' if len(ev['prompt']) > 200 else ''}")
            print(f"  Prompt length: {len(ev['prompt'])} chars")
            print(f"  System prompt length: {len(ev.get('system_prompt', ''))} chars")

        elif kind == "assistant_text":
            text_preview = ev["text"][:300].replace("\n", " ")
            model = ev.get("model", "?")
            print(f"[{short_ts}]   Assistant ({model}): {text_preview}{'...' if len(ev['text']) > 300 else ''}")

        elif kind == "thinking":
            text_preview = ev["text"][:150].replace("\n", " ")
            print(f"[{short_ts}]   Thinking: {text_preview}{'...' if len(ev['text']) > 150 else ''}")

        elif kind == "tool_use":
            tool = ev["tool_name"]
            inp = ev.get("tool_input", {})
            # Compact display of tool input
            if tool == "Task":
                desc = inp.get("description", "")[:200]
                print(f"[{short_ts}]   Tool: {tool} -> {inp.get('agent', '?')}")
                print(f"             desc: {desc}{'...' if len(inp.get('description', '')) > 200 else ''}")
            elif tool == "AskUserQuestion":
                qs = inp.get("questions", [])
                print(f"[{short_ts}]   Tool: {tool} ({len(qs)} question(s))")
                for q in qs:
                    print(f"             Q: {q.get('question', '')[:150]}")
            else:
                inp_str = json.dumps(inp, ensure_ascii=False)
                if len(inp_str) > 200:
                    inp_str = inp_str[:200] + "..."
                print(f"[{short_ts}]   Tool: {tool}  input={inp_str}")

        elif kind == "tool_result":
            is_err = ev.get("is_error")
            content = ev.get("content", "")
            if isinstance(content, str):
                preview = content[:200].replace("\n", " ")
            else:
                preview = str(content)[:200]
            status = "ERROR" if is_err else "ok"
            print(f"[{short_ts}]   Tool result ({status}): {preview}{'...' if len(str(content)) > 200 else ''}")

        elif kind == "user_answer":
            answers = ev.get("answers", [])
            print(f"[{short_ts}]   User answered: {answers}")

        elif kind == "system_message":
            print(f"[{short_ts}]   System [{ev.get('subtype', '?')}]")

        elif kind == "result":
            cost = ev.get("total_cost_usd")
            usage = ev.get("usage") or {}
            dur = ev.get("duration_ms", 0)
            dur_api = ev.get("duration_api_ms", 0)
            turns = ev.get("num_turns", 0)
            session = ev.get("session_id", "?")

            print(f"\n[{short_ts}]   Result (session {session[:12]}...):")
            print(f"             Turns: {turns}")
            print(f"             Duration: {dur / 1000:.1f}s total, {dur_api / 1000:.1f}s API")
            if cost is not None:
                print(f"             Cost: ${cost:.4f}")
            if usage:
                inp_tok = usage.get("input_tokens") or usage.get("input", 0)
                out_tok = usage.get("output_tokens") or usage.get("output", 0)
                cache_read = usage.get("cache_read_input_tokens", 0)
                cache_create = usage.get("cache_creation_input_tokens", 0)
                print(f"             Tokens: {inp_tok} in / {out_tok} out")
                if cache_read or cache_create:
                    print(f"             Cache: {cache_read} read / {cache_create} created")
                # Print any other usage keys for visibility
                known = {"input_tokens", "output_tokens", "input", "output",
                         "cache_read_input_tokens", "cache_creation_input_tokens"}
                extra = {k: v for k, v in usage.items() if k not in known and v}
                if extra:
                    print(f"             Other usage: {extra}")

    print("\n" + "=" * 60)


async def run(args: argparse.Namespace) -> None:
    # Build the answer function
    scripted = ScriptedAnswerer(args.answers) if args.answers else None
    llm = LLMAnswerer(args.persona) if args.persona else None

    if scripted and llm:
        answer_fn = ComboAnswerer(scripted, llm)
    elif scripted:
        answer_fn = scripted
    elif llm:
        answer_fn = llm
    else:
        print("Error: provide --answers and/or --persona so the driver can answer questions.", file=sys.stderr)
        sys.exit(1)

    print(f"=== Driver starting ===")
    print(f"Prompt : {args.prompt}")
    if args.answers:
        print(f"Scripted answers: {args.answers}")
    if args.persona:
        print(f"Persona: {args.persona}")
    print()

    result = await run_agent(args.prompt, answer_fn=answer_fn)

    # Print detailed transcript summary
    _print_summary(result)

    print(f"\n=== Driver finished ===")
    print(f"Total cost: ${result['total_cost_usd']:.4f}")
    print(f"Conversation turns: {len(result['conversation'])}")
    print(f"Events recorded: {len(result.get('events', []))}")

    if args.output:
        log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt": args.prompt,
            "answers": args.answers,
            "persona": args.persona,
            **result,
        }
        with open(args.output, "w") as f:
            json.dump(log, f, indent=2)
        print(f"Log saved to {args.output}")


def main():
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
