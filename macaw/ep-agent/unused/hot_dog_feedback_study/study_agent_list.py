from edsl import Agent, AgentList

# Create diverse personas to simulate different types of feedback
agent_list = AgentList([
    Agent(traits={
        "persona": "Food critic with refined palate",
        "age": 45,
        "preferences": "Values quality ingredients and proper technique"
    }),
    Agent(traits={
        "persona": "Casual hot dog enthusiast",
        "age": 28,
        "preferences": "Loves classic hot dogs, not too picky"
    }),
    Agent(traits={
        "persona": "Health-conscious eater",
        "age": 35,
        "preferences": "Concerned about freshness and quality of ingredients"
    }),
    Agent(traits={
        "persona": "Traditional hot dog purist",
        "age": 52,
        "preferences": "Believes in simple, classic preparation"
    }),
    Agent(traits={
        "persona": "Adventurous foodie",
        "age": 30,
        "preferences": "Enjoys trying new combinations and flavors"
    }),
])
