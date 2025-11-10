"""drop article table

Revision ID: d708480feb25
Revises: efa29385c571
Create Date: 2025-11-10 09:24:45.084153

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd708480feb25'
down_revision: Union[str, None] = 'efa29385c571'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table('articles')

def downgrade():
    # Falls du rollback willst, Tabelle wieder erstellen
    op.create_table(
        'table_name',
        sa.Column('id', sa.Integer(), primary_key=True),
        # ... andere Columns
    )

