"""make recipe versions immutable

Revision ID: ceebbd0a8326
Revises: 21d0866c5841
Create Date: 2026-09-12 10:50:34.506555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ceebbd0a8326'
down_revision: Union[str, Sequence[str], None] = '21d0866c5841'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE FUNCTION guard_version_immutability() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'recipe versions are immutable'
                USING ERRCODE = 'integrity_constraint_violation';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    for table in ("recipe_versions", "recipe_version_ingredients", "recipe_version_instructions"):
        op.execute(
            f"""
            CREATE TRIGGER no_{table}_update
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION guard_version_immutability()
            """
        )


def downgrade() -> None:
    """Downgrade schema."""
    for table in ("recipe_versions", "recipe_version_ingredients", "recipe_version_instructions"):
        op.execute(f"DROP TRIGGER IF EXISTS no_{table}_update ON {table}")
    op.execute("DROP FUNCTION IF EXISTS guard_version_immutability()")
