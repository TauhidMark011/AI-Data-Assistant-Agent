# Business Rules

## 1. Purpose

This document defines the principles for using business rules in data-quality validation and decision-making.

Business rules describe conditions that data must satisfy to meet a defined business, operational, or process requirement.

Business rules must be explicitly defined and approved before they are used to classify dataset values as compliant or non-compliant.

They do not perform dataset analysis by themselves.

---

## 2. Definition of a Business Rule

A business rule is an explicit condition that represents a business or operational requirement.

Examples include:

- a transaction must not exceed an approved limit;
- an order must contain a valid status;
- a completed transaction must have a completion date;
- an approved record must satisfy required conditions;
- a quantity must be greater than zero.

A business rule should be sufficiently clear that it can be applied consistently.

---

## 3. Business Rule Authority

Business rules should originate from an authoritative source such as:

- approved business requirements;
- documented operational procedures;
- source-system specifications;
- contractual requirements;
- regulatory requirements;
- approved data contracts;
- explicitly configured application rules.

The source of a business rule should be identifiable where possible.

The LLM must not create a business rule based only on patterns observed in the dataset.

---

## 4. Explicit Rule Requirement

A business rule must be explicitly defined before a violation can be confirmed.

For example:

```text
Rule:
Transaction Amount must not exceed 100000.
```

A value of:

```text
125000
```

can be classified as a business-rule violation only when the `100000` limit is an authoritative requirement.

Without that requirement, the value is simply an observed value.

An unusual value must not automatically become a business-rule violation.

---

## 5. Rule Components

A business rule should contain enough information to identify and evaluate the requirement.

Where applicable, a rule should define:

- rule identifier;
- rule description;
- affected field or fields;
- expected condition;
- allowed values or limits;
- applicable records or population;
- severity or business impact;
- source or authority;
- validation method.

A clearly defined rule improves consistency and traceability.

---

## 6. Field-Level Business Rules

A field-level business rule applies to an individual field.

Examples include:

- status must belong to an approved set;
- quantity must be greater than zero;
- transaction amount must be within an approved limit;
- customer type must use an approved value.

The acceptable condition must come from an authoritative business requirement.

### Current System Support

The current deterministic pipeline does not provide a universal business-rule engine for arbitrary field-level requirements.

Such rules are supported only when explicitly configured and implemented as deterministic validation logic.

---

## 7. Cross-Field Business Rules

A cross-field business rule evaluates a relationship between two or more fields.

Examples include:

```text
Total Amount = Quantity × Unit Price
```

or:

```text
Start Date <= End Date
```

or:

```text
Completed Status requires Completion Date
```

The relationship must be explicitly defined.

An apparent relationship discovered from the dataset must not automatically be treated as a business rule.

### Current System Support

The current deterministic pipeline supports configured logical relationships.

The actual rules and breach counts produced by the deterministic system are authoritative.

---

## 8. Conditional Business Rules

A conditional business rule applies only when a specified condition is satisfied.

For example:

```text
IF Status = "Completed"
THEN Completion Date must be present.
```

The condition and required outcome must both be explicitly defined.

Conditional logic should be evaluated consistently for the applicable records.

The LLM must not invent conditional requirements.

---

## 9. Business Rule Violation

A business-rule violation occurs when deterministic validation shows that an explicitly defined business rule has not been satisfied.

A violation should be supported by evidence such as:

- rule identifier;
- rule description;
- affected field or fields;
- affected record information;
- breach count;
- observed condition;
- expected condition.

A violation does not automatically identify the root cause.

Possible causes may include:

- data-entry error;
- source-system problem;
- process failure;
- incorrect transformation;
- outdated business rule;
- legitimate exception.

---

## 10. Exceptions and Overrides

Business processes may contain approved exceptions to normal rules.

An exception should be explicitly documented or identifiable through an authoritative source.

A record that appears to violate a rule may therefore require review before being classified as an actual business failure.

The system must not automatically remove or correct an apparent violation without confirming whether an approved exception exists.

---

## 11. Rule Versioning

Business rules may change over time.

When rules are versioned, validation should use the rule version applicable to the relevant dataset or business period.

A change in a business rule does not necessarily mean that historical data was previously invalid.

Where possible, rule definitions should include:

- version;
- effective date;
- status;
- source;
- approval information.

The applicable rule version should be established before historical compliance is assessed.

---

## 12. Business Rule Conflicts

Two business rules may sometimes produce conflicting requirements.

For example:

```text
Rule A: Status must be "Approved".
Rule B: Status must be "Pending" for the same condition.
```

Conflicting rules should not be resolved by the LLM based on assumption.

The conflict should be escalated to the appropriate business or rule owner.

The authoritative rule definition or approved precedence should determine which requirement applies.

---

## 13. Evidence and Traceability

Business-rule findings must be traceable to:

```text
rule_id
rule_description
rule_source
rule_version
affected_columns
affected_records
breach_count
observed_condition
expected_condition
```

Only evidence actually available from the deterministic validation process should be presented as a confirmed finding.

RAG may explain the meaning and purpose of a rule but must not create evidence that does not exist.

---

## 14. Severity and Business Impact

The severity of a business-rule violation should consider the defined business impact and applicable severity guidance.

Factors may include:

- operational impact;
- financial impact;
- regulatory impact;
- customer impact;
- downstream data impact;
- frequency or scale of the violation.

Severity should not be assigned solely because a value appears unusual.

The project's governance and severity guidance should be used when assigning recommendation priority.

---

## 15. Remediation Considerations

A business-rule violation should normally be investigated before corrective action.

Possible actions include:

- reviewing the affected records;
- checking the source system;
- confirming the applicable rule version;
- checking for approved exceptions;
- correcting confirmed data-entry errors;
- fixing an upstream process;
- updating an incorrectly configured rule;
- documenting a legitimate exception.

The appropriate remediation depends on the cause of the violation.

The system must distinguish between recommending an action and actually executing that action.

---

## 16. Human Review

Human review may be required when:

- business context is needed;
- an approved exception may exist;
- rules conflict;
- the applicable rule version is unclear;
- the violation could have significant operational or financial impact;
- changing the dataset could affect downstream decisions;
- the correct remediation cannot be established automatically.

Consequential changes require appropriate human approval according to the project's HITL policy.

---

## 17. Current System Support

The current deterministic pipeline supports selected configured logical relationships and produces deterministic evidence for detected breaches.

It does not provide a universal business-rule engine covering all possible business requirements.

The following should therefore be treated as future or explicitly configured capabilities:

- general business-rule management;
- business-rule version management;
- universal conditional-rule validation;
- general exception management;
- rule-conflict resolution;
- automated business-impact assessment.

The system must not represent these capabilities as currently implemented unless deterministic support has actually been added.

---

## 18. RAG Guidance

RAG may use these rules to:

- explain business-rule concepts;
- explain why an explicit rule is required;
- explain business-rule violations;
- explain exceptions and rule versioning;
- explain possible causes and remediation approaches;
- explain the importance of traceability;
- distinguish current capabilities from future capabilities.

RAG must not:

- invent business rules;
- invent business limits;
- infer business requirements from unusual values;
- invent rule versions;
- invent exceptions;
- calculate breach counts;
- claim a business-rule violation without deterministic evidence;
- modify the dataset.

The deterministic validation system remains the source of truth for dataset-specific business-rule findings.

---

## 19. Key Principle

> A business-rule violation can only be confirmed when an authoritative business requirement exists and deterministic evidence shows that the requirement was not satisfied.