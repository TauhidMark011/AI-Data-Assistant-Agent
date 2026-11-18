# Remediation Guidance

## 1. Purpose

This document defines guidance for investigating and remediating data-quality issues identified by the deterministic pipeline.

Remediation means taking an appropriate action to address a confirmed or sufficiently understood data-quality problem.

This document provides guidance for recommendations and human decision-making.

It does not modify datasets by itself.

---

## 2. Detection, Recommendation, and Execution

The system must clearly separate three stages:

```text
Detection
    ↓
Recommendation
    ↓
Execution
```

### Detection

Deterministic Python identifies and reports data-quality evidence.

### Recommendation

The DecisionEngine evaluates deterministic evidence and produces structured recommendations.

RAG may provide supporting knowledge about the issue, possible causes, severity, and remediation approaches.

### Execution

Actual dataset modification or other consequential action is separate from detection and recommendation.

The current system does not automatically modify the dataset.

Human approval is required before consequential remediation is executed.

---

## 3. Remediation Should Follow Evidence

Remediation should be based on reliable evidence.

Before recommending a corrective action, consider:

- the detected issue;
- affected fields or records;
- deterministic evidence;
- the likely cause;
- applicable rules;
- business context;
- potential downstream impact;
- whether the proposed action could introduce new errors.

An unusual value should not automatically be corrected.

---

## 4. Confirm the Issue Before Correction

A detected observation does not always mean that data is incorrect.

Examples include:

- numerical outlier;
- unusual transaction;
- legitimate exception;
- rare business event;
- unexpected but valid value.

Where appropriate, the system should recommend investigation before correction.

For example:

```text
Numerical outlier detected
        ↓
Review affected records
        ↓
Check source and business context
        ↓
Confirm whether value is incorrect
        ↓
Recommend correction if justified
```

---

## 5. Missing and Dirty Values

Possible remediation approaches for missing or dirty values include:

- checking the source system;
- correcting known data-entry errors;
- using an approved replacement value;
- obtaining the value from an authoritative source;
- retaining the missing value when it is genuinely unavailable;
- flagging the record for manual review.

Missing values should not automatically be replaced with:

- zero;
- mean;
- median;
- mode;
- an arbitrary default;
- an LLM-generated value.

The appropriate approach depends on the field meaning and approved business rules.

---

## 6. Duplicate Records

Possible remediation approaches for confirmed duplicate records include:

- reviewing the affected records;
- identifying the authoritative record;
- determining whether the records are true duplicates;
- merging records where an approved process exists;
- removing a confirmed duplicate when authorized;
- retaining legitimate repeated transactions.

A repeated record should not automatically be deleted.

The system should distinguish duplicate evidence from the decision to remove or merge records.

---

## 7. Logical-Rule Breaches

For a logical-rule breach, remediation should first establish why the relationship was not satisfied.

Possible actions include:

- reviewing the affected fields;
- checking source values;
- checking calculation logic;
- checking units;
- checking transformation logic;
- confirming whether an approved exception exists;
- correcting confirmed input or transformation errors.

For example:

```text
Total ≠ Quantity × Unit Price
```

does not automatically identify which value is wrong.

The correct field should be established before recommending a correction.

---

## 8. Numerical Outliers

Numerical outliers should normally be investigated before correction.

Possible actions include:

- reviewing the affected record;
- checking the source system;
- checking the transaction or event context;
- checking units;
- comparing against trusted reference information;
- confirming whether the value represents a genuine exceptional event.

An outlier must not automatically be:

- deleted;
- replaced;
- capped;
- winsorized;
- converted to a missing value.

The current pipeline treats outliers as statistical evidence requiring review.

---

## 9. Schema and Structural Issues

Possible remediation approaches for structural issues include:

- checking the source-system schema;
- comparing the dataset with the approved data contract;
- correcting an incorrect export configuration;
- restoring required columns;
- resolving datatype mismatches;
- correcting malformed source records;
- updating an approved schema version when a legitimate change has occurred.

Structural changes should only be made when the intended schema is known.

The system must not invent missing columns or expected datatypes.

---

## 10. Validation and Business-Rule Violations

For a confirmed validation or business-rule violation, possible actions include:

- reviewing the affected record;
- checking the applicable rule;
- confirming the rule version;
- checking for approved exceptions;
- correcting confirmed data-entry errors;
- fixing the upstream process;
- correcting an incorrect transformation;
- updating an incorrectly configured rule.

A rule violation does not automatically establish the root cause.

The remediation should address the actual cause where it can be reliably established.

---

## 11. Remediation Selection

The proposed action should be proportionate to the evidence and potential impact.

Possible recommendation categories include:

```text
INVESTIGATE
CORRECT
REPLACE
REMOVE
MERGE
ESCALATE
MONITOR
NO_ACTION
```

The recommendation category should be supported by the deterministic finding and applicable knowledge.

The LLM must not independently select a consequential remediation action without the required evidence and governance context.

---

## 12. Remediation Priority

Remediation priority may consider:

- severity;
- number of affected records;
- business impact;
- downstream impact;
- regulatory or compliance implications;
- likelihood of continued occurrence;
- confidence in the proposed corrective action.

Priority should come from the deterministic DecisionEngine and applicable governance rules where available.

RAG may explain why an action may be important but must not override deterministic priority decisions.

---

## 13. Source-System and Root-Cause Consideration

Correcting individual records may not resolve the underlying problem.

Possible root causes include:

- source-system errors;
- incorrect data-entry procedures;
- missing validation;
- transformation defects;
- integration problems;
- incorrect business rules;
- process changes;
- schema changes.

Where repeated issues suggest an upstream cause, the recommendation may include investigation of the source or process rather than only correcting individual records.

---

## 14. Dataset Modification Policy

The current system is read-only with respect to the analyzed dataset.

The following actions must not be claimed as completed unless an actual remediation component has executed and verified them:

- changing values;
- deleting records;
- inserting records;
- merging records;
- changing columns;
- changing datatypes;
- rewriting the source file.

The LLM and RAG must never state that remediation was executed when only a recommendation was generated.

---

## 15. Human Approval

Human review and approval are required before consequential remediation is executed.

Human approval may be required when:

- data values will be changed;
- records will be deleted or merged;
- schema will be changed;
- business rules are involved;
- the correct value is uncertain;
- the action may affect downstream decisions;
- the impact is significant.

The recommendation should clearly communicate when human approval is required.

The project's HITL policy is the authoritative governance source for approval requirements.

---

## 16. Remediation Evidence

A remediation recommendation should be traceable to the evidence that produced it.

Relevant information may include:

```text
recommendation_id
issue_type
severity
priority
affected_columns
affected_records
source_evidence
recommended_action
review_required
```

The recommendation must not contain invented counts, records, columns, or findings.

The deterministic evidence remains the source of truth.

---

## 17. Verification After Remediation

If remediation is executed in a future system version, the result should be verified.

Verification may include:

- rerunning deterministic quality checks;
- confirming that the original issue was resolved;
- checking that no new quality issues were introduced;
- comparing before-and-after evidence;
- recording the action and outcome.

A recommendation alone is not evidence that an issue has been resolved.

The current system does not execute or verify dataset remediation.

---

## 18. Current System Support

The current system supports:

- deterministic quality detection;
- deterministic decision-making;
- structured remediation recommendations;
- severity and priority assignment;
- HITL review requirements;
- RAG-based remediation guidance.

The current system does not automatically execute dataset remediation.

Future capabilities may include:

- approved automated corrections;
- remediation execution;
- before-and-after validation;
- remediation audit history;
- rollback;
- remediation approval workflows.

These capabilities must not be represented as currently implemented.

---

## 19. RAG Guidance

RAG may use this document to:

- explain possible remediation approaches;
- explain why investigation may be required;
- explain the difference between recommendation and execution;
- explain remediation risks;
- explain human approval requirements;
- explain verification requirements;
- provide issue-specific remediation guidance.

RAG must not:

- modify the dataset;
- claim that remediation was executed;
- invent corrective values;
- invent affected records;
- invent issue counts;
- override deterministic recommendations;
- bypass HITL requirements;
- recommend consequential changes without appropriate evidence.

The deterministic evidence and DecisionEngine remain authoritative for dataset-specific findings and recommendations.

---

## 20. Key Principle

> Remediation should address a confirmed or sufficiently understood data-quality problem, and consequential changes must remain separate from detection and recommendation and require appropriate human approval.