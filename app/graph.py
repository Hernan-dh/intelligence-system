import re
from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from app.config import settings
from app.rag import LocalRAG
from app.schemas import AgentTrace, SearchKnowledgeInput, Source


class IntelligenceState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    query: str
    route: Literal["researcher", "writer"]
    sources: list[Source]
    answer: str
    trace: list[AgentTrace]


RETRIEVAL_TERMS = {
    "cómo", "como", "cuál", "cual", "qué", "que", "vpn", "contraseña",
    "incidente", "política", "proceso", "acceso",
}


def deterministic_route(query: str) -> Literal["researcher", "writer"]:
    """Route known knowledge requests without depending on model wording."""
    return "researcher" if any(term in query.lower() for term in RETRIEVAL_TERMS) else "writer"


def parse_route(content: object) -> Literal["researcher", "writer"] | None:
    """Accept only the constrained routing tokens, never a best-effort guess."""
    match = re.fullmatch(r"\s*(RESEARCHER|WRITER)\s*[.!]?\s*", str(content), flags=re.IGNORECASE)
    return match.group(1).lower() if match else None


def build_graph(rag: LocalRAG, checkpointer):
    async def supervisor(state: IntelligenceState):
        fallback_route = deterministic_route(state["query"])
        if settings.openai_api_key:
            from langchain_openai import ChatOpenAI
            model = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0)
            decision = await _invoke_with_retry(model, f"Sos un supervisor. Respondé únicamente RESEARCHER si la pregunta requiere consultar documentación; respondé únicamente WRITER si es conversación general. Pregunta: {state['query']}")
            model_route = parse_route(decision.content)
            route = "researcher" if fallback_route == "researcher" else (model_route or fallback_route)
        else:
            route = fallback_route
        detail = "Delegó la búsqueda de conocimiento al agente RAG." if route == "researcher" else "Identificó una consulta conversacional y delegó la respuesta directa al escritor."
        return {"route": route, "sources": [], "trace": [AgentTrace(agent="supervisor", detail=detail)]}

    async def researcher(state: IntelligenceState):
        result = await rag.search(SearchKnowledgeInput(query=state["query"]))
        return {"sources": result.sources, "trace": state["trace"] + [AgentTrace(agent="researcher", detail=f"Recuperó {len(result.sources)} fuentes locales mediante ranking híbrido.")]}

    async def writer(state: IntelligenceState):
        sources = state["sources"]
        context = "\n".join(f"- {source.title}: {source.excerpt}" for source in sources) or "Sin fuentes recuperadas."
        history = "\n".join(str(message.content) for message in state.get("messages", [])[-6:] if hasattr(message, "content"))
        if state["route"] == "researcher" and not sources:
            answer = "No encontré información suficiente en la documentación disponible para responder esa consulta."
        elif settings.openai_api_key:
            from langchain_openai import ChatOpenAI
            model = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0)
            response = await _invoke_with_retry(model, f"Respondé en español usando solo este contexto. Considerá el historial para mantener la conversación. Si no alcanza, decilo.\n\nHistorial:\n{history}\n\nContexto:\n{context}\n\nPregunta: {state['query']}")
            answer = str(response.content)
        elif sources:
            answer = f"Según la documentación disponible: {sources[0].excerpt}"
        else:
            answer = "Hola. Puedo ayudarte con consultas sobre los procedimientos disponibles."
        return {"answer": answer, "trace": state["trace"] + [AgentTrace(agent="writer", detail="Generó una respuesta fundamentada en las fuentes recuperadas.")]}

    graph = StateGraph(IntelligenceState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", lambda state: state["route"], {"researcher": "researcher", "writer": "writer"})
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", END)
    return graph.compile(checkpointer=checkpointer)


async def _invoke_with_retry(model, prompt: str):
    import asyncio
    last_error = None
    for attempt in range(3):
        try:
            return await model.ainvoke(prompt)
        except Exception as error:
            last_error = error
            if attempt < 2:
                await asyncio.sleep(2**attempt)
    raise RuntimeError("El proveedor LLM no respondió después de 3 intentos") from last_error
