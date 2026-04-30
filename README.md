# Meridian Electronics AI Assistant

A production-oriented MVP support assistant for Meridian Electronics.

It provides:

- Next.js chat frontend with login
- FastAPI backend with JWT-protected chat endpoint
- OpenAI GPT-4o-mini for response generation and tool-calling
- MCP integration for factual business tool lookups
- AWS deployment (App Runner backend + Amplify frontend)

## Architecture

```text
Browser (Customer)
        |
        v
Next.js Frontend (Amplify)
        |
        v
FastAPI Backend (App Runner)
   |                     |
   v                     v
OpenAI GPT-4o-mini   MCP Server (tools)
```

## Repository layout

- `backend/`: FastAPI app, auth, chat engine, LLM and MCP services, tests
- `frontend/`: Next.js chat UI and API client
- `infra/terraform/`: AWS infrastructure modules and environment wiring
- `.github/workflows/`: CI and deployment automation

## Local setup

1. Copy environment values.

```bash
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
```

1. Start backend.

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

1. Start frontend.

```bash
cd frontend
npm install
npm run dev
```

1. Sign in with synthetic demo credentials from `backend/app/services/demo_users.py`.
   Local quick reference can be stored in `testdata.md` (gitignored).

## Minimal secrets for GitHub Actions

Only three repository secrets are required:

- `AWS_ROLE_TO_ASSUME`: IAM role ARN for GitHub OIDC deployment access
- `OPENAI_API_KEY`: API key used by the backend runtime
- `JWT_SECRET`: secret for backend token signing

Optional repository variables (with defaults in workflow):

- `AWS_REGION` (default `eu-west-1`)
- `ECR_REPO_NAME` (default `meridian-electronics-ai-assistant-dev-backend`)
- `APP_RUNNER_SERVICE_NAME` (default `meridian-electronics-ai-assistant-dev-backend`)

## Workflow model

- `ci.yml`
  - Runs on pull requests and non-main branch pushes
  - Executes backend tests and frontend build
  - Does not require AWS credentials

- `deploy.yml`
  - Runs only on push to `main`
  - Re-runs tests/build as deployment gate
  - Uses OIDC to authenticate to AWS
  - Builds and pushes backend Docker image to ECR
  - Updates App Runner service to new image and environment values

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
- [x] Simplified CI/CD with minimal secret surface
