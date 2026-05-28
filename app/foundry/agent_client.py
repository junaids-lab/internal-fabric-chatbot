import json
from typing import Any

import httpx
from azure.identity import DefaultAzureCredential

from app.core import settings
from app.powerbi.client import PowerBIClient
from app.rag.search_client import MetadataSearchClient
from app.routing.router import RoutedQuery, route_question


class FoundryAgentClient:
    def __init__(self, powerbi_token: str) -> None:
        self.powerbi_token = powerbi_token

    @property
    def is_configured(self) -> bool:
        return bool(
            settings.azure_ai_foundry_use_agent
            and settings.azure_ai_foundry_project_endpoint
            and (settings.azure_ai_foundry_agent_name or settings.azure_ai_foundry_model_deployment)
        )

    async def answer(self, question: str, locale: str | None, filters: dict[str, Any]) -> dict[str, Any]:
        evidence = await MetadataSearchClient().search(question)
        response = await self._create_response(
            input_items=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": self._build_user_prompt(question, locale, filters, evidence),
                        }
                    ],
                }
            ],
            include_tools=True,
        )

        route: RoutedQuery | None = None
        result_rows: list[dict[str, Any]] = []
        dax_query = ""
        semantic_query_executed = False

        for _ in range(3):
            function_calls = self._function_calls(response)
            if not function_calls:
                break

            tool_outputs = []
            for call in function_calls:
                if call["name"] != "execute_semantic_query":
                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": call["call_id"],
                            "output": json.dumps({"error": f"Unsupported tool: {call['name']}"}),
                        }
                    )
                    continue

                arguments = json.loads(call.get("arguments") or "{}")
                tool_result = await self._execute_semantic_query(
                    question=arguments.get("question") or question,
                    filters=arguments.get("filters") or filters,
                    evidence=evidence,
                )
                route = tool_result["route"]
                result_rows = tool_result["rows"]
                dax_query = route.dax_query
                semantic_query_executed = True
                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call["call_id"],
                        "output": json.dumps(
                            {
                                "semantic_model": route.semantic_model_name,
                                "intent": route.intent,
                                "rows": result_rows,
                                "dax_query": route.dax_query,
                            },
                            ensure_ascii=False,
                        ),
                    }
                )

            response = await self._create_response(
                input_items=tool_outputs,
                previous_response_id=response.get("id"),
                include_tools=True,
            )

        answer = self._output_text(response)
        if not semantic_query_executed and _requires_semantic_query(question):
            tool_result = await self._execute_semantic_query(question=question, filters=filters, evidence=evidence)
            route = tool_result["route"]
            result_rows = tool_result["rows"]
            dax_query = route.dax_query
            semantic_query_executed = True
            answer = self._fallback_agent_answer(route, result_rows, locale, question)

        if route is None:
            route = route_question(question, filters, evidence)

        return {
            "answer": answer or self._fallback_agent_answer(route, result_rows, locale, question),
            "route": route,
            "rows": result_rows,
            "dax_query": dax_query if semantic_query_executed else "",
            "evidence": evidence,
            "semantic_query_executed": semantic_query_executed,
        }

    async def _execute_semantic_query(
        self,
        question: str,
        filters: dict[str, Any],
        evidence: list[dict[str, Any]],
    ) -> dict[str, Any]:
        route = route_question(question, filters, evidence)
        rows = await PowerBIClient(self.powerbi_token).execute_dax(
            workspace_id=route.workspace_id,
            semantic_model_id=route.semantic_model_id,
            dax_query=route.dax_query,
        )
        return {"route": route, "rows": rows}

    async def _create_response(
        self,
        input_items: list[dict[str, Any]],
        previous_response_id: str | None = None,
        include_tools: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "input": input_items,
            "instructions": AGENT_INSTRUCTIONS,
        }

        if settings.azure_ai_foundry_agent_name:
            payload["agent_reference"] = {
                "type": "agent_reference",
                "name": settings.azure_ai_foundry_agent_name,
            }
        else:
            payload["model"] = settings.azure_ai_foundry_model_deployment

        if previous_response_id:
            payload["previous_response_id"] = previous_response_id
        if include_tools:
            payload["tools"] = [EXECUTE_SEMANTIC_QUERY_TOOL]

        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(await self._responses_url(), headers=await self._headers(), json=payload)

        if response.status_code >= 400:
            raise RuntimeError(f"Foundry agent call failed: {response.status_code} {response.text}")
        return response.json()

    async def _responses_url(self) -> str:
        endpoint = settings.azure_ai_foundry_project_endpoint.rstrip("/")
        if endpoint.endswith("/openai/v1"):
            return f"{endpoint}/responses"
        return f"{endpoint}/openai/v1/responses"

    async def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if settings.azure_ai_foundry_api_key:
            headers["api-key"] = settings.azure_ai_foundry_api_key
            return headers

        token = DefaultAzureCredential().get_token("https://ai.azure.com/.default")
        headers["Authorization"] = f"Bearer {token.token}"
        return headers

    def _build_user_prompt(
        self,
        question: str,
        locale: str | None,
        filters: dict[str, Any],
        evidence: list[dict[str, Any]],
    ) -> str:
        metadata = [
            {
                "title": item.get("title"),
                "content": item.get("content"),
                "semantic_model": item.get("semantic_model"),
                "doc_type": item.get("doc_type"),
            }
            for item in evidence[:5]
        ]
        detected_language = "Arabic" if _looks_arabic(question) else "English"
        requested_language = _requested_language(locale, detected_language)
        return json.dumps(
            {
                "question": question,
                "requested_locale": locale or "auto",
                "detected_input_language": detected_language,
                "final_answer_language": requested_language,
                "filters": filters,
                "metadata_context": metadata,
                "instruction": (
                    "Understand Arabic and English questions. Translate terms internally when needed to map "
                    "the question to the correct semantic model, measure, and backend tool call. Call "
                    "execute_semantic_query for any numeric, count, comparison, trend, ranking, or KPI question. "
                    "After tool results return, explain the answer in final_answer_language unless the user "
                    "explicitly asks for another language. Do not invent values."
                ),
            },
            ensure_ascii=False,
        )

    def _function_calls(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        calls = []
        for item in response.get("output", []):
            if item.get("type") == "function_call":
                calls.append(
                    {
                        "call_id": item.get("call_id"),
                        "name": item.get("name"),
                        "arguments": item.get("arguments"),
                    }
                )
        return calls

    def _output_text(self, response: dict[str, Any]) -> str:
        if response.get("output_text"):
            return str(response["output_text"])

        parts = []
        for item in response.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") in {"output_text", "text"}:
                        text = content.get("text")
                        if isinstance(text, dict):
                            parts.append(text.get("value", ""))
                        elif text:
                            parts.append(str(text))
        return "\n".join(part for part in parts if part).strip()

    def _fallback_agent_answer(
        self,
        route: RoutedQuery,
        rows: list[dict[str, Any]],
        locale: str | None,
        question: str,
    ) -> str:
        if not rows:
            return "لم يتم العثور على نتائج." if locale == "ar" or _looks_arabic(question) else "No results were returned."

        first_row = rows[0]
        value = next(iter(first_row.values())) if len(first_row) == 1 else rows
        if locale == "ar" or _looks_arabic(question):
            return f"الإجابة: {value}\n\nالمصدر: {route.semantic_model_name}\nالمؤشر: {route.intent}"
        return f"Answer: {value}\n\nSource: {route.semantic_model_name}\nIntent: {route.intent}"


def _looks_arabic(text: str) -> bool:
    return any("\u0600" <= char <= "\u06ff" for char in text)


def _requested_language(locale: str | None, detected_language: str) -> str:
    if locale == "ar":
        return "Arabic"
    if locale == "en":
        return "English"
    return detected_language


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


AGENT_INSTRUCTIONS = """
You are RDCCI Internal's Arabic/English analytical chatbot.
Users may ask in Arabic or English. Detect the input language unless requested_locale explicitly says ar or en.
Translate Arabic and English business terms internally when needed to understand intent, semantic model routing, measures, and dimensions.
Use metadata context to understand business terms, measure names, dimensions, and semantic model routing.
For numeric answers, counts, comparisons, ratios, rankings, trends, or KPI questions, call execute_semantic_query.
Never invent numbers. Never create arbitrary SQL or arbitrary DAX.
The backend tool returns the approved DAX query, semantic model, intent, and rows from Fabric.
After the tool returns data, interpret the result clearly in final_answer_language.
If the user asks in Arabic, answer in Arabic. If the user asks in English, answer in English. If requested_locale overrides this, follow requested_locale.
Mention the semantic model and, when useful, the intent/measure.
If a required date, branch, permit type, or attestation type is missing and the question cannot be answered safely, ask one concise clarification question.
""".strip()


EXECUTE_SEMANTIC_QUERY_TOOL = {
    "type": "function",
    "name": "execute_semantic_query",
    "description": "Execute an approved semantic-model KPI query through the backend. Use this for any numeric analytical question.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The user's business question, preserving Arabic or English wording.",
            },
            "filters": {
                "type": "object",
                "description": "Optional structured filters such as start_date, end_date, branch, city, degree, activity, permit_type, or status.",
                "additionalProperties": True,
            },
        },
        "required": ["question"],
    },
}
