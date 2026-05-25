import os
import sys
import glob
import uuid

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langchain_text_splitters import MarkdownHeaderTextSplitter
from app.core.chromadb_client import ChromaDBClient
from app.core.logging import get_logger

logger = get_logger("ingest_kb")

def main():
    logger.info("Iniciando ingesta de la Base de Conocimientos (RAG)...")
    
    client = ChromaDBClient()
    collection = client.knowledge_base
    
    if not collection:
        logger.error("No se pudo conectar a la colección 'conversapay_knowledge_base' de ChromaDB.")
        return

    # Limpiar colección existente para re-ingesta
    # (En la práctica, podríamos hacer update, pero para el MVP limpiamos e insertamos)
    try:
        docs = collection.get()
        if docs and docs['ids']:
            collection.delete(ids=docs['ids'])
            logger.info(f"Colección limpiada. Se eliminaron {len(docs['ids'])} fragmentos previos.")
    except Exception as e:
        logger.warning(f"No se pudo limpiar la colección: {e}")

    kb_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "knowledge_base")
    md_files = glob.glob(os.path.join(kb_dir, "*.md"))
    
    if not md_files:
        logger.warning(f"No se encontraron archivos Markdown en {kb_dir}")
        return

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    total_chunks = 0
    for file_path in md_files:
        filename = os.path.basename(file_path)
        logger.info(f"Procesando: {filename}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        splits = markdown_splitter.split_text(content)
        
        if not splits:
            continue
            
        docs_texts = []
        docs_metadatas = []
        docs_ids = []
        
        for i, split in enumerate(splits):
            docs_texts.append(split.page_content)
            
            # Combine extracted headers with filename
            meta = split.metadata.copy()
            meta["source"] = filename
            meta["chunk"] = i
            docs_metadatas.append(meta)
            
            docs_ids.append(str(uuid.uuid4()))
            
        collection.add(
            documents=docs_texts,
            metadatas=docs_metadatas,
            ids=docs_ids
        )
        total_chunks += len(splits)
        logger.info(f"Insertados {len(splits)} fragmentos de {filename}")

    logger.info(f"Ingesta completada. Total de fragmentos: {total_chunks}")

if __name__ == "__main__":
    main()
