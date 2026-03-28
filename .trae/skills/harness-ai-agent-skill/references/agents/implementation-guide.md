# AI Agent 实现指南

> **框架**: FastAPI + Pydantic v2  
> **集成**: Harness API, OpenTelemetry, LLM (OpenAI/Claude)

---

## 1. 项目结构

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

## 2. 核心实现

### 2.1 基础 Agent 类

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

### 2.2 Harness 客户端

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

### 2.3 LLM 客户端

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

## 3. 具体 Agent 实现

### 3.1 代码审查 Agent

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

### 3.2 部署建议 Agent

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
        
        # 3. 获取部署历史
        # deployments = await self.harness.get_deployment_history(...)
        
        # 4. 风险分析
        risk_factors = self._analyze_risk(metrics, alerts)
        
        # 5. 生成金丝雀配置
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
        critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
        if critical_alerts:
            factors.append({
                "type": "active_alerts",
                "level": "high",
                "value": len(critical_alerts),
                "message": f"存在 {len(critical_alerts)} 个严重告警",
            })
        
        return factors
    
    def _generate_canary_config(self, risk_factors: list[dict]) -> dict:
        """生成金丝雀发布配置."""
        high_risk = any(f["level"] == "high" for f in risk_factors)
        medium_risk = any(f["level"] == "medium" for f in risk_factors)
        
        if high_risk:
            return {
                "strategy": "cautious",
                "steps": [5, 10, 25, 50, 100],
                "interval_minutes": 15,
                "auto_rollback": True,
                "rollback_thresholds": {
                    "error_rate": 0.02,
                    "latency_p99": 800,
                },
                "analysis_duration": "15m",
            }
        elif medium_risk:
            return {
                "strategy": "standard",
                "steps": [10, 25, 50, 100],
                "interval_minutes": 10,
                "auto_rollback": True,
                "rollback_thresholds": {
                    "error_rate": 0.03,
                    "latency_p99": 1000,
                },
                "analysis_duration": "10m",
            }
        else:
            return {
                "strategy": "aggressive",
                "steps": [25, 50, 100],
                "interval_minutes": 5,
                "auto_rollback": False,
                "rollback_thresholds": {
                    "error_rate": 0.05,
                    "latency_p99": 1500,
                },
                "analysis_duration": "5m",
            }
    
    def _calculate_overall_risk(self, risk_factors: list[dict]) -> str:
        """计算整体风险等级."""
        if any(f["level"] == "high" for f in risk_factors):
            return "high"
        elif any(f["level"] == "medium" for f in risk_factors):
            return "medium"
        return "low"
    
    def _summarize_metrics(self, metrics: dict) -> dict:
        """摘要指标."""
        return {
            "error_rate": f"{metrics.get('error_rate', 0):.2%}",
            "latency_p50": f"{metrics.get('p50_latency', 0)}ms",
            "latency_p99": f"{metrics.get('p99_latency', 0)}ms",
            "throughput": f"{metrics.get('requests_per_second', 0):.0f} req/s",
        }
    
    def _recommend_deploy_action(
        self,
        risk_level: str,
        force_deploy: bool,
    ) -> str:
        """推荐部署操作."""
        if risk_level == "high" and not force_deploy:
            return "建议暂缓部署，先解决线上问题"
        elif risk_level == "high":
            return "强制部署，建议启用自动回滚并密切监控"
        elif risk_level == "medium":
            return "可以部署，建议使用保守的金丝雀策略"
        return "风险较低，可以正常部署"
```

### 3.3 故障处理 Agent

```python
# agents/incident_handler.py
from dataclasses import dataclass

from models import IncidentContext

from .base import AgentResult, BaseAgent


@dataclass
class IncidentContext:
    """故障上下文."""
    service: str
    alert_name: str
    severity: str
    description: str
    metrics: dict | None = None
    logs: list[str] | None = None


class IncidentHandlerAgent(BaseAgent[IncidentContext]):
    """故障处理 Agent."""
    
    async def execute(self, context: IncidentContext) -> AgentResult:
        """处理故障事件."""
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
        
        # 2. 生成修复建议
        remediation = self._generate_remediation(context, root_cause)
        
        # 3. 判断是否需要自动回滚
        should_rollback = self._should_auto_rollback(context, root_cause)
        
        # 4. 执行自动修复 (如果是安全的)
        if remediation.get("auto_fixable") and remediation.get("action"):
            action_result = await self._execute_auto_fix(remediation["action"])
        else:
            action_result = None
        
        await self.log_action(
            "incident_handling_completed",
            {
                "service": context.service,
                "root_cause": root_cause.get("type"),
                "auto_fix_applied": action_result is not None,
            },
        )
        
        return AgentResult(
            success=True,
            data={
                "root_cause": root_cause,
                "remediation": remediation,
                "should_rollback": should_rollback,
                "auto_fix_result": action_result,
            },
            confidence=root_cause.get("confidence", 0.5),
            recommended_action=remediation.get("recommendation"),
        )
    
    async def _analyze_root_cause(self, context: IncidentContext) -> dict:
        """分析故障根因."""
        # 基于告警名称和描述进行模式匹配
        alert_patterns = {
            "HighErrorRate": {
                "type": "deployment_issue",
                "confidence": 0.8,
                "checklist": [
                    "检查最近部署",
                    "查看错误日志",
                    "检查依赖服务状态",
                ],
            },
            "HighLatency": {
                "type": "performance_degradation",
                "confidence": 0.7,
                "checklist": [
                    "检查数据库查询",
                    "检查外部 API 调用",
                    "检查资源使用率",
                ],
            },
            "ServiceDown": {
                "type": "service_failure",
                "confidence": 0.9,
                "checklist": [
                    "检查 Pod 状态",
                    "检查资源限制",
                    "检查配置变更",
                ],
            },
        }
        
        for pattern, analysis in alert_patterns.items():
            if pattern in context.alert_name:
                return analysis
        
        # 使用 LLM 进行深度分析
        if self.llm and context.logs:
            prompt = f"""分析以下故障日志，找出根因:

告警: {context.alert_name}
描述: {context.description}

日志:
{chr(10).join(context.logs[-50:])}  # 最近 50 行

请给出:
1. 最可能的根因类型
2. 置信度 (0-1)
3. 建议检查的方向
"""
            response = await self.llm.complete(prompt, temperature=0.3)
            # 解析响应...
            return {
                "type": "llm_analysis",
                "confidence": 0.6,
                "analysis": response,
            }
        
        return {
            "type": "unknown",
            "confidence": 0.3,
            "checklist": ["需要人工介入分析"],
        }
    
    def _generate_remediation(
        self,
        context: IncidentContext,
        root_cause: dict,
    ) -> dict:
        """生成修复方案."""
        remediation_map = {
            "deployment_issue": {
                "auto_fixable": True,
                "action": "rollback",
                "recommendation": "建议回滚到上一个稳定版本",
                "steps": [
                    "触发回滚 Pipeline",
                    "监控回滚过程",
                    "验证服务恢复",
                ],
            },
            "performance_degradation": {
                "auto_fixable": False,
                "action": None,
                "recommendation": "需要人工分析和优化",
                "steps": [
                    "分析性能瓶颈",
                    "考虑扩容",
                    "优化慢查询",
                ],
            },
            "service_failure": {
                "auto_fixable": True,
                "action": "restart",
                "recommendation": "尝试重启服务",
                "steps": [
                    "滚动重启 Pod",
                    "检查启动日志",
                    "验证健康检查",
                ],
            },
        }
        
        return remediation_map.get(
            root_cause.get("type"),
            {
                "auto_fixable": False,
                "action": None,
                "recommendation": "需要人工介入",
                "steps": ["联系 on-call 工程师"],
            },
        )
    
    def _should_auto_rollback(
        self,
        context: IncidentContext,
        root_cause: dict,
    ) -> bool:
        """判断是否应该自动回滚."""
        # 严重级别且是部署问题
        if context.severity == "critical" and root_cause.get("type") == "deployment_issue":
            return True
        
        # 错误率超过阈值
        if context.metrics and context.metrics.get("error_rate", 0) > 0.1:
            return True
        
        return False
    
    async def _execute_auto_fix(self, action: str) -> dict:
        """执行自动修复."""
        if action == "rollback":
            try:
                result = await self.harness.trigger_pipeline(
                    pipeline_id="rollback_pipeline",
                    org_id="default",
                    project_id="my_project",
                )
                return {
                    "action": "rollback",
                    "status": "triggered",
                    "execution_id": result.get("execution_id"),
                }
            except Exception as e:
                return {
                    "action": "rollback",
                    "status": "failed",
                    "error": str(e),
                }
        
        elif action == "restart":
            # 调用 K8s API 重启服务
            return {
                "action": "restart",
                "status": "not_implemented",
            }
        
        return {
            "action": action,
            "status": "unknown_action",
        }
```

---

## 4. FastAPI 服务入口

```python
# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from agents.code_reviewer import CodeReviewAgent, CodeReviewContext
from agents.deploy_advisor import DeployAdvisorAgent, DeployContext
from agents.incident_handler import IncidentContext, IncidentHandlerAgent
from config import Settings
from models import (
    CodeReviewRequest,
    CodeReviewResponse,
    DeployAnalysisRequest,
    DeployAnalysisResponse,
    IncidentHandlingRequest,
    IncidentHandlingResponse,
)
from services.harness_client import HarnessClient
from services.llm_client import LLMClient

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期."""
    # 初始化
    app.state.harness = HarnessClient(
        api_key=settings.HARNESS_API_KEY,
        account_id=settings.HARNESS_ACCOUNT_ID,
    )
    
    app.state.llm = LLMClient(
        provider=settings.LLM_PROVIDER,
        api_key=settings.LLM_API_KEY,
        model=settings.LLM_MODEL,
    )
    
    # 初始化 Agents
    app.state.code_reviewer = CodeReviewAgent(app.state.harness, app.state.llm)
    app.state.deploy_advisor = DeployAdvisorAgent(app.state.harness, app.state.llm)
    app.state.incident_handler = IncidentHandlerAgent(app.state.harness, app.state.llm)
    
    yield
    
    # 清理
    await app.state.harness.close()


app = FastAPI(
    title="Harness AI Agent Service",
    description="AI-powered agents for Harness Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# OpenTelemetry 埋点
FastAPIInstrumentor.instrument_app(app)


tracer = trace.get_tracer(__name__)


@app.post("/review/code", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """代码审查接口."""
    with tracer.start_as_current_span("code_review") as span:
        span.set_attribute("file.path", str(request.file_path))
        span.set_attribute("language", request.language)
        
        agent: CodeReviewAgent = app.state.code_reviewer
        
        context = CodeReviewContext(
            file_path=request.file_path,
            content=request.content,
            language=request.language,
            pr_description=request.pr_description,
        )
        
        result = await agent.execute(context)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return CodeReviewResponse(
            success=True,
            comments=result.data.get("comments", []),
            summary=result.data.get("summary", ""),
            confidence=result.confidence,
            recommended_action=result.recommended_action,
        )


@app.post("/deploy/analyze", response_model=DeployAnalysisResponse)
async def analyze_deployment(request: DeployAnalysisRequest):
    """部署风险分析接口."""
    with tracer.start_as_current_span("deploy_analysis") as span:
        span.set_attribute("service", request.service)
        span.set_attribute("environment", request.environment)
        
        agent: DeployAdvisorAgent = app.state.deploy_advisor
        
        context = DeployContext(
            service=request.service,
            environment=request.environment,
            version=request.version,
            force_deploy=request.force_deploy,
        )
        
        result = await agent.execute(context)
        
        return DeployAnalysisResponse(
            success=result.success,
            risk_level=result.data.get("risk_level", "unknown"),
            risk_factors=result.data.get("risk_factors", []),
            canary_config=result.data.get("canary_config", {}),
            metrics_summary=result.data.get("metrics_summary", {}),
            confidence=result.confidence,
            recommended_action=result.recommended_action,
        )


@app.post("/incident/handle", response_model=IncidentHandlingResponse)
async def handle_incident(request: IncidentHandlingRequest):
    """故障处理接口."""
    with tracer.start_as_current_span("incident_handling") as span:
        span.set_attribute("service", request.service)
        span.set_attribute("alert", request.alert_name)
        
        agent: IncidentHandlerAgent = app.state.incident_handler
        
        context = IncidentContext(
            service=request.service,
            alert_name=request.alert_name,
            severity=request.severity,
            description=request.description,
            metrics=request.metrics,
            logs=request.logs,
        )
        
        result = await agent.execute(context)
        
        return IncidentHandlingResponse(
            success=result.success,
            root_cause=result.data.get("root_cause", {}),
            remediation=result.data.get("remediation", {}),
            should_rollback=result.data.get("should_rollback", False),
            auto_fix_result=result.data.get("auto_fix_result"),
            confidence=result.confidence,
            recommended_action=result.recommended_action,
        )


@app.get("/health")
async def health_check():
    """健康检查."""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 5. 数据模型

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

---

## 6. 配置

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
    
    # Harness
    HARNESS_API_KEY: str
    HARNESS_ACCOUNT_ID: str
    HARNESS_BASE_URL: str = "https://app.harness.io/gateway"
    
    # LLM
    LLM_PROVIDER: str = "openai"  # openai, anthropic
    LLM_API_KEY: str | None = None
    LLM_MODEL: str | None = None
    
    # OpenTelemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    OTEL_SERVICE_NAME: str = "harness-ai-agent"
    
    # 应用
    LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```
