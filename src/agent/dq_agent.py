#agent/ → reasoning + control flow
#Combines tools + RAG + LLM reasoning
"""
dq_agent.py

Phase 1: Runnable-based Data Quality Agent
- Uses Local LLM (Llama3, mistral via Ollama)
- Uses Python tools for data quality checks
- Produces human-readable explanations
"""
"""
Phase 2 Data Quality Agent
- Uses schema rules via LlamaIndex (RAG)
- Performs schema-aware validation
- Explains violations using LLM reasoning
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda

from tools.data_quality import (
    load_csv,
    check_nulls,
    check_duplicates,
    basic_stats #descriptive statistics
)
from tools.schema_validation import validate_schema
from rag.schema_index import load_schema_index
from llama_index.llms.ollama import Ollama

# =========================
# Runnable-Based Agent
# =========================

def create_agent():
    """
    Phase 1 Data Quality Agent

    Responsibilities:
    - Read dataset
    - Run data quality checks (nulls, duplicates, stats)
    - Ask LLM to explain issues in plain English
    - Validates structure against schema
    - Uses RAG to explain WHY issues matter
    """

    #LangChain LLM (agent reasoning)
    llm = ChatOllama(
        model="mistral:7b",
        temperature=0
    )
#     #LlamaIndex LLM (RAG query engine)
#     schema_llm = Ollama(
#     model="mistral:7b",
#     temperature=0
# )

    #Load schema knowledge index (RAG memory)
    schema_index = load_schema_index()
    #Create retriever (no llm involved)
    schema_retriever = schema_index.as_retriever(similarity_top_k=3)

    def agent_logic(user_input: str):
        """
        Agent execution logic.
        In Phase 1, tool execution order is deterministic
        for clarity and learning purposes.
        Agent execution flow:
        1. Load dataset
        2. Run deterministic checks
        3. Validate schema
        4. Ask LLM to reason using retrieved schema rules
        """

        file_path = "data/messy_IMDB_dataset.csv"

        # -------------------------
        # Tool execution (Python)
        # -------------------------
        df = load_csv(file_path)

        #Phase 1 checks
        nulls = check_nulls(df)
        duplicates = check_duplicates(df)
        stats = basic_stats(df)
        # Schema validation (Phase 2 logic)
        # -------------------------
        schema_issues = validate_schema(df)

        #Retrieve schema rules using RAG
        schema_nodes = schema_retriever.retrieve(
            "What are the required columns and constraints for this dataset?"
            )
        schema_context = "\n".join([n.text for n in schema_nodes])
        # -------------------------
        # LLM reasoning prompt (GROUNDED) & explanation
        # -------------------------
        prompt = f"""
You are a Data Quality Agent.

Schema Rules (Ground Truth):
{schema_context}

Detected Issues:
- Null values: {nulls}
- Duplicates: {duplicates}
- Schema violations: {schema_issues}

Explain:
1. Which issues violate schema rules
2. Why they are critical or warnings
3. Safe corrective actions

Do NOT invent rules. Use only the schema context.
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content

    return RunnableLambda(agent_logic)
