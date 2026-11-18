# Human-in-the-Loop Policy

## 1. Purpose

This document defines the Human-in-the-Loop (HITL) policy for the AI Data Assistant Agent.

The policy establishes the boundary between:

```text
Deterministic Finding
        ↓
Recommendation
        ↓
Human Review
        ↓
Approval or Rejection
        ↓
Future Execution
```

The purpose of HITL is to ensure that consequential actions are reviewed by an appropriate human before execution.

---

## 2. Core HITL Principle

The system may automatically detect data-quality evidence and generate structured recommendations.

However, detection and recommendation do not constitute authorization to modify data.

The core principle is:

> The system may recommend an action, but a human must approve consequential remediation before execution.

---

## 3. Deterministic Finding

The deterministic Python pipeline is responsible for identifying dataset-specific evidence.

Examples include:

- missing/dirty values;
- duplicate records;
- logical-rule breaches;
- numerical outliers;
- schema information.

Deterministic findings are the source of truth for dataset-specific evidence.

The LLM must not replace or override deterministic findings.

---

## 4. Decision and Recommendation

The DecisionEngine evaluates deterministic quality evidence and produces structured recommendations.

A recommendation may contain:

```text
recommendation_id
issue_type
severity
priority
recommended_action
review_required
source_evidence
```

The recommendation describes what may need to be done.

It does not constitute permission to execute the action.

---

## 5. Human Review

A human reviewer should evaluate a recommendation before consequential action is taken.

The reviewer should consider:

- the underlying evidence;
- the issue description;
- severity;
- priority;
- recommended action;
- business context;
- potential downstream impact;
- available remediation guidance;
- whether the proposed action is appropriate.

The reviewer should be able to make an informed decision using the evidence presented by the system.

---

## 6. Approval

Approval means that an authorized human has reviewed the recommendation and explicitly permitted the proposed action to proceed.

Approval should be associated with the specific recommendation or action being reviewed.

Approval must not be inferred from:

- silence;
- lack of rejection;
- system-generated severity;
- model confidence;
- automated recommendation;
- previous approval of a different recommendation.

An explicit approval is required where HITL is mandatory.

---

## 7. Rejection

A reviewer may reject a recommendation when:

- the evidence is insufficient;
- the recommendation is incorrect;
- the issue is a legitimate exception;
- the proposed action is inappropriate;
- the business context does not support the action;
- the risk of the proposed action is unacceptable.

A rejected recommendation must not be treated as approved.

Where appropriate, the rejection reason should be recorded for traceability.

---

## 8. Review Required Status

Recommendations may contain a review requirement such as:

```text
review_required = true
```

When review is required, the recommendation must remain pending until an authorized human decision is received.

The system must not treat:

```text
review_required = true
```

as permission to execute the recommendation.

---

## 9. Consequential Actions

Human approval is required before consequential actions such as:

- changing dataset values;
- deleting records;
- merging records;
- inserting records;
- changing columns;
- changing datatypes;
- applying business-rule-driven corrections;
- modifying source data;
- performing other actions that may affect downstream decisions.

The exact approval requirements may depend on organizational governance and the nature of the action.

---

## 10. Non-Consequential Explanations

Not every system response requires human approval.

The system may provide explanatory information such as:

- definitions;
- issue descriptions;
- deterministic findings;
- statistical observations;
- remediation guidance;
- general investigation steps.

Providing an explanation does not constitute execution of a remediation action.

---

## 11. Uncertain Findings

Human review should be used when the system cannot establish the correct action reliably.

Examples include:

- numerical outliers that may be legitimate;
- ambiguous business-rule violations;
- unclear schema changes;
- missing authoritative reference information;
- uncertain replacement values;
- conflicting business rules.

The system should communicate uncertainty rather than presenting an uncertain recommendation as a confirmed correction.

---

## 12. Approval Boundary

The approval boundary is:

```text
Python Detection
      ↓
Deterministic Evidence
      ↓
DecisionEngine
      ↓
Recommendation
      ↓
HITL Review
      ↓
┌───────────────┐
│               │
Approval      Rejection
│               │
↓               ↓
Future        Stop / Review
Execution
```

The current system stops at the recommendation and HITL decision boundary.

Actual remediation execution is a separate future capability.

---

## 13. No Implicit Execution

The system must never interpret a recommendation as an executed action.

For example:

```text
Recommendation:
Remove confirmed duplicate record.
```

does not mean:

```text
Duplicate record removed.
```

The second statement is only valid if an actual remediation component has executed the action and verified the result.

The LLM must not claim that an action was completed when the system only generated a recommendation.

---

## 14. Approval Scope

Approval should apply only to the action and evidence that were reviewed.

A reviewer approving one recommendation does not automatically approve:

- unrelated recommendations;
- additional records;
- additional data modifications;
- future recommendations;
- newly detected issues.

If the proposed action changes materially, additional review may be required.

---

## 15. Evidence Presented for Review

The reviewer should have access to sufficient evidence to understand the recommendation.

Relevant evidence may include:

```text
recommendation_id
issue_type
severity
priority
affected_columns
affected_records
deterministic_findings
source_evidence
recommended_action
review_required
```

The evidence must originate from the deterministic pipeline or approved knowledge sources.

The LLM must not invent evidence for the reviewer.

---

## 16. Auditability

HITL decisions should be traceable.

Where an approval workflow is implemented, the system should record information such as:

```text
recommendation_id
review_status
reviewer
decision
decision_time
decision_reason
approved_action
execution_status
```

The current system does not implement a complete approval audit database.

These fields represent the intended future governance model.

---

## 17. Execution After Approval

In a future remediation-enabled version, an approved recommendation may be passed to a controlled execution component.

The intended sequence is:

```text
Recommendation
      ↓
Human Approval
      ↓
Authorized Execution
      ↓
Deterministic Verification
      ↓
Execution Result
```

Execution should not occur before required approval.

After execution, deterministic validation should be used to verify whether the intended change occurred and whether new quality problems were introduced.

---

## 18. Current System Support

The current system supports:

- deterministic quality findings;
- deterministic DecisionEngine recommendations;
- severity and priority;
- `review_required`;
- HITL-oriented recommendation output;
- read-only dataset analysis.

The current system does not automatically:

- request or record a real human approval;
- modify the dataset;
- execute approved remediation;
- maintain a complete approval audit trail;
- verify executed remediation.

These are future workflow capabilities.

---

## 19. RAG Guidance

RAG may use this policy to:

- explain the purpose of HITL;
- explain approval and rejection;
- explain why consequential actions require review;
- explain the difference between recommendation and execution;
- explain uncertainty and review requirements;
- explain the future execution workflow.

RAG must not:

- approve an action;
- reject an action;
- impersonate a human reviewer;
- interpret silence as approval;
- claim that a recommendation was approved;
- claim that remediation was executed;
- bypass the HITL boundary.

The human reviewer remains the authority for approval decisions.

---

## 20. Key Principle

> Deterministic evidence supports recommendations, recommendations require appropriate human review, and consequential remediation must not be executed without the required human approval.