import pytest
from sqlalchemy import inspect
from app.database import engine
from app.models import Vehicle


def test_database_connection():
    """
    test connection and inspect to PostgreSQL tables.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "vehicles" in tables


def test_vehicle_columns_match():
    """
    test SQLAlchemy model columns match the database schema.
    """
    inspector = inspect(engine)

    cols = inspector.get_columns("vehicles")
    col_names = {col['name'] for col in cols}

    expected = {
        "vin",
        "manufacturer_name",
        "description",
        "horse_power",
        "model_name",
        "model_year",
        "purchase_price",
        "fuel_type",
    }

    assert expected <= col_names  # expected = subset of real columns
