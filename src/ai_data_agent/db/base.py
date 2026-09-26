from abc import ABC, abstractmethod
from typing import Any


class DatabaseAdapter(ABC):
    """Abstract contract every database backend must implement.

    Any concrete adapter (Postgres now, Snowflake later) must fulfill
    this interface so the rest of the app never needs to know which
    database engine is actually running underneath.
    """

    @abstractmethod
    def execute_query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Run a read-only SQL query and return rows as a list of dicts."""
        raise NotImplementedError

    @abstractmethod
    def get_schema_summary(self) -> str:
        """Return a human/LLM-readable summary of available tables and columns."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Release any held database connections/resources."""
        raise NotImplementedError