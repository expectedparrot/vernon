---
name: study-file-organization
description: Directory structure, naming conventions, and git workflow for organizing studies.
---

# Study File Organization & Rules

Complete reference for how to organize files, directories, and git workflow when running studies.

## Directory Layout

All work lives in `sessions/`. Inside sessions, files are organized by **topic** (a general area of study). Each topic gets a directory with a descriptive alias derived from the user's request.

Example: "I want to study status quo bias among older people" → `topic_status-quo-bias-age`

If the directory already has topic folders, make sure your topic name is unique.

Within each topic, create one or more **studies** — self-contained collections of files that do something (create an agent list, run a simulation, etc.). Studies are named with snake-case post-fix indices: `_a`, `_b`, etc.

```
sessions/
  topic_<alias>/
    README.md
    .git
    study_a/
    study_b/
    study_c/
```

## Creating a Study

Use the `create_study_project.py` tool to scaffold the structure:

```bash
python create_study_project.py sessions/topic_<alias>/<study_name>
```

This produces:

```
.git
README.md
requirements.txt
Makefile
refs/
DOCKERFILE
data/
  raw/
    .gitkeep
  cooked/
    .gitkeep
  uploaded/
    .gitkeep
edsl_jobs/
  job_a/
    study_agent_list.py
    study_scenario_list.py
    study_model_list.py
    run_job.py
  job_b/
    …
analysis/
computed_objects/
writeup/
  planning.md
  report.md
  report.css
  appendix.md
  tables/
  plots/
  numbers/
```

## Report Formatting

**CSS**: Copy the Expected Parrot branded stylesheet into every study's writeup directory:

```bash
cp /Users/johnhorton/tools/ep/macaw/ep-agent/report.css <study_root>/writeup/report.css
```

The Makefile's `report.html` target must use `--css=report.css` to apply this stylesheet. Use this template for the report targets:

```makefile
# --- Report ---
writeup/report.html: writeup/report.md PLOTS TABLES
	cd writeup && pandoc report.md -o report.html --standalone --css=report.css

writeup/report.pdf: writeup/report.md PLOTS TABLES
	cd writeup && pandoc report.md -o report.pdf --pdf-engine=xelatex

report: writeup/report.html writeup/report.pdf
```

**No duplicate title**: The `report.md` file uses a YAML frontmatter block with `title:` and `date:`. Pandoc renders the `title` as an H1 heading automatically. Do NOT also include an `# H1` heading in the body — this causes the title to appear twice. Start the body with `## Summary` or another H2.

Correct format:
```markdown
---
title: "My Study Title"
date: 2026-01-15
---

## Summary

The body starts here with an H2...
```

Wrong format (title appears twice):
```markdown
---
title: "My Study Title"
date: 2026-01-15
---

# My Study Title

## Summary
...
```

## Rules

1. **Always create this file structure** for each study and do a `git init`. Also create `checklist.md` (see `skills/study-checklist/SKILL.md`).

2. **Use README.md as your lab notebook** — write what you did at each step:
   ```markdown
   PURPOSE
   Author
   Timestamp
   LOG Entries
   ```

3. **Git-add every new file** immediately after creating it.

4. **All file interactions are git-mediated.** At good stopping points, create a detailed git commit.

   **IMPORTANT**: The Makefile runs EDSL scripts from `edsl_jobs/` (`cd edsl_jobs && python ...`). All git commands must be run from the **study root** (the directory containing the Makefile). Always `cd` back to the study root and verify your working directory before any `git add` / `git commit`.

5. **Do not run Python files directly.** Write scripts into `analysis/` and wire them into the Makefile. Use `make` targets to execute them (e.g., `make plots`, `make writeup/report.html`). Analysis scripts create plots/tables written to `writeup/tables` or `writeup/plots`.

6. **Snake-case names for outputs.** Name scripts after what they produce:
   - `table_growth_over_time.py` → `writeup/tables/growth_over_time.csv`
   - `plot_growth_over_time.py` → `writeup/plots/growth_over_time.png`
   - Each has a corresponding Makefile recipe.

7. **PLOT and TABLES phony targets** in the Makefile are dependencies for the overall report.

8. **Follow-up studies use `git subtree`** to pull predecessors into `refs/`.

   **IMPORTANT: Both repos must have at least one commit before adding a subtree.**

   Step-by-step:
   1. Ensure the predecessor has at least one commit: `git -C <path_to_predecessor> log --oneline -1`
   2. Create the new study and make an initial commit
   3. From inside the new study's git repo:
      ```bash
      git subtree add --prefix=refs/<predecessor_study_name> <absolute_path_to_predecessor> main --squash
      ```
   4. Verify: `ls refs/<predecessor_study_name>/`
   5. If any step fails, log the error to `errors.jsonl` (see `skills/error-logging/SKILL.md`) immediately, then fix and retry

9. **Intermediate datasets** (transformed raw data, fitted models, etc.) go in `computed_objects/`.

10. **Add packages to `requirements.txt`** as needed.

11. **EDSL code goes in the `edsl_jobs/` directory.** Read `skills/edsl-study-files/SKILL.md` for the standard file templates and export conventions.

12. **User-uploaded data** goes in `data/uploads`. Data is also added to the repo unless too large.

13. **Use the SearchExpectedParrot tool** to search Expected Parrot for EDSL objects. Use it directly instead of writing Python scripts with `Coop().list()`.

14. **Single report file rule**: Only ONE report markdown in `writeup/` — that is `report.md`. To elaborate on results or extend the report, edit `report.md` rather than creating new files. Allowed `.md` files in `writeup/`: `report.md`, `survey.md` (auto-generated), `planning.md` (working notes), `appendix.md` (supplementary material). After any analysis run, run `python check_writeup.py <study_dir>` to verify compliance.
