# Issue Taxonomy: Structural

## 1. Purpose

This document defines the data-quality issues associated with the Structural quality category.

Structural issues concern whether the basic structure of a dataset is correctly formed and suitable for reliable processing and analysis.

Structural quality is concerned with elements such as:

- columns;
- headers;
- datatypes;
- record structure;
- schema;
- file structure;
- unexpected fields.

The taxonomy provides knowledge for explanation and interpretation.

It does not perform dataset analysis.

---

## 2. Issue Types

The following structural issues are defined:

- schema mismatch;
- missing column;
- unexpected column;
- duplicate column;
- invalid datatype;
- header mismatch;
- malformed record;
- inconsistent record structure.

Not all issue types listed here are currently detected automatically by the deterministic pipeline.

---

## 3. Schema Mismatch

### Definition

A schema mismatch occurs when the actual structure or datatype of a dataset does not match an expected schema.

A schema may define:

- column names;
- column order;
- datatypes;
- required fields;
- allowed structural properties.

### Interpretation

A schema mismatch may affect downstream processing, validation, transformation, or analysis.

The expected schema must be known before a mismatch can be confirmed.

### Current System Support

The deterministic schema tool currently provides information about the detected dataset structure and datatypes.

General comparison against an externally defined expected schema is not currently implemented as a general capability.

---

## 4. Missing Column

### Definition

A missing column occurs when a field expected to be present in the dataset is not available.

For example, an expected `Customer_ID` column may be absent from the input dataset.

### Interpretation

A missing column may prevent specific validation, transformation, or analysis operations.

Confirmation requires knowledge of which columns are expected.

### Current System Support

The current deterministic pipeline reports the columns actually present in the dataset.

General validation against a predefined required-column list is a future capability unless such a rule is explicitly configured.

---

## 5. Unexpected Column

### Definition

An unexpected column occurs when the dataset contains a field that is not part of the expected schema or data contract.

For example, a dataset expected to contain five columns may contain an additional unrecognised field.

### Interpretation

An unexpected column may result from:

- source-system changes;
- export configuration changes;
- accidental data additions;
- schema evolution.

The presence of an additional column is not automatically an error unless an expected schema requires otherwise.

### Current System Support

The deterministic schema tool reports the columns detected in the input dataset.

General detection of unexpected columns requires an authoritative expected schema and is not currently a general capability.

---

## 6. Duplicate Column

### Definition

A duplicate column occurs when multiple fields use the same column name or otherwise represent duplicated structural fields.

Duplicate columns can create ambiguity during data processing.

### Interpretation

Duplicate column names may cause:

- incorrect field selection;
- transformation ambiguity;
- unexpected library behaviour;
- loss or overwriting of information.

The exact impact depends on the input format and processing framework.

### Current System Support

The current schema evidence reports the detected column structure.

A dedicated duplicate-column validation rule is not currently implemented as a general deterministic quality check.

---

## 7. Invalid Datatype

### Definition

An invalid datatype occurs when a field contains a datatype that is incompatible with its intended use or expected schema.

Examples include:

- text where numerical data is expected;
- invalid date representation;
- numerical values stored using an unsuitable datatype.

### Interpretation

Datatype suitability depends on the intended meaning and expected use of the field.

A datatype should therefore be evaluated against an expected schema or validation rule where possible.

### Current System Support

The deterministic schema tool reports detected datatypes.

The system does not independently determine the correct datatype for every business field without an expected schema or explicit rule.

---

## 8. Header Mismatch

### Definition

A header mismatch occurs when column headers do not match the expected field names or structural definition.

Examples include:

- spelling differences;
- unexpected spaces;
- renamed fields;
- missing headers;
- unexpected header names.

### Interpretation

Header differences may affect downstream processing when applications depend on exact field names.

A header mismatch can only be confirmed when an expected header structure is known.

### Current System Support

The current schema tool provides the detected column names.

Comparison against an external expected header definition is not currently implemented as a general capability.

---

## 9. Malformed Record

### Definition

A malformed record is a record whose structure cannot be correctly interpreted according to the expected file or dataset format.

Examples may include:

- incorrect number of fields;
- broken delimiters;
- incorrectly quoted values;
- corrupted record structure.

### Interpretation

Malformed records may prevent correct loading or cause fields to be assigned incorrectly.

The effect depends on the file format and parsing method.

### Current System Support

The current pipeline expects successfully loaded tabular data for downstream deterministic analysis.

A dedicated malformed-record detection layer is not currently implemented as a general quality check.

---

## 10. Inconsistent Record Structure

### Definition

An inconsistent record structure occurs when records do not follow the expected structural pattern of the dataset.

For example, records may contain different numbers of fields or structurally different representations.

### Interpretation

Structural inconsistency may indicate:

- source-system changes;
- malformed records;
- export problems;
- delimiter problems;
- schema changes.

The specific cause requires investigation.

### Current System Support

The deterministic pipeline operates on successfully loaded tabular data and provides schema information after loading.

General detection of every possible record-structure inconsistency is not currently implemented.

---

## 11. Evidence and Counts

Structural evidence must come from deterministic analysis.

Current supported evidence may include:

```text
loader_metadata
schema
columns
datatypes
row_count
column_count

---

## 12. Remediation Considerations

Possible actions include:

- checking the source-system schema;
- comparing the dataset with the expected data contract;
- correcting column names;
- resolving datatype mismatches;
- investigating unexpected fields;
- correcting malformed records at the source;
- validating file-export settings;
- updating the schema contract when a legitimate schema change has occurred.

Structural changes should be made only after confirming the intended schema.

---

## 13. Human Review

Human review may be required when:

- the expected schema is unclear;
- a source-system change may be intentional;
- a column has been renamed;
- a datatype change may be legitimate;
- removing or changing a field could affect downstream systems;
- malformed records require source-system investigation.

Structural corrections should follow the project's HITL policy when they could affect the dataset or downstream processing.

---

## 14. RAG Guidance

RAG may use this taxonomy to:

- explain structural data-quality concepts;
- explain schema and datatype terminology;
- explain the difference between observed structure and expected structure;
- explain possible causes of structural issues;
- explain investigation and remediation approaches;
- distinguish current capabilities from future capabilities.

RAG must not:

- invent an expected schema;
- invent missing or unexpected columns;
- infer structural errors without supporting evidence;
- replace deterministic schema evidence;
- claim that a structural issue was detected when Python did not provide evidence for it.

The deterministic pipeline remains the source of truth for observed dataset structure.

---

## 15. Key Principle

> Structural quality concerns whether the dataset has the expected form and structure; observed structure must be distinguished from an expected schema, and structural issues should not be confirmed without supporting evidence.