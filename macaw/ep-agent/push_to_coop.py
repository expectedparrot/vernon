from study_agent_list import agent_list

# Push to Expected Parrot (Coop)
result = agent_list.push(
    visibility="unlisted",
    description="A diverse collection of 5 realistic buyer personas for silk sheet shoppers, representing key market segments including luxury shoppers, skin health focused consumers, eco-conscious buyers, gift purchasers, and sleep quality seekers. Each agent includes detailed demographics, motivations, specific needs, budget considerations, and shopping behaviors to enable realistic market research and customer insight simulations.",
    alias="silk-sheet-buyers-personas"
)

print("Successfully pushed to Coop!")
print(f"Result: {result}")
