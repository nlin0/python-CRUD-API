import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.database import get_db, Session
from tests.conftest import VehicleTest


def override_get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    # Patch models.Vehicle to use VehicleTest for tests
    # setup_test_table runs automatically via autouse=True
    with patch('app.models.Vehicle', VehicleTest):
        with patch('app.crud.models.Vehicle', VehicleTest):
            app.dependency_overrides[get_db] = override_get_db
            with TestClient(app) as test_client:
                yield test_client
            app.dependency_overrides.clear()


@pytest.fixture
def vehicle_data():
    return {
        "vin": "1HGBH41JXMN109186",
        "manufacturer_name": "Toyota",
        "description": "A reliable sedan",
        "horse_power": 180,
        "model_name": "Camry",
        "model_year": 2023,
        "purchase_price": "25000.00",
        "fuel_type": "Gasoline"
    }


# GET /vehicle tests
def test_get_all(client, vehicle_data):
    # empty
    response = client.get("/vehicle")
    assert response.status_code == 200
    assert response.json() == []
    
    # with data
    client.post("/vehicle", json=vehicle_data)
    response = client.get("/vehicle")
    assert response.status_code == 200
    assert len(response.json()) == 1


# GET /vehicle/{vin} tests
def test_get_by_vin(client, vehicle_data):
    # success
    client.post("/vehicle", json=vehicle_data)
    vin = vehicle_data["vin"].lower()
    response = client.get(f"/vehicle/{vin}")
    assert response.status_code == 200
    assert response.json()["vin"] == vin
    
    # not found
    response = client.get("/vehicle/NONEXISTENT")
    assert response.status_code == 404
    
    # case insensitive
    response = client.get(f"/vehicle/{vehicle_data['vin'].upper()}")
    assert response.status_code == 200
    assert response.json()["vin"] == vehicle_data["vin"].lower()


# POST /vehicle tests
def test_create(client, vehicle_data):
    # success
    response = client.post("/vehicle", json=vehicle_data)
    assert response.status_code == 201
    assert response.json()["vin"] == vehicle_data["vin"].lower()
    
    # duplicate VIN
    response = client.post("/vehicle", json=vehicle_data)
    assert response.status_code == 422
    
    # invalid data
    response = client.post("/vehicle", json={"vin": "TEST123"})
    assert response.status_code == 422
    
    # malformed JSON (should return 400 per assignment)
    response = client.post(
        "/vehicle",
        data="not json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    
    # VIN normalized to lowercase
    vehicle_data["vin"] = "UPPERCASE12345678"
    response = client.post("/vehicle", json=vehicle_data)
    assert response.status_code == 201
    assert response.json()["vin"] == "uppercase12345678"
    
    # VIN too short
    vehicle_data["vin"] = "ABC"
    response = client.post("/vehicle", json=vehicle_data)
    assert response.status_code == 422
    
    # VIN too long
    vehicle_data["vin"] = "A" * 18
    response = client.post("/vehicle", json=vehicle_data)
    assert response.status_code == 422


# PUT /vehicle/{vin} tests
def test_update(client, vehicle_data):
    # success
    client.post("/vehicle", json=vehicle_data)
    vin = vehicle_data["vin"].lower()
    update_data = vehicle_data.copy()
    update_data.pop("vin")
    update_data["manufacturer_name"] = "Honda"
    
    response = client.put(f"/vehicle/{vin}", json=update_data)
    assert response.status_code == 200
    assert response.json()["manufacturer_name"] == "Honda"
    
    # not found
    update_data = vehicle_data.copy()
    update_data.pop("vin")
    response = client.put("/vehicle/NONEXISTENT", json=update_data)
    assert response.status_code == 404
    
    # invalid data
    client.post("/vehicle", json=vehicle_data)
    vin = vehicle_data["vin"].lower()
    response = client.put(f"/vehicle/{vin}", json={"manufacturer_name": "Toyota"})
    assert response.status_code == 422


# DELETE /vehicle/{vin} tests
def test_delete(client, vehicle_data):
    # success
    client.post("/vehicle", json=vehicle_data)
    vin = vehicle_data["vin"].lower()
    response = client.delete(f"/vehicle/{vin}")
    assert response.status_code == 204
    assert client.get(f"/vehicle/{vin}").status_code == 404
    
    # not found
    response = client.delete("/vehicle/NONEXISTENT")
    assert response.status_code == 404
    
    # no response body
    client.post("/vehicle", json=vehicle_data)
    vin = vehicle_data["vin"].lower()
    response = client.delete(f"/vehicle/{vin}")
    assert response.status_code == 204
    assert response.content == b""
