"""
Script de ingesta de la Base de Conocimientos en ChromaDB.
Implementa:
  - Structure-Aware Chunking (MarkdownHeaderTextSplitter)
  - Question-to-Question Matching (Q2Q) con generación de preguntas hipotéticas
  - Doble colección: chunks originales + índice Q2Q
"""

import os
import sys
import uuid
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage
from app.core.chromadb_client import ChromaDBClient
from app.core.llm_service import LLMService
from app.core.logging import get_logger

logger = get_logger("knowledge_loader")

# Structure-Aware: respetar jerarquías Markdown
HEADERS_TO_SPLIT_ON = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

# Chunk size limit para segunda pasada si un chunk es muy grande
MAX_CHUNK_SIZE = 800  # caracteres (~200 tokens)
CHUNK_OVERLAP = 100


async def generate_q2q_questions(chunk_content: str, headers: dict, llm_service: LLMService) -> list[str]:
    """
    Genera preguntas hipotéticas (Q2Q) que un usuario podría hacer y que se responden
    con la información del chunk. Esto mejora drásticamente la precisión del retrieval.
    """
    header_context = " > ".join([v for v in headers.values() if v]) if headers else "General"

    prompt = f"""Sos un experto en servicio al cliente de una fintech llamada Conversa Pay.
Tu tarea es leer el siguiente fragmento de documentación interna y generar exactamente 5 preguntas
que un cliente real podría hacerle al chatbot y que se responden con esta información.

Las preguntas deben ser:
- En español rioplatense informal (como hablaría un usuario argentino real)
- Variadas: algunas formales, algunas coloquiales, algunas con jerga
- Directas y específicas (no genéricas)

Sección: {header_context}

Texto del fragmento:
{chunk_content}

Respondé SOLO con las 5 preguntas, una por línea, sin numeración ni viñetas. Nada más."""

    try:
        response = await llm_service.generate([HumanMessage(content=prompt)])
        lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
        # Limpiar cualquier formateo residual del LLM
        questions = []
        for line in lines:
            cleaned = line.lstrip('-*•0123456789.) ').strip()
            if cleaned and len(cleaned) > 10:
                questions.append(cleaned)
        return questions[:5]
    except Exception as e:
        logger.error(f"Error generando preguntas Q2Q: {e}")
        return []


def clean_collection(collection, name: str):
    """Limpia todos los documentos de una colección para re-ingesta."""
    try:
        existing = collection.get()
        if existing and existing['ids']:
            collection.delete(ids=existing['ids'])
            logger.info(f"Colección '{name}' limpiada: {len(existing['ids'])} documentos eliminados.")
    except Exception as e:
        logger.warning(f"No se pudo limpiar '{name}': {e}")


async def process_document(
    file_path: str,
    kb_collection,
    q2q_collection,
    llm_service: LLMService,
    md_splitter: MarkdownHeaderTextSplitter,
    text_splitter: RecursiveCharacterTextSplitter
):
    """Procesa un archivo Markdown y lo inserta en ambas colecciones de ChromaDB."""
    filename = os.path.basename(file_path)
    logger.info(f"Procesando: {filename}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error leyendo {file_path}: {e}")
        return 0, 0

    # 1. Structure-Aware Chunking: dividir por headers Markdown
    header_splits = md_splitter.split_text(content)

    if not header_splits:
        logger.warning(f"No se generaron chunks para {filename}")
        return 0, 0

    kb_docs, kb_metas, kb_ids = [], [], []
    q2q_docs, q2q_metas, q2q_ids = [], [], []

    total_chunks = 0
    total_questions = 0

    for i, split in enumerate(header_splits):
        chunk_text = split.page_content.strip()
        if not chunk_text or len(chunk_text) < 30:
            continue

        # 2. Si el chunk es muy grande, subdividir con RecursiveCharacterTextSplitter
        if len(chunk_text) > MAX_CHUNK_SIZE:
            sub_chunks = text_splitter.split_text(chunk_text)
        else:
            sub_chunks = [chunk_text]

        for j, sub_chunk in enumerate(sub_chunks):
            chunk_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{filename}_{i}_{j}"))
            headers = split.metadata.copy()

            # --- Colección A: Knowledge Base (chunks originales) ---
            kb_meta = {
                "source": filename,
                "chunk_index": total_chunks,
                **{k: v for k, v in headers.items() if v}
            }
            kb_docs.append(sub_chunk)
            kb_metas.append(kb_meta)
            kb_ids.append(chunk_id)

            # --- Colección Q2Q: Preguntas hipotéticas ---
            questions = await generate_q2q_questions(sub_chunk, headers, llm_service)

            for q_idx, question in enumerate(questions):
                q2q_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{filename}_{i}_{j}_q{q_idx}"))
                q2q_meta = {
                    "source": filename,
                    "chunk_index": total_chunks,
                    "original_chunk_id": chunk_id,
                    "original_content": sub_chunk[:1500],  # Guardar contenido original para retrieval
                    **{k: v for k, v in headers.items() if v}
                }
                q2q_docs.append(question)
                q2q_metas.append(q2q_meta)
                q2q_ids.append(q2q_id)
                total_questions += 1

            total_chunks += 1
            logger.info(f"  Chunk {total_chunks} ({len(sub_chunk)} chars) -> {len(questions)} preguntas Q2Q")

    # 3. Insertar en ChromaDB (batch upsert para idempotencia)
    if kb_docs:
        # ChromaDB tiene límite de batch, insertar en grupos de 40
        batch_size = 40
        for start in range(0, len(kb_docs), batch_size):
            end = start + batch_size
            kb_collection.upsert(
                documents=kb_docs[start:end],
                metadatas=kb_metas[start:end],
                ids=kb_ids[start:end]
            )

    if q2q_docs:
        batch_size = 40
        for start in range(0, len(q2q_docs), batch_size):
            end = start + batch_size
            q2q_collection.upsert(
                documents=q2q_docs[start:end],
                metadatas=q2q_metas[start:end],
                ids=q2q_ids[start:end]
            )

    logger.info(f"  {filename}: {total_chunks} chunks, {total_questions} preguntas Q2Q insertadas.")
    return total_chunks, total_questions


async def main():
    """Punto de entrada principal para la ingesta de la base de conocimiento."""
    logger.info("=" * 60)
    logger.info("INICIANDO INGESTA DE BASE DE CONOCIMIENTOS (RAG)")
    logger.info("=" * 60)

    client = ChromaDBClient()
    kb_collection = client.knowledge_base
    q2q_collection = client.q2q_index

    if not kb_collection or not q2q_collection:
        logger.error("No se pudo conectar a las colecciones de ChromaDB. Abortando.")
        return

    # Limpiar colecciones para re-ingesta limpia
    clean_collection(kb_collection, "conversapay_knowledge_base")
    clean_collection(q2q_collection, "conversapay_q2q_index")

    llm_service = LLMService()

    # Splitters
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "]
    )

    # Buscar archivos Markdown en el directorio de knowledge_base
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "knowledge_base")
    docs_dir = os.path.abspath(docs_dir)

    if not os.path.exists(docs_dir):
        logger.error(f"El directorio {docs_dir} no existe. Abortando.")
        return

    md_files = [f for f in os.listdir(docs_dir) if f.endswith(".md")]
    if not md_files:
        logger.warning(f"No se encontraron archivos .md en {docs_dir}")
        return

    logger.info(f"Encontrados {len(md_files)} archivos Markdown para procesar.")

    grand_total_chunks = 0
    grand_total_questions = 0

    for filename in sorted(md_files):
        file_path = os.path.join(docs_dir, filename)
        chunks, questions = await process_document(
            file_path, kb_collection, q2q_collection, llm_service, md_splitter, text_splitter
        )
        grand_total_chunks += chunks
        grand_total_questions += questions

    logger.info("=" * 60)
    logger.info(f"INGESTA COMPLETADA")
    logger.info(f"  Total chunks en knowledge_base: {grand_total_chunks}")
    logger.info(f"  Total preguntas en q2q_index: {grand_total_questions}")
    logger.info(f"  Archivos procesados: {len(md_files)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
