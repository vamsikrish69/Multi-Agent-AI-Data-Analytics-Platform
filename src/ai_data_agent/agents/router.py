import structlog

from ai_data_agent.agents.state import AgentState, RouteType
from ai_data_agent.llm.provider import get_chat_model

logger = structlog.get_logger()

ROUTER_SYSTEM_PROMPT = """You are a routing classifier for a data analytics system.

Classify the user's request into exactly ONE of these categories:
- sql_analyst: the user is asking a question about mobility/rides/drivers/customers/payments data (e.g. counts, sums, comparisons, lookups about rides, customers, drivers, payments, ratings, locations)
- marketing_analyst: the user is asking a question about marketing campaigns, channels, attribution, conversions, revenue, or ROAS
- etl_analyst: the user wants Python or SQL ETL/pipeline code reviewed for bugs, data quality issues, or transformation logic
- unsupported: the request is unsafe, asks to modify/delete data, is unrelated to data analysis, or is unclear

Respond with ONLY one word: sql_analyst, marketing_analyst, etl_analyst, or unsupported. No punctuation, no explanation.
"""


def route_request(state: AgentState) -> AgentState:
    """Classify the user's question and set state.route accordingly."""
    model = get_chat_model()

    response = model.invoke(
        [
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": state.user_question},
        ]
    )

    raw_decision = str(response.content).strip().lower()

    if "marketing_analyst" in raw_decision:
        state.route = RouteType.MARKETING_ANALYST
    elif "sql_analyst" in raw_decision:
        state.route = RouteType.SQL_ANALYST
    elif "etl_analyst" in raw_decision:
        state.route = RouteType.ETL_ANALYST
    elif "unsupported" in raw_decision:
        state.route = RouteType.UNSUPPORTED
        state.rejection_reason = "Request was classified as unsupported or unsafe."
    else:
        state.route = RouteType.UNSUPPORTED
        state.rejection_reason = f"Request could not be confidently classified (model said: '{raw_decision}')"

    logger.info(
        "router_decision",
        correlation_id=state.correlation_id,
        raw_decision=raw_decision,
        route=state.route,
    )

    return state
