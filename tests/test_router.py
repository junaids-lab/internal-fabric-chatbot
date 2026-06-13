from app.routing.router import route_question


def test_routes_arabic_new_subscription() -> None:
    route = route_question("كم عدد الاشتراكات الجديدة هذا الشهر؟", {}, [])
    assert route.intent == "new_subscriptions_count"
    assert route.semantic_model_name == "dddm_sm_subscription"


def test_routes_manual_stamp() -> None:
    route = route_question("كم عدد التصاديق اليدوية في الفرع؟", {}, [])
    assert route.intent == "manual_attestations_count"
    assert route.semantic_model_name == "dddm_sm_manualstamp"


def test_routes_permits() -> None:
    route = route_question("How many permits this month?", {}, [])
    assert route.intent == "permits_count"
    assert route.semantic_model_name == "dddm_sm_permit"


def test_current_quarter_question_adds_date_filter() -> None:
    route = route_question("كم عدد التصاديق الإلكترونية خلال الربع الحالي؟", {}, [])

    assert route.intent == "electronic_attestations_count"
    assert "ApprovalDate" in route.dax_query
    assert "DATEVALUE(" in route.dax_query


def test_breakdown_question_uses_filtered_subscription_count() -> None:
    route = route_question("Number of subscriptions by legal form (sole proprietorship) and Grade 1", {}, [])

    assert route.intent == "new_subscriptions_count"
    assert "'Member'[OwnerTypeId] = 1" in route.dax_query
    assert "'Member'[DegreeId] = 1" in route.dax_query
    assert "'Member'[OwnerType]" not in route.dax_query
