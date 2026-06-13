from typing import Any

from app.routing.router import RoutedQuery


async def format_answer(
    question: str,
    route: RoutedQuery,
    result_rows: list[dict[str, Any]],
    locale: str | None,
    evidence: list[dict[str, Any]],
) -> str:
    # Phase 1 keeps formatting deterministic. Replace this function with a Foundry Agent call
    # once the agent and tool connection are provisioned.
    is_arabic = locale == "ar" or _looks_arabic(question)

    if not result_rows:
        return "لم يتم العثور على نتائج." if is_arabic else "No results were returned."

    first_row = result_rows[0]
    if len(first_row) == 1:
        value = next(iter(first_row.values()))
        if value is None:
            value = 0
        label = _friendly_label(route.intent, is_arabic)
        if is_arabic:
            return f"{label} هو {value:,}.\n\nالمصدر: {route.semantic_model_name}.\nالمؤشر: {route.intent}."
        return f"{label} is {value:,}.\n\nSource: {route.semantic_model_name}.\nIntent: {route.intent}."

    if is_arabic:
        return f"تم إرجاع {len(result_rows)} صفوف من {route.semantic_model_name} للمؤشر {route.intent}."
    return f"Returned {len(result_rows)} rows from {route.semantic_model_name} for intent {route.intent}."


def _looks_arabic(text: str) -> bool:
    return any("\u0600" <= char <= "\u06ff" for char in text)


def _friendly_label(intent: str, is_arabic: bool) -> str:
    labels = {
        "new_subscriptions_count": ("عدد الاشتراكات الجديدة", "the number of new subscriptions"),
        "renewed_memberships_count": ("عدد العضويات المجددة", "the number of renewed memberships"),
        "cancelled_subscriptions_count": ("عدد الاشتراكات الملغاة", "the number of cancelled subscriptions"),
        "manual_attestations_count": ("عدد التصاديق اليدوية", "the number of manual attestations"),
        "electronic_attestations_count": ("عدد التصاديق الإلكترونية", "the number of electronic attestations"),
        "permits_count": ("عدد التصاريح", "the number of permits"),
    }
    return labels.get(intent, ("النتيجة", "the result"))[0 if is_arabic else 1]

