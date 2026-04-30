# Meridian Electronics AI Assistant

A production-oriented MVP support assistant for Meridian Electronics.

It provides:

- Next.js chat frontend (static export on **S3 + CloudFront**)
- FastAPI backend with a **POST /chat** endpoint (no JWT; customer context uses `DEFAULT_CUSTOMER_EMAIL`)
- OpenAI GPT-4o-mini for response generation and tool-calling
- MCP integration for factual business tool lookups
- AWS deployment: **CloudFront** (UI) → **API Gateway HTTP API** → **ALB** → **ECS Fargate** (API)

## Architecture

```text
Browser
   |
   v
Amazon CloudFront  --->  S3 bucket (Next.js static export)
   |
   |  (browser calls API)
   v
API Gateway (HTTP API)  --->  ALB  --->  ECS Fargate (FastAPI)
                                    |
                                    +-- OpenAI, MCP server
```

Terraform provisions **ECR**, **Secrets Manager** (OpenAI key only), **HTTP API Gateway**, and **S3 + CloudFront** for the frontend. **ECS and the ALB** are expected to exist separately; set `ecs_backend_https_url` to the ALB HTTPS URL (no trailing slash).

### Outputs to wire after `terraform apply`

| Output | Use |
|--------|-----|
| `frontend_url` / `frontend_origin_https` | Browser URL (`https://xxxx.cloudfront.net`); set **`ALLOWED_ORIGINS`** on ECS (or GitHub var) to this |
| `api_gateway_invoke_url` | Set GitHub variable **`NEXT_PUBLIC_API_BASE_URL`** for CI builds |
| `frontend_s3_bucket` | GitHub variable **`FRONTEND_S3_BUCKET`** |
| `cloudfront_distribution_id` | GitHub variable **`CLOUDFRONT_DISTRIBUTION_ID`** |
| `openai_secret_arn` | ECS task `secrets` for `OPENAI_API_KEY` |

### ECS task definition

Store **OpenAI** in Secrets Manager (Terraform creates the secret from `openai_api_key`). Point the container at `openai_secret_arn`. The GitHub Actions OIDC role needs **`s3:PutObject`**, **`s3:DeleteObject`**, **`s3:ListBucket`** on the frontend bucket, and **`cloudfront:CreateInvalidation`** on the distribution (in addition to existing ECR/ECS permissions).

## Repository layout

- `backend/`: FastAPI app, chat engine, LLM and MCP services, tests
- `frontend/`: Next.js UI ([`frontend/lib/api.ts`](frontend/lib/api.ts) uses `NEXT_PUBLIC_API_BASE_URL`); **`output: 'export'`** writes to `frontend/out/`
- `infra/terraform/`: AWS modules (`ecr`, `secrets`, `http_api_gateway`, `frontend_cloudfront`) and root wiring
- `.github/workflows/`: CI and deployment automation

## Local setup

1. Copy environment values.

```bash
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
```

2. Start backend.

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. Start frontend.

```bash
cd frontend
npm install
npm run dev
```

4. Open the app and use the chat box (no sign-in). Optional: set **`DEFAULT_CUSTOMER_EMAIL`** in `.env` for MCP/LLM customer context.

## Terraform (`terraform.tfvars`)

Required: `project_name`, `environment`, `aws_region`, `ecs_backend_https_url`, `openai_api_key`.

Remove any leftover keys from older configs (**`github_repository`**, **`github_token`**, **`git_branch`**, **`jwt_secret`**) so Terraform does not warn about undeclared variables.

## GitHub Actions variables

Set **`NEXT_PUBLIC_API_BASE_URL`**, **`FRONTEND_S3_BUCKET`**, and **`CLOUDFRONT_DISTRIBUTION_ID`** from Terraform outputs so the **`deploy-frontend`** job runs (it is skipped until all three are non-empty). Optional **`ALLOWED_ORIGINS`** = `terraform output -raw frontend_origin_https` for CORS.

## Workflow model

- [`ci.yml`](.github/workflows/ci.yml): PRs and non-`main` pushes; backend tests + frontend static build.
- [`deploy.yml`](.github/workflows/deploy.yml): push to `main`; tests; **ECS** image deploy; **S3 sync + CloudFront invalidation** when the three frontend variables are set.

## Testing

```bash
cd backend
uv run pytest -q
```

## MVP status

- [x] FastAPI chat endpoint and health check
- [x] Next.js chat UI
- [x] MCP tool discovery and execution loop
- [x] GPT-4o-mini orchestration
- [x] AWS: API Gateway, ECS deploy, S3 + CloudFront frontend, Secrets Manager for OpenAI
