"""create recipes and recipe_versions (with ingredient/instruction snapshots)

Revision ID: 21d0866c5841
Revises: 614080983b0b
Create Date: 2026-09-12 00:58:14.434245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21d0866c5841'
down_revision: Union[str, Sequence[str], None] = '614080983b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('recipes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('cuisine', sa.String(length=50), nullable=True),
    sa.Column('difficulty', sa.String(length=20), nullable=True),
    sa.Column('prep_time', sa.Integer(), nullable=True),
    sa.Column('cook_time', sa.Integer(), nullable=True),
    sa.Column('servings', sa.Integer(), nullable=True),
    sa.Column('forked_from_recipe_id', sa.Integer(), nullable=True),
    sa.Column('forked_from_version_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['forked_from_recipe_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipes_author_id'), 'recipes', ['author_id'], unique=False)
    op.create_index(op.f('ix_recipes_forked_from_recipe_id'), 'recipes', ['forked_from_recipe_id'], unique=False)
    op.create_table('recipe_versions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('version_number', sa.String(length=20), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('parent_version_id', sa.Integer(), nullable=True),
    sa.Column('change_description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['parent_version_id'], ['recipe_versions.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('recipe_id', 'version_number')
    )
    op.create_index(op.f('ix_recipe_versions_recipe_id'), 'recipe_versions', ['recipe_id'], unique=False)
    op.create_table('recipe_version_ingredients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('unit', sa.String(length=30), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['version_id'], ['recipe_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipe_version_ingredients_version_id'), 'recipe_version_ingredients', ['version_id'], unique=False)
    op.create_table('recipe_version_instructions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version_id', sa.Integer(), nullable=False),
    sa.Column('step_number', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['version_id'], ['recipe_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipe_version_instructions_version_id'), 'recipe_version_instructions', ['version_id'], unique=False)
    op.create_foreign_key('recipes_forked_from_version_id', 'recipes', 'recipe_versions',
                          ['forked_from_version_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('recipes_forked_from_version_id', 'recipes', type_='foreignkey')
    op.drop_index(op.f('ix_recipe_version_instructions_version_id'), table_name='recipe_version_instructions')
    op.drop_table('recipe_version_instructions')
    op.drop_index(op.f('ix_recipe_version_ingredients_version_id'), table_name='recipe_version_ingredients')
    op.drop_table('recipe_version_ingredients')
    op.drop_index(op.f('ix_recipe_versions_recipe_id'), table_name='recipe_versions')
    op.drop_table('recipe_versions')
    op.drop_index(op.f('ix_recipes_forked_from_recipe_id'), table_name='recipes')
    op.drop_index(op.f('ix_recipes_author_id'), table_name='recipes')
    op.drop_table('recipes')
