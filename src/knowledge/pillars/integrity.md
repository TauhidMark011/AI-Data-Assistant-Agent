
---

```markdown
# Data Quality Pillar: Integrity

## 1. Definition

Integrity refers to whether data maintains valid relationships, structure, and logical connections within the dataset or across related datasets.

Integrity helps ensure that records and values remain logically connected and that relationships between data elements are not broken.

---

## 2. Why Integrity Matters

Poor data integrity can cause:

- incorrect relationships;
- duplicate information;
- orphaned records;
- incorrect joins;
- inaccurate aggregations;
- inconsistent reporting;
- downstream processing errors.

The impact depends on the type of integrity problem and the role of the affected data.

---

## 3. Common Integrity Issues

Examples include:

- duplicate records;
- duplicate identifiers;
- orphaned records;
- invalid references;
- broken relationships;
- inconsistent parent-child relationships;
- records violating defined structural relationships.

Not every duplicate or unusual relationship is automatically an error.

Business context may be required to determine whether the condition is valid.

---

## 4. Duplicate Records

A duplicate record is a record that matches another record according to the duplicate-detection logic being used.

Duplicate detection must be interpreted according to the defined comparison method.

A duplicate does not automatically mean that one record should be deleted.

Possible explanations include:

- genuine duplicate entry;
- repeated business event;
- multiple valid transactions;
- intentional duplicate information;
- source-system duplication.

The correct action requires context.

---

## 5. Relationships and References

Data may contain relationships such as:

- customer-to-order;
- order-to-product;
- employee-to-department;
- transaction-to-account.

An integrity problem may occur when a relationship points to a record that does not exist or violates a defined relationship rule.

The expected relationship must be defined before a violation can be confirmed.

---

## 6. Logical Integrity

Some datasets contain mathematical or logical relationships between fields.

For example:

```text
Total = Quantity × Unit Price