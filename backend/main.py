import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from database.init_db import init_db
from api.routes import api_router

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if not settings.is_production else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: initialise DB tables.
    Shutdown: nothing special needed (connections close via engine disposal).
    """
    logger.info("Starting GitHub Time Machine API…")
    await init_db()
    logger.info("Database tables verified ✓")
    yield
    logger.info("Shutting down…")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="GitHub Time Machine API",
    description=(
        "AI-powered repository intelligence platform. "
        "Analyze GitHub commit history and transform it into engineering insights."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Check server logs."},
    )


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


# ── Health / ping ─────────────────────────────────────────────────────────────
@app.get("/ping", tags=["system"])
async def ping():
    return {"status": "ok", "service": "github-time-machine"}


@app.get("/", tags=["system"])
async def root():
    return {
        "service": "GitHub Time Machine API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/ping",
    }
