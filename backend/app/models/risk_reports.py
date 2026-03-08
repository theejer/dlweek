"""Risk report data-access module.

Risk engine writes computed results here; trips/analysis routes read for clients.
"""

import json
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.extensions import get_db_engine


def _is_uuid(value: str) -> bool:
    try:
        UUID(str(value))
        return True
    except (ValueError, TypeError):
        return False


def _is_missing_table_error(exc: Exception, table_name: str) -> bool:
    message = str(exc).lower()
    return f"no such table: {table_name}" in message or f'relation "{table_name}" does not exist' in message


def _is_sqlite_engine(engine) -> bool:
    return getattr(getattr(engine, "dialect", None), "name", "") == "sqlite"


def _ensure_risk_reports_table_for_sqlite() -> None:
    engine = get_db_engine()
    if not _is_sqlite_engine(engine):
        return

    create_table_query = text(
        """
        CREATE TABLE IF NOT EXISTS risk_reports (
            id TEXT PRIMARY KEY,
            trip_id TEXT NOT NULL,
            report TEXT NOT NULL,
            summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    with engine.begin() as connection:
        connection.execute(create_table_query)


def save_risk_report(trip_id: str, report: dict) -> dict:
    """Persist risk output (location + connectivity risk summaries)."""
    if not _is_uuid(trip_id):
        return {}

    engine = get_db_engine()
    if _is_sqlite_engine(engine):
        query = text(
            """
            INSERT INTO risk_reports (id, trip_id, report, summary)
            VALUES (:id, :trip_id, :report, :summary)
            RETURNING *
            """
        )
    else:
        query = text(
            """
            INSERT INTO risk_reports (trip_id, report, summary)
            VALUES (:trip_id, CAST(:report AS jsonb), :summary)
            RETURNING *
            """
        )
    params = {
        "trip_id": trip_id,
        "report": json.dumps(report),
        "summary": report.get("summary"),
    }
    if _is_sqlite_engine(engine):
        params["id"] = str(uuid4())

    try:
        with engine.begin() as connection:
            result = connection.execute(query, params)
            row = result.mappings().first()
    except (ProgrammingError, OperationalError) as exc:
        if _is_missing_table_error(exc, "risk_reports"):
            _ensure_risk_reports_table_for_sqlite()
            try:
                with engine.begin() as connection:
                    result = connection.execute(query, params)
                    row = result.mappings().first()
            except (ProgrammingError, OperationalError) as retry_exc:
                if _is_missing_table_error(retry_exc, "risk_reports"):
                    raise RuntimeError("risk_reports table is missing") from retry_exc
                raise
        else:
            raise
    row_dict = dict(row) if row else {}
    if isinstance(row_dict.get("report"), str):
        try:
            row_dict["report"] = json.loads(row_dict["report"])
        except Exception:
            pass
    return row_dict


def latest_risk_report(trip_id: str) -> dict:
    """Fetch latest risk report used by mobile PREVENTION views."""
    if not _is_uuid(trip_id):
        return {}

    query = text(
        """
        SELECT *
        FROM risk_reports
        WHERE trip_id = :trip_id
        ORDER BY created_at DESC
        LIMIT 1
        """
    )
    engine = get_db_engine()
    try:
        with engine.begin() as connection:
            result = connection.execute(query, {"trip_id": trip_id})
            row = result.mappings().first()
    except (ProgrammingError, OperationalError) as exc:
        if _is_missing_table_error(exc, "risk_reports"):
            _ensure_risk_reports_table_for_sqlite()
            try:
                with engine.begin() as connection:
                    result = connection.execute(query, {"trip_id": trip_id})
                    row = result.mappings().first()
            except (ProgrammingError, OperationalError) as retry_exc:
                if _is_missing_table_error(retry_exc, "risk_reports"):
                    raise RuntimeError("risk_reports table is missing") from retry_exc
                raise
        else:
            raise
    row_dict = dict(row) if row else {}
    if isinstance(row_dict.get("report"), str):
        try:
            row_dict["report"] = json.loads(row_dict["report"])
        except Exception:
            pass
    return row_dict
