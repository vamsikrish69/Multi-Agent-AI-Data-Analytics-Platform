from ai_data_agent.config.settings import get_settings
from ai_data_agent.db.postgres_adapter import PostgresAdapter

settings = get_settings()
adapter = PostgresAdapter(settings.database_url, settings.query_timeout_seconds)

print("--- Schema summary ---")
print(adapter.get_schema_summary())

print("\n--- Sample query ---")
rows = adapter.execute_query("SELECT full_name, email FROM customers;")
for row in rows:
    print(row)

adapter.close()