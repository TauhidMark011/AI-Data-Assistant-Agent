#rag/ → knowledge grounding
"""schema_index.py
Creates a vector index over schema documents
using LOCAL embeddings (no OpenAI).
"""
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
#LlamaIndex: Searches vectors, Returns relevant schema text, Feeds it to the LLM. (Indexes rules (RAG memory))
from llama_index.embeddings.ollama import OllamaEmbedding

def load_schema_index():
    """
    Loads schema documents and builds a vector index
    using Ollama embeddings to avoid OpenAI dependency.
    """
    docs = SimpleDirectoryReader("src/schemas").load_data()
    #Explicitly use local embeddings (no API, no cost)
    embed_model = OllamaEmbedding(
        model_name="nomic-embed-text"
    ) 
    #Build vector index with Ollama embeddings
    index = VectorStoreIndex.from_documents(
        docs,
        embed_model=embed_model
        ) #Reads our schema files as text, Breaks them into chunks,
    #Converts chunks → embeddings (vectors), Stores them in a local in-memory vector index, Enables semantic search. 
    return index

#Optional - *Use a local Huggingface embedding model, LlamaIndex will load a small sentence-transformer model, Embeddings will run locally, Vectors stored in memory. : Encountered error while generating package metadata.╰─> numpy