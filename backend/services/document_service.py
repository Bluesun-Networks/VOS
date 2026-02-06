import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from models.document import Document, DocumentCreate, DocumentVersion
from services.git_service import GitService

class DocumentService:
    """Document management with git-backed versioning"""
    
    def __init__(self):
        self.git = GitService()
        self._documents: dict = {}  # In-memory store (replace with DB later)
    
    def create(self, doc: DocumentCreate) -> Document:
        """Create a new document"""
        repo_id, repo_path = self.git.create_repo(doc.title.lower().replace(" ", "-"))
        
        # Create the markdown file
        file_name = "document.md"
        commit_hash = self.git.commit_file(
            str(repo_path),
            file_name,
            doc.content,
            f"Initial version: {doc.title}"
        )
        
        now = datetime.utcnow()
        document = Document(
            id=repo_id,
            title=doc.title,
            description=doc.description,
            repo_path=str(repo_path),
            current_branch="main",
            created_at=now,
            updated_at=now,
            versions=[DocumentVersion(
                commit_hash=commit_hash,
                message=f"Initial version: {doc.title}",
                author="VOS System",
                timestamp=now
            )]
        )
        
        self._documents[repo_id] = document
        return document
    
    def get(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID"""
        doc = self._documents.get(doc_id)
        if doc:
            # Refresh version history
            history = self.git.get_history(doc.repo_path)
            doc.versions = [
                DocumentVersion(
                    commit_hash=h["hash"],
                    message=h["message"],
                    author=h["author"],
                    timestamp=h["timestamp"]
                )
                for h in history
            ]
        return doc
    
    def list(self) -> List[Document]:
        """List all documents"""
        return list(self._documents.values())
    
    def get_content(self, doc_id: str, version: Optional[str] = None) -> str:
        """Get document content at specific version"""
        doc = self.get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")
        
        return self.git.get_file_content(doc.repo_path, "document.md", version)
    
    def update(self, doc_id: str, content: str, message: str) -> Document:
        """Update document content (creates new version)"""
        doc = self.get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")
        
        commit_hash = self.git.commit_file(
            doc.repo_path,
            "document.md",
            content,
            message
        )
        
        doc.updated_at = datetime.utcnow()
        return self.get(doc_id)
    
    def get_diff(self, doc_id: str, from_version: str, to_version: Optional[str] = None) -> str:
        """Get diff between versions"""
        doc = self.get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")
        
        return self.git.get_diff(doc.repo_path, from_version, to_version, "document.md")
    
    def create_branch(self, doc_id: str, branch_name: str) -> Document:
        """Create a new branch for the document"""
        doc = self.get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")
        
        self.git.create_branch(doc.repo_path, branch_name)
        return doc
    
    def switch_branch(self, doc_id: str, branch_name: str) -> Document:
        """Switch document to a different branch"""
        doc = self.get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")
        
        self.git.switch_branch(doc.repo_path, branch_name)
        doc.current_branch = branch_name
        return doc
    
    def list_branches(self, doc_id: str) -> List[dict]:
        """List branches for a document"""
        doc = self.get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")
        
        return self.git.list_branches(doc.repo_path)
