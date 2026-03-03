"""Risk report data-access module.

Risk engine writes computed results here; trips/analysis routes read for clients.
"""

import json
from uuid import UUID

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


def save_risk_report(trip_id: str, report: dict) -> dict:
    """Persist risk output (location + connectivity risk summaries)."""
    if not _is_uuid(trip_id):
        return {}

    query = text(
        """
        INSERT INTO risk_reports (trip_id, report, summary)
        VALUES (:trip_id, CAST(:report AS jsonb), :summary)
        RETURNING *
        """
    )
    try:
        with get_db_engine().begin() as connection:
            result = connection.execute(
                query,
                {
                    "trip_id": trip_id,
                    "report": json.dumps(report),
                    "summary": report.get("summary"),
                },
            )
            row = result.mappings().first()
    except (ProgrammingError, OperationalError) as exc:
        if _is_missing_table_error(exc, "risk_reports"):
            raise RuntimeError("risk_reports table is missing") from exc
        raise
    return dict(row) if row else {}


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
    try:
        with get_db_engine().begin() as connection:
            result = connection.execute(query, {"trip_id": trip_id})
            row = result.mappings().first()
    except (ProgrammingError, OperationalError) as exc:
        if _is_missing_table_error(exc, "risk_reports"):
            raise RuntimeError("risk_reports table is missing") from exc
        raise
    return dict(row) if row else {}
