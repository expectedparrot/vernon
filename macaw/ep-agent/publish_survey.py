"""
Script to publish the NYU Cafeteria Satisfaction Survey to Coop
"""

from study_survey import survey

# Push to Coop
print("Publishing survey to Coop...")
print("-" * 70)

result = survey.push(
    visibility="unlisted",
    description="Comprehensive survey to assess NYU student satisfaction with cafeteria services, covering food quality, cleanliness, pricing, service, dietary options, and suggestions for improvement.",
    alias="nyu-cafeteria-satisfaction-survey"
)

print("\n✅ Survey published successfully!")
print("=" * 70)
print(f"URL: {result.get('url', 'N/A')}")
print(f"Alias: {result.get('alias', 'N/A')}")
print(f"Visibility: {result.get('visibility', 'N/A')}")
print("=" * 70)
