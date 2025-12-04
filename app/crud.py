from sqlalchemy.orm import Session

from app import models, schemas

def add_vehicle(db: Session, vehicle_data: schemas.VehicleCreate):
  """
  adds a new vehicle to the database

  Args:
      db (Session): _description_
      vehicle_data (schemas.VehicleCreate): _description_
  """
  new_vehicle = models.Vehicle(
    vin=vehicle_data.vin,
    manufacturer_name=vehicle_data.manufacturer_name,
    description=vehicle_data.description,
    horse_power=vehicle_data.horse_power,
    model_name=vehicle_data.model_name,
    model_year=vehicle_data.model_year,
    purchase_price=vehicle_data.purchase_price,
    fuel_type=vehicle_data.fuel_type,
  )
  db.add(new_vehicle) # add to database
  db.commit()

  db.refresh(new_vehicle) # just in case
  return new_vehicle

def get_vehicle(db: Session, vin: str):
  """
  gets one vehicle by vin

  Args:
      db (Session): _description_
      vin (str): _description_
  """
  # normalize vin to lowercase since model validator stores it lowercase
  return (
    db.query(models.Vehicle)
      .filter(models.Vehicle.vin == vin.lower())
      .first()
  )

def get_all_vehicles(db: Session):
  """
  gets all vehicles in the database

  Args:
      db (Session): _description_

  Returns:
      _type_: _description_
  """
  return (
    db.query(models.Vehicle)
      .order_by(models.Vehicle.manufacturer_name)
      .all()
  )

def update_vehicle(db: Session, vin: str, vehicle_data: schemas.VehicleUpdate):
  """
  Updates the vehicle associated with vin with update_data

  Args:
      db (Session): _description_
      vin (str): _description_
      vehicle_data (schemas.VehicleUpdate): _description_

  Returns:
      models.Vehicle | None: the updated vehicle if found, None otherwise
  """
  vehicle = get_vehicle(db, vin)
  
  if not vehicle:
    return None
  
  # PUT = replace all
  vehicle.manufacturer_name = vehicle_data.manufacturer_name
  vehicle.description = vehicle_data.description
  vehicle.horse_power = vehicle_data.horse_power
  vehicle.model_name = vehicle_data.model_name
  vehicle.model_year = vehicle_data.model_year
  vehicle.purchase_price = vehicle_data.purchase_price
  vehicle.fuel_type = vehicle_data.fuel_type

  db.commit()
  db.refresh(vehicle)
  return vehicle


def delete_vehicle(db: Session, vin: str):
  """
  removes vehicle associated with vin from database

  Args:
      db (Session): _description_
      vin (str): _description_
  """
  vehicle = get_vehicle(db, vin)
  # if there is nothing to delete, return deletion unsuccessful
  if vehicle is None:
    return False

  db.delete(vehicle)
  db.commit()
  return True # successfully deleted






