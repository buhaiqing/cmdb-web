"""关系类型定义"""

from enum import Enum


class RelationType(str, Enum):
    """配置项关系类型"""

    # 依赖关系
    DEPENDS_ON = "depends_on"  # 依赖于
    REQUIRED_BY = "required_by"  # 被需要

    # 连接关系
    CONNECTS_TO = "connects_to"  # 连接到
    LINKED_TO = "linked_to"  # 关联到

    # 运行关系
    RUNS_ON = "runs_on"  # 运行在
    HOSTS = "hosts"  # 托管

    # 数据关系
    READS_FROM = "reads_from"  # 从...读取
    WRITES_TO = "writes_to"  # 写入到

    # 管理关系
    MANAGES = "manages"  # 管理
    MANAGED_BY = "managed_by"  # 被管理

    # 部署关系
    DEPLOYS_TO = "deploys_to"  # 部署到
    DEPLOYED_ON = "deployed_on"  # 部署在

    # 网络关系
    ROUTES_TO = "routes_to"  # 路由到
    BALANCES = "balances"  # 负载均衡

    # 存储关系
    STORES_IN = "stores_in"  # 存储在
    CONTAINS = "contains"  # 包含

    # 继承关系
    EXTENDS = "extends"  # 扩展
    INHERITS_FROM = "inherits_from"  # 继承自


# 关系类型描述
RELATION_TYPE_DESCRIPTIONS = {
    RelationType.DEPENDS_ON: "源 CI 依赖于目标 CI",
    RelationType.REQUIRED_BY: "源 CI 被目标 CI 需要",
    RelationType.CONNECTS_TO: "源 CI 连接到目标 CI",
    RelationType.LINKED_TO: "源 CI 与目标 CI 关联",
    RelationType.RUNS_ON: "源 CI 运行在目标 CI 上",
    RelationType.HOSTS: "源 CI 托管目标 CI",
    RelationType.READS_FROM: "源 CI 从目标 CI 读取数据",
    RelationType.WRITES_TO: "源 CI 向目标 CI 写入数据",
    RelationType.MANAGES: "源 CI 管理目标 CI",
    RelationType.MANAGED_BY: "源 CI 被目标 CI 管理",
    RelationType.DEPLOYS_TO: "源 CI 部署到目标 CI",
    RelationType.DEPLOYED_ON: "源 CI 部署在目标 CI 上",
    RelationType.ROUTES_TO: "源 CI 路由到目标 CI",
    RelationType.BALANCES: "源 CI 负载均衡目标 CI",
    RelationType.STORES_IN: "源 CI 存储在目标 CI",
    RelationType.CONTAINS: "源 CI 包含目标 CI",
    RelationType.EXTENDS: "源 CI 扩展目标 CI",
    RelationType.INHERITS_FROM: "源 CI 继承自目标 CI",
}
