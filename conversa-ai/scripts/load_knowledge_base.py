import os
import sys
import uuid
import asyncio

# Añadir el directorio raíz al path para poder importar módulos de la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__name__))))

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.messages import HumanMessage
from app.core.chromadb_client import ChromaDBClient
from app.core.llm_service import LLMService
from app.core.logging import get_logger

logger = get_logger("knowledge_loader")

# Configuración del splitter para respetar la estructura del Markdown
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)


async def generate_q2q_questions(chunk_content: str, llm_service: LLMService) -> list[str]:
    """
    Genera preguntas hipotéticas (Q2Q) basadas en un fragmento de texto.
    """
    prompt = f"""Sos un experto en bases de conocimiento. 
Dada la siguiente sección de un manual de usuario, generá exactamente 3 preguntas que un usuario podría hacer y que se responden con esta información.
Devolvé solo las preguntas, una por línea, sin viñetas ni numeración.

Texto:
{chunk_content}
"""
    try:
        response = await llm_service.generate([HumanMessage(content=prompt)])
        questions = [q.strip() for q in response.split('\n') if q.strip() and not q.startswith('¿')]
        # Limpiar posibles caracteres de viñetas si el LLM las agregó
        questions = [q.lstrip('-*1234567890. ') for q in questions]
        return questions[:3]
    except Exception as e:
        logger.error(f"Error generando preguntas Q2Q: {e}")
        return []


async def process_document(file_path: str, collection, llm_service: LLMService):
    """
    Procesa un documento Markdown y lo inserta en ChromaDB.
    """
    logger.info(f"Procesando {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            markdown_document = f.read()
    except Exception as e:
        logger.error(f"Error leyendo {file_path}: {e}")
        return

    # Structure-Aware Chunking
    md_header_splits = markdown_splitter.split_text(markdown_document)
    
    documents_to_insert = []
    metadatas_to_insert = []
    ids_to_insert = []

    for i, split in enumerate(md_header_splits):
        chunk_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{file_path}_{i}"))
        
        # Generar preguntas Q2Q
        questions = await generate_q2q_questions(split.page_content, llm_service)
        
        # El documento principal a indexar es una combinación de las preguntas Q2Q y el texto
        # Esto mejora drásticamente el Retrieval
        indexed_content = "\n".join(questions) + "\n\n=== CONTENIDO ===\n\n" + split.page_content
        
        metadata = split.metadata
        metadata["source"] = os.path.basename(file_path)
        metadata["chunk_index"] = i
        metadata["original_content"] = split.page_content # Guardamos el original para mostrar al usuario
        
        documents_to_insert.append(indexed_content)
        metadatas_to_insert.append(metadata)
        ids_to_insert.append(chunk_id)
        
        logger.info(f"Chunk {i+1}/{len(md_header_splits)} procesado con {len(questions)} preguntas Q2Q.")

    # Insertar en ChromaDB (Upsert para idempotencia)
    if documents_to_insert:
        collection.upsert(
            documents=documents_to_insert,
            metadatas=metadatas_to_insert,
            ids=ids_to_insert
        )
        logger.info(f"Insertados/Actualizados {len(documents_to_insert)} chunks en la base de conocimiento.")


async def main():
    client = ChromaDBClient()
    collection = client.knowledge_base
    if not collection:
        logger.error("No se pudo obtener la colección de la base de conocimiento.")
        return

    llm_service = LLMService()
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__name__))), "docs", "knowledge_base")
    
    if not os.path.exists(docs_dir):
        logger.warning(f"El directorio {docs_dir} no existe.")
        return
        
    for filename in os.listdir(docs_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(docs_dir, filename)
            await process_document(file_path, collection, llm_service)
            
    logger.info("Carga de base de conocimiento completada.")


if __name__ == "__main__":
    asyncio.run(main())
