import logging
import sys

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from api import api_router
from core.config import get_settings
from core.errors import VosError, vos_error_handler, unhandled_error_handler
from core.observability import RequestLoggingMiddleware, metrics
from core.security import RateLimitMiddleware, CSRFMiddleware
from database import init_db, get_db
from services.review_service import seed_default_personas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)

VOS_VERSION = "0.3.0"

settings = get_settings()

app = FastAPI(
    title="VOS API",
    description="Voxora · Opinari · Scrutara - AI Document Review",
    version=VOS_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception handlers — structured JSON for all errors
app.add_exception_handler(VosError, vos_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

# Middleware stack (outermost first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CSRFMiddleware)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    init_db()
    seed_default_personas()
    logging.getLogger("vos").info("VOS %s started (python %s)", VOS_VERSION, sys.version.split()[0])


@app.get("/")
async def root():
    return {
        "name": "VOS",
        "tagline": "Voxora · Opinari · Scrutara",
        "status": "operational",
        "version": VOS_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ready")
async def readiness(db: Session = Depends(get_db)):
    """Readiness probe for container orchestration.

    Returns 200 only when the DB is reachable and the app can serve traffic.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={"ready": False, "reason": str(e)})


@app.get("/api/v1/metrics")
async def get_metrics():
    """Return in-memory request and review metrics."""
    return metrics.snapshot()
