from contextlib import asynccontextmanager
from fastapi import FastAPI

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

# include router
app.include_router(vehicles.router)