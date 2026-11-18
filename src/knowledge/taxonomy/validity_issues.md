# Issue Taxonomy: Validity

## 1. Purpose

This document defines the data-quality issues associated with the Validity quality pillar.

Validity issues occur when data does not conform to defined datatype, format, range, domain, structural, or other validation rules.

The taxonomy provides knowledge for explanation and interpretation.

It does not perform dataset analysis.

---

## 2. Issue Types

The following validity-related issues are defined:

- invalid datatype;
- invalid date;
- mixed date format;
- invalid numerical range;
- invalid domain value;
- invalid format;
- invalid code;
- unexpected or invalid characters.

Not all issue types listed here are currently detected automatically by the deterministic pipeline.

---

## 3. Invalid Datatype

### Definition

An invalid datatype occurs when a value does not conform to the expected datatype defined for a field.

Examples include:

- text where a numeric value is required;
- invalid date representation where a date is required;
- incompatible values in a typed field.

### Interpretation

The expected datatype must be defined before a value can be classified as invalid.

A datatype problem does not automatically prove that the underlying real-world information is inaccurate.

### Current System Support

The current schema and quality tools provide schema-related information.

A complete datatype-validation capability across all fields is not currently established.

This issue type should therefore be treated as a future capability unless explicit deterministic validation rules are implemented.

---

## 4. Invalid Date

### Definition

An invalid date occurs when a value intended to represent a date cannot be interpreted as a valid date according to the defined date rules.

Examples may include:

```text
2026-13-45
31/02/2026
not-a-date
```

### Interpretation

Date validity depends on:

- the expected date datatype;
- the accepted date format;
- valid calendar values.

A date-format difference should not automatically be classified as an invalid date.

### Current System Support

The current quality pipeline can identify date-related information.

A complete invalid-date validation capability is not currently established for all possible date representations.

This issue type should therefore be treated as a future capability unless explicit deterministic validation rules are implemented.

---

## 5. Mixed Date Format

### Definition

A mixed date format occurs when date values use different formats within a field where a common format is expected.

For example:

```text
2026-09-29
29/09/2026
09-29-2026
```

These values may represent valid dates but use different representations.

### Interpretation

Mixed date formats are primarily a consistency and validity concern depending on the defined validation rule.

The expected format must be explicitly defined before the values can be classified as invalid.

### Current System Support

The current quality pipeline can identify date-related information but does not provide a complete mixed-date-format validation rule.

This issue type is therefore a future capability unless an explicit deterministic rule is implemented.

---

## 6. Invalid Numerical Range

### Definition

An invalid numerical range occurs when a numerical value falls outside the range explicitly allowed for a field.

For example, if a percentage must be between `0` and `100`, a value of `150` violates that defined range.

### Interpretation

A valid range must be established before a value can be classified as invalid.

An unusually high or low value is not automatically an invalid range violation.

Statistical outliers and rule-based range violations are different concepts.

### Current System Support

The current deterministic pipeline detects numerical outliers using a statistical method.

It does not provide a general business-defined range validation capability.

Therefore, numerical outlier detection must not be described as general range validation.

---

## 7. Invalid Domain Value

### Definition

An invalid domain value occurs when a field contains a value outside an explicitly approved set of allowed values.

For example:

```text
Status:
ACTIVE
INACTIVE
PENDING
```

A different value may be invalid if these are the only permitted domain values.

### Interpretation

The allowed domain must come from an authoritative rule or reference source.

The LLM must not invent an allowed domain.

### Current System Support

The current deterministic pipeline does not provide a general domain-value validation capability.

This issue type is therefore a future capability unless explicit deterministic rules are implemented.

---

## 8. Invalid Format

### Definition

An invalid format occurs when a value does not conform to an explicitly defined format requirement.

Examples include:

- invalid identifier pattern;
- invalid postal-code format;
- invalid product-code format;
- invalid email format.

### Interpretation

A format rule must be defined before a violation can be confirmed.

A different representation is not automatically invalid if multiple representations are permitted.

### Current System Support

The current deterministic pipeline does not provide general format validation across arbitrary fields.

This issue type is therefore a future capability unless explicit deterministic rules are implemented.

---

## 9. Invalid Code

### Definition

An invalid code occurs when a coded value does not belong to an approved coding system or reference set.

Examples include:

- unsupported status code;
- unknown product code;
- invalid location code;
- unrecognized category code.

### Interpretation

The authoritative code set must be available before a code can be classified as invalid.

An unknown code may require checking the latest reference data before correction.

### Current System Support

The current deterministic pipeline does not provide general reference-code validation.

This issue type is therefore a future capability unless an explicit deterministic rule and authoritative code set are introduced.

---

## 10. Unexpected or Invalid Characters

### Definition

Unexpected or invalid characters occur when a field contains characters that are not permitted by its defined validation rule.

Examples may include:

- unsupported symbols in an identifier;
- unexpected control characters;
- characters outside an approved pattern.

### Interpretation

The allowed character set must be defined for the relevant field.

Special characters are not automatically invalid because some fields legitimately require them.

### Current System Support

The current deterministic pipeline does not provide general character-set validation.

This issue type is therefore a future capability unless explicit deterministic rules are implemented.

---

## 11. Evidence and Counts

Dataset-specific validity evidence must come from deterministic analysis.

The knowledge layer must not independently calculate:

- the number of invalid values;
- the number of affected records;
- whether a value violates a range;
- whether a value belongs to an approved domain;
- whether a code is valid.

RAG may explain a detected validation issue using the applicable knowledge.

It must not invent validation rules or evidence.

---

## 12. Remediation Considerations

Possible actions include:

- checking the source value;
- validating the datatype;
- correcting confirmed date values;
- standardizing an approved format;
- checking an allowed range;
- validating against an authoritative domain;
- checking reference codes;
- correcting confirmed character or format violations.

Remediation should follow the defined validation rule.

Automatic correction should not be assumed to be appropriate.

---

## 13. Human Review

Human review may be required when:

- the validation rule is unclear;
- the allowed range is uncertain;
- the domain is business-specific;
- reference data must be checked;
- the correct value cannot be determined automatically;
- changing the value could affect downstream processing.

Recommendations involving dataset modification must follow the project's HITL policy.

---

## 14. RAG Guidance

RAG may use this taxonomy to:

- explain the meaning of validity issues;
- explain why explicit validation rules are required;
- distinguish validity from consistency and accuracy;
- distinguish current capabilities from future capabilities;
- explain possible investigation steps;
- explain possible remediation approaches.

RAG must not convert a general taxonomy definition into a claim about the uploaded dataset.

The deterministic evidence remains the source of truth for detected validity-related findings.

---

## 15. Key Principle

> A validity issue occurs when data does not conform to an explicitly defined rule for datatype, format, range, domain, code, or other accepted constraint.