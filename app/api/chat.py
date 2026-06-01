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
    greeting = _greeting_response(request)
    if greeting is not None:
        return greeting

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

    if not _requires_semantic_query(request.question):
        return ChatResponse(
            answer=_metadata_only_fallback_answer(request),
            intent="metadata_or_general_question",
            semantic_model="",
            dax_query="",
            data=[],
            evidence=[
                EvidenceItem(source=item.get("source", ""), title=item.get("title"), snippet=item.get("content"))
                for item in evidence
            ],
        )

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


def _greeting_response(request: ChatRequest) -> ChatResponse | None:
    normalized = request.question.strip().lower()
    greetings = {
        "hello",
        "hi",
        "hey",
        "help",
        "who are you",
        "who are you?",
        "what can you do",
        "what can you do?",
        "مرحبا",
        "مرحباً",
        "هلا",
        "السلام عليكم",
        "اهلا",
        "أهلا",
        "من أنت",
        "من انت",
        "ماذا تستطيع أن تفعل",
        "ماذا تستطيع ان تفعل",
        "مساعدة",
    }

    if normalized not in greetings:
        return None

    return ChatResponse(
        answer=_help_answer(request),
        intent="greeting",
        semantic_model="",
        dax_query="",
        data=[],
        evidence=[],
    )


def _metadata_only_fallback_answer(request: ChatRequest) -> str:
    return _help_answer(request)


def _help_answer(request: ChatRequest) -> str:
    is_arabic = request.locale == "ar" or any("\u0600" <= char <= "\u06ff" for char in request.question)

    if is_arabic:
        return (
            "مرحباً، أنا مساعد تحليلي داخلي للإجابة عن أسئلة RDCCI من نماذج Microsoft Fabric الدلالية.\n\n"
            "يمكنني مساعدتك في أسئلة عن الاشتراكات، العضويات، التصاديق اليدوية، التصاديق الإلكترونية، والتصاريح.\n\n"
            "أمثلة يمكنك تجربتها:\n"
            "- كم عدد الاشتراكات الجديدة هذا الشهر؟\n"
            "- كم عدد العضويات المجددة هذا الربع؟\n"
            "- كم عدد التصاديق اليدوية هذا الشهر؟\n"
            "- كم عدد التصاديق الإلكترونية المعتمدة هذا الشهر؟\n"
            "- كم عدد التصاريح هذا الشهر؟\n\n"
            "للإجابات الرقمية، يتم جلب الأرقام من نماذج Fabric الدلالية وليس من قاعدة المعرفة."
        )

    return (
        "Hello, I am an internal analytical assistant for answering RDCCI questions from Microsoft Fabric semantic models.\n\n"
        "I can help with subscriptions, memberships, manual attestations, electronic attestations, and permits.\n\n"
        "Sample questions you can try:\n"
        "- How many new subscriptions are there this month?\n"
        "- How many memberships were renewed this quarter?\n"
        "- How many manual attestations this month?\n"
        "- How many approved electronic attestations this month?\n"
        "- How many permits this month?\n\n"
        "For numeric answers, values are retrieved from Fabric semantic models, not from the knowledge base."
    )


def _requires_semantic_query(question: str) -> bool:
    normalized = question.lower()
    numeric_terms = [
        "how many",
        "how much",
        "count",
        "number",
        "total",
        "sum",
        "average",
        "ratio",
        "percentage",
        "percent",
        "compare",
        "comparison",
        "trend",
        "ranking",
        "rank",
        "top",
        "kpi",
        "measure",
        "subscriptions",
        "memberships",
        "attestations",
        "permits",
        "كم",
        "عدد",
        "إجمالي",
        "اجمالي",
        "مجموع",
        "متوسط",
        "نسبة",
        "مقارنة",
        "قارن",
        "اتجاه",
        "ترتيب",
        "أعلى",
        "اعلى",
        "أكثر",
        "اكثر",
        "اشتراك",
        "اشتراكات",
        "عضوية",
        "عضويات",
        "تصديق",
        "تصاديق",
        "تصريح",
        "تصاريح",
    ]
    return any(term in normalized for term in numeric_terms)