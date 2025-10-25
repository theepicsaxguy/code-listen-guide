from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

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

from backend.api.dependencies import limiter
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


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        csp_directives = " ".join(
            [
                "default-src 'none';",
                "frame-ancestors 'none';",
                "base-uri 'none';",
                "form-action 'self';",
                "connect-src 'self';",
            ]
        )
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "microphone=(), camera=()")
        response.headers.setdefault("Content-Security-Policy", csp_directives)
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload"
        )
        return response


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    retry_after = None
    if getattr(exc, "limit", None) is not None:
        retry_after = getattr(exc.limit, "window_seconds", None)
    headers = {}
    if retry_after is not None:
        headers["Retry-After"] = str(int(retry_after))
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests"},
        headers=headers,
    )


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

cors_origins = set()

if settings.frontend_url:
    cors_origins.add(settings.frontend_url.rstrip("/"))

if settings.environment.lower() == "development":
    cors_origins.update(
        {
            "http://localhost:4173",
            "http://127.0.0.1:4173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        }
    )

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
    expose_headers=["Retry-After"],
    max_age=3600,
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

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
