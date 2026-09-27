import uuid

from ai_data_agent.agents.sql_analyst import generate_sql, execute_sql, explain_result
from ai_data_agent.agents.state import AgentState

state = AgentState(
    user_question="How many rides were completed?",
    correlation_id=str(uuid.uuid4()),
)
state = generate_sql(state)
state = execute_sql(state)
state = explain_result(state)

print(f"Generated SQL: {state.generated_sql}")
print(f"Query result: {state.query_result}")
print(f"\nBusiness explanation:\n{state.business_explanation}")