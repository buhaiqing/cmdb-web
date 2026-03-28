#!/usr/bin/env python3
"""
AGENTS.md 动态生成器
根据项目实际需求生成定制化的 AGENTS.md
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jinja2 import Template


@dataclass
class ProjectContext:
    """项目上下文信息."""
    name: str
    description: str
    team: str
    
    # 技术栈
    frontend_stack: dict[str, str] = field(default_factory=dict)
    backend_stack: dict[str, str] = field(default_factory=dict)
    database: str = ""
    message_queue: str = ""
    
    # Harness 配置
    harness_account: str = ""
    harness_org: str = ""
    harness_project: str = ""
    environments: list[str] = field(default_factory=lambda: ["dev", "staging", "prod"])
    
    # AI Agent 需求
    enable_code_review: bool = True
    enable_agentic_testing: bool = True
    enable_deploy_advisor: bool = True
    enable_incident_handler: bool = True
    enable_cost_optimizer: bool = False
    
    # 合规要求
    compliance_requirements: list[str] = field(default_factory=list)
    security_policies: list[str] = field(default_factory=list)
    
    # 特殊需求
    custom_rules: list[dict[str, Any]] = field(default_factory=list)


AGENTS_MD_TEMPLATE = """# AGENTS.md - {{ project.name }}

> **Version**: {{ version }}  
> **Generated**: {{ generated_at }}  
> **Team**: {{ project.team }}  
> **Description**: {{ project.description }}

---

## 1. 项目概览

### 1.1 技术架构
| 层级 | 技术选型 | 版本 |
|------|----------|------|
{% if project.frontend_stack %}
| 前端 | {{ project.frontend_stack.framework }} + {{ project.frontend_stack.language }} | {{ project.frontend_stack.version }} |
{% endif %}
{% if project.backend_stack %}
| 后端 | {{ project.backend_stack.framework }} + {{ project.backend_stack.language }} | {{ project.backend_stack.version }} |
{% endif %}
{% if project.database %}
| 数据库 | {{ project.database }} | - |
{% endif %}
{% if project.message_queue %}
| 消息队列 | {{ project.message_queue }} | - |
{% endif %}
| 部署 | Harness CD + GitOps | Latest |
| 观测 | OpenTelemetry + Harness CCM | v1.0+ |

### 1.2 部署环境
{% for env in project.environments %}
- **{{ env }}**: {{ env_descriptions.get(env, env) }}
{% endfor %}

---

## 2. AI Agent 配置

{% if project.enable_code_review %}
### 2.1 CodeReviewer Agent
**职责**: 代码审查、规范检查、安全扫描

**触发条件**:
- PR 创建/更新
- 代码提交到 main 分支前
- 定时全量扫描

**检查项**:
{% if project.frontend_stack %}
- 前端: ESLint, TypeScript 类型检查, Prettier 格式
{% endif %}
{% if project.backend_stack %}
- 后端: {{ "Ruff" if project.backend_stack.language == "Python" else "ESLint" }} 规范, 类型注解检查
{% endif %}
- 安全: 密钥泄露检测, SQL 注入检查, XSS 防护
- 性能: 代码复杂度, 重复代码检测

**集成点**: Harness STO (Security Testing Orchestration)
{% endif %}

{% if project.enable_deploy_advisor %}
### 2.2 DeployAdvisor Agent
**职责**: 部署风险评估、金丝雀配置建议

**触发条件**:
- 生产环境部署前
- 定时风险评估报告

**评估维度**:
- 当前系统健康度 (错误率、延迟)
- 最近变更影响范围
- 历史部署成功率
- 资源使用率

**决策规则**:
| 风险等级 | 错误率阈值 | 延迟阈值 | 建议操作 |
|----------|-----------|----------|----------|
| 低 | < 1% | P99 < 500ms | 正常部署 |
| 中 | 1-5% | P99 500-1000ms | 保守金丝雀 |
| 高 | > 5% | P99 > 1000ms | 阻断部署 |

**集成点**: Harness CD Pipeline + Feature Flags
{% endif %}

{% if project.enable_incident_handler %}
### 2.3 IncidentHandler Agent
**职责**: 故障诊断、自动回滚、告警处理

**触发条件**:
- 告警触发 (P1/P2)
- 错误率突增
- 服务可用性下降

**处理流程**:
1. 收集上下文 (日志、指标、最近变更)
2. 根因分析 (基于历史模式)
3. 生成修复建议
4. 自动执行 (如配置允许)
5. 通知相关团队

**自动修复范围**:
- ✅ 服务重启
- ✅ 配置回滚
- ✅ 流量切换
- ❌ 数据变更 (需人工确认)

**集成点**: Harness CCM + SRM + PagerDuty
{% endif %}

{% if project.enable_cost_optimizer %}
### 2.4 CostOptimizer Agent
**职责**: 资源优化建议、成本分析

**触发条件**:
- 月度成本报告
- 资源使用率异常
- 预算阈值告警

**优化建议**:
- 闲置资源清理
- 实例规格调整
- 自动伸缩策略优化
- Spot 实例使用建议

**集成点**: Harness CCM (Cloud Cost Management)
{% endif %}

---

## 3. 关键决策流

```
代码提交
    ↓
{% if project.enable_code_review %}
[AI Code Review] → 规范检查 → 安全扫描
    ↓ (通过)
{% endif %}
构建 & 测试
    ↓
{% if project.enable_deploy_advisor %}
[AI 风险评估] → 风险等级判定
    ↓ (低风险/人工确认)
{% endif %}
{% for env in project.environments %}
{% if env != "prod" %}
部署到 {{ env }} → 自动化测试
    ↓
{% else %}
生产部署 (金丝雀) → AI 健康检查
    ↓
全量发布 / 自动回滚
{% endif %}
{% endfor %}
    ↓
持续观测 [AI 异常检测]
```

---

## 4. 合规与治理

{% if project.compliance_requirements %}
### 4.1 合规要求
{% for req in project.compliance_requirements %}
- {{ req }}
{% endfor %}
{% endif %}

{% if project.security_policies %}
### 4.2 安全策略
{% for policy in project.security_policies %}
- {{ policy }}
{% endfor %}
{% endif %}

### 4.3 审计要求
- 所有 AI 决策记录到 Harness 审计日志
- 关键操作需人工确认
- 每月生成 AI 效能报告

---

## 5. 自定义规则

{% if project.custom_rules %}
{% for rule in project.custom_rules %}
### 5.{{ loop.index }} {{ rule.name }}
**描述**: {{ rule.description }}

**触发条件**:
{% for condition in rule.conditions %}
- {{ condition }}
{% endfor %}

**执行动作**:
{% for action in rule.actions %}
- {{ action }}
{% endfor %}
{% endfor %}
{% else %}
暂无自定义规则
{% endif %}

---

## 6. 参考文档

- [项目技术文档](./docs/)
- [Harness Pipeline 配置](./.harness/)
- [运维手册](./docs/operations.md)

---

**生成器**: Harness AI Agent Skill  
**维护者**: {{ project.team }}  
**更新频率**: 按需生成 / 每季度评审
"""


def generate_agents_md(project: ProjectContext, output_path: Path | None = None) -> str:
    """生成 AGENTS.md 文件.
    
    Args:
        project: 项目上下文信息
        output_path: 输出文件路径，None 则返回字符串
        
    Returns:
        生成的 AGENTS.md 内容
    """
    from datetime import datetime
    
    template = Template(AGENTS_MD_TEMPLATE)
    
    # 环境描述映射
    env_descriptions = {
        "dev": "开发环境，自动部署",
        "develop": "开发环境，自动部署",
        "staging": "预发布环境，自动化测试",
        "test": "测试环境，自动化测试",
        "prod": "生产环境，金丝雀发布",
        "production": "生产环境，金丝雀发布",
    }
    
    content = template.render(
        project=project,
        version="1.0.0",
        generated_at=datetime.now().isoformat(),
        env_descriptions=env_descriptions,
    )
    
    if output_path:
        output_path.write_text(content, encoding="utf-8")
        print(f"✅ AGENTS.md 已生成: {output_path}")
    
    return content


def interactive_generate() -> None:
    """交互式生成 AGENTS.md."""
    print("🚀 AGENTS.md 生成器")
    print("=" * 50)
    
    # 基本信息
    name = input("项目名称: ").strip()
    description = input("项目描述: ").strip()
    team = input("负责团队: ").strip()
    
    # 技术栈
    print("\n📦 技术栈配置")
    has_frontend = input("是否包含前端? (y/n): ").lower() == "y"
    frontend_stack = {}
    if has_frontend:
        frontend_stack = {
            "framework": input("前端框架 (React/Vue/Angular): ").strip() or "React",
            "language": "TypeScript",
            "version": "19",
        }
    
    has_backend = input("是否包含后端? (y/n): ").lower() == "y"
    backend_stack = {}
    if has_backend:
        backend_stack = {
            "framework": input("后端框架 (FastAPI/Django/Spring): ").strip() or "FastAPI",
            "language": input("后端语言 (Python/Java/Go): ").strip() or "Python",
            "version": "3.12",
        }
    
    database = input("数据库 (PostgreSQL/MySQL/MongoDB/无): ").strip()
    
    # AI Agent 配置
    print("\n🤖 AI Agent 配置")
    enable_code_review = input("启用代码审查 Agent? (y/n, 默认y): ").lower() != "n"
    enable_agentic_testing = input("启用 Agentic Testing? (y/n, 默认y): ").lower() != "n"
    enable_deploy_advisor = input("启用部署建议 Agent? (y/n, 默认y): ").lower() != "n"
    enable_incident_handler = input("启用故障处理 Agent? (y/n, 默认y): ").lower() != "n"
    enable_cost_optimizer = input("启用成本优化 Agent? (y/n, 默认n): ").lower() == "y"
    
    # 创建项目上下文
    project = ProjectContext(
        name=name,
        description=description,
        team=team,
        frontend_stack=frontend_stack,
        backend_stack=backend_stack,
        database=database if database != "无" else "",
        enable_code_review=enable_code_review,
        enable_agentic_testing=enable_agentic_testing,
        enable_deploy_advisor=enable_deploy_advisor,
        enable_incident_handler=enable_incident_handler,
        enable_cost_optimizer=enable_cost_optimizer,
    )
    
    # 生成文件
    output_path = Path("AGENTS.md")
    generate_agents_md(project, output_path)
    print(f"\n✨ 完成! 请查看 {output_path.absolute()}")


def generate_from_config(config_path: Path, output_path: Path | None = None) -> str:
    """从配置文件生成 AGENTS.md.
    
    Args:
        config_path: JSON/YAML 配置文件路径
        output_path: 输出文件路径
        
    Returns:
        生成的 AGENTS.md 内容
    """
    import yaml
    
    # 读取配置
    config_text = config_path.read_text(encoding="utf-8")
    if config_path.suffix in (".yaml", ".yml"):
        config = yaml.safe_load(config_text)
    else:
        config = json.loads(config_text)
    
    # 创建项目上下文
    project = ProjectContext(**config)
    
    # 生成
    if output_path is None:
        output_path = Path("AGENTS.md")
    
    return generate_agents_md(project, output_path)


def main():
    """命令行入口."""
    parser = argparse.ArgumentParser(description="AGENTS.md 生成器")
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="交互式生成"
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="从配置文件生成 (JSON/YAML)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("AGENTS.md"),
        help="输出文件路径"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_generate()
    elif args.config:
        generate_from_config(args.config, args.output)
    else:
        # 示例：生成默认配置
        example_project = ProjectContext(
            name="example-service",
            description="示例微服务",
            team="Platform Team",
            frontend_stack={
                "framework": "React",
                "language": "TypeScript",
                "version": "19",
            },
            backend_stack={
                "framework": "FastAPI",
                "language": "Python",
                "version": "3.12",
            },
            database="PostgreSQL",
            enable_code_review=True,
            enable_deploy_advisor=True,
            enable_incident_handler=True,
        )
        generate_agents_md(example_project, args.output)


if __name__ == "__main__":
    main()
