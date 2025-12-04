import pytest
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from unittest.mock import patch

from app.database import Session
from app import schemas, crud
from tests.conftest import VehicleTest


@pytest.fixture(scope="function")
def db_session():
    # setup_test_table runs automatically via autouse=True
    db = Session()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def vehicle_create():
    return schemas.VehicleCreate(
        vin="TEST1234567890123",
        manufacturer_name="Toyota",
        description="A reliable sedan",
        horse_power=180,
        model_name="Camry",
        model_year=2023,
        purchase_price=Decimal("25000.00"),
        fuel_type="Gasoline"
    )


@pytest.fixture
def vehicle_update():
    return schemas.VehicleUpdate(
        manufacturer_name="Honda",
        description="An updated description",
        horse_power=200,
        model_name="Accord",
        model_year=2024,
        purchase_price=Decimal("27000.00"),
        fuel_type="Hybrid"
    )


# add_vehicle tests
def test_add(db_session, vehicle_create):
    with patch('app.crud.models.Vehicle', VehicleTest):
        # success
        vehicle = crud.add_vehicle(db_session, vehicle_create)
        assert vehicle.vin == vehicle_create.vin.lower()
        assert vehicle.manufacturer_name == vehicle_create.manufacturer_name
        
        # VIN normalized to lowercase
        vehicle_create.vin = "UPPERCASE12345678"
        vehicle = crud.add_vehicle(db_session, vehicle_create)
        assert vehicle.vin == "uppercase12345678"
        
        # duplicate VIN raises IntegrityError
        vehicle_create.vin = "DUPLICATE12345678"
        crud.add_vehicle(db_session, vehicle_create)
        with pytest.raises(IntegrityError):
            crud.add_vehicle(db_session, vehicle_create)


# get_vehicle tests
def test_get(db_session, vehicle_create):
    with patch('app.crud.models.Vehicle', VehicleTest):
        # success
        created = crud.add_vehicle(db_session, vehicle_create)
        vehicle = crud.get_vehicle(db_session, created.vin)
        assert vehicle is not None
        assert vehicle.vin == created.vin
        
        # not found
        assert crud.get_vehicle(db_session, "NONEXISTENT") is None
        
        # case insensitive
        vehicle_create.vin = "CASETEST123456789"
        created = crud.add_vehicle(db_session, vehicle_create)
        vehicle = crud.get_vehicle(db_session, created.vin.upper())
        assert vehicle is not None
        assert vehicle.vin == created.vin


# get_all_vehicles tests
def test_get_all(db_session):
    with patch('app.crud.models.Vehicle', VehicleTest):
        # empty
        assert crud.get_all_vehicles(db_session) == []
        
        # ordered by manufacturer_name
        v1 = schemas.VehicleCreate(
            vin="VIN00123456789012",
            manufacturer_name="Toyota",
            horse_power=150,
            model_name="Model1",
            model_year=2020,
            purchase_price=Decimal("20000.00"),
            fuel_type="Gasoline"
        )
        v2 = schemas.VehicleCreate(
            vin="VIN00234567890123",
            manufacturer_name="Honda",
            horse_power=160,
            model_name="Model2",
            model_year=2021,
            purchase_price=Decimal("21000.00"),
            fuel_type="Gasoline"
        )
        crud.add_vehicle(db_session, v1)
        crud.add_vehicle(db_session, v2)
        
        vehicles = crud.get_all_vehicles(db_session)
        assert len(vehicles) == 2
        assert vehicles[0].manufacturer_name == "Honda"
        assert vehicles[1].manufacturer_name == "Toyota"


# update_vehicle tests
def test_update(db_session, vehicle_create, vehicle_update):
    with patch('app.crud.models.Vehicle', VehicleTest):
        # success
        created = crud.add_vehicle(db_session, vehicle_create)
        updated = crud.update_vehicle(db_session, created.vin, vehicle_update)
        assert updated.manufacturer_name == vehicle_update.manufacturer_name
        assert updated.vin == created.vin
        
        # not found
        assert crud.update_vehicle(db_session, "NONEXISTENT", vehicle_update) is None
        
        # full replacement
        vehicle_create.vin = "UPDATE12345678901"
        created = crud.add_vehicle(db_session, vehicle_create)
        vehicle_update.description = None
        updated = crud.update_vehicle(db_session, created.vin, vehicle_update)
        assert updated.description is None


# delete_vehicle tests
def test_delete(db_session, vehicle_create):
    with patch('app.crud.models.Vehicle', VehicleTest):
        # success
        created = crud.add_vehicle(db_session, vehicle_create)
        assert crud.delete_vehicle(db_session, created.vin) is True
        assert crud.get_vehicle(db_session, created.vin) is None
        
        # not found
        assert crud.delete_vehicle(db_session, "NONEXISTENT") is False
        
        # case insensitive
        vehicle_create.vin = "DELETE12345678901"
        created = crud.add_vehicle(db_session, vehicle_create)
        assert crud.delete_vehicle(db_session, created.vin.upper()) is True
        assert crud.get_vehicle(db_session, created.vin) is None
