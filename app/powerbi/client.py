from typing import Any

import httpx
from fastapi import HTTPException


class PowerBIClient:
    def __init__(self, delegated_token: str) -> None:
        self.delegated_token = delegated_token

    async def execute_dax(
        self,
        workspace_id: str,
        semantic_model_id: str,
        dax_query: str,
    ) -> list[dict[str, Any]]:
        if not workspace_id or not semantic_model_id:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Power BI workspace or semantic model ID is not configured.",
                    "workspace_id": workspace_id,
                    "semantic_model_id": semantic_model_id,
                },
            )

        url = (
            "https://api.powerbi.com/v1.0/myorg/groups/"
            f"{workspace_id}/datasets/{semantic_model_id}/executeQueries"
        )
        payload = {
            "queries": [{"query": dax_query}],
            "serializerSettings": {"includeNulls": True},
        }
        headers = {
            "Authorization": f"Bearer {self.delegated_token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=60, trust_env=False) as client:
                response = await client.post(url, headers=headers, json=payload)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Unable to reach Power BI service.",
                    "error": str(exc),
                    "url": url,
                },
            ) from exc

        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Power BI semantic model query failed.",
                    "status_code": response.status_code,
                    "body": response.text,
                },
            )

        body = response.json()
        try:
            return body["results"][0]["tables"][0]["rows"]
        except (KeyError, IndexError, TypeError) as exc:
            raise HTTPException(
                status_code=502,
                detail={"message": "Unexpected Power BI response.", "body": body},
            ) from exc

