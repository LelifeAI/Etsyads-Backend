"""Fix user email field

Revision ID: a32721fb9c05
Revises: 2d116cde9960
Create Date: 2025-01-27 22:20:54.630373

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = 'a32721fb9c05'
down_revision = '2d116cde9960'
branch_labels = None
depends_on = None


def upgrade():
    # Tạo bảng tạm với ràng buộc chính xác
    op.create_table(
        'users_temp',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('username', sa.String, unique=True, index=True),
        sa.Column('email', sa.String, nullable=False, unique=True),  # Thêm NOT NULL ở đây
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('is_admin', sa.Boolean, default=False),
        sa.Column('is_verified', sa.Boolean, default=False)
    )

    # Sao chép dữ liệu từ bảng cũ sang bảng mới
    op.execute('INSERT INTO users_temp (id, username, email, hashed_password, is_admin, is_verified) '
               'SELECT id, username, email, hashed_password, is_admin, is_verified FROM users')

    # Xóa bảng cũ
    op.drop_table('users')

    # Đổi tên bảng mới thành tên cũ
    op.rename_table('users_temp', 'users')


def downgrade():
    # Khôi phục lại bảng users cũ mà không có ràng buộc NOT NULL
    op.create_table(
        'users_old',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('username', sa.String, unique=True, index=True),
        sa.Column('email', sa.String, unique=True),  # Xóa nullable=False
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('is_admin', sa.Boolean, default=False),
        sa.Column('is_verified', sa.Boolean, default=False)
    )

    # Sao chép dữ liệu về bảng cũ
    op.execute('INSERT INTO users_old (id, username, email, hashed_password, is_admin, is_verified) '
               'SELECT id, username, email, hashed_password, is_admin, is_verified FROM users')

    # Xóa bảng hiện tại
    op.drop_table('users')

    # Đổi tên bảng cũ về lại users
    op.rename_table('users_old', 'users')
