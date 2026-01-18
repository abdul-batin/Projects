"""Main FastAPI application for Autonomous Wall Planner."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api import walls, planning, execution, telemetry, monitoring

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting application...")
    logger.info("Note: Database tables must exist (run 'python Server/migrate.py migrate' first)")
    yield
    # Shutdown: cleanup if needed
    logger.info("Shutting down application...")


app = FastAPI(
    title="Autonomous Wall Planner",
    description="API for planning and executing robot wall coverage paths",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(walls.router)
app.include_router(planning.router)
app.include_router(execution.router)
app.include_router(telemetry.router)
app.include_router(monitoring.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Autonomous Wall Planner API",
        "version": "1.0.0",
        "docs": "/docs"
    }

