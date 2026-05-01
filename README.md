# Meridian Electronics AI Assistant

A customer support chat assistant for Meridian Electronics. Customers enter their email, then ask questions about their orders, products, and account. The backend fetches real data from an MCP server and generates responses with GPT-4o-mini.

## Architecture

```
Browser
  │
  ▼
CloudFront ──► S3 (Next.js static export)
  │
  │  (API calls)
  ▼
API Gateway (HTTP API)
  │
  ▼
ALB
  │
  ▼
ECS Fargate (FastAPI, port 8000)
  │
  ├── OpenAI GPT-4o-mini
  └── MCP server (order/customer data)
```

## Stack

- **Frontend**: Next.js 14 (static export) → S3 + CloudFront
- **Backend**: FastAPI (Python 3.12) on ECS Fargate
- **AI**: GPT-4o-mini via OpenAI API
- **Data**: External MCP server — all customer and order data lives there, not in this repo
- **Infra**: Terraform — ECR, Secrets Manager, API Gateway, ALB, S3, CloudFront, GitHub OIDC IAM

## Local development

**Prerequisites**: Python 3.12+, `uv`, Node.js 18+

1. Copy env file and set `OPENAI_API_KEY`:
```bash
cp .env.example .env
```

2. Start the backend:
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

3. Start the frontend:
```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

4. Open http://localhost:3000, enter any customer email, and start chatting.

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Send a message |

`POST /chat` body:
```json
{ "customer_email": "user@example.com", "message": "Where is my order?" }
```

## Tests

```bash
cd backend
uv run pytest -q
```

## Infrastructure

Terraform manages: ECR, Secrets Manager (OpenAI key), API Gateway, ALB, S3, CloudFront, and the GitHub OIDC IAM role.

The ECS cluster/service and VPC are pre-existing. Their IDs are hardcoded in `infra/terraform/main.tf` under the `alb` module.

### First-time setup

1. Copy and fill in `terraform.tfvars`:
```bash
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
```
Set `openai_api_key`. Set `create_github_oidc_provider = false` if one already exists in the account.

2. Apply:
```bash
cd infra/terraform
terraform init
terraform apply
```

3. Set these GitHub Actions variables from the Terraform outputs:

| GitHub Variable | Terraform Output |
|----------------|-----------------|
| `NEXT_PUBLIC_API_BASE_URL` | `api_gateway_invoke_url` |
| `FRONTEND_S3_BUCKET` | `frontend_s3_bucket` |
| `CLOUDFRONT_DISTRIBUTION_ID` | `cloudfront_distribution_id` |
| `OPENAI_SECRET_ARN` | `openai_secret_arn` |
| `ALLOWED_ORIGINS` | `frontend_origin_https` |

## CI/CD

- **`ci.yml`**: Runs on PRs — backend tests + frontend build
- **`deploy.yml`**: Runs on push to `main` — builds and pushes Docker image to ECR, updates ECS service, syncs frontend to S3, invalidates CloudFront
