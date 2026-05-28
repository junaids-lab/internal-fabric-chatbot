from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    locale: str | None = Field(default=None, description="Optional response locale, for example ar or en.")
    filters: dict[str, Any] = Field(default_factory=dict)


class EvidenceItem(BaseModel):
    source: str
    title: str | None = None
    snippet: str | None = None


class ChatResponse(BaseModel):
    answer: str
    intent: str
    semantic_model: str
    dax_query: str
    data: list[dict[str, Any]]
    evidence: list[EvidenceItem] = Field(default_factory=list)

