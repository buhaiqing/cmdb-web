"""配置项 (CI) 模型"""

from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    Column,
    Enum as SQLEnum,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import Enum
from datetime import datetime
from app.models.base import Base, TimestampMixin


class CIStatus(str, Enum):
    """配置项状态"""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class CIType(str, Enum):
    """配置项类型"""

    SERVER = "server"
    NETWORK_DEVICE = "network_device"
    DATABASE = "database"
    MIDDLEWARE = "middleware"
    APPLICATION = "application"
    CONTAINER = "container"
    K8S_RESOURCE = "k8s_resource"
    CLOUD_RESOURCE = "cloud_resource"


class ConfigurationItem(Base, TimestampMixin):
    """配置项基类模型"""

    __tablename__ = "t_configuration_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ci_type: Mapped[CIType] = mapped_column(
        SQLEnum(CIType), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CIStatus] = mapped_column(
        SQLEnum(CIStatus), default=CIStatus.ONLINE, nullable=False
    )
    environment: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)  # JSON 字符串存储标签

    # 关系
    relations = relationship(
        "ConfigurationItemRelation",
        foreign_keys="ConfigurationItemRelation.source_ci_id",
        back_populates="source_ci",
    )
    target_relations = relationship(
        "ConfigurationItemRelation",
        foreign_keys="ConfigurationItemRelation.target_ci_id",
        back_populates="target_ci",
    )
    change_records = relationship("ChangeRecord", back_populates="configuration_item")

    def __repr__(self) -> str:
        return f"<CI(id={self.id}, code={self.code}, type={self.ci_type})>"


class ConfigurationItemRelation(Base, TimestampMixin):
    """配置项关系模型"""

    __tablename__ = "t_configuration_item_relation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_ci_id: Mapped[int] = mapped_column(
        ForeignKey("t_configuration_item.id", ondelete="CASCADE"), nullable=False
    )
    target_ci_id: Mapped[int] = mapped_column(
        ForeignKey("t_configuration_item.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 关系
    source_ci = relationship(
        "ConfigurationItem",
        foreign_keys=[source_ci_id],
        back_populates="relations",
    )
    target_ci = relationship(
        "ConfigurationItem",
        foreign_keys=[target_ci_id],
        back_populates="target_relations",
    )

    def __repr__(self) -> str:
        return f"<CIRelation(id={self.id}, source={self.source_ci_id}, target={self.target_ci_id})>"


# ==================== 具体 CI 类型模型 ====================


class Server(Base, TimestampMixin):
    """服务器配置项"""

    __tablename__ = "t_ci_server"

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_configuration_item.id"), primary_key=True
    )
    hostname: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)  # 支持 IPv6
    os_type: Mapped[str] = mapped_column(String(50), nullable=False)
    os_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cpu_cores: Mapped[int | None] = mapped_column(Integer, nullable=True)
    memory_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disk_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cloud_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    instance_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<Server(hostname={self.hostname}, ip={self.ip_address})>"


class NetworkDevice(Base, TimestampMixin):
    """网络设备配置项"""

    __tablename__ = "t_ci_network_device"

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_configuration_item.id"), primary_key=True
    )
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)  # router, switch, firewall
    vendor: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    firmware_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    management_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)

    def __repr__(self) -> str:
        return f"<NetworkDevice(device_type={self.device_type}, vendor={self.vendor})>"


class Database(Base, TimestampMixin):
    """数据库配置项"""

    __tablename__ = "t_ci_database"

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_configuration_item.id"), primary_key=True
    )
    db_type: Mapped[str] = mapped_column(String(50), nullable=False)  # mysql, postgresql, mongodb
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    database_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    master_ci_id: Mapped[int | None] = mapped_column(
        ForeignKey("t_ci_database.id"), nullable=True
    )
    is_cluster: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Database(db_type={self.db_type}, host={self.host})>"


class Middleware(Base, TimestampMixin):
    """中间件配置项"""

    __tablename__ = "t_ci_middleware"

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_configuration_item.id"), primary_key=True
    )
    mw_type: Mapped[str] = mapped_column(String(50), nullable=False)  # redis, kafka, rabbitmq, nginx
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<Middleware(type={self.mw_type}, host={self.host})>"


class Application(Base, TimestampMixin):
    """应用配置项"""

    __tablename__ = "t_ci_application"

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_configuration_item.id"), primary_key=True
    )
    app_type: Mapped[str] = mapped_column(String(50), nullable=False)  # web, api, worker
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    framework: Mapped[str | None] = mapped_column(String(100), nullable=True)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    git_repo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    health_check_path: Mapped[str | None] = mapped_column(String(200), nullable=True)

    def __repr__(self) -> str:
        return f"<Application(name={self.code}, type={self.app_type})>"


class Container(Base, TimestampMixin):
    """容器配置项"""

    __tablename__ = "t_ci_container"

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_configuration_item.id"), primary_key=True
    )
    container_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    image: Mapped[str] = mapped_column(String(255), nullable=False)
    host_server_id: Mapped[int | None] = mapped_column(
        ForeignKey("t_ci_server.id"), nullable=True
    )
    cpu_limit: Mapped[float | None] = mapped_column(nullable=True)
    memory_limit_mb: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<Container(id={self.container_id}, image={self.image})>"


class K8sResource(Base, TimestampMixin):
    """K8s 资源配置项"""

    __tablename__ = "t_ci_k8s_resource"

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_configuration_item.id"), primary_key=True
    )
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pod, deployment, service
    namespace: Mapped[str] = mapped_column(String(100), nullable=False)
    cluster_name: Mapped[str] = mapped_column(String(100), nullable=False)
    yaml_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<K8sResource(type={self.resource_type}, namespace={self.namespace})>"


class CloudResource(Base, TimestampMixin):
    """云资源配置项"""

    __tablename__ = "t_ci_cloud_resource"

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_configuration_item.id"), primary_key=True
    )
    cloud_provider: Mapped[str] = mapped_column(String(50), nullable=False)  # aliyun, aws
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(50), nullable=False)
    zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cloud_resource_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    billing_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # pay_as_you_go, subscription
    expiration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<CloudResource(provider={self.cloud_provider}, type={self.resource_type})>"
