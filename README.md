# 🤖 DataAssistant AI-Agent
### Automated Data Quality Checker — Detect → Explain → Decide → Fix

> *"Quality becomes enforceable, not just observable."*

An intelligent, modular multi-agent system that automatically profiles, cleans, and validates CSV datasets to ensure they are analytics- and ML-ready. It uses schema-aware RAG and confidence-based decisions to fix errors, nulls, and duplicates, while generating structured reports. The system is powered by LLMs, LangChain, LlamaIndex, and CrewAI across a structured, phase-wise architecture.

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Why This Is a True AI Agent](#-why-this-is-a-true-ai-agent)
- [System Architecture](#-system-architecture)
- [Phase-wise Implementation](#-phase-wise-implementation)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Capabilities by Phase](#-capabilities-by-phase)
- [Roadmap](#-roadmap)

---

## Project Overview

**Data Assistant AI-Agent** is a production-grade, autonomous data quality pipeline. It accepts a dataset (CSV initially), runs multi-dimensional quality checks, reasons about the problems using a local LLM, and delivers a structured, human-readable audit report.

The core engineering principle driving the entire pipeline:

```
Detect → Explain → Decide → Fix
```

**What the agent does:**

- Ingests CSV / Parquet datasets robustly (encoding + delimiter auto-detection)
- Detects null values, duplicate records, schema mismatches, outliers, and logic breaches
- Reasons about issues using an LLM (local via Ollama — no cloud dependency)
- Grounds responses using RAG (LlamaIndex) to prevent hallucination
- Applies confidence-aware cleaning: auto-fix safe issues, flag risky ones, block unsafe ones
- Delivers a structured Markdown audit report via CLI

---

__*How It Works*__ :-

<img width="1097" height="958" alt="mermaid-diagram" src="https://github.com/user-attachments/assets/aad1c423-bb36-43b9-83f4-9103124ee71f" />

## Why This Is a True AI Agent

| Requirement | Status |
|---|---|
| Dynamic reasoning | ✅ |
| Tool modularity | ✅ |
| RAG grounding | ✅ |
| Safety guardrails | ✅ |
| Industry-aligned architecture | ✅ |

The system: **understands context** (RAG), **evaluates confidence**, **makes decisions**, **explains reasoning**, and **avoids unsafe actions**. That is the definition of an autonomous agent in production AI — not a script dressed up as AI.

---

## System Architecture

```
User (CLI / Future UI)
   │
   │  Natural Language Instruction
   │  ("Check data quality of sales.csv")
   ▼
────────────────────────────────────────────
  AI AGENT ORCHESTRATION LAYER
────────────────────────────────────────────
   │
   ├── LangChain  (Agent Controller)
   │     · Understands user intent
   │     · Decides which tool/agent to call
   │     · Maintains reasoning flow
   │
   ├── CrewAI  (Multi-Agent Coordinator)      ← Phase 4
   │     · Data Loader Gatekeeper
   │     · Schema Mapping Specialist
   │     · Data Forensic Transcriptionist
   │     · Final Verification Automaton
   │
   └── LlamaIndex  (Knowledge + RAG Layer)
         · Data quality rules
         · Schema definitions
         · Business logic & past issue logs
   │
   ▼
────────────────────────────────────────────
  EXECUTION & TOOL LAYER
────────────────────────────────────────────
   │
   ├── Python Tools
   │     · pandas  — profiling, nulls, duplicates
   │     · numpy   — IQR outlier detection
   │     · statistics — numeric anomaly scoring
   │
   ├── File System
   │     · CSV / Parquet input
   │
   └── Optional (Future)
         · SQL / DuckDB
         · Azure Blob Storage / AWS S3
   │
   ▼
────────────────────────────────────────────
  OUTPUT & RESPONSE LAYER
────────────────────────────────────────────
   │
   ├── Structured JSON metrics (evidence-locked)
   ├── Natural Language Explanation (LLM-generated)
   └── Confidence-tagged fix recommendations

   ▼
   User receives:
   ✔ Data Quality Audit Report (Markdown)
   ✔ Human-readable issue explanations
   ✔ Recommended + blocked actions
```

---

## 🔄 Phase-wise Implementation

| Phase | What Is Built | Architecture Layer |
|---|---|---|
| **Phase 1** | LangChain agent — ingestion, nulls, duplicates, structural anomalies | Agent Controller |
| **Phase 2** | LlamaIndex RAG — schema-aware validation, embedding-based rule retrieval | Knowledge Layer |
| **Phase 3.1** | Column normalization (embedding similarity + confidence scoring) | Intelligent Cleaning |
| **Phase 3.2** | Numeric cleaning — symbols (`$`, `,`), units, safe casting | Intelligent Cleaning |
| **Phase 3.3** | Date normalization & multi-format enforcement | Intelligent Cleaning |
| **Phase 3.4** | Text & categorical normalization — analytics-ready output | Intelligent Cleaning |
| **Phase 3.5** | Semantic typo correction via embeddings + cosine similarity | Intelligent Cleaning |
| **Phase 3.6** | Confidence-aware orchestration — auto-fix / suggest / block | Orchestration |
| **Phase 3.7** | Structured agent output parsing — final CLI report | Output Layer |
| **Phase 4** | CrewAI multi-agent pipeline — 4 specialized sequential agents | Multi-Agent Orchestration |

### Framework Roles

 **LangChain** — *Agent Brain & Decision Maker*
Receives instructions, interprets intent via LLM, decides which tools and agents to invoke, maintains the full reasoning loop.

 **LlamaIndex** — *Knowledge + RAG Layer*
Stores and retrieves data quality rules, schema expectations, and validation policies. Grounds LLM responses — prevents hallucination.

 **CrewAI** — *Multi-Agent Task Manager*
Splits work across four specialized agents. Coordinates sequential execution with evidence-locked outputs and guardrail verification.

**Mastra.ai** – *Architecture guidance & inspiration* 

---

## Tech Stack

| Category | Technology |
|---|---|
| **Agent Frameworks** | LangChain, LlamaIndex, CrewAI 1.9.0 |
| **LLM (Local)** | Ollama — `llama3.2:3b`, `mistral:7b` |
| **Embeddings** | `nomic-embed-text` (local, via Ollama) |
| **Data Processing** | pandas 2.2.3, numpy, pyarrow |
| **Vector Search** | LlamaIndex VectorStoreIndex |
| **Language** | Python 3.12 |
| **Config** | `python-dotenv` |
| **Pinned Dependencies** | `pydantic==2.11.9`, `openai==1.83.0`, `pandas==2.2.3` |

---

## Project Structure

```
DataAssistant_AI-Agent/
├── src/
│   ├── agent/
│   │   └── validation_agent.py        # Phase 3.7 LangChain agent
│   ├── agent_output/
│   │   ├── agent_output_parser.py     # Structured output parsing
│   │   └── structured_report.py       # CLI report renderer
│   ├── data/
│   │   ├── dirty_cafe_sales.csv       # Primary test dataset
│   │   ├── messy_IMDB_dataset.csv
│   │   └── sales.csv
│   ├── orchestration/
│   │   └── crew/
│   │       ├── crew.py                # Phase 4 — CrewAI multi-agent controller
│   │       └── tools/
│   │           ├── file_tool.py       # DataLoadTool
│   │           ├── schema_tool.py     # SchemaInferenceTool
│   │           └── quality_tool.py    # QualityCheckTool (IQR + math breach detection)
│   ├── rag/
│   │   └── schema_index.py            # LlamaIndex RAG setup
│   └── schemas/                       # Data quality rule documents
├── main.py                            # Master pipeline entry point
├── DataAssistantAgent_Overall_flow.ipynb
├── .env                               # API keys / config (not committed)
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com/) installed and running locally
- Required Ollama models pulled:

```bash
ollama pull llama3.2:3b
ollama pull mistral:7b          # Phase 2 LangChain agent
ollama pull nomic-embed-text    # Phase 2 RAG embeddings
```

- Git

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/DataAssistant_AI-Agent.git
cd DataAssistant_AI-Agent

# 2. Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 3. Install pinned dependencies
pip install -r requirements.txt

# 4. Verify critical package versions
python -c "import pydantic, crewai, pandas as pd; print(pydantic.__version__, crewai.__version__, pd.__version__)"
# Expected: 2.11.9  1.9.0  2.2.3

# 5. Configure environment
cp .env.example .env
# Edit .env — set OPENAI_API_KEY if using OpenAI; leave blank for Ollama-only

# 6. Confirm Ollama is running
ollama list
```

> **Note:** The project is designed to run fully locally via Ollama. No OpenAI API key is required for local execution.

---

## Usage

### Phase 3.7 — LangChain Validation Agent (Single Agent)

```bash
cd DataAssistant_AI-Agent
python main.py
```

**What runs:** Full LangChain validation pipeline → structured CLI report with null issues, malformed columns, auto-fixes, suggested fixes, blocked fixes, and NLG explanations.

---

### Phase 4 — CrewAI Multi-Agent Pipeline

```bash
cd DataAssistant_AI-Agent
python -m src.orchestration.crew.crew
```

**What runs:** Four specialized agents execute sequentially:

1. **Data Loader Gatekeeper** — confirms file existence, extracts row/column metadata
2. **Schema Mapping Specialist** — infers column types, produces JSON schema blueprint
3. **Data Forensic Transcriptionist** — runs full quality audit (nulls, duplicates, outliers, logic breaches), produces evidence-locked JSON
4. **Final Verification Automaton** — cross-checks report against tool output, corrects any LLM hallucinations, delivers final verified Markdown report

**Expected output:**

```
=== Launching Phase 4: CrewAI DQ Pipeline ===
[OK] Resolved path: D:\DataAssistant_AI-Agent\src\data\dirty_cafe_sales.csv

## Final Verified Data Quality Audit Report with Seal of Approval

- **Total Records**: 1000
- **Total Nulls**: 347

| Pillar       | Finding                        | Remediation        |
|:-------------|:-------------------------------|:-------------------|
| Accuracy     | 23 outliers in `unit_price`    | `Check outliers`   |
| Consistency  | 12 logic breaches (qty*price)  | `Fix math`         |
```

---

## Capabilities by Phase

| Phase | Capability |
|---|---|
| Phase 1 ✅ | Robust CSV ingestion (encoding + delimiter detection) |
| Phase 1 ✅ | Null value detection |
| Phase 1 ✅ | Duplicate record detection |
| Phase 1 ✅ | Structural anomaly detection (`Unnamed:*` columns, trailing delimiters) |
| Phase 1 ✅ | Plain English explanations + fix suggestions |
| Phase 2 ✅ | Schema-aware validation via RAG (LlamaIndex) |
| Phase 2 ✅ | Embedding-based semantic mismatch detection |
| Phase 2 ✅ | Hallucination prevention via retrieved rule grounding |
| Phase 3 ✅ | Column normalization with confidence scoring |
| Phase 3 ✅ | Numeric cleaning (symbols, units, safe casting) |
| Phase 3 ✅ | Date normalization & multi-format enforcement |
| Phase 3 ✅ | Semantic typo correction via cosine similarity |
| Phase 3 ✅ | Confidence-aware orchestration (auto-fix / suggest / block) |
| Phase 4 ✅ | CrewAI 4-agent sequential pipeline |
| Phase 4 ✅ | Evidence-locked JSON reporting (anti-hallucination) |
| Phase 4 ✅ | Guardrail agent with final verification |

---

## 🗺 Roadmap

- [ ] Integrate Phase 4 CrewAI execution into `main.py` master pipeline
- [ ] FastAPI interface — expose pipeline as REST endpoints
- [ ] Streamlit dashboard — visual data quality report UI
- [ ] PySpark support — large-scale dataset profiling
- [ ] DuckDB integration — in-process SQL quality checks
- [ ] Cloud storage connectors — Azure Blob / AWS S3 input
- [ ] OpenAI / HuggingFace provider swap — vendor-neutral LLM layer
- [ ] Explainable diff — before vs after cleaning view
- [ ] Human-in-the-loop approval — confidence threshold gate before applying fixes

---

## Key Engineering Principles

**Defensive tool design** — every CrewAI tool implements `_resolve_path()` with hardcoded fallback. Small LLMs (llama3.2:3b) sometimes call tools without properly passing arguments; the guard ensures the pipeline never fails silently.

**Evidence-locked reporting** — the `QualityCheckTool` pre-calculates all metrics and locks them into a structured JSON before the LLM sees them. The guardrail agent cross-verifies the final report against raw tool output, correcting any hallucinated numbers.

**Vendor-neutral LLM layer** — the architecture supports OpenAI, HuggingFace, or local Ollama models by swapping the `LLM(model=...)` parameter. No cloud dependency for local execution.

**Self-contained path resolution** — all scripts resolve their own location via `Path(__file__).resolve()`, making the project immune to CWD and `PYTHONPATH` variations.

---

## 📄 License
MIT License — see `LICENSE` for details.

---

*Built from scratch. Debugged at midnight. Documented with purpose.*

__Author__
:- *Tauhid Alam* | 
Data Engineer | AI Enthusiast | Building Intelligent Solutions
