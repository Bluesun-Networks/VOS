from fastapi import APIRouter
from .documents import router as documents_router
from .personas import router as personas_router

api_router = APIRouter()
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(personas_router, prefix="/personas", tags=["personas"])
