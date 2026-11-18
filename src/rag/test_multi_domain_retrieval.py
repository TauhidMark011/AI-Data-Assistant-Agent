"""
Multi-domain retrieval validation for the AI Data Assistant Agent.

This script validates semantic retrieval across multiple knowledge domains.

It does NOT:
    - modify knowledge files
    - modify datasets
    - generate LLM responses
    - perform remediation
"""

from .retrieval import retrieve_relevant_nodes


TEST_QUERIES = [
    (
        "Completeness",
        "What are common data quality problems related to completeness?",
    ),
    (
        "Validity",
        "What is a validity issue in data quality?",
    ),
    (
        "Schema",
        "What should be checked when validating a dataset schema?",
    ),
    (
        "Remediation",
        "What guidance should be followed before correcting a data quality issue?",
    ),
    (
        "HITL",
        "When is human approval required?",
    ),
]


def run_multi_domain_retrieval_test():
    print("=" * 70)
    print("MULTI-DOMAIN RETRIEVAL VALIDATION")
    print("=" * 70)
    print()

    for domain, query in TEST_QUERIES:
        print("=" * 70)
        print(f"DOMAIN: {domain}")
        print("=" * 70)

        print(f"Query: {query}")
        print()

        results = retrieve_relevant_nodes(
            query=query,
            top_k=3,
        )

        #Extract all returned fields, including distances.
        ids = results.get("ids", [[]])[0] or []
        documents = results.get("documents", [[]])[0] or []
        metadatas = results.get("metadatas", [[]])[0] or []
        distances = results.get("distances", [[]])[0] or []

        #Validate that retrieval returned usable, traceable evidence.
        assert ids, f"No results returned for domain: {domain}"
        assert documents, (
            f"No documents returned for domain: {domain}"
        )
        assert any(
            isinstance(document, str) and document.strip()
            for document in documents
        ), f"No usable document text returned for domain: {domain}"

        assert any(
            isinstance(metadata, dict)
            and metadata.get("source_path")
            for metadata in metadatas
        ), f"No traceable source returned for domain: {domain}"

        print(f"Validation: PASS — {domain}")
        print(f"Results returned: {len(ids)}")
        print()

        # Display each retrieved knowledge result.
        for index, record_id in enumerate(ids):
            metadata = (
                metadatas[index]
                if index < len(metadatas)
                and isinstance(metadatas[index], dict)
                else {}
            )

            document = (
                documents[index]
                if index < len(documents)
                and isinstance(documents[index], str)
                else ""
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            print("-" * 70)
            print(f"Result {index + 1}")
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
            print(f"Distance : {distance}")
            print()

            print("Node preview:")
            print("-" * 70)

            preview = " ".join(document.split())

            if len(preview) > 500:
                preview = preview[:500] + "..."

            print(preview)
            print()

        print()


if __name__ == "__main__":
    run_multi_domain_retrieval_test()