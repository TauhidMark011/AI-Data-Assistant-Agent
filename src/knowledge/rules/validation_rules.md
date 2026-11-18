# Validation Rules

## 1. Purpose

This document defines the rules and principles for validating dataset values and relationships against explicitly defined validation conditions.

Validation rules determine whether observed data satisfies a known requirement.

These rules provide knowledge for validation interpretation, explanation, and governance.

They do not perform dataset analysis by themselves.

---

## 2. Validation Rule as an Explicit Condition

A validation rule should define a condition that can be evaluated against dataset data.

A validation rule may specify:

- the field or fields involved;
- the expected condition;
- the allowed values or ranges;
- the relationship between fields;
- the expected datatype or format;
- the action to take when the condition is not satisfied.

A validation rule should be explicit enough that the same condition can be evaluated consistently.

---

## 3. Rule Source and Authority

Validation rules should come from an authoritative source such as:

- an approved data contract;
- documented business requirements;
- source-system specifications;
- regulatory or operational requirements;
- approved pipeline configuration;
- explicitly configured deterministic rules.

An LLM must not create a validation rule merely because a value appears unusual.

If no authoritative rule exists, the system should describe the observed condition without claiming that a validation requirement has been violated.

---

## 4. Field-Level Validation

Field-level validation evaluates individual fields against defined requirements.

Examples include:

- datatype validation;
- allowed-value validation;
- numerical-range validation;
- date-format validation;
- required-field validation;
- character or format validation.

The expected condition must be known before a field can be classified as invalid.

### Current System Support

The current deterministic pipeline supports selected data-quality checks, including missing/dirty-value detection and numerical outlier detection.

General field-level validation is not implemented for every possible datatype, format, domain, or business requirement.

---

## 5. Range Validation

A range validation rule checks whether a numerical or date value falls within an explicitly defined acceptable range.

For example:

```text
Age must be between 0 and 120
```

A value outside the defined range may represent a validation failure.

The range must come from an authoritative requirement.

The LLM must not invent acceptable minimum or maximum values.

### Current System Support

The current deterministic pipeline does not provide a universal configurable range-validation engine.

Numerical outlier detection is a statistical check and must not be confused with an explicit business range rule.

---

## 6. Domain Validation

Domain validation checks whether a value belongs to an explicitly defined set of allowed values.

For example:

```text
Status ∈ {Pending, Approved, Rejected}
```

A value outside the approved domain may represent a validation failure.

The allowed domain must be explicitly defined.

RAG must not infer an allowed domain from the values currently present in a dataset.

### Current System Support

The current pipeline does not provide a general domain-validation engine.

Domain validation is a future capability unless an explicit deterministic rule is configured.

---

## 7. Format Validation

Format validation checks whether a value follows an explicitly defined representation.

Examples include:

- date formats;
- identifier formats;
- codes;
- structured text patterns;
- approved character formats.

A format rule should define the expected pattern clearly.

A value should not be considered invalid simply because it differs from another common format.

### Current System Support

The deterministic pipeline provides selected structural and quality evidence but does not implement a universal format-validation framework.

---

## 8. Date Validation

Date validation may check whether:

- a value can be interpreted as a valid date;
- the date follows an expected format;
- a date falls within an allowed range;
- relationships between dates satisfy an explicit rule.

Examples:

```text
Start Date <= End Date
```

or:

```text
Transaction Date must not be in the future
```

These are valid only when the corresponding requirements are explicitly defined.

The LLM must not invent date constraints.

---

## 9. Logical Relationship Validation

A logical relationship rule checks whether multiple fields satisfy an explicitly defined relationship.

For example:

```text
Total = Quantity × Unit Price
```

If the relationship is not satisfied, the deterministic system may report a logical-rule breach.

The breach indicates that the relationship was not satisfied.

It does not automatically identify which field contains the incorrect value.

### Current System Support

The current deterministic pipeline supports configured logical relationships.

The detected rules and breach counts are authoritative deterministic evidence.

RAG may explain the rule but must not recalculate or alter the breach count.

---

## 10. Cross-Field Validation

Cross-field validation evaluates relationships between two or more fields.

Examples include:

- start date must be earlier than end date;
- quantity must be greater than zero;
- total must equal quantity multiplied by unit price;
- status must be compatible with another field.

Each relationship must be explicitly defined.

An apparent relationship discovered by the LLM must not be treated as an authoritative validation rule.

### Current System Support

The current pipeline supports configured logical relationships but does not provide a general engine for every possible cross-field business rule.

---

## 11. Missing and Dirty-Value Validation

Missing and dirty-value validation identifies values that are absent or represented using configured missing/dirty tokens.

Examples may include:

- null values;
- blank values;
- configured missing-value tokens;
- dirty placeholders.

The exact detection behaviour must come from the deterministic implementation.

RAG must not independently count missing or dirty values.

### Current System Support

The current deterministic quality pipeline supports missing/dirty-value detection.

The authoritative totals and per-column evidence come from deterministic quality results.

---

## 12. Duplicate Validation

Duplicate validation identifies records or identifiers that violate an explicitly defined uniqueness requirement.

A duplicate check must distinguish between:

- duplicate records;
- duplicate identifiers;
- legitimate repeated values.

Repeated values are not automatically errors.

A uniqueness requirement must be known before a duplicate can be classified as a validation failure.

### Current System Support

The current deterministic pipeline provides duplicate-record evidence.

A general configurable uniqueness validation framework is not currently implemented.

---

## 13. Statistical Validation and Outliers

Statistical checks may identify observations that differ substantially from the distribution of a numerical field.

The current pipeline uses the IQR method for numerical outlier detection.

An outlier is statistical evidence, not automatic proof of invalidity or inaccuracy.

For example:

```text
A high transaction value
```

may be:

- a genuine transaction;
- an exceptional business event;
- a data-entry error.

The value should therefore be reviewed before any corrective action.

---

## 14. Validation Failure Interpretation

A validation failure means that an explicitly defined condition was not satisfied.

It does not necessarily mean that the underlying value is incorrect.

Possible causes include:

- incorrect source data;
- data-entry error;
- source-system changes;
- incorrect rule configuration;
- legitimate exception;
- transformation problem;
- unit or format mismatch.

Investigation may be required before remediation.

---

## 15. Evidence Requirements

Validation findings must be supported by deterministic evidence.

Relevant evidence may include:

```text
rule_id
rule_description
affected_column
affected_columns
breach_count
affected_records
observed_value
expected_condition
```

Only evidence actually produced by the deterministic pipeline should be presented as a confirmed finding.

RAG must not:

- invent rule IDs;
- invent breach counts;
- invent affected records;
- invent expected conditions;
- create validation findings from general knowledge alone.

---

## 16. Current System Support

The current deterministic pipeline supports selected validation and quality checks, including:

- missing/dirty-value detection;
- duplicate-record detection;
- configured logical-rule validation;
- numerical outlier detection;
- schema and datatype observation.

The following are not general capabilities unless explicitly implemented:

- universal range validation;
- universal domain validation;
- universal format validation;
- general uniqueness rules;
- comprehensive business-rule validation;
- general cross-field validation beyond configured rules.

Current capabilities must not be represented as broader than the actual deterministic implementation.

---

## 17. Human Review

Human review may be required when:

- a validation failure may represent a legitimate exception;
- the expected condition is unclear;
- a rule may be incorrectly configured;
- the correct value cannot be established automatically;
- changing a value could affect downstream decisions;
- business context is required to interpret the finding.

Validation findings should be reviewed before consequential data changes are approved.

---

## 18. RAG Guidance

RAG may use these rules to:

- explain validation concepts;
- explain the meaning of a validation failure;
- explain configured logical rules;
- explain statistical outliers;
- explain possible causes of validation failures;
- distinguish deterministic findings from general knowledge;
- explain possible investigation and remediation approaches.

RAG must not:

- invent validation rules;
- invent acceptable ranges;
- invent allowed domains;
- invent business constraints;
- calculate validation counts;
- replace deterministic validation;
- claim a rule was violated without supporting evidence.

The deterministic pipeline remains the source of truth for dataset-specific validation findings.

---

## 19. Key Principle

> A validation finding is meaningful only when an explicit condition exists and deterministic evidence shows whether the observed data satisfies that condition.