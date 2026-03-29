"""配置项相关 Schemas"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


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


class RelationType(str, Enum):
    """关系类型"""

    DEPENDS_ON = "depends_on"
    REQUIRED_BY = "required_by"
    CONNECTS_TO = "connects_to"
    RUNS_ON = "runs_on"
    HOSTS = "hosts"
    READS_FROM = "reads_from"
    WRITES_TO = "writes_to"
    MANAGES = "manages"
    MANAGED_BY = "managed_by"
    DEPLOYS_TO = "deploys_to"
    DEPLOYED_ON = "deployed_on"
    CONTAINS = "contains"


# ==================== 配置项基础 Schemas ====================


class CIBase(BaseModel):
    """配置项基础 Schema"""

    name: str = Field(..., min_length=1, max_length=100, description="配置项名称")
    code: str = Field(..., min_length=1, max_length=100, description="配置项代码")
    description: Optional[str] = Field(None, description="配置项描述")
    status: CIStatus = Field(default=CIStatus.ONLINE, description="状态")
    environment: str = Field(..., min_length=1, max_length=50, description="环境")
    owner: Optional[str] = Field(None, max_length=100, description="负责人")
    tags: Optional[Dict[str, Any]] = Field(None, description="标签")


class CICreate(CIBase):
    """创建配置项请求"""

    model_config = ConfigDict(extra="allow")

    ci_type: CIType = Field(..., description="配置项类型")


class CIUpdate(BaseModel):
    """更新配置项请求"""

    name: Optional[str] = Field(None, max_length=100, description="配置项名称")
    description: Optional[str] = Field(None, description="配置项描述")
    status: Optional[CIStatus] = Field(None, description="状态")
    environment: Optional[str] = Field(None, max_length=50, description="环境")
    owner: Optional[str] = Field(None, max_length=100, description="负责人")
    tags: Optional[Dict[str, Any]] = Field(None, description="标签")


class CIResponse(CIBase):
    """配置项响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="配置项 ID")
    ci_type: CIType = Field(..., description="配置项类型")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class CIListResponse(BaseModel):
    """配置项列表响应"""

    items: List[CIResponse] = Field(..., description="配置项列表")
    total: int = Field(..., description="总数")


# ==================== 配置项搜索 ====================


class CISearchRequest(BaseModel):
    """配置项搜索请求"""

    ci_type: Optional[CIType] = Field(None, description="配置项类型")
    name: Optional[str] = Field(None, description="名称（模糊匹配）")
    code: Optional[str] = Field(None, description="代码（模糊匹配）")
    status: Optional[CIStatus] = Field(None, description="状态")
    environment: Optional[str] = Field(None, description="环境")
    owner: Optional[str] = Field(None, description="负责人")
    tags: Optional[Dict[str, Any]] = Field(None, description="标签")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页大小")


# ==================== 配置项关系 Schemas ====================


class CIRelationBase(BaseModel):
    """配置项关系基础 Schema"""

    relation_type: str = Field(..., min_length=2, max_length=50, description="关系类型")
    description: Optional[str] = Field(None, max_length=255, description="关系描述")


class CIRelationCreate(CIRelationBase):
    """创建配置项关系请求"""

    source_ci_id: int = Field(..., description="源配置项 ID")
    target_ci_id: int = Field(..., description="目标配置项 ID")


class CIRelationResponse(CIRelationBase):
    """配置项关系响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="关系 ID")
    source_ci_id: int = Field(..., description="源配置项 ID")
    target_ci_id: int = Field(..., description="目标配置项 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ==================== 具体 CI 类型 Schemas ====================


class ServerCI(BaseModel):
    """服务器配置项 Schema"""

    model_config = ConfigDict(from_attributes=True)

    ci_id: int = Field(..., description="配置项 ID")
    hostname: str = Field(..., description="主机名")
    ip_address: str = Field(..., description="IP 地址")
    os_type: str = Field(..., description="操作系统类型")
    os_version: Optional[str] = Field(None, description="操作系统版本")
    cpu_cores: Optional[int] = Field(None, description="CPU 核心数")
    memory_gb: Optional[int] = Field(None, description="内存大小 (GB)")
    disk_gb: Optional[int] = Field(None, description="磁盘大小 (GB)")
    cloud_provider: Optional[str] = Field(None, description="云服务商")
    instance_type: Optional[str] = Field(None, description="实例类型")


class NetworkDeviceCI(BaseModel):
    """网络设备配置项 Schema"""

    model_config = ConfigDict(from_attributes=True)

    ci_id: int = Field(..., description="配置项 ID")
    device_type: str = Field(..., description="设备类型")
    vendor: str = Field(..., description="厂商")
    model: str = Field(..., description="型号")
    serial_number: Optional[str] = Field(None, description="序列号")
    firmware_version: Optional[str] = Field(None, description="固件版本")
    management_ip: str = Field(..., description="管理 IP")
    location: Optional[str] = Field(None, description="位置")


class DatabaseCI(BaseModel):
    """数据库配置项 Schema"""

    model_config = ConfigDict(from_attributes=True)

    ci_id: int = Field(..., description="配置项 ID")
    db_type: str = Field(..., description="数据库类型")
    version: Optional[str] = Field(None, description="版本")
    host: str = Field(..., description="主机")
    port: int = Field(..., description="端口")
    database_name: Optional[str] = Field(None, description="数据库名")
    is_cluster: bool = Field(default=False, description="是否集群")


class MiddlewareCI(BaseModel):
    """中间件配置项 Schema"""

    model_config = ConfigDict(from_attributes=True)

    ci_id: int = Field(..., description="配置项 ID")
    mw_type: str = Field(..., description="中间件类型")
    version: Optional[str] = Field(None, description="版本")
    host: str = Field(..., description="主机")
    port: int = Field(..., description="端口")


class ApplicationCI(BaseModel):
    """应用配置项 Schema"""

    model_config = ConfigDict(from_attributes=True)

    ci_id: int = Field(..., description="配置项 ID")
    app_type: str = Field(..., description="应用类型")
    language: Optional[str] = Field(None, description="编程语言")
    framework: Optional[str] = Field(None, description="框架")
    version: Optional[str] = Field(None, description="版本")
    git_repo: Optional[str] = Field(None, description="Git 仓库")
    health_check_path: Optional[str] = Field(None, description="健康检查路径")


class ContainerCI(BaseModel):
    """容器配置项 Schema"""

    model_config = ConfigDict(from_attributes=True)

    ci_id: int = Field(..., description="配置项 ID")
    container_id: str = Field(..., description="容器 ID")
    image: str = Field(..., description="镜像")
    host_server_id: Optional[int] = Field(None, description="宿主机 ID")
    cpu_limit: Optional[float] = Field(None, description="CPU 限制")
    memory_limit_mb: Optional[int] = Field(None, description="内存限制 (MB)")


class K8sResourceCI(BaseModel):
    """K8s 资源配置项 Schema"""

    model_config = ConfigDict(from_attributes=True)

    ci_id: int = Field(..., description="配置项 ID")
    resource_type: str = Field(..., description="资源类型")
    namespace: str = Field(..., description="命名空间")
    cluster_name: str = Field(..., description="集群名称")


class CloudResourceCI(BaseModel):
    """云资源配置项 Schema"""

    model_config = ConfigDict(from_attributes=True)

    ci_id: int = Field(..., description="配置项 ID")
    cloud_provider: str = Field(..., description="云服务商")
    resource_type: str = Field(..., description="资源类型")
    region: str = Field(..., description="区域")
    zone: Optional[str] = Field(None, description="可用区")
    cloud_resource_id: str = Field(..., description="云资源 ID")
    billing_type: Optional[str] = Field(None, description="计费类型")
    expiration_date: Optional[datetime] = Field(None, description="过期时间")
