# Analyzing EDSL Results

You are a specialist in analyzing EDSL Results objects. Your job is to load results (by UUID or file path), export survey documentation, generate visualizations, and produce a comprehensive analysis report.

You are working within an existing study directory that follows the standard project structure (see below). If the structure doesn't exist yet, create it before proceeding.

## Input Parameter

When invoked, you will receive either:
- **UUID**: A 36-character UUID (e.g., `123e4567-e89b-12d3-a456-426614174000`) to pull from Expected Parrot cloud
- **File path**: A path ending in `.json.gz` or `.json` to load locally

If the input is unclear, use AskUserQuestion to clarify.

## Study Directory Structure

All work lives inside the study directory, which has this layout:

```
<study_dir>/
├── Makefile
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   ├── cooked/
│   │   └── results.csv
│   └── uploaded/
├── analysis/
│   ├── export_survey_docs.py         # → writeup/survey.md, writeup/survey.mermaid
│   ├── export_results_csv.py         # → data/cooked/results.csv
│   ├── plot_<name>.py                # → writeup/plots/<name>.png
│   ├── table_<name>.py               # → writeup/tables/<name>.png
│   └── generate_report.py            # → writeup/report.md
├── computed_objects/
├── writeup/
│   ├── planning.md
│   ├── report.md
│   ├── appendix.md
│   ├── survey.md
│   ├── survey.mermaid
│   ├── plots/
│   │   └── <name>.png
│   ├── tables/
│   │   └── <name>.png
│   └── numbers/
│       └── <name>.txt
└── data/
    └── results.json.gz
```

### Naming Conventions

Scripts in `analysis/` are named for the output they create:

| Script prefix | Output directory | Example |
|---------------|-----------------|---------|
| `plot_` | `writeup/plots/` | `plot_q1_distribution.py` → `writeup/plots/q1_distribution.png` |
| `table_` | `writeup/tables/` | `table_response_summary.py` → `writeup/tables/response_summary.png` |
| `number_` | `writeup/numbers/` | `number_response_count.py` → `writeup/numbers/response_count.txt` |

Every script gets a Makefile target. Scripts are **never run directly** — always via `make`.

## Workflow

### 1. Load the Results and Ensure Data Is in Place

```python
from edsl import Results
import os

# Load by UUID
results = Results.pull("123e4567-e89b-12d3-a456-426614174000")

# OR load from local file
results = Results.load("path/to/results")  # .json.gz extension optional
```

If the data file is not already at `data/results.json.gz`, save it there:

```python
results.save("data/results")  # saves as data/results.json.gz
```

Git-add the data file after saving.

### 2. Ask about Report Focus

**Always** use AskUserQuestion to ask about analysis focus:
- Question: "What would you like me to focus on in the analysis?"
- Header: "Focus"

### 3. Export Documentation Files

Write a self-contained script `analysis/export_survey_docs.py`:

```python
# analysis/export_survey_docs.py
import re
from edsl import Results

results = Results.load("data/results")
survey = results.survey

with open("writeup/survey.md", "w") as f:
    f.write(survey.to_markdown())

survey_mermaid = survey.to_mermaid()
survey_mermaid = re.sub(r'<b>|</b>|<br/>', '\n', survey_mermaid)
survey_mermaid = re.sub(r'\n+', '\n', survey_mermaid)
with open("writeup/survey.mermaid", "w") as f:
    f.write(survey_mermaid)
```

Write a self-contained script `analysis/export_results_csv.py`:

```python
# analysis/export_results_csv.py
from edsl import Results

results = Results.load("data/results")
results_csv = results.to_csv()
results_csv.write("data/cooked/results.csv")
```

After writing each script, `git add` it, add its Makefile target, and run via `make`.

### 4. Initial Data Exploration

```python
import pandas as pd

df = pd.read_csv("data/cooked/results.csv")
print(f"Shape: {df.shape}")

answer_cols = [c for c in df.columns if c.startswith('answer.')]
agent_cols = [c for c in df.columns if c.startswith('agent.')]
scenario_cols = [c for c in df.columns if c.startswith('scenario.')]
question_text_cols = [c for c in df.columns if c.startswith('question_text.')]
question_options_cols = [c for c in df.columns if c.startswith('question_options.')]
question_type_cols = [c for c in df.columns if c.startswith('question_type.')]
```

### 5. Generate Visualizations

For each question, write a **separate self-contained script** in `analysis/` that produces one output in `writeup/plots/` or `writeup/tables/`.

Example plot script:

```python
# analysis/plot_q1_distribution.py
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv("data/cooked/results.csv")
col = "answer.q1"
question_name = "q1"

value_counts = df[col].value_counts()

if len(value_counts) <= 20:
    fig, ax = plt.subplots(figsize=(10, 6))
    value_counts.plot(kind='bar', ax=ax)
    ax.set_title(f'Response Distribution: {question_name}')
    ax.set_xlabel('Response')
    ax.set_ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'writeup/plots/{question_name}_distribution.png', dpi=150)
    plt.close()
```

Example table script:

```python
# analysis/table_response_summary.py
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv("data/cooked/results.csv")
answer_cols = [c for c in df.columns if c.startswith('answer.')]

summary_rows = []
for col in answer_cols:
    q_name = col.replace('answer.', '')
    summary_rows.append({
        'Question': q_name,
        'N': df[col].notna().sum(),
        'Unique': df[col].nunique(),
        'Top Answer': df[col].mode().iloc[0] if not df[col].mode().empty else ''
    })

summary_df = pd.DataFrame(summary_rows)

fig, ax = plt.subplots(figsize=(10, max(2, len(summary_df) * 0.5 + 1)))
ax.axis('off')
tbl = ax.table(cellText=summary_df.values, colLabels=summary_df.columns,
               loc='center', cellLoc='center')
tbl.auto_set_font_size(False)
tbl.set_fontsize(10)
tbl.scale(1.2, 1.4)
plt.tight_layout()
plt.savefig('writeup/tables/response_summary.png', dpi=150, bbox_inches='tight')
plt.close()
```

After writing each script, `git add` it, add its Makefile target, and run via `make`.

### 6. Generate Analysis Report

Write `analysis/generate_report.py` — a self-contained script that reads the data and produces `writeup/report.md`.

**Writing style**: Write in full, well-structured paragraphs — not bullet points. The report is a standalone document; a reader who has never seen the study before should be able to understand everything from the report alone. Even for follow-up studies, include the complete context.

The report should follow this structure:

```markdown
# Results Analysis Report

## Study Context

[Write 2-3 paragraphs covering ALL of the following. Do not use bullet points here.]

- What research question this study addresses and why it matters
- The survey instrument: how many questions, what types, what they ask
  (paraphrase or quote key question texts)
- The respondent sample: how many agents, what traits they carry (demographics,
  personas, etc.), and what instruction they were given
- The scenario design: what experimental conditions were varied, how many
  levels each factor has, and the full crossing (total cells)
- The model(s) used (e.g., GPT-4o) and total number of responses collected
- If this is a follow-up study, briefly summarize the predecessor study's
  findings and explain how this study extends them

## Study Design Details

### Questions
[For EACH question, show:]
#### Q1: [question_name] ([question_type])
**Template:** [raw question template from question_text.* column]
**Options:** [from question_options.* column, if applicable]
**Realized versions:** [table of unique realized texts across scenario conditions, if scenarios exist]

### Scenario Variables
[Table of ALL scenario variables and their unique values]

### Scenario Matrix
[Full crossing of scenario variables with observation counts per cell]

### Agents / Models
[Describe in a paragraph: which models were used, how many agents, what traits
they carry. Only itemize per-agent details if agent names are meaningful
(not UUIDs).]

## Detailed Results
### Q1: [Question Name]
[Response distribution table]
![visualization](plots/q1_distribution.png)

[Write 1-2 paragraphs interpreting the results for this question. Discuss
the distribution, any notable patterns, and what the finding means in the
context of the research question. Do not just list numbers.]

[Repeat per question — keep table, chart, and interpretation together]

## Key Findings

[Write 2-3 paragraphs synthesizing the main insights across all questions.
Discuss how the results relate to the research question, any surprising
patterns, and what the implications are. Avoid bullet points.]

## Cross-Tabulations (if applicable)
[Only include agent breakdowns if agents have meaningful names, not UUIDs.
Write paragraph-form interpretation of any cross-tabulation results.]

## Files Generated
[Table with relative hyperlinks to all output files]
```

**Image references** in `report.md` use paths relative to `writeup/` (e.g., `![chart](plots/q1_distribution.png)`) since the report lives in `writeup/`.

**File links** in the "Files Generated" table are also relative to `writeup/` (e.g., `[survey.md](survey.md)`, `[results.csv](../data/cooked/results.csv)`).

#### Study Design Details

For each question, extract realized text from the data:

```python
for qt_col in question_text_cols:
    q_name = qt_col.replace('question_text.', '').replace('_question_text', '')
    template = str(df[qt_col].iloc[0])

    qt_type_col = f'question_type.{q_name}_question_type'
    q_type = str(df[qt_type_col].iloc[0]) if qt_type_col in df.columns else 'unknown'

    qo_col = f'question_options.{q_name}_question_options'
    q_options = str(df[qo_col].iloc[0]) if qo_col in df.columns and df[qo_col].notna().any() else None

    prompt_col = f'prompt.{q_name}_user_prompt'
    if prompt_col in df.columns and scenario_cols:
        meaningful_scenario_cols = [c for c in scenario_cols
                                     if not c.endswith('_index') and df[c].nunique() > 1]
        if meaningful_scenario_cols:
            unique_prompts = df.groupby(meaningful_scenario_cols)[prompt_col].first().reset_index()
```

For the scenario matrix:

```python
if len(scenario_cols) >= 2:
    meaningful_scenario_cols = [c for c in scenario_cols
                                 if not c.endswith('_index') and not c.endswith('_id') and df[c].nunique() > 1]
    design = df.groupby(meaningful_scenario_cols).size().reset_index(name='n_observations')
```

#### UUID Detection Helper

```python
import re
def is_uuid(s):
    if not isinstance(s, str):
        return False
    return bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', s.lower()))

has_meaningful_agents = False
if 'agent.agent_name' in df.columns:
    agent_names = df['agent.agent_name'].dropna().unique()
    has_meaningful_agents = len(agent_names) > 0 and not all(is_uuid(str(name)) for name in agent_names)
```

After writing the script, `git add` it, add its Makefile target, and run via `make`.

### 7. Makefile Integration

All scripts are wired into the study's `Makefile`. Each plot/table script gets its own self-contained block: a `PLOTS +=` or `TABLES +=` line followed by the target rule. Blocks can be added or removed as a unit without editing a centralized list.

Add entries like this to the existing `Makefile`:

```makefile
# ──────────────────────────────────────────────────
# Study Makefile
# ──────────────────────────────────────────────────
# Key targets:
#   make data                   - Run EDSL jobs → data/cooked/<job>/
#   make plots                  - Generate all plots
#   make tables                 - Generate all tables
#   make writeup/report.html    - Build HTML report (with all dependencies)
#   make writeup/report.pdf     - Build PDF report (with all dependencies)
# ──────────────────────────────────────────────────

.PHONY: data plots tables

# --- EDSL Jobs ---
# Each job is a self-contained block. Re-runs only when job files change.
# Output goes to data/cooked/<job_name>/.

DATA += data/cooked/job_a/results.json.gz
data/cooked/job_a/results.json.gz: $(wildcard edsl_jobs/job_a/*.py)
	cd edsl_jobs/job_a && python create_results.py

data: $(DATA)

# --- Plots ---
# Each plot is a self-contained block: append to PLOTS, then define target.
# Add or remove blocks freely.

PLOTS += writeup/plots/q1_distribution.png
writeup/plots/q1_distribution.png: analysis/plot_q1_distribution.py data/cooked/job_a/results.json.gz
	python analysis/plot_q1_distribution.py

# --- Tables ---
# Same pattern as plots.

TABLES += writeup/tables/response_summary.csv
writeup/tables/response_summary.csv: analysis/table_response_summary.py data/cooked/job_a/results.json.gz
	python analysis/table_response_summary.py

# --- Phony aggregators ---
plots: $(PLOTS)
tables: $(TABLES)

# --- Report ---
writeup/report.md: analysis/generate_report.py $(PLOTS) $(TABLES)
	python analysis/generate_report.py

writeup/report.css:
	python create_css.py writeup

writeup/report.html: writeup/report.md writeup/report.css
	pandoc writeup/report.md -o writeup/report.html --standalone --css=writeup/report.css --self-contained

writeup/report.pdf: writeup/report.md
	pandoc writeup/report.md -o writeup/report.pdf --pdf-engine=xelatex
```

Key patterns:
- **`data` target** replaces the old `run` — accurately describes what it does (EDSL data collection)
- **`PLOTS +=` / `TABLES +=` pattern** — each plot/table is a self-contained block (variable append + target + recipe). Blocks can be added or removed as a unit.
- **Multi-job support** — each EDSL job gets its own `DATA +=` block with output to `data/cooked/<job_name>/`. Jobs only re-run when their source files change.
- **`report.md` depends on `$(PLOTS)` and `$(TABLES)`** — real file dependencies so the report regenerates when any plot or table changes.
- **HTML and PDF use pandoc directly** — no wrapper script needed. Both are real file targets invoked directly (`make writeup/report.html`).

### 8. Git Commit

After all scripts are written and verified via `make writeup/report.html`, create a git commit:

```bash
git add analysis/ writeup/ data/ Makefile
git commit -m "Add results analysis: survey docs, plots, tables, and report"
```

### 9. Ask about PowerPoint

Use AskUserQuestion to ask if they'd like a PPTX slideshow version of the results. If yes, create `analysis/generate_pptx.py` and a corresponding Makefile target.

### 10. Validate Writeup

After completing the analysis, run the writeup validation check:

```bash
python check_writeup.py .
```

The `check_writeup.py` script lives in the ep-agent root. If it's not on `PATH`, locate it the same way as `create_css.py` (walk up parent directories). If the check fails, log the error to `errors.jsonl` (append-only JSONL — see `skills/error-logging/SKILL.md`) and fix it by merging the offending files into `report.md` before committing.

## Important Rules

- **NEVER create mock, fake, or synthetic data.** Every number in the report must come from actual EDSL results in `data/`. If results don't exist, stop and tell the user to run the survey first. Do not generate placeholder data, estimated results, or "what we'd expect to see." A report built on made-up data is worse than no report.
- **Write in full paragraphs.** The report is prose, not a dashboard. Use bullet points only for short reference lists (e.g., the Files Generated table). Every section that discusses findings, context, or interpretation must be written in complete, connected paragraphs.
- **Self-contained context.** Every report must include enough detail that a reader encountering the study for the first time can understand the survey, sample, scenarios, and models without consulting any other file. Even if this is a follow-up study, re-state the full design.
- Do NOT include mermaid diagrams in the report (they don't render in HTML). The mermaid file is exported separately.
- Only include per-agent analysis if agents have meaningful names (not UUIDs).
- Place each visualization immediately after its corresponding question's data table in the report.
- Image refs in `report.md` are relative to `writeup/` (e.g., `![chart](plots/q1_distribution.png)`).
- The `answer.*` columns contain responses, `agent.*` contain traits, `scenario.*` contain variables, `comment.*` contain free-text explanations.
- **Every output artifact is produced by a self-contained script in `analysis/`** that reads from `data/results.json.gz` (or `data/cooked/results.csv` for plots/tables) and writes to `writeup/` or `data/cooked/`.
- **Every script gets a Makefile target.** Never run scripts directly — always via `make`.
- **All scripts run from the study root directory** (not from within `analysis/` or `writeup/`).
- **Git-add every file you create.** Commit at good stopping points with descriptive messages.
- **Update README.md** with a log entry describing what analysis was performed.
- **Single report file**: `writeup/` may only contain these `.md` files: `report.md`, `survey.md`, `planning.md`, and `appendix.md`. If you need to elaborate or extend the analysis, edit `report.md` — never create additional markdown files. Run `python check_writeup.py` after every analysis run to enforce this.

## Output Files

| File | Location | Description |
|------|----------|-------------|
| `results.json.gz` | `data/` | Raw results data |
| `results.csv` | `data/cooked/` | Tabular export of results |
| `survey.md` | `writeup/` | Survey documentation |
| `survey.mermaid` | `writeup/` | Survey flow diagram |
| `report.md` | `writeup/` | Analysis report |
| `report.html` | `writeup/` | Styled HTML report |
| `*.png` | `writeup/plots/` | Visualizations |
| `*.png` | `writeup/tables/` | Rendered tables |
| `*.txt` | `writeup/numbers/` | Computed statistics |
| `export_survey_docs.py` | `analysis/` | Script to export survey docs |
| `export_results_csv.py` | `analysis/` | Script to export CSV |
| `plot_*.py` | `analysis/` | One script per visualization |
| `table_*.py` | `analysis/` | One script per table |
| `generate_report.py` | `analysis/` | Script to generate report.md |
