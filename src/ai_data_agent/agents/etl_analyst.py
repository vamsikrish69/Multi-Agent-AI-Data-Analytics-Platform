import structlog

from ai_data_agent.agents.state import AgentState
from ai_data_agent.llm.provider import get_chat_model

logger = structlog.get_logger()

ETL_REVIEW_PROMPT_TEMPLATE = """You are a senior data engineer reviewing ETL (Extract, Transform, Load) code for problems.

Review the following code for:
- Data quality issues (missing null handling, no validation of inputs, silent failures)
- Transformation bugs (incorrect logic, off-by-one errors, wrong data types)
- Pipeline reliability issues (no error handling, no logging, hardcoded values that should be config)

Code to review:
{code}

Provide your review as a short numbered list of specific issues found, each with a brief suggested fix. If you find no issues, say so clearly. Do not rewrite the entire code, just list the issues and fixes."""


def review_etl_code(state: AgentState) -> AgentState:
    """Review ETL code for data-quality, transformation, and pipeline issues."""
    code = state.code_to_review or state.user_question

    if not code or not code.strip():
        state.etl_review_notes = "No code was provided to review."
        return state

    model = get_chat_model()
    prompt = ETL_REVIEW_PROMPT_TEMPLATE.format(code=code)
    response = model.invoke(prompt)

    state.etl_review_notes = str(response.content).strip()

    logger.info(
        "etl_reviewed",
        correlation_id=state.correlation_id,
        review_length=len(state.etl_review_notes),
    )

    return state
