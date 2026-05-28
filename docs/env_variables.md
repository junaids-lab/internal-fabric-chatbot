# Environment Variables

Required for local chatbot runtime:

```text
FABRIC_WORKSPACE_ID=7eb67fcb-de1d-4b4f-94dd-09d1c2071ff8
SUBSCRIPTION_SEMANTIC_MODEL_ID=67835d94-14e8-4831-bf06-3edc9f9d2240
MANUAL_STAMP_SEMANTIC_MODEL_ID=5a1ddc68-3b26-41fa-ab2f-a3729bad3b88
ELECTRONIC_STAMP_SEMANTIC_MODEL_ID=a8b38be1-f917-492b-9bfd-c93bb5791259
PERMIT_SEMANTIC_MODEL_ID=c3bd890f-ea15-4c0d-a28d-2ad89435fe34
```

The provided Fabric URL also includes the Entra tenant ID:

```text
ENTRA_TENANT_ID=0a0efc93-807d-479a-818e-db0372a19c6a
ENTRA_FRONTEND_CLIENT_ID=5e8e0c75-afe1-4510-94bc-77dc5984eaf7
POWERBI_DELEGATED_SCOPES=https://analysis.windows.net/powerbi/api/Dataset.Read.All
```

`ENTRA_FRONTEND_CLIENT_ID` is the public SPA app registration client ID used by the browser frontend for MSAL sign-in.

Required for RAG ingestion:

```text
AZURE_SEARCH_ENDPOINT=https://swc-rdcci-dddm-ai-search-dev.search.windows.net
AZURE_SEARCH_API_KEY
AZURE_SEARCH_INDEX_NAME
AZURE_OPENAI_ENDPOINT=https://swc-rdcci-ai-foundry-dddm-dev.openai.azure.com/openai/v1
AZURE_OPENAI_API_KEY
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
EMBEDDING_DIMENSIONS=3072
```

Keep `AZURE_SEARCH_API_KEY` and `AZURE_OPENAI_API_KEY` only in local `.env` or deployment secrets. Do not commit keys to documentation or `.env.example`.

Required for Foundry IQ knowledge base creation:

```text
AZURE_SEARCH_KNOWLEDGE_BASE_NAME
AZURE_SEARCH_API_VERSION
AZURE_SEARCH_KNOWLEDGE_BASE_MODEL_ENDPOINT=https://swc-rdcci-ai-foundry-dddm-dev.services.ai.azure.com/openai/v1
AZURE_SEARCH_KNOWLEDGE_BASE_MODEL_DEPLOYMENT=gpt-5.4
AZURE_SEARCH_KNOWLEDGE_BASE_MODEL_NAME=gpt-5.4
AZURE_SEARCH_KNOWLEDGE_BASE_MODEL_API_KEY
```

Optional for later Foundry answer formatting:

```text
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://swc-rdcci-ai-foundry-dddm-dev.services.ai.azure.com/api/projects/ai-dddm-internal
AZURE_AI_FOUNDRY_AGENT_NAME=rdcci-internal-fabric-chatbot-agent
AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT=gpt-5.4
AZURE_AI_FOUNDRY_API_KEY
AZURE_AI_FOUNDRY_USE_AGENT=true
AZURE_CLIENT_ID=92355922-19e6-4ee1-8a93-670a46adf96e
```

`AZURE_CLIENT_ID` selects the user-assigned managed identity `swc-rdcci-dddm-uami-dev` for Foundry authentication when `AZURE_AI_FOUNDRY_API_KEY` is empty.

The current Foundry agent is referenced by `AZURE_AI_FOUNDRY_AGENT_NAME`. No separate agent ID is required.

Optional for local/deployed CORS control:

```text
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```
