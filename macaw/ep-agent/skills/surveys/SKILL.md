---
name: surveys
description: Complete reference for EDSL survey construction: question types, Jinja2 templating, skip/navigation rules, and memory modes.
---

# EDSL Survey Reference

Consolidated reference for building surveys with EDSL: question types, Jinja2 templating, skip/navigation rules, memory modes, helper utilities, and visualization.

## Basic Survey Creation

```python
from edsl import Survey, QuestionFreeText, QuestionMultipleChoice

q1 = QuestionFreeText(
    question_name="name",
    question_text="What is your name?"
)
q2 = QuestionMultipleChoice(
    question_name="color",
    question_text="What is your favorite color?",
    question_options=["Red", "Blue", "Green", "Yellow"]
)
q3 = QuestionFreeText(
    question_name="why_color",
    question_text="Why do you like that color?"
)

survey = Survey([q1, q2, q3])
```

## Adding Questions Incrementally

Survey is immutable - each operation returns a new Survey instance:

```python
survey = Survey()
survey = survey.add_question(QuestionFreeText(
    question_name="q1",
    question_text="First question?"
))
survey = survey.add_question(QuestionFreeText(
    question_name="q2",
    question_text="Second question?"
))

# Add at specific index
survey = survey.add_question(new_question, index=1)
```

## Adding Instructions

Instructions are displayed to respondents between questions:

```python
from edsl import Survey, Instruction

instruction = Instruction(
    text="Please answer the following questions honestly.",
    name="intro"
)

survey = survey.add_instruction(instruction)

survey = survey.add_instruction(
    Instruction(text="Now for some demographic questions...")
)
```

> **IMPORTANT**: `Instruction` text is NOT checked for scenario field references. If your scenarios have fields that must be used, reference them in a **question's `question_text`**, not in an Instruction. EDSL's `JobsCompatibilityError` only looks at question text.

---

## Question Types

All questions require `question_name` (a valid Python identifier) and `question_text`.

To see the question types available:

```python
from edsl import Question
Question.available()
```

### QuestionFreeText

Open-ended text responses without constraints.

```python
from edsl import QuestionFreeText

q = QuestionFreeText(
    question_name="feedback",
    question_text="What do you think about our service?"
)
```

### QuestionMultipleChoice

Single selection from a predefined list of options.

```python
from edsl import QuestionMultipleChoice

q = QuestionMultipleChoice(
    question_name="color",
    question_text="What is your favorite color?",
    question_options=["Red", "Blue", "Green", "Yellow"]
)
```

### QuestionCheckBox

Multiple selections from a predefined list (checkbox-style).

```python
from edsl import QuestionCheckBox

q = QuestionCheckBox(
    question_name="features",
    question_text="Which features do you use? (Select all that apply)",
    question_options=["Feature A", "Feature B", "Feature C", "Feature D"],
    min_selections=1,
    max_selections=3
)
```

### QuestionNumerical

Numeric responses with optional min/max bounds.

```python
from edsl import QuestionNumerical

q = QuestionNumerical(
    question_name="age",
    question_text="How old are you?",
    min_value=0,
    max_value=120
)
```

### QuestionYesNo

Simple binary yes/no question (derived from MultipleChoice).

```python
from edsl import QuestionYesNo

q = QuestionYesNo(
    question_name="consent",
    question_text="Do you agree to participate in this survey?"
)
# Options are automatically ["Yes", "No"]
```

### QuestionLinearScale

Linear scale with customizable range and endpoint labels.

```python
from edsl import QuestionLinearScale

q = QuestionLinearScale(
    question_name="satisfaction",
    question_text="How satisfied are you with our service?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Very Unsatisfied", 5: "Very Satisfied"}
)
```

### QuestionLikertFive

Standard 5-point Likert scale (agree/disagree).

```python
from edsl import QuestionLikertFive

q = QuestionLikertFive(
    question_name="statement_agree",
    question_text="I find the product easy to use."
)
# Options: Strongly disagree, Disagree, Neutral, Agree, Strongly agree
```

### QuestionList

Response as a list of items.

```python
from edsl import QuestionList

q = QuestionList(
    question_name="top_movies",
    question_text="List your top 3 favorite movies.",
    max_list_items=3
)
```

### QuestionRank

Ranking/ordering items by preference.

```python
from edsl import QuestionRank

q = QuestionRank(
    question_name="priority",
    question_text="Rank these features by importance (1 = most important):",
    question_options=["Speed", "Security", "Price", "Support"],
    num_selections=4
)
```

### QuestionMatrix

Grid-based responses with rows (items) and columns (options).

```python
from edsl import QuestionMatrix

q = QuestionMatrix(
    question_name="product_ratings",
    question_text="Rate each product on the following attributes:",
    question_items=["Product A", "Product B", "Product C"],
    question_options=["Poor", "Fair", "Good", "Excellent"],
)
```

### QuestionBudget

Allocating a fixed budget across multiple options.

```python
from edsl import QuestionBudget

q = QuestionBudget(
    question_name="time_allocation",
    question_text="How would you allocate 100 hours across these activities?",
    question_options=["Work", "Exercise", "Leisure", "Sleep"],
    budget_sum=100
)
```

### QuestionDict

Response as key-value pairs (structured data).

```python
from edsl import QuestionDict

q = QuestionDict(
    question_name="contact_info",
    question_text="Provide your contact information:",
    answer_keys=["name", "email", "phone"]
)
```

### QuestionExtract

Extracting specific information from text.

```python
from edsl import QuestionExtract

q = QuestionExtract(
    question_name="entities",
    question_text="Extract all company names from the following text: {{ text }}",
    answer_template={"companies": "List of company names"}
)
```

### QuestionDropdown

BM25-powered search through large option sets.

```python
from edsl import QuestionDropdown

q = QuestionDropdown(
    question_name="country",
    question_text="Select your country:",
    question_options=["Afghanistan", "Albania", ..., "Zimbabwe"]
)
```

### QuestionMultipleChoiceWithOther

Multiple choice with an "Other" option for custom responses.

```python
from edsl import QuestionMultipleChoiceWithOther

q = QuestionMultipleChoiceWithOther(
    question_name="source",
    question_text="How did you hear about us?",
    question_options=["Google", "Friend", "Advertisement"],
    other_option_label="Other (please specify)"
)
```

### QuestionCheckboxWithOther

Checkbox with an "Other" option for custom responses.

```python
from edsl import QuestionCheckboxWithOther

q = QuestionCheckboxWithOther(
    question_name="interests",
    question_text="What are your interests?",
    question_options=["Sports", "Music", "Reading"],
    other_option_label="Other"
)
```

### QuestionTopK

Select top K items from a list.

```python
from edsl import QuestionTopK

q = QuestionTopK(
    question_name="favorites",
    question_text="Select your top 3 favorite items:",
    question_options=["A", "B", "C", "D", "E"],
    k=3
)
```

### QuestionFunctional

Python function-based question (not sent to LLM - computed locally).

```python
from edsl import QuestionFunctional

def compute_sum(scenario, agent):
    numbers = scenario.get("numbers", [])
    return sum(numbers)

q = QuestionFunctional(
    question_name="total",
    question_text="Calculate the sum",
    func=compute_sum
)
```

### QuestionPydantic

Use custom Pydantic models as response schemas.

```python
from edsl import QuestionPydantic
from pydantic import BaseModel

class PersonInfo(BaseModel):
    name: str
    age: int
    occupation: str

q = QuestionPydantic(
    question_name="person",
    question_text="Describe a person:",
    pydantic_model=PersonInfo
)
```

### QuestionMarkdown

Responses with markdown formatting.

```python
from edsl import QuestionMarkdown

q = QuestionMarkdown(
    question_name="formatted_response",
    question_text="Write a formatted response with headers and lists."
)
```

## Common Parameters

All questions support these common parameters:

| Parameter | Description |
|-----------|-------------|
| `question_name` | Unique identifier (valid Python identifier) |
| `question_text` | The question text (supports Jinja2 templating) |
| `answering_instructions` | Optional custom instructions for the LLM |
| `question_presentation` | Optional custom presentation template |

## Question Type Quick Reference

| Type | Use Case | Key Parameter |
|------|----------|---------------|
| `QuestionFreeText` | Open-ended responses | - |
| `QuestionMultipleChoice` | Single selection | `question_options` |
| `QuestionCheckBox` | Multiple selections | `question_options` |
| `QuestionNumerical` | Numbers | `min_value`, `max_value` |
| `QuestionYesNo` | Binary yes/no | - |
| `QuestionLinearScale` | Numeric scale | `question_options`, `option_labels` |
| `QuestionLikertFive` | 5-point agree/disagree | - |
| `QuestionList` | List of items | `max_list_items` |
| `QuestionRank` | Ordering | `question_options`, `num_selections` |
| `QuestionMatrix` | Grid/table | `question_items`, `question_options` |
| `QuestionBudget` | Budget allocation | `question_options`, `budget_sum` |
| `QuestionDict` | Key-value pairs | `answer_keys` |
| `QuestionExtract` | Extract from text | `answer_template` |
| `QuestionDropdown` | Large option sets | `question_options` |

---

## Jinja2 Templating in Questions

EDSL uses Jinja2 templating to create dynamic questions. Template variables are enclosed in `{{ }}` and are rendered at runtime.

### Scenario Templating

```python
from edsl import QuestionFreeText, Scenario

q = QuestionFreeText(
    question_name="opinion",
    question_text="What do you think about {{ scenario.fruit }}?"
)

scenarios = [
    Scenario({"fruit": "apples"}),
    Scenario({"fruit": "oranges"}),
]

results = q.by(scenarios).run()
```

### Agent Templating

```python
from edsl import QuestionFreeText, Agent

q = QuestionFreeText(
    question_name="perspective",
    question_text="As a {{ agent.occupation }}, what do you think about remote work?"
)

agent = Agent(traits={"occupation": "software engineer", "age": 35})
results = q.by(agent).run()
```

### Piping (Answer References)

Reference previous answers within a survey:

```python
q1 = QuestionFreeText(
    question_name="name",
    question_text="What is your name?"
)
q2 = QuestionFreeText(
    question_name="greeting",
    question_text="Hello {{ name.answer }}! How are you today?"
)
survey = Survey([q1, q2])
```

### Templating in Question Options

```python
q = QuestionMultipleChoice(
    question_name="preference",
    question_text="Which {{ scenario.category }} do you prefer?",
    question_options=[
        "{{ scenario.option_a }}",
        "{{ scenario.option_b }}",
        "{{ scenario.option_c }}"
    ]
)
```

### Template Variables Reference

| Variable | Access Pattern | Example |
|----------|---------------|---------|
| Scenario value | `{{ scenario.key }}` | `{{ scenario.fruit }}` |
| Agent trait | `{{ agent.trait }}` | `{{ agent.occupation }}` |
| Prior answer | `{{ question_name.answer }}` | `{{ q1.answer }}` |

---

## Survey Rules and Flow Control

Rules define conditional navigation through surveys using Jinja2 template expressions.

### Skip Rules (Before Rules)

```python
survey = survey.add_skip_rule(
    "pet_name",
    "{{ has_pet.answer }} == 'No'"
)
```

### Navigation Rules (After Rules)

```python
survey = (survey
    .add_rule("preference", "{{ preference.answer }} == 'A'", "section_a")
    .add_rule("preference", "{{ preference.answer }} == 'B'", "section_b"))
```

### Stop Rules (Early Termination)

```python
survey = survey.add_stop_rule(
    "eligibility",
    "{{ eligibility.answer }} == 'No'"
)
```

### EndOfSurvey Marker

```python
from edsl.surveys.navigation_markers import EndOfSurvey

survey = survey.add_rule("screening", "{{ screening.answer }} == 'disqualified'", EndOfSurvey)
```

### Expression Syntax

```python
"{{ question_name.answer }} == 'value'"
"{{ age.answer }} > 18"
"{{ q1.answer }} == 'yes' and {{ q2.answer }} != 'no'"
```

### Rules Quick Reference

| Task | Method |
|------|--------|
| Add skip rule | `survey.add_skip_rule(question, expression)` |
| Add navigation rule | `survey.add_rule(question, expression, next_question)` |
| Add stop rule | `survey.add_stop_rule(question, expression)` |
| Set priority | `survey.add_rule(q, expr, next_q, priority=1)` |
| View rules | `survey.show_rules()` |
| Jump to end | `survey.add_rule(q, expr, EndOfSurvey)` |

---

## Survey Memory System

Memory controls which previous question-answer pairs an agent sees when answering each question.

| Mode | Method | Use Case |
|------|--------|----------|
| No Memory | (default) | Independent questions |
| Full Memory | `survey.set_full_memory_mode()` | Conversational surveys |
| Lagged Memory | `survey.set_lagged_memory(lags=N)` | Recent context only |
| Targeted Memory | `survey.add_targeted_memory(focal, prior)` | Precise control |
| Memory Collection | `survey.add_memory_collection(focal, [priors])` | Multiple targeted |

---

## Survey Helper Utilities

### Matrix Combiner

```python
from edsl.surveys.survey_helpers.matrix_combiner import combine_multiple_choice_to_matrix

new_survey = combine_multiple_choice_to_matrix(
    survey=survey,
    question_names=["trust_freelancer", "trust_ai", "trust_agency"],
    matrix_question_name="trust_matrix"
)
```

---

## Chaining Operations

Survey methods can be chained since each returns a new Survey:

```python
survey = (Survey([q1, q2, q3])
    .add_rule("q1", "{{ q1.answer }} == 'skip'", "q3")
    .add_skip_rule("q2", "{{ q1.answer }} == 'skip'")
    .add_question(q4))
```


## Survey Quick Reference

| Task | Method |
|------|--------|
| Create survey | `Survey([q1, q2, q3])` |
| Add question | `survey.add_question(q, index=None)` |
| Add instruction | `survey.add_instruction(inst)` |
| Get question | `survey.get("question_name")` |
| List questions | `survey.questions` |
| Question names | `survey.question_names` |
| Number of questions | `len(survey)` |
