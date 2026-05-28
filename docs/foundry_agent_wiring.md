# Foundry Agent Wiring

The project now supports an active Foundry Agent/Responses path.

Set:

```text
AZURE_AI_FOUNDRY_USE_AGENT=true
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://swc-rdcci-ai-foundry-dddm-dev.services.ai.azure.com/api/projects/ai-dddm-internal
AZURE_AI_FOUNDRY_AGENT_NAME=<agent-name>
AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT=gpt-5.4
```

The backend appends `/openai/v1/responses` when the endpoint is provided as a Foundry project endpoint.

If you do not have a named agent yet, leave `AZURE_AI_FOUNDRY_AGENT_NAME` blank and set `AZURE_AI_FOUNDRY_MODEL_DEPLOYMENT`. The backend will call the Foundry model directly through the same Responses API. The preferred production path is the named agent.

The current Foundry experience uses the agent name as the reference. No separate agent ID is required for this project.

## `execute_semantic_query` Tool

Do not add `execute_semantic_query` manually in the Foundry UI for the normal chatbot runtime.

The backend provides `execute_semantic_query` dynamically when it calls the Foundry Responses API. The function schema is defined in `app/foundry/agent_client.py`, and the Python backend executes the tool call. This is required because the backend has the user's delegated Power BI token and owns approved DAX generation.

The Foundry Playground can test language and knowledge-base behavior, but it cannot complete the real Power BI KPI path unless a separate OpenAPI action is exposed and secured. That is not recommended for phase 1 because semantic model execution must remain user-delegated.

## Managed Identity

The backend can call Foundry with managed identity instead of an API key.

For the user-assigned managed identity `swc-rdcci-dddm-uami-dev`:

- Attach the identity to the Container App.
- Set `AZURE_AI_FOUNDRY_API_KEY` empty.
- Set `AZURE_CLIENT_ID` to the managed identity client ID if more than one identity is available.
- Grant data-plane access on the Azure AI Foundry / Azure AI Services resource. If token calls fail with `401` or `403`, add `Cognitive Services OpenAI User` or the equivalent data-plane role in addition to project/developer roles.

Current known roles on the identity:

- `Azure AI Developer`
- `AcrPull`
- `Cognitive Services Contributor`

`AcrPull` is only for pulling the container image. `Cognitive Services Contributor` is useful for management operations, but model inference may still require a data-plane role such as `Cognitive Services OpenAI User`.

Recommended production split:

- Foundry IQ: knowledge over metadata, synonyms, and sample questions.
- Container App: controlled business action API.
- Fabric semantic models: source of numeric truth.

## Agent Instructions

```text
You are RDCCI Internal's Arabic/English analytical assistant.
Detect whether the user asked in Arabic or English, unless the request explicitly asks for a specific answer language.
Translate Arabic/English business terms internally when needed for routing.
Use Foundry IQ only for metadata, terminology, table mapping, and routing support.
Never answer business KPI numbers from the knowledge base.
For counts, comparisons, ratios, rankings, or trends, call the application semantic query endpoint.
After the backend tool returns Fabric rows, explain the result in the user's input language.
If required parameters are missing, ask one concise clarification question.
For Arabic questions, answer in Arabic. For English questions, answer in English.
Always include the semantic model name used for numeric answers.
```

## Tool Pattern

The backend owns the critical numeric path:

```text
Frontend -> Container App /chat -> Foundry Agent -> execute_semantic_query tool -> approved DAX -> Fabric semantic model -> Foundry final answer
```

The agent receives one tool definition:

```text
execute_semantic_query(question, filters)
```

The agent decides when the function is needed. The Python backend executes the function, not the model. This keeps DAX generation, model IDs, and user-delegated Power BI calls under backend control.

Input to `/chat`:

```json
{
  "question": "كم عدد الاشتراكات الجديدة هذا الشهر؟",
  "locale": "ar",
  "filters": {
    "start_date": "2026-05-01",
    "end_date": "2026-05-24"
  }
}
```

Security note: semantic model execution remains user-delegated. The browser sends the user's Power BI token to the backend. The backend calls Foundry with its own identity/API key, but calls Power BI with the user's token.

## Failure And Safety Fallbacks

Recommended behavior:

1. If the Foundry call fails, fall back to the deterministic backend path: metadata search, approved intent routing, approved DAX execution, and deterministic formatting.
2. If Foundry responds without calling `execute_semantic_query` for a numeric/KPI question, the backend forces `execute_semantic_query` itself and returns deterministic formatting.
3. If the question is non-numeric and informational, the agent may answer from metadata context without calling the semantic query tool.

This keeps Fabric semantic models as the only source of numeric truth while still allowing the agent to handle language, terminology, and explanation.
