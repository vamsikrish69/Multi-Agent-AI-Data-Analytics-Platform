import uuid

from ai_data_agent.agents.marketing_analyst import generate_marketing_sql, execute_marketing_sql, explain_marketing_result
from ai_data_agent.agents.state import AgentState

state = AgentState(
    user_question="Which channel had the best ROAS?",
    correlation_id=str(uuid.uuid4()),
)
state = generate_marketing_sql(state)
state = execute_marketing_sql(state)
state = explain_marketing_result(state)

print(f"Generated SQL: {state.generated_sql}")
print(f"Query result: {state.query_result}")
print(f"\nBusiness explanation:\n{state.business_explanation}")
