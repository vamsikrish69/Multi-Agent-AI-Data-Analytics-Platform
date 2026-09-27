import time
from typing import Any

import structlog

logger = structlog.get_logger()


def traced_invoke(app: Any, initial_state: Any) -> dict:
    """Run the graph once, timing it and emitting one consolidated trace record.

    This wraps app.invoke() so every request produces a single, structured
    summary log line - correlation ID, route, SQL, validation/execution
    status, judge decision, retry count, and latency - in one place,
    instead of scattered across each agent's individual log lines.
    """
    start_time = time.perf_counter()
    result = app.invoke(initial_state)
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 1)

    trace = {
        "correlation_id": result.get("correlation_id"),
        "route": result.get("route"),
        "validation_error": result.get("validation_error"),
        "row_count": len(result["query_result"]) if result.get("query_result") is not None else None,
        "judge_verdict": result.get("judge_verdict"),
        "retry_count": result.get("retry_count"),
        "latency_ms": elapsed_ms,
    }

    logger.info("request_trace", **trace)

    return result
