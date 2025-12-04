from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

class VehicleBase(BaseModel):
  # FastAPI built in excpetion handlers handle 422 and 400
  # exclude VIN... should not be updatable
  manufacturer_name: str
  description: str | None = None
  horse_power: int
  model_name: str
  model_year: int
  purchase_price: Decimal
  fuel_type: str


class VehicleCreate(VehicleBase):
  # adds VIN and makes sure it is lowercase
  # VIN must be exactly 17 characters (standard VIN length)
  vin: str = Field(..., min_length=5, max_length=17)
  
  @field_validator("vin")
  @classmethod
  def vin_validate(cls, v):
    return v.lower() if v else v
    

class VehicleUpdate(VehicleBase):
    """
    PUT: requires a full vehicle object, all fields are required
    VIN cannot be updated.
    """
    # requires all fields, just inherit from the VehicleBase
    pass

  
############################
#    RESPONSE MODEL        #
############################
class VehicleRead(VehicleBase):
  vin: str

  model_config = {"from_attributes": True}
