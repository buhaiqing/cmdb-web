# Harness AI Agent Skill - 实现指南

> **说明**: 本文档包含SKILL.md中所有能力的具体实现方法，供开发者参考。  
> **对应**: SKILL.md中的What to do在此文档中提供How to do实现。

---

## 目录

1. [快速开始](#1-快速开始)
2. [项目结构](#2-项目结构)
3. [核心服务实现](#3-核心服务实现)
4. [Agent实现](#4-agent实现)
5. [核心组件实现](#5-核心组件实现)
6. [使用场景详解](#6-使用场景详解)
7. [配置参考](#7-配置参考)
8. [最佳实践](#8-最佳实践)
9. [故障排查](#9-故障排查)

---

## 1. 快速开始

### 1.1 安装与初始化

```bash
# 克隆 Skill 到项目
git clone https://github.com/your-org/harness-ai-agent-skill.git

# 或使用 submodule
git submodule add https://github.com/your-org/harness-ai-agent-skill.git
```

### 1.2 生成项目规范

```bash
# 交互式生成 AGENTS.md
python harness-ai-agent-skill/generator/agents_md_generator.py --interactive

# 或从配置文件生成
python harness-ai-agent-skill/generator/agents_md_generator.py --config project-config.yaml
```

### 1.3 配置Pipeline

```bash
# 复制 CI/CD Pipeline 模板
cp -r harness-ai-agent-skill/templates/pipelines/* ./.harness/pipelines/

# 配置环境变量
export HARNESS_API_KEY="your-api-key"
export HARNESS_ACCOUNT_ID="your-account-id"
export LLM_API_KEY="your-openai-key"
```

---

## 2. 项目结构

```
agents/
├── __init__.py
├── main.py                     # FastAPI 入口
├── config.py                   # 配置
├── models.py                   # 数据模型
├── services/
│   ├── __init__.py
│   ├── harness_client.py       # Harness API 客户端
│   ├── llm_client.py          # LLM 客户端
│   └── telemetry.py           # 可观测性
├── agents/
│   ├── __init__.py
│   ├── base.py                # 基础 Agent 类
│   ├── approval_gateway.py    # 人工确认网关
│   ├── orchestrator.py        # Agent编排器
│   ├── agentic_testing.py     # 智能测试Agent
│   ├── code_reviewer.py       # 代码审查
│   ├── deploy_advisor.py      # 部署建议
│   ├── incident_handler.py    # 故障处理
│   └── cost_optimizer.py      # 成本优化
└── prompts/
    ├── code_review.txt
    ├── deploy_analysis.txt
    └── incident_response.txt
```

---

## 3. 核心服务实现

### 3.1 Harness 客户端

```python
# services/harness_client.py
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class HarnessClient:
    """Harness API 客户端."""
    
    def __init__(
        self,
        api_key: str,
        account_id: str,
        base_url: str = "https://app.harness.io/gateway",
    ):
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
    
    async def close(self) -> None:
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def get_pipeline_execution(
        self,
        pipeline_id: str,
        org_id: str,
        project_id: str,
    ) -> dict[str, Any]:
        """获取 Pipeline 执行详情."""
        url = f"{self.base_url}/pipeline/api/pipelines/execution/{pipeline_id}"
        params = {
            "accountIdentifier": self.account_id,
            "orgIdentifier": org_id,
            "projectIdentifier": project_id,
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_service_metrics(
        self,
        service: str,
        environment: str,
        duration_minutes: int = 60,
    ) -> dict[str, Any]:
        """获取服务指标 (通过 SRM)."""
        url = f"{self.base_url}/cv/api/metrics"
        params = {
            "accountId": self.account_id,
            "service": service,
            "environment": environment,
            "duration": duration_minutes,
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def trigger_pipeline(
        self,
        pipeline_id: str,
        org_id: str,
        project_id: str,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """触发 Pipeline."""
        url = f"{self.base_url}/pipeline/api/pipeline/execute/{pipeline_id}"
        params = {
            "accountIdentifier": self.account_id,
            "orgIdentifier": org_id,
            "projectIdentifier": project_id,
        }
        payload = {
            "inputs": inputs or {},
        }
        response = await self.client.post(url, params=params, json=payload)
        response.raise_for_status()
        return response.json()
    
    async def get_current_alerts(
        self,
        environment: str,
    ) -> list[dict[str, Any]]:
        """获取当前告警."""
        url = f"{self.base_url}/cv/api/alerts"
        params = {
            "accountId": self.account_id,
            "environment": environment,
            "status": "open",
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("alerts", [])
    
    async def log_audit_event(
        self,
        agent: str,
        action: str,
        details: dict[str, Any],
    ) -> None:
        """记录审计事件."""
        url = f"{self.base_url}/audit/api/audits"
        payload = {
            "accountIdentifier": self.account_id,
            "agent": agent,
            "action": action,
            "timestamp": "now",
            "details": details,
        }
        try:
            await self.client.post(url, json=payload)
        except Exception:
            # 审计日志失败不应影响主流程
            pass
```

### 3.2 LLM 客户端

```python
# services/llm_client.py
from typing import Any, AsyncIterator

import openai
from anthropic import AsyncAnthropic


class LLMClient:
    """LLM 客户端 (支持多提供商)."""
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.provider = provider
        self.model = model or self._default_model(provider)
        
        if provider == "openai":
            self.client = openai.AsyncOpenAI(api_key=api_key)
        elif provider == "anthropic":
            self.client = AsyncAnthropic(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _default_model(self, provider: str) -> str:
        defaults = {
            "openai": "gpt-4-turbo-preview",
            "anthropic": "claude-3-opus-20240229",
        }
        return defaults.get(provider, "gpt-4")
    
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """完成文本生成."""
        if self.provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        
        elif self.provider == "anthropic":
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        
        return ""
    
    async def stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """流式生成."""
        if self.provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
```

---

## 4. Agent实现

### 4.1 基础 Agent 类

```python
# agents/base.py
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from services.harness_client import HarnessClient
from services.llm_client import LLMClient

T = TypeVar("T", bound=BaseModel)


class AgentResult(BaseModel):
    """Agent 执行结果."""
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    confidence: float = 0.0  # 0-1
    recommended_action: str | None = None


class BaseAgent(ABC, Generic[T]):
    """基础 Agent 类."""
    
    def __init__(
        self,
        harness_client: HarnessClient,
        llm_client: LLMClient | None = None,
    ):
        self.harness = harness_client
        self.llm = llm_client
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def execute(self, context: T) -> AgentResult:
        """执行 Agent 任务."""
        pass
    
    async def log_action(
        self,
        action: str,
        details: dict[str, Any],
    ) -> None:
        """记录操作日志到 Harness."""
        await self.harness.log_audit_event(
            agent=self.name,
            action=action,
            details=details,
        )
```

### 4.2 代码审查 Agent

```python
# agents/code_reviewer.py
import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator

from models import CodeReviewContext, ReviewComment
from services.llm_client import LLMClient

from .base import AgentResult, BaseAgent


@dataclass
class CodeReviewContext:
    """代码审查上下文."""
    file_path: Path
    content: str
    language: str  # python, typescript, etc.
    pr_description: str | None = None


class CodeReviewAgent(BaseAgent[CodeReviewContext]):
    """代码审查 Agent."""
    
    async def execute(self, context: CodeReviewContext) -> AgentResult:
        """执行代码审查."""
        await self.log_action(
            "code_review_started",
            {"file": str(context.file_path), "language": context.language},
        )
        
        comments: list[ReviewComment] = []
        
        # 1. 静态规则检查
        if context.language == "python":
            comments.extend(self._check_python(context))
        elif context.language in ("typescript", "javascript"):
            comments.extend(self._check_typescript(context))
        
        # 2. LLM 深度分析
        if self.llm:
            llm_comments = await self._llm_review(context)
            comments.extend(llm_comments)
        
        # 3. 计算置信度
        confidence = self._calculate_confidence(comments)
        
        await self.log_action(
            "code_review_completed",
            {
                "file": str(context.file_path),
                "issues_found": len(comments),
                "confidence": confidence,
            },
        )
        
        return AgentResult(
            success=True,
            data={
                "comments": [c.model_dump() for c in comments],
                "summary": self._generate_summary(comments),
            },
            confidence=confidence,
            recommended_action=self._recommend_action(comments),
        )
    
    def _check_python(self, context: CodeReviewContext) -> list[ReviewComment]:
        """Python 静态检查."""
        comments = []
        content = context.content
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return [ReviewComment(
                line=e.lineno or 1,
                severity="error",
                message=f"语法错误: {e.msg}",
                rule_id="SYNTAX_ERROR",
            )]
        
        # 检查类型注解
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查参数注解
                for arg in node.args.args:
                    if arg.annotation is None and arg.arg not in ("self", "cls"):
                        comments.append(ReviewComment(
                            line=node.lineno,
                            severity="warning",
                            message=f"参数 '{arg.arg}' 缺少类型注解",
                            suggestion=f"添加类型注解: {arg.arg}: Type",
                            rule_id="MISSING_TYPE_ANNOTATION",
                        ))
                
                # 检查返回值注解
                if node.returns is None:
                    comments.append(ReviewComment(
                        line=node.lineno,
                        severity="warning",
                        message=f"函数 '{node.name}' 缺少返回值注解",
                        suggestion="添加 -> ReturnType 注解",
                        rule_id="MISSING_RETURN_TYPE",
                    ))
                
                # 检查文档字符串
                if not ast.get_docstring(node):
                    comments.append(ReviewComment(
                        line=node.lineno,
                        severity="info",
                        message=f"函数 '{node.name}' 缺少文档字符串",
                        suggestion="添加文档字符串描述函数功能",
                        rule_id="MISSING_DOCSTRING",
                    ))
        
        # 检查 SQL 注入风险
        sql_patterns = [
            r'execute\s*\(\s*["\'].*%s',
            r'execute\s*\(\s*f["\']',
            r'\.format\s*\(.*\)',
        ]
        for pattern in sql_patterns:
            for match in re.finditer(pattern, content):
                line = content[:match.start()].count("\n") + 1
                comments.append(ReviewComment(
                    line=line,
                    severity="error",
                    message="检测到潜在的 SQL 注入风险",
                    suggestion="使用参数化查询",
                    rule_id="SQL_INJECTION_RISK",
                ))
        
        return comments
    
    def _check_typescript(self, context: CodeReviewContext) -> list[ReviewComment]:
        """TypeScript 静态检查."""
        comments = []
        content = context.content
        
        # 检查 any 类型使用
        any_pattern = r':\s*any\b'
        for match in re.finditer(any_pattern, content):
            line = content[:match.start()].count("\n") + 1
            comments.append(ReviewComment(
                line=line,
                severity="warning",
                message="使用了 'any' 类型",
                suggestion="使用具体类型或 'unknown'",
                rule_id="AVOID_ANY_TYPE",
            ))
        
        # 检查 console.log
        console_pattern = r'console\.(log|warn|error)\s*\('
        for match in re.finditer(console_pattern, content):
            line = content[:match.start()].count("\n") + 1
            comments.append(ReviewComment(
                line=line,
                severity="warning",
                message="代码中包含 console 语句",
                suggestion="生产代码中应移除 console 语句",
                rule_id="NO_CONSOLE",
            ))
        
        return comments
    
    async def _llm_review(
        self,
        context: CodeReviewContext,
    ) -> list[ReviewComment]:
        """LLM 深度审查."""
        if not self.llm:
            return []
        
        prompt = f"""请审查以下代码，找出潜在问题:

文件: {context.file_path}
语言: {context.language}

```
{context.content}
```

请按以下格式输出问题:
- 行号: [行号]
- 严重程度: [error/warning/info]
- 问题: [描述]
- 建议: [修复建议]
"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="你是一位资深代码审查专家，擅长发现代码中的潜在问题和改进点。",
            temperature=0.3,
        )
        
        # 解析 LLM 输出
        comments = []
        # 这里简化处理，实际应使用更健壮的解析
        
        return comments
    
    def _calculate_confidence(self, comments: list[ReviewComment]) -> float:
        """计算审查置信度."""
        if not comments:
            return 0.95  # 无问题，高置信度
        
        error_count = sum(1 for c in comments if c.severity == "error")
        warning_count = sum(1 for c in comments if c.severity == "warning")
        
        # 错误越多，置信度越低
        base_confidence = 0.9
        penalty = error_count * 0.1 + warning_count * 0.05
        return max(0.5, base_confidence - penalty)
    
    def _generate_summary(self, comments: list[ReviewComment]) -> str:
        """生成审查摘要."""
        errors = sum(1 for c in comments if c.severity == "error")
        warnings = sum(1 for c in comments if c.severity == "warning")
        infos = sum(1 for c in comments if c.severity == "info")
        
        return f"发现 {errors} 个错误, {warnings} 个警告, {infos} 个建议"
    
    def _recommend_action(self, comments: list[ReviewComment]) -> str | None:
        """推荐操作."""
        errors = sum(1 for c in comments if c.severity == "error")
        if errors > 0:
            return "修复错误后重新提交"
        warnings = sum(1 for c in comments if c.severity == "warning")
        if warnings > 5:
            return "建议修复警告"
        return None
```

### 4.3 部署建议 Agent

```python
# agents/deploy_advisor.py
from dataclasses import dataclass
from datetime import datetime, timedelta

from models import DeployContext

from .base import AgentResult, BaseAgent


@dataclass
class DeployContext:
    """部署上下文."""
    service: str
    environment: str
    version: str
    previous_deployment: datetime | None = None
    force_deploy: bool = False


class DeployAdvisorAgent(BaseAgent[DeployContext]):
    """部署建议 Agent."""
    
    async def execute(self, context: DeployContext) -> AgentResult:
        """分析部署风险并给出建议."""
        await self.log_action(
            "deploy_analysis_started",
            {"service": context.service, "environment": context.environment},
        )
        
        # 1. 获取当前指标
        metrics = await self.harness.get_service_metrics(
            context.service,
            context.environment,
            duration_minutes=60,
        )
        
        # 2. 获取最近告警
        alerts = await self.harness.get_current_alerts(context.environment)
        
        # 3. 风险分析
        risk_factors = self._analyze_risk(metrics, alerts)
        
        # 4. 生成金丝雀配置
        canary_config = self._generate_canary_config(risk_factors)
        
        overall_risk = self._calculate_overall_risk(risk_factors)
        
        await self.log_action(
            "deploy_analysis_completed",
            {
                "service": context.service,
                "risk_level": overall_risk,
                "factors_count": len(risk_factors),
            },
        )
        
        return AgentResult(
            success=True,
            data={
                "risk_level": overall_risk,
                "risk_factors": risk_factors,
                "canary_config": canary_config,
                "metrics_summary": self._summarize_metrics(metrics),
            },
            confidence=0.85 if risk_factors else 0.95,
            recommended_action=self._recommend_deploy_action(
                overall_risk, context.force_deploy
            ),
        )
    
    def _analyze_risk(
        self,
        metrics: dict,
        alerts: list[dict],
    ) -> list[dict]:
        """分析风险因素."""
        factors = []
        
        # 检查错误率
        error_rate = metrics.get("error_rate", 0)
        if error_rate > 0.05:  # 5%
            factors.append({
                "type": "error_rate",
                "level": "high",
                "value": error_rate,
                "threshold": 0.05,
                "message": f"当前错误率 {error_rate:.2%} 过高",
            })
        elif error_rate > 0.01:  # 1%
            factors.append({
                "type": "error_rate",
                "level": "medium",
                "value": error_rate,
                "threshold": 0.01,
                "message": f"当前错误率 {error_rate:.2%} 偏高",
            })
        
        # 检查延迟
        p99_latency = metrics.get("p99_latency", 0)
        if p99_latency > 1000:  # 1s
            factors.append({
                "type": "latency",
                "level": "high",
                "value": p99_latency,
                "threshold": 1000,
                "message": f"P99 延迟 {p99_latency}ms 过高",
            })
        elif p99_latency > 500:  # 500ms
            factors.append({
                "type": "latency",
                "level": "medium",
                "value": p99_latency,
                "threshold": 500,
                "message": f"P99 延迟 {p99_latency}ms 偏高",
            })
        
        # 检查活跃告警
        if alerts:
            factors.append({
                "type": "active_alerts",
                "level": "high" if len(alerts) > 3 else "medium",
                "value": len(alerts),
                "message": f"当前有 {len(alerts)} 个活跃告警",
            })
        
        return factors
    
    def _calculate_overall_risk(self, risk_factors: list[dict]) -> str:
        """计算整体风险等级."""
        if not risk_factors:
            return "low"
        
        high_risks = sum(1 for f in risk_factors if f["level"] == "high")
        if high_risks > 0:
            return "high"
        
        medium_risks = sum(1 for f in risk_factors if f["level"] == "medium")
        if medium_risks > 2:
            return "high"
        elif medium_risks > 0:
            return "medium"
        
        return "low"
    
    def _generate_canary_config(self, risk_factors: list[dict]) -> dict:
        """生成金丝雀部署配置."""
        risk_level = self._calculate_overall_risk(risk_factors)
        
        configs = {
            "low": {
                "steps": [10, 25, 50, 100],
                "interval": 5,  # minutes
                "error_threshold": 5,  # percentage
            },
            "medium": {
                "steps": [5, 10, 25, 50, 100],
                "interval": 10,
                "error_threshold": 2,
            },
            "high": {
                "steps": [1, 5, 10, 25, 50, 100],
                "interval": 15,
                "error_threshold": 1,
            },
        }
        
        return configs.get(risk_level, configs["low"])
    
    def _summarize_metrics(self, metrics: dict) -> dict[str, str]:
        """生成指标摘要."""
        return {
            "error_rate": f"{metrics.get('error_rate', 0):.2%}",
            "p99_latency": f"{metrics.get('p99_latency', 0)}ms",
            "throughput": f"{metrics.get('throughput', 0)}/s",
        }
    
    def _recommend_deploy_action(
        self,
        risk_level: str,
        force_deploy: bool,
    ) -> str | None:
        """推荐部署操作."""
        if risk_level == "high" and not force_deploy:
            return "建议暂缓部署，先解决当前问题"
        elif risk_level == "medium":
            return "可以使用保守的金丝雀部署策略"
        return None
```

### 4.4 故障处理 Agent

```python
# agents/incident_handler.py
from dataclasses import dataclass
from typing import Any

from models import IncidentContext

from .base import AgentResult, BaseAgent


@dataclass
class IncidentContext:
    """故障处理上下文."""
    service: str
    alert_name: str
    severity: str
    description: str
    metrics: dict[str, Any] | None = None
    logs: list[str] | None = None


class IncidentHandlerAgent(BaseAgent[IncidentContext]):
    """故障处理 Agent."""
    
    async def execute(self, context: IncidentContext) -> AgentResult:
        """处理故障告警."""
        await self.log_action(
            "incident_handling_started",
            {
                "service": context.service,
                "alert": context.alert_name,
                "severity": context.severity,
            },
        )
        
        # 1. 根因分析
        root_cause = await self._analyze_root_cause(context)
        
        # 2. 生成修复方案
        remediation = await self._generate_remediation(context, root_cause)
        
        # 3. 判断是否建议回滚
        should_rollback = self._should_rollback(context, root_cause)
        
        # 4. 尝试自动修复（低风险操作）
        auto_fix_result = None
        if remediation.get("auto_fixable") and context.severity == "critical":
            auto_fix_result = await self._attempt_auto_fix(remediation)
        
        confidence = self._calculate_confidence(root_cause, remediation)
        
        await self.log_action(
            "incident_handling_completed",
            {
                "service": context.service,
                "root_cause": root_cause.get("type"),
                "should_rollback": should_rollback,
                "auto_fix_attempted": auto_fix_result is not None,
            },
        )
        
        return AgentResult(
            success=True,
            data={
                "root_cause": root_cause,
                "remediation": remediation,
                "should_rollback": should_rollback,
                "auto_fix_result": auto_fix_result,
            },
            confidence=confidence,
            recommended_action=self._recommend_incident_action(
                should_rollback, remediation
            ),
        )
    
    async def _analyze_root_cause(
        self,
        context: IncidentContext,
    ) -> dict[str, Any]:
        """分析故障根因."""
        root_cause = {
            "type": "unknown",
            "confidence": 0.0,
            "evidence": [],
        }
        
        # 基于告警名称和描述进行模式匹配
        alert_patterns = {
            "HighErrorRate": "error_spike",
            "HighLatency": "performance_degradation",
            "ServiceDown": "service_failure",
            "DiskFull": "resource_exhaustion",
            "MemoryHigh": "resource_exhaustion",
        }
        
        for pattern, cause_type in alert_patterns.items():
            if pattern in context.alert_name:
                root_cause["type"] = cause_type
                root_cause["confidence"] = 0.8
                root_cause["evidence"].append(f"告警名称匹配: {pattern}")
                break
        
        # 如果有日志，进行日志分析
        if context.logs and self.llm:
            log_analysis = await self._analyze_logs(context.logs)
            root_cause["log_analysis"] = log_analysis
        
        return root_cause
    
    async def _analyze_logs(self, logs: list[str]) -> dict[str, Any]:
        """分析日志."""
        if not self.llm:
            return {"error": "LLM not available"}
        
        # 简化处理，实际应使用更复杂的日志分析
        error_patterns = [
            "Exception",
            "Error",
            "Failed",
            "Timeout",
            "Connection refused",
        ]
        
        errors = []
        for log in logs:
            for pattern in error_patterns:
                if pattern in log:
                    errors.append(log)
                    break
        
        return {
            "error_count": len(errors),
            "sample_errors": errors[:5],
        }
    
    async def _generate_remediation(
        self,
        context: IncidentContext,
        root_cause: dict[str, Any],
    ) -> dict[str, Any]:
        """生成修复方案."""
        cause_type = root_cause.get("type", "unknown")
        
        remediation_strategies = {
            "error_spike": {
                "actions": [
                    "检查最近的代码变更",
                    "查看错误日志详情",
                    "考虑回滚到上一个稳定版本",
                ],
                "auto_fixable": False,
            },
            "performance_degradation": {
                "actions": [
                    "检查资源使用情况",
                    "分析慢查询",
                    "考虑扩容",
                ],
                "auto_fixable": False,
            },
            "service_failure": {
                "actions": [
                    "检查服务健康状态",
                    "重启服务",
                    "检查依赖服务状态",
                ],
                "auto_fixable": True,
                "auto_fix_action": "restart_service",
            },
            "resource_exhaustion": {
                "actions": [
                    "清理临时文件",
                    "扩容资源",
                    "优化资源使用",
                ],
                "auto_fixable": False,
            },
        }
        
        return remediation_strategies.get(cause_type, {
            "actions": ["需要人工介入调查"],
            "auto_fixable": False,
        })
    
    def _should_rollback(
        self,
        context: IncidentContext,
        root_cause: dict[str, Any],
    ) -> bool:
        """判断是否建议回滚."""
        # 严重级别故障建议回滚
        if context.severity == "critical":
            return True
        
        # 错误激增建议回滚
        if root_cause.get("type") == "error_spike":
            return True
        
        return False
    
    async def _attempt_auto_fix(self, remediation: dict[str, Any]) -> dict[str, Any]:
        """尝试自动修复."""
        action = remediation.get("auto_fix_action")
        
        if action == "restart_service":
            # 实现服务重启逻辑
            return {
                "action": action,
                "status": "attempted",
                "result": "Service restart initiated",
            }
        
        return {
            "action": action,
            "status": "not_supported",
            "result": "Auto-fix not supported for this action",
        }
    
    def _calculate_confidence(
        self,
        root_cause: dict[str, Any],
        remediation: dict[str, Any],
    ) -> float:
        """计算置信度."""
        base_confidence = root_cause.get("confidence", 0.5)
        
        # 如果有明确的修复方案，提高置信度
        if remediation.get("actions"):
            base_confidence += 0.1
        
        return min(0.95, base_confidence)
    
    def _recommend_incident_action(
        self,
        should_rollback: bool,
        remediation: dict[str, Any],
    ) -> str:
        """推荐故障处理操作."""
        if should_rollback:
            return "建议立即回滚到上一个稳定版本"
        
        actions = remediation.get("actions", [])
        if actions:
            return f"建议操作: {actions[0]}"
        
        return "需要人工介入调查"
```

---

## 5. 核心组件实现

### 5.1 人工确认网关

**对应SKILL.md**: 第3.1节 - 人机协作规范

```python
# agents/approval_gateway.py
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
import asyncio


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalConfig(BaseModel):
    """审批配置"""
    min_confidence: float = 0.85
    approvers: List[str]
    require_all_approvers: bool = False
    timeout: timedelta = timedelta(hours=24)
    channels: List[str] = ["web", "slack"]
    auto_escalate: bool = True
    escalation_delay: timedelta = timedelta(hours=2)


class ApprovalRequest(BaseModel):
    """审批请求"""
    id: str
    action: str
    context: dict
    confidence: float
    requester: str
    status: ApprovalStatus
    created_at: datetime
    expires_at: datetime
    approvers: List[str]
    responses: dict = {}


class ApprovalGateway:
    """人工确认网关 - 确保关键AI决策需人工审批"""
    
    def __init__(self):
        self._requests: dict[str, ApprovalRequest] = {}
        self._notification_handlers = {}
    
    def requires_approval(self, confidence: float, action: str) -> bool:
        """判断是否需要审批"""
        high_risk_actions = [
            "deploy_to_production",
            "auto_rollback",
            "database_migration",
            "security_policy_change",
        ]
        
        if action in high_risk_actions:
            return True
        
        if confidence < 0.85:
            return True
        
        return False
    
    async def request_approval(
        self,
        action: str,
        context: dict,
        confidence: float,
        requester: str,
        config: ApprovalConfig,
    ) -> ApprovalRequest:
        """发起审批请求"""
        import uuid
        
        request_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        request = ApprovalRequest(
            id=request_id,
            action=action,
            context=context,
            confidence=confidence,
            requester=requester,
            status=ApprovalStatus.PENDING,
            created_at=now,
            expires_at=now + config.timeout,
            approvers=config.approvers,
        )
        
        self._requests[request_id] = request
        await self._send_notifications(request, config)
        
        if config.auto_escalate:
            asyncio.create_task(self._handle_escalation(request_id, config))
        
        return request
    
    async def _send_notifications(self, request: ApprovalRequest, config: ApprovalConfig):
        """发送审批通知"""
        message = self._format_notification(request)
        
        for channel in config.channels:
            handler = self._notification_handlers.get(channel)
            if handler:
                for approver in config.approvers:
                    await handler(approver, message)
    
    def _format_notification(self, request: ApprovalRequest) -> str:
        """格式化通知消息"""
        return f"""
🔔 **AI决策需要您的审批**

**操作**: {request.action}
**请求人**: {request.requester}
**置信度**: {request.confidence:.2f}
**上下文**: {request.context}

请访问审批中心进行审批。
        """
    
    async def _handle_escalation(self, request_id: str, config: ApprovalConfig):
        """处理审批超时升级"""
        await asyncio.sleep(config.escalation_delay.total_seconds())
        
        request = self._requests.get(request_id)
        if request and request.status == ApprovalStatus.PENDING:
            await self._escalate_request(request)
    
    async def _escalate_request(self, request: ApprovalRequest):
        """升级审批请求"""
        pass
    
    async def wait_for_approval(
        self,
        request_id: str,
        timeout: Optional[timedelta] = None,
    ) -> ApprovalRequest:
        """等待审批结果"""
        request = self._requests.get(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        poll_interval = 5
        max_wait = timeout or timedelta(minutes=30)
        start_time = datetime.utcnow()
        
        while request.status == ApprovalStatus.PENDING:
            await asyncio.sleep(poll_interval)
            
            if datetime.utcnow() - start_time > max_wait:
                request.status = ApprovalStatus.EXPIRED
                break
            
            if datetime.utcnow() > request.expires_at:
                request.status = ApprovalStatus.EXPIRED
                break
        
        return request
    
    async def approve(self, request_id: str, approver: str) -> ApprovalRequest:
        """审批通过"""
        request = self._requests.get(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        request.responses[approver] = "approved"
        
        if self._check_approval_complete(request):
            request.status = ApprovalStatus.APPROVED
        
        return request
    
    async def reject(self, request_id: str, approver: str, reason: str) -> ApprovalRequest:
        """审批拒绝"""
        request = self._requests.get(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        request.responses[approver] = f"rejected: {reason}"
        request.status = ApprovalStatus.REJECTED
        
        return request
    
    def _check_approval_complete(self, request: ApprovalRequest) -> bool:
        """检查审批是否完成"""
        return True
```

### 5.2 Agent编排器

**对应SKILL.md**: 第3.2节 - Agent编排能力

```python
# agents/orchestrator.py
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
import asyncio
import uuid


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(str, Enum):
    COORDINATION = "coordination"
    RESULT = "result"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class AgentMessage(BaseModel):
    """Agent间消息"""
    type: MessageType
    sender: str
    recipient: str
    payload: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()


class TaskDefinition(BaseModel):
    """任务定义"""
    id: str = None
    name: str
    agent_type: str
    input_data: Dict[str, Any]
    dependencies: List[str] = []
    requires_approval: bool = False
    confidence_threshold: float = 0.85
    timeout: int = 300
    retry_count: int = 3
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid.uuid4())


class TaskResult(BaseModel):
    """任务结果"""
    task_id: str
    status: TaskStatus
    output: Dict[str, Any] = {}
    error: Optional[str] = None
    confidence: float = 0.0
    execution_time: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowDefinition(BaseModel):
    """工作流定义"""
    id: str = None
    name: str
    tasks: List[TaskDefinition]
    context: Dict[str, Any] = {}
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid.uuid4())


class WorkflowResult(BaseModel):
    """工作流结果"""
    workflow_id: str
    status: TaskStatus
    task_results: Dict[str, TaskResult]
    started_at: datetime
    completed_at: Optional[datetime] = None


class MessageBus:
    """消息总线 - Agent间通信"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[AgentMessage] = []
    
    async def publish(self, message: AgentMessage):
        """发布消息"""
        self._history.append(message)
        
        handlers = self._subscribers.get(message.recipient, [])
        for handler in handlers:
            asyncio.create_task(handler(message))
    
    async def subscribe(self, agent_id: str, handler: Callable):
        """订阅消息"""
        if agent_id not in self._subscribers:
            self._subscribers[agent_id] = []
        self._subscribers[agent_id].append(handler)
    
    def get_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
    ) -> List[AgentMessage]:
        """获取消息历史"""
        messages = self._history
        
        if agent_id:
            messages = [
                m for m in messages
                if m.sender == agent_id or m.recipient == agent_id
            ]
        
        if message_type:
            messages = [m for m in messages if m.type == message_type]
        
        return messages


class AgentOrchestrator:
    """Agent编排器 - 协调多Agent协作执行复杂工作流"""
    
    def __init__(self):
        self._agents: Dict[str, Any] = {}
        self._workflows: Dict[str, WorkflowResult] = {}
        self.message_bus = MessageBus()
    
    def register_agent(self, agent_id: str, agent_instance: Any):
        """注册Agent"""
        self._agents[agent_id] = agent_instance
    
    async def execute_workflow(
        self,
        workflow: WorkflowDefinition,
        context: Dict[str, Any] = None,
    ) -> WorkflowResult:
        """执行工作流"""
        result = WorkflowResult(
            workflow_id=workflow.id,
            status=TaskStatus.RUNNING,
            task_results={},
            started_at=datetime.utcnow(),
        )
        
        self._workflows[workflow.id] = result
        
        task_graph = self._build_task_graph(workflow.tasks)
        
        try:
            await self._execute_tasks_with_deps(
                workflow.tasks,
                task_graph,
                result,
                context or {},
            )
            result.status = TaskStatus.COMPLETED
        except Exception as e:
            result.status = TaskStatus.FAILED
        
        result.completed_at = datetime.utcnow()
        return result
    
    def _build_task_graph(self, tasks: List[TaskDefinition]) -> Dict[str, List[str]]:
        """构建任务依赖图"""
        graph = {task.id: [] for task in tasks}
        
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in graph:
                    graph[task.id].append(dep_id)
        
        return graph
    
    async def _execute_tasks_with_deps(
        self,
        tasks: List[TaskDefinition],
        task_graph: Dict[str, List[str]],
        workflow_result: WorkflowResult,
        context: Dict[str, Any],
    ):
        """执行有依赖的任务"""
        completed_tasks = set()
        running_tasks = {}
        
        while len(completed_tasks) < len(tasks):
            ready_tasks = [
                task for task in tasks
                if task.id not in completed_tasks
                and task.id not in running_tasks
                and all(dep in completed_tasks for dep in task_graph[task.id])
            ]
            
            for task in ready_tasks:
                task_future = asyncio.create_task(
                    self._execute_single_task(task, context)
                )
                running_tasks[task.id] = task_future
            
            if running_tasks:
                done, pending = await asyncio.wait(
                    running_tasks.values(),
                    return_when=asyncio.FIRST_COMPLETED,
                )
                
                for future in done:
                    task_result = await future
                    workflow_result.task_results[task_result.task_id] = task_result
                    completed_tasks.add(task_result.task_id)
                    
                    for tid, tf in list(running_tasks.items()):
                        if tf == future:
                            del running_tasks[tid]
                            break
    
    async def _execute_single_task(
        self,
        task: TaskDefinition,
        context: Dict[str, Any],
    ) -> TaskResult:
        """执行单个任务"""
        agent = self._agents.get(task.agent_type)
        if not agent:
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"Agent {task.agent_type} not found",
            )
        
        start_time = datetime.utcnow()
        
        try:
            result = await agent.execute(task.input_data, context)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                output=result,
                confidence=result.get("confidence", 0.0),
                execution_time=execution_time,
                started_at=start_time,
                completed_at=datetime.utcnow(),
            )
        except Exception as e:
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                started_at=start_time,
            )
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResult]:
        """获取工作流状态"""
        return self._workflows.get(workflow_id)
```

### 5.3 智能测试Agent

**对应SKILL.md**: 第3.4节 - 智能测试能力

```python
# agents/agentic_testing.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class TestCase(BaseModel):
    """测试用例"""
    id: str
    name: str
    description: str
    test_code: str
    target_function: str
    confidence: float
    test_type: str
    tags: List[str] = []


class TestSuite(BaseModel):
    """测试套件"""
    test_cases: List[TestCase]
    coverage_estimate: float
    total_confidence: float


class HealingReport(BaseModel):
    """测试自我修复报告"""
    healed_tests: List[str]
    failed_tests: List[str]
    new_tests_generated: int


class AgenticTestingAgent:
    """智能测试Agent - AI驱动的测试生成、执行与维护"""
    
    async def generate_tests(
        self,
        code_context: Dict[str, Any],
    ) -> TestSuite:
        """智能生成测试"""
        source_code = code_context.get("source_code", "")
        function_name = code_context.get("function_name", "")
        
        test_cases = await self._llm_generate_tests(
            source_code=source_code,
            function_name=function_name,
        )
        
        total_confidence = sum(tc.confidence for tc in test_cases) / len(test_cases) if test_cases else 0
        
        return TestSuite(
            test_cases=test_cases,
            coverage_estimate=self._estimate_coverage(test_cases),
            total_confidence=total_confidence,
        )
    
    async def _llm_generate_tests(
        self,
        source_code: str,
        function_name: str,
    ) -> List[TestCase]:
        """使用LLM生成测试"""
        pass
    
    def _estimate_coverage(self, test_cases: List[TestCase]) -> float:
        """估算测试覆盖率"""
        return 0.0
    
    async def self_heal_tests(
        self,
        code_changes: List[Dict[str, Any]],
    ) -> HealingReport:
        """测试自我修复"""
        healed = []
        failed = []
        new_generated = 0
        
        for change in code_changes:
            file_path = change.get("file", "")
            change_type = change.get("change_type", "")
            
            affected_tests = await self._find_affected_tests(file_path)
            
            for test in affected_tests:
                try:
                    if await self._heal_test(test, change):
                        healed.append(test.id)
                    else:
                        failed.append(test.id)
                except Exception:
                    failed.append(test.id)
        
        return HealingReport(
            healed_tests=healed,
            failed_tests=failed,
            new_tests_generated=new_generated,
        )
    
    async def _find_affected_tests(self, file_path: str) -> List[TestCase]:
        """查找受影响的测试"""
        return []
    
    async def _heal_test(self, test: TestCase, change: Dict[str, Any]) -> bool:
        """修复单个测试"""
        return False
```

### 5.4 自动化测试友好支持实现

**对应SKILL.md**: 第5.4节 - 自动化测试友好支持

#### 5.4.1 交互元素定位优化实现

**实现指南**：

1. **添加test-data-id属性**：
   - 在所有用户交互元素（按钮、输入框、下拉菜单等）上添加唯一的`test-data-id`属性
   - 遵循"功能-组件-用途"的命名规范

**示例代码**：

```tsx
// 好的实现
<button 
  test-data-id="login-button-submit"
  onClick={handleSubmit}
>
  登录
</button>

// 好的实现
<input 
  test-data-id="user-input-email"
  type="email"
  value={email}
  onChange={handleEmailChange}
/>

// 好的实现
<select test-data-id="user-select-role">
  <option value="admin">管理员</option>
  <option value="user">普通用户</option>
</select>
```

**命名规范**：
- 格式：`{功能}-{组件类型}-{用途}`
- 示例：
  - `login-button-submit` - 登录功能的提交按钮
  - `user-input-email` - 用户功能的邮箱输入框
  - `dashboard-dropdown-filter` - 仪表盘功能的过滤下拉菜单

#### 5.4.2 数组类组件标记系统实现

**实现指南**：

1. **添加aria-labels索引标记**：
   - 对数组渲染的组件添加`aria-label`属性
   - 格式为"组件名称-索引值"
   - 索引从0开始连续编号

**示例代码**：

```tsx
// 好的实现
const users = [
  { id: 1, name: "张三" },
  { id: 2, name: "李四" },
  { id: 3, name: "王五" }
];

// 数组渲染的组件
users.map((user, index) => (
  <div 
    key={user.id}
    aria-label={`user-item-${index}`}
    test-data-id={`user-item-${user.id}`}
  >
    <span>{user.name}</span>
  </div>
));

// 列表项的交互元素
users.map((user, index) => (
  <div key={user.id} aria-label={`user-item-${index}`}>
    <button 
      test-data-id={`user-button-edit-${user.id}`}
      onClick={() => editUser(user.id)}
    >
      编辑
    </button>
    <button 
      test-data-id={`user-button-delete-${user.id}`}
      onClick={() => deleteUser(user.id)}
    >
      删除
    </button>
  </div>
));
```

**索引规则**：
- 索引从0开始连续编号
- 与数组数据结构保持一致对应关系
- 确保`aria-label`值唯一且清晰

#### 5.4.3 代码结构要求实现

**实现指南**：

1. **清晰的层次结构**：
   - 使用模块化组件设计
   - 保持组件嵌套关系明确

2. **容器边界**：
   - 为关键交互区域设置明确的容器边界
   - 使用语义化的HTML标签

**示例代码**：

```tsx
// 好的实现 - 清晰的层次结构
<div test-data-id="login-container">
  <h2>登录</h2>
  <form test-data-id="login-form">
    <div test-data-id="login-input-group-email">
      <label htmlFor="email">邮箱</label>
      <input 
        id="email"
        test-data-id="login-input-email"
        type="email"
        value={email}
        onChange={handleEmailChange}
      />
    </div>
    <div test-data-id="login-input-group-password">
      <label htmlFor="password">密码</label>
      <input 
        id="password"
        test-data-id="login-input-password"
        type="password"
        value={password}
        onChange={handlePasswordChange}
      />
    </div>
    <button 
      test-data-id="login-button-submit"
      type="submit"
      onClick={handleSubmit}
    >
      登录
    </button>
  </form>
</div>
```

**模块化设计**：
- 将复杂页面拆分为多个可测试的组件
- 每个组件都有明确的职责和边界
- 使用props传递数据和回调函数

#### 5.4.4 自动化测试友好性验证实现

**实现指南**：

1. **测试属性检查**：
   - 集成自动化测试友好性检查机制
   - 验证所有关键交互控件均具备可被测试框架识别的定位属性

2. **测试属性文档**：
   - 生成测试属性文档，说明各交互元素的`test-data-id`属性值及其对应功能

**示例代码**：

```typescript
// 测试属性检查工具函数
function validateTestAttributes(element: React.ReactElement): boolean {
  const attributes = element.props;
  
  // 检查交互元素是否有test-data-id
  if (isInteractiveElement(element)) {
    return !!attributes['test-data-id'];
  }
  
  // 检查数组渲染的组件是否有aria-label
  if (isArrayRenderedElement(element)) {
    return !!attributes['aria-label'];
  }
  
  return true;
}

// 生成测试属性文档
function generateTestAttributesDocumentation(components: React.ReactElement[]): string {
  const documentation = components.map(component => {
    const testId = component.props['test-data-id'];
    const ariaLabel = component.props['aria-label'];
    
    return {
      element: component.type,
      testId,
      ariaLabel,
      purpose: inferElementPurpose(component)
    };
  });
  
  return JSON.stringify(documentation, null, 2);
}
```

**验证流程**：
1. 在代码生成后自动运行测试属性验证
2. 生成测试属性文档
3. 确保所有要求的属性都已正确添加

#### 5.4.5 兼容性要求实现

**实现指南**：

1. **W3C标准兼容**：
   - 确保添加的测试属性符合W3C标准
   - 不影响页面可访问性和正常功能

2. **浏览器兼容性**：
   - 保证测试属性在各主流浏览器环境下的一致性表现

3. **性能影响**：
   - 确保测试属性的添加不会对页面性能产生显著影响

**最佳实践**：
- 使用标准的HTML属性，避免自定义属性冲突
- 保持属性值简洁明了
- 避免在生产环境中暴露敏感信息
- 确保属性名称符合HTML规范

**示例代码**：

```tsx
// 好的实现 - 符合W3C标准
<button 
  test-data-id="submit-button"
  aria-label="提交表单"
  onClick={handleSubmit}
>
  提交
</button>

// 好的实现 - 浏览器兼容
<input 
  test-data-id="search-input"
  type="text"
  placeholder="搜索..."
  value={searchTerm}
  onChange={handleSearchChange}
/>

// 好的实现 - 性能友好
// 避免过度使用测试属性
// 只在关键交互元素上添加
<div>
  <h1>欢迎页面</h1>
  <p>这是一个示例页面</p>
  <button test-data-id="welcome-button-start">开始使用</button>
</div>
```

---

## 6. 使用场景详解

### 6.1 AI代码审查集成

**对应SKILL.md**: CAP-001 代码审查能力

```yaml
# .harness/pipelines/ci.yml
steps:
  - step:
      name: AI Code Review
      identifier: ai_code_review
      type: Run
      spec:
        image: python:3.12-slim
        command: |
          curl -X POST http://ai-agent:8000/review/code \
            -H "Content-Type: application/json" \
            -d '{
              "file_path": "src/main.py",
              "content": "'"$(cat src/main.py | base64)"'",
              "language": "python"
            }'
```

**API请求**:

```http
POST /review/code
Content-Type: application/json

{
  "file_path": "src/main.py",
  "content": "def hello(): pass",
  "language": "python",
  "pr_description": "Add hello function"
}
```

**响应格式**:

```json
{
  "success": true,
  "comments": [
    {
      "line": 1,
      "severity": "warning",
      "message": "函数缺少类型注解",
      "suggestion": "添加 -> None 返回值注解"
    }
  ],
  "confidence": 0.85
}
```

### 6.2 部署风险评估集成

**对应SKILL.md**: CAP-002 部署建议能力

```yaml
# CD Pipeline 中集成
steps:
  - step:
      name: AI Risk Assessment
      identifier: ai_risk_assessment
      type: Run
      spec:
        command: |
          curl -X POST http://ai-agent:8000/deploy/analyze \
            -H "Content-Type: application/json" \
            -d '{
              "service": "myapp",
              "environment": "production",
              "version": "<+pipeline.sequenceId>"
            }'
```

**决策规则**:

| 风险等级 | 错误率阈值 | 延迟阈值 | 建议操作 |
|----------|-----------|----------|----------|
| 低 | < 1% | P99 < 500ms | 正常部署 |
| 中 | 1-5% | P99 500-1000ms | 保守金丝雀 |
| 高 | > 5% | P99 > 1000ms | 阻断部署 |

### 6.3 故障自动处理集成

**对应SKILL.md**: CAP-003 故障处理能力

```python
# 告警 Webhook 处理
@app.post("/webhook/alert")
async def handle_alert(alert: Alert):
    response = requests.post(
        "http://ai-agent:8000/incident/handle",
        json={
            "service": alert.service,
            "alert_name": alert.name,
            "severity": alert.severity,
            "description": alert.description,
        }
    )
    result = response.json()
    
    if result.get("should_rollback"):
        approval = await approval_gateway.request_approval(
            action="auto_rollback",
            context={"service": alert.service, "reason": result.get("root_cause")},
            confidence=result.get("confidence", 0.8),
            requester="incident-handler",
            config=ApprovalConfig(min_confidence=0.9),
        )
        
        if approval.status.value == "approved":
            await trigger_rollback(alert.service)
```

### 6.4 智能测试集成

**对应SKILL.md**: CAP-004 智能测试能力

```yaml
# CI Pipeline 集成智能测试
steps:
  - step:
      name: AI Test Generation
      type: Run
      spec:
        command: |
          python -m agents.agentic_testing generate \
            --source src/ \
            --output tests/generated/ \
            --confidence-threshold 0.85
  
  - step:
      name: AI Test Review
      type: Run
      spec:
        command: |
          python -m agents.approval_gateway check \
            --tests tests/generated/ \
            --auto-approve-confidence 0.9
```

---

## 7. 配置参考

### 7.1 环境变量配置

```bash
# Harness
HARNESS_API_KEY="pat.xxx"
HARNESS_ACCOUNT_ID="your-account-id"
HARNESS_BASE_URL="https://app.harness.io/gateway"

# LLM
LLM_PROVIDER="openai"
LLM_API_KEY="sk-xxx"
LLM_MODEL="gpt-4-turbo-preview"

# OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT="http://otel-collector:4317"
OTEL_SERVICE_NAME="harness-ai-agent"

# Approval Gateway
APPROVAL_DEFAULT_TIMEOUT="24h"
APPROVAL_AUTO_ESCALATE="true"
APPROVAL_ESCALATION_DELAY="2h"
```

### 7.2 项目配置示例

```yaml
# project-config.yaml
name: "my-microservice"
description: "用户服务微服务"
team: "Platform Team"

frontend_stack:
  framework: "React"
  language: "TypeScript"
  version: "19"

backend_stack:
  framework: "FastAPI"
  language: "Python"
  version: "3.12"

enable_code_review: true
enable_agentic_testing: true
enable_deploy_advisor: true
enable_incident_handler: true
enable_cost_optimizer: false

approval_config:
  min_confidence: 0.85
  approvers:
    - "tech-lead@company.com"
    - "sre-oncall@company.com"
  require_all_approvers: false
  channels: ["web", "slack"]
```

### 7.3 数据模型

```python
# models.py
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ReviewComment(BaseModel):
    """代码审查评论."""
    line: int
    severity: str = Field(..., pattern="^(error|warning|info)$")
    message: str
    suggestion: str | None = None
    rule_id: str | None = None


class CodeReviewRequest(BaseModel):
    """代码审查请求."""
    file_path: Path
    content: str
    language: str
    pr_description: str | None = None


class CodeReviewResponse(BaseModel):
    """代码审查响应."""
    success: bool
    comments: list[ReviewComment]
    summary: str
    confidence: float
    recommended_action: str | None = None


class DeployAnalysisRequest(BaseModel):
    """部署分析请求."""
    service: str
    environment: str
    version: str
    force_deploy: bool = False


class DeployAnalysisResponse(BaseModel):
    """部署分析响应."""
    success: bool
    risk_level: str
    risk_factors: list[dict[str, Any]]
    canary_config: dict[str, Any]
    metrics_summary: dict[str, str]
    confidence: float
    recommended_action: str | None = None


class IncidentHandlingRequest(BaseModel):
    """故障处理请求."""
    service: str
    alert_name: str
    severity: str
    description: str
    metrics: dict[str, Any] | None = None
    logs: list[str] | None = None


class IncidentHandlingResponse(BaseModel):
    """故障处理响应."""
    success: bool
    root_cause: dict[str, Any]
    remediation: dict[str, Any]
    should_rollback: bool
    auto_fix_result: dict[str, Any] | None = None
    confidence: float
    recommended_action: str | None = None
```

### 7.4 配置管理

```python
# config.py
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    HARNESS_API_KEY: str
    HARNESS_ACCOUNT_ID: str
    HARNESS_BASE_URL: str = "https://app.harness.io/gateway"
    
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str | None = None
    LLM_MODEL: str | None = None
    
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    OTEL_SERVICE_NAME: str = "harness-ai-agent"
    
    LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

## 8. 最佳实践

### 8.1 渐进式落地路径

| 阶段 | 目标 | 时间 | 关键动作 |
|------|------|------|----------|
| Phase 1 | AI代码审查 | 1-2周 | 配置CodeReviewer Agent |
| Phase 2 | 部署风险评估 | 2-3周 | 集成DeployAdvisor |
| Phase 3 | 智能测试 | 3-4周 | 落地测试生成与自我修复 |
| Phase 4 | 自动故障处理 | 4-6周 | 配置IncidentHandler + 人工确认网关 |
| Phase 5 | 全链路优化 | 持续 | 多Agent协作编排 |

### 8.2 安全准则

- ✅ **所有AI建议需人工确认后执行** - 使用ApprovalGateway
- ✅ **生产环境变更需审批流** - 配置多级审批
- ✅ **敏感操作记录审计日志** - 集成Harness审计
- ✅ **定期评估AI决策准确性** - 置信度追踪与模型优化

### 8.3 治理策略 (Policy as Code)

```rego
# Policy as Code 示例
deny[msg] {
    input.pipeline.stages[_].type == "Deployment"
    not input.pipeline.stages[_].spec.execution.steps[_].identifier == "ai_risk_assessment"
    msg := "Production deployment requires AI risk assessment"
}

deny[msg] {
    input.agent_result.confidence < 0.85
    not input.approval.status == "approved"
    msg := "Low confidence AI decision requires human approval"
}
```

---

## 9. 故障排查

### 9.1 常见问题

**Q: Agent执行失败，如何调试？**

```bash
# 查看Agent日志
docker logs ai-agent-container

# 检查Agent健康状态
curl http://ai-agent:8000/health

# 查看消息总线历史
python -m agents.orchestrator message-history --agent-id code-reviewer
```

**Q: 审批请求未收到通知？**

```bash
# 检查通知配置
curl http://ai-agent:8000/config/notifications

# 手动触发测试通知
python -m agents.approval_gateway test-notification \
  --approver "user@company.com" \
  --channel "slack"
```

**Q: 如何查看多Agent协作状态？**

```bash
# 查看工作流执行状态
python -m agents.orchestrator workflow-status \
  --workflow-id <uuid>

# 查看Agent间消息
python -m agents.orchestrator message-history \
  --workflow-id <uuid>
```

---

**Maintainer**: Platform Engineering Team  
**License**: MIT  
**Version**: 2026.1
