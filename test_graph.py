import uuid

from ai_data_agent.agents.graph import build_graph
from ai_data_agent.agents.state import AgentState

app = build_graph()

test_cases = [
    ("How many rides were completed?", None),
    ("Review this ETL function", "def load(df):\n    df['x'] = df['x'] / 0\n    return df"),
    ("Please delete all customer records.", None),
]

for question, code in test_cases:
    initial_state = AgentState(
        user_question=question,
        correlation_id=str(uuid.uuid4()),
        code_to_review=code,
    )
    result = app.invoke(initial_state)
    print(f"Q: {question}")
    print(f"route: {result['route']}")
    print(f"final_answer: {result['final_answer']}")
    print(f"retry_count: {result['retry_count']}")
    print()
