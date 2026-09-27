import uuid

from ai_data_agent.agents.judge import judge_answer
from ai_data_agent.agents.state import AgentState

print("--- Case 1: correct answer, should PASS ---")
state = AgentState(
    user_question="How many rides were completed?",
    correlation_id=str(uuid.uuid4()),
    validated_sql="SELECT COUNT(*) FROM rides WHERE status = 'completed' LIMIT 500",
    query_result=[{"count": 3}],
    business_explanation="There are 3 completed rides.",
)
result = judge_answer(state)
print(f"verdict: {result.judge_verdict}, feedback: {result.judge_feedback}, retry_count: {result.retry_count}")

print("\n--- Case 2: WRONG answer (numbers don't match), should FAIL ---")
state2 = AgentState(
    user_question="How many rides were completed?",
    correlation_id=str(uuid.uuid4()),
    validated_sql="SELECT COUNT(*) FROM rides WHERE status = 'completed' LIMIT 500",
    query_result=[{"count": 3}],
    business_explanation="There are 47 completed rides.",
)
result2 = judge_answer(state2)
print(f"verdict: {result2.judge_verdict}, feedback: {result2.judge_feedback}, retry_count: {result2.retry_count}")
