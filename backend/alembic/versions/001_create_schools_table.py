"""Create schools table

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create schools table."""
    op.create_table(
        'schools',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_schools_id'), 'schools', ['id'], unique=False)
    op.create_index(op.f('ix_schools_name'), 'schools', ['name'], unique=False)
    op.create_index(op.f('ix_schools_code'), 'schools', ['code'], unique=True)
    op.create_index(op.f('ix_schools_is_deleted'), 'schools', ['is_deleted'], unique=False)


def downgrade() -> None:
    """Drop schools table."""
    op.drop_index(op.f('ix_schools_is_deleted'), table_name='schools')
    op.drop_index(op.f('ix_schools_code'), table_name='schools')
    op.drop_index(op.f('ix_schools_name'), table_name='schools')
    op.drop_index(op.f('ix_schools_id'), table_name='schools')
    op.drop_table('schools')

