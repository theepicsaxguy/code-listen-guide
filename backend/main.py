import asyncio
import contextlib
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
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

# Add project root to Python path when running as a script
# This allows 'python3 backend/main.py' to work without PYTHONPATH
import sys
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from backend.api.dependencies import limiter
from backend.api.routes import auth, jobs, outlines, payments, player, admin, parse, agents_admin, episodes, passkeys
from backend.api.routes.admin_workflows import router as admin_workflows_router
from backend.api.routes.admin_routes.agent_test import router as agent_test_router
from backend.api.routes.admin_plugins import (
    router as admin_plugins_router,
    tools_router as admin_tools_router,
)
from backend.api.routes.admin_agents_crud import router as admin_agents_crud_router
from backend.api.routes.traces import router as traces_router
from backend.api.ws import router as ws_router
from backend.config import get_settings
from backend.db.session import init_db
from backend.tasks.tool_integrity import tool_registry_integrity_loop
from backend.utils.checkpointing import PostgresCheckpointStorage
from backend.workflows.dynamic_loader import get_tool_registry_manager
from backend.workflows.tool_registry_validator import (
    ToolValidationError,
    validate_registered_tools,
)

settings = get_settings()
frontend_dist_path = (Path(__file__).resolve().parent / "frontend_dist").resolve()
frontend_dist_exists = frontend_dist_path.exists()


def get_frontend_file(relative_path: str) -> Path:
    candidate = (frontend_dist_path / relative_path).resolve()
    if not candidate.is_relative_to(frontend_dist_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return candidate

# Configure logging
_settings = get_settings()
log_level = getattr(logging, _settings.log_level.upper(), logging.INFO)
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    init_db()
    
    # Auto-seed agents and tools if tables are empty
    from backend.db.session import SessionLocal
    from backend.models.agent_registry import AgentRegistry
    from backend.models.tool_registry import ToolRegistry
    from backend.scripts.seed_workflow_registry import seed_agents, seed_tools
    
    db = SessionLocal()
    try:
        agent_count = db.query(AgentRegistry).count()
        tool_count = db.query(ToolRegistry).count()
        
        if agent_count == 0:
            logger.info("No agents found, seeding agents_registry...")
            seed_agents(db)
        else:
            logger.info(f"Found {agent_count} existing agents, skipping seed")
        
        if tool_count == 0:
            logger.info("No tools found, seeding tools_registry...")
            seed_tools(db)
        else:
            logger.info(f"Found {tool_count} existing tools, skipping seed")
    except Exception as e:
        logger.error(f"Error during auto-seeding: {e}", exc_info=True)
        # Don't fail startup if seeding fails - allow manual seeding
    finally:
        db.close()
    
    get_tool_registry_manager().reload()
    try:
        results = validate_registered_tools(raise_on_error=False)
        logger.info("Validated %s registered tool(s)", len(results))
    except ToolValidationError as exc:
        logger.warning("Tool registry validation failed: %s", exc)
        # Don't raise - allow startup to continue
    
    stop_event = asyncio.Event()
    task = asyncio.create_task(
        tool_registry_integrity_loop(
            settings.tool_registry_check_interval_seconds,
            stop_event,
        )
    )
    app.state.tool_registry_stop_event = stop_event
    app.state.tool_registry_task = task
    try:
        yield
    finally:
        logger.info("Shutting down...")
        stop_event.set()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Allow Swagger UI and ReDoc resources for API documentation
        # For API-first development, documentation should be accessible
        csp_directives = " ".join(
            [
                "default-src 'none';",
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com;",
                "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net;",
                "font-src 'self' https://fonts.gstatic.com;",
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

if frontend_dist_exists:
    assets_dir = frontend_dist_path / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

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

if settings.environment.lower() == "development":
    if settings.frontend_url:
        cors_origins.add(settings.frontend_url.rstrip("/"))
    cors_origins.update(
        {
            "http://localhost:4173",
            "http://127.0.0.1:4173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8081",
            "http://127.0.0.1:8081",
        }
    )
else:
    # Production: Allow frontend origins
    if settings.frontend_url:
        cors_origins.add(settings.frontend_url.rstrip("/"))
    # Allow localhost for docker-compose deployments
    cors_origins.update(
        {
            "http://localhost:8081",
            "http://127.0.0.1:8081",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        }
    )

app.add_middleware(SecurityHeadersMiddleware)

if cors_origins:
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
app.include_router(passkeys.router)
app.include_router(jobs.router)
app.include_router(outlines.router)
app.include_router(payments.router)
app.include_router(player.router)
app.include_router(admin_workflows_router)
app.include_router(admin.router)
app.include_router(agents_admin.router)
app.include_router(admin_agents_crud_router)
app.include_router(admin_plugins_router)
app.include_router(admin_tools_router)
app.include_router(traces_router)
app.include_router(agent_test_router)
app.include_router(parse.router)
app.include_router(ws_router)
app.include_router(episodes.router)


def custom_openapi():
    """Customize OpenAPI schema to include OAuth2 security scheme for Swagger UI."""
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add OAuth2 Password Flow security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/auth/login",
                    "scopes": {},
                }
            },
        }
    }

    # Apply security globally to all endpoints (except auth endpoints)
    for path, path_item in openapi_schema["paths"].items():
        # Don't require auth for login, register, and docs endpoints
        if path in ["/api/v1/auth/login", "/api/v1/auth/register"]:
            continue

        for method in path_item:
            if method in ["get", "post", "put", "delete", "patch", "options"]:
                if "security" not in path_item[method]:
                    path_item[method]["security"] = [{"OAuth2PasswordBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return structured validation errors."""
    logger.error(f"Request validation error for {request.method} {request.url.path}: {exc.errors()}")
    
    # Safely serialize errors by converting to JSON-serializable format
    def sanitize_error(error):
        """Convert validation error to JSON-serializable format."""
        sanitized = {}
        for key, value in error.items():
            if isinstance(value, (str, int, float, bool, type(None))):
                sanitized[key] = value
            elif isinstance(value, (list, tuple)):
                sanitized[key] = [
                    sanitize_error(item) if isinstance(item, dict) else str(item)
                    for item in value
                ]
            elif isinstance(value, dict):
                sanitized[key] = sanitize_error(value)
            else:
                # Convert non-serializable objects to string
                sanitized[key] = str(value)
        return sanitized

    errors = [sanitize_error(error) for error in exc.errors()]

    # Safely handle body - it might contain non-serializable data
    body = None
    if exc.body is not None:
        try:
            # Try to decode if it's bytes
            if isinstance(exc.body, bytes):
                body = exc.body.decode('utf-8')
            elif isinstance(exc.body, str):
                body = exc.body
            else:
                body = str(exc.body)
        except Exception:
            body = "<unable to serialize body>"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors, "body": body},
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
    if frontend_dist_exists:
        index_file = get_frontend_file("index.html")
        return FileResponse(index_file)
    return {
        "message": "Codebase Audiobook API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


if frontend_dist_exists:
    restricted_paths = {"docs", "redoc", "openapi.json", "health"}

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        if not full_path:
            index_file = get_frontend_file("index.html")
            return FileResponse(index_file)
        if full_path.startswith("api/") or full_path in restricted_paths:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        try:
            asset = get_frontend_file(full_path)
            return FileResponse(asset)
        except HTTPException:
            index_file = get_frontend_file("index.html")
            return FileResponse(index_file)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request and response."""
    logger.info(f"{request.method} {request.url.path}")
    
    # For 400 errors, try to log request body for debugging
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                logger.info(f"Request body: {body.decode('utf-8', errors='replace')}")
        except Exception as e:
            logger.warning(f"Could not read request body: {e}")
    
    response = await call_next(request)
    
    # Log error responses with more detail
    if response.status_code >= 400:
        logger.error(f"Error response: {response.status_code} for {request.method} {request.url.path}")
    
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
