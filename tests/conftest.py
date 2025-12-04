import pytest
from sqlalchemy import Column, String, Integer, Numeric, Text
from sqlalchemy.orm import validates

from app.database import Base, engine, Session


# model using vehicles_test table
class VehicleTest(Base):
    __tablename__ = "vehicles_test"
    
    vin = Column(String(17), primary_key=True)
    manufacturer_name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    horse_power = Column(Integer, nullable=False)
    model_name = Column(String(100), nullable=False)
    model_year = Column(Integer, nullable=False)
    purchase_price = Column(Numeric(12, 2), nullable=False)
    fuel_type = Column(String(50), nullable=False)
    
    @validates("vin")
    def vin_validate(self, _, value):
        return value.lower() if value else value


@pytest.fixture(scope="function", autouse=True)
def setup_test_table():
    """Create and cleanup test table for each test"""
    VehicleTest.metadata.create_all(bind=engine)
    # cleanup before test
    db = Session()
    try:
        db.query(VehicleTest).delete()
        db.commit()
    finally:
        db.close()
    yield
    # cleanup after test
    db = Session()
    try:
        db.query(VehicleTest).delete()
        db.commit()
    finally:
        db.close()
