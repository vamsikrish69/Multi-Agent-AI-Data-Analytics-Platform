from ai_data_agent.security.sql_validator import validate_sql, SQLValidationError

print("--- Safe query ---")
safe_sql = "SELECT full_name, email FROM customers"
print(validate_sql(safe_sql, max_result_rows=500))

print("\n--- Unsafe query (DELETE) ---")
try:
    validate_sql("DELETE FROM customers WHERE customer_id = 1")
except SQLValidationError as e:
    print(f"Correctly blocked: {e}")

print("\n--- Unsafe query (unapproved table) ---")
try:
    validate_sql("SELECT * FROM pg_shadow")
except SQLValidationError as e:
    print(f"Correctly blocked: {e}")