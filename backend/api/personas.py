import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from database import get_db, DbPersona
from models.persona import Persona, PersonaCreate, PersonaUpdate

router = APIRouter()


def _db_persona_to_schema(db_p: DbPersona) -> Persona:
    return Persona(
        id=db_p.id,
        name=db_p.name,
        description=db_p.description,
        system_prompt=db_p.system_prompt,
        tone=db_p.tone,
        focus_areas=db_p.focus_areas or [],
        color=db_p.color,
        output_requirements=db_p.output_requirements,
        reference_notes=db_p.reference_notes,
        examples=db_p.examples,
        is_default=db_p.is_default,
        is_active=db_p.is_active,
        sort_order=db_p.sort_order,
        color_theme=db_p.color_theme,
    )


@router.get("/", response_model=List[Persona])
async def list_personas(active_only: bool = False, db: Session = Depends(get_db)):
    """List all personas, optionally filtered to active only"""
    query = db.query(DbPersona)
    if active_only:
        query = query.filter(DbPersona.is_active == True)
    personas = query.order_by(DbPersona.sort_order, DbPersona.name).all()
    return [_db_persona_to_schema(p) for p in personas]


@router.get("/{persona_id}", response_model=Persona)
async def get_persona(persona_id: str, db: Session = Depends(get_db)):
    """Get a persona by ID"""
    db_p = db.query(DbPersona).filter(DbPersona.id == persona_id).first()
    if not db_p:
        raise HTTPException(status_code=404, detail="Persona not found")
    return _db_persona_to_schema(db_p)


@router.post("/", response_model=Persona, status_code=201)
async def create_persona(persona: PersonaCreate, db: Session = Depends(get_db)):
    """Create a new persona"""
    persona_id = str(uuid.uuid4())[:8]
    db_p = DbPersona(
        id=persona_id,
        name=persona.name,
        description=persona.description,
        system_prompt=persona.system_prompt,
        tone=persona.tone.value,
        focus_areas=persona.focus_areas,
        color=persona.color,
        output_requirements=persona.output_requirements,
        reference_notes=persona.reference_notes,
        examples=persona.examples,
        is_default=persona.is_default,
        is_active=persona.is_active,
        sort_order=persona.sort_order,
        color_theme=persona.color_theme,
    )
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return _db_persona_to_schema(db_p)


@router.put("/{persona_id}", response_model=Persona)
async def update_persona(persona_id: str, updates: PersonaUpdate, db: Session = Depends(get_db)):
    """Update an existing persona"""
    db_p = db.query(DbPersona).filter(DbPersona.id == persona_id).first()
    if not db_p:
        raise HTTPException(status_code=404, detail="Persona not found")

    update_data = updates.model_dump(exclude_unset=True)
    if "tone" in update_data and update_data["tone"] is not None:
        update_data["tone"] = update_data["tone"].value
    for field, value in update_data.items():
        setattr(db_p, field, value)

    db.commit()
    db.refresh(db_p)
    return _db_persona_to_schema(db_p)


@router.delete("/{persona_id}")
async def delete_persona(persona_id: str, db: Session = Depends(get_db)):
    """Delete a persona"""
    db_p = db.query(DbPersona).filter(DbPersona.id == persona_id).first()
    if not db_p:
        raise HTTPException(status_code=404, detail="Persona not found")
    db.delete(db_p)
    db.commit()
    return {"message": "Persona deleted"}
