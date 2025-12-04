from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/vehicle",
    tags=["Vehicle API"],
)

# GET /vehicle (all vehicles) -> 200 OK
@router.get("", response_model=list[schemas.VehicleRead],
      status_code=status.HTTP_200_OK)
def get_all_vehicles(db: Session = Depends(get_db)):
  return crud.get_all_vehicles(db)

# GET /vehicle (single vehicle) -> 200 OK
@router.get("/{vin}",response_model=schemas.VehicleRead,
    status_code=status.HTTP_200_OK,
)
def get_vehicle(vin: str, db: Session = Depends(get_db)):
    vehicle = crud.get_vehicle(db, vin)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

# POST /vehicle -> 201 Created
@router.post("", response_model=schemas.VehicleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(vehicle_data: schemas.VehicleCreate, db: Session = Depends(get_db)):
  try:
    new_vehicle = crud.add_vehicle(db, vehicle_data)
    return new_vehicle
  except IntegrityError:
    db.rollback()
    raise HTTPException(
      status_code=422,
      detail=f"Vehicle with VIN {vehicle_data.vin} already exists"
    )

# PUT /vehicle/{:vin} (update) -> 200 OK
@router.put( "/{vin}", response_model=schemas.VehicleRead,
    status_code=status.HTTP_200_OK,
)
def update_vehicle(vin: str, vehicle_data: schemas.VehicleUpdate, db: Session = Depends(get_db)):
    vehicle = crud.get_vehicle(db, vin)
    if vehicle is None:
      raise HTTPException(status_code=404, detail="Vehicle not found")

    updated = crud.update_vehicle(db, vin, vehicle_data)
    return updated

# DELETE /vehicle/{:vin} -> 204 No Content
@router.delete(
    "/{vin}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vehicle(vin: str, db: Session = Depends(get_db)):
    successful = crud.delete_vehicle(db, vin)
    if not successful:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return None  # doesn't return anything