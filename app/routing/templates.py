from typing import Any


MEASURE_BY_INTENT = {
    "new_subscriptions_count": "[New Subscription]",
    "renewed_memberships_count": "[Renewed Memberships]",
    "cancelled_subscriptions_count": "[Cancelled Subscriptions]",
    "manual_attestations_count": "[Manual Attestations]",
    "electronic_attestations_count": "[Approved Electronic Attestations]",
    "permits_count": "[Total Permits]",
}


def build_dax_for_intent(intent: str, filters: dict[str, Any]) -> str:
    measure = MEASURE_BY_INTENT[intent]
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    if start_date and end_date:
        date_filter = _date_filter_for_intent(intent, start_date, end_date)
        return f"""
EVALUATE
ROW(
    "value",
    CALCULATE(
        {measure},
        {date_filter}
    )
)
""".strip()

    return f"""
EVALUATE
ROW("value", {measure})
""".strip()


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
