# Runbook

## 1. Prepare Semantic Models

- Workspace ID from Fabric URL: `7eb67fcb-de1d-4b4f-94dd-09d1c2071ff8`
- Tenant ID from Fabric URL: `0a0efc93-807d-479a-818e-db0372a19c6a`
- Confirm model IDs and workspace ID.
- Confirm users have Read and Build permission.
- Confirm RLS behavior if applicable.
- Create or rename measures listed in `docs/measures_to_create.md`.

## 2. Build Metadata Knowledge Base

```bash
python scripts/extract_kb_from_workbook.py \
  --workbook "/Users/mancunian_naz/Downloads/DDDM-DEV/Final Data Tables for Subscription Model-V15.xlsx" \
  --out data/kb_docs/rdcci-internal_kb.jsonl

python scripts/create_ai_search_index.py
python scripts/upload_kb_documents.py --file data/kb_docs/rdcci-internal_kb.jsonl
python scripts/create_foundry_iq_knowledge_base.py
```

## 3. Enable Foundry Orchestration

For a named Foundry Agent:

```text
AZURE_AI_FOUNDRY_USE_AGENT=true
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
AZURE_AI_FOUNDRY_AGENT_NAME=<agent-name>
```

For direct Foundry model orchestration without a named agent:

```text
AZURE_AI_FOUNDRY_USE_AGENT=true
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/openai/v1
AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT=<deployment-name>
```

Use either `AZURE_AI_FOUNDRY_API_KEY` locally or grant the backend managed identity access to Foundry and leave the key blank.

## 4. Run Local API

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000
```

Sign in and ask a question from the browser UI.

## 5. Test Chat By Curl

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $POWERBI_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "كم عدد الإشتراكات الجديدة هذا الشهر؟",
    "locale": "ar",
    "filters": {
      "start_date": "2026-05-01",
      "end_date": "2026-05-24"
    }
  }'
```

## 5. Deploy

- Build Docker image.
- Push to ACR.
- Deploy Container App.
- Add environment variables as secrets.
- Restrict CORS to the frontend URL.
- Enable Application Insights.
