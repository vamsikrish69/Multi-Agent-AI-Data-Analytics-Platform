from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ai_data_agent.db.base import DatabaseAdapter


class PostgresAdapter(DatabaseAdapter):
    """PostgreSQL implementation of the DatabaseAdapter contract."""

    def __init__(self, database_url: str, query_timeout_seconds: int = 10):
        self._engine: Engine = create_engine(
            database_url,
            connect_args={"options": f"-c statement_timeout={query_timeout_seconds * 1000}"},
        )

    def execute_query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with self._engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]

    def get_schema_summary(self) -> str:
        query = """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """
        rows = self.execute_query(query)

        summary_by_table: dict[str, list[str]] = {}
        for row in rows:
            table = row["table_name"]
            summary_by_table.setdefault(table, []).append(f"{row['column_name']} ({row['data_type']})")

        lines = []
        for table, columns in summary_by_table.items():
            lines.append(f"{table}: " + ", ".join(columns))
        return "\n".join(lines)

    def close(self) -> None:
        self._engine.dispose()