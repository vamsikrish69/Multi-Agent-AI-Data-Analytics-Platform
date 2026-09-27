import structlog
from langgraph.graph import StateGraph, END

from ai_data_agent.agents.etl_analyst import review_etl_code
from ai_data_agent.agents.judge import judge_answer
from ai_data_agent.agents.router import route_request
from ai_data_agent.agents.sql_analyst import execute_sql, explain_result, generate_sql
from ai_data_agent.agents.state import AgentState, JudgeVerdict, RouteType

logger = structlog.get_logger()


def finalize_etl(state: AgentState) -> AgentState:
    """Set the final answer from the ETL review notes."""
    state.final_answer = state.etl_review_notes
    return state


def finalize_reject(state: AgentState) -> AgentState:
    """Set the final answer for an unsupported/rejected request."""
    state.final_answer = state.rejection_reason or "This request could not be processed."
    return state


def route_decision(state: AgentState) -> str:
    """Read state.route and tell LangGraph which node to go to next."""
    if state.route == RouteType.SQL_ANALYST:
        return "sql_generate"
    elif state.route == RouteType.ETL_ANALYST:
        return "etl_review"
    else:
        return "reject"


def judge_decision(state: AgentState) -> str:
    """Read state.judge_verdict and tell LangGraph whether to retry, stop, or finish."""
    if state.judge_verdict == JudgeVerdict.PASS:
        return "done"
    elif state.judge_verdict == JudgeVerdict.FAIL_RETRY:
        return "retry"
    else:
        return "done"


def build_graph():
    """Assemble the full multi-agent LangGraph."""
    graph = StateGraph(AgentState)

    graph.add_node("router", route_request)
    graph.add_node("sql_generate", generate_sql)
    graph.add_node("sql_execute", execute_sql)
    graph.add_node("sql_explain", explain_result)
    graph.add_node("judge", judge_answer)
    graph.add_node("etl_review", review_etl_code)
    graph.add_node("finalize_etl", finalize_etl)
    graph.add_node("reject", finalize_reject)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "sql_generate": "sql_generate",
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
        {
            "retry": "sql_generate",
            "done": END,
        },
    )

    graph.add_edge("etl_review", "finalize_etl")
    graph.add_edge("finalize_etl", END)
    graph.add_edge("reject", END)

    return graph.compile()
