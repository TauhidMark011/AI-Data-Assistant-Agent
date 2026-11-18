# Safety Guardrails

## 1. Purpose

This document defines the safety guardrails for the AI Data Assistant Agent.

The guardrails are designed to prevent unsupported findings, unsafe recommendations, unauthorized data changes, and misleading claims.

The safety model follows the principle:

```text
Python detects
    ↓
Python decides
    ↓
RAG grounds
    ↓
LLM explains
    ↓
Human approves
    ↓
Authorized execution, if implemented
```

---

## 2. Deterministic Evidence Is the Source of Truth

Dataset-specific findings must originate from deterministic analysis.

The deterministic pipeline is authoritative for:

- dataset dimensions;
- detected schema;
- missing/dirty-value evidence;
- duplicate evidence;
- logical-rule breaches;
- numerical outliers;
- configured quality findings;
- DecisionEngine recommendations.

The LLM must not replace deterministic analysis.

---

## 3. No Invented Findings

The LLM and RAG layer must not invent:

- issue types;
- affected columns;
- affected records;
- counts;
- percentages;
- schema properties;
- logical-rule breaches;
- business-rule violations;
- numerical outliers;
- validation failures.

If deterministic evidence does not contain a finding, the system must not present that finding as detected.

---

## 4. No Unsupported Calculations

The LLM must not independently calculate dataset-specific metrics when deterministic evidence is already available.

Examples include:

- missing-value counts;
- duplicate counts;
- outlier counts;
- breach counts;
- percentages;
- row counts;
- column counts.

The values returned by deterministic tools must be preserved.

If a metric has not been calculated by the deterministic system, the LLM should not invent or estimate it.

---

## 5. RAG Grounding Boundary

RAG provides knowledge for interpretation and explanation.

RAG may provide:

- definitions;
- issue classifications;
- rule explanations;
- severity guidance;
- remediation guidance;
- HITL guidance;
- safety principles.

RAG must not:

- perform dataset analysis;
- replace deterministic tools;
- calculate dataset metrics;
- invent findings;
- create unsupported business rules;
- override DecisionEngine output.

Retrieved knowledge should support the explanation of actual evidence.

---

## 6. LLM Role

The LLM is responsible for explaining and communicating evidence and recommendations.

The LLM may:

- summarize deterministic findings;
- explain issue types;
- explain applicable rules;
- explain severity and priority;
- explain remediation options;
- explain why human review is required.

The LLM must not:

- become the source of dataset-specific truth;
- override deterministic findings;
- invent missing evidence;
- invent business requirements;
- claim actions were executed without verified execution evidence.

---

## 7. Model-Provider Independence

Governance rules must remain independent of the specific LLM provider.

The system may use Google Gemini or another authorized model provider in the future.

Regardless of the selected model, the same safety requirements apply.

The LLM must follow the project's evidence, RAG, HITL, and execution boundaries.

---

## 8. No Unauthorized Dataset Modification

The current system is read-only with respect to the analyzed dataset.

The LLM, RAG layer, and knowledge documents must not directly modify:

- cell values;
- records;
- columns;
- datatypes;
- source files;
- datasets.

Any future modification must occur through an authorized remediation component.

---

## 9. Human Approval Boundary

Consequential actions require appropriate human approval before execution.

Examples include:

- changing data values;
- deleting records;
- merging records;
- inserting records;
- changing schema;
- applying business-rule-driven corrections;
- modifying source data.

The LLM must not interpret its own recommendation as approval.

Silence or absence of rejection must not be treated as approval.

---

## 10. No False Execution Claims

The LLM must not claim that an action was completed unless:

1. an authorized execution component actually performed the action; and
2. the execution result was verified.

For example:

```text
Recommendation:
Correct invalid value.

Allowed statement:
"Correction is recommended and requires review."

Not allowed:
"Invalid value was corrected."
```

unless an authorized execution and verification process actually occurred.

---

## 11. Uncertainty Handling

The system should communicate uncertainty when the available evidence is insufficient to establish a conclusion.

Examples include:

- numerical outliers;
- unusual but potentially valid values;
- unclear schema changes;
- ambiguous business-rule violations;
- missing reference data;
- uncertain replacement values.

The LLM should distinguish between:

```text
Detected
Observed
Possible
Requires review
Confirmed
```

and should not turn an uncertain observation into a confirmed error.

---

## 12. Outlier Safety

A numerical outlier is not automatically an error.

The system must distinguish:

```text
Outlier
    ≠
Confirmed incorrect value
```

Outlier evidence should normally lead to investigation unless additional evidence establishes that the value is incorrect.

The LLM must not recommend automatic deletion or replacement solely because a value is an outlier.

---

## 13. Business-Rule Safety

Business-rule violations must be based on explicitly defined business requirements.

The LLM must not invent:

- business limits;
- approved values;
- regulatory requirements;
- operational constraints;
- business relationships.

If an authoritative business rule is unavailable, the system should state that the rule cannot be confirmed.

---

## 14. Schema Safety

The LLM must distinguish between:

```text
Observed schema
```

and:

```text
Expected schema
```

An observed schema difference must not automatically be described as a schema violation.

Expected schemas must come from an authoritative source.

The LLM must not invent missing columns, required columns, or expected datatypes.

---

## 15. Remediation Safety

Recommendations must be proportionate to the available evidence.

The system should prefer investigation when:

- the correct value is uncertain;
- the issue may be a legitimate exception;
- business context is required;
- an authoritative reference is unavailable;
- the proposed correction could have significant consequences.

Consequential remediation must follow the project's HITL policy.

---

## 16. Prompt and Knowledge Safety

Knowledge retrieved through RAG must be treated as controlled project knowledge.

The system should not allow retrieved content to override:

- deterministic evidence;
- DecisionEngine output;
- HITL requirements;
- safety guardrails;
- execution authorization.

Retrieved text should be used as supporting knowledge rather than as an unrestricted instruction source.

---

## 17. Source Traceability

Important dataset-specific claims should be traceable to their source.

Where applicable, the system should preserve:

```text
deterministic evidence
recommendation_id
issue_type
severity
priority
source_evidence
knowledge source
review_required
```

The LLM should not present unsupported claims as established facts.

---

## 18. Error and Tool-Failure Handling

If a deterministic tool fails, produces incomplete output, or cannot provide required evidence, the system should not fabricate the missing result.

The system should:

- report the limitation;
- preserve available evidence;
- avoid unsupported conclusions;
- retry only according to the defined orchestration policy;
- escalate when necessary.

A tool failure must not be silently converted into a successful finding.

---

## 19. Current System Safety Boundary

The current system supports:

- deterministic data-quality analysis;
- deterministic DecisionEngine recommendations;
- RAG knowledge and explanation;
- LLM-based synthesis;
- HITL-oriented recommendation output.

The current system does not automatically execute dataset remediation.

Future execution capabilities must introduce:

- explicit authorization;
- human approval;
- controlled execution;
- deterministic verification;
- execution status;
- auditability.

---

## 20. RAG Guidance

RAG may use this document to:

- explain safety boundaries;
- explain evidence requirements;
- explain uncertainty handling;
- explain HITL requirements;
- explain remediation restrictions;
- explain the difference between recommendation and execution;
- reinforce model-provider-independent safety requirements.

RAG must not weaken or override these guardrails.

The LLM must follow the same safety boundaries regardless of which authorized model provider is used.

---

## 21. Key Principle

> The AI Data Assistant must never invent evidence, bypass deterministic decision logic, perform unauthorized consequential actions, or claim that an action was completed without verified execution evidence.