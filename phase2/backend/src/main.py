"""FastAPI application entry point"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import engine, settings
from .api.routes.tasks import router as tasks_router
from .api.routes.auth import router as auth_router


# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="FastAPI backend for Todo Full-Stack Application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",  # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager

    Connects to database on startup and disconnects on shutdown.
    """
    # Startup: Validate JWT_SECRET is configured
    if not settings.JWT_SECRET:
        raise Exception("JWT_SECRET not configured in .env")
    yield
    # Shutdown
    await engine.dispose()


# Add lifespan to app
app.router.lifespan_context = lifespan

# Include routers
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(tasks_router, prefix="/api", tags=["Tasks"])




@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Todo API - Task CRUD functionality", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
