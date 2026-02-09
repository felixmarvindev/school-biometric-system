"""add_enrollment_composite_index

Revision ID: e1a2b3c4d5e6
Revises: 0bbdb6b76e88
Create Date: 2026-02-08

Add composite index on enrollment_sessions for efficient queries by student, device, status.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "e1a2b3c4d5e6"
down_revision: Union[str, None] = "0bbdb6b76e88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_enrollment_sessions_student_device_status",
        "enrollment_sessions",
        ["student_id", "device_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_enrollment_sessions_student_device_status",
        table_name="enrollment_sessions",
    )
