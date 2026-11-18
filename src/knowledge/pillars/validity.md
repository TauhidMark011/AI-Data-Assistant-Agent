
---

```markdown
# Data Quality Pillar: Validity

## 1. Definition

Validity refers to whether data conforms to defined rules for datatype, format, range, domain, structure, or other accepted constraints.

A value is valid when it satisfies the rules established for that field or data element.

---

## 2. Why Validity Matters

Invalid data can cause:

- processing failures;
- incorrect calculations;
- failed transformations;
- rejected records;
- unreliable analysis;
- downstream system errors.

Validity rules should be defined according to the intended use of the data.

---

## 3. Common Validity Issues

Examples include:

- invalid datatype;
- invalid date;
- invalid date format;
- invalid numerical range;
- invalid domain value;
- invalid format;
- invalid code;
- unexpected characters;
- values outside defined constraints.

The exact rules depend on the dataset and business requirements.

---

## 4. Datatype Validity

A field may have an expected datatype.

Examples include:

```text
Age        → integer
Price      → numeric
Order Date → date
Customer ID → identifier/string