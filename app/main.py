from contextlib import asynccontextmanager
import logging
import gradio as gr
from fastapi import FastAPI, HTTPException
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from opentelemetry import trace
from app.config import settings
from app.graph import build_graph
from app.observability import configure_observability
from app.rag import LocalRAG
from app.schemas import ChatRequest, ChatResponse, DocumentIngestRequest, DocumentIngestResponse, HealthResponse
from app.ui import build_ui

logging.basicConfig(level=logging.INFO, format='{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_data_dir()
    configure_observability(settings.phoenix_collector_endpoint)
    rag = LocalRAG(settings.database_path)
    await rag.initialize()
    app.state.rag = rag
    async with AsyncSqliteSaver.from_conn_string(settings.database_path) as checkpointer:
        app.state.graph = build_graph(rag, checkpointer)
        yield


app = FastAPI(title="Intelligence System", version="1.0.0", lifespan=lifespan, root_path=settings.app_root_path)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", database=settings.database_path)


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        with trace.get_tracer("intelligence-system.api").start_as_current_span("intelligence.chat") as span:
            span.set_attribute("session.id", request.thread_id)
            span.set_attribute("input.value", request.message)
            state = await app.state.graph.ainvoke(
                {"query": request.message, "messages": [("user", request.message)], "trace": []},
                {"configurable": {"thread_id": request.thread_id}},
            )
            span.set_attribute("output.value", state["answer"])
            span.set_attribute("rag.source_count", len(state["sources"]))
    except RuntimeError as error:
        logger.exception("LLM execution failed for thread_id=%s", request.thread_id)
        raise HTTPException(status_code=503, detail="El servicio de generación no está disponible. Intentá nuevamente.") from error
    return ChatResponse(answer=state["answer"], sources=state["sources"], trace=state["trace"], thread_id=request.thread_id)


@app.post("/v1/documents", response_model=DocumentIngestResponse, status_code=201)
async def ingest_document(request: DocumentIngestRequest) -> DocumentIngestResponse:
    status = await app.state.rag.ingest(request)
    return DocumentIngestResponse(document_id=request.document_id, status=status)


app = gr.mount_gradio_app(app, build_ui(chat, ingest_document), path="/", root_path=settings.app_root_path, show_api=False)
