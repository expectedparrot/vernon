"""
Hot Dog Feedback Study
======================

This script runs a comprehensive feedback survey about hot dogs served to guests.
It simulates responses from different types of diners with varied preferences and perspectives.

The survey collects:
- Overall satisfaction ratings
- Component-specific ratings (bun, meat, toppings)
- Temperature and presentation feedback
- Portion size assessment
- Free-text feedback on strengths and improvements
- Recommendation likelihood

Results are saved to data/results.json.gz for analysis.
"""

from study_survey import survey
from study_scenario_list import scenario_list
from study_agent_list import agent_list
from study_model_list import model_list

import os

# Run the survey
print("Running hot dog feedback survey...")
print(f"- Survey has {len(survey)} questions")
print(f"- Using {len(agent_list)} different respondent personas")
print(f"- Using model(s): {[m.model for m in model_list]}")

# Combine survey with agents and models
job = survey.by(agent_list).by(model_list)

# If scenarios exist, add them
if len(scenario_list) > 0:
    job = job.by(scenario_list)

# Run and get results
results = job.run()

# Save results
output_path = "data/results.json.gz"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
results.save(output_path)

print(f"\n✓ Results saved to {output_path}")
print(f"✓ Collected {len(results)} responses")

# Display a quick preview
print("\n" + "="*60)
print("PREVIEW: Overall Satisfaction Ratings")
print("="*60)
df = results.select("overall_satisfaction").to_pandas()
print(df)

print("\n" + "="*60)
print("To analyze results further:")
print("  1. Load results: results = Results.load('data/results.json.gz')")
print("  2. Convert to DataFrame: df = results.to_pandas()")
print("  3. Explore columns: df.columns")
print("="*60)
