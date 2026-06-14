# Bloom — Backend (FastAPI + Microsoft Agent Framework + Foundry IQ)

Backend for **Bloom**, the women's-health-at-work agentic app for the Microsoft AI Agents Hackathon.

## Calendar protection — proactive but never automatic

Bloom can pre-empt schedule conflicts around medical events (chemo, IVF, surgery, mammograms) by blocking recovery slots on the user's Outlook calendar. The architecture enforces a two-step protocol:

1. **Propose** — `propose_calendar_blocks` is read-only. It computes the recommended slots, detects conflicts with existing meetings, and returns the plan with the neutral title and privacy level that would be applied.
2. **Confirm** — the agent shows the plan to the user in natural language: "Shall I block these slots?" Nothing is written yet.
3. **Execute** — only after explicit affirmative confirmation, the agent calls `execute_calendar_blocks` with the exact slots from the proposal. Events are created with neutral titles ("Unavailable"), private sensitivity, and tagged with a hidden "Bloom" category for later review.

All Graph calls run under the user's delegated permissions (`Calendars.ReadWrite` scope obtained via Teams SSO + On-Behalf-Of). The employer's tenant admin sees no Bloom service principal accessing calendars — every event is created by the user themselves.

See `docs/demo_calendar_flow.py` for the full conversational pattern.

## Stack

| Layer | Choice |
|---|---|
| Web framework | FastAPI (Python 3.12), gunicorn + uvicorn workers |
| Agent orchestration | Microsoft Agent Framework 1.0 (Python) — handoff pattern |
| Knowledge / grounding | Foundry IQ (3 knowledge bases) + Web IQ |
| Models | Azure OpenAI (gpt-4o) via the Foundry project |
| Identity | Microsoft Entra ID + Managed Identity (no API keys) |
| Data | Cosmos DB serverless (2 separate containers) |
| Hosting | Azure App Service (Linux Python) |
| Observability | Application Insights via OpenTelemetry |
| IaC | Bicep |

## Architecture in one screen

```
Teams tab → React SPA (App Service) → FastAPI (App Service)
                                          │
                                          ▼
                     Microsoft Agent Framework (handoff)
                                          │
            ┌──────────┬──────────┬──────────┬──────────┐
            ▼          ▼          ▼          ▼          ▼
        Orchestr.  Cycle    Conception  Menopause   Breast
            │          │          │          │          │
            └──────────┴──────────┴──────────┴──────────┘
                                 │
                                 ▼
                         Foundry IQ MCP server
                                 │
            ┌──────────┬──────────┬──────────┐
            ▼          ▼          ▼          ▼
         Medical   Legal-FR   Company    Web IQ
           KB        KB         KB     (live web)
                                 │
                                 ▼
                          Cosmos DB
                  (employee memory ‖ HR aggregates)
                       — separated by RBAC —
```

## Project layout

```
bloom-backend/
├── app/
│   ├── main.py                  FastAPI entry + lifespan
│   ├── config.py                Pydantic settings
│   ├── models/schemas.py        API contracts
│   ├── routers/
│   │   ├── chat.py              POST /api/v1/chat (employee)
│   │   ├── hr.py                GET  /api/v1/hr/insights, POST /api/v1/hr/policy
│   │   └── auth.py              Entra ID validation
│   ├── agents/
│   │   ├── orchestrator.py      Handoff coordinator
│   │   ├── modules.py           Cycle / Conception / Menopause / Breast
│   │   ├── policy.py            HR policy agent (separate Foundry project)
│   │   └── tools.py             AIFunctions for absence emails, reminders, etc.
│   └── services/
│       ├── foundry_iq.py        AzureAISearchContextProvider factories
│       └── memory.py            Cosmos DB longitudinal memory + HR aggregates
├── infra/main.bicep             Full Azure stack (deploy in one command)
├── requirements.txt
└── docs/
```

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Either set AUTH_DISABLED=true for quick local testing
# or run `az login` and let DefaultAzureCredential pick up your creds
export AUTH_DISABLED=true
export AZURE_AI_PROJECT_ENDPOINT="https://<your-project>.services.ai.azure.com/api/projects/default"
export FOUNDRY_IQ_SEARCH_ENDPOINT="https://<your-search>.search.windows.net"
export COSMOS_ENDPOINT="https://<your-cosmos>.documents.azure.com:443/"
export AZURE_TENANT_ID="<tenant>"
export AZURE_SUBSCRIPTION_ID="<sub>"

uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for Swagger.

## Provisioning the Azure infrastructure

```bash
az group create -n bloom-rg -l swedencentral
az deployment group create -g bloom-rg -f infra/main.bicep -p env=dev
```

This creates the Foundry project, Azure AI Search (Foundry IQ backend), Cosmos DB, two App Services (API + web), Application Insights, Key Vault, and the role assignments so the backend's managed identity can talk to everything without API keys.

## Setting up Foundry IQ knowledge bases

In the Microsoft Foundry portal (or via the Azure AI Search SDK):

1. **Medical KB** (`bloom-kb-medical`): index PDFs from WHO, NICE, ACOG, ESHRE into Blob Storage, then create a knowledge source pointing to that container.
2. **Legal KB** (`bloom-kb-legal-fr`): index Code du travail articles (L.1225-16 etc.), the Rist Report, the July 2025 IVF law.
3. **Company KB** (`bloom-kb-company`): per-tenant deployment — ingests the customer's own agreements.
4. **Web IQ**: enable as an additional knowledge source on the medical KB for live grounding of recent guideline updates.

Each KB is referenced by name in `app/services/foundry_iq.py` and consumed by agents through the `AzureAISearchContextProvider` in agentic mode.

## Deploying

CI/CD via GitHub Actions or `az webapp up`:

```bash
az webapp up -g bloom-rg -n bloom-dev-api --runtime "PYTHON:3.12" --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app"
```

## The confidentiality wall — how it's enforced

This is the key trust property of Bloom. It is enforced at four layers:

1. **Two Foundry projects.** Employee agents and HR agents run in separate Foundry projects with different RBAC scopes.
2. **Two Cosmos containers.** `employee-memory` and `hr-aggregates` have different partition keys and separate RBAC role assignments.
3. **K-anonymity in code.** `HRAggregateStore.fetch_insights` only returns metrics with `contributorCount >= 20`.
4. **Two App Service identities.** The employee API and HR API can run on the same App Service but use distinct route prefixes; in production they can be split into two App Services with distinct managed identities for even stricter isolation.

## Observability

Every Agent Framework call emits OpenTelemetry traces with the model, latency, tokens, and grounding sources used. They flow into Application Insights automatically once `APPLICATIONINSIGHTS_CONNECTION_STRING` is set.

## Evaluations

Use Foundry Evaluations + the Rubric Evaluator to score responses on:
- Groundedness (did every claim have a citation?)
- Safety (no diagnosis, no harmful recommendations)
- Tone (warm, plain language)

Run these against a curated test set before each deploy.
