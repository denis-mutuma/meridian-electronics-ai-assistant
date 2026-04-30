# Meridian Electronics AI Assistant

MVP chatbot for Meridian customer support using:
- FastAPI backend (Python + uv)
- Next.js frontend
- MCP tool integration (next slices)
- AWS deployment with Terraform

## Repository layout

- `backend/`: API, auth, chat engine, MCP adapter
- `frontend/`: chat UI
- `infra/terraform/`: AWS infrastructure as code

## Local setup

1. Copy environment values:

```bash
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
```

2. Run backend:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. Run frontend:

```bash
cd frontend
npm install
npm run dev
```

4. Use synthetic demo login credentials from `backend/app/services/demo_users.py`.
   Example: `demo.customer1@example.com` / `1111`.

## Team testing and secrets

- `JWT_SECRET` in `.env` must be a long random value (do not use `change_me`).
- For team local testing, use one shared **development-only** secret distributed out-of-band (vault/password manager/secure chat), and have each tester set it in their local `.env`.
- Do not commit `.env` files or post real secrets in PRs/issues/chat.
- Use different secrets for `local`, `staging`, and `production`.

Generate a local secret:

```bash
openssl rand -hex 32
```

Then set in `.env`:

```dotenv
JWT_SECRET=<paste-generated-value>
```

Quick local verification:

```bash
cd backend
uv run pytest -q
```

## Current MVP status

- [x] FastAPI scaffold, auth, and protected chat endpoint
- [x] Next.js chat UI with login
- [x] Terraform base stack scaffold
- [ ] MCP server tool discovery and execution loop
- [ ] GPT-4o-mini tool-calling orchestration
- [ ] AWS deploy pipeline and App Runner/Amplify wiring
