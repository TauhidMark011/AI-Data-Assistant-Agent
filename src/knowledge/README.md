# Knowledge Contract v1

## 1. Purpose

The `src/knowledge/` directory contains the authoritative knowledge used by the RAG layer of the AI Data Assistant Agent.

This knowledge is used to:

- explain data-quality concepts;
- classify detected issues into defined quality categories;
- provide severity guidance;
- provide remediation guidance;
- explain governance and human-in-the-loop requirements;
- provide grounded context for the LLM.

The knowledge layer does not perform data analysis.

Deterministic Python tools remain the source of truth for dataset evidence.

---

## 2. Core Architecture Principle

The project follows this execution model:

> **Python detects → Python decides → RAG grounds → LLM explains → Human approves**

Each layer has a separate responsibility.

### Python

Python performs deterministic dataset analysis.

Examples:

- record counts;
- column information;
- missing/dirty value counts;
- duplicate detection;
- logical-rule checks;
- numerical outlier detection;
- schema-related evidence.

Python-generated evidence is authoritative for the current dataset.

### Decision Engine

The Decision Engine converts deterministic evidence into structured recommendations.

It determines:

- detected issue type;
- severity;
- priority;
- recommended action;
- whether human approval is required.

The Decision Engine does not modify the dataset.

### RAG / Knowledge Layer

RAG provides grounded domain knowledge.

It may provide:

- definitions;
- quality-pillar explanations;
- issue-taxonomy descriptions;
- validation guidance;
- remediation guidance;
- severity guidance;
- governance rules;
- HITL requirements.

RAG does not calculate dataset evidence.

### LLM

The LLM explains the deterministic evidence using retrieved knowledge.

The LLM may:

- summarize findings;
- explain why an issue matters;
- explain recommended actions;
- provide human-readable guidance.

The LLM must not invent dataset findings.

### Human

Human approval remains required where defined by the Decision Engine.

The AI assistant must not silently modify production data.

---

## 3. Knowledge Scope

The knowledge base is organized into the following areas:

```text
knowledge/
├── pillars/
├── taxonomy/
├── rules/
├── remediation/
├── governance/
└── README.md