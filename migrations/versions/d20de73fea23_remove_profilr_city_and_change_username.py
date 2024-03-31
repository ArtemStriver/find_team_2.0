"""remove_profilr-city_and_change_username

Revision ID: d20de73fea23
Revises: 2698cce1ca1e
Create Date: 2024-03-18 17:25:10.623755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d20de73fea23"
down_revision: Union[str, None] = "2698cce1ca1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "auth_user", "username", existing_type=sa.VARCHAR(), nullable=False
    )
    op.create_index(
        op.f("ix_auth_user_username"), "auth_user", ["username"], unique=True
    )
    op.add_column(
        "user_profile",
        sa.Column("hobbies", sa.String(length=50), nullable=False),
    )
    op.drop_column("user_profile", "city")
    op.drop_column("user_profile", "hobby")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user_profile",
        sa.Column(
            "hobby", sa.VARCHAR(length=50), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "user_profile",
        sa.Column("city", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_column("user_profile", "hobbies")
    op.drop_index(op.f("ix_auth_user_username"), table_name="auth_user")
    op.alter_column(
        "auth_user", "username", existing_type=sa.VARCHAR(), nullable=True
    )
    # ### end Alembic commands ###