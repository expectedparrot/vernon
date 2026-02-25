"""
MIT Faculty AgentList for Satisfaction Survey

This module creates an EDSL AgentList representing diverse MIT faculty members
with various departments, ranks, years of experience, and research focus areas.
"""

from edsl import Agent, AgentList

# Create diverse MIT faculty agents
agents_data = [
    {
        "name": "Prof. Sarah Chen",
        "department": "Electrical Engineering and Computer Science",
        "rank": "Assistant Professor",
        "years_at_mit": 3,
        "research_focus": "Machine Learning and AI",
        "age": 35,
        "gender": "Female"
    },
    {
        "name": "Prof. Michael Rodriguez",
        "department": "Mechanical Engineering",
        "rank": "Full Professor",
        "years_at_mit": 18,
        "research_focus": "Robotics and Automation",
        "age": 52,
        "gender": "Male"
    },
    {
        "name": "Prof. Amara Okafor",
        "department": "Biology",
        "rank": "Associate Professor",
        "years_at_mit": 8,
        "research_focus": "Computational Biology",
        "age": 42,
        "gender": "Female"
    },
    {
        "name": "Prof. David Goldstein",
        "department": "Economics",
        "rank": "Full Professor",
        "years_at_mit": 22,
        "research_focus": "Behavioral Economics",
        "age": 56,
        "gender": "Male"
    },
    {
        "name": "Prof. Yuki Tanaka",
        "department": "Physics",
        "rank": "Assistant Professor",
        "years_at_mit": 2,
        "research_focus": "Quantum Computing",
        "age": 33,
        "gender": "Non-binary"
    },
    {
        "name": "Prof. Jennifer Walsh",
        "department": "Sloan School of Management",
        "rank": "Associate Professor",
        "years_at_mit": 10,
        "research_focus": "Organizational Behavior",
        "age": 45,
        "gender": "Female"
    },
    {
        "name": "Prof. Raj Patel",
        "department": "Chemical Engineering",
        "rank": "Full Professor",
        "years_at_mit": 25,
        "research_focus": "Sustainable Energy",
        "age": 58,
        "gender": "Male"
    },
    {
        "name": "Prof. Maria Santos",
        "department": "Linguistics and Philosophy",
        "rank": "Assistant Professor",
        "years_at_mit": 4,
        "research_focus": "Cognitive Linguistics",
        "age": 37,
        "gender": "Female"
    },
    {
        "name": "Prof. James Lee",
        "department": "Mathematics",
        "rank": "Associate Professor",
        "years_at_mit": 12,
        "research_focus": "Applied Mathematics",
        "age": 46,
        "gender": "Male"
    },
    {
        "name": "Prof. Elena Volkov",
        "department": "Aeronautics and Astronautics",
        "rank": "Full Professor",
        "years_at_mit": 20,
        "research_focus": "Space Systems",
        "age": 54,
        "gender": "Female"
    },
    {
        "name": "Prof. Omar Hassan",
        "department": "Civil and Environmental Engineering",
        "rank": "Assistant Professor",
        "years_at_mit": 3,
        "research_focus": "Climate Adaptation",
        "age": 36,
        "gender": "Male"
    },
    {
        "name": "Prof. Lisa Kim",
        "department": "Brain and Cognitive Sciences",
        "rank": "Associate Professor",
        "years_at_mit": 9,
        "research_focus": "Neuroscience",
        "age": 43,
        "gender": "Female"
    },
    {
        "name": "Prof. Thomas Anderson",
        "department": "Materials Science and Engineering",
        "rank": "Full Professor",
        "years_at_mit": 28,
        "research_focus": "Nanomaterials",
        "age": 60,
        "gender": "Male"
    },
    {
        "name": "Prof. Priya Sharma",
        "department": "Architecture",
        "rank": "Associate Professor",
        "years_at_mit": 7,
        "research_focus": "Urban Design",
        "age": 41,
        "gender": "Female"
    },
    {
        "name": "Prof. Carlos Mendez",
        "department": "Political Science",
        "rank": "Assistant Professor",
        "years_at_mit": 2,
        "research_focus": "International Relations",
        "age": 34,
        "gender": "Male"
    }
]

# Create AgentList from the data
agent_list = AgentList([
    Agent(
        name=faculty["name"],
        traits={
            "department": faculty["department"],
            "rank": faculty["rank"],
            "years_at_mit": faculty["years_at_mit"],
            "research_focus": faculty["research_focus"],
            "age": faculty["age"],
            "gender": faculty["gender"]
        }
    )
    for faculty in agents_data
])

# Save the agent list to JSON
agent_list.save('study_agent_list')

# Print summary
print(f"Created AgentList with {len(agent_list)} MIT faculty members")
print("\nBreakdown by rank:")
ranks = {}
for agent in agent_list:
    rank = agent.traits["rank"]
    ranks[rank] = ranks.get(rank, 0) + 1
for rank, count in sorted(ranks.items()):
    print(f"  {rank}: {count}")

print("\nBreakdown by department:")
departments = {}
for agent in agent_list:
    dept = agent.traits["department"]
    departments[dept] = departments.get(dept, 0) + 1
for dept, count in sorted(departments.items()):
    print(f"  {dept}: {count}")

print("\nAgent list saved to: study_agent_list.json")
