from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.review_service import ReviewService

router = APIRouter()
review_service = ReviewService()


class PersonaUpdate(BaseModel):
    weight: Optional[float] = None


@router.get("/")
async def list_personas():
    """List all available personas"""
    return [p.model_dump() for p in review_service.list_personas()]


@router.get("/{persona_id}")
async def get_persona(persona_id: str):
    """Get a persona by ID"""
    persona = review_service.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona.model_dump()


@router.patch("/{persona_id}")
async def update_persona(persona_id: str, update: PersonaUpdate):
    """Update a persona's configurable fields (e.g. weight)"""
    persona = review_service.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    if update.weight is not None:
        if update.weight < 0.0 or update.weight > 5.0:
            raise HTTPException(status_code=400, detail="Weight must be between 0.0 and 5.0")
        persona.weight = update.weight

    return persona.model_dump()
