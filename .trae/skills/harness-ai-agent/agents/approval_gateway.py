"""人工确认网关 - 确保关键操作需人工审批.

该模块实现宪章要求的人工确认机制，防止未授权操作。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Coroutine
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    """审批状态."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    """风险等级."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalChannel(str, Enum):
    """审批渠道."""
    WEB = "web"
    SLACK = "slack"
    EMAIL = "email"
    MOBILE = "mobile"


@dataclass
class ApprovalConfig:
    """审批配置."""
    min_confidence: float = 0.85
    timeout: timedelta = field(default_factory=lambda: timedelta(hours=24))
    approvers: list[str] = field(default_factory=list)
    require_all_approvers: bool = False
    channels: list[ApprovalChannel] = field(
        default_factory=lambda: [ApprovalChannel.WEB, ApprovalChannel.SLACK]
    )
    auto_escalate: bool = True
    escalation_delay: timedelta = field(default_factory=lambda: timedelta(hours=2))


class ApprovalRequest(BaseModel):
    """审批请求模型."""
    id: UUID = Field(default_factory=uuid4)
    action: str
    context: dict[str, Any]
    risk_level: RiskLevel
    confidence: float
    requester: str
    approvers: list[str]
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    approved_by: list[str] = Field(default_factory=list)
    rejected_by: list[str] = Field(default_factory=list)
    comments: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApprovalResult(BaseModel):
    """审批结果模型."""
    request_id: UUID
    status: ApprovalStatus
    approved_by: list[str]
    rejected_by: list[str]
    comments: list[dict[str, Any]]
    resolved_at: datetime
    escalation_triggered: bool = False


class ApprovalGateway:
    """人工确认网关.

    核心职责:
    1. 拦截低置信度AI决策
    2. 管理审批工作流
    3. 确保关键操作人工确认
    4. 审计日志记录

    使用示例:
        gateway = ApprovalGateway()

        # 检查是否需要审批
        if gateway.requires_approval(agent_result, config):
            result = await gateway.request_approval(
                action="deploy_to_production",
                context={"service": "myapp", "version": "v1.2.3"},
                config=approval_config,
            )

            if not result.status == ApprovalStatus.APPROVED:
                raise ApprovalRequiredError("部署需人工审批")
    """

    def __init__(self):
        self._pending_requests: dict[UUID, ApprovalRequest] = {}
        self._callbacks: dict[UUID, Callable[[ApprovalResult], Coroutine]] = {}
        self._notification_handlers: list[Callable[[ApprovalRequest], Coroutine]] = []

    def register_notification_handler(
        self,
        handler: Callable[[ApprovalRequest], Coroutine],
    ) -> None:
        """注册通知处理器."""
        self._notification_handlers.append(handler)

    def requires_approval(
        self,
        confidence: float,
        action: str,
        config: ApprovalConfig | None = None,
    ) -> bool:
        """判断是否需要人工审批.

        Args:
            confidence: AI决策置信度 (0-1)
            action: 操作类型
            config: 审批配置

        Returns:
            是否需要审批
        """
        cfg = config or ApprovalConfig()

        # 置信度低于阈值需要审批
        if confidence < cfg.min_confidence:
            return True

        # 高风险操作强制审批
        high_risk_actions = {
            "deploy_to_production",
            "auto_rollback",
            "database_migration",
            "delete_resource",
            "modify_security_policy",
        }
        if action in high_risk_actions:
            return True

        return False

    async def request_approval(
        self,
        action: str,
        context: dict[str, Any],
        confidence: float,
        requester: str,
        config: ApprovalConfig,
        risk_level: RiskLevel | None = None,
    ) -> ApprovalRequest:
        """发起审批请求.

        Args:
            action: 操作标识
            context: 操作上下文
            confidence: AI置信度
            requester: 请求人
            config: 审批配置
            risk_level: 风险等级 (自动计算 if None)

        Returns:
            审批请求对象
        """
        # 自动计算风险等级
        if risk_level is None:
            risk_level = self._calculate_risk_level(confidence, action)

        request = ApprovalRequest(
            action=action,
            context=context,
            risk_level=risk_level,
            confidence=confidence,
            requester=requester,
            approvers=config.approvers,
            expires_at=datetime.utcnow() + config.timeout,
            metadata={
                "require_all_approvers": config.require_all_approvers,
                "channels": [c.value for c in config.channels],
            },
        )

        self._pending_requests[request.id] = request

        # 发送通知
        await self._notify_approvers(request, config)

        # 启动超时检查
        asyncio.create_task(self._check_timeout(request.id, config.timeout))

        # 启动升级检查 (如启用)
        if config.auto_escalate:
            asyncio.create_task(
                self._check_escalation(request.id, config.escalation_delay)
            )

        return request

    async def approve(
        self,
        request_id: UUID,
        approver: str,
        comment: str | None = None,
    ) -> ApprovalResult:
        """审批通过.

        Args:
            request_id: 请求ID
            approver: 审批人
            comment: 审批意见

        Returns:
            审批结果
        """
        request = self._pending_requests.get(request_id)
        if not request:
            raise ValueError(f"审批请求不存在: {request_id}")

        if request.status != ApprovalStatus.PENDING:
            raise ValueError(f"审批请求状态错误: {request.status}")

        if approver not in request.approvers:
            raise ValueError(f"{approver} 不在审批人列表中")

        if approver in request.approved_by:
            raise ValueError(f"{approver} 已审批")

        # 记录审批
        request.approved_by.append(approver)
        if comment:
            request.comments.append({
                "approver": approver,
                "action": "approved",
                "comment": comment,
                "timestamp": datetime.utcnow().isoformat(),
            })

        # 检查是否满足审批条件
        require_all = request.metadata.get("require_all_approvers", False)

        if require_all:
            # 需要所有审批人通过
            if set(request.approved_by) >= set(request.approvers):
                request.status = ApprovalStatus.APPROVED
        else:
            # 只需任一审批人通过
            request.status = ApprovalStatus.APPROVED

        result = ApprovalResult(
            request_id=request_id,
            status=request.status,
            approved_by=request.approved_by,
            rejected_by=request.rejected_by,
            comments=request.comments,
            resolved_at=datetime.utcnow(),
        )

        # 触发回调
        if request_id in self._callbacks:
            await self._callbacks[request_id](result)

        return result

    async def reject(
        self,
        request_id: UUID,
        approver: str,
        reason: str,
    ) -> ApprovalResult:
        """拒绝审批.

        Args:
            request_id: 请求ID
            approver: 审批人
            reason: 拒绝原因

        Returns:
            审批结果
        """
        request = self._pending_requests.get(request_id)
        if not request:
            raise ValueError(f"审批请求不存在: {request_id}")

        if request.status != ApprovalStatus.PENDING:
            raise ValueError(f"审批请求状态错误: {request.status}")

        request.status = ApprovalStatus.REJECTED
        request.rejected_by.append(approver)
        request.comments.append({
            "approver": approver,
            "action": "rejected",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })

        result = ApprovalResult(
            request_id=request_id,
            status=ApprovalStatus.REJECTED,
            approved_by=request.approved_by,
            rejected_by=request.rejected_by,
            comments=request.comments,
            resolved_at=datetime.utcnow(),
        )

        # 触发回调
        if request_id in self._callbacks:
            await self._callbacks[request_id](result)

        return result

    async def wait_for_approval(
        self,
        request_id: UUID,
        timeout: timedelta | None = None,
    ) -> ApprovalResult:
        """等待审批完成.

        Args:
            request_id: 请求ID
            timeout: 超时时间

        Returns:
            审批结果
        """
        request = self._pending_requests.get(request_id)
        if not request:
            raise ValueError(f"审批请求不存在: {request_id}")

        # 如果已完成，直接返回
        if request.status in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED):
            return ApprovalResult(
                request_id=request_id,
                status=request.status,
                approved_by=request.approved_by,
                rejected_by=request.rejected_by,
                comments=request.comments,
                resolved_at=datetime.utcnow(),
            )

        # 创建 Future 等待回调
        future: asyncio.Future[ApprovalResult] = asyncio.get_event_loop().create_future()

        async def callback(result: ApprovalResult) -> None:
            if not future.done():
                future.set_result(result)

        self._callbacks[request_id] = callback

        try:
            result = await asyncio.wait_for(
                future,
                timeout=timeout.total_seconds() if timeout else None,
            )
            return result
        except asyncio.TimeoutError:
            request.status = ApprovalStatus.EXPIRED
            return ApprovalResult(
                request_id=request_id,
                status=ApprovalStatus.EXPIRED,
                approved_by=request.approved_by,
                rejected_by=request.rejected_by,
                comments=request.comments,
                resolved_at=datetime.utcnow(),
            )
        finally:
            del self._callbacks[request_id]

    def get_request(self, request_id: UUID) -> ApprovalRequest | None:
        """获取审批请求."""
        return self._pending_requests.get(request_id)

    def list_pending_requests(
        self,
        approver: str | None = None,
    ) -> list[ApprovalRequest]:
        """列出待审批请求."""
        requests = [
            r for r in self._pending_requests.values()
            if r.status == ApprovalStatus.PENDING
        ]
        if approver:
            requests = [
                r for r in requests
                if approver in r.approvers and approver not in r.approved_by
            ]
        return requests

    def _calculate_risk_level(
        self,
        confidence: float,
        action: str,
    ) -> RiskLevel:
        """计算风险等级."""
        critical_actions = {
            "delete_production_data",
            "modify_security_policy",
            "grant_admin_access",
        }
        high_risk_actions = {
            "deploy_to_production",
            "auto_rollback",
            "database_migration",
        }

        if action in critical_actions:
            return RiskLevel.CRITICAL
        if action in high_risk_actions or confidence < 0.5:
            return RiskLevel.HIGH
        if confidence < 0.75:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    async def _notify_approvers(
        self,
        request: ApprovalRequest,
        config: ApprovalConfig,
    ) -> None:
        """通知审批人."""
        for handler in self._notification_handlers:
            try:
                await handler(request)
            except Exception:
                # 通知失败不应影响主流程
                pass

    async def _check_timeout(
        self,
        request_id: UUID,
        timeout: timedelta,
    ) -> None:
        """检查超时."""
        await asyncio.sleep(timeout.total_seconds())

        request = self._pending_requests.get(request_id)
        if request and request.status == ApprovalStatus.PENDING:
            request.status = ApprovalStatus.EXPIRED

    async def _check_escalation(
        self,
        request_id: UUID,
        delay: timedelta,
    ) -> None:
        """检查是否需要升级."""
        await asyncio.sleep(delay.total_seconds())

        request = self._pending_requests.get(request_id)
        if request and request.status == ApprovalStatus.PENDING:
            # 触发升级逻辑
            request.metadata["escalated"] = True
            request.metadata["escalated_at"] = datetime.utcnow().isoformat()
            # 可扩展: 通知更高级别审批人


class ApprovalRequiredError(Exception):
    """需要审批异常."""
    pass


# 全局网关实例 (单例模式)
_approval_gateway: ApprovalGateway | None = None


def get_approval_gateway() -> ApprovalGateway:
    """获取审批网关实例."""
    global _approval_gateway
    if _approval_gateway is None:
        _approval_gateway = ApprovalGateway()
    return _approval_gateway
