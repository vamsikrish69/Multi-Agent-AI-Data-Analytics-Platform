import sqlglot
from sqlglot import exp


class SQLValidationError(Exception):
    """Raised when generated SQL fails a security or structural check."""


MOBILITY_ALLOWED_TABLES = {
    "customers",
    "drivers",
    "rides",
    "payments",
    "locations",
    "driver_ratings",
}

MARKETING_ALLOWED_TABLES = {
    "fct_campaign_measurement",
    "fct_channel_attribution",
    "fct_attribution_performance",
}


def validate_sql(sql: str, allowed_tables: set[str], max_result_rows: int = 500) -> str:
    """Validate that `sql` is a single, safe, read-only SELECT statement.

    allowed_tables scopes the check to one domain's approved tables, so
    a marketing question can never accidentally (or maliciously) reach
    a mobility table, and vice versa.

    Returns the (possibly rewritten) SQL with a LIMIT enforced.
    Raises SQLValidationError if the query is unsafe in any way.
    """
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except Exception as e:
        raise SQLValidationError(f"SQL failed to parse: {e}") from e

    if len(statements) != 1:
        raise SQLValidationError("Only a single SQL statement is allowed per query.")

    tree = statements[0]
    if tree is None:
        raise SQLValidationError("SQL could not be parsed into a valid statement.")

    if not isinstance(tree, exp.Select):
        raise SQLValidationError(
            f"Only SELECT statements are allowed. Got: {type(tree).__name__}"
        )

    forbidden_types = (
        exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter,
        exp.Create, exp.TruncateTable, exp.Grant,
    )
    for node in tree.walk():
        node_obj = node[0] if isinstance(node, tuple) else node
        if isinstance(node_obj, forbidden_types):
            raise SQLValidationError(
                f"Forbidden operation detected: {type(node_obj).__name__}"
            )

    referenced_tables = {t.name.lower() for t in tree.find_all(exp.Table)}
    unapproved = referenced_tables - allowed_tables
    if unapproved:
        raise SQLValidationError(f"Query references unapproved table(s): {unapproved}")

    existing_limit = tree.args.get("limit")
    if existing_limit is None:
        tree.set("limit", exp.Limit(expression=exp.Literal.number(max_result_rows)))
    else:
        limit_value = int(existing_limit.expression.this)
        if limit_value > max_result_rows:
            tree.set("limit", exp.Limit(expression=exp.Literal.number(max_result_rows)))

    return tree.sql(dialect="postgres")
