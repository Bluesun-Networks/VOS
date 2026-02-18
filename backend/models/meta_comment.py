from pydantic import BaseModel
from typing import List, Literal
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


class MetaSynthesisResult(BaseModel):
    """Full result of meta synthesis including verdict and confidence."""
    comments: List[MetaComment]
    verdict: Literal['ship_it', 'fix_first', 'major_rework']
    confidence: float  # 0.0 - 1.0, based on reviewer consensus
