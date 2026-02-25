---
name: error-review
description: "Developer tool: find the most recent errors.jsonl from an agent run, diagnose root causes, and interactively patch the agent's instruction files to prevent recurrence."
---

# Error Review & Agent Improvement

This is a **developer-facing skill**. The developer invokes this to review errors from a recent agent run and fix the agent's own instruction files (system_prompt.md, sub-agent prompts, skill files) so the agent stops making the same mistakes.

The errors.jsonl files are produced by the agent during study runs. Each error represents a place where the agent hit a wall — wrong API, bad path, broken assumption. The goal here is to trace each error back to whichever instruction file misled the agent (or failed to guide it), and patch that file.

## Workflow

### 1. Find the most recent errors.jsonl

```bash
find . -name 'errors.jsonl' -print0 | xargs -0 ls -t | head -1
```

If no file is found, say so and stop.

### 2. Read and parse

Read the entire file. Each line is a JSON object with: `timestamp`, `summary`, `error`, `context`, `command`, `output`, `fix_attempted`, `outcome`.

### 3. Categorize by root cause

For each error, determine: **what instruction file should have prevented this?**

| Category | Pattern | Likely fix target |
|----------|---------|-------------------|
| **working-directory** | `cd` with relative path, wrong cwd | `system_prompt.md` — needs absolute-path rule |
| **edsl-api-misuse** | Wrong method, bad args, empty collection passed | `skills/*.md` — wrong or missing API reference |
| **file-format** | Wrong extension, bad serialization | `skills/*.md` or `sub-agents/*.md` — template code is wrong |
| **missing-file** | File not where expected after creation | `skills/study-file-organization/SKILL.md` or `system_prompt.md` |
| **latex-unicode** | Emoji/unicode breaks PDF generation | `system_prompt.md` — needs no-emoji rule for reports |
| **script-path** | Python script run from wrong directory | `skills/study-file-organization/SKILL.md` or Makefile template |
| **other** | Doesn't fit above | Determine the right file |

### 4. Present the diagnosis

Show a table summarizing all errors, grouped by fix target:

```
## Error Review: <path_to_errors.jsonl>

N errors found. Root causes trace to M instruction files.

| # | Category | Error summary | Instruction file to fix |
|---|----------|---------------|------------------------|
| 1 | working-directory | cd relative path failed (x6) | system_prompt.md |
| 2 | edsl-api-misuse | Results.from_file doesn't exist | skills/edsl-study-files/SKILL.md |
| ... | ... | ... | ... |

### Proposed patches
1. **system_prompt.md** — Add: "Always use absolute paths..."
2. **skills/edsl-study-files/SKILL.md** — Fix: Results.from_file → Results.load
```

### 5. Apply fixes interactively

For each proposed patch:
1. Read the target instruction file
2. Show the developer the exact edit (old text → new text)
3. Wait for approval
4. Apply the edit
5. Move to the next

### 6. Rules

- **Read before editing.** Always read the target file first.
- **Minimal patches.** Add the smallest rule/note/fix that prevents the error class. Don't rewrite files.
- **Don't duplicate.** If the guidance already exists, skip it and note that.
- **Preserve style.** Match the existing formatting and voice of each file.
- **One patch at a time.** Get approval before each edit.
- **Check for contradictions.** If a new rule would conflict with an existing one, flag it.
- **Summarize at the end.** List all files changed and what was added/fixed.

## Common patches

### Working directory → system_prompt.md

Under "Critical constraints", add:
```markdown
- **Use absolute paths in all Bash commands.** Never use `cd` with relative paths — the Bash tool does not preserve working directory between calls. Always construct paths from the known study root (e.g., `$STUDY_ROOT/writeup/report.md`). When you create a study, store its absolute path and use it for all subsequent commands.
```

### EDSL API misuse → relevant skill file

Read the actual edsl source or docs, then fix the skill. Common ones:
- `Results.from_file()` and `Results.from_disk()` do not exist → correct method is `Results.load("path.json.gz")`
- Empty `ScenarioList` causes `IndexError` → add to `create_results.py` template: guard with `if len(scenario_list) > 0` before chaining `.by(scenario_list)`
- `Results.load` needs the full filename including `.json.gz` extension

### LaTeX/emoji → system_prompt.md

Add under "Communication style" or a "Report generation" section:
```markdown
- **No emoji in reports.** `writeup/report.md` is compiled to PDF via LaTeX. Emoji and non-standard Unicode cause compilation failures. Use plain text only. If using xelatex, note this in the Makefile.
```

### Script path errors → study-file-organization/SKILL.md

Ensure templates use `Path(__file__).resolve().parent` for path resolution, and that the Makefile `cd`s into the right directory before running scripts.
