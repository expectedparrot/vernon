# kahn

A structured scenario planning CLI, named after [Herman Kahn](https://en.wikipedia.org/wiki/Herman_Kahn), the RAND strategist who pioneered scenario-based strategic thinking.

Kahn guides you through a disciplined 5-phase process: scan the environment for forces, select two critical uncertainties as axes, build a 2×2 scenario matrix, stress-test strategic options across all four futures, and generate a final report. All state lives as JSON and Markdown files on disk — no database, no daemon, no vendor lock-in.

The tool never calls an LLM. It provides the structure; you (or an LM agent) provide the judgment. Every command supports `--json` output with `next_steps` guidance, making it a natural tool for agentic workflows.

## Install

```bash
pip install git+https://github.com/expectedparrot/kahn.git
```

Or for local development:

```bash
git clone git@github.com:expectedparrot/kahn.git
pip install -e kahn/
```

Requires Python 3.11+. Dependencies: typer, pydantic, rich, jinja2.

## Quick start

```bash
# 1. Initialize a project with a focal question
kahn init \
  --question "How should Acme position itself over the next 10 years?" \
  --domain "consumer electronics" \
  --horizon "10 years"

# 2. Add environmental forces (aim for 8-15, spanning PESTEL domains)
kahn force add \
  --name "AI commoditization" \
  --domain technological \
  --type uncertainty \
  --impact high \
  --predictability low \
  --direction "AI capabilities may commoditize or create moats"

kahn force add \
  --name "Aging population in key markets" \
  --domain social \
  --type trend \
  --impact medium \
  --predictability high \
  --direction "Median age rising steadily in US, EU, Japan"

# 3. Select two high-impact, low-predictability forces as critical uncertainties
kahn uncertainty select f001 f003

# 4. Define the extreme poles for each axis
kahn uncertainty set-poles cu001 \
  --pole-a "AI creates winner-take-all dynamics" \
  --pole-b "AI capabilities become a commodity"

kahn uncertainty set-poles cu002 \
  --pole-a "Regulation fragments global markets" \
  --pole-b "Light-touch regulation enables free trade"

# 5. Run independence check, then lock the phase and build scenarios
kahn uncertainty check-independence
kahn phase advance
kahn scenario build

# 6. Name, narrate, and add signals for each scenario
kahn scenario name sc001 \
  --name "The Walled Gardens" \
  --tagline "AI moats meet fragmented regulation"

kahn scenario narrative set sc001 --file narrative_sc001.md

kahn scenario signals set sc001 \
  --signal "Top-3 AI labs refuse to open-source models" \
  --observable-in "Corporate announcements, patent filings" \
  --signal "EU passes AI sovereignty act" \
  --observable-in "Legislative trackers, trade press"

# ... repeat for sc002-sc004, then advance phase

# 7. Add and evaluate strategic options
kahn option add \
  --name "Platform Play" \
  --description "Build an open ecosystem and monetize via services"

kahn option evaluate op001 \
  --scenario sc001 --rating fragile --rationale "Walled gardens block platform adoption" \
  --scenario sc002 --rating robust --rationale "Open markets reward platform effects" \
  --scenario sc003 --rating acceptable --rationale "Mixed dynamics" \
  --scenario sc004 --rating robust --rationale "Commodity AI + open trade = platform heaven"

# 8. Rank options and generate the final report
kahn option robustness-rank
kahn report generate
```

## The five phases

Each phase must be completed and locked before the next one begins. Phase locks are irreversible (use snapshots to roll back if needed).

### Phase 1: Forces

Scan the environment for 8-15 forces across [PESTEL](https://en.wikipedia.org/wiki/PEST_analysis) domains (political, economic, social, technological, environmental, legal). Classify each as a **trend** (predictable direction) or **uncertainty** (could go either way). Rate impact and predictability as low/medium/high.

**Lock requires:** at least 2 uncertainty forces + at least 1 trend.

### Phase 2: Uncertainty selection

Pick two high-impact, low-predictability forces as the **critical uncertainties** that will form the axes of your scenario matrix. Define two extreme poles for each (e.g., "AI as Amplifier" vs "AI as Equalizer"). Run `uncertainty check-independence` to verify the axes aren't correlated.

**Lock requires:** both CUs have poles set + independence check has been run.

### Phase 3: Scenario construction

`scenario build` generates four scenarios from the 2×2 combination of poles. For each scenario:

1. **Name it** evocatively (not just the axis positions)
2. **Write a narrative** (200-400 words, internally consistent, vivid)
3. **Define early warning signals** (3+ per scenario, with where to observe them)

Trend forces automatically appear as predetermined elements in every scenario.

**Lock requires:** all four scenarios have names, narratives, and signals.

### Phase 4: Option evaluation

Add 4-6 strategic options. Rate each option's performance in each scenario as `robust` (thrives), `acceptable` (survives), or `fragile` (fails). The tool computes a robustness score (robust=1.0, acceptable=0.5, fragile=0.0, averaged across scenarios) and ranks options.

**Lock requires:** all options evaluated across all scenarios.

### Phase 5: Complete

Generate the final report artifacts into the `output/` directory:

| File | Contents |
|------|----------|
| `summary.md` | Narrative overview of the exercise |
| `strategy_matrix.json` | Options × scenarios performance grid |
| `robust_recommendations.md` | Ranked strategic recommendations |
| `signal_dashboard.json` | All early warning signals consolidated |

## Project directory structure

All state is stored under a single project directory (default: `./kahn_project`):

```
kahn_project/
├── meta.json                          # Focal question, domain, horizon, phase state
├── forces/
│   ├── trends/
│   │   └── f001.json, f002.json ...
│   └── uncertainties/
│       └── f003.json, f004.json ...
├── critical_uncertainties/
│   ├── cu001.json
│   └── cu002.json
├── scenarios/
│   ├── sc001/
│   │   ├── meta.json                 # Name, tagline, axis positions, consistency score
│   │   ├── narrative.md              # The scenario story
│   │   └── signals.json              # Early warning indicators
│   ├── sc002/, sc003/, sc004/
├── strategic_options/
│   ├── op001/
│   │   ├── meta.json                 # Name, description, hedging flag
│   │   └── performance.json          # Ratings per scenario + robustness score
│   ├── op002/, ...
├── snapshots/                         # Named full-state backups
└── output/                            # Generated report files
```

## Command reference

### Global flags

All commands accept:

| Flag | Default | Description |
|------|---------|-------------|
| `--project-dir PATH` | `./kahn_project` | Override project directory |
| `--json` | `false` | Machine-readable JSON envelope output |
| `--quiet` | `false` | Suppress output except errors |

Environment variables: `KAHN_PROJECT_DIR`, `KAHN_JSON_OUTPUT`, `KAHN_NO_COLOR`.

### Commands

```
kahn init --question ... --domain ... --horizon ...
kahn status

kahn force add --name ... --domain ... --type ... --impact ... --predictability ... --direction ...
kahn force list [--type trend|uncertainty] [--impact low|medium|high] [--domain ...]
kahn force show <force_id>
kahn force edit <force_id> [--name ...] [--impact ...] [--predictability ...] [--direction ...] [--notes ...]
kahn force delete <force_id> --confirm

kahn uncertainty select <force_id_a> <force_id_b>
kahn uncertainty set-poles <cu_id> --pole-a ... --pole-b ... [--description ...] [--independence-note ...]
kahn uncertainty list
kahn uncertainty show <cu_id>
kahn uncertainty check-independence

kahn scenario build
kahn scenario name <scenario_id> --name ... --tagline ...
kahn scenario list
kahn scenario show <scenario_id>
kahn scenario check-consistency [--scenario <scenario_id>]
kahn scenario narrative set <scenario_id> --file ... | --text ...
kahn scenario narrative show <scenario_id>
kahn scenario signals set <scenario_id> --signal ... --observable-in ... [repeated]
kahn scenario signals show <scenario_id>

kahn option add --name ... --description ... [--hedging] [--notes ...]
kahn option list
kahn option show <option_id>
kahn option evaluate <option_id> --scenario ... --rating ... --rationale ... [repeated]
kahn option evaluate-all
kahn option robustness-rank

kahn phase status
kahn phase lock <phase>
kahn phase advance

kahn report generate [--force]
kahn report show [--section summary|strategy|recommendations|signals]
kahn report export [--format markdown|json] [--output PATH]

kahn validate
kahn snapshot save <label>
kahn snapshot list
kahn snapshot restore <label>
```

## JSON output for agents

Every command with `--json` returns a consistent envelope:

```json
{
  "command": "force add",
  "status": "ok",
  "data": { ... },
  "warnings": [],
  "errors": [],
  "next_steps": ["kahn force list"]
}
```

Errors use the same structure with `"status": "error"` and a structured error object:

```json
{
  "code": "PHASE_LOCKED",
  "message": "Phase `forces` is locked.",
  "context": "...",
  "hint": "Use a snapshot restore if you need to recover."
}
```

Error codes: `PHASE_LOCKED`, `PHASE_REQUIRED`, `VALIDATION_FAILED`, `ID_NOT_FOUND`, `DEPENDENCY_MISSING`, `INTEGRITY_ERROR`, `ALREADY_EXISTS`.

## Design principles

- **Pure structure, no LLM calls.** The tool enforces workflow discipline. Agents or humans supply the thinking.
- **Filesystem-backed.** Every entity is a JSON or Markdown file. Version control, diff, copy, and inspect with standard tools.
- **Phase-locked progression.** You can't skip steps. Snapshots let you escape if you need to redo a phase.
- **Stateless between invocations.** No daemon, no database. Each command reads from disk, acts, writes to disk.
- **Dual interface.** Rich terminal output for humans, `--json` envelopes with `next_steps` for agents.
