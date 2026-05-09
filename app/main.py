from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.cache import redis_client
from app.config import settings
from app.database import Base, engine, SessionLocal
from app.logger import logger

from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User

from app.routes.accounts import router as accounts_router
from app.routes.analytics import router as analytics_router
from app.routes.auth import router as auth_router
from app.routes.transactions import router as transactions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FinFlow API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"API Version: {settings.app_version}")

    try:
        logger.info("Creating database tables if they do not exist...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database table check completed.")
    except Exception:
        logger.exception("Database table creation failed.")

    yield

    logger.info("Shutting down FinFlow API...")


tags_metadata = [
    {
        "name": "Authentication",
        "description": "User authentication and JWT login endpoints.",
    },
    {
        "name": "Transactions",
        "description": "Transaction creation, retrieval, updates, deletion, and filtering.",
    },
    {
        "name": "Accounts",
        "description": "Bank account and balance management.",
    },
    {
        "name": "Analytics",
        "description": "Financial analytics, summaries, and reporting endpoints.",
    },
    {
        "name": "Health",
        "description": "Application, database, and Redis health monitoring.",
    },
]

app = FastAPI(
    title="FinFlow API",
    description="""
Backend API for financial transaction management,
analytics, caching, and account tracking.

Features include:
- JWT authentication
- Transaction CRUD operations
- Financial analytics
- Redis caching
- Health monitoring
- API versioning
""",
    version=settings.app_version,
    debug=settings.debug,
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    contact={
        "name": "Muhammad Qazi",
        "email": "qz_usman@yahoo.com",
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = round(time.time() - start_time, 4)

    logger.info(
        f"{request.method} {request.url.path} "
        f"completed with {response.status_code} "
        f"in {process_time}s"
    )

    return response


@app.get("/info", tags=["Health"])
def api_info():
    return {
        "name": "FinFlow API",
        "version": settings.app_version,
        "environment": settings.environment,
        "description": "Backend API for financial transaction management and analytics",
        "features": [
            "JWT authentication",
            "Transaction CRUD",
            "Account tracking",
            "Financial analytics",
            "Redis caching",
            "Health monitoring",
            "API versioning",
        ],
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "finflow-api",
        "environment": settings.environment,
    }


@app.get("/health/db", tags=["Health"])
def database_health_check():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.environment,
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "environment": settings.environment,
        }

    finally:
        db.close()


@app.get("/health/redis", tags=["Health"])
def redis_health_check():
    try:
        redis_client.ping()

        return {
            "status": "healthy",
            "redis": "connected",
            "environment": settings.environment,
        }

    except Exception:
        return {
            "status": "unhealthy",
            "redis": "disconnected",
            "environment": settings.environment,
        }


@app.get("/health/full", tags=["Health"])
def full_health_check():
    db = SessionLocal()

    health_status = {
        "status": "healthy",
        "service": "finflow-api",
        "database": "connected",
        "redis": "connected",
        "environment": settings.environment,
    }

    try:
        db.execute(text("SELECT 1"))
    except Exception:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"

    try:
        redis_client.ping()
    except Exception:
        health_status["status"] = "unhealthy"
        health_status["redis"] = "disconnected"

    finally:
        db.close()

    return health_status


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to FinFlow API",
        "version": "v1",
        "docs": "/docs",
        "api_base": "/api/v1",
        "health": "/health",
        "full_health": "/health/full",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")

    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": "An unexpected error occurred.",
        },
    )


API_PREFIX = settings.api_prefix

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(transactions_router, prefix=API_PREFIX)
app.include_router(accounts_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)