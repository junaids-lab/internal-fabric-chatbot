# RDCCI Internal Fabric Chatbot

End-to-end starter for an Arabic/English analytical chatbot over existing Microsoft Fabric semantic models.

The intended runtime is:

1. User signs in with Entra ID.
2. The included browser frontend gets a delegated Power BI/Fabric access token with MSAL.
3. Backend sends the question to AI Foundry when `AZURE_AI_FOUNDRY_USE_AGENT=true`.
4. Foundry uses metadata context and can request the controlled `execute_semantic_query` tool.
5. Backend executes approved DAX against the relevant semantic model using the user's Power BI token.
6. Foundry interprets the rows and answers in the user's language, while numeric truth comes from Fabric.

This project intentionally does not generate arbitrary SQL or arbitrary DAX in production paths.

## Project Layout

```text
app/
  api/                 FastAPI routes
  static/              Simple chat UI served by the same Container App
  auth/                Bearer token handling
  foundry/             AI Foundry formatting/client integration
  powerbi/             Power BI Execute Queries client
  rag/                 Azure AI Search / Foundry IQ retrieval client
  routing/             Intent router and DAX templates
  schemas/             Request/response models
config/
  semantic_models.yaml Semantic model IDs, measures, date columns
  intents.yaml         Supported approved chatbot intents
scripts/
  extract_kb_from_workbook.py
  create_ai_search_index.py
  upload_kb_documents.py
  create_foundry_iq_knowledge_base.py
data/kb_docs/          Generated metadata/question documents
docs/                  Setup notes
```

## Quick Start

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/extract_kb_from_workbook.py \
  --workbook "/Users/mancunian_naz/Downloads/DDDM-DEV/Final Data Tables for Subscription Model-V15.xlsx" \
  --out data/kb_docs/rdcci-internal_kb.jsonl

python scripts/create_ai_search_index.py
python scripts/upload_kb_documents.py --file data/kb_docs/rdcci-internal_kb.jsonl

uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` to use the included chat interface.

To enable the Foundry orchestration path, set:

```text
AZURE_AI_FOUNDRY_USE_AGENT=true
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
AZURE_AI_FOUNDRY_AGENT_NAME=<agent-name>
```

If you only have a Foundry model endpoint such as `https://<account>.services.ai.azure.com/openai/v1`, leave `AZURE_AI_FOUNDRY_AGENT_NAME` blank and set `AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT`.

## User Delegated Querying

The backend expects a user-delegated Power BI token in the `Authorization` header:

```http
Authorization: Bearer <user-powerbi-access-token>
```

The frontend should acquire this token with MSAL for:

```text
https://analysis.windows.net/powerbi/api/.default
```

or the delegated scopes approved by your tenant, such as `Dataset.Read.All`.

The signed-in user must have the required Fabric/Power BI semantic model permissions, normally Read and Build.

## RAG / Foundry IQ

The knowledge base stores metadata only:

- table names
- column names
- semantic model names
- Arabic/English synonyms
- approved sample questions
- approved KPI intent hints
- source workbook lineage

Do not index transactional rows. The actual answer must come from the semantic model.

See [docs/foundry_iq_setup.md](docs/foundry_iq_setup.md).
