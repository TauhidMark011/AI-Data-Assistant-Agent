"""
Retrieval layer for the AI Data Assistant Agent.

Responsibilities:
    1. Convert a user question into an embedding vector.
    2. Search the existing Chroma knowledge collection.
    3. Return the most relevant knowledge Nodes.

This module intentionally does NOT:
    - generate a final LLM answer
    - analyze datasets
    - calculate data-quality findings
    - modify datasets
    - perform remediation
"""

from .embeddings import create_embedding_model
from .vector_store import create_chroma_vector_store


DEFAULT_TOP_K = 3


def retrieve_relevant_nodes(
    query: str,
    top_k: int = DEFAULT_TOP_K,
):
    """
    Retrieve the most relevant knowledge Nodes for a user query.
    """

    if not query or not query.strip():
        raise ValueError("Query must not be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    embedding_model = create_embedding_model()

    query_vector = embedding_model.get_text_embedding(
        query
    )

    _, chroma_collection, _ = create_chroma_vector_store()

    results = chroma_collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    return results


if __name__ == "__main__":
    query = "When is human approval required?"

    results = retrieve_relevant_nodes(
        query=query,
        top_k=DEFAULT_TOP_K,
    )

    print("=" * 70)
    print("CHROMA RETRIEVAL TEST")
    print("=" * 70)

    print(f"Query   : {query}")
    print(f"Top-K   : {DEFAULT_TOP_K}")
    print()

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    print(f"Results returned: {len(ids)}")
    print()

    for index, record_id in enumerate(ids):
        print("-" * 70)
        print(f"Result {index + 1}")
        print("-" * 70)

        print(f"ID       : {record_id}")
        print(
            f"Source   : "
            f"{metadatas[index].get('source_path', 'unknown')}"
        )
        print(
            f"Category : "
            f"{metadatas[index].get('category', 'unknown')}"
        )
        print(f"Distance : {distances[index]}")
        print()

        print("Node text:")
        print("-" * 70)
        print(documents[index])
        print()