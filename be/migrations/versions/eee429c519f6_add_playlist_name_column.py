"""Add playlist name column

Revision ID: eee429c519f6
Revises: 2cb0cd4da1b3
Create Date: 2024-11-24 12:01:11.254543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eee429c519f6'
down_revision: Union[str, None] = '2cb0cd4da1b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('playlist', sa.Column('name', sa.String(length=255), nullable=False))
    op.create_unique_constraint(None, 'playlist', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'playlist', type_='unique')
    op.drop_column('playlist', 'name')
    # ### end Alembic commands ###