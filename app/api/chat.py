from fastapi import APIRouter, Depends, HTTPException

from app.auth.delegated_token import get_delegated_powerbi_token
from app.foundry.agent_client import FoundryAgentClient
from app.foundry.formatter import format_answer
from app.powerbi.client import PowerBIClient
from app.rag.search_client import MetadataSearchClient
from app.routing.router import route_question
from app.schemas.chat import ChatRequest, ChatResponse, EvidenceItem

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    powerbi_token: str = Depends(get_delegated_powerbi_token),
) -> ChatResponse:
    agent_client = FoundryAgentClient(powerbi_token)
    if agent_client.is_configured:
        try:
            agent_result = await agent_client.answer(request.question, request.locale, request.filters)
            route = agent_result["route"]
            evidence = agent_result["evidence"]
            return ChatResponse(
                answer=agent_result["answer"],
                intent=route.intent,
                semantic_model=route.semantic_model_name,
                dax_query=agent_result["dax_query"],
                data=agent_result["rows"],
                evidence=[
                    EvidenceItem(source=item.get("source", ""), title=item.get("title"), snippet=item.get("content"))
                    for item in evidence
                ],
            )
        except HTTPException:
            raise
        except Exception:
            return await _deterministic_chat_response(request, powerbi_token)

    return await _deterministic_chat_response(request, powerbi_token)


async def _deterministic_chat_response(request: ChatRequest, powerbi_token: str) -> ChatResponse:
    rag_client = MetadataSearchClient()
    evidence = await rag_client.search(request.question)

    route = route_question(request.question, request.filters, evidence)
    result_rows = await PowerBIClient(powerbi_token).execute_dax(
        workspace_id=route.workspace_id,
        semantic_model_id=route.semantic_model_id,
        dax_query=route.dax_query,
    )

    answer = await format_answer(
        question=request.question,
        route=route,
        result_rows=result_rows,
        locale=request.locale,
        evidence=evidence,
    )

    return ChatResponse(
        answer=answer,
        intent=route.intent,
        semantic_model=route.semantic_model_name,
        dax_query=route.dax_query,
        data=result_rows,
        evidence=[
            EvidenceItem(source=item.get("source", ""), title=item.get("title"), snippet=item.get("content"))
            for item in evidence
        ],
    )
