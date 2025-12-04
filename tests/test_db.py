import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect

from app.database import engine, Session as DBSession
from app import models


def test_connection():
    inspector = inspect(engine)
    assert "vehicles" in inspector.get_table_names()


def test_schema():
    inspector = inspect(engine)
    cols = {col['name']: col for col in inspector.get_columns("vehicles")}
    col_names = set(cols.keys())
    
    # column names
    expected = {
        "vin", "manufacturer_name", "description", "horse_power",
        "model_name", "model_year", "purchase_price", "fuel_type"
    }
    assert expected <= col_names
    
    # column types
    # VIN: max length 17 (database allows up to 17 chars)
    # Minimum length 5 is enforced by Pydantic schema validation, not database
    assert cols['vin']['type'].length == 17
    assert 'NUMERIC' in str(cols['purchase_price']['type']).upper()
    assert 'INTEGER' in str(cols['horse_power']['type']).upper()
    assert cols['vin']['nullable'] is False
    assert cols['description']['nullable'] is True


def test_constraints():
    db = DBSession()
    try:
        # unique constraint (case-insensitive)
        v1 = models.Vehicle(
            vin="TEST1234567890123",
            manufacturer_name="Toyota",
            description="Test",
            horse_power=180,
            model_name="Camry",
            model_year=2023,
            purchase_price=25000.00,
            fuel_type="Gasoline"
        )
        db.add(v1)
        db.commit()
        
        v2 = models.Vehicle(
            vin="test1234567890123",
            manufacturer_name="Honda",
            description="Duplicate",
            horse_power=200,
            model_name="Accord",
            model_year=2024,
            purchase_price=30000.00,
            fuel_type="Gasoline"
        )
        db.add(v2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
        
        # VIN length constraint
        vehicle = models.Vehicle(
            vin="A" * 18,
            manufacturer_name="Toyota",
            description="Test",
            horse_power=180,
            model_name="Camry",
            model_year=2023,
            purchase_price=25000.00,
            fuel_type="Gasoline"
        )
        db.add(vehicle)
        with pytest.raises(Exception):
            db.commit()
        db.rollback()
    finally:
        db.query(models.Vehicle).filter(models.Vehicle.vin == "test1234567890123").delete()
        db.commit()
        db.close()

