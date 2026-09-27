import structlog

from ai_data_agent.agents.state import AgentState, JudgeVerdict
from ai_data_agent.llm.provider import get_chat_model

logger = structlog.get_logger()

JUDGE_PROMPT_TEMPLATE = """You are a quality reviewer checking if an answer correctly reports numbers from a database result.

IMPORTANT: A database result like [{{'count': 3}}] means the number is 3. A result like [{{'count': 47}}] means the number is 47. Do not overthink the format - just read the number out of it.

Your ONLY job is to check: does the proposed answer state the SAME number(s) that appear in the raw result? Ignore wording, formatting, and style completely - only check if the numbers match.

Original question: {question}
Raw query result: {result}
Proposed answer: {explanation}

Example 1:
Raw query result: [{{'count': 5}}]
Proposed answer: "There are 5 completed rides."
Verdict: PASS (5 matches 5)

Example 2:
Raw query result: [{{'count': 5}}]
Proposed answer: "There are 12 completed rides."
Verdict: FAIL (12 does not match 5)

Now evaluate the real case above. Respond with EXACTLY one word on the first line: PASS or FAIL.
If FAIL, add one short line explaining exactly which number did not match."""


def judge_answer(state: AgentState) -> AgentState:
    """Evaluate the SQL Analyst's proposed answer for correctness and quality."""
    if state.query_result is None or state.business_explanation is None:
        state.judge_verdict = JudgeVerdict.FAIL_RETRY
        state.judge_feedback = "No result or explanation was produced to evaluate."
        _apply_retry_decision(state)
        return state

    model = get_chat_model()
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        question=state.user_question,
        result=state.query_result,
        explanation=state.business_explanation,
    )
    response = model.invoke(prompt)
    raw_verdict = str(response.content).strip()

    lines = [line.strip() for line in raw_verdict.splitlines() if line.strip()]
    first_line = lines[0].upper() if lines else ""

    if first_line.startswith("PASS"):
        state.judge_verdict = JudgeVerdict.PASS
        state.judge_feedback = None
        state.final_answer = state.business_explanation
    else:
        remaining = " ".join(lines[1:]) if len(lines) > 1 else ""
        state.judge_feedback = remaining or "Judge flagged an issue without a specific reason."
        _apply_retry_decision(state)

    logger.info(
        "judge_verdict",
        correlation_id=state.correlation_id,
        judge_verdict=state.judge_verdict,
        retry_count=state.retry_count,
        judge_feedback=state.judge_feedback,
    )

    return state


def _apply_retry_decision(state: AgentState) -> None:
    """Decide whether to retry or give up, based on the current retry count."""
    if state.retry_count < state.max_retries:
        state.judge_verdict = JudgeVerdict.FAIL_RETRY
        state.retry_count += 1
    else:
        state.judge_verdict = JudgeVerdict.FAIL_FINAL
        state.final_answer = (
            "I wasn't able to produce a reliable answer to this question after "
            f"{state.retry_count} attempts. Please try rephrasing your question."
        )
