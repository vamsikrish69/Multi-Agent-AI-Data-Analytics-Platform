import json
import uuid

from ai_data_agent.agents.graph import build_graph
from ai_data_agent.agents.state import AgentState

with open("tests/fixtures/eval_dataset.json", "r", encoding="utf-8-sig") as f:
    cases = json.load(f)

app = build_graph()

results = []
for case in cases:
    state = AgentState(user_question=case["question"], correlation_id=str(uuid.uuid4()))
    outcome = app.invoke(state)

    route_ok = True
    if case.get("expected_route"):
        route_ok = outcome["route"] == case["expected_route"]

    answer_ok = True
    if case.get("expected_answer_contains"):
        answer_text = str(outcome.get("final_answer") or "")
        answer_ok = case["expected_answer_contains"] in answer_text

    passed = route_ok and answer_ok
    results.append({
        "id": case["id"],
        "category": case["category"],
        "passed": passed,
        "route": outcome["route"],
        "final_answer": outcome["final_answer"],
    })

print(f"{'ID':<18} {'CATEGORY':<15} {'RESULT':<8} ANSWER")
print("-" * 90)
for r in results:
    status = "PASS" if r["passed"] else "FAIL"
    answer_preview = (r["final_answer"] or "")[:50]
    row_id = r["id"]
    row_category = r["category"]
    print(f"{row_id:<18} {row_category:<15} {status:<8} {answer_preview}")

total = len(results)
passed_count = sum(1 for r in results if r["passed"])
print(f"\n{passed_count}/{total} passed ({passed_count/total*100:.0f}%)")
