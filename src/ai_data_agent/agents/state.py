from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class RouteType(str, Enum):
    """Which specialist agent should handle this request."""

    SQL_ANALYST = "sql_analyst"
    ETL_ANALYST = "etl_analyst"
    UNSUPPORTED = "unsupported"


class JudgeVerdict(str, Enum):
    """The Judge agent's decision on a candidate answer."""

    PASS = "pass"
    FAIL_RETRY = "fail_retry"
    FAIL_FINAL = "fail_final"


class AgentState(BaseModel):
    """The shared state object passed between every node in the LangGraph.

    Starts mostly empty when a request comes in, and gets progressively
    filled in as it moves through Router -> Specialist -> Judge -> Response.
    """

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

    # Input
    user_question: str
    correlation_id: str
    code_to_review: Optional[str] = None

    # Router output
    route: Optional[RouteType] = None
    rejection_reason: Optional[str] = None

    # SQL Analyst output
    generated_sql: Optional[str] = None
    validated_sql: Optional[str] = None
    validation_error: Optional[str] = None
    query_result: Optional[list[dict[str, Any]]] = None
    business_explanation: Optional[str] = None

    # ETL Analyst output
    etl_review_notes: Optional[str] = None

    # Judge output
    judge_verdict: Optional[JudgeVerdict] = None
    judge_feedback: Optional[str] = None

    # Retry control
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=2, ge=0)

    # Final output
    final_answer: Optional[str] = None
