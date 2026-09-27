import structlog

from ai_data_agent.agents.state import AgentState
from ai_data_agent.config.settings import get_settings
from ai_data_agent.db.postgres_adapter import PostgresAdapter
from ai_data_agent.llm.provider import get_chat_model
from ai_data_agent.security.sql_validator import SQLValidationError, validate_sql

logger = structlog.get_logger()

SQL_GENERATION_PROMPT_TEMPLATE = """You are a PostgreSQL expert. Given the database schema below, write a single SELECT query that answers the user's question.

Rules:
- Only output the raw SQL query, nothing else. No explanation, no markdown code fences.
- Only use SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, or ALTER.
- Only use the tables and columns shown in the schema below.

Schema:
{schema}

Question: {question}

SQL query:"""

EXPLANATION_PROMPT_TEMPLATE = """You are a data analyst explaining a query result to a non-technical business user.

Original question: {question}
SQL query used: {sql}
Query result (raw data): {result}

IMPORTANT: if the SQL query has a LIMIT clause but returns a small number of rows (like a single COUNT result), the LIMIT is irrelevant and does NOT mean the true count could be higher. A LIMIT only caps how many rows come back - it does not affect the accuracy of an aggregate like COUNT, SUM, or AVG. Do not mention the LIMIT unless the result actually contains as many rows as the limit allows.

Write a short, clear, plain-English answer to the original question, based ONLY on the result data above. Do not invent numbers that are not in the result. If the result is empty, say so clearly."""


def generate_sql(state: AgentState) -> AgentState:
    """Generate a candidate SQL query for the user's question, then validate it."""
    settings = get_settings()
    model = get_chat_model()

    adapter = PostgresAdapter(settings.database_url, settings.query_timeout_seconds)
    schema = adapter.get_schema_summary()
    adapter.close()

    prompt = SQL_GENERATION_PROMPT_TEMPLATE.format(schema=schema, question=state.user_question)
    response = model.invoke(prompt)

    raw_sql = str(response.content).strip()
    raw_sql = raw_sql.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()

    state.generated_sql = raw_sql

    try:
        state.validated_sql = validate_sql(raw_sql, max_result_rows=settings.max_result_rows)
        state.validation_error = None
    except SQLValidationError as e:
        state.validated_sql = None
        state.validation_error = str(e)

    logger.info(
        "sql_generated",
        correlation_id=state.correlation_id,
        generated_sql=state.generated_sql,
        validation_error=state.validation_error,
    )

    return state


def execute_sql(state: AgentState) -> AgentState:
    """Execute the validated SQL using the read-only database role."""
    if state.validated_sql is None:
        logger.warning("execute_sql_skipped_no_validated_sql", correlation_id=state.correlation_id)
        return state

    settings = get_settings()
    adapter = PostgresAdapter(settings.readonly_database_url, settings.query_timeout_seconds)

    try:
        state.query_result = adapter.execute_query(state.validated_sql)
    except Exception as e:
        state.validation_error = f"Execution failed: {e}"
        state.query_result = None
    finally:
        adapter.close()

    logger.info(
        "sql_executed",
        correlation_id=state.correlation_id,
        row_count=len(state.query_result) if state.query_result else 0,
    )

    return state


def explain_result(state: AgentState) -> AgentState:
    """Ask the LLM to explain the query result in plain business language."""
    if state.query_result is None:
        state.business_explanation = f"I could not answer this question: {state.validation_error or 'no result was produced.'}"
        return state

    model = get_chat_model()
    prompt = EXPLANATION_PROMPT_TEMPLATE.format(
        question=state.user_question,
        sql=state.validated_sql,
        result=state.query_result,
    )
    response = model.invoke(prompt)
    state.business_explanation = str(response.content).strip()

    logger.info(
        "result_explained",
        correlation_id=state.correlation_id,
        business_explanation=state.business_explanation,
    )

    return state
