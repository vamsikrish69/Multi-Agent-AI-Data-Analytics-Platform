import pytest

from ai_data_agent.security.sql_validator import SQLValidationError, validate_sql


def test_valid_select_is_allowed():
    result = validate_sql("SELECT full_name FROM customers", max_result_rows=500)
    assert "SELECT" in result
    assert "LIMIT" in result


def test_delete_is_blocked():
    with pytest.raises(SQLValidationError):
        validate_sql("DELETE FROM customers WHERE customer_id = 1")


def test_drop_table_is_blocked():
    with pytest.raises(SQLValidationError):
        validate_sql("DROP TABLE customers")


def test_update_is_blocked():
    with pytest.raises(SQLValidationError):
        validate_sql("UPDATE customers SET full_name = 'x'")


def test_unapproved_table_is_blocked():
    with pytest.raises(SQLValidationError):
        validate_sql("SELECT * FROM pg_shadow")


def test_multiple_statements_are_blocked():
    with pytest.raises(SQLValidationError):
        validate_sql("SELECT * FROM customers; DROP TABLE customers;")


def test_existing_limit_is_capped_not_exceeded():
    result = validate_sql("SELECT * FROM customers LIMIT 99999", max_result_rows=500)
    assert "LIMIT 500" in result


def test_reasonable_limit_is_preserved():
    result = validate_sql("SELECT * FROM customers LIMIT 10", max_result_rows=500)
    assert "LIMIT 10" in result
