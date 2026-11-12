import json
import logging
import time
import uuid
from contextvars import ContextVar

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import MEDIA_DIR, settings
from app.core.limiter import limiter
from app.db.session import SessionLocal
from app.routers import admin_catalog, auth, catalog
from app.services.admin_catalog_service import ConflictError, InvalidImageError, NotFoundError

request_id_context: ContextVar[str] = ContextVar("request_id", default=None)

class RequestIdFilter:
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("app")
logger.addFilter(RequestIdFilter())

def log_event(level: int, **fields) -> None:
    fields["request_id"] = request_id_context.get()
    logger.log(level, json.dumps(fields))

app = FastAPI(title="TNDC Jewelry House API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_context.set(request_id)
    start = time.monotonic()

    response = await call_next(request)

    duration_ms = round((time.monotonic() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    log_event(
        logging.INFO,
        event="request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log_event(logging.ERROR, event="unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})

@app.exception_handler(InvalidImageError)
async def invalid_image_handler(request: Request, exc: InvalidImageError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": str(exc)})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not ready"})
    return {"status": "ready"}


app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(admin_catalog.router)

MEDIA_DIR.mkdir(exist_ok=True)  
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")