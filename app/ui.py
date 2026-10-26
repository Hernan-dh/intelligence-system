from __future__ import annotations

import json
from collections.abc import Awaitable, Callable

import gradio as gr
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas import ChatRequest, ChatResponse, DocumentIngestRequest, DocumentIngestResponse
from app.styles import CSS

ChatHandler = Callable[[ChatRequest], Awaitable[ChatResponse]]
IngestHandler = Callable[[DocumentIngestRequest], Awaitable[DocumentIngestResponse]]


def _header() -> str:
    return """<div class="is-mark"><span></span><span></span><span></span><span></span></div><div><p class="is-eyebrow">Local-first knowledge API · English-first</p><h1 class="is-title">AI Knowledge <span>Copilot</span></h1></div><p class="is-status">● API online</p>"""


def build_ui(chat_handler: ChatHandler, ingest_handler: IngestHandler) -> gr.Blocks:
    async def ask(message: str, thread_id: str, history: list[dict] | None):
        conversation = history or []
        if not message or len(message.strip()) < 3:
            raise gr.Error("Enter a question with at least 3 characters.")
        try:
            response = await chat_handler(ChatRequest(message=message.strip(), thread_id=thread_id.strip() or "demo-1"))
        except HTTPException as error:
            raise gr.Error(str(error.detail)) from error
        conversation.extend([
            {"role": "user", "content": message.strip()},
            {"role": "assistant", "content": response.answer},
        ])
        sources = [[source.title, f"{source.score:.3f}", source.excerpt] for source in response.sources]
        trace = "\n".join(f"**{item.agent.upper()}** — {item.detail}" for item in response.trace)
        return conversation, "", sources, trace

    async def ingest(document_id: str, title: str, content: str, metadata: str):
        try:
            parsed_metadata = json.loads(metadata or "{}")
            if not isinstance(parsed_metadata, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in parsed_metadata.items()):
                raise ValueError("Metadata must be a JSON object with string keys and values.")
            response = await ingest_handler(DocumentIngestRequest(
                document_id=document_id.strip(), title=title.strip(), content=content.strip(), metadata=parsed_metadata,
            ))
        except (ValueError, json.JSONDecodeError, ValidationError) as error:
            raise gr.Error(str(error)) from error
        except HTTPException as error:
            raise gr.Error(str(error.detail)) from error
        return f"**{response.status.title()}** — `{response.document_id}` is ready for retrieval."

    with gr.Blocks(title="AI Knowledge Copilot", css=CSS, theme=gr.themes.Base()) as demo:
        gr.HTML(_header(), elem_id="is-header")
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="Knowledge conversation", type="messages", height=420, elem_id="is-chat")
                with gr.Row():
                    message = gr.Textbox(label="Ask the knowledge base", placeholder="How do I request VPN access?", scale=4)
                    thread_id = gr.Textbox(label="Thread ID", value="demo-1", scale=1)
                ask_button = gr.Button("Ask knowledge base", variant="primary")
            with gr.Column(scale=2, elem_id="is-inspect"):
                gr.Markdown("### Retrieved sources")
                sources = gr.Dataframe(headers=["Source", "Score", "Excerpt"], datatype=["str", "str", "str"], interactive=False, wrap=True)
                gr.Markdown("### Execution trace")
                trace = gr.Markdown("Ask a question to inspect the supervisor, retrieval, and writer path.")
        with gr.Group(elem_id="is-ingest"):
            gr.Markdown("### Add knowledge")
            with gr.Row():
                document_id = gr.Textbox(label="Document ID", placeholder="remote-access")
                title = gr.Textbox(label="Title", placeholder="Remote access policy")
            content = gr.Textbox(label="Content", lines=4, placeholder="Write the procedure available to the knowledge base.")
            metadata = gr.Textbox(label="Metadata JSON", value='{"area":"it"}')
            ingest_button = gr.Button("Ingest document")
            ingest_status = gr.Markdown()
        ask_button.click(ask, [message, thread_id, chatbot], [chatbot, message, sources, trace])
        message.submit(ask, [message, thread_id, chatbot], [chatbot, message, sources, trace])
        ingest_button.click(ingest, [document_id, title, content, metadata], ingest_status)
    return demo
