---
name: edsl-study-files
description: Templates for the standard EDSL study files: survey, scenarios, agents, models, and create_results.py.
---

# EDSL Study File Templates

Reference for the standard files in an EDSL study job directory. Each file exports a named object that `create_results.py` imports and assembles into a job.

| File | Purpose | Exports |
|------|---------|---------|
| `study_survey.py` | Defines questions and survey with rules/memory | `survey` |
| `study_scenario_list.py` | Defines scenario variations | `scenario_list` |
| `study_agent_list.py` | Defines respondent personas | `agent_list` |
| `study_model_list.py` | Defines which LLMs to use | `model_list` |
| `create_results.py` | Imports all objects, runs survey, saves results | (script) |

## `study_survey.py`

Defines and exports a `survey` object. Read `skills/surveys/SKILL.md` for the full question type reference.

```python
from edsl import (
    Survey,
    QuestionMultipleChoice,
    QuestionFreeText,
    QuestionLinearScale,
)

q_cuisine = QuestionMultipleChoice(
    question_name="favorite_cuisine",
    question_text="Which cuisine do you enjoy most?",
    question_options=["Italian", "Japanese", "Mexican", "Indian", "Thai"]
)

q_dish = QuestionFreeText(
    question_name="favorite_dish",
    question_text="What is your favorite {{ favorite_cuisine.answer }} dish?"
)

q_frequency = QuestionLinearScale(
    question_name="frequency",
    question_text="How often do you eat {{ favorite_cuisine.answer }} food?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Rarely", 5: "Very Often"}
)

survey = (Survey([q_cuisine, q_dish, q_frequency])
    .set_full_memory_mode())
```

## `study_scenario_list.py`

Defines and exports a `scenario_list`. If no scenarios are needed, export an empty `ScenarioList`.

> **IMPORTANT**: Every field in your `ScenarioList` must be referenced in at least one **question's `question_text`** using `{{ scenario.field_name }}` syntax, or EDSL will raise a `JobsCompatibilityError`. For example, a scenario with key `"topic"` needs a question containing `{{ scenario.topic }}`. Note: `Instruction` text does NOT count — only `question_text` satisfies this requirement.

```python
from edsl import Scenario, ScenarioList

scenario_list = ScenarioList([
    Scenario({"topic": "artificial intelligence"}),
    Scenario({"topic": "climate change"}),
])
```

When no scenarios are needed:
```python
from edsl import ScenarioList
scenario_list = ScenarioList()
```

## `study_agent_list.py`

Defines and exports an `agent_list`. Read `skills/agent-lists/SKILL.md` for creation patterns (from CSV, DataFrame, combinations, etc.).

> **IMPORTANT**: `name` is a reserved keyword for `Agent()`. Use `Agent(name='...', traits={...})` — never put `name` inside the `traits` dict. Putting `name` in traits will raise `AgentNameError`.

```python
from edsl import Agent, AgentList

agent_list = AgentList([
    Agent(traits={"persona": "health-conscious millennial", "age": 28}),
    Agent(traits={"persona": "traditional home cook", "age": 55}),
])
```

When no agents are needed:
```python
from edsl import AgentList
agent_list = AgentList()
```

## `study_model_list.py`

Defines and exports a `model_list` specifying which LLMs to use.

```python
from edsl import ModelList, Model

model_list = ModelList([Model("gpt-4o")])
```

## `create_results.py`

Imports all study objects, assembles the job, runs it, and saves results.
**Critical**: Save with `results.save()` — never print the Results object.

> **IMPORTANT**: This script lives in `edsl_jobs/` but results must be saved to the study root's `data/` directory. Use `Path(__file__)` to resolve paths relative to the study root so the save location is correct regardless of the working directory.

```python
from pathlib import Path
from study_survey import survey
from study_agent_list import agent_list
from study_scenario_list import scenario_list
from study_model_list import model_list

_STUDY_ROOT = Path(__file__).resolve().parent.parent
output = _STUDY_ROOT / "data" / "results"
output.parent.mkdir(parents=True, exist_ok=True)

# Chain .by() only for non-empty collections — empty ones cause IndexError
job = survey
if len(scenario_list) > 0:
    job = job.by(scenario_list)
if len(agent_list) > 0:
    job = job.by(agent_list)
job = job.by(model_list)

results = job.run()
results.save(str(output))  # writes <study_root>/data/results.json.gz
print(f"Done. Saved {len(results)} results to {output}.json.gz")
```

The `.save(filename)` method writes a compressed `filename.json.gz` file.

> **IMPORTANT**: When loading results back, use `Results.load()` (NOT `Results.from_disk()` which does not exist). Pass the **full filename including the `.json.gz` extension**: `Results.load("data/results.json.gz")`. Passing just `"data/results"` (without the extension) will fail.

> **IMPORTANT**: Do NOT add preview code that indexes into individual results with
> dot-separated keys like `results[0]['scenario.field']` — this raises `KeyError`.
> If you want a quick preview, use the `select()` API:
> `results.select("scenario.message_frame", "answer.q1").print(max_rows=3)`

## Working with Results

After running a job, access columns using dot-separated prefixes. The `select()` method filters columns; `to_list()` extracts values.

```python
from edsl import Results

results = Results.load("data/results.json.gz")  # NOT from_disk or from_file (don't exist)

# Column names use prefixes: answer.*, scenario.*, agent.*, model.*
results.columns            # list all available column names
results.select("answer.q_support", "scenario.message_frame")  # filter columns

# Extract a single column as a list
results.select("answer.q_support").to_list()

# Print a formatted table
results.select("answer.*").print()

# Quick preview of a few rows
results.select("scenario.message_frame", "answer.q_support").print(max_rows=5)
```

Column name prefixes:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `answer.<question_name>` | Response to each question | `answer.q_support` |
| `scenario.<field>` | Scenario field values | `scenario.message_frame` |
| `agent.<trait>` | Agent trait values | `agent.age` |
| `model.model` | Which model produced the response | `model.model` |

### Accessing a single Result

`results[i]` returns a `Result` object. Access fields through `sub_dicts`, NOT
with dot-separated string keys:

```python
sample = results[0]
sample.sub_dicts['scenario']['message_frame']  # correct
sample.sub_dicts['answer']['q_support']        # correct
sample.combined_dict['message_frame']          # also works (flat, no prefix)

# WRONG — raises KeyError:
# sample['scenario.message_frame']
```

## Running

Run the EDSL job via the Makefile:
```
make data
```
