import pytest
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.graph import build_graph, deterministic_route, parse_route
from app.rag import LocalRAG


@pytest.mark.asyncio
async def test_graph_routes_research_and_persists_messages_after_restart(tmp_path):
    rag = LocalRAG(str(tmp_path / "test.db"))
    await rag.initialize()
    config = {"configurable": {"thread_id": "memory-test"}}
    checkpoint_path = str(tmp_path / "checkpoints.db")
    async with AsyncSqliteSaver.from_conn_string(checkpoint_path) as checkpointer:
        graph = build_graph(rag, checkpointer)
        first = await graph.ainvoke({"query": "¿Cómo solicito acceso VPN?", "messages": [("user", "¿Cómo solicito acceso VPN?")], "trace": []}, config)
    async with AsyncSqliteSaver.from_conn_string(checkpoint_path) as checkpointer:
        restarted_graph = build_graph(rag, checkpointer)
        second = await restarted_graph.ainvoke({"query": "Hola", "messages": [("user", "Hola")], "trace": []}, config)
        snapshot = await restarted_graph.aget_state(config)
    assert first["sources"][0].document_id == "vpn"
    assert second["trace"][0].agent == "supervisor"
    assert len(snapshot.values["messages"]) >= 2


def test_route_helpers_preserve_deterministic_knowledge_routing():
    assert deterministic_route("¿Cómo solicito acceso VPN?") == "researcher"
    assert deterministic_route("Hola") == "writer"
    assert parse_route("RESEARCHER") == "researcher"
    assert parse_route("writer.") == "writer"
    assert parse_route("Use RESEARCHER when needed") is None
