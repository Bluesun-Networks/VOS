import logging

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

from core.config import get_settings

logger = logging.getLogger("vos.db")

_settings = get_settings()
DATABASE_URL = _settings.database_url


def _build_engine(url: str):
    """Create a SQLAlchemy engine with driver-appropriate settings."""
    if url.startswith("sqlite"):
        # SQLite: single-threaded, no connection pool needed
        return create_engine(url, connect_args={"check_same_thread": False})
    else:
        # PostgreSQL (or other): use connection pooling
        return create_engine(
            url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # verify connections before checkout
        )


engine = _build_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DbDocument(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    repo_path = Column(String, nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviews = relationship("DbReview", back_populates="document", cascade="all, delete-orphan")


class DbPersona(Base):
    __tablename__ = "personas"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    tone = Column(String, nullable=False, default="neutral")
    focus_areas = Column(JSON, default=[])
    color = Column(String, default="#6366f1")
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DbReviewJob(Base):
    __tablename__ = "review_jobs"

    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    status = Column(String, default="queued")  # queued, running, completed, failed
    provider = Column(String, nullable=True)
    model = Column(String, nullable=True)
    trigger = Column(String, default="manual")  # manual, ci, webhook
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    reviews = relationship("DbReview", back_populates="job")


class DbReview(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    job_id = Column(String, ForeignKey("review_jobs.id"), nullable=True)
    persona_ids = Column(JSON, nullable=False)
    status = Column(String, default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    meta_verdict = Column(String, nullable=True)  # ship_it, fix_first, major_rework
    meta_confidence = Column(Float, nullable=True)  # 0.0 - 1.0

    document = relationship("DbDocument", back_populates="reviews")
    job = relationship("DbReviewJob", back_populates="reviews")
    comments = relationship("DbComment", back_populates="review", cascade="all, delete-orphan")
    meta_comments = relationship("DbMetaComment", back_populates="review", cascade="all, delete-orphan")


class DbComment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True)
    review_id = Column(String, ForeignKey("reviews.id"), nullable=False)
    document_id = Column(String, nullable=False)
    persona_id = Column(String, nullable=False)
    persona_name = Column(String, nullable=False)
    persona_color = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    review = relationship("DbReview", back_populates="comments")


class DbMetaComment(Base):
    __tablename__ = "meta_comments"

    id = Column(String, primary_key=True)
    review_id = Column(String, ForeignKey("reviews.id"), nullable=False)
    content = Column(Text, nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    sources = Column(JSON, nullable=False)  # [{persona_id, persona_name, persona_color, original_content}]
    category = Column(String, nullable=False)  # structure, clarity, technical, security, accessibility
    priority = Column(String, nullable=False)  # critical, high, medium, low
    created_at = Column(DateTime, default=datetime.utcnow)

    review = relationship("DbReview", back_populates="meta_comments")


def init_db():
    Base.metadata.create_all(bind=engine)
    db_type = "PostgreSQL" if "postgresql" in DATABASE_URL else "SQLite"
    logger.info("Database initialized (%s)", db_type)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
