from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from models.document import Document, DocumentCreate
from services.document_service import DocumentService

router = APIRouter()
doc_service = DocumentService()

class UpdateRequest(BaseModel):
    content: str
    message: str

class BranchRequest(BaseModel):
    branch_name: str

@router.post("/", response_model=Document)
async def create_document(doc: DocumentCreate):
    """Create a new document"""
    return doc_service.create(doc)

@router.get("/", response_model=List[Document])
async def list_documents():
    """List all documents"""
    return doc_service.list()

@router.get("/{doc_id}", response_model=Document)
async def get_document(doc_id: str):
    """Get a document by ID"""
    doc = doc_service.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/{doc_id}/content")
async def get_document_content(doc_id: str, version: Optional[str] = None):
    """Get document content (optionally at specific version)"""
    try:
        content = doc_service.get_content(doc_id, version)
        return {"content": content, "version": version}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{doc_id}")
async def update_document(doc_id: str, update: UpdateRequest):
    """Update document content (creates new version)"""
    try:
        doc = doc_service.update(doc_id, update.content, update.message)
        return doc
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{doc_id}/diff")
async def get_document_diff(doc_id: str, from_version: str, to_version: Optional[str] = None):
    """Get diff between versions"""
    try:
        diff = doc_service.get_diff(doc_id, from_version, to_version)
        return {"diff": diff, "from": from_version, "to": to_version or "HEAD"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{doc_id}/branches")
async def list_branches(doc_id: str):
    """List all branches for a document"""
    try:
        branches = doc_service.list_branches(doc_id)
        return {"branches": branches}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{doc_id}/branches")
async def create_branch(doc_id: str, req: BranchRequest):
    """Create a new branch"""
    try:
        doc = doc_service.create_branch(doc_id, req.branch_name)
        return {"message": f"Branch '{req.branch_name}' created", "document": doc}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{doc_id}/branches/{branch_name}/checkout")
async def checkout_branch(doc_id: str, branch_name: str):
    """Switch to a branch"""
    try:
        doc = doc_service.switch_branch(doc_id, branch_name)
        return {"message": f"Switched to branch '{branch_name}'", "document": doc}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
