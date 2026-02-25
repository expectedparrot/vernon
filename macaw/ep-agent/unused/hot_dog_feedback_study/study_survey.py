from edsl import (
    Survey,
    QuestionLinearScale,
    QuestionFreeText,
    QuestionMultipleChoice,
    QuestionCheckBox,
    QuestionLikertFive,
    Instruction,
)

# === INSTRUCTIONS ===

intro = Instruction(
    text="Thank you for trying the hot dogs! Please share your honest feedback.",
    name="intro"
)

# === QUESTIONS ===

# Overall satisfaction
q_overall = QuestionLinearScale(
    question_name="overall_satisfaction",
    question_text="Overall, how would you rate the hot dog?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Poor", 5: "Excellent"}
)

# Component ratings
q_bun = QuestionLinearScale(
    question_name="bun_rating",
    question_text="How would you rate the bun?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Poor", 5: "Excellent"}
)

q_meat = QuestionLinearScale(
    question_name="meat_rating",
    question_text="How would you rate the hot dog itself (the meat)?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Poor", 5: "Excellent"}
)

# Temperature
q_temp = QuestionMultipleChoice(
    question_name="temperature",
    question_text="How was the temperature of the hot dog?",
    question_options=["Too cold", "Lukewarm", "Just right", "Too hot"]
)

# Toppings and condiments
q_toppings = QuestionCheckBox(
    question_name="toppings_used",
    question_text="Which toppings/condiments did you use? (Select all that apply)",
    question_options=[
        "Ketchup",
        "Mustard",
        "Relish",
        "Onions",
        "Sauerkraut",
        "Mayo",
        "Hot sauce",
        "Other/None"
    ],
    min_selections=0,
    max_selections=8
)

q_toppings_rating = QuestionLinearScale(
    question_name="toppings_rating",
    question_text="How would you rate the quality/freshness of the toppings?",
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Poor", 5: "Excellent"}
)

# Presentation and portion
q_presentation = QuestionLikertFive(
    question_name="presentation",
    question_text="The hot dog was well-assembled and looked appetizing."
)

q_portion = QuestionMultipleChoice(
    question_name="portion_size",
    question_text="How was the portion size?",
    question_options=["Too small", "Just right", "Too large"]
)

# Detailed feedback
q_best_part = QuestionFreeText(
    question_name="best_part",
    question_text="What did you like most about the hot dog?"
)

q_improvement = QuestionFreeText(
    question_name="improvement",
    question_text="What could be improved?"
)

q_additional = QuestionFreeText(
    question_name="additional_comments",
    question_text="Any other comments or suggestions?"
)

# Would serve again
q_recommend = QuestionLikertFive(
    question_name="would_recommend",
    question_text="I would recommend this hot dog to others."
)

# === SURVEY ===

survey = Survey([
    intro,
    q_overall,
    q_bun,
    q_meat,
    q_temp,
    q_toppings,
    q_toppings_rating,
    q_presentation,
    q_portion,
    q_best_part,
    q_improvement,
    q_additional,
    q_recommend
]).set_full_memory_mode()
