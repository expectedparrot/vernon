---
name: error-logging
description: Error logging protocol using append-only JSONL format (errors.jsonl).
---

# Error Logging

All errors, unexpected results, and surprises must be logged to `errors.jsonl` in the study root (never in a subdirectory like `writeup/`). The file is **append-only JSONL** — one JSON object per line.

## When to log

Log **before** attempting any fix whenever you encounter:

- A command that exits with a non-zero exit code
- A Python traceback or exception
- A file, directory, or output that is missing or empty when expected
- Output that doesn't match expectations (wrong location, content, or format)
- Having to retry something or "check where it actually went"
- Running something from the wrong directory
- Any behavior that surprises you

**The sequence is always: (1) log the error, (2) then fix it. Never fix first.**

## JSONL format

Append exactly one JSON object per error. Every line must be valid JSON.

```json
{"timestamp": "2025-06-15T14:32:00Z", "summary": "Short description", "error": "exact error message or description", "context": "what you were doing", "command": "the exact command or code that failed — verbatim", "output": "the complete traceback or unexpected output — verbatim, never summarize", "fix_attempted": "what you tried", "outcome": "success or failure — update after fix"}
```

### Required fields

| Field | Description |
|-------|-------------|
| `timestamp` | ISO-8601 UTC timestamp |
| `summary` | Brief one-line description |
| `error` | The exact error message |
| `context` | What you were trying to do |
| `command` | The verbatim command or code that failed |
| `output` | The complete raw traceback / stderr — never paraphrase or abbreviate |
| `fix_attempted` | What you did to fix it |
| `outcome` | `"success"` or `"failure"` — update after attempting the fix |

### How to append

Use a single echo/printf to append one line:

```bash
echo '{"timestamp":"2025-06-15T14:32:00Z","summary":"ModuleNotFoundError for pandas","error":"ModuleNotFoundError: No module named '\''pandas'\''","context":"Running make data","command":"cd edsl_jobs && python create_results.py","output":"Traceback (most recent call last):\n  File \"create_results.py\", line 2\n    import pandas\nModuleNotFoundError: No module named '\''pandas'\''","fix_attempted":"pip install pandas","outcome":"success"}' >> errors.jsonl
```

Or use Python for complex output with special characters:

```python
import json, datetime
entry = {
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "summary": "Short description",
    "error": "...",
    "context": "...",
    "command": "...",
    "output": "...",  # paste the full traceback here
    "fix_attempted": "...",
    "outcome": "pending"
}
with open("errors.jsonl", "a") as f:
    f.write(json.dumps(entry) + "\n")
```

## End-of-study review

Before finishing a study, read `errors.jsonl` and confirm all encountered issues are captured. Check that every entry has a final `outcome` of `"success"` or document why it remains unresolved.
