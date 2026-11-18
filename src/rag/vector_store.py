
"""
Persistent Chroma vector store for the AI Data Assistant Agent.

Responsibilities:
    1. Load the chunked knowledge Nodes.
    2. Generate embeddings for those Nodes.
    3. Assign stable IDs to the Nodes.
    4. Store or update the Nodes in Chroma.
    5. Validate the stored record count.
    6. Inspect existing Chroma records.

This module intentionally does NOT:
    - perform retrieval
    - call Gemini for text generation
    - analyze datasets
    - modify knowledge files
    - modify dataset contents
"""

import hashlib

import chromadb

from llama_index.vector_stores.chroma import ChromaVectorStore

from .config import CHROMA_DIR
from .embeddings import embed_knowledge_nodes


COLLECTION_NAME = "data_assistant_knowledge"
DISTANCE_METRIC = "cosine"


def create_stable_node_id(node) -> str:
    """
    Return the same ID for the same source path and Node text.
    """

    source_path = str(
        node.metadata.get("source_path", "")
    )

    content = node.text

    stable_content = (
        f"{source_path}\n{content}"
    )

    return hashlib.sha256(
        stable_content.encode("utf-8")
    ).hexdigest()


def create_chroma_vector_store():
    """
    Create or open the persistent cosine collection.
    """

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    chroma_collection = (
        chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": DISTANCE_METRIC
            },
        )
    )

    # Prevent accidental use of an existing collection
    # configured with a different distance metric.
    actual_metric = (
        (chroma_collection.metadata or {})
        .get("hnsw:space", "l2")
    )

    if actual_metric != DISTANCE_METRIC:
        raise RuntimeError(
            "Incorrect Chroma distance metric. "
            f"Expected {DISTANCE_METRIC!r}, "
            f"found {actual_metric!r}."
        )

    vector_store = ChromaVectorStore(
        chroma_collection=chroma_collection
    )

    return (
        chroma_client,
        chroma_collection,
        vector_store,
    )


def store_knowledge_embeddings():
    """
    Store knowledge Nodes using stable IDs.

    Repeated runs update records with matching IDs
    instead of creating additional copies.
    """

    nodes, embeddings = embed_knowledge_nodes()

    if len(nodes) != len(embeddings):
        raise RuntimeError(
            "Node count does not match embedding count: "
            f"{len(nodes)} Nodes vs "
            f"{len(embeddings)} embeddings."
        )

    node_ids = [
        create_stable_node_id(node)
        for node in nodes
    ]

    if len(node_ids) != len(set(node_ids)):
        raise RuntimeError(
            "Duplicate stable Node IDs detected. "
            "Indexing stopped."
        )

    (
        chroma_client,
        chroma_collection,
        vector_store,
    ) = create_chroma_vector_store()

    documents = [node.text for node in nodes]
    metadatas = [node.metadata for node in nodes]

    chroma_collection.upsert(
        ids=node_ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    return (
        chroma_client,
        chroma_collection,
        vector_store,
        nodes,
        embeddings,
    )

def inspect_chroma_collection(sample_size: int = 3):
    """
    Inspect stored Chroma records without generating embeddings.
    """

    if sample_size < 0:
        raise ValueError(
            "sample_size must not be negative."
        )

    (
        _,
        chroma_collection,
        _,
    ) = create_chroma_vector_store()

    total_records = chroma_collection.count()

    print("=" * 70)
    print("CHROMA COLLECTION INSPECTION")
    print("=" * 70)

    print(f"Collection name : {COLLECTION_NAME}")
    print(f"Distance metric : {DISTANCE_METRIC}")
    print(f"Total records   : {total_records}")
    print(f"Metadata        : {chroma_collection.metadata}")
    print()

    if total_records == 0:
        print("The collection is empty.")
        return

    sample_size = min(
        sample_size,
        total_records,
    )

    if sample_size == 0:
        print("No sample records requested.")
        return

    results = chroma_collection.get(
        limit=sample_size,
        include=[
            "documents",
            "metadatas",
            "embeddings",
        ],
    )

    ids = results.get("ids", [])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    embeddings = results.get("embeddings", [])

    print(f"Records inspected: {len(ids)}")
    print()

    for index, record_id in enumerate(ids):
        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        document = (
            documents[index]
            if index < len(documents)
            else ""
        )

        embedding = (
            embeddings[index]
            if index < len(embeddings)
            else None
        )

        print("=" * 70)
        print(f"Record {index + 1}")
        print("-" * 70)

        print(f"ID       : {record_id}")
        print(
            f"Source   : "
            f"{metadata.get('source_path', 'unknown')}"
        )
        print(
            f"Category : "
            f"{metadata.get('category', 'unknown')}"
        )

        print()
        print("Node text:")
        print("-" * 70)
        print(document)
        print()

        if embedding is not None:
            print(
                f"Embedding dimensions: {len(embedding)}"
            )
            print(
                f"First 5 values      : {embedding[:5]}"
            )
        else:
            print("Embedding: not returned")

        print()


if __name__ == "__main__":
    inspect_chroma_collection()
