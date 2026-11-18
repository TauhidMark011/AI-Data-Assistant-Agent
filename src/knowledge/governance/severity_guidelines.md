# Severity Guidelines

## 1. Purpose

This document defines general guidance for interpreting the severity of data-quality issues and recommendations.

Severity describes the potential significance or impact of a data-quality issue.

Severity guidance supports consistent explanation and decision-making.

It does not replace deterministic severity logic implemented by the DecisionEngine.

---

## 2. Severity and Priority

Severity and priority are related but different concepts.

### Severity

Severity describes the potential significance or impact of an issue.

### Priority

Priority describes the order in which an issue or recommendation should receive attention.

A high-severity issue does not necessarily mean that it must always be addressed first without considering other factors.

The deterministic DecisionEngine remains the source of truth for dataset-specific severity and priority outputs.

---

## 3. Severity Factors

Severity may consider factors such as:

- potential business impact;
- number of affected records;
- affected fields;
- downstream impact;
- operational impact;
- financial impact;
- regulatory or compliance impact;
- customer impact;
- data integrity impact;
- likelihood of continued occurrence;
- potential consequences if the issue remains unresolved.

The applicable factors depend on the issue type and business context.

---

## 4. High Severity

A high-severity issue may involve significant potential impact.

Examples may include:

- a major logical or business-rule breach;
- widespread data-quality problems affecting important records;
- an issue that may significantly affect downstream decisions;
- a structural problem that prevents critical processing;
- a data issue with potentially significant financial, regulatory, or customer impact.

High severity should be supported by available evidence and applicable governance criteria.

An issue must not be classified as high severity simply because it appears unusual.

---

## 5. Medium Severity

A medium-severity issue may have meaningful impact but may not represent an immediate or widespread critical problem.

Examples may include:

- a moderate number of affected records;
- a data-quality problem requiring investigation;
- numerical anomalies requiring review;
- issues that may affect downstream analysis;
- problems with a limited but meaningful operational impact.

The actual severity depends on evidence and context.

---

## 6. Low Severity

A low-severity issue may have limited immediate impact.

Examples may include:

- minor formatting inconsistencies;
- limited non-critical data-quality issues;
- issues with low downstream impact;
- observations that require monitoring rather than immediate corrective action.

A low-severity classification does not mean that an issue is irrelevant.

Repeated low-severity issues may indicate a wider process problem.

---

## 7. Statistical Findings

Statistical findings require particular care when assigning severity.

A numerical outlier is evidence of statistical unusualness.

It is not automatically evidence of an incorrect value.

For example:

```text
Numerical outlier detected
        ↓
Statistical observation
        ↓
Investigation required
```

The severity should consider the available evidence and potential impact rather than assuming that every outlier is an error.

---

## 8. Missing and Dirty Values

Severity for missing or dirty values may depend on:

- the number of affected values;
- the affected field;
- whether the field is required;
- downstream dependency;
- business importance;
- whether the missing value prevents processing;
- whether a reliable replacement value exists.

A large count does not automatically establish high severity.

The meaning and impact of the affected field must also be considered.

---

## 9. Structural and Schema Issues

Structural issues may have significant impact when they prevent reliable processing or cause downstream incompatibility.

Severity may consider:

- whether required fields are affected;
- whether datatype changes affect processing;
- whether the issue affects many records;
- whether downstream systems depend on the affected structure;
- whether the change is intentional or unauthorized.

An observed schema difference should not be classified as a severe schema failure without an authoritative expected schema.

---

## 10. Integrity and Logical Issues

Integrity issues may become more significant when they affect:

- uniqueness;
- relationships between records;
- referential integrity;
- financial calculations;
- critical business processes;
- downstream reporting.

A logical-rule breach should be interpreted according to the importance of the affected relationship.

The breach count and affected fields must come from deterministic evidence.

---

## 11. Business-Rule Issues

Business-rule violations may have different levels of severity depending on the business requirement involved.

Factors may include:

- financial impact;
- regulatory requirements;
- contractual requirements;
- operational consequences;
- customer impact;
- number of affected records;
- duration of the problem.

The applicable business rule must be explicitly defined.

The LLM must not invent business impact or severity criteria that are not supported by the available knowledge or evidence.

---

## 12. Evidence Requirements

Severity interpretation must be grounded in available evidence.

Relevant evidence may include:

```text
issue_type
affected_columns
affected_records
breach_count
deterministic_finding
rule_information
business_context
downstream_impact
```

The deterministic pipeline remains the source of truth for dataset-specific findings and counts.

RAG must not:

- invent counts;
- invent affected records;
- invent business impact;
- change deterministic severity;
- create a finding that Python did not detect.

---

## 13. DecisionEngine Authority

The DecisionEngine is responsible for deterministic recommendation decisions based on the available quality evidence.

The knowledge base may explain:

- what severity means;
- factors that can influence severity;
- why an issue may require attention;
- why human review may be required.

The knowledge base must not override the DecisionEngine's dataset-specific output.

If the DecisionEngine reports:

```text
severity = HIGH
```

RAG may explain the meaning of high severity using this document.

It must not change the result to MEDIUM or LOW.

---

## 14. Priority Considerations

Priority may consider:

- severity;
- number of affected records;
- business impact;
- downstream impact;
- urgency;
- recurrence;
- confidence in the finding;
- availability of a practical remediation.

Priority should be determined by the deterministic decision logic where implemented.

RAG may explain the resulting priority but must not independently reorder recommendations.

---

## 15. Human Review and Severity

Severity does not automatically determine whether a recommendation can be executed.

Human review requirements depend on:

- the nature of the recommended action;
- potential consequences;
- uncertainty;
- data modification;
- business impact;
- applicable HITL policy.

A low-severity recommendation may still require human approval if it modifies data.

A high-severity finding may require urgent human attention even when automated remediation is not permitted.

---

## 16. Current System Support

The current system supports deterministic recommendation severity and priority through the DecisionEngine.

Current Phase 4B evidence may include:

```text
severity
priority
recommendation_id
issue_type
review_required
```

The knowledge base provides explanatory guidance around these concepts.

The knowledge layer does not independently calculate or assign dataset-specific severity.

---

## 17. RAG Guidance

RAG may use these guidelines to:

- explain severity levels;
- explain factors that can influence severity;
- explain the difference between severity and priority;
- explain why statistical findings require care;
- explain why business context matters;
- explain why human review may still be required.

RAG must not:

- recalculate severity;
- override DecisionEngine severity;
- invent business impact;
- invent affected-record counts;
- change recommendation priority;
- present general guidance as a dataset-specific finding.

The deterministic DecisionEngine remains authoritative for dataset-specific recommendation severity and priority.

---

## 18. Key Principle

> Severity provides a structured way to describe the potential significance of a data-quality issue, while dataset-specific severity and priority must remain grounded in deterministic evidence and DecisionEngine logic.