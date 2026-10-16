from typing import Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=3, max_length=4000, examples=["¿Cómo solicito acceso al VPN?"])
    thread_id: str = Field(min_length=1, max_length=100, examples=["usuario-123"])


class DocumentIngestRequest(BaseModel):
    document_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{1,99}$")
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=20, max_length=20_000)
    metadata: dict[str, str] = Field(default_factory=dict)


class DocumentIngestResponse(BaseModel):
    document_id: str
    status: Literal["created", "updated"]


class SearchKnowledgeInput(BaseModel):
    query: str = Field(min_length=3, max_length=4000)
    limit: int = Field(default=3, ge=1, le=10)


class Source(BaseModel):
    document_id: str
    title: str
    excerpt: str
    score: float = Field(ge=0)


class SearchKnowledgeOutput(BaseModel):
    sources: list[Source]


class AgentTrace(BaseModel):
    agent: Literal["supervisor", "researcher", "writer"]
    detail: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    trace: list[AgentTrace]
    thread_id: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    database: str
