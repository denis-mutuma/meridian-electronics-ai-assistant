# Meridian Electronics AI Assistant

A production-oriented MVP support assistant for Meridian Electronics.

It provides:

- Next.js chat frontend with login
- FastAPI backend with JWT-protected chat endpoint
- OpenAI GPT-4o-mini for response generation and tool-calling
- MCP integration for factual business tool lookups
- AWS deployment: **Amplify** (frontend) → **API Gateway HTTP API** → **Application Load Balancer** → **ECS Fargate** (backend)

## Architecture

```text
Browser (Customer)
        |
        v
Next.js Frontend (Amplify)
        |
        v
Amazon API Gateway (HTTP API, throttling on $default stage)
        |
        v
Application Load Balancer (HTTPS) ──► ECS Fargate (FastAPI)
   |                                          |
   v                                          v
(optional WAF on API GW stage)          OpenAI + MCP server
```

Terraform in this repository provisions **ECR**, **Secrets Manager** secrets (OpenAI + JWT), **HTTP API Gateway** (proxy to your ALB), and **Amplify**. The **ECS cluster, service, task definition, and ALB** are expected to exist already (created in the console or separate IaC); set `ecs_backend_https_url` to the ALB’s public HTTPS URL (no trailing slash).

### Terraform outputs to wire manually

After `terraform apply`, copy values into GitHub and ECS as needed:

| Output | Use |
|--------|-----|
| `api_gateway_invoke_url` | Already injected into Amplify as `NEXT_PUBLIC_API_BASE_URL` |
| `amplify_origin_https` | Set GitHub Actions variable `ALLOWED_ORIGINS` to this value (comma-separate if you add custom domains) so the ECS task CORS matches the real UI origin |
| `openai_secret_arn` / `jwt_secret_arn` | ECS container `secrets` entries (see below) |

### ECS task definition: Secrets Manager

Store sensitive values in Secrets Manager (Terraform creates two secrets from `openai_api_key` and `jwt_secret` in `terraform.tfvars`). Point the **backend** container at them so deploy workflows never need the raw OpenAI key:

```json
"secrets": [
  {
    "name": "OPENAI_API_KEY",
    "valueFrom": "<terraform output openai_secret_arn>"
  },
  {
    "name": "JWT_SECRET",
    "valueFrom": "<terraform output jwt_secret_arn>"
  }
]
```

The **ECS task execution role** must allow `secretsmanager:GetSecretValue` on those ARNs (and KMS decrypt if the secrets use a CMK).

Other runtime env vars (`MCP_SERVER_URL`, etc.) stay in the task `environment` block as you maintain them today.

## Repository layout

- `backend/`: FastAPI app, auth, chat engine, LLM and MCP services, tests
- `frontend/`: Next.js chat UI and API client ([`frontend/lib/api.ts`](frontend/lib/api.ts) uses `NEXT_PUBLIC_API_BASE_URL`)
- `infra/terraform/`: AWS modules (`ecr`, `secrets`, `http_api_gateway`, `amplify`) and root wiring
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

4. Sign in with synthetic demo credentials from `backend/app/services/demo_users.py`.
   Local quick reference can be stored in `testdata.md` (gitignored).

## Secrets and variables

**Terraform (`terraform.tfvars`, not committed):** `openai_api_key`, `jwt_secret`, `github_token`, and `ecs_backend_https_url` (your ALB HTTPS URL).

**GitHub Actions:** No repository secret is strictly required for deploy if the ECS task loads OpenAI/JWT from Secrets Manager. Optional repository **variable** `ALLOWED_ORIGINS` should match `amplify_origin_https` (and any extra origins) so CORS is locked to your UI.

Optional repository variables (defaults in [`deploy.yml`](.github/workflows/deploy.yml)):

- `AWS_ROLE_ARN`, `AWS_REGION`, `ECR_REPO_NAME`, `ECS_CLUSTER_NAME`, `ECS_SERVICE_NAME`, `ECS_TASK_FAMILY`, `ECS_CONTAINER_NAME`

## Workflow model

- [`ci.yml`](.github/workflows/ci.yml): pull requests and pushes to branches other than `main`; backend tests and frontend build; no AWS credentials.
- [`deploy.yml`](.github/workflows/deploy.yml): push to `main` only; gates on tests/build; OIDC to AWS; ECR image build/push; new ECS task revision **image-only** (preserves secrets and the rest of the task definition); optional `ALLOWED_ORIGINS` variable merge; Amplify rebuilds via GitHub webhook.

## Observability (recommended follow-ups)

- Enable API Gateway access logging to CloudWatch Logs; add alarms on `4XXError`, `5XXError`, and integration latency.
- Confirm the ALB target group health check uses `GET /health` (see [`backend/app/routes/health.py`](backend/app/routes/health.py)).
- Associate **AWS WAF** with the API Gateway stage if you need IP or bot filtering.
- Add an **ACM custom domain** on API Gateway if you want a stable hostname instead of `*.execute-api.*.amazonaws.com`.

## Testing

```bash
cd backend
uv run pytest -q
```

## MVP status

- [x] FastAPI scaffold, auth, and protected chat endpoint
- [x] Next.js chat UI with login
- [x] MCP tool discovery and execution loop
- [x] GPT-4o-mini prompt and tool-calling orchestration
- [x] AWS deploy pipeline with push-to-main deploy
- [x] API Gateway in front of ECS ALB; Amplify uses gateway URL
- [x] Simplified CI/CD with minimal secret surface (Secrets Manager for runtime secrets)
