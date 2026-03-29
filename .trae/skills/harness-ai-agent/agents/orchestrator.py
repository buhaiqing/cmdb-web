"""Agent 编排器 - 协调多Agent协作.

实现多独立SubAgents架构，支持任务分配和跨Agent沟通协商。
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .approval_gateway import (
    ApprovalConfig,
    ApprovalGateway,
    ApprovalResult,
    get_approval_gateway,
)
from .base import AgentResult, BaseAgent


class TaskStatus(str, Enum):
    """任务状态."""
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(str, Enum):
    """消息类型."""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_RESULT = "task_result"
    AGENT_STATUS = "agent_status"
    COORDINATION = "coordination"
    BROADCAST = "broadcast"


@dataclass
class AgentCapability:
    """Agent能力定义."""
    name: str
    description: str
    input_types: list[str]
    output_types: list[str]
    confidence_threshold: float = 0.8


class AgentRegistration(BaseModel):
    """Agent注册信息."""
    agent_id: str
    agent_type: str
    capabilities: list[AgentCapability]
    endpoint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)


class TaskDefinition(BaseModel):
    """任务定义."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    agent_type: str
    input_data: dict[str, Any]
    dependencies: list[UUID] = Field(default_factory=list)
    requires_approval: bool = False
    confidence_threshold: float = 0.85
    timeout_seconds: int = 300
    retry_count: int = 3
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    """任务结果."""
    task_id: UUID
    agent_id: str
    status: TaskStatus
    result: dict[str, Any] | None = None
    error: str | None = None
    confidence: float = 0.0
    execution_time_ms: int = 0
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class AgentMessage(BaseModel):
    """Agent间消息."""
    id: UUID = Field(default_factory=uuid4)
    type: MessageType
    sender: str
    recipient: str | None = None  # None表示广播
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: UUID | None = None


class WorkflowDefinition(BaseModel):
    """工作流定义."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    tasks: list[TaskDefinition]
    parallel_groups: list[list[UUID]] = Field(default_factory=list)
    global_approval_config: ApprovalConfig | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowResult(BaseModel):
    """工作流结果."""
    workflow_id: UUID
    status: TaskStatus
    task_results: dict[UUID, TaskResult]
    execution_time_ms: int
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class MessageBus:
    """Agent消息总线.

    实现SubAgents间的直接通信机制，支持:
    - 点对点消息
    - 广播消息
    - 消息持久化
    - 订阅/发布模式
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable[[AgentMessage], Coroutine]]] = {}
        self._message_history: list[AgentMessage] = []
        self._max_history = 1000

    async def publish(self, message: AgentMessage) -> None:
        """发布消息."""
        self._message_history.append(message)

        # 限制历史记录大小
        if len(self._message_history) > self._max_history:
            self._message_history = self._message_history[-self._max_history:]

        # 广播或点对点发送
        if message.recipient is None:
            # 广播
            for handlers in self._subscribers.values():
                for handler in handlers:
                    asyncio.create_task(self._safe_handle(handler, message))
        else:
            # 点对点
            handlers = self._subscribers.get(message.recipient, [])
            for handler in handlers:
                asyncio.create_task(self._safe_handle(handler, message))

    async def subscribe(
        self,
        agent_id: str,
        handler: Callable[[AgentMessage], Coroutine],
    ) -> None:
        """订阅消息."""
        if agent_id not in self._subscribers:
            self._subscribers[agent_id] = []
        self._subscribers[agent_id].append(handler)

    async def unsubscribe(
        self,
        agent_id: str,
        handler: Callable[[AgentMessage], Coroutine],
    ) -> None:
        """取消订阅."""
        if agent_id in self._subscribers:
            self._subscribers[agent_id] = [
                h for h in self._subscribers[agent_id] if h != handler
            ]

    def get_message_history(
        self,
        agent_id: str | None = None,
        message_type: MessageType | None = None,
        limit: int = 100,
    ) -> list[AgentMessage]:
        """获取消息历史."""
        messages = self._message_history

        if agent_id:
            messages = [
                m for m in messages
                if m.sender == agent_id or m.recipient == agent_id
            ]

        if message_type:
            messages = [m for m in messages if m.type == message_type]

        return messages[-limit:]

    async def _safe_handle(
        self,
        handler: Callable[[AgentMessage], Coroutine],
        message: AgentMessage,
    ) -> None:
        """安全处理消息."""
        try:
            await handler(message)
        except Exception as e:
            # 记录错误但不影响其他处理器
            print(f"消息处理错误: {e}")


class AgentOrchestrator:
    """Agent编排器.

    核心职责:
    1. Agent注册与发现
    2. 任务分配与调度
    3. 跨Agent协作协调
    4. 工作流执行管理
    5. 人工确认集成

    使用示例:
        orchestrator = AgentOrchestrator()

        # 注册Agent
        orchestrator.register_agent("code-reviewer", code_review_agent)

        # 定义工作流
        workflow = WorkflowDefinition(
            name="代码审查工作流",
            tasks=[
                TaskDefinition(name="静态检查", agent_type="code-reviewer"),
                TaskDefinition(name="安全扫描", agent_type="security-scanner"),
            ],
        )

        # 执行工作流
        result = await orchestrator.execute_workflow(workflow, context)
    """

    def __init__(self):
        self.agents: dict[str, BaseAgent] = {}
        self.agent_registrations: dict[str, AgentRegistration] = {}
        self.message_bus = MessageBus()
        self.approval_gateway = get_approval_gateway()
        self._task_results: dict[UUID, TaskResult] = {}
        self._running_workflows: dict[UUID, asyncio.Task] = {}

    def register_agent(
        self,
        agent_id: str,
        agent: BaseAgent,
        capabilities: list[AgentCapability] | None = None,
    ) -> None:
        """注册Agent.

        Args:
            agent_id: Agent唯一标识
            agent: Agent实例
            capabilities: Agent能力列表
        """
        self.agents[agent_id] = agent

        registration = AgentRegistration(
            agent_id=agent_id,
            agent_type=agent.__class__.__name__,
            capabilities=capabilities or [],
        )
        self.agent_registrations[agent_id] = registration

        # 订阅消息
        asyncio.create_task(
            self.message_bus.subscribe(agent_id, self._create_message_handler(agent_id))
        )

    def unregister_agent(self, agent_id: str) -> None:
        """注销Agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
        if agent_id in self.agent_registrations:
            del self.agent_registrations[agent_id]

    def find_agents_by_capability(
        self,
        capability_name: str,
    ) -> list[AgentRegistration]:
        """根据能力查找Agent."""
        return [
            reg for reg in self.agent_registrations.values()
            if any(c.name == capability_name for c in reg.capabilities)
        ]

    async def execute_workflow(
        self,
        workflow: WorkflowDefinition,
        context: dict[str, Any],
    ) -> WorkflowResult:
        """执行工作流.

        Args:
            workflow: 工作流定义
            context: 执行上下文

        Returns:
            工作流执行结果
        """
        start_time = datetime.utcnow()
        task_results: dict[UUID, TaskResult] = {}

        # 构建任务依赖图
        dependency_graph = self._build_dependency_graph(workflow.tasks)

        # 按依赖顺序执行任务
        completed_tasks: set[UUID] = set()
        failed_tasks: set[UUID] = set()

        while len(completed_tasks) + len(failed_tasks) < len(workflow.tasks):
            # 找出可执行的任务 (依赖已完成)
            ready_tasks = [
                task for task in workflow.tasks
                if task.id not in completed_tasks
                and task.id not in failed_tasks
                and all(dep in completed_tasks for dep in task.dependencies)
            ]

            if not ready_tasks:
                break

            # 并行执行就绪任务
            task_futures = [
                self._execute_task_with_guardrails(task, context, workflow)
                for task in ready_tasks
            ]

            results = await asyncio.gather(*task_futures, return_exceptions=True)

            for task, result in zip(ready_tasks, results):
                if isinstance(result, Exception):
                    task_results[task.id] = TaskResult(
                        task_id=task.id,
                        agent_id="",
                        status=TaskStatus.FAILED,
                        error=str(result),
                    )
                    failed_tasks.add(task.id)
                else:
                    task_results[task.id] = result
                    if result.status == TaskStatus.COMPLETED:
                        completed_tasks.add(task.id)
                    else:
                        failed_tasks.add(task.id)

            # 广播进度更新
            await self.message_bus.publish(AgentMessage(
                type=MessageType.AGENT_STATUS,
                sender="orchestrator",
                recipient=None,
                payload={
                    "workflow_id": str(workflow.id),
                    "completed": len(completed_tasks),
                    "failed": len(failed_tasks),
                    "total": len(workflow.tasks),
                },
            ))

        # 确定工作流状态
        if failed_tasks:
            workflow_status = TaskStatus.FAILED
        elif len(completed_tasks) == len(workflow.tasks):
            workflow_status = TaskStatus.COMPLETED
        else:
            workflow_status = TaskStatus.CANCELLED

        execution_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        return WorkflowResult(
            workflow_id=workflow.id,
            status=workflow_status,
            task_results=task_results,
            execution_time_ms=execution_time,
        )

    async def coordinate_agents(
        self,
        agent_ids: list[str],
        coordination_type: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """协调多个Agent协作.

        Args:
            agent_ids: Agent ID列表
            coordination_type: 协调类型
            context: 协调上下文

        Returns:
            协调结果
        """
        # 发送协调请求
        coordination_id = uuid4()

        for agent_id in agent_ids:
            await self.message_bus.publish(AgentMessage(
                type=MessageType.COORDINATION,
                sender="orchestrator",
                recipient=agent_id,
                payload={
                    "coordination_id": str(coordination_id),
                    "type": coordination_type,
                    "context": context,
                },
            ))

        # 等待响应 (简化实现)
        await asyncio.sleep(1)

        return {"coordination_id": str(coordination_id), "status": "initiated"}

    async def _execute_task_with_guardrails(
        self,
        task: TaskDefinition,
        context: dict[str, Any],
        workflow: WorkflowDefinition,
    ) -> TaskResult:
        """执行任务 (带保护机制)."""
        start_time = datetime.utcnow()

        # 查找合适的Agent
        agent = self._select_agent_for_task(task)
        if not agent:
            return TaskResult(
                task_id=task.id,
                agent_id="",
                status=TaskStatus.FAILED,
                error=f"未找到适合任务 {task.name} 的Agent",
            )

        try:
            # 执行Agent
            result = await asyncio.wait_for(
                agent.execute(context),
                timeout=task.timeout_seconds,
            )

            execution_time = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            # 检查置信度
            if result.confidence < task.confidence_threshold:
                if task.requires_approval:
                    # 需要人工确认
                    approval_result = await self._request_task_approval(
                        task, result, workflow
                    )

                    if approval_result.status.value != "approved":
                        return TaskResult(
                            task_id=task.id,
                            agent_id=agent.name,
                            status=TaskStatus.FAILED,
                            error=f"任务未通过审批: {approval_result.status}",
                            confidence=result.confidence,
                            execution_time_ms=execution_time,
                        )

            return TaskResult(
                task_id=task.id,
                agent_id=agent.name,
                status=TaskStatus.COMPLETED if result.success else TaskStatus.FAILED,
                result=result.data,
                error=result.error,
                confidence=result.confidence,
                execution_time_ms=execution_time,
            )

        except asyncio.TimeoutError:
            return TaskResult(
                task_id=task.id,
                agent_id=agent.name,
                status=TaskStatus.FAILED,
                error="任务执行超时",
            )
        except Exception as e:
            return TaskResult(
                task_id=task.id,
                agent_id=agent.name,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    def _select_agent_for_task(self, task: TaskDefinition) -> BaseAgent | None:
        """为任务选择合适的Agent."""
        for agent_id, registration in self.agent_registrations.items():
            if registration.agent_type == task.agent_type:
                return self.agents.get(agent_id)
        return None

    async def _request_task_approval(
        self,
        task: TaskDefinition,
        agent_result: AgentResult,
        workflow: WorkflowDefinition,
    ) -> ApprovalResult:
        """请求任务审批."""
        config = workflow.global_approval_config or ApprovalConfig()

        approval_request = await self.approval_gateway.request_approval(
            action=f"workflow_task:{task.name}",
            context={
                "workflow_id": str(workflow.id),
                "task_id": str(task.id),
                "task_name": task.name,
                "agent_result": agent_result.data,
            },
            confidence=agent_result.confidence,
            requester="orchestrator",
            config=config,
        )

        return await self.approval_gateway.wait_for_approval(
            approval_request.id,
            timeout=config.timeout,
        )

    def _build_dependency_graph(
        self,
        tasks: list[TaskDefinition],
    ) -> dict[UUID, list[UUID]]:
        """构建任务依赖图."""
        return {task.id: task.dependencies for task in tasks}

    def _create_message_handler(
        self,
        agent_id: str,
    ) -> Callable[[AgentMessage], Coroutine]:
        """创建消息处理器."""
        async def handler(message: AgentMessage) -> None:
            # 处理消息
            agent = self.agents.get(agent_id)
            if agent:
                # 可扩展: 调用Agent的消息处理方法
                pass
        return handler


# 全局编排器实例
_orchestrator: AgentOrchestrator | None = None


def get_orchestrator() -> AgentOrchestrator:
    """获取编排器实例."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
