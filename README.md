# Meridian Electronics AI Assistant

A customer support chat assistant for Meridian Electronics. Customers enter their email, then ask questions about their orders, products, and account. The backend fetches real data from an MCP server and generates responses with GPT-5.4 mini.

## Architecture

```
Browser
  │
  ▼
CloudFront ──► S3 (Next.js static export)
  │
  │  /api/* requests
  ▼
API Gateway (HTTP API)
  │
  ▼
Lambda (FastAPI + Mangum)
  │
  ├── OpenAI GPT-5.4 mini
  └── MCP server (order/customer data)
```

## Stack

- **Frontend**: Next.js 14 (static export) → S3 + CloudFront
- **Backend**: FastAPI (Python 3.12) on AWS Lambda via Mangum
- **AI**: GPT-5.4 mini via OpenAI API
- **Data**: External MCP server — all customer and order data lives there, not in this repo
- **Infra**: Terraform — Lambda, API Gateway, S3, CloudFront, GitHub OIDC IAM

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
| `GET` | `/api/health` | CloudFront/API Gateway health check |
| `POST` | `/api/chat` | CloudFront/API Gateway chat endpoint |

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

Terraform manages: Lambda, API Gateway, S3, CloudFront, and the GitHub OIDC IAM role.

The existing CloudFront distribution is kept in place. Terraform updates it with an `/api/*` behavior that forwards API requests to API Gateway, while the default behavior continues to serve the static frontend from S3.

### First-time setup

1. Copy and fill in `terraform.tfvars`:
```bash
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
```
Set `openai_api_key`. Set `create_github_oidc_provider = false` if one already exists in the account.

2. Build the initial Lambda package:
```bash
bash scripts/build_lambda_package.sh
```

3. Apply:
```bash
cd infra/terraform
terraform init
terraform apply
```

4. Set these GitHub Actions variables from the Terraform outputs:

| GitHub Variable | Terraform Output |
|----------------|-----------------|
| `BACKEND_LAMBDA_FUNCTION_NAME` | `lambda_function_name` |
| `FRONTEND_S3_BUCKET` | `frontend_s3_bucket` |
| `CLOUDFRONT_DISTRIBUTION_ID` | `cloudfront_distribution_id` |

After the new Lambda path is verified, scale the old manually-created ECS service to `0` or delete the old ECS/ALB resources in AWS if they still exist outside this Terraform state.

## CI/CD

- **`ci.yml`**: Runs on PRs — backend tests + frontend build
- **`deploy.yml`**: Runs on push to `main` — builds and updates the Lambda backend, syncs frontend to S3, invalidates CloudFront
