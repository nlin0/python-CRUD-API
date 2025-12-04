from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import engine
from app import models
from app.routers import vehicles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    lifespan event handler for startup and shutdown. creates database 
    tables on startup if they don't exist.
    """
    models.Base.metadata.create_all(bind=engine)
    yield
    # dispose sqlalchemy engine after we're done using
    engine.dispose()


# initialize the app
app = FastAPI(
    title="Apollo Vehicles API",
    description="A CRUD-style web service for managing vehicle records.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors according to assignment requirements:
    - 400 Bad Request: Cannot parse request entity as JSON
    - 422 Unprocessable Entity: Can parse JSON but entity is invalid
    """
    errors = exc.errors()
    
    # Check if error is due to JSON parsing failure
    # JSON parsing errors typically have "type": "json_invalid" or "type": "value_error.jsondecode"
    is_json_parse_error = any(
        error.get("type") in ["json_invalid", "value_error.jsondecode", "type_error.json"]
        for error in errors
    )
    
    if is_json_parse_error:
        # 400 Bad Request: Cannot parse as JSON
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Cannot parse request entity as JSON representation of a Vehicle"}
        )
    else:
        # 422 Unprocessable Entity: Can parse but invalid attributes
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )


# include router
app.include_router(vehicles.router)