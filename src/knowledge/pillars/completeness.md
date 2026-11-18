# Data Quality Pillar: Completeness

## 1. Definition

Completeness refers to whether the required data is present and available for its intended use.

A dataset is incomplete when required values, fields, or records are missing or contain representations that effectively mean no usable value is available.

Completeness is concerned with the presence of required information.

It does not determine whether the available information is correct.

---

## 2. Why Completeness Matters

Missing or incomplete data can affect:

- reporting;
- analysis;
- calculations;
- filtering;
- aggregation;
- machine learning;
- business decisions;
- downstream data pipelines.

The impact depends on which fields are affected, how many records are affected, and how important those fields are to the intended use of the data.

---

## 3. Common Completeness Issues

Examples include:

- missing values;
- blank values;
- missing required fields;
- missing records;
- partially populated records;
- placeholder values representing missing information.

Examples of placeholder values may include:

- `NULL`
- `N/A`
- `NONE`
- `UNKNOWN`
- `NAN`
- blank strings

The exact definition of a missing or dirty value depends on the validation rules used by the data-quality system.

---

## 4. Completeness vs Other Quality Dimensions

Completeness answers:

> Is the required information present?

It does not answer:

> Is the information correct?

For example:

```text
Customer Age = 35