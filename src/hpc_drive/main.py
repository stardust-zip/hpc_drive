from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Import from our new database file
from .database import create_db_and_tables
from .api.v1 import router_drive, router_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run on startup
    print("Starting up...")
    print("Creating database and tables...")
    create_db_and_tables()  # This creates tables from models.py
    yield
    # Run on shutdown
    print("Shutting down...")


origins = [
    "http://localhost:3000", 
    "http://localhost:3001",
]



app = FastAPI(
    title="HPC Drive Microservice",
    description="Drive service for the college management system",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers (Authorization, Content-Type, etc.)
)


# Include the router
app.include_router(router_drive.router, prefix="/api/v1")
app.include_router(router_admin.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}


# uvicorn --app-dir src hpc_drive.main:app --host 0.0.0.0 --port 7777 --reload
