from fastapi import FastAPI
from contextlib import asynccontextmanager

from .db import create_db_and_tables
from .api.v1 import router_drive


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chạy khi khởi động server
    print("Starting up...")
    print("Creating database and tables...")
    create_db_and_tables()
    yield
    # Chạy khi tắt server
    print("Shutting down...")


app = FastAPI(
    title="HPC Drive Microservice",
    description="Drive service cho hệ thống quản lý trường học",
    version="0.1.0",
    lifespan=lifespan,
)

# Gắn router
app.include_router(router_drive.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
