from typing import Any

import snowflake.connector

from ai_data_agent.db.base import DatabaseAdapter


class SnowflakeAdapter(DatabaseAdapter):
    """Snowflake implementation of the DatabaseAdapter contract.

    Fulfills the exact same contract as PostgresAdapter (Milestone 2),
    so agent code that only depends on DatabaseAdapter never needs to
    change when switching between Postgres and Snowflake.
    """

    def __init__(
        self,
        account: str,
        user: str,
        password: str,
        warehouse: str,
        database: str,
        schema: str = "PUBLIC",
        query_timeout_seconds: int = 10,
    ):
        self._connection = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema,
            network_timeout=query_timeout_seconds,
        )

    def execute_query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        cursor = self._connection.cursor(snowflake.connector.DictCursor)
        try:
            cursor.execute(sql, params or {})
            return cursor.fetchall()
        finally:
            cursor.close()

    def get_schema_summary(self) -> str:
        query = """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'PUBLIC'
            ORDER BY table_name, ordinal_position
        """
        rows = self.execute_query(query)

        summary_by_table: dict[str, list[str]] = {}
        for row in rows:
            table = row["TABLE_NAME"]
            summary_by_table.setdefault(table, []).append(f"{row['COLUMN_NAME']} ({row['DATA_TYPE']})")

        lines = []
        for table, columns in summary_by_table.items():
            lines.append(f"{table}: " + ", ".join(columns))
        return "\n".join(lines)

    def close(self) -> None:
        self._connection.close()
