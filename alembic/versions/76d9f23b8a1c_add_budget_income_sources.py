"""add budget income sources

Revision ID: 76d9f23b8a1c
Revises: 52785a1ed36e
Create Date: 2026-05-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '76d9f23b8a1c'
down_revision: Union[str, Sequence[str], None] = '52785a1ed36e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'budget_income_sources',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('yearly_budget_id', sa.Uuid(), nullable=True),
        sa.Column('dcc_budget_id', sa.Uuid(), nullable=True),
        sa.Column('local_church_budget_id', sa.Uuid(), nullable=True),
        sa.Column('source_type', sqlmodel.sql.sqltypes.AutoString(),
                  nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(),
                  nullable=True),
        sa.Column('received_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['yearly_budget_id'], ['yearly_budgets.id'], ),
        sa.ForeignKeyConstraint(['dcc_budget_id'], ['dcc_budgets.id'], ),
        sa.ForeignKeyConstraint(['local_church_budget_id'], [
                                'local_church_budgets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_budget_income_sources_yearly_budget_id'),
                    'budget_income_sources', ['yearly_budget_id'], unique=False)
    op.create_index(op.f('ix_budget_income_sources_dcc_budget_id'),
                    'budget_income_sources', ['dcc_budget_id'], unique=False)
    op.create_index(op.f('ix_budget_income_sources_local_church_budget_id'),
                    'budget_income_sources', ['local_church_budget_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_budget_income_sources_local_church_budget_id'),
                  table_name='budget_income_sources')
    op.drop_index(op.f('ix_budget_income_sources_dcc_budget_id'),
                  table_name='budget_income_sources')
    op.drop_index(op.f('ix_budget_income_sources_yearly_budget_id'),
                  table_name='budget_income_sources')
    op.drop_table('budget_income_sources')
