"""Itinerary storage access.

Itinerary analysis routes and parser services persist normalized itinerary JSON here.
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


def _ensure_itineraries_table_for_sqlite() -> None:
    engine = get_db_engine()
    if engine.dialect.name != "sqlite":
        return

    create_table_query = text(
        """
        CREATE TABLE IF NOT EXISTS itineraries (
            id TEXT PRIMARY KEY,
            trip_id TEXT NOT NULL UNIQUE,
            itinerary_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    with engine.begin() as connection:
        connection.execute(create_table_query)


def upsert_itinerary(trip_id: str, itinerary_json: dict) -> dict:
    """Store latest itinerary snapshot for a trip."""
    if not _is_uuid(trip_id):
        return {}

    engine = get_db_engine()
    if engine.dialect.name == "sqlite":
        query = text(
            """
            INSERT INTO itineraries (id, trip_id, itinerary_json)
            VALUES (:id, :trip_id, :itinerary_json)
            ON CONFLICT (trip_id)
            DO UPDATE SET itinerary_json = excluded.itinerary_json
            RETURNING *
            """
        )
    else:
        query = text(
            """
            INSERT INTO itineraries (id, trip_id, itinerary_json)
            VALUES (:id, :trip_id, CAST(:itinerary_json AS jsonb))
            ON CONFLICT (trip_id)
            DO UPDATE SET itinerary_json = EXCLUDED.itinerary_json
            RETURNING *
            """
        )

    params = {
        "id": str(uuid4()),
        "trip_id": trip_id,
        "itinerary_json": json.dumps(itinerary_json),
    }

    try:
        with engine.begin() as connection:
            result = connection.execute(query, params)
            row = result.mappings().first()
    except (ProgrammingError, OperationalError) as exc:
        if not _is_missing_table_error(exc, "itineraries"):
            raise
        _ensure_itineraries_table_for_sqlite()
        with engine.begin() as connection:
            result = connection.execute(query, params)
            row = result.mappings().first()
    return dict(row) if row else {}


def get_itinerary(trip_id: str) -> dict:
    """Fetch itinerary consumed by risk engine and heartbeat monitor."""
    if not _is_uuid(trip_id):
        return {}

    query = text("SELECT * FROM itineraries WHERE trip_id = :trip_id LIMIT 1")
    engine = get_db_engine()
    try:
        with engine.begin() as connection:
            result = connection.execute(query, {"trip_id": trip_id})
            row = result.mappings().first()
    except (ProgrammingError, OperationalError) as exc:
        if not _is_missing_table_error(exc, "itineraries"):
            raise
        _ensure_itineraries_table_for_sqlite()
        with engine.begin() as connection:
            result = connection.execute(query, {"trip_id": trip_id})
            row = result.mappings().first()
    return dict(row) if row else {}
