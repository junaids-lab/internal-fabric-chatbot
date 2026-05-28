from typing import Any

import httpx

from app.core import settings


class MetadataSearchClient:
    async def search(self, question: str, top: int = 5) -> list[dict[str, Any]]:
        if not settings.azure_search_endpoint or not settings.azure_search_api_key:
            return []

        endpoint = settings.azure_search_endpoint.rstrip("/")
        url = f"{endpoint}/indexes/{settings.azure_search_index_name}/docs/search?api-version=2024-07-01"
        payload = {
            "search": question,
            "queryType": "semantic",
            "semanticConfiguration": "default",
            "top": top,
            "select": "id,title,content,source,semantic_model,doc_type",
        }
        headers = {"api-key": settings.azure_search_api_key, "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code >= 400:
            return []

        return response.json().get("value", [])

