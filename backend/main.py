from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
except ImportError:
    trace = None
    OTLPSpanExporter = None
    FastAPIInstrumentor = None
    Resource = None
    TracerProvider = None
    BatchSpanProcessor = None

from backend.api.routes import auth, jobs, outlines, payments, player
from backend.api.ws import router as ws_router
from backend.config import get_settings
from backend.db.session import init_db
from backend.utils.checkpointing import PostgresCheckpointStorage

settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    try:
        init_db()
    except Exception as exc:
        logger.warning("Database initialization skipped: %s", exc)
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Codebase Audiobook API",
    description="API for generating audiobooks from code repositories",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

if trace and Resource and TracerProvider:
    resource = Resource.create({"service.name": settings.service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    if settings.otel_exporter_otlp_endpoint and OTLPSpanExporter and BatchSpanProcessor:
        exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
    if FastAPIInstrumentor:
        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

cors_origins = ["http://localhost:5173", "http://localhost:3000"]
if settings.frontend_url not in cors_origins:
    cors_origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(outlines.router)
app.include_router(payments.router)
app.include_router(player.router)
app.include_router(ws_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return structured validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Log unexpected errors and return a generic response."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/health")
async def health_check():
    status_payload = {
        "status": "healthy",
        "version": "0.1.0",
    }
    try:
        storage = PostgresCheckpointStorage("healthcheck")
        await storage.list_checkpoint_ids()
        status_payload["checkpoint_store"] = "ok"
    except Exception:
        status_payload["checkpoint_store"] = "error"
    return status_payload


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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request and response."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
