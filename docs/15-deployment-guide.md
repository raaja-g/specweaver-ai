### Deployment Guide

#### Local Development Setup

Prerequisites:
- Python 3.11+
- Node.js 18+
- Docker Desktop
- Git

Steps:
```bash
# Clone repository
git clone https://github.com/raaja-g/specweaver-ai.git
cd specweaver-ai

# Backend setup
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend setup
cd ui
npm install
cd ..

# Environment setup
cp config/.env.example .env
# Edit .env with your API keys:
# GROQ_API_KEY=...
# GOOGLE_API_KEY=...
# OPENAI_API_KEY=...

# Local LLM (optional)
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama pull llama3

# Start services
docker-compose up -d  # Redis, DB
uvicorn api.app:app --reload --port 8080
cd ui && npm start  # React on port 3000

# n8n (optional)
docker run -it --rm -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

#### Production Deployment (AWS)

Infrastructure:
- ECS Fargate for API/Workers
- RDS PostgreSQL for metrics
- ElastiCache Redis for queues
- S3 for artifacts
- CloudFront for UI
- Secrets Manager for credentials
- ALB for load balancing

Steps:
```bash
# Build and push images
docker build -t specweaver-api -f docker/Dockerfile .
docker tag specweaver-api:latest $ECR_REGISTRY/specweaver-api:latest
docker push $ECR_REGISTRY/specweaver-api:latest

# Deploy with Terraform/CDK
cd infrastructure
terraform apply -var-file=prod.tfvars

# Or using docker-compose for staging
docker-compose -f docker-compose.prod.yml up -d
```

Environment Variables (production):
```yaml
AWS_REGION: us-east-1
SECRETS_PREFIX: /specweaver/prod/
DATABASE_URL: postgresql://...
REDIS_URL: redis://...
S3_BUCKET: specweaver-artifacts
EXECUTION_MODE_DEFAULT: mock
```

#### CI/CD Pipeline

GitHub Actions workflow:
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/unit
      - run: docker build -t test .
      - run: docker run test pytest tests/integration
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
      - run: |
          docker build -t specweaver .
          docker push $ECR_REGISTRY/specweaver:latest
      - run: aws ecs update-service --force-new-deployment
```

#### Monitoring & Alerting

Metrics:
- CloudWatch: API latency, error rates, queue depth
- Prometheus: custom metrics (test generation time, LLM latency)
- Grafana dashboards: real-time monitoring

Alerts:
- PagerDuty: critical failures (API down, DB unreachable)
- Slack: warnings (high queue depth, LLM fallbacks)
- Email: daily reports (test coverage, flaky tests)

Health checks:
- `/health`: basic liveness
- `/ready`: dependencies check (DB, Redis, LLMs)
- `/metrics`: Prometheus endpoint

#### Backup & Recovery

Backup strategy:
- RDS: automated daily snapshots, 7-day retention
- S3 artifacts: versioning enabled, lifecycle policies
- Configuration: stored in Git, secrets in AWS Secrets Manager

Disaster recovery:
- RPO: 24 hours (daily backups)
- RTO: 2 hours (automated restore)
- Runbook: documented procedures for common failures
- Rollback: blue-green deployments, quick revert capability

#### Security Hardening

- Network: VPC with private subnets, security groups
- Secrets: AWS Secrets Manager, rotation policies
- Authentication: OAuth2/OIDC for UI, API keys for MCP
- Authorization: RBAC, least privilege IAM roles
- Scanning: Gitleaks, Trivy for containers, OWASP ZAP
- Compliance: SOC2 controls, audit logging
