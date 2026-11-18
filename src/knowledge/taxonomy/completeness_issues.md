# Issue Taxonomy: Completeness

## 1. Purpose

This document defines the data-quality issues associated with the Completeness quality pillar.

Completeness issues concern missing, unavailable, or unusable required information.

The taxonomy provides knowledge for explanation and interpretation.

It does not perform dataset analysis.

---

## 2. Issue Types

The following completeness-related issues are defined:

- missing value;
- dirty or missing-value token;
- blank value;
- missing required field;
- missing record;
- incomplete record.

Not all issue types listed here are currently detected automatically by the deterministic pipeline.

---

## 3. Missing Value

### Definition

A missing value occurs when a field does not contain usable information where a value is expected.

Examples include:

- empty field;
- `NULL`;
- `N/A`;
- `NONE`;
- `NAN`;
- another configured missing-value representation.

### Interpretation

A missing value indicates that information is unavailable or not represented as a usable value.

It does not by itself establish why the information is missing.

Possible causes include:

- incomplete data entry;
- unavailable source information;
- extraction failure;
- transformation problems;
- intentional absence of information.

### Current System Support

The deterministic quality pipeline currently detects configured missing or dirty value representations.

The actual count and affected columns must always come from deterministic evidence.

---

## 4. Dirty or Missing-Value Token

### Definition

A dirty or missing-value token is a value used in a dataset to represent missing, unknown, unavailable, or unusable information.

Examples configured by the current quality pipeline include:

```text
ERROR
UNKNOWN
NAN
NONE
NULL
N/A
blank
```

### Interpretation

A configured token is treated as quality evidence by the deterministic pipeline.

The token itself does not necessarily explain why the data is missing or whether another value should replace it.

### Current System Support

This issue type is currently supported by the deterministic quality tool.

The deterministic evidence provides:

- total missing/dirty value count;
- per-column missing/dirty information;
- sample indices for relevant error findings where available.

RAG must use these values as evidence and must not recalculate them.

---

## 5. Blank Value

### Definition

A blank value is an empty field where a value may be expected.

Blank values can occur because of:

- incomplete data entry;
- missing source information;
- parsing problems;
- formatting problems;
- intentional absence.

### Interpretation

A blank value should only be considered a completeness problem when the field is expected to contain information.

A field that is legitimately optional should not automatically be treated as defective.

### Current System Support

Blank values are included in the current configured missing/dirty-value detection logic.

The deterministic quality tool is the source of truth for the detected count.

---

## 6. Missing Required Field

### Definition

A missing required field occurs when a required attribute is absent from a record or dataset structure.

Examples include:

- a required customer identifier not being populated;
- a required transaction date being absent;
- a required business field not being supplied.

### Interpretation

Whether a field is required must come from an explicit schema or business rule.

The knowledge layer must not assume that every field is mandatory.

### Current System Support

The general issue type is defined for the taxonomy, but a complete required-field validation capability is not currently established by the Phase 4A deterministic pipeline.

It should therefore be treated as a future capability unless explicit deterministic rules are added.

---

## 7. Missing Record

### Definition

A missing record occurs when an expected record or business event is absent from the dataset.

Examples might include:

- an expected transaction not appearing in a transaction dataset;
- an expected customer record not being present;
- a required event not being captured.

### Interpretation

Detecting a missing record normally requires an external reference, expected record count, event source, or other authoritative comparison.

A dataset alone may not provide enough evidence to confirm that a record is missing.

### Current System Support

The current deterministic pipeline does not independently establish missing business records.

This issue type is therefore a future capability unless an appropriate reference source or deterministic rule is introduced.

---

## 8. Incomplete Record

### Definition

An incomplete record contains one or more missing or unusable fields where required information is expected.

For example:

```text
Customer ID | Name | Age | City
1001        | Ravi |     | Kolkata
```

The record contains a missing `Age` value.

### Interpretation

The importance of an incomplete record depends on:

- which field is missing;
- whether the field is required;
- how the data is used;
- whether the missing information can be recovered.

### Current System Support

The current quality pipeline can provide missing/dirty-value evidence at the field level.

It does not automatically determine the business significance of every incomplete record.

---

## 9. Evidence and Counts

Dataset-specific completeness evidence must come from deterministic analysis.

Examples include:

```text
total_missing_dirty_values
missing_dirty_matrix
error_sample_indices
```

RAG must not:

- calculate a new count;
- estimate a count;
- invent affected records;
- infer a missing record without evidence.

If Python reports:

```text
total_missing_dirty_values = 16908
```

the explanation layer must preserve that value.

---

## 10. Remediation Considerations

Possible actions include:

- reviewing affected records;
- checking the source system;
- correcting confirmed data-entry problems;
- recovering missing information;
- applying an approved imputation strategy;
- leaving the value missing when the absence is valid.

The correct action depends on the meaning and importance of the field.

Automatic replacement should not be assumed to be appropriate.

---

## 11. Human Review

Human review may be required when:

- the correct replacement value is unknown;
- the field is business-critical;
- imputation could change analytical results;
- the source system must be checked;
- missingness may be intentional;
- an automated correction could affect downstream decisions.

Recommendations involving data modification should follow the project's HITL policy.

---

## 12. RAG Guidance

RAG may use this taxonomy to:

- identify the meaning of a completeness issue;
- explain why missing information matters;
- distinguish currently supported checks from future capabilities;
- explain possible investigation steps;
- explain possible remediation approaches.

RAG must not convert a general taxonomy definition into a claim about the uploaded dataset.

---

## 13. Key Principle

> A completeness issue indicates missing or unusable required information; the appropriate corrective action depends on why the information is missing and how the field is used.