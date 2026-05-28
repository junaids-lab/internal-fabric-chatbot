import argparse
import json
import os
from pathlib import Path
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
from openai import AzureOpenAI


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload RDCCI Internal KB JSONL docs to Azure AI Search.")
    parser.add_argument("--file", required=True)
    parser.add_argument("--batch-size", type=int, default=100)
    args = parser.parse_args()

    load_dotenv()
    endpoint = required("AZURE_SEARCH_ENDPOINT")
    api_key = required("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "rdcci-internal-chatbot-kb")

    docs = [json.loads(line) for line in Path(args.file).read_text(encoding="utf-8").splitlines() if line.strip()]
    embedder = EmbeddingClient()

    search_client = SearchClient(endpoint, index_name, AzureKeyCredential(api_key))
    uploaded = 0
    for batch in chunked(docs, args.batch_size):
        enriched = []
        for doc in batch:
            doc["content_vector"] = embedder.embed(f"{doc.get('title', '')}\n{doc.get('content', '')}")
            enriched.append(doc)
        result = search_client.upload_documents(enriched)
        uploaded += sum(1 for item in result if item.succeeded)
        print(f"Uploaded {uploaded}/{len(docs)} documents")

    print(f"Finished uploading {uploaded} documents to {index_name}")


class EmbeddingClient:
    def __init__(self) -> None:
        endpoint = required("AZURE_OPENAI_ENDPOINT")
        self.client = AzureOpenAI(
            azure_endpoint=normalize_azure_openai_endpoint(endpoint),
            api_key=required("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )
        self.deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.deployment, input=text)
        return response.data[0].embedding


def chunked(values: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def normalize_azure_openai_endpoint(endpoint: str) -> str:
    endpoint = endpoint.rstrip("/")
    if endpoint.endswith("/openai/v1"):
        return endpoint[: -len("/openai/v1")]
    return endpoint


if __name__ == "__main__":
    main()

