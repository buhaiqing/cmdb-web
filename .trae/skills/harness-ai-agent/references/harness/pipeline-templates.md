# Harness Pipeline 模板 (2026 Edition)

> **集成**: STO, CCM, SRM, GitOps, Feature Flags  
> **治理**: Policy as Code, OPA (Open Policy Agent)

---

参考： [developer.harness.io/ ](https://developer.harness.io/)

## 1. 完整 CI/CD Pipeline

```yaml
# templates/pipelines/fullstack-cicd.yml
pipeline:
  name: Fullstack CI/CD
  identifier: fullstack_cicd
  description: "AI-assisted full-stack CI/CD pipeline"
  projectIdentifier: <+project.identifier>
  orgIdentifier: <+org.identifier>
  tags:
    - ai-assisted
    - fullstack
    - 2026-standard

  stages:
    # ==========================================
    # Stage 1: 代码质量与 AI 审查
    # ==========================================
    - stage:
        name: Code Quality
        identifier: code_quality
        type: CI
        spec:
          cloneCodebase: true
          execution:
            steps:
              # Python 后端检查
              - step:
                  name: Python Lint
                  identifier: python_lint
                  type: Run
                  spec:
                    connectorRef: account.dockerhub
                    image: ghcr.io/astral-sh/ruff:latest
                    command: |
                      ruff check src/ --output-format=github
                      ruff format --check src/
                    resources:
                      limits:
                        memory: 1Gi
                        cpu: "1"

              - step:
                  name: Python Type Check
                  identifier: python_type_check
                  type: Run
                  spec:
                    image: python:3.12-slim
                    command: |
                      pip install mypy pydantic
                      mypy src/ --strict --ignore-missing-imports

              # 前端检查
              - step:
                  name: Frontend Lint
                  identifier: frontend_lint
                  type: Run
                  spec:
                    image: node:22-alpine
                    command: |
                      cd frontend
                      npm ci
                      npm run lint
                      npm run type-check

              # AI 代码审查
              - step:
                  name: AI Code Review
                  identifier: ai_code_review
                  type: Run
                  spec:
                    image: python:3.12-slim
                    connectorRef: account.dockerhub
                    command: |
                      pip install -r requirements-agent.txt
                      python -m agents.code_reviewer \
                        --backend-path src/ \
                        --frontend-path frontend/src/ \
                        --output-format harness
                  failureStrategies:
                    - onFailure:
                        errors:
                          - AllErrors
                        action:
                          type: MarkAsWarning  # AI 审查失败不阻断，仅警告

              # 安全扫描 (STO)
              - step:
                  name: Security Scan
                  identifier: security_scan
                  type: Security
                  spec:
                    scanType: SAST
                    scanner: Snyk
                    config: default
                    target:
                      type: repository
                      detection: auto
                    advanced:
                      log:
                        level: info

          infrastructure:
            type: KubernetesDirect
            spec:
              connectorRef: account.k8s_cluster
              namespace: harness-ci
              automountServiceAccountToken: true
              os: Linux

    # ==========================================
    # Stage 2: 测试
    # ==========================================
    - stage:
        name: Testing
        identifier: testing
        type: CI
        spec:
          execution:
            steps:
              # Python 测试
              - step:
                  name: Python Unit Tests
                  identifier: python_unit_tests
                  type: Run
                  spec:
                    image: python:3.12-slim
                    command: |
                      pip install pytest pytest-cov pytest-asyncio
                      pytest tests/unit \
                        --cov=src \
                        --cov-report=xml:coverage.xml \
                        --cov-report=term \
                        --cov-fail-under=80

              - step:
                  name: Python Integration Tests
                  identifier: python_integration_tests
                  type: Run
                  spec:
                    image: python:3.12-slim
                    command: |
                      pip install pytest pytest-asyncio httpx
                      pytest tests/integration -v

              # 前端测试
              - step:
                  name: Frontend Unit Tests
                  identifier: frontend_unit_tests
                  type: Run
                  spec:
                    image: node:22-alpine
                    command: |
                      cd frontend
                      npm ci
                      npm run test:unit -- --coverage

              - step:
                  name: Frontend E2E Tests
                  identifier: frontend_e2e
                  type: Run
                  spec:
                    image: mcr.microsoft.com/playwright:v1.42-jammy
                    command: |
                      cd frontend
                      npm ci
                      npx playwright install
                      npm run test:e2e

          infrastructure:
            type: KubernetesDirect
            spec:
              connectorRef: account.k8s_cluster
              namespace: harness-ci

    # ==========================================
    # Stage 3: AI 部署风险评估
    # ==========================================
    - stage:
        name: AI Risk Assessment
        identifier: ai_risk_assessment
        type: Custom
        spec:
          execution:
            steps:
              - step:
                  name: Analyze Deployment Risk
                  identifier: analyze_risk
                  type: Run
                  spec:
                    image: python:3.12-slim
                    command: |
                      pip install harness-ai-agent
                      python -m agents.deploy_advisor analyze \
                        --service <+service.name> \
                        --environment staging \
                        --output harness

              - step:
                  name: Suggest Canary Config
                  identifier: suggest_canary
                  type: Run
                  spec:
                    image: python:3.12-slim
                    command: |
                      python -m agents.deploy_advisor canary-config \
                        --service <+service.name> \
                        --output-file canary-config.json

    # ==========================================
    # Stage 4: 构建与推送
    # ==========================================
    - stage:
        name: Build and Push
        identifier: build_push
        type: CI
        spec:
          execution:
            steps:
              # 构建后端镜像
              - step:
                  name: Build Backend Image
                  identifier: build_backend
                  type: BuildAndPushECR
                  spec:
                    connectorRef: account.aws_ecr
                    region: us-east-1
                    account: "123456789012"
                    imageName: myapp-backend
                    tags:
                      - <+pipeline.sequenceId>
                      - <+gitbranch>
                      - <+gitcommit>
                    dockerfile: Dockerfile
                    context: .
                    target: production
                    multiArch:
                      - linux/amd64
                      - linux/arm64

              # 构建前端镜像
              - step:
                  name: Build Frontend Image
                  identifier: build_frontend
                  type: BuildAndPushECR
                  spec:
                    connectorRef: account.aws_ecr
                    region: us-east-1
                    account: "123456789012"
                    imageName: myapp-frontend
                    tags:
                      - <+pipeline.sequenceId>
                      - <+gitbranch>
                    dockerfile: frontend/Dockerfile
                    context: frontend

              # Trivy 镜像扫描
              - step:
                  name: Container Scan
                  identifier: container_scan
                  type: Run
                  spec:
                    image: aquasec/trivy:latest
                    command: |
                      trivy image \
                        --exit-code 1 \
                        --severity HIGH,CRITICAL \
                        --format sarif \
                        --output trivy-results.sarif \
                        123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp-backend:<+pipeline.sequenceId>

    # ==========================================
    # Stage 5: 部署到 Staging (GitOps)
    # ==========================================
    - stage:
        name: Deploy Staging
        identifier: deploy_staging
        type: Deployment
        spec:
          service:
            serviceRef: myapp_service
          environment:
            environmentRef: staging
            infrastructureDefinitions:
              - identifier: k8s_staging
          execution:
            steps:
              - step:
                  name: GitOps Sync
                  identifier: gitops_sync
                  type: GitOpsUpdateReleaseRepo
                  spec:
                    connectorRef: account.github
                    repoName: myorg/gitops-config
                    branch: main
                    filePaths:
                      - environments/staging/myapp/values.yaml
                    values:
                      backend:
                        image:
                          tag: <+pipeline.sequenceId>
                      frontend:
                        image:
                          tag: <+pipeline.sequenceId>

              - step:
                  name: Wait for Sync
                  identifier: wait_sync
                  type: GitOpsFetchLinkedApps
                  timeout: 10m

              - step:
                  name: Health Check
                  identifier: health_check
                  type: K8sRollingDeploy
                  spec:
                    skipDryRun: false

    # ==========================================
    # Stage 6: 生产金丝雀发布
    # ==========================================
    - stage:
        name: Deploy Production
        identifier: deploy_prod
        type: Deployment
        spec:
          service:
            serviceRef: myapp_service
          environment:
            environmentRef: production
          execution:
            steps:
              - step:
                  name: Canary Deployment
                  identifier: canary_deploy
                  type: K8sCanaryDeploy
                  spec:
                    instanceSelection:
                      type: Count
                      spec:
                        count: 1  # 初始 1 个实例
                    skipDryRun: false

              - step:
                  name: AI Health Check
                  identifier: ai_health_check
                  type: Run
                  spec:
                    image: python:3.12-slim
                    command: |
                      python -m agents.incident_handler health-check \
                        --service myapp \
                        --duration 5m \
                        --thresholds error_rate=0.01,latency_p99=500

              - step:
                  name: Canary Analysis
                  identifier: canary_analysis
                  type: Verify
                  timeout: 15m
                  spec:
                    type: Canary
                    monitoredService:
                      type: Default
                      spec: {}
                    spec:
                      sensitivity: HIGH
                      duration: 10m
                      baseline: LastSuccessfulExecution

              - step:
                  name: Promote or Rollback
                  identifier: promote_or_rollback
                  type: Run
                  spec:
                    image: harness/delegate:latest
                    command: |
                      if [ "<+pipeline.stages.deploy_prod.spec.execution.steps.canary_analysis.output.verifyResult>" = "PASSED" ]; then
                        echo "Canary passed, promoting to full deployment"
                      else
                        echo "Canary failed, triggering rollback"
                        harness pipeline trigger --id rollback_pipeline
                        exit 1
                      fi

  variables:
    - name: HARNESS_API_KEY
      type: Secret
      value: account.harness_api_key
    - name: SLACK_WEBHOOK
      type: Secret
      value: account.slack_webhook

  notificationRules:
    - name: Notify on Failure
      identifier: notify_failure
      pipelineEvents:
        - type: PipelineFailed
      notificationMethod:
        type: Slack
        spec:
          webhook: <+pipeline.variables.SLACK_WEBHOOK>
```

---

## 2. Policy as Code (OPA)

```yaml
# templates/configs/security-policies.rego
package harness.security

# 禁止部署到生产环境如果没有通过安全扫描
deny[msg] {
    input.pipeline.stages[_].type == "Deployment"
    input.pipeline.stages[_].spec.environment.environmentRef == "production"
    not input.pipeline.stages[_].identifier == "security_scan"
    msg := "Production deployment requires security scanning stage"
}

# 要求所有部署阶段有回滚策略
deny[msg] {
    input.pipeline.stages[_].type == "Deployment"
    not input.pipeline.stages[_].spec.execution.steps[_].identifier == "rollback"
    msg := "All deployment stages must include rollback step"
}

# 要求镜像标签不能是 latest
deny[msg] {
    input.pipeline.stages[_].spec.execution.steps[_].type == "BuildAndPushECR"
    input.pipeline.stages[_].spec.execution.steps[_].spec.tags[_] == "latest"
    msg := "Image tag 'latest' is not allowed"
}

# 要求 AI 审查阶段
deny[msg] {
    not input.pipeline.stages[_].spec.execution.steps[_].identifier == "ai_code_review"
    msg := "Pipeline must include AI code review step"
}
```

---

## 3. Feature Flags 配置

```yaml
# templates/configs/feature-flags.yml
featureFlags:
  - name: new_dashboard_v2
    identifier: new_dashboard_v2
    description: "New dashboard UI with AI insights"
    permanent: false
    defaultOn: false
    variations:
      - identifier: enabled
        value: "true"
      - identifier: disabled
        value: "false"
    targets:
      - identifier: beta_users
        variation: enabled
      - identifier: all_users
        variation: disabled

  - name: ai_assistant_enabled
    identifier: ai_assistant_enabled
    description: "AI assistant for code review"
    permanent: false
    defaultOn: true
    variations:
      - identifier: enabled
        value: "true"
      - identifier: disabled
        value: "false"

  - name: dark_mode_default
    identifier: dark_mode_default
    description: "Default to dark mode"
    permanent: false
    defaultOn: false
    variations:
      - identifier: dark
        value: "dark"
      - identifier: light
        value: "light"
```

---

## 4. GitOps 应用配置

```yaml
# templates/configs/gitops-application.yml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-staging
  namespace: argocd
  annotations:
    harness.io/service: myapp
    harness.io/environment: staging
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/gitops-config
    targetRevision: HEAD
    path: environments/staging/myapp
    helm:
      valueFiles:
        - values.yaml
        - values-staging.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

---

## 5. 监控与 SLO 配置

```yaml
# templates/configs/slo-config.yml
monitoredServices:
  - name: myapp-backend
    identifier: myapp_backend
    serviceRef: myapp_service
    environmentRef: production
    sources:
      healthSources:
        - name: Prometheus Metrics
          identifier: prometheus_metrics
          type: Prometheus
          spec:
            connectorRef: account.prometheus
            metricDefinitions:
              - identifier: error_rate
                metricName: Error Rate
                query: |
                  sum(rate(http_requests_total{status=~"5.."}[5m]))
                  /
                  sum(rate(http_requests_total[5m]))
                riskProfile:
                  category: Errors
                  metricType: Error
                sli:
                  enabled: true
                analysis:
                  liveMonitoring:
                    enabled: true
                  deploymentVerification:
                    enabled: true

slos:
  - name: Availability SLO
    identifier: availability_slo
    monitoredServiceRef: myapp_backend
    type: Availability
    spec:
      period:
        type: Rolling
        spec:
          duration: 30d
      target:
        type: Percentage
        spec:
          value: 99.9
      budgetingMethod: Occurrences

  - name: Latency SLO
    identifier: latency_slo
    monitoredServiceRef: myapp_backend
    type: Latency
    spec:
      period:
        type: Rolling
        spec:
          duration: 30d
      target:
        type: Percentage
        spec:
          value: 95
      latency:
        type: Threshold
        spec:
          threshold: 200  # ms
```

---

## 6. 成本管理 (CCM)

```yaml
# templates/configs/ccm-budgets.yml
budgets:
  - name: Production Infrastructure
    identifier: prod_infrastructure
    period: MONTHLY
    type: SPECIFIED_AMOUNT
    amount: 10000
    notifyOnForecastedCost: true
    alertThresholds:
      - percentage: 50
        emailAddresses:
          - platform-team@company.com
      - percentage: 80
        emailAddresses:
          - platform-team@company.com
          - finance@company.com
      - percentage: 100
        emailAddresses:
          - platform-team@company.com
          - finance@company.com
          - cto@company.com

autoStopping:
  - name: Non-Prod Instances
    identifier: non_prod_autostop
    cloudProvider: AWS
    resources:
      - type: EC2
        tags:
          - key: Environment
            value: staging
      - type: RDS
        tags:
          - key: Environment
            value: dev
    schedule:
      timezone: Asia/Shanghai
      on: "09:00"
      off: "19:00"
      days:
        - MON
        - TUE
        - WED
        - THU
        - FRI
```
