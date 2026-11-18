# Issue Taxonomy: Integrity

## 1. Purpose

This document defines the data-quality issues associated with the Integrity quality pillar.

Integrity issues concern broken, duplicated, invalid, or unreliable relationships and logical connections within data.

The taxonomy provides knowledge for explanation and interpretation.

It does not perform dataset analysis.

---

## 2. Issue Types

The following integrity-related issues are defined:

- duplicate record;
- duplicate identifier;
- invalid reference;
- orphaned record;
- broken relationship;
- logical-rule breach;
- business-rule violation.

Not all issue types listed here are currently detected automatically by the deterministic pipeline.

---

## 3. Duplicate Record

### Definition

A duplicate record occurs when a record matches another record according to the duplicate-detection logic being used.

Duplicate detection depends on the fields and comparison method defined by the deterministic quality process.

### Interpretation

A duplicate record does not automatically mean that the record is incorrect or should be deleted.

Possible explanations include:

- accidental duplicate entry;
- repeated source-system record;
- legitimate repeated business event;
- intentionally repeated information.

Business context may be required before deciding whether a duplicate should be removed.

### Current System Support

The deterministic quality pipeline currently detects duplicate records.

The detected duplicate count must always come from deterministic evidence.

RAG must not independently calculate or change the duplicate count.

---

## 4. Duplicate Identifier

### Definition

A duplicate identifier occurs when an identifier expected to be unique appears more than once.

Examples may include:

- duplicate customer ID;
- duplicate employee ID;
- duplicate order ID;
- duplicate transaction ID.

### Interpretation

An identifier should only be considered incorrectly duplicated when uniqueness is required by an explicit schema or business rule.

Some identifiers may legitimately repeat when they represent a group, category, or relationship rather than a unique record.

### Current System Support

The current deterministic pipeline does not establish a general unique-identifier validation capability.

This issue type should therefore be treated as a future capability unless an explicit deterministic uniqueness rule is implemented.

---

## 5. Invalid Reference

### Definition

An invalid reference occurs when a value intended to reference another entity does not correspond to an available or valid referenced entity.

For example:

```text
Order.Customer_ID = 1050
```

may be invalid if customer `1050` does not exist in the authoritative customer dataset.

### Interpretation

Reference validity requires a defined relationship and an authoritative reference source.

A value should not be classified as an invalid reference without evidence from the relevant reference data.

### Current System Support

The current deterministic pipeline does not independently perform general cross-dataset reference validation.

This issue type is therefore a future capability unless an appropriate reference dataset and deterministic rule are introduced.

---

## 6. Orphaned Record

### Definition

An orphaned record is a record that depends on another record or entity but cannot be linked to the expected parent or referenced entity.

Examples may include:

- an order without a valid customer;
- a transaction without a valid account;
- a child record without a valid parent.

### Interpretation

An orphaned record can only be established when the expected relationship and reference data are known.

The absence of a matching reference should be interpreted according to the defined relationship rules.

### Current System Support

The current deterministic pipeline does not independently establish general orphaned-record detection.

This issue type is therefore a future capability.

---

## 7. Broken Relationship

### Definition

A broken relationship occurs when related data does not satisfy an explicitly defined relationship rule.

Examples include:

- child records pointing to nonexistent parents;
- inconsistent parent-child associations;
- records failing a required relationship constraint.

### Interpretation

A relationship must be explicitly defined before a violation can be confirmed.

RAG must not invent relationships or assume that two fields are related without supporting rules.

### Current System Support

The current deterministic pipeline does not provide general cross-dataset relationship validation.

Relationship validation should be treated as a future capability unless explicit deterministic rules are implemented.

---

## 8. Logical-Rule Breach

### Definition

A logical-rule breach occurs when data violates a defined mathematical or logical relationship between values.

For example:

```text
Total = Quantity × Unit Price
```

If the deterministic validation rule identifies a record that does not satisfy the relationship, the record may be reported as a logical-rule breach.

### Interpretation

A logical-rule breach is evidence that a defined relationship has not been satisfied.

It does not automatically prove which value is incorrect.

Possible causes include:

- incorrect input value;
- calculation error;
- incorrect unit;
- transformation problem;
- legitimate exception to the rule.

### Current System Support

The deterministic quality pipeline currently supports logical-rule validation.

The detected rules and breach counts must come from deterministic evidence.

RAG may explain the meaning of the rule but must not independently recalculate the number of breaches.

---

## 9. Business-Rule Violation

### Definition

A business-rule violation occurs when data does not satisfy a defined business requirement or operational constraint.

Examples may include:

- an order exceeding an approved limit;
- an invalid status transition;
- a transaction violating an approved business condition.

### Interpretation

A business rule must be explicitly defined and authoritative before a violation can be confirmed.

Business rules should not be invented by the LLM or inferred solely from unusual data.

### Current System Support

The current pipeline supports configured logical relationships but does not provide a general business-rule engine covering all possible business requirements.

General business-rule violation detection is therefore a future capability unless an explicit deterministic rule is implemented.

---

## 10. Evidence and Counts

Dataset-specific integrity evidence must come from deterministic analysis.

Current evidence may include:

```text
duplicate_records
logic_breaches
```

RAG must not:

- calculate a new duplicate count;
- estimate a breach count;
- invent relationships;
- invent affected records;
- change deterministic evidence.

If Python reports:

```text
duplicate_records = 0
```

RAG must not state that duplicate records were detected.

If Python reports:

```text
logic_breaches = {}
```

RAG must not invent a logical-rule breach.

---

## 11. Remediation Considerations

Possible actions include:

- reviewing duplicate records;
- checking the source system;
- validating identifiers;
- investigating logical-rule breaches;
- checking reference data;
- validating relationship rules;
- correcting confirmed data-quality problems.

Duplicate records should not automatically be deleted.

Logical-rule breaches should not automatically result in overwriting a value.

The appropriate corrective action depends on the evidence and business context.

---

## 12. Human Review

Human review may be required when:

- a duplicate may represent a legitimate business event;
- a record may need to be deleted;
- the correct value cannot be determined automatically;
- a logical relationship has been breached;
- business context is required;
- reference data needs to be checked;
- a correction could affect downstream records.

Recommendations involving dataset modification must follow the project's HITL policy.

---

## 13. RAG Guidance

RAG may use this taxonomy to:

- explain the meaning of integrity issues;
- explain why duplicates may require investigation;
- explain logical-rule breaches;
- distinguish current capabilities from future capabilities;
- explain possible investigation steps;
- explain possible remediation approaches.

RAG must not convert a general taxonomy definition into a claim about the uploaded dataset.

The deterministic evidence remains the source of truth for detected integrity issues.

---

## 14. Key Principle

> Integrity issues indicate that records, relationships, identifiers, or defined logical conditions may not be reliable; the appropriate action depends on the supporting evidence and business context.