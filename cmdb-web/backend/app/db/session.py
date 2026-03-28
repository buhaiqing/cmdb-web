"""数据库会话配置"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings


# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 连接前测试
    pool_size=20,  # 连接池大小
    max_overflow=40,  # 最大溢出连接数
    pool_recycle=3600,  # 连接回收时间 (秒)
    echo=settings.DEBUG,  # 调试模式输出 SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话依赖项"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """初始化数据库表"""
    from app.models.base import Base

    Base.metadata.create_all(bind=engine)
