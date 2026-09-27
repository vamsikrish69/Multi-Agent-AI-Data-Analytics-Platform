from ai_data_agent.db.base import DatabaseAdapter
from ai_data_agent.db.postgres_adapter import PostgresAdapter
from ai_data_agent.db.snowflake_adapter import SnowflakeAdapter

print("PostgresAdapter is a valid DatabaseAdapter:", issubclass(PostgresAdapter, DatabaseAdapter))
print("SnowflakeAdapter is a valid DatabaseAdapter:", issubclass(SnowflakeAdapter, DatabaseAdapter))

for method in ("execute_query", "get_schema_summary", "close"):
    pg_has_it = hasattr(PostgresAdapter, method)
    sf_has_it = hasattr(SnowflakeAdapter, method)
    print(f"{method}: Postgres={pg_has_it}, Snowflake={sf_has_it}")
