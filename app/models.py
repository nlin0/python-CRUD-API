from sqlalchemy import Column, String, Integer, Numeric, Text
from sqlalchemy.orm import validates

from app.database import Base


#############################
#      VEHICLE MAPPING      #
#############################
class Vehicle(Base):
  # postgres table
  __tablename__ = "vehicles"

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
      """
      To enforce VIN's case-insensitivity, we get rid of cases 
      """
      return value.lower() if value else value

  