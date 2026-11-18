# Call retrieve_relevant_nodes() to get the top matching knowledge chunks.
# Convert Chroma's nested result format into a clean, structured context.
# Preserve source information for traceability.
# Handle empty results safely.
# Limit context size to control unnecessary token usage.
# Make no Gemini API calls and modify no dataset.

"""
Grounded context builder for the AI Data Assistant Agent.

Responsibilities:
1. Retrieve relevant knowledge using the existing RAG retrieval layer.
2. Organize retrieved evidence into a structured format.
3. Preserve source information for traceability.
4. Limit the amount of context prepared for future LLM generation.

This module does NOT:
- generate LLM responses;
- detect data-quality issues;
- make decisions about datasets;
- modify datasets;
- execute remediation.
"""

from .retrieval import DEFAULT_TOP_K, retrieve_relevant_nodes


DEFAULT_MAX_CONTEXT_CHARS = 12000
DEFAULT_MAX_CHUNK_CHARS = 4000


def build_grounded_context(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
) -> dict:
    """
    Retrieve relevant knowledge and prepare grounded context.

    Returns:
        A dictionary containing the query, retrieval status,
        evidence records, source references, and formatted context.
    """

    if not query or not query.strip():
        raise ValueError("Query must not be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    if max_context_chars <= 0:
        raise ValueError("max_context_chars must be greater than zero.")

    if max_chunk_chars <= 0:
        raise ValueError("max_chunk_chars must be greater than zero.")

    results = retrieve_relevant_nodes(
        query=query,
        top_k=top_k,
    )

    ids = results.get("ids", [[]])[0] or []
    documents = results.get("documents", [[]])[0] or []
    metadatas = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    # Use only records that have both an ID and document text.
    record_count = min(len(ids), len(documents))

    evidence = []
    context_blocks = []
    used_chars = 0

    for index in range(record_count):
        document_text = documents[index]

        if not isinstance(document_text, str) or not document_text.strip():
            continue

        metadata = (
            metadatas[index]
            if index < len(metadatas) and metadatas[index]
            else {}
        )

        record_id = ids[index]
        source_path = metadata.get("source_path", "unknown")
        category = metadata.get("category", "unknown")
        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        # Limit the size of an individual knowledge chunk.
        text = document_text[:max_chunk_chars]

        if len(document_text) > max_chunk_chars:
            text += "\n[Knowledge chunk truncated.]"

        block = (
            f"[Evidence {len(evidence) + 1}]\n"
            f"Source: {source_path}\n"
            f"Category: {category}\n"
            f"Record ID: {record_id}\n"
            f"Cosine distance: {distance}\n"
            f"Knowledge:\n{text}\n"
        )

        # Keep the complete evidence block within the overall limit.
        separator = "\n---\n" if context_blocks else ""
        remaining = max_context_chars - used_chars - len(separator)

        if remaining <= 0:
            break

        if len(block) > remaining:
            notice = "\n[Context limit reached.]"

            if remaining <= len(notice):
                break

            block = block[:remaining - len(notice)] + notice

        context_blocks.append(separator + block)
        used_chars += len(separator + block)

        evidence.append(
            {
                "id": record_id,
                "source_path": source_path,
                "category": category,
                "distance": distance,
                "text": text,
            }
        )

        if used_chars >= max_context_chars:
            break

    context_text = "".join(context_blocks)

    return {
        "query": query.strip(),
        "top_k": top_k,
        "retrieved_count": len(ids),
        "evidence_count": len(evidence),
        "status": "ok" if evidence else "no_results",
        "sources": list(
            dict.fromkeys(item["source_path"] for item in evidence)
        ),
        "evidence": evidence,
        "context_text": context_text,
        "context_characters": len(context_text),
        "max_context_characters": max_context_chars,
    }


if __name__ == "__main__":
    test_query = "When is human approval required?"

    result = build_grounded_context(
        query=test_query,
        top_k=DEFAULT_TOP_K,
    )

    print("=" * 70)
    print("GROUNDED CONTEXT BUILDER TEST")
    print("=" * 70)
    print(f"Query            : {result['query']}")
    print(f"Status           : {result['status']}")
    print(f"Retrieved        : {result['retrieved_count']}")
    print(f"Evidence records : {result['evidence_count']}")
    print(f"Context chars    : {result['context_characters']}")
    print(f"Sources          : {result['sources']}")
    print()
    print("GROUNDED CONTEXT")
    print("-" * 70)
    print(result["context_text"])
