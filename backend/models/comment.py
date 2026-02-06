from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentAnchor(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    start_char: Optional[int] = None
    end_char: Optional[int] = None

class CommentBase(BaseModel):
    content: str
    anchor: CommentAnchor

class CommentCreate(CommentBase):
    persona_id: str
    document_id: str
    version_hash: str

class Comment(CommentBase):
    id: str
    persona_id: str
    persona_name: str
    persona_color: str
    document_id: str
    version_hash: str
    created_at: datetime
    
    class Config:
        from_attributes = True
