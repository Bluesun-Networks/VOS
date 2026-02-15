from pydantic import BaseModel
from typing import List
from datetime import datetime


class MetaCommentSource(BaseModel):
    persona_id: str
    persona_name: str
    persona_color: str
    original_content: str


class MetaComment(BaseModel):
    id: str
    content: str
    start_line: int
    end_line: int
    sources: List[MetaCommentSource]
    category: str  # structure, clarity, technical, security, accessibility
    priority: str  # critical, high, medium, low
    created_at: datetime

    class Config:
        from_attributes = True
