import structlog

from ai_data_agent.agents.state import AgentState
from ai_data_agent.config.settings import get_settings
from ai_data_agent.db.postgres_adapter import PostgresAdapter
from ai_data_agent.llm.provider import get_chat_model
from ai_data_agent.security.sql_validator import MARKETING_ALLOWED_TABLES, SQLValidationError, validate_sql

logger = structlog.get_logger()

MARKETING_SQL_GENERATION_PROMPT_TEMPLATE = """You are a marketing analytics expert writing PostgreSQL queries.

Schema:
{schema}

IMPORTANT domain knowledge:
- This data uses three attribution models: first_touch, last_touch, and linear.
- Different attribution models can give very different numbers for the same question,
  since they credit different touchpoints for a conversion.
- If the user's question does not specify an attribution model, default to using the
  linear_* columns, since linear attribution is the most balanced default.
- ROAS (Return on Ad Spend) columns are named first_touch_roas, last_touch_roas, linear_roas.

Rules:
- Only output the raw SQL query, nothing else. No explanation, no markdown code fences.
- Only use SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, or ALTER.
- Only use the tables and columns shown in the schema below.

Question: {question}

SQL query:"""

MARKETING_EXPLANATION_PROMPT_TEMPLATE = """You are a marketing analyst explaining a query result to a
non-technical stakeholder.

MANDATORY: your answer MUST include the words "linear attribution", "first-touch attribution", or
"last-touch attribution" - whichever model the SQL query actually used - if the result involves
conversions, revenue, or ROAS. A reader must never be able to mistake this for the single unambiguous
answer, since a different model would give a different number.

MANDATORY: express ROAS as a ratio, for example "23x return" or "a 23:1 ratio". Never write it as a
dollar amount like "$23.00" - ROAS is not currency.

Original question: {question}
SQL query used: {sql}
Query result (raw data): {result}

Write a short, clear, plain-English answer based ONLY on the result data above. Do not invent numbers
that are not in the result. If the result is empty, say so clearly.

Before you finish, re-read your own answer and confirm it satisfies both MANDATORY rules above. If it
does not, rewrite it so that it does."""


def generate_marketing_sql(state: AgentState) -> AgentState:
    settings = get_settings()
    model = get_chat_model()

    adapter = PostgresAdapter(settings.marketing_database_url, settings.query_timeout_seconds)
    schema = adapter.get_schema_summary()
    adapter.close()

    prompt = MARKETING_SQL_GENERATION_PROMPT_TEMPLATE.format(schema=schema, question=state.user_question)
    response = model.invoke(prompt)

    raw_sql = str(response.content).strip()
    raw_sql = raw_sql.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()
    state.generated_sql = raw_sql

    try:
        state.validated_sql = validate_sql(raw_sql, MARKETING_ALLOWED_TABLES, max_result_rows=settings.max_result_rows)
        state.validation_error = None
    except SQLValidationError as e:
        state.validated_sql = None
        state.validation_error = str(e)

    logger.info("marketing_sql_generated", correlation_id=state.correlation_id,
        generated_sql=state.generated_sql, validation_error=state.validation_error)
    return state


def execute_marketing_sql(state: AgentState) -> AgentState:
    if state.validated_sql is None:
        logger.warning("execute_marketing_sql_skipped_no_validated_sql", correlation_id=state.correlation_id)
        return state

    settings = get_settings()
    adapter = PostgresAdapter(settings.marketing_readonly_database_url, settings.query_timeout_seconds)
    try:
        state.query_result = adapter.execute_query(state.validated_sql)
    except Exception as e:
        state.validation_error = f"Execution failed: {e}"
        state.query_result = None
    finally:
        adapter.close()

    logger.info("marketing_sql_executed", correlation_id=state.correlation_id,
        row_count=len(state.query_result) if state.query_result else 0)
    return state


def explain_marketing_result(state: AgentState) -> AgentState:
    if state.query_result is None:
        state.business_explanation = f"I could not answer this question: {state.validation_error or 'no result was produced.'}"
        return state

    model = get_chat_model()
    prompt = MARKETING_EXPLANATION_PROMPT_TEMPLATE.format(question=state.user_question,
        sql=state.validated_sql, result=state.query_result)
    response = model.invoke(prompt)
    state.business_explanation = str(response.content).strip()

    logger.info("marketing_result_explained", correlation_id=state.correlation_id,
        business_explanation=state.business_explanation)
    return state
