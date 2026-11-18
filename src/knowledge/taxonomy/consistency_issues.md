# Issue Taxonomy: Consistency

## 1. Purpose

This document defines the data-quality issues associated with the Consistency quality pillar.

Consistency issues occur when data that should follow the same representation, format, naming convention, or structural pattern is represented differently.

The taxonomy provides knowledge for explanation and interpretation.

It does not perform dataset analysis.

---

## 2. Issue Types

The following consistency-related issues are defined:

- string inconsistency;
- leading or trailing whitespace;
- case inconsistency;
- format inconsistency;
- date-format inconsistency;
- unit inconsistency;
- naming inconsistency;
- header/data mismatch.

Not all issue types listed here are currently detected automatically by the deterministic pipeline.

---

## 3. String Inconsistency

### Definition

A string inconsistency occurs when values representing the same type of information use different textual representations.

For example:

```text
Kolkata
kolkata
KOLKATA
```

These values may represent the same location but use different text representations.

### Interpretation

A difference in text representation does not automatically mean that the values are incorrect.

The expected representation should be defined before values are classified as inconsistent.

### Current System Support

The current deterministic pipeline does not provide a general string-consistency validation capability.

This issue type should therefore be treated as a future capability unless an explicit deterministic rule is implemented.

---

## 4. Leading or Trailing Whitespace

### Definition

Leading or trailing whitespace occurs when unnecessary spaces appear before or after a value.

For example:

```text
Kolkata
 Kolkata
Kolkata
```

The latter two values contain additional whitespace.

### Interpretation

Unnecessary whitespace can affect:

- matching;
- grouping;
- filtering;
- joins;
- duplicate detection;
- downstream transformations.

However, whitespace may sometimes be meaningful, so trimming should follow an explicit rule.

### Current System Support

The current deterministic pipeline does not provide a dedicated whitespace-consistency check.

This issue type is therefore a future capability unless explicit deterministic validation is added.

---

## 5. Case Inconsistency

### Definition

Case inconsistency occurs when equivalent text values use different capitalization.

For example:

```text
Active
ACTIVE
active
```

These values may represent the same status depending on the defined business rules.

### Interpretation

Case normalization should only be applied when the field is intended to be case-insensitive or when a standard representation has been defined.

Changing case without understanding the field can alter meaningful information.

### Current System Support

The current deterministic pipeline does not provide a general case-consistency validation capability.

This issue type should therefore be treated as a future capability unless an explicit deterministic rule is implemented.

---

## 6. Format Inconsistency

### Definition

A format inconsistency occurs when values representing the same type of information use different formats where a common format is expected.

Examples include:

- different identifier formats;
- different phone-number formats;
- different date representations;
- inconsistent code formatting.

### Interpretation

A format difference may be acceptable when multiple formats are supported.

A consistency issue exists when an explicit standard requires one representation.

### Current System Support

The current deterministic pipeline does not provide a general format-consistency validation capability.

This issue type is therefore a future capability unless explicit deterministic rules are added.

---

## 7. Date-Format Inconsistency

### Definition

Date-format inconsistency occurs when date values use different representations where one standard format is expected.

For example:

```text
2026-09-29
29/09/2026
09-29-2026
```

These values may represent dates but use different formats.

### Interpretation

The expected date format must be defined before a consistency issue can be confirmed.

A date-format difference is not necessarily the same as an invalid date.

### Current System Support

The current quality pipeline can identify date-related information, but it does not establish a general cross-record date-format consistency rule.

Date-format consistency should therefore be treated as a future capability unless an explicit deterministic rule is implemented.

---

## 8. Unit Inconsistency

### Definition

Unit inconsistency occurs when measurements representing the same quantity use different units without clear or controlled conversion.

Examples include:

```text
10 kg
10000 g
```

These values can represent the same quantity when correctly converted.

### Interpretation

Unit consistency requires knowledge of:

- the expected unit;
- the conversion relationship;
- the meaning of the field.

Values should not be converted automatically unless the unit and conversion rule are known.

### Current System Support

The current deterministic pipeline does not provide general unit-consistency detection or conversion.

This issue type is therefore a future capability unless explicit deterministic rules are implemented.

---

## 9. Naming Inconsistency

### Definition

Naming inconsistency occurs when the same entity, category, field, or business concept is represented using different names where a common naming convention is expected.

Examples include:

```text
Customer_Name
customer_name
CustomerName
```

or:

```text
New York
NewYork
New York City
```

The correct interpretation depends on the defined naming rules and business context.

### Interpretation

Naming differences should not automatically be treated as errors.

An authoritative naming convention or mapping should be available before standardization is performed.

### Current System Support

The current deterministic pipeline does not provide a general naming-consistency validation capability.

This issue type is therefore a future capability unless an explicit deterministic rule is implemented.

---

## 10. Header/Data Mismatch

### Definition

A header/data mismatch occurs when column names or header information do not correctly correspond to the structure or meaning of the underlying data.

Examples may include:

- incorrect column names;
- shifted columns;
- unexpected header values;
- data appearing under the wrong header.

### Interpretation

A header/data mismatch can affect the interpretation of the entire dataset.

Confirmation normally requires schema information and validation of the relationship between column names and their data.

### Current System Support

The current schema and quality tools provide schema-related evidence.

However, a complete semantic header/data consistency validation capability is not currently established.

This issue type should therefore be treated as a future capability unless explicit deterministic rules are implemented.

---

## 11. Evidence and Counts

Dataset-specific consistency evidence must come from deterministic analysis.

The knowledge layer must not independently calculate:

- the number of inconsistent values;
- the number of affected records;
- the correct representation;
- the correct naming convention;
- the correct unit.

If deterministic validation identifies a consistency issue, the detected evidence must be treated as authoritative.

RAG may explain the meaning of the issue using this taxonomy.

---

## 12. Remediation Considerations

Possible actions include:

- standardizing text representation;
- trimming unnecessary whitespace;
- standardizing capitalization;
- applying an approved format;
- standardizing date representation;
- converting units using an approved conversion rule;
- applying an approved naming convention;
- correcting confirmed header or schema mismatches.

Remediation should preserve the intended meaning of the data.

Automatic standardization should not be assumed to be appropriate.

---

## 13. Human Review

Human review may be required when:

- multiple representations may have different meanings;
- the correct standard is unclear;
- unit conversion is required;
- naming conventions are business-specific;
- changing values could affect downstream systems;
- schema interpretation is uncertain.

Recommendations involving dataset modification must follow the project's HITL policy.

---

## 14. RAG Guidance

RAG may use this taxonomy to:

- explain the meaning of consistency issues;
- explain why consistent representation matters;
- distinguish formatting differences from actual data errors;
- distinguish current capabilities from future capabilities;
- explain possible investigation steps;
- explain possible remediation approaches.

RAG must not convert a general taxonomy definition into a claim about the uploaded dataset.

The deterministic evidence remains the source of truth for detected issues.

---

## 15. Key Principle

> A consistency issue occurs when data that should follow a common representation or rule is represented differently; the correct standard must be supported by an explicit rule or reliable business context.