---
name: study-checklist
description: Compliance checklist template for studies. All items must be checked with evidence before marking a study complete.
---

# Study Checklist

Every study gets a `checklist.md` in its root directory. Create it when you start the study. Work through it as you go. You may NOT output `[STUDY_COMPLETE]` until every item is checked with evidence.

## Creating the checklist

At study start, write this template to `checklist.md`:

```markdown
# Study Checklist

## Setup
- [ ] Study structure created via `create_study_project.py`
- [ ] `git init` done, initial commit made
- [ ] README.md has PURPOSE, Author, Timestamp

## Data Integrity
- [ ] All survey data comes from actual EDSL runs (no mock/fake/synthetic data)
      Evidence: <!-- e.g., data/results.json.gz, 312 rows, run at 2025-06-15T14:32Z -->
- [ ] Every number, table, and chart in the report traces to a file in `data/`
      Evidence: <!-- list the source files -->

## Analysis
- [ ] All analysis scripts live in `analysis/` and run via `make`
      Evidence: <!-- e.g., make PLOTS TABLES succeeds -->
- [ ] Plots written to `writeup/plots/`, tables to `writeup/tables/`

## Report
- [ ] `writeup/report.md` exists and is the single report file
- [ ] `check_writeup.py` passes
      Evidence: <!-- paste output -->
- [ ] PDF version exists
      Evidence: <!-- filename -->
- [ ] HTML version exists
      Evidence: <!-- filename -->

## Errors & Git
- [ ] `errors.jsonl` reviewed — all issues resolved or documented
      Evidence: <!-- e.g., 3 entries, all outcome: success -->
- [ ] All files committed, git status clean
      Evidence: <!-- e.g., git log --oneline -1 output -->
```

## Rules

1. **Create at study start.** The checklist is one of the first files you write, right after scaffolding.

2. **Update as you go.** Check items off when they're done, filling in the evidence comment. Don't batch all checks at the end.

3. **Evidence is mandatory.** Each checked item must have a concrete reference — a filename, row count, timestamp, command output, or similar. Never check a box without evidence.

4. **No mock data — ever.** If a survey hasn't been run, run it. If it failed, fix it and re-run. If cost is a concern, reduce agent or scenario count. A report built on made-up data is worse than no report at all.

5. **Completion gate.** Before outputting `[STUDY_COMPLETE]`, verify every box is checked. If any item is unchecked, finish it first.

6. **Add study-specific items.** If the study has unique requirements (e.g., subtree from a predecessor, specific computed objects), add checklist items for those.

## Final deliverables

A completed study must have all three:
- `writeup/report.md`
- PDF version of the report
- HTML version of the report

Only when all checklist items are checked AND all three deliverables exist, output `[STUDY_COMPLETE]`.
