Developed a production-grade AI Data Assistant using a local LLM + Retrieval-Augmented Generation (RAG) architecture. The system ingests messy real-world datasets, profiles data quality issues, validates structure against schema rules using LlamaIndex, applies semantic understanding via embeddings, and performs confidence-aware cleaning decisions. The agent uses deterministic tools for data inspection, vector search for schema grounding, and natural language generation to explain issues and recommended fixes. I validated the entire pipeline using end-to-end testing to ensure safety, stability, non-hallucinated reasoning, and repeatable behavior.”

*Primary Use cases of Agent* :- 

1. AI Agents: The application uses AI algorithms designed specifically for data analysis and quality assessment. These agents are programmed to perform tasks such as identifying missing values, detecting outliers, checking for inconsistencies, and understanding data patterns [1].
2. Upload CSV or other tabular format file: The core functionality begins with the user uploading their structured data files (e.g., CSV, Excel spreadsheets, etc.
3. Detailed insights of the data quality: The AI agents process the data and generate a report that details common data quality issues. This could include:
- `Completeness`: Percentage of missing values in each column.
- `Validity`: Identification of incorrect data types or values outside of expected ranges.
- `Consistency`: Highlighting conflicting information across different rows or columns.
- `Uniqueness`: Reporting duplicate entries.
- `Accuracy`: Are there conflicting records or data entry errors? (e.g., a person listed as living in two different cities simultaneously, or spelling variations like "California" vs. "CA").

4. Suggestions for improvement (fix-recommendations): The system goes beyond just identifying problems. The AI suggests actionable steps to fix the issues, such as:
- "Impute missing values in the 'Age' column with the median value."
- "Remove duplicate customer IDs."
- "Standardize the date format in the 'Date' column to YYYY-MM-DD."

__Core AI & Agent Frameworks / LLM Engineering (Implemented)__

- LangChain (Runnable-based architecture), LlamaIndex (Schema-aware RAG) (RAG, VectorStoreIndex), Ollama (LLM inference, Models: mistral:7b (primary), llama3:8b (evaluated)), Embeddings, Vector Search & Similarity, SequenceMatcher (String Similarity Algorithm), Cosine Similarity (Vector Mathematics).
- Data Engineering : pandas, numpy, Python Standard Library. ML Utilities : scikit-learn.
