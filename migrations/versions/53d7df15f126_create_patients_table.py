"""create patients table

Revision ID: 53d7df15f126
Revises:
Create Date: 2026-09-28 22:49:17.580264

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "53d7df15f126"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS patients")

    op.create_table(
        "patients",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("tipo_documento", sa.String(length=20), nullable=False),
        sa.Column("numero_documento", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("fecha_nacimiento", sa.Date(), nullable=False),
        sa.Column("telefono", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("direccion", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="patients",
    )

    op.create_index(
        op.f("ix_patients_patients_numero_documento"),
        "patients",
        ["numero_documento"],
        unique=True,
        schema="patients",
    )

    op.create_index(
        op.f("ix_patients_patients_user_id"),
        "patients",
        ["user_id"],
        unique=True,
        schema="patients",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_patients_patients_user_id"),
        table_name="patients",
        schema="patients",
    )

    op.drop_index(
        op.f("ix_patients_patients_numero_documento"),
        table_name="patients",
        schema="patients",
    )

    op.drop_table(
        "patients",
        schema="patients",
    )

    op.execute("DROP SCHEMA IF EXISTS patients")
