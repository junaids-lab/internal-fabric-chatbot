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
    if not result_rows:
        return "لم يتم العثور على نتائج." if locale == "ar" else "No results were returned."

    first_row = result_rows[0]
    if len(first_row) == 1:
        value = next(iter(first_row.values()))
        if locale == "ar" or _looks_arabic(question):
            return f"الإجابة: {value}\n\nالمصدر: {route.semantic_model_name}\nالمؤشر: {route.intent}"
        return f"Answer: {value}\n\nSource: {route.semantic_model_name}\nIntent: {route.intent}"

    if locale == "ar" or _looks_arabic(question):
        return f"تم إرجاع {len(result_rows)} صفوف من {route.semantic_model_name} للمؤشر {route.intent}."
    return f"Returned {len(result_rows)} rows from {route.semantic_model_name} for intent {route.intent}."


def _looks_arabic(text: str) -> bool:
    return any("\u0600" <= char <= "\u06ff" for char in text)

