import pytest

from ai_data_agent.security.sql_validator import MOBILITY_ALLOWED_TABLES, SQLValidationError, validate_sql


def test_valid_select_is_allowed():
    result = validate_sql("SELECT full_name FROM customers", MOBILITY_ALLOWED_TABLES, max_result_rows=500)
    assert "SELECT" in result
    assert "LIMIT" in result


def test_delete_is_blocked():
    with pytest.raises(SQLValidationError):
        validate_sql("DELETE FROM customers WHERE customer_id = 1", MOBILITY_ALLOWED_TABLES)


def test_drop_table_is_blocked():
    with pytest.raises(SQLValidationError):
        validate_sql("DROP TABLE customers", MOBILITY_ALLOWED_TABLES)


def test_update_is_blocked():
    with pytest.raises(SQLValidationError):
        validate_sql("UPDATE customers SET full_name = 'x'", MOBILITY_ALLOWED_TABLES)


def test_unapproved_table_is_blocked():
    with pytest.raises(SQLValidationError):
        validate_sql("SELECT * FROM pg_shadow", MOBILITY_ALLOWED_TABLES)


def test_multiple_statements_are_blocked():
    with pytest.raises(SQLValidationError):
        validate_sql("SELECT * FROM customers; DROP TABLE customers;", MOBILITY_ALLOWED_TABLES)


def test_existing_limit_is_capped_not_exceeded():
    result = validate_sql("SELECT * FROM customers LIMIT 99999", MOBILITY_ALLOWED_TABLES, max_result_rows=500)
    assert "LIMIT 500" in result


def test_reasonable_limit_is_preserved():
    result = validate_sql("SELECT * FROM customers LIMIT 10", MOBILITY_ALLOWED_TABLES, max_result_rows=500)
    assert "LIMIT 10" in result


def test_marketing_table_is_blocked_under_mobility_scope():
    """A marketing table must never be reachable through the mobility validator scope."""
    with pytest.raises(SQLValidationError):
        validate_sql("SELECT * FROM fct_campaign_measurement", MOBILITY_ALLOWED_TABLES)
