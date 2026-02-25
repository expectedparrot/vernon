---
name: agent-lists
description: Patterns for creating EDSL AgentLists from various sources: lists, CSV, Excel, DataFrame, and programmatic combinations.
---

# AgentList Creation Patterns

> **IMPORTANT**: `name` is a reserved keyword for `Agent()`. Use `Agent(name='...', traits={...})` — never put `name` inside the `traits` dict. Putting `name` in traits raises `AgentNameError`.

> **IMPORTANT**: `instructions` is a parameter of `AgentList.from_source()` only — it is NOT accepted by the `AgentList()` constructor. To add instructions when building an AgentList manually, set `instruction` on each Agent: `Agent(traits={...}, instruction="Answer as if...")`.

> **IMPORTANT**: All agents in an `AgentList` must have the **same** `instruction` string. EDSL raises `AgentListError` if any agent's instruction differs. Use **traits** for individuality (persona, background, demographics) and a single shared instruction for behavioral guidance. If agents don't need special instructions, omit `instruction` entirely.

## From a List of Agents

```python
from edsl import Agent, AgentList

agent1 = Agent(name="Alice", traits={"age": 25, "occupation": "teacher"})
agent2 = Agent(traits={"age": 35, "occupation": "doctor"})
agents = AgentList([agent1, agent2])
```

## From External Data Sources

The `from_source()` method auto-detects the source type:

```python
from edsl import AgentList

# From CSV file
agents = AgentList.from_source("people.csv")

# From Excel file
agents = AgentList.from_source("data.xlsx", sheet_name="Participants")

# From dictionary
agents = AgentList.from_source({
    "age": [25, 30, 35],
    "name": ["Alice", "Bob", "Charlie"],
    "occupation": ["teacher", "doctor", "engineer"]
})

# From pandas DataFrame
import pandas as pd
df = pd.DataFrame({"age": [25, 30], "city": ["NYC", "LA"]})
agents = AgentList.from_source(df)
```

## With Instructions and Codebook

```python
agents = AgentList.from_source(
    "people.csv",
    instructions="Answer as if you were this person",
    codebook={"age": "Age in years", "income": "Annual income in USD"},
    name_field="respondent_name"
)

# Or load codebook from a CSV file (2 columns: key, description)
agents = AgentList.from_source("people.csv", codebook="codebook.csv")
```

## Programmatically with Combinations

```python
from edsl import Agent, AgentList
from itertools import product

ages = [25, 35, 45]
occupations = ["teacher", "doctor", "engineer"]

agents = AgentList([
    Agent(traits={"age": age, "occupation": occ})
    for age, occ in product(ages, occupations)
])
# Creates 9 agents (3 ages x 3 occupations)
```

## Generated from Research / Web Data

```python
from edsl import Agent, AgentList

agents = AgentList([
    Agent(name="Person A", traits={"role": "CEO", "age": 45, "company": "Acme"}),
    Agent(name="Person B", traits={"role": "CTO", "age": 38, "company": "Acme"}),
])
```

## Quick Reference

| Source | Example |
|--------|---------|
| List of Agents | `AgentList([agent1, agent2])` |
| CSV file | `AgentList.from_source("file.csv")` |
| Excel file | `AgentList.from_source("file.xlsx", sheet_name="Sheet1")` |
| Dictionary | `AgentList.from_source({"col": [1, 2, 3]})` |
| DataFrame | `AgentList.from_source(df)` |
