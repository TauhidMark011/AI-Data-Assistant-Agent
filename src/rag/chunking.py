"""
Document-to-Node chunking for the AI Data Assistant Agent.

Responsibilities:
    1. Load knowledge Documents using the ingestion layer.
    2. Split Documents into smaller Nodes.
    3. Preserve source metadata.
    4. Provide deterministic chunking configuration.

This module intentionally does NOT:
    - generate embeddings
    - call Gemini
    - create/use Chroma
    - perform retrieval
    - call an LLM
    - analyze datasets
    - modify knowledge files
"""
#In LlamaIndex, the SentenceSplitter is a tool that breaks down long documents into smaller, manageable -
#text pieces (called "chunks" or "nodes") while trying its best to keep complete sentences and paragraphs together.
#LlamaIndex uses to chop up your data before saving it into a vector database for AI search (RAG)
from llama_index.core.node_parser import SentenceSplitter

from .ingestion import load_knowledge_documents


# ============================================================================
# CHUNKING CONFIGURATION
# ============================================================================

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


# ============================================================================
# DOCUMENT → NODES
# ============================================================================

def chunk_knowledge_documents():
    """
    Convert LlamaIndex Documents into smaller Nodes.

    Returns:
        A list of LlamaIndex Nodes.
    """

    documents = load_knowledge_documents()

    splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    nodes = splitter.get_nodes_from_documents(
        documents
    )

    return nodes


# ============================================================================
# LOCAL TEST
# ============================================================================

if __name__ == "__main__":
    nodes = chunk_knowledge_documents()

    print("=" * 70)
    print("KNOWLEDGE CHUNKING TEST")
    print("=" * 70)

    print(f"Documents loaded : 19")
    print(f"Chunk size       : {CHUNK_SIZE}")
    print(f"Chunk overlap    : {CHUNK_OVERLAP}")
    print(f"Nodes created    : {len(nodes)}")
    print()

    print("Sample nodes:")
    print("-" * 70)

    for index, node in enumerate(nodes[:10], start=1):
        source_path = node.metadata.get(
            "source_path",
            "unknown"
        )

        print(f"[{index:02d}] Source : {source_path}")
        print(f"     Characters : {len(node.text)}")
        print(f"     Preview    : {node.text[:200].replace(chr(10), ' ')}")
        print()