from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class PersonaTone(str, Enum):
    CRITICAL = "critical"
    SUPPORTIVE = "supportive"
    NEUTRAL = "neutral"
    DEVIL_ADVOCATE = "devil_advocate"
    TECHNICAL = "technical"

class PersonaBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    tone: PersonaTone = PersonaTone.NEUTRAL
    focus_areas: List[str] = []
    color: str = "#6366f1"  # Default indigo
    output_requirements: Optional[str] = None
    reference_notes: Optional[str] = None
    examples: Optional[str] = None
    is_default: bool = False
    is_active: bool = True
    sort_order: int = 0
    color_theme: Optional[str] = None

class PersonaCreate(PersonaBase):
    pass

class PersonaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    tone: Optional[PersonaTone] = None
    focus_areas: Optional[List[str]] = None
    color: Optional[str] = None
    output_requirements: Optional[str] = None
    reference_notes: Optional[str] = None
    examples: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    color_theme: Optional[str] = None

class Persona(PersonaBase):
    id: str

    class Config:
        from_attributes = True

class PersonaGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    persona_ids: List[str] = []

class PersonaGroupCreate(PersonaGroupBase):
    pass

class PersonaGroup(PersonaGroupBase):
    id: str

    class Config:
        from_attributes = True
