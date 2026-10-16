import pytest
from langgraph.checkpoint.memory import MemorySaver
from app.graph import build_graph
from app.rag import LocalRAG


@pytest.mark.asyncio
async def test_graph_routes_research_and_remembers_messages(tmp_path):
    rag = LocalRAG(str(tmp_path / "test.db"))
    await rag.initialize()
    graph = build_graph(rag, MemorySaver())
    config = {"configurable": {"thread_id": "memory-test"}}
    first = await graph.ainvoke({"query": "¿Cómo solicito acceso VPN?", "messages": [("user", "¿Cómo solicito acceso VPN?")], "trace": []}, config)
    second = await graph.ainvoke({"query": "Hola", "messages": [("user", "Hola")], "trace": []}, config)
    snapshot = await graph.aget_state(config)
    assert first["sources"][0].document_id == "vpn"
    assert second["trace"][0].agent == "supervisor"
    assert len(snapshot.values["messages"]) >= 2
