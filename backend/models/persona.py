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
    weight: float = 1.0  # Review weight multiplier (higher = more influence)

class PersonaCreate(PersonaBase):
    pass

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
