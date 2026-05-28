from dataclasses import dataclass
from typing import Any

from app.core import settings
from app.routing.templates import build_dax_for_intent


@dataclass(frozen=True)
class RoutedQuery:
    intent: str
    semantic_model_name: str
    semantic_model_id: str
    workspace_id: str
    dax_query: str


def route_question(question: str, filters: dict[str, Any], evidence: list[dict[str, Any]]) -> RoutedQuery:
    normalized = question.lower()
    intent = _classify_intent(normalized, evidence)
    model_name = _semantic_model_for_intent(intent)
    model_id = _semantic_model_id(model_name)
    dax_query = build_dax_for_intent(intent, filters)

    return RoutedQuery(
        intent=intent,
        semantic_model_name=model_name,
        semantic_model_id=model_id,
        workspace_id=settings.fabric_workspace_id,
        dax_query=dax_query,
    )


def _classify_intent(question: str, evidence: list[dict[str, Any]]) -> str:
    if any(term in question for term in ["renew", "مجدد", "مجدده", "تجديد"]):
        return "renewed_memberships_count"
    if any(term in question for term in ["cancel", "إلغاء", "الغاء", "ملغ"]):
        return "cancelled_subscriptions_count"
    if any(term in question for term in ["manual", "يدوي", "يدوية"]):
        return "manual_attestations_count"
    if any(term in question for term in ["electronic", "الكتروني", "إلكتروني", "الإلكترونية"]):
        return "electronic_attestations_count"
    if any(term in question for term in ["permit", "تصريح", "تصاريح"]):
        return "permits_count"
    return "new_subscriptions_count"


def _semantic_model_for_intent(intent: str) -> str:
    if intent in {"new_subscriptions_count", "renewed_memberships_count", "cancelled_subscriptions_count"}:
        return "dddm_sm_subscription"
    if intent == "manual_attestations_count":
        return "dddm_sm_manualstamp"
    if intent == "electronic_attestations_count":
        return "dddm_sm_electronicstamp"
    if intent == "permits_count":
        return "dddm_sm_permit"
    return "dddm_sm_subscription"


def _semantic_model_id(model_name: str) -> str:
    ids = {
        "dddm_sm_subscription": settings.subscription_semantic_model_id,
        "dddm_sm_manualstamp": settings.manual_stamp_semantic_model_id,
        "dddm_sm_electronicstamp": settings.electronic_stamp_semantic_model_id,
        "dddm_sm_permit": settings.permit_semantic_model_id,
    }
    return ids[model_name]
