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
