# Issue Taxonomy: Accuracy

## 1. Purpose

This document defines the data-quality issues associated with the Accuracy quality pillar.

Accuracy issues concern whether data correctly represents the real-world information, event, measurement, or business condition that it is intended to describe.

The taxonomy provides knowledge for explanation and interpretation.

It does not perform dataset analysis.

---

## 2. Issue Types

The following accuracy-related issues are defined:

- incorrect value;
- numerical anomaly;
- numerical outlier;
- logical inconsistency;
- business-rule violation;
- incorrect reference value;
- measurement error.

Not all issue types listed here are currently detected automatically by the deterministic pipeline.

---

## 3. Incorrect Value

### Definition

An incorrect value is a value that does not correctly represent the information it is intended to describe.

Examples may include:

- incorrect customer information;
- incorrect transaction amount;
- incorrect measurement;
- incorrect date representing an event.

### Interpretation

A value should not be classified as inaccurate only because it appears unusual.

Confirmation of an accuracy problem normally requires:

- a trusted reference;
- source-system verification;
- an established business rule;
- another reliable source of evidence.

### Current System Support

The current deterministic pipeline does not independently establish the real-world correctness of arbitrary values.

This issue type should therefore be treated as a general accuracy concept rather than an automatically confirmed finding.

---

## 4. Numerical Anomaly

### Definition

A numerical anomaly is a numerical observation that differs substantially from the expected pattern of the data.

An anomaly may be identified using statistical or rule-based methods.

### Interpretation

A numerical anomaly is an indicator for investigation.

Possible explanations include:

- genuine exceptional observation;
- unusual business event;
- data-entry error;
- measurement problem;
- incorrect unit;
- transformation issue.

An anomaly should not automatically be classified as an inaccurate value.

### Current System Support

The deterministic quality pipeline currently provides numerical outlier evidence using the IQR method.

The detected outlier count and affected columns must come from deterministic evidence.

---

## 5. Numerical Outlier

### Definition

A numerical outlier is an observation that falls unusually far from the central distribution of a numerical field according to the selected statistical detection method.

The current pipeline uses the Interquartile Range (IQR) method with a configurable multiplier.

### Interpretation

An outlier indicates statistical unusualness.

It does not prove that the value is incorrect.

For example, an unusually high transaction amount may represent:

- a genuine large transaction;
- an exceptional business event;
- a data-entry error.

The value should therefore be reviewed before correction.

### Current System Support

The current deterministic pipeline supports numerical outlier detection.

The evidence includes:

- affected numerical columns;
- detected outlier counts;
- detection method;
- configured IQR multiplier.

RAG must not recalculate or replace these values.

---

## 6. Logical Inconsistency

### Definition

A logical inconsistency occurs when values do not satisfy an explicitly defined logical or mathematical relationship.

For example:

```text
Total = Quantity × Unit Price
```

A record that does not satisfy the defined relationship may be identified as a logical-rule breach.

### Interpretation

A logical inconsistency provides evidence that a defined relationship has not been satisfied.

It does not automatically identify which individual value is incorrect.

Possible causes include:

- incorrect input;
- calculation error;
- incorrect unit;
- transformation problem;
- legitimate exception.

### Current System Support

The deterministic quality pipeline currently supports configured logical-rule validation.

The detected rules and breach counts must come from deterministic evidence.

RAG may explain the relationship but must not independently calculate the number of breaches.

---

## 7. Business-Rule Violation

### Definition

A business-rule violation occurs when data does not satisfy an explicitly defined business requirement.

Examples may include:

- a transaction exceeding an approved limit;
- an invalid business status transition;
- a value violating an approved operational condition.

### Interpretation

A business rule must be explicitly defined before a violation can be confirmed.

The LLM must not invent business rules based only on unusual data.

### Current System Support

The current deterministic pipeline supports configured logical relationships but does not provide a general business-rule engine covering all possible business requirements.

General business-rule validation should therefore be treated as a future capability unless an explicit deterministic rule is implemented.

---

## 8. Incorrect Reference Value

### Definition

An incorrect reference value occurs when a value does not match a trusted reference source that is expected to represent the correct information.

Examples may include:

- incorrect product information;
- incorrect customer information;
- incorrect location information;
- incorrect master-data attributes.

### Interpretation

Accuracy against reference data requires an authoritative reference source.

A value should not be classified as inaccurate simply because it differs from another dataset unless the reference source is known to be authoritative.

### Current System Support

The current deterministic pipeline does not independently perform general reference-data accuracy validation.

This issue type is therefore a future capability unless an authoritative reference source and deterministic comparison rule are introduced.

---

## 9. Measurement Error

### Definition

A measurement error occurs when a recorded measurement does not correctly represent the quantity or condition that was intended to be measured.

Possible causes include:

- instrument problems;
- incorrect measurement procedure;
- incorrect units;
- data-entry errors;
- transformation problems.

### Interpretation

Measurement accuracy normally requires knowledge of the measurement process or a trusted reference.

A statistically unusual measurement is not automatically a measurement error.

### Current System Support

The current deterministic pipeline does not independently verify physical or operational measurements.

This issue type is therefore a future capability unless suitable reference data and deterministic validation rules are introduced.

---

## 10. Evidence and Counts

Dataset-specific accuracy evidence must come from deterministic analysis.

Current supported evidence may include:

```text
numerical_outliers
outlier_detection
logic_breaches
```

RAG must not:

- calculate a new outlier count;
- change the detected outlier count;
- classify every outlier as an error;
- invent logical-rule breaches;
- claim a value is inaccurate without supporting evidence.

If Python reports a numerical outlier, the explanation should describe it as an observation requiring review unless additional evidence confirms an error.

---

## 11. Remediation Considerations

Possible actions include:

- reviewing unusual values;
- checking the source system;
- comparing against trusted reference data;
- validating business rules;
- checking units and measurement procedures;
- correcting confirmed data-entry errors;
- investigating transformation problems.

An outlier should not automatically be deleted or replaced.

Corrections should be based on evidence and appropriate business context.

---

## 12. Human Review

Human review may be required when:

- an unusual value may be a genuine observation;
- the correct value cannot be established automatically;
- trusted reference data is required;
- business context is required;
- changing a value could affect downstream decisions;
- a detected rule breach requires interpretation.

Recommendations involving dataset modification must follow the project's HITL policy.

---

## 13. RAG Guidance

RAG may use this taxonomy to:

- explain the meaning of accuracy issues;
- explain the difference between an anomaly and a confirmed error;
- explain why numerical outliers require investigation;
- explain logical-rule evidence;
- distinguish current capabilities from future capabilities;
- explain possible investigation and remediation approaches.

RAG must not convert a statistical anomaly into a confirmed accuracy error without supporting evidence.

The deterministic evidence remains the source of truth for detected findings.

---

## 14. Key Principle

> An accuracy issue concerns whether data correctly represents the intended real-world information; unusual or statistically abnormal values require investigation but do not automatically prove that the data is wrong.