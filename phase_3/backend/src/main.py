
"""FastAPI application entry point"""
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlmodel import SQLModel

from .db import engine, settings
from .api.routes.tasks import router as tasks_router
from .api.routes.auth import router as auth_router
from .api.routes.chat import router as chat_router
load_dotenv()



def validate_environment():
    required_vars = ["JWT_SECRET"]

    if os.getenv("USE_AI_SERVICES", "true").lower() == "true":
        required_vars.append("OPENROUTER_API_KEY")

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise Exception(f"Missing required environment variables: {', '.join(missing_vars)}")



# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="FastAPI backend for Todo Full-Stack Application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"docExpansion": "none"} if os.getenv("ENVIRONMENT") == "production" else None
)

# Add security headers via middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Access-Control-Allow-Origin", "Authorization"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - creates DB tables and validates env"""
    validate_environment()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await engine.dispose()


app.router.lifespan_context = lifespan

# Include routers
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
app.include_router(chat_router, tags=["Chat"])  # No prefix needed as chat endpoints already have /api in their definition


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Todo API - Task CRUD functionality", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
