from app.foundry.agent_client import FoundryAgentClient
from app.foundry.formatter import format_answer
from app.routing.router import RoutedQuery


def test_fallback_answer_turns_none_into_zero() -> None:
    client = FoundryAgentClient(powerbi_token="token")

    route = RoutedQuery(
        intent="new_subscriptions_count",
        semantic_model_name="dddm_sm_subscription",
        semantic_model_id="model",
        workspace_id="ws",
        dax_query="",
    )

    answer = client._fallback_agent_answer(
        route=route,
        rows=[{"value": None}],
        locale="en",
        question="Number of subscriptions by legal form (sole proprietorship) and Grade 1",
    )

    assert "the number of new subscriptions is 0." in answer.lower()
    assert "None" not in answer


def test_fallback_answer_uses_arabic_for_arabic_question() -> None:
    client = FoundryAgentClient(powerbi_token="token")
    route = RoutedQuery(
        intent="new_subscriptions_count",
        semantic_model_name="dddm_sm_subscription",
        semantic_model_id="model",
        workspace_id="ws",
        dax_query="",
    )

    answer = client._fallback_agent_answer(
        route=route,
        rows=[{"value": 5}],
        locale=None,
        question="كم عدد الاشتراكات هذا الشهر؟",
    )

    assert "عدد الاشتراكات الجديدة هو 5" in answer
    assert "The answer is" not in answer


def test_format_answer_uses_english_for_english_question() -> None:
    route = RoutedQuery(
        intent="new_subscriptions_count",
        semantic_model_name="subscription_model",
        semantic_model_id="model",
        workspace_id="ws",
        dax_query="",
    )

    answer = __import__("asyncio", fromlist=["run"]).run(
        format_answer(
            question="How many subscriptions are there?",
            route=route,
            result_rows=[{"value": 7}],
            locale=None,
            evidence=[],
        )
    )

    assert "the number of new subscriptions is 7." in answer.lower()
    assert "الإجابة:" not in answer
