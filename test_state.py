import uuid

from ai_data_agent.agents.state import AgentState, RouteType, JudgeVerdict

print("--- Valid initial state ---")
state = AgentState(
    user_question="How many rides were completed?",
    correlation_id=str(uuid.uuid4()),
)
print(state.model_dump())

print("\n--- State after Router assigns a route ---")
state.route = RouteType.SQL_ANALYST
print(f"route = {state.route}")

print("\n--- State after Judge fails once ---")
state.judge_verdict = JudgeVerdict.FAIL_RETRY
state.retry_count += 1
print(f"judge_verdict = {state.judge_verdict}, retry_count = {state.retry_count}")

print("\n--- Invalid route should be rejected ---")
try:
    state.route = "not_a_real_route"
except Exception as e:
    print(f"Correctly rejected: {type(e).__name__}")