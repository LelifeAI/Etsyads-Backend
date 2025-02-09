"""Fix users schema

Revision ID: 227b1d8e7902
Revises: 0f201023ac7b
Create Date: 2025-01-28 11:51:47.215451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '227b1d8e7902'
down_revision: Union[str, None] = '0f201023ac7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tạo bảng tạm với schema cập nhật
    op.create_table(
        "users_temp",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String, nullable=False),  # NOT NULL
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("is_admin", sa.Boolean, nullable=False, default=False),  # DEFAULT 0
        sa.Column("is_verified", sa.Boolean, nullable=False, default=False),  # DEFAULT 0
    )
    # Sao chép dữ liệu từ bảng cũ sang bảng tạm
    op.execute(
        """
        INSERT INTO users_temp (id, username, email, hashed_password, is_admin, is_verified)
        SELECT id, username, email, hashed_password, 
               COALESCE(is_admin, 0), COALESCE(is_verified, 0)
        FROM users
        """
    )
    # Xóa bảng cũ
    op.drop_table("users")
    # Đổi tên bảng tạm thành bảng chính
    op.rename_table("users_temp", "users")


def downgrade() -> None:
    # Khôi phục schema cũ nếu cần
    op.create_table(
        "users_old",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String, nullable=True),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("is_admin", sa.Boolean, nullable=True),
        sa.Column("is_verified", sa.Boolean, nullable=True),
    )
    # Chuyển dữ liệu trở lại bảng cũ
    op.execute(
        """
        INSERT INTO users_old (id, username, email, hashed_password, is_admin, is_verified)
        SELECT id, username, email, hashed_password, is_admin, is_verified
        FROM users
        """
    )
    # Xóa bảng cập nhật
    op.drop_table("users")
    # Đổi tên bảng cũ trở lại
    op.rename_table("users_old", "users")
