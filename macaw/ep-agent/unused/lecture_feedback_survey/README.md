# Lecture Feedback Survey

A short, generic survey for collecting student feedback on lectures.

## Survey Structure

This survey collects feedback across several dimensions:

1. **Clarity** - Linear scale (1-5) measuring how clear the lecture content was
2. **Pace** - Linear scale (1-5) measuring the lecture pace (too slow to too fast)
3. **Engagement** - Linear scale (1-5) measuring how engaging the lecture was
4. **Strengths** - Checkbox question identifying strong points (multiple selections allowed)
5. **Improvements** - Free text for suggested improvements
6. **Additional Feedback** - Free text for any other comments

## Files

- `study_survey.py` - Survey definition with all questions
- `study_scenario_list.py` - Empty (no scenario variations)
- `study_agent_list.py` - Empty (for real student responses)
- `study_model_list.py` - LLM model configuration
- `create_results.py` - Script to run survey and save results
- `Makefile` - Build commands for running the study

## Usage

### View the survey structure
```bash
make show-survey
```

### Run the survey
```bash
make run
```

### Clean up results
```bash
make clean
```

## Customization

Since this is a generic survey, you can easily:
- Add scenarios for specific lecture topics
- Modify question text to match your needs
- Add or remove questions as needed
- Adjust scale ranges or options

## Notes

- The survey is designed to be reusable across different lectures
- No specific lecture context is embedded in the questions
- Can be administered repeatedly throughout a course
