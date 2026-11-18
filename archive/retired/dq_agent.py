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
from utils import load_schema_by_dataset
import json

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

        file_path = "data/dirty_cafe_sales.csv"
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
        schema_issues = validate_schema(df, file_path)

        #Retrieve schema rules using RAG
        schema_nodes = schema_retriever.retrieve(
            "What are the required columns, data types, allowed value ranges, and business constraints for this dataset? Include what is expected vs invalid."
            )
        schema_json = load_schema_by_dataset(file_path)
        # schema_context = "\n".join([n.text for n in schema_nodes])
        schema_context = json.dumps(schema_json, indent=2)
        
        #logic to extract column types and constraints dynamically(Dynamically extract value expectations)
        value_expectations = ""
        for node in schema_nodes:
            try:
                 j = json.loads(node.text)
                 if "column_types" in j: 
                      for col, dtype in j["column_types"].items():
                           value_expectations += f"- Column '{col}' should be of type {dtype}.\n"
                 if "value_constraints" in j:
                     for col, rule in j["value_constraints"].items():
                         constraint = []
                         if "min" in rule:
                            constraint.append(f"min = {rule['min']}")
                         if "max" in rule:
                            constraint.append(f"max = {rule['max']}")
                         if constraint:
                            value_expectations += f"- Column '{col}' must satisfy: {', '.join(constraint)}\n"
            except Exception:
                continue

        # -------------------------
        # LLM reasoning prompt (GROUNDED) & explanation, Inject explicit expectation logic for the LLM
        # ------------------------- (Augmented Prompt Block)
        prompt = f"""
You are a Data Quality Agent responsible for identifying and explaining data quality issues in a structured dataset.

Your knowledge base:
Schema Rules (Ground Truth):
{schema_context}

Detected Dataset Issues:
- Null values: {nulls}
- Duplicates: {duplicates}
- Schema violations: {schema_issues}

Based on the schema, validates: 
{value_expectations}

Also verify:
- Are there encoding issues in column names?
- Are categorical columns consistent with expected categories?
- Are there malformed rows or unexpected delimiters?
- Which rows/columns show high nulls or format problems?
- Are any values malformed 
- Identify non-standard or locale-specific symbols that may impact parsing.
- Suggest clear fixes or transformations.
- If column names appear malformed, attempt to match them to the closest required column in the schema using fuzzy logic. Assume minor symbol or encoding mismatches.

Note: A mismatch between value types and expected data types is not a reason to rename a column. Rename column headers only when the column name itself appears malformed or misaligned with the schema.

Your Task:
1. Identify which issues violate schema rules, including:
   - Missing required columns
   - Columns with incorrect data types
   - Values outside allowed ranges
   - Unexpected symbols or formatting in numeric/date columns
   - Fields that should be pure numeric but contain text/symbols
   - Float fields that are improperly formatted
   - Columns with high % of null values (highlight the most affected ones)
   - Rows that contain missing data in required fields (mention row patterns if identifiable)

2. Clearly classify issues as:
   - Critical → violates schema or logic
   - Warning → suspicious, potentially acceptable

3. Recommend safe corrective actions, such as:
   - Recast or clean data types (e.g., convert float to string if required by schema)
   - Impute null values using appropriate methods
   - Remove malformed rows if they violate multiple schema rules
   - Suggest header renaming **only** if the column name itself is corrupted or misencoded (e.g., "Prïce" instead of "Price")
   
Constraints:
- Use only the schema rules provided above
- Do not invent assumptions or guess column meanings

Do NOT invent rules. Use only the schema context.
Output your analysis in a detailed and structured way.
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content

    return RunnableLambda(agent_logic)
