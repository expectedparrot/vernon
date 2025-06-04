from edsl import FileStore, QuestionFreeText, QuestionMultipleChoice, Scenario, Model, Survey 

m = Model("gemini-1.5-flash", service = "google")


s = Scenario.from_pdf("examples/smith1962jpe.pdf")

scenario = Scenario({'paper': FileStore(path = "examples/smith1962jpe.pdf")})

q_num_roles = QuestionFreeText(
    question_text = "In this paper, {{ scenario.paper }}, how many different 'roles' are there in this experiment?",
    question_name = "num_roles", 
)

q_timing = QuestionMultipleChoice(
    question_text = "In this paper, {{ scenario.paper }}, is timing continuous or discrete?",
    question_name = "timing",
    question_options = ["continuous", "discrete"],
)


q_instructions = QuestionFreeText(
    question_text = "In this paper, {{ scenario.paper }}, what instructions are given to participants in the experiment?",
    question_name = "instructions", 
)

results = Survey([q_num_roles, q_instructions]).by(m).by(scenario).run()

print(results.select('instructions', 'num_roles'))








