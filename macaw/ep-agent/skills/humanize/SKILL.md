---
name: humanize
description: Launching EDSL surveys for real human respondents via humanize, including scenario methods, Prolific integration, and retrieving responses.
---

# Humanize — Sending EDSL Surveys to Real Humans

Humanize converts an EDSL survey into a web-hosted survey on Expected Parrot (Coop) that real people can fill out in a browser. Results come back as standard EDSL `Results` objects.

## Basic usage (no scenarios)

```python
from edsl import Survey, QuestionFreeText, QuestionMultipleChoice

q1 = QuestionMultipleChoice(
    question_name="preference",
    question_text="Which do you prefer?",
    question_options=["Option A", "Option B", "Option C"],
)
q2 = QuestionFreeText(
    question_name="why",
    question_text="Why did you choose that?",
)

survey = Survey([q1, q2])

info = survey.humanize(
    human_survey_name="Preference Study",
    survey_visibility="unlisted",
)

print(info["respondent_url"])  # share this link with respondents
print(info["admin_url"])       # monitor responses here
```

`survey.humanize()` returns a `Scenario` (dict-like) with these keys:

| Key | Description |
|-----|-------------|
| `uuid` | Human survey UUID — needed to fetch responses later |
| `respondent_url` | Public link for respondents |
| `admin_url` | Admin dashboard link |
| `name` | Survey name |
| `n_responses` | Response count (0 at creation) |
| `survey_uuid` | UUID of the pushed survey object |
| `scenario_list_uuid` | UUID of the pushed scenario list (if any) |

**Save the `uuid`** — you need it to retrieve responses.

## With scenarios

When using scenarios, call `.humanize()` on a `Jobs` object (not directly on the survey). You must specify a `scenario_list_method`.

```python
from edsl import Scenario, ScenarioList

scenarios = ScenarioList([
    Scenario({"product": "Widget A", "price": "$10"}),
    Scenario({"product": "Widget B", "price": "$25"}),
    Scenario({"product": "Widget C", "price": "$50"}),
])

q = QuestionFreeText(
    question_name="opinion",
    question_text="What do you think of {{ product }} at {{ price }}?",
)

survey = Survey([q])

info = survey.by(scenarios).humanize(
    human_survey_name="Product Feedback",
    scenario_list_method="randomize",
)
```

### Scenario list methods

| Method | Behavior |
|--------|----------|
| `"randomize"` | Each respondent gets a random scenario (with replacement) |
| `"ordered"` | Scenarios are assigned sequentially to respondents |
| `"loop"` | Survey is expanded — every question is repeated for every scenario (creates a longer survey) |
| `"single_scenario"` | Exactly one scenario is used for all respondents (scenario list must have length 1) |

**Rules:**
- If you attach scenarios, you **must** specify `scenario_list_method`.
- If you specify a method, you **must** attach scenarios.
- Agents and models are **not supported** with humanize — the survey goes to real humans.

## Retrieving responses

```python
from edsl import Coop

coop = Coop()

# Using the uuid from the humanize call
results = coop.get_human_survey_responses(info["uuid"])

# Results is a standard EDSL Results object
results.select("answer.preference", "answer.why").print()
```

If EDSL cannot construct a full `Results` object (e.g., schema mismatch), it falls back to returning a `ScenarioList` with the raw response data.

### Checking status

```python
status = coop.get_human_survey(info["uuid"])
print(f"Responses so far: {status['n_responses']}")
```

## Prolific integration

For paid recruitment via Prolific:

```python
coop = Coop()

# First, create the human survey
info = survey.humanize(human_survey_name="Paid Study")

# Then launch a Prolific study
study = coop.create_prolific_study(
    human_survey_uuid=info["uuid"],
    name="Product Preference Study",
    description="5-minute survey about product preferences",
    num_participants=100,
    estimated_completion_time_minutes=5,
    participant_payment_cents=150,  # $1.50 per respondent
    device_compatibility=["desktop", "tablet"],
)
```

**Minimum pay**: Prolific requires at least $8.00 USD/hour. EDSL validates this — if your payment / estimated time is below $8/hr, it raises a `CoopValueError`.

### Prolific filters

```python
filters = coop.list_prolific_filters()

# Inspect a filter
filters.find("age")

# Create filter dicts for the study
age_filter = filters.create_study_filter("age", min=25, max=45)

study = coop.create_prolific_study(
    human_survey_uuid=info["uuid"],
    name="Filtered Study",
    description="...",
    num_participants=50,
    estimated_completion_time_minutes=5,
    participant_payment_cents=200,
    filters=[age_filter],
)
```

### Retrieving Prolific responses

```python
results = coop.get_prolific_study_responses(
    human_survey_uuid=info["uuid"],
    study_id=study["study_id"],
)
```

## Complete workflow example

```python
from edsl import (
    Survey, QuestionMultipleChoice, QuestionFreeText,
    QuestionLinearScale, Scenario, ScenarioList, Coop,
)

# 1. Build the survey
q1 = QuestionMultipleChoice(
    question_name="appeal",
    question_text="How appealing is {{ product }}?",
    question_options=["Very appealing", "Somewhat appealing", "Not appealing"],
)
q2 = QuestionLinearScale(
    question_name="buy_likelihood",
    question_text="How likely are you to buy {{ product }} at {{ price }}?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Very unlikely", 5: "Very likely"},
)
q3 = QuestionFreeText(
    question_name="feedback",
    question_text="Any other thoughts on {{ product }}?",
)

survey = Survey([q1, q2, q3])

scenarios = ScenarioList([
    Scenario({"product": "EcoBottle", "price": "$15"}),
    Scenario({"product": "SmartMug", "price": "$30"}),
])

# 2. Launch as human survey
info = survey.by(scenarios).humanize(
    human_survey_name="Product Concept Test",
    scenario_list_method="randomize",
)

print(f"Share this link: {info['respondent_url']}")
print(f"Monitor here:    {info['admin_url']}")

# 3. Save the UUID for later
human_survey_uuid = info["uuid"]

# 4. Retrieve responses (run this after people have responded)
coop = Coop()
results = coop.get_human_survey_responses(human_survey_uuid)
results.select("answer.appeal", "answer.buy_likelihood", "scenario.product").print()
```

## Quick reference

| Task | Code |
|------|------|
| Humanize a survey | `survey.humanize(human_survey_name="...")` |
| Humanize with scenarios | `survey.by(scenarios).humanize(scenario_list_method="randomize")` |
| Get respondent link | `info["respondent_url"]` |
| Check response count | `Coop().get_human_survey(uuid)["n_responses"]` |
| Fetch results | `Coop().get_human_survey_responses(uuid)` |
| Launch Prolific study | `Coop().create_prolific_study(uuid, ...)` |
| Fetch Prolific results | `Coop().get_prolific_study_responses(uuid, study_id)` |
| List Prolific filters | `Coop().list_prolific_filters()` |
| Reset scenario ordering | `Coop().reset_scenario_sampling_state(uuid)` |
