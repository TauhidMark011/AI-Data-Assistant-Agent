
---

```markdown
# Data Quality Pillar: Accuracy

## 1. Definition

Accuracy refers to whether data correctly represents the real-world value, event, or condition that it is intended to describe.

Accuracy is concerned with correctness of meaning, not simply whether a value is present or correctly formatted.

---

## 2. Why Accuracy Matters

Inaccurate data can lead to:

- incorrect analysis;
- incorrect reports;
- incorrect calculations;
- poor operational decisions;
- incorrect customer or business information;
- unreliable downstream models.

The effect depends on the importance of the affected data.

---

## 3. Examples of Accuracy Problems

Possible examples include:

- an incorrect customer value;
- an incorrect transaction amount;
- an incorrect date representing an event;
- a value that does not reflect the actual measurement;
- a value that violates a known business relationship.

Accuracy problems normally require some form of trusted reference or business knowledge to confirm that a value is incorrect.

---

## 4. Statistical Anomalies and Outliers

A numerical outlier is a value that is statistically unusual compared with other observations according to the selected detection method.

An outlier is not automatically inaccurate.

Possible explanations include:

- genuine exceptional observation;
- unusual business event;
- valid high or low value;
- data-entry error;
- measurement error;
- incorrect unit or scale.

Therefore:

> Outlier detection identifies values for investigation; it does not prove that the values are wrong.

---

## 5. Logical and Business-Rule Evidence

A known business rule can provide evidence relevant to accuracy.

For example:

```text
Total = Quantity × Unit Price