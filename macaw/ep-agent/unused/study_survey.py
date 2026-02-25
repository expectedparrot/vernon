"""
MIT Cafeteria Satisfaction Survey

A comprehensive survey to gather student feedback on campus dining services,
covering satisfaction, food quality, dietary accommodations, pricing, service,
cleanliness, hours, and suggestions for improvement.
"""

from edsl import (
    Survey,
    Instruction,
    QuestionLinearScale,
    QuestionMultipleChoice,
    QuestionCheckBox,
    QuestionFreeText,
    QuestionLikertFive,
    QuestionYesNo,
    QuestionRank,
)


# Introduction
intro = Instruction(
    text="""Welcome to the MIT Dining Services Satisfaction Survey!

Your feedback is valuable and will help us improve the dining experience for all MIT students.
This survey should take approximately 5-7 minutes to complete. All responses are confidential.""",
    name="intro"
)

# Section 1: Overall Satisfaction
q1_overall = QuestionLinearScale(
    question_name="overall_satisfaction",
    question_text="Overall, how satisfied are you with MIT campus dining services?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Dissatisfied", 4: "Neutral", 7: "Very Satisfied"}
)

q2_frequency = QuestionMultipleChoice(
    question_name="dining_frequency",
    question_text="How often do you eat at MIT dining facilities?",
    question_options=[
        "Multiple times daily",
        "Once daily",
        "Several times per week",
        "Once per week",
        "Less than once per week",
        "Rarely or never"
    ]
)

q3_primary_location = QuestionCheckBox(
    question_name="primary_locations",
    question_text="Which dining locations do you use most frequently? (Select all that apply)",
    question_options=[
        "Next House Dining",
        "Simmons Hall Dining",
        "McCormick Dining",
        "Maseeh Dining",
        "Anna's Taqueria",
        "Subway",
        "Au Bon Pain",
        "LaVerde's Market",
        "Food trucks",
        "Other campus dining locations"
    ]
)

# Section 2: Food Quality and Variety
section_food = Instruction(
    text="The next section focuses on food quality and variety.",
    name="section_food"
)

q4_food_quality = QuestionLinearScale(
    question_name="food_quality",
    question_text="How would you rate the overall quality of food at MIT dining facilities?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Poor", 4: "Adequate", 7: "Excellent"}
)

q5_food_variety = QuestionLinearScale(
    question_name="food_variety",
    question_text="How satisfied are you with the variety of food options available?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Dissatisfied", 4: "Neutral", 7: "Very Satisfied"}
)

q6_freshness = QuestionLikertFive(
    question_name="food_freshness",
    question_text="The food served at MIT dining facilities is fresh and well-prepared."
)

q7_taste = QuestionLikertFive(
    question_name="food_taste",
    question_text="The food at MIT dining facilities is flavorful and tastes good."
)

q8_menu_rotation = QuestionLikertFive(
    question_name="menu_rotation",
    question_text="There is enough variety in the menu rotation (menus don't become repetitive)."
)

# Section 3: Dietary Accommodations
section_dietary = Instruction(
    text="The next section asks about dietary accommodations and special dietary needs.",
    name="section_dietary"
)

q9_dietary_needs = QuestionCheckBox(
    question_name="dietary_needs",
    question_text="Do you have any of the following dietary needs or preferences? (Select all that apply)",
    question_options=[
        "Vegetarian",
        "Vegan",
        "Gluten-free",
        "Dairy-free",
        "Nut allergies",
        "Other food allergies",
        "Halal",
        "Kosher",
        "Low-sodium",
        "Other dietary restrictions",
        "No dietary restrictions"
    ]
)

q10_dietary_satisfaction = QuestionLinearScale(
    question_name="dietary_accommodation_satisfaction",
    question_text="How well do MIT dining services accommodate your dietary needs?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Poorly", 4: "Adequately", 7: "Excellently"}
)

q11_dietary_labeling = QuestionLikertFive(
    question_name="dietary_labeling",
    question_text="Food items are clearly labeled with ingredients and allergen information."
)

q12_dietary_options = QuestionLikertFive(
    question_name="dietary_options_availability",
    question_text="There are sufficient food options available that meet my dietary needs."
)

# Section 4: Pricing and Value
section_pricing = Instruction(
    text="The next section focuses on pricing and value for money.",
    name="section_pricing"
)

q13_value = QuestionLinearScale(
    question_name="value_for_money",
    question_text="How would you rate the value for money at MIT dining facilities?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Poor Value", 4: "Fair Value", 7: "Excellent Value"}
)

q14_pricing = QuestionMultipleChoice(
    question_name="pricing_perception",
    question_text="In your opinion, the prices at MIT dining facilities are:",
    question_options=[
        "Much too expensive",
        "Somewhat expensive",
        "About right",
        "Somewhat inexpensive",
        "Very inexpensive"
    ]
)

q15_portion_size = QuestionLikertFive(
    question_name="portion_size",
    question_text="Portion sizes are appropriate for the prices charged."
)

q16_meal_plan = QuestionYesNo(
    question_name="has_meal_plan",
    question_text="Do you have a meal plan?"
)

q17_meal_plan_satisfaction = QuestionLinearScale(
    question_name="meal_plan_satisfaction",
    question_text="How satisfied are you with your meal plan?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Dissatisfied", 4: "Neutral", 7: "Very Satisfied"}
)

# Section 5: Service and Staff
section_service = Instruction(
    text="The next section asks about service quality and staff interactions.",
    name="section_service"
)

q18_staff_friendliness = QuestionLinearScale(
    question_name="staff_friendliness",
    question_text="How would you rate the friendliness and helpfulness of dining staff?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Unfriendly", 4: "Neutral", 7: "Very Friendly"}
)

q19_service_speed = QuestionLinearScale(
    question_name="service_speed",
    question_text="How would you rate the speed of service at dining facilities?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Slow", 4: "Adequate", 7: "Very Fast"}
)

q20_wait_times = QuestionMultipleChoice(
    question_name="typical_wait_time",
    question_text="What is your typical wait time during peak hours?",
    question_options=[
        "Less than 5 minutes",
        "5-10 minutes",
        "10-15 minutes",
        "15-20 minutes",
        "More than 20 minutes"
    ]
)

q21_staff_knowledge = QuestionLikertFive(
    question_name="staff_knowledge",
    question_text="Staff members are knowledgeable about menu items and ingredients."
)

# Section 6: Cleanliness and Ambiance
section_environment = Instruction(
    text="The next section focuses on the dining environment, cleanliness, and ambiance.",
    name="section_environment"
)

q22_cleanliness = QuestionLinearScale(
    question_name="cleanliness",
    question_text="How would you rate the cleanliness of MIT dining facilities?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Unclean", 4: "Adequately Clean", 7: "Very Clean"}
)

q23_dining_area = QuestionLikertFive(
    question_name="dining_area_cleanliness",
    question_text="Dining areas and tables are kept clean and well-maintained."
)

q24_food_area = QuestionLikertFive(
    question_name="food_area_cleanliness",
    question_text="Food preparation and serving areas appear clean and sanitary."
)

q25_ambiance = QuestionLinearScale(
    question_name="ambiance",
    question_text="How would you rate the overall ambiance and atmosphere of the dining spaces?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Unpleasant", 4: "Neutral", 7: "Very Pleasant"}
)

q26_seating = QuestionLikertFive(
    question_name="seating_availability",
    question_text="There is adequate seating available when I visit dining facilities."
)

q27_comfort = QuestionLikertFive(
    question_name="dining_comfort",
    question_text="The dining spaces are comfortable and conducive to eating and socializing."
)

# Section 7: Hours of Operation
section_hours = Instruction(
    text="The next section asks about dining facility hours and convenience.",
    name="section_hours"
)

q28_hours_satisfaction = QuestionLinearScale(
    question_name="hours_satisfaction",
    question_text="How satisfied are you with the hours of operation at MIT dining facilities?",
    question_options=[1, 2, 3, 4, 5, 6, 7],
    option_labels={1: "Very Dissatisfied", 4: "Neutral", 7: "Very Satisfied"}
)

q29_hours_adequate = QuestionLikertFive(
    question_name="hours_adequate",
    question_text="Dining facility hours adequately accommodate my schedule."
)

q30_extended_hours = QuestionYesNo(
    question_name="want_extended_hours",
    question_text="Would you like to see extended hours at any dining facilities?"
)

q31_preferred_times = QuestionCheckBox(
    question_name="preferred_extended_hours",
    question_text="If extended hours were offered, which time periods would be most useful to you? (Select all that apply)",
    question_options=[
        "Earlier breakfast (before 7 AM)",
        "Late breakfast (10-11 AM)",
        "Late lunch (2-4 PM)",
        "Late dinner (after 8 PM)",
        "Late night (after 10 PM)",
        "Weekend brunch",
        "24-hour options"
    ]
)

# Section 8: Improvement Priorities
section_priorities = Instruction(
    text="We're interested in your priorities for improvement.",
    name="section_priorities"
)

q32_improvement_rank = QuestionRank(
    question_name="improvement_priorities",
    question_text="Please rank the following areas by priority for improvement (1 = highest priority):",
    question_options=[
        "Food quality",
        "Food variety",
        "Pricing and value",
        "Dietary accommodations",
        "Service speed",
        "Staff friendliness",
        "Cleanliness",
        "Hours of operation"
    ],
    num_selections=8
)

# Section 9: Open Feedback
section_feedback = Instruction(
    text="Finally, we'd love to hear your specific feedback and suggestions.",
    name="section_feedback"
)

q33_like_most = QuestionFreeText(
    question_name="like_most",
    question_text="What do you like most about MIT dining services?"
)

q34_like_least = QuestionFreeText(
    question_name="like_least",
    question_text="What do you like least about MIT dining services?"
)

q35_suggestions = QuestionFreeText(
    question_name="suggestions",
    question_text="What specific suggestions do you have for improving MIT dining services?"
)

q36_new_options = QuestionFreeText(
    question_name="new_food_options",
    question_text="Are there any specific food options, cuisines, or menu items you would like to see added?"
)

q37_additional_comments = QuestionFreeText(
    question_name="additional_comments",
    question_text="Is there anything else you would like to share about your dining experience at MIT?"
)

# Closing
closing = Instruction(
    text="Thank you for completing the MIT Dining Services Satisfaction Survey! Your feedback is invaluable in helping us improve the dining experience for all students.",
    name="closing"
)


# Build the survey
survey = Survey([
    intro,
    q1_overall,
    q2_frequency,
    q3_primary_location,

    section_food,
    q4_food_quality,
    q5_food_variety,
    q6_freshness,
    q7_taste,
    q8_menu_rotation,

    section_dietary,
    q9_dietary_needs,
    q10_dietary_satisfaction,
    q11_dietary_labeling,
    q12_dietary_options,

    section_pricing,
    q13_value,
    q14_pricing,
    q15_portion_size,
    q16_meal_plan,
    q17_meal_plan_satisfaction,

    section_service,
    q18_staff_friendliness,
    q19_service_speed,
    q20_wait_times,
    q21_staff_knowledge,

    section_environment,
    q22_cleanliness,
    q23_dining_area,
    q24_food_area,
    q25_ambiance,
    q26_seating,
    q27_comfort,

    section_hours,
    q28_hours_satisfaction,
    q29_hours_adequate,
    q30_extended_hours,
    q31_preferred_times,

    section_priorities,
    q32_improvement_rank,

    section_feedback,
    q33_like_most,
    q34_like_least,
    q35_suggestions,
    q36_new_options,
    q37_additional_comments,

    closing
])

# Add skip logic: only ask about meal plan satisfaction if they have a meal plan
survey = survey.add_skip_rule(
    "meal_plan_satisfaction",
    "{{ has_meal_plan.answer }} == 'No'"
)

# Add skip logic: only ask about extended hours preferences if they want them
survey = survey.add_skip_rule(
    "preferred_extended_hours",
    "{{ want_extended_hours.answer }} == 'No'"
)


if __name__ == "__main__":
    # Display survey information
    print("MIT Cafeteria Satisfaction Survey")
    print("=" * 50)
    print(f"Total questions: {len(survey.questions)}")
    print(f"\nQuestion names: {survey.question_names}")

    print("\n" + "=" * 50)
    print("Survey ready to run!")
    print("\nTo run the survey with an AI agent:")
    print("  from edsl import Agent")
    print("  results = survey.by(Agent()).run()")
    print("\nTo export:")
    print("  results.to_csv('survey_results.csv')")
