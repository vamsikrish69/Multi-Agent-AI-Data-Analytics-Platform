import structlog
from langgraph.graph import StateGraph, END

from ai_data_agent.agents.etl_analyst import review_etl_code
from ai_data_agent.agents.judge import judge_answer
from ai_data_agent.agents.marketing_analyst import execute_marketing_sql, explain_marketing_result, generate_marketing_sql
from ai_data_agent.agents.router import route_request
from ai_data_agent.agents.sql_analyst import execute_sql, explain_result, generate_sql
from ai_data_agent.agents.state import AgentState, JudgeVerdict, RouteType

logger = structlog.get_logger()


def finalize_etl(state: AgentState) -> AgentState:
    state.final_answer = state.etl_review_notes
    return state


def finalize_reject(state: AgentState) -> AgentState:
    state.final_answer = state.rejection_reason or "This request could not be processed."
    return state


def route_decision(state: AgentState) -> str:
    if state.route == RouteType.SQL_ANALYST:
        return "sql_generate"
    elif state.route == RouteType.MARKETING_ANALYST:
        return "marketing_generate"
    elif state.route == RouteType.ETL_ANALYST:
        return "etl_review"
    else:
        return "reject"


def judge_decision(state: AgentState) -> str:
    if state.judge_verdict == JudgeVerdict.PASS:
        return "done"
    elif state.judge_verdict == JudgeVerdict.FAIL_RETRY:
        return "retry"
    else:
        return "done"


def marketing_judge_decision(state: AgentState) -> str:
    """Separate retry-routing function for the marketing path, so a marketing retry
    goes back to marketing_generate, never to the mobility sql_generate node."""
    if state.judge_verdict == JudgeVerdict.PASS:
        return "done"
    elif state.judge_verdict == JudgeVerdict.FAIL_RETRY:
        return "retry"
    else:
        return "done"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", route_request)
    graph.add_node("sql_generate", generate_sql)
    graph.add_node("sql_execute", execute_sql)
    graph.add_node("sql_explain", explain_result)
    graph.add_node("judge", judge_answer)
    graph.add_node("marketing_generate", generate_marketing_sql)
    graph.add_node("marketing_execute", execute_marketing_sql)
    graph.add_node("marketing_explain", explain_marketing_result)
    graph.add_node("marketing_judge", judge_answer)
    graph.add_node("etl_review", review_etl_code)
    graph.add_node("finalize_etl", finalize_etl)
    graph.add_node("reject", finalize_reject)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "sql_generate": "sql_generate",
            "marketing_generate": "marketing_generate",
            "etl_review": "etl_review",
            "reject": "reject",
        },
    )

    graph.add_edge("sql_generate", "sql_execute")
    graph.add_edge("sql_execute", "sql_explain")
    graph.add_edge("sql_explain", "judge")
    graph.add_conditional_edges(
        "judge",
        judge_decision,
        {"retry": "sql_generate", "done": END},
    )

    graph.add_edge("marketing_generate", "marketing_execute")
    graph.add_edge("marketing_execute", "marketing_explain")
    graph.add_edge("marketing_explain", "marketing_judge")
    graph.add_conditional_edges(
        "marketing_judge",
        marketing_judge_decision,
        {"retry": "marketing_generate", "done": END},
    )

    graph.add_edge("etl_review", "finalize_etl")
    graph.add_edge("finalize_etl", END)
    graph.add_edge("reject", END)

    return graph.compile()
