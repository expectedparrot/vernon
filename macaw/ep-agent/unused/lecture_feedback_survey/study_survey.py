from edsl import (
    Survey,
    QuestionLinearScale,
    QuestionFreeText,
    QuestionCheckBox,
)

# === QUESTIONS ===

q_clarity = QuestionLinearScale(
    question_name="clarity",
    question_text="How clear was the lecture content?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Not clear at all", 5: "Very clear"}
)

q_pace = QuestionLinearScale(
    question_name="pace",
    question_text="How would you rate the pace of the lecture?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Too slow", 3: "Just right", 5: "Too fast"}
)

q_engagement = QuestionLinearScale(
    question_name="engagement",
    question_text="How engaging was the lecture?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Not engaging", 5: "Very engaging"}
)

q_strengths = QuestionCheckBox(
    question_name="strengths",
    question_text="What were the strengths of this lecture? (Select all that apply)",
    question_options=[
        "Clear explanations",
        "Good examples",
        "Interactive activities",
        "Visual aids/slides",
        "Well-organized content",
        "Relevant to course material"
    ],
    min_selections=0,
    max_selections=6
)

q_improvements = QuestionFreeText(
    question_name="improvements",
    question_text="What could be improved in future lectures?"
)

q_additional_feedback = QuestionFreeText(
    question_name="additional_feedback",
    question_text="Any additional comments or feedback?"
)

# === SURVEY ===

survey = Survey([
    q_clarity,
    q_pace,
    q_engagement,
    q_strengths,
    q_improvements,
    q_additional_feedback
])
