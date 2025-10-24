"""
Main FastAPI application entry point.

TODO: Implementation steps:
1. Initialize FastAPI app
2. Configure CORS middleware
3. Add all routers
4. Add exception handlers
5. Add startup/shutdown events
6. Configure static file serving
7. Add health check endpoint
8. Add API documentation
9. Initialize Sentry for error tracking
10. Add request logging middleware
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

# TODO: Import routers
# from backend.api.routes import auth, jobs, outlines, payments, player
# from backend.config import get_settings
# from backend.db.session import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: Get settings
# settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.

    TODO:
    - Add startup logic (database initialization, etc.)
    - Add shutdown logic (close connections, etc.)
    """
    # Startup
    logger.info("Starting up...")
    # TODO: Initialize database
    # init_db()
    # TODO: Initialize Sentry
    # if settings.sentry_dsn:
    #     import sentry_sdk
    #     sentry_sdk.init(dsn=settings.sentry_dsn)

    yield

    # Shutdown
    logger.info("Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Codebase Audiobook API",
    description="API for generating audiobooks from code repositories",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
# TODO: Get allowed origins from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Frontend dev server
        "http://localhost:3000",
        # TODO: Add production frontend URL from settings
        # settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors.

    TODO:
    - Format validation errors nicely
    - Log validation errors
    - Return user-friendly message
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.

    TODO:
    - Log exception with traceback
    - Send to Sentry
    - Return generic error message (don't leak details)
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    TODO:
    - Check database connection
    - Check checkpoint database connection
    - Check external API connectivity
    - Return health status
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        # TODO: Add more health checks
        # "database": "connected",
        # "checkpoint_store": "connected",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Codebase Audiobook API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
# TODO: Import and include all routers
# app.include_router(auth.router)
# app.include_router(jobs.router)
# app.include_router(outlines.router)
# app.include_router(payments.router)
# app.include_router(player.router)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests.

    TODO:
    - Log request method, path, headers
    - Log response status code
    - Log request duration
    - Add request ID
    """
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response


# Run with: uvicorn backend.main:app --reload
if __name__ == "__main__":
    import uvicorn

    # TODO: Get host and port from settings
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Only for development
    )
