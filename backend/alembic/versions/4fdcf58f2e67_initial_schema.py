"""initial schema

Revision ID: 4fdcf58f2e67
Revises:
Create Date: 2026-02-18 09:07:07.925561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fdcf58f2e67'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'documents',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('repo_path', sa.String(), nullable=True),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )

    op.create_table(
        'personas',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('system_prompt', sa.Text(), nullable=False),
        sa.Column('tone', sa.String(), nullable=False, server_default='neutral'),
        sa.Column('focus_areas', sa.JSON(), server_default='[]'),
        sa.Column('color', sa.String(), server_default='#6366f1'),
        sa.Column('weight', sa.Float(), server_default='1.0'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )

    op.create_table(
        'review_jobs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('document_id', sa.String(), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('status', sa.String(), server_default='queued'),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('trigger', sa.String(), server_default='manual'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'reviews',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('document_id', sa.String(), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('job_id', sa.String(), sa.ForeignKey('review_jobs.id'), nullable=True),
        sa.Column('persona_ids', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(), server_default='pending'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('meta_verdict', sa.String(), nullable=True),
        sa.Column('meta_confidence', sa.Float(), nullable=True),
    )

    op.create_table(
        'comments',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('review_id', sa.String(), sa.ForeignKey('reviews.id'), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('persona_id', sa.String(), nullable=False),
        sa.Column('persona_name', sa.String(), nullable=False),
        sa.Column('persona_color', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('start_line', sa.Integer(), nullable=False),
        sa.Column('end_line', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime()),
    )

    op.create_table(
        'meta_comments',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('review_id', sa.String(), sa.ForeignKey('reviews.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('start_line', sa.Integer(), nullable=False),
        sa.Column('end_line', sa.Integer(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table('meta_comments')
    op.drop_table('comments')
    op.drop_table('reviews')
    op.drop_table('review_jobs')
    op.drop_table('personas')
    op.drop_table('documents')
