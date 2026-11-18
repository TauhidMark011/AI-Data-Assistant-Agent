"""
Embedding layer for the AI Data Assistant Agent.

Responsibilities:
    1. Load the chunked knowledge Nodes.
    2. Create a Google Gemini embedding model.
    3. Convert Node text into embedding vectors.
    4. Validate the resulting embeddings.

This module intentionally does NOT:
    - create/use Chroma
    - perform retrieval
    - call Gemini for text generation
    - analyze datasets
    - modify knowledge files
    - modify dataset contents
"""

from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

from .chunking import chunk_knowledge_documents
from .config import GOOGLE_API_KEY


# ============================================================================
# EMBEDDING CONFIGURATION
# ============================================================================

EMBEDDING_MODEL_NAME = "gemini-embedding-001"


# ============================================================================
# EMBEDDING MODEL
# ============================================================================

def create_embedding_model() -> GoogleGenAIEmbedding:
    """
    Create the Google Gemini embedding model.

    Returns:
        Configured GoogleGenAIEmbedding instance.
    """

    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured."
        )

    return GoogleGenAIEmbedding(
        model_name=EMBEDDING_MODEL_NAME,
        api_key=GOOGLE_API_KEY,
    )


# ============================================================================
# NODE EMBEDDING
# ============================================================================

def embed_knowledge_nodes():
    """
    Convert all knowledge Nodes into embedding vectors.

    Returns:
        Tuple containing:
            - Nodes
            - Corresponding embedding vectors
    """

    nodes = chunk_knowledge_documents()

    embedding_model = create_embedding_model()

    texts = [
        node.text
        for node in nodes
    ]

    embeddings = embedding_model.get_text_embedding_batch(
        texts
    )

    if len(embeddings) != len(nodes):
        raise RuntimeError(
            "Embedding count does not match Node count: "
            f"{len(embeddings)} embeddings for "
            f"{len(nodes)} Nodes."
        )

    return nodes, embeddings


# ============================================================================
# LOCAL TEST
# ============================================================================

if __name__ == "__main__":
    nodes, embeddings = embed_knowledge_nodes()

    print("=" * 70)
    print("KNOWLEDGE EMBEDDING TEST")
    print("=" * 70)

    print(f"Embedding model : {EMBEDDING_MODEL_NAME}")
    print(f"Nodes received  : {len(nodes)}")
    print(f"Embeddings      : {len(embeddings)}")

    if embeddings:
        dimension = len(embeddings[0])

        print(f"Vector dimension: {dimension}")
        print()

        print("Validation:")
        print("-" * 70)

        all_same_dimension = all(
            len(vector) == dimension
            for vector in embeddings
        )

        print(
            f"All vectors same dimension : "
            f"{all_same_dimension}"
        )

        print()
        print("First vector preview:")
        print("-" * 70)
        print(embeddings[0][:10])
        print("...")
        print(
            f"Total values in first vector: "
            f"{len(embeddings[0])}"
        )

        print()
        print("First vector source:")
        print("-" * 70)
        print(
            nodes[0].metadata.get(
                "source_path",
                "unknown"
            )
        )