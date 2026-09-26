import uuid

from ai_data_agent.agents.router import route_request
from ai_data_agent.agents.state import AgentState

questions = [
    "How many rides were completed last week?",
    "Can you review this Python ETL script for bugs?",
    "Please delete all customer records.",
]

for q in questions:
    state = AgentState(user_question=q, correlation_id=str(uuid.uuid4()))
    result = route_request(state)
    print(f"Q: {q}")
    print(f"-> route: {result.route}, rejection_reason: {result.rejection_reason}\n")