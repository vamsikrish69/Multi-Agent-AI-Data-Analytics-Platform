from ai_data_agent.config.settings import get_settings
from ai_data_agent.db.base import DatabaseAdapter


class UnsupportedDatabaseError(Exception):
    """Raised when DB_PROVIDER in settings doesn't match a known provider."""


def get_database_adapter(readonly: bool = False) -> DatabaseAdapter:
    """Return a DatabaseAdapter instance based on the configured DB_PROVIDER.

    Every agent should call this function rather than importing a
    specific adapter (Postgres, Snowflake) directly. Swapping database
    providers later means changing .env, not agent code.
    """
    settings = get_settings()
    provider = getattr(settings, "db_provider", "postgres")

    if provider == "postgres":
        from ai_data_agent.db.postgres_adapter import PostgresAdapter

        url = settings.readonly_database_url if readonly else settings.database_url
        return PostgresAdapter(url, settings.query_timeout_seconds)

    if provider == "snowflake":
        from ai_data_agent.db.snowflake_adapter import SnowflakeAdapter

        return SnowflakeAdapter(
            account=settings.snowflake_account,
            user=settings.snowflake_user,
            password=settings.snowflake_password,
            warehouse=settings.snowflake_warehouse,
            database=settings.snowflake_database,
            query_timeout_seconds=settings.query_timeout_seconds,
        )

    raise UnsupportedDatabaseError(
        f"Unknown DB_PROVIDER '{provider}'. Supported providers: postgres, snowflake"
    )
