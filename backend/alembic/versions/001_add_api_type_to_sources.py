"""add api_type to sources

Revision ID: 001
Revises: 
Create Date: 2026-01-05 10:00:00.000000

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
    # Add api_type column (nullable first to allow existing data)
    op.add_column('sources', sa.Column('api_type', sa.String(length=64), nullable=True))
    
    # Update existing rows with default value
    op.execute("UPDATE sources SET api_type = 'finnhub' WHERE api_type IS NULL")
    
    # Make api_type non-nullable
    op.alter_column('sources', 'api_type', nullable=False)
    
    # Drop url column if it exists
    try:
        op.drop_constraint('sources_url_key', 'sources', type_='unique')
    except:
        pass  # Constraint might not exist
    
    try:
        op.drop_column('sources', 'url')
    except:
        pass  # Column might not exist


def downgrade() -> None:
    # Add url column back
    op.add_column('sources', sa.Column('url', sa.String(length=1024), nullable=True))
    
    # Drop api_type column
    op.drop_column('sources', 'api_type')
