import hashlib
import math
import re
import aiosqlite
from app.schemas import DocumentIngestRequest, SearchKnowledgeInput, SearchKnowledgeOutput, Source

DOCUMENTS = [
    ("vpn", "Acceso VPN", "Para solicitar acceso VPN, abrí un ticket en Soporte, indicá tu equipo y la fecha de necesidad. El responsable aprueba en un día hábil.", '{"area":"soporte"}'),
    ("password", "Restablecer contraseña", "Usá el portal de identidad para restablecer la contraseña. Si no tenés acceso al segundo factor, contactá a Seguridad.", '{"area":"seguridad"}'),
    ("incident", "Reporte de incidentes", "Los incidentes de seguridad se reportan inmediatamente al canal de Seguridad y mediante un ticket con prioridad alta.", '{"area":"seguridad"}'),
]


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúüñ0-9]+", text.lower())


def _embedding(text: str, dimensions: int = 64) -> list[float]:
    values = [0.0] * dimensions
    for token in _tokens(text):
        values[int(hashlib.sha256(token.encode()).hexdigest(), 16) % dimensions] += 1
    norm = math.sqrt(sum(item * item for item in values)) or 1.0
    return [item / norm for item in values]


class LocalRAG:
    def __init__(self, database_path: str):
        self.database_path = database_path

    async def initialize(self) -> None:
        async with aiosqlite.connect(self.database_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL, metadata TEXT NOT NULL DEFAULT '{}')")
            columns = {row[1] for row in await (await db.execute("PRAGMA table_info(documents)")).fetchall()}
            if "metadata" not in columns:
                await db.execute("ALTER TABLE documents ADD COLUMN metadata TEXT NOT NULL DEFAULT '{}'")
            for document in DOCUMENTS:
                await db.execute("INSERT OR IGNORE INTO documents VALUES (?, ?, ?, ?)", document)
            await db.commit()

    async def ingest(self, document: DocumentIngestRequest) -> str:
        import json
        async with aiosqlite.connect(self.database_path) as db:
            exists = await (await db.execute("SELECT 1 FROM documents WHERE id = ?", (document.document_id,))).fetchone()
            await db.execute(
                "INSERT INTO documents (id, title, content, metadata) VALUES (?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET title=excluded.title, content=excluded.content, metadata=excluded.metadata",
                (document.document_id, document.title, document.content, json.dumps(document.metadata)),
            )
            await db.commit()
        return "updated" if exists else "created"

    async def search(self, tool_input: SearchKnowledgeInput) -> SearchKnowledgeOutput:
        query_vector = _embedding(tool_input.query)
        query_terms = set(_tokens(tool_input.query))
        async with aiosqlite.connect(self.database_path) as db:
            rows = await (await db.execute("SELECT id, title, content FROM documents")).fetchall()
        ranked = []
        for document_id, title, content in rows:
            vector_score = sum(a * b for a, b in zip(query_vector, _embedding(content)))
            terms = set(_tokens(content))
            lexical_score = len(query_terms & terms) / max(len(query_terms), 1)
            score = round(0.65 * vector_score + 0.35 * lexical_score, 3)
            ranked.append(Source(document_id=document_id, title=title, excerpt=content, score=max(score, 0)))
        return SearchKnowledgeOutput(sources=sorted(ranked, key=lambda item: item.score, reverse=True)[: tool_input.limit])
