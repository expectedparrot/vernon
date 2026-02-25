# Hot Dog Feedback Study

A comprehensive EDSL-based feedback survey system for collecting detailed opinions about hot dogs.

## 📋 Survey Components

This study collects feedback on:

- **Overall Satisfaction** - General rating (1-5 scale)
- **Component Quality**
  - Bun rating
  - Hot dog/meat rating
  - Toppings/condiments rating
- **Temperature** - Was it served at the right temperature?
- **Presentation** - Visual appeal and assembly
- **Portion Size** - Too small, just right, or too large
- **Open Feedback**
  - What you liked most
  - What could be improved
  - Additional comments
- **Recommendation** - Likelihood to recommend to others

## 🚀 Quick Start

### 1. Install Dependencies

```bash
make install-deps
# or
pip install edsl -U
```

### 2. Run the Survey

```bash
make run
# or
python create_results.py
```

This will:
- Simulate responses from 5 different respondent personas
- Generate comprehensive feedback for each component
- Save results to `data/results.json.gz`

### 3. View Results

```bash
make view-results
```

## 📁 Project Structure

```
hot_dog_feedback_study/
├── Makefile                      # Build commands
├── README.md                     # This file
├── study_survey.py              # Survey questions and logic
├── study_scenario_list.py       # Scenario variations (empty for this study)
├── study_agent_list.py          # Respondent personas
├── study_model_list.py          # LLM models to use
├── create_results.py            # Main script to run survey
├── data/                        # Results storage
├── writeup/                     # Analysis writeups
└── analysis/                    # Analysis notebooks/scripts
```

## 👥 Respondent Personas

The study simulates feedback from 5 diverse personas:

1. **Food Critic** (45) - Refined palate, values quality and technique
2. **Hot Dog Enthusiast** (28) - Casual lover of classic hot dogs
3. **Health-Conscious Eater** (35) - Focuses on freshness and quality
4. **Traditional Purist** (52) - Prefers simple, classic preparation
5. **Adventurous Foodie** (30) - Enjoys trying new combinations

## 📊 Analyzing Results

```python
from edsl import Results

# Load results
results = Results.load('data/results.json.gz')

# Convert to pandas DataFrame
df = results.to_pandas()

# Explore the data
print(df.columns)
print(df['overall_satisfaction'].describe())

# Select specific columns
feedback_df = results.select(
    'overall_satisfaction',
    'bun_rating',
    'meat_rating',
    'best_part',
    'improvement'
).to_pandas()

print(feedback_df)
```

## 🎯 Customization

### Modify Questions

Edit `study_survey.py` to add/remove/modify questions:

```python
from edsl import QuestionLinearScale

q_custom = QuestionLinearScale(
    question_name="spice_level",
    question_text="How would you rate the spice level?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Too Mild", 5: "Too Spicy"}
)
```

### Add Scenarios

If you served different types of hot dogs, edit `study_scenario_list.py`:

```python
from edsl import Scenario, ScenarioList

scenario_list = ScenarioList([
    Scenario({"hot_dog_type": "Classic Beef", "style": "Chicago"}),
    Scenario({"hot_dog_type": "Veggie", "style": "California"}),
    Scenario({"hot_dog_type": "Premium", "style": "New York"}),
])
```

### Change Respondent Personas

Edit `study_agent_list.py` to modify or add personas.

### Use Different Models

Edit `study_model_list.py` to use different LLMs:

```python
from edsl import ModelList, Model

model_list = ModelList([
    Model("gpt-4o"),
    Model("claude-3-5-sonnet-20241022"),
])
```

## 🧹 Cleanup

```bash
make clean
```

## 📝 Notes

- The survey uses **full memory mode**, so each question has context from previous answers
- Results are compressed (`.json.gz`) to save space
- Each persona generates unique, contextually appropriate feedback
- Temperature check helps identify serving issues
- Open-ended questions capture qualitative insights

## 🔧 Makefile Commands

| Command | Description |
|---------|-------------|
| `make help` | Show available commands |
| `make install-deps` | Install EDSL package |
| `make run` | Run the survey |
| `make clean` | Remove result files |
| `make view-results` | Quick preview of results |

---

**Built with [EDSL](https://docs.expectedparrot.com/)** - Expected Parrot Domain Specific Language for AI-powered surveys
