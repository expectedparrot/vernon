"""
MIT Faculty Life Satisfaction Survey

A comprehensive survey to assess faculty quality of life, administrative concerns,
compensation, work-life balance, support/resources, and overall job satisfaction.
"""

from edsl import (
    Survey,
    Instruction,
    QuestionLinearScale,
    QuestionMultipleChoice,
    QuestionCheckBox,
    QuestionFreeText,
    QuestionLikertFive
)

# Introduction instruction
intro = Instruction(
    text="""Welcome to the MIT Faculty Life Satisfaction Survey.

    This survey aims to understand your experiences as a faculty member at MIT,
    including quality of life issues, administrative concerns, compensation,
    work-life balance, and overall job satisfaction. Your responses will help
    identify areas for improvement and inform institutional policies.

    The survey takes approximately 10-15 minutes to complete. All responses are
    confidential and will be reported only in aggregate form.""",
    name="intro"
)

# Question 1: Overall job satisfaction
q1_overall_satisfaction = QuestionLinearScale(
    question_name="overall_satisfaction",
    question_text="Overall, how satisfied are you with your position at MIT?",
    question_options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    option_labels={1: "Extremely Dissatisfied", 10: "Extremely Satisfied"}
)

# Question 2: Workload assessment
q2_workload = QuestionLinearScale(
    question_name="workload_satisfaction",
    question_text="How satisfied are you with your current workload?",
    question_options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    option_labels={1: "Completely Unmanageable", 10: "Perfectly Balanced"}
)

# Question 3: Compensation satisfaction
q3_compensation = QuestionLinearScale(
    question_name="compensation_satisfaction",
    question_text="How satisfied are you with your overall compensation (salary and benefits)?",
    question_options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    option_labels={1: "Extremely Dissatisfied", 10: "Extremely Satisfied"}
)

# Question 4: Specific compensation concerns
q4_compensation_concerns = QuestionCheckBox(
    question_name="compensation_concerns",
    question_text="Which of the following compensation-related concerns do you have? (Select all that apply)",
    question_options=[
        "Salary not competitive with peer institutions",
        "Health insurance costs too high",
        "Retirement benefits insufficient",
        "Limited salary growth/raises",
        "Inequitable pay across departments",
        "Housing costs relative to salary",
        "Lack of transparency in compensation decisions",
        "No concerns"
    ]
)

# Question 5: Administrative burden
q5_admin_burden = QuestionLikertFive(
    question_name="admin_burden",
    question_text="Administrative tasks and bureaucracy significantly interfere with my research and teaching responsibilities."
)

# Question 6: Administrative concerns
q6_admin_concerns = QuestionCheckBox(
    question_name="admin_concerns",
    question_text="What administrative issues concern you most? (Select all that apply)",
    question_options=[
        "Excessive paperwork and reporting requirements",
        "Inefficient administrative processes",
        "Lack of administrative support staff",
        "Poor communication from administration",
        "Limited faculty voice in decision-making",
        "Unclear or changing policies",
        "Slow response times from administrative offices",
        "No significant concerns"
    ]
)

# Question 7: Work-life balance
q7_work_life_balance = QuestionLinearScale(
    question_name="work_life_balance",
    question_text="How would you rate your work-life balance?",
    question_options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    option_labels={1: "Very Poor Balance", 10: "Excellent Balance"}
)

# Question 8: Work-life balance challenges
q8_work_life_challenges = QuestionCheckBox(
    question_name="work_life_challenges",
    question_text="What challenges do you face regarding work-life balance? (Select all that apply)",
    question_options=[
        "Excessive work hours required",
        "Difficulty taking time off",
        "Work expectations during evenings/weekends",
        "Limited flexibility in schedule",
        "Pressure to be constantly available",
        "Insufficient family leave policies",
        "Lack of childcare support",
        "Difficulty maintaining personal health and wellness",
        "No significant challenges"
    ]
)

# Question 9: Resources and support
q9_resources = QuestionMultipleChoice(
    question_name="resources_adequacy",
    question_text="Overall, how adequate are the resources and support provided for your work (research funding, lab space, teaching support, professional development, etc.)?",
    question_options=[
        "Severely inadequate",
        "Inadequate",
        "Somewhat inadequate",
        "Adequate",
        "More than adequate",
        "Excellent"
    ]
)

# Question 10: Specific resource concerns
q10_resource_concerns = QuestionCheckBox(
    question_name="resource_concerns",
    question_text="What specific resource or support gaps do you experience? (Select all that apply)",
    question_options=[
        "Insufficient research funding",
        "Inadequate lab or office space",
        "Limited access to equipment or facilities",
        "Insufficient teaching assistant support",
        "Limited professional development opportunities",
        "Inadequate mentoring for junior faculty",
        "Lack of technical or administrative support staff",
        "Limited funding for conference travel",
        "Insufficient computing/IT resources",
        "No significant gaps"
    ]
)

# Question 11: Career development satisfaction
q11_career_development = QuestionLikertFive(
    question_name="career_development",
    question_text="I feel supported in my career development and advancement at MIT."
)

# Question 12: Greatest challenges (open-ended)
q12_challenges = QuestionFreeText(
    question_name="greatest_challenges",
    question_text="What are the greatest challenges you face as a faculty member at MIT? Please provide specific examples."
)

# Question 13: Improvements needed (open-ended)
q13_improvements = QuestionFreeText(
    question_name="needed_improvements",
    question_text="What changes or improvements would most significantly enhance your satisfaction and effectiveness as a faculty member?"
)

# Question 14: Likelihood to recommend
q14_recommend = QuestionLinearScale(
    question_name="recommend_likelihood",
    question_text="How likely would you be to recommend MIT as a place to work to a colleague in your field?",
    question_options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    option_labels={0: "Not at all likely", 10: "Extremely likely"}
)

# Build the survey
survey = Survey([
    q1_overall_satisfaction,
    q2_workload,
    q3_compensation,
    q4_compensation_concerns,
    q5_admin_burden,
    q6_admin_concerns,
    q7_work_life_balance,
    q8_work_life_challenges,
    q9_resources,
    q10_resource_concerns,
    q11_career_development,
    q12_challenges,
    q13_improvements,
    q14_recommend
])

# Add the introduction at the beginning
survey = survey.add_instruction(intro, index=0)

if __name__ == "__main__":
    # Display survey information
    print("MIT Faculty Life Satisfaction Survey")
    print("=" * 60)
    print(f"Total questions: {len(survey)}")
    print(f"\nQuestion names: {survey.question_names}")
    print("\nSurvey created successfully!")
    print("\nTo run this survey with AI agents:")
    print("  results = survey.run()")
    print("\nTo run with specific scenarios or agents:")
    print("  results = survey.by(scenarios).run()")
