import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import api_router
from core.config import get_settings
from core.errors import VosError, vos_error_handler, unhandled_error_handler
from core.security import RateLimitMiddleware, CSRFMiddleware
from database import init_db
from services.review_service import seed_default_personas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)

settings = get_settings()

app = FastAPI(
    title="VOS API",
    description="Voxora · Opinari · Scrutara - AI Document Review",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception handlers — structured JSON for all errors
app.add_exception_handler(VosError, vos_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CSRFMiddleware)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    init_db()
    seed_default_personas()


@app.get("/")
async def root():
    return {
        "name": "VOS",
        "tagline": "Voxora · Opinari · Scrutara",
        "status": "operational",
        "version": "0.2.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
