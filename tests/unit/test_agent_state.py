import pytest
from pydantic import ValidationError

from ai_data_agent.agents.state import AgentState, JudgeVerdict, RouteType


def test_minimal_state_creation():
    state = AgentState(user_question="test?", correlation_id="abc-123")
    assert state.user_question == "test?"
    assert state.route is None
    assert state.retry_count == 0


def test_route_assignment_accepts_valid_enum():
    state = AgentState(user_question="test?", correlation_id="abc-123")
    state.route = RouteType.SQL_ANALYST
    assert state.route == "sql_analyst"


def test_invalid_route_assignment_is_rejected():
    state = AgentState(user_question="test?", correlation_id="abc-123")
    with pytest.raises(ValidationError):
        state.route = "not_a_real_route"


def test_negative_retry_count_is_rejected():
    with pytest.raises(ValidationError):
        AgentState(user_question="test?", correlation_id="abc-123", retry_count=-1)


def test_judge_verdict_assignment():
    state = AgentState(user_question="test?", correlation_id="abc-123")
    state.judge_verdict = JudgeVerdict.FAIL_RETRY
    assert state.judge_verdict == "fail_retry"
