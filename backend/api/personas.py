from fastapi import APIRouter, HTTPException
from typing import List
import uuid

from models.persona import Persona, PersonaCreate, PersonaGroup, PersonaGroupCreate

router = APIRouter()

# In-memory store (replace with DB later)
_personas: dict[str, Persona] = {}
_persona_groups: dict[str, PersonaGroup] = {}

# Create some default personas
DEFAULT_PERSONAS = [
    PersonaCreate(
        name="Security Reviewer",
        description="Focuses on security implications, vulnerabilities, and data privacy concerns",
        system_prompt="You are a senior security engineer reviewing this document. Look for security vulnerabilities, data privacy concerns, authentication/authorization issues, and potential attack vectors. Be thorough and critical.",
        tone="critical",
        focus_areas=["security", "privacy", "authentication", "vulnerabilities"],
        color="#ef4444"  # Red
    ),
    PersonaCreate(
        name="Technical Architect",
        description="Evaluates technical design, scalability, and implementation details",
        system_prompt="You are a principal software architect reviewing this document. Evaluate the technical design, scalability considerations, performance implications, and architectural patterns. Suggest improvements.",
        tone="technical",
        focus_areas=["architecture", "scalability", "performance", "design patterns"],
        color="#3b82f6"  # Blue
    ),
    PersonaCreate(
        name="Devil's Advocate",
        description="Challenges assumptions and finds weaknesses in arguments",
        system_prompt="You are a critical thinker whose job is to find flaws in reasoning. Challenge every assumption, question the evidence, and identify logical fallacies or gaps in the argument. Be constructively contrarian.",
        tone="devil_advocate", 
        focus_areas=["logic", "assumptions", "evidence", "counterarguments"],
        color="#f59e0b"  # Amber
    ),
    PersonaCreate(
        name="Clarity Editor",
        description="Improves readability, structure, and communication",
        system_prompt="You are a professional editor focused on clarity and communication. Identify confusing passages, suggest clearer phrasing, improve document structure, and ensure the message is effectively communicated.",
        tone="supportive",
        focus_areas=["clarity", "structure", "readability", "communication"],
        color="#10b981"  # Emerald
    ),
]

def _init_defaults():
    for persona_data in DEFAULT_PERSONAS:
        pid = str(uuid.uuid4())[:8]
        _personas[pid] = Persona(id=pid, **persona_data.model_dump())

_init_defaults()

@router.get("/", response_model=List[Persona])
async def list_personas():
    """List all personas"""
    return list(_personas.values())

@router.post("/", response_model=Persona)
async def create_persona(persona: PersonaCreate):
    """Create a new persona"""
    pid = str(uuid.uuid4())[:8]
    new_persona = Persona(id=pid, **persona.model_dump())
    _personas[pid] = new_persona
    return new_persona

@router.get("/{persona_id}", response_model=Persona)
async def get_persona(persona_id: str):
    """Get a persona by ID"""
    if persona_id not in _personas:
        raise HTTPException(status_code=404, detail="Persona not found")
    return _personas[persona_id]

@router.delete("/{persona_id}")
async def delete_persona(persona_id: str):
    """Delete a persona"""
    if persona_id not in _personas:
        raise HTTPException(status_code=404, detail="Persona not found")
    del _personas[persona_id]
    return {"message": "Persona deleted"}

# Persona Groups
@router.get("/groups/", response_model=List[PersonaGroup])
async def list_persona_groups():
    """List all persona groups"""
    return list(_persona_groups.values())

@router.post("/groups/", response_model=PersonaGroup)
async def create_persona_group(group: PersonaGroupCreate):
    """Create a new persona group"""
    gid = str(uuid.uuid4())[:8]
    new_group = PersonaGroup(id=gid, **group.model_dump())
    _persona_groups[gid] = new_group
    return new_group
