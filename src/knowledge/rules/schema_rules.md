# Schema Rules

## 1. Purpose

This document defines the rules and principles used to interpret and validate dataset schemas.

A schema describes the expected structural characteristics of a dataset, including:

- column names;
- column presence;
- datatypes;
- required fields;
- structural expectations;
- allowed schema changes.

These rules provide knowledge for schema validation, explanation, and governance.

They do not perform dataset analysis by themselves.

---

## 2. Schema as a Data Contract

A schema can act as a data contract between a data producer and a data consumer.

A data contract may define:

- expected column names;
- expected datatypes;
- required fields;
- optional fields;
- allowed values or formats where applicable;
- structural constraints;
- rules for approved schema changes.

An observed dataset should be compared with an authoritative expected schema when schema compliance needs to be confirmed.

---

## 3. Expected Schema

An expected schema is the authoritative definition of the structure that a dataset is required to follow.

The expected schema should come from a trusted source such as:

- an approved data contract;
- an authoritative source-system definition;
- an approved schema configuration;
- documented pipeline requirements.

An LLM must not invent an expected schema from the observed dataset.

If no authoritative expected schema is available, the system should report the observed structure without claiming that it matches or violates an expected schema.

---

## 4. Column Name Rules

Column names should follow the naming standard defined by the applicable data contract or source-system specification.

Where a naming standard exists, validation may consider:

- spelling;
- capitalization;
- separators;
- whitespace;
- naming conventions;
- duplicate names;
- reserved names.

A difference in column naming should only be classified as a schema issue when an expected naming standard or schema provides supporting evidence.

### Current System Support

The deterministic schema tool reports the column names detected in the dataset.

General comparison against an external naming standard is not currently implemented unless an explicit deterministic rule is provided.

---

## 5. Required Column Rules

A required column is a field that must be present for the dataset or a specific downstream process to operate correctly.

Required columns should be explicitly defined by:

- the data contract;
- pipeline requirements;
- source-system specification;
- configured validation rules.

A column must not be classified as missing merely because it is not known to the LLM.

### Current System Support

The deterministic pipeline reports the columns that are actually present.

General validation against a configurable required-column list is a future capability unless such a rule is explicitly implemented.

---

## 6. Datatype Rules

Each field should use a datatype that is appropriate for its intended meaning and processing requirements.

Examples include:

- integer;
- floating-point number;
- string;
- boolean;
- date;
- datetime.

Datatype expectations should be defined by an authoritative schema or explicit validation rule.

A detected datatype is an observation about the loaded dataset. It is not automatically proof that the datatype is correct for the business meaning of the field.

### Current System Support

The deterministic schema tool reports detected datatypes.

It does not independently determine the correct business datatype for every field without an expected schema or explicit rule.

---

## 7. Required and Optional Fields

Schema definitions may distinguish between required and optional fields.

### Required field

A required field must be present for the applicable dataset or process.

### Optional field

An optional field may be absent without automatically causing a schema violation.

The required or optional status must come from an authoritative schema or explicit configuration.

RAG must not infer that a field is required only because its name appears important.

---

## 8. Column Count Rules

Column count is an observed structural property of the dataset.

A column count mismatch can only be confirmed when an expected column count or expected schema is available.

For example:

```text
Expected schema: 8 columns
Observed schema: 7 columns
```

This may indicate a structural issue if the expected schema is authoritative.

Without an expected schema:

```text
Observed schema: 7 columns
```

is only an observation and should not be described as a mismatch.

### Current System Support

The deterministic loader and schema evidence provide dataset dimensions and detected columns.

General expected-versus-observed column-count validation is not currently implemented.

---

## 9. Datatype Compatibility Rules

A datatype should be considered compatible when it satisfies the requirements defined by the expected schema or validation rule.

Examples:

```text
Expected: numerical
Observed: numerical
```

may be compatible.

Whereas:

```text
Expected: numerical
Observed: text
```

may represent a datatype mismatch.

However, the actual interpretation depends on the schema and intended use of the field.

The LLM must not decide datatype compatibility without the relevant expected rule or schema.

---

## 10. Schema Evolution Rules

Schema changes may be legitimate.

Examples include:

- adding a new optional column;
- renaming a field;
- changing a datatype;
- removing a deprecated field;
- introducing a new version of a dataset.

A schema change should not automatically be treated as a data-quality failure.

The change should be evaluated against the approved schema-evolution process.

Where schema versioning is used, the applicable version should be identified before validation.

---

## 11. Schema Mismatch Rules

A schema mismatch may be confirmed when the observed dataset differs from an authoritative expected schema.

Possible mismatch categories include:

- missing expected column;
- unexpected column;
- incorrect datatype;
- incorrect column name;
- incorrect required/optional status;
- incompatible structural change.

The evidence should identify:

- the expected condition;
- the observed condition;
- the source of the expected schema;
- the affected field or structural element.

RAG must explain the mismatch using the supplied evidence rather than creating additional schema assumptions.

---

## 12. Duplicate Column Rules

Column names should be unique unless the applicable data format and processing system explicitly allow otherwise.

Duplicate column names may cause:

- ambiguous field selection;
- incorrect transformations;
- unexpected processing behaviour;
- loss or overwriting of information.

A duplicate-column issue should be confirmed using deterministic structural evidence.

### Current System Support

The current schema evidence reports the detected dataset structure.

A dedicated duplicate-column validation rule is not currently implemented as a general quality check.

---

## 13. Schema Validation Evidence

Schema validation evidence must come from deterministic analysis and authoritative schema definitions.

Relevant evidence may include:

```text
loader_metadata
row_count
column_count
columns
datatypes
expected_schema
schema_version
```

Where an expected schema is unavailable, only observed structural evidence should be reported.

RAG must not:

- invent expected columns;
- invent expected datatypes;
- invent schema versions;
- calculate unsupported schema findings;
- convert an observation into a confirmed mismatch without an authoritative expectation.

---

## 14. Current System Support

The current deterministic pipeline supports observation of dataset structure through:

- dataset dimensions;
- detected column names;
- detected datatypes;
- loader metadata.

The current system does not provide a general external expected-schema validation engine.

Therefore, the following are future capabilities unless explicitly configured and implemented:

- required-column validation;
- expected-column comparison;
- expected-datatype comparison;
- schema-version validation;
- general schema-evolution validation;
- external data-contract validation.

The distinction between observed structure and expected structure must be maintained.

---

## 15. Human Review

Human review may be required when:

- a schema mismatch may result from an intentional source-system change;
- a datatype change may be legitimate;
- a column has been renamed;
- an expected schema is unclear;
- a schema change could affect downstream systems;
- the correct schema version cannot be established automatically.

Schema changes with downstream impact should not be applied automatically without appropriate approval.

---

## 16. RAG Guidance

RAG may use these rules to:

- explain schema terminology;
- explain observed versus expected schema;
- explain datatype and column requirements;
- explain possible schema mismatches;
- explain schema-evolution concepts;
- explain why an expected schema is required for certain validations.

RAG must not:

- invent an expected schema;
- invent required columns;
- invent datatype requirements;
- claim a schema mismatch without supporting evidence;
- replace deterministic schema analysis;
- modify the dataset.

The deterministic pipeline and authoritative schema definition remain the source of truth.

---

## 17. Key Principle

> A schema rule defines what structure is expected; deterministic analysis establishes what structure was observed, and a schema mismatch should only be confirmed when those two sources can be reliably compared.