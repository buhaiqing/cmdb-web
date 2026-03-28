"""Alembic 脚本入口"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 导入所有模型
from app.models.base import Base
from app.models.user import User, Role, Permission, user_roles
from app.models.ci import (
    ConfigurationItem,
    ConfigurationItemRelation,
    Server,
    NetworkDevice,
    Database,
    Middleware,
    Application,
    Container,
    K8sResource,
    CloudResource,
    CIType,
    CIStatus,
)
from app.models.relation import RelationType
from app.models.change import ChangeRecord, ChangeType, ChangeStatus, ChangePriority
from app.models.audit import AuditLog, AuditAction, AuditStatus

# 导入配置
from app.core.config import settings

# Alembic Config
config = context.config

# 设置数据库 URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 解释器日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 模型元数据
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式下运行迁移"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式下运行迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
