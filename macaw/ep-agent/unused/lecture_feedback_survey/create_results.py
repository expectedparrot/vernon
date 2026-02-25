"""
Run the lecture feedback survey and save results.

This script imports all study components and executes the survey.
"""

from study_survey import survey
from study_scenario_list import scenario_list
from study_agent_list import agent_list
from study_model_list import model_list

# Combine all components
job = survey.by(scenario_list).by(agent_list).by(model_list)

# Run the survey
results = job.run()

# Save results
results.save("lecture_feedback_results.json")

# Display results
print("\n=== Survey Completed ===\n")
print(results)

# Optional: Generate a summary report
results.select("clarity", "pace", "engagement", "strengths", "improvements", "additional_feedback").print()
