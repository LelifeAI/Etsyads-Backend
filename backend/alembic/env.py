import os
import sys


# Thêm thư mục gốc của dự án vào sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Đọc cấu hình Alembic
config = context.config

# Thiết lập logging từ tập tin cấu hình Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Thêm đường dẫn thư mục backend vào sys.path để tránh lỗi import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import models và Base (Đặt sau khi sys.path được cấu hình đúng)
from backend.etsyads.database import Base
from backend.etsyads import models

# Cập nhật metadata để Alembic có thể nhận diện được các bảng
target_metadata = Base.metadata

def run_migrations_offline():
    """Chạy migration trong chế độ 'offline'."""

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Chạy migration trong chế độ 'online'."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
