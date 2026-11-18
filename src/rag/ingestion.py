"""
Deterministic Markdown ingestion for the AI Data Assistant Agent.

Responsibilities:
    1. Discover Markdown files under src/knowledge/
    2. Read their contents without modifying them
    3. Convert each file into a LlamaIndex Document
    4. Attach deterministic source metadata

This module intentionally does NOT:
    - generate embeddings
    - call Gemini
    - create/use Chroma
    - perform retrieval
    - call an LLM
    - analyze datasets
    - modify knowledge files
"""

from pathlib import Path

from llama_index.core import Document

from .config import KNOWLEDGE_DIR

# ============================================================================
# MARKDOWN DISCOVERY
# ============================================================================

#Deterministic means: Given the same input, the process produces the same result.
def discover_markdown_files() -> list[Path]:
    """
    Discover all Markdown files under the frozen knowledge directory.

    Returns:
        A deterministically sorted list of Markdown file paths.
    """

    if not KNOWLEDGE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge directory does not exist: {KNOWLEDGE_DIR}"
        )

    markdown_files = [
        path
        for path in KNOWLEDGE_DIR.rglob("*.md")
        if path.is_file()
    ]

    return sorted(markdown_files)


# ============================================================================
# DOCUMENT LOADING
# ============================================================================

def load_knowledge_documents() -> list[Document]:
    """
    Load all discovered Markdown files into LlamaIndex Documents.

    Each Document receives deterministic metadata describing its source.

    Returns:
        A list of LlamaIndex Document objects.
    """

    markdown_files = discover_markdown_files()

    documents: list[Document] = []

    for file_path in markdown_files:
        text = file_path.read_text(
            encoding="utf-8"
        )

        relative_path = file_path.relative_to(KNOWLEDGE_DIR)

        if len(relative_path.parts) > 1:
            category = relative_path.parts[0]
        else:
            category = "root"

        metadata = {
            "source_path": relative_path.as_posix(),
            "document": file_path.name,
            "category": category,
            "file_type": "markdown",
        }

        document = Document(
            text=text,
            metadata=metadata,
        )

        documents.append(document)

    return documents


# ============================================================================
# LOCAL TEST
# ============================================================================

if __name__ == "__main__":
    documents = load_knowledge_documents()

    print("=" * 70)
    print("KNOWLEDGE INGESTION TEST")
    print("=" * 70)

    print(f"Knowledge directory : {KNOWLEDGE_DIR}")
    print(f"Markdown files      : {len(documents)}")
    print()

    for index, document in enumerate(documents, start=1):
        print(f"[{index:02d}] {document.metadata['source_path']}")
        print(f"     Category : {document.metadata['category']}")
        print(f"     Type     : {document.metadata['file_type']}")
        print(f"     Characters: {len(document.text)}")
        print()