import pytest
from pydantic import ValidationError
from app.rag import LocalRAG
from app.schemas import DocumentIngestRequest, SearchKnowledgeInput


@pytest.mark.asyncio
async def test_hybrid_retrieval_returns_vpn_source(tmp_path):
    rag = LocalRAG(str(tmp_path / "test.db"))
    await rag.initialize()
    results = await rag.search(SearchKnowledgeInput(query="Necesito acceso a la VPN"))
    assert results.sources[0].document_id == "vpn"


@pytest.mark.asyncio
async def test_ingestion_updates_a_document(tmp_path):
    rag = LocalRAG(str(tmp_path / "test.db"))
    await rag.initialize()
    document = DocumentIngestRequest(document_id="handbook", title="Manual interno", content="El manual interno explica cómo registrar una solicitud operativa.")
    assert await rag.ingest(document) == "created"
    assert await rag.ingest(document) == "updated"


def test_document_validation_rejects_invalid_id():
    with pytest.raises(ValidationError):
        DocumentIngestRequest(document_id="ID CON ESPACIOS", title="Título válido", content="Este contenido tiene el largo mínimo para pasar la validación.")
