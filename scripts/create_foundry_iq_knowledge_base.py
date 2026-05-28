import json
import os

import httpx
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    endpoint = required("AZURE_SEARCH_ENDPOINT").rstrip("/")
    api_key = required("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "rdcci-internal-chatbot-kb")
    knowledge_base_name = os.getenv("AZURE_SEARCH_KNOWLEDGE_BASE_NAME", "rdcci-internal-fabric-kb")
    knowledge_source_name = os.getenv("AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME", f"{index_name}-source")
    api_version = os.getenv("AZURE_SEARCH_API_VERSION", "2025-11-01-preview")
    headers = {"api-key": api_key, "Content-Type": "application/json", "Prefer": "return=representation"}

    knowledge_source_payload = {
        "name": knowledge_source_name,
        "description": "RDCCI Internal Fabric chatbot metadata from the Azure AI Search index.",
        "kind": "searchIndex",
        "searchIndexParameters": {
            "searchIndexName": index_name,
            "semanticConfigurationName": "default",
            "searchFields": [
                {"name": "title"},
                {"name": "content"},
                {"name": "table_name"},
                {"name": "column_name"},
            ],
            "sourceDataFields": [
                {"name": "title"},
                {"name": "content"},
                {"name": "source"},
                {"name": "doc_type"},
                {"name": "semantic_model"},
                {"name": "table_name"},
                {"name": "column_name"},
                {"name": "language"},
            ],
        },
    }

    knowledge_source_url = f"{endpoint}/knowledgesources('{knowledge_source_name}')?api-version={api_version}"
    knowledge_source_response = httpx.put(
        knowledge_source_url,
        headers=headers,
        json=knowledge_source_payload,
        timeout=60,
    )
    if knowledge_source_response.status_code >= 400:
        raise RuntimeError(
            "Failed to create knowledge source: "
            f"{knowledge_source_response.status_code}\n{knowledge_source_response.text}"
        )

    # Foundry IQ knowledge bases are Azure AI Search top-level objects.
    # Keep this payload small and metadata-focused; the search index remains the knowledge source.
    payload = {
        "name": knowledge_base_name,
        "description": "RDCCI Internal Fabric chatbot knowledge base over semantic model metadata, table columns, synonyms, and approved sample questions.",
        "knowledgeSources": [
            {
                "name": knowledge_source_name,
            }
        ],
        "outputMode": "extractiveData",
        "retrievalReasoningEffort": {"kind": "low"},
    }

    model_payload = knowledge_base_model_payload()
    if model_payload:
        payload["models"] = [model_payload]
        payload["retrievalInstructions"] = (
            "Use this knowledge base only to understand business terminology, semantic model mapping, "
            "table/column lineage, approved question examples, and KPI routing hints. "
            "Do not answer numeric business questions directly from this index; numeric answers must come from Fabric semantic models."
        )
        payload["answerInstructions"] = (
            "Cite the source metadata when explaining routing or definitions. "
            "For actual KPI values, tell the application to query the semantic model."
        )

    url = f"{endpoint}/knowledgebases('{knowledge_base_name}')?api-version={api_version}"
    response = httpx.put(url, headers=headers, json=payload, timeout=60)
    if response.status_code >= 400:
        raise RuntimeError(f"Failed to create knowledge base: {response.status_code}\n{response.text}")

    print(f"Created or updated knowledge source: {knowledge_source_name}")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def knowledge_base_model_payload() -> dict[str, object] | None:
    deployment = os.getenv("AZURE_SEARCH_KNOWLEDGE_BASE_MODEL_DEPLOYMENT")
    model_name = os.getenv("AZURE_SEARCH_KNOWLEDGE_BASE_MODEL_NAME")
    resource_uri = os.getenv("AZURE_SEARCH_KNOWLEDGE_BASE_MODEL_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_KNOWLEDGE_BASE_MODEL_API_KEY")

    if not deployment or not model_name or not resource_uri:
        return None

    azure_openai_parameters: dict[str, object] = {
        "resourceUri": normalize_model_endpoint(resource_uri),
        "deploymentId": deployment,
        "modelName": model_name,
    }
    if api_key:
        azure_openai_parameters["apiKey"] = api_key

    return {
        "kind": "azureOpenAI",
        "azureOpenAIParameters": azure_openai_parameters,
    }


def normalize_model_endpoint(endpoint: str) -> str:
    endpoint = endpoint.rstrip("/")
    if endpoint.endswith("/openai/v1"):
        return endpoint[: -len("/openai/v1")]
    return endpoint


if __name__ == "__main__":
    main()

