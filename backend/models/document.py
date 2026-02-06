from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    content: str

class DocumentVersion(BaseModel):
    commit_hash: str
    message: str
    author: str
    timestamp: datetime
    
class Document(DocumentBase):
    id: str
    repo_path: str
    current_branch: str
    created_at: datetime
    updated_at: datetime
    versions: List[DocumentVersion] = []
    
    class Config:
        from_attributes = True
