import re
from calendar import monthrange
from datetime import date
from typing import Any


MEASURE_BY_INTENT = {
    "new_subscriptions_count": "[New Subscription]",
    "renewed_memberships_count": "[Renewed Memberships]",
    "cancelled_subscriptions_count": "[Cancelled Subscriptions]",
    "manual_attestations_count": "[Manual Attestations]",
    "electronic_attestations_count": "[Approved Electronic Attestations]",
    "permits_count": "[Total Permits]",
}


def build_dax_for_intent(intent: str, filters: dict[str, Any], question: str = "") -> str:
    measure = MEASURE_BY_INTENT[intent]
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    inferred_start_date, inferred_end_date = _infer_date_range_from_question(question)

    if not start_date and inferred_start_date:
        start_date = inferred_start_date
    if not end_date and inferred_end_date:
        end_date = inferred_end_date

    dimension_filters = _dimension_filters_for_question(question)

    if start_date and end_date:
        date_filter = _date_filter_for_intent(intent, start_date, end_date)
        return _render_dax_query(measure, date_filter, dimension_filters)

    if dimension_filters:
        return _render_dax_query(measure, None, dimension_filters)

    return f"""
EVALUATE
ROW("value", {measure})
""".strip()


def _render_dax_query(measure: str, date_filter: str | None, dimension_filters: list[str]) -> str:
    filter_clauses = []
    if date_filter:
        filter_clauses.append(date_filter)
    filter_clauses.extend(dimension_filters)

    filter_text = ",\n        ".join(filter_clauses)
    return f"""
EVALUATE
ROW(
    "value",
    CALCULATE(
        {measure},
        {filter_text}
    )
)
""".strip()


def _infer_date_range_from_question(question: str) -> tuple[str | None, str | None]:
    normalized = question.lower()
    today = date.today()

    if any(term in normalized for term in ["current quarter", "this quarter", "الربع الحالي", "هذا الربع"]):
        quarter = (today.month - 1) // 3 + 1
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        start_date = date(today.year, start_month, 1)
        end_date = date(today.year, end_month, monthrange(today.year, end_month)[1])
        return start_date.isoformat(), end_date.isoformat()

    if any(term in normalized for term in ["current month", "this month", "الشهر الحالي", "هذا الشهر"]):
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, monthrange(today.year, today.month)[1])
        return start_date.isoformat(), end_date.isoformat()

    return None, None


def _dimension_filters_for_question(question: str) -> list[str]:
    normalized = question.lower()
    dimension_filters: list[str] = []

    if "legal form" in normalized or "owner type" in normalized:
        owner_type_id = _extract_owner_type_id(question)
        if owner_type_id is not None:
            dimension_filters.append(f"'Member'[OwnerTypeId] = {owner_type_id}")

    if "grade" in normalized or "degree" in normalized:
        grade_value = _extract_grade_value(question)
        if grade_value is not None:
            dimension_filters.append(f"'Member'[DegreeId] = {grade_value}")

    return dimension_filters


def _extract_owner_type_id(question: str) -> int | None:
    parenthetical = re.findall(r"\(([^)]+)\)", question)
    if parenthetical:
        raw = parenthetical[0].strip().lower()
        return _owner_type_alias_to_id(raw)

    match = re.search(r"legal form\s+([a-zA-Z\s-]+)", question, flags=re.IGNORECASE)
    if match:
        raw = match.group(1).strip().lower()
        return _owner_type_alias_to_id(raw)
    return None


def _owner_type_alias_to_id(raw: str) -> int | None:
    alias_map = {
        "sole proprietorship": 1,
        "sole proprietorships": 1,
        "company": 2,
        "companies": 2,
        "partnership": 3,
        "partnerships": 3,
        "individual": 4,
        "individuals": 4,
    }
    return alias_map.get(raw.lower())


def _extract_grade_value(question: str) -> int | None:
    grade_match = re.search(r"grade\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten)", question, flags=re.IGNORECASE)
    if grade_match:
        token = grade_match.group(1).lower()
        number_map = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }
        return number_map.get(token, int(token))

    degree_match = re.search(r"degree\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten)", question, flags=re.IGNORECASE)
    if degree_match:
        token = degree_match.group(1).lower()
        number_map = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }
        return number_map.get(token, int(token))

    return None

def _date_filter_for_intent(intent: str, start_date: str, end_date: str) -> str:
    table_column = {
        "new_subscriptions_count": "'VoucherHeader'[TransDate]",
        "renewed_memberships_count": "'VoucherHeader'[TransDate]",
        "cancelled_subscriptions_count": "'VoucherHeader'[TransDate]",
        "manual_attestations_count": "'SignCollHeader'[TransDate]",
        "electronic_attestations_count": "'ESFormContents'[ApprovalDate]",
        "permits_count": "'PermitCompet'[IssueDate]",
    }[intent]
    return f"{table_column} >= DATEVALUE(\"{start_date}\") && {table_column} <= DATEVALUE(\"{end_date}\")"
