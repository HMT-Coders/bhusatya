# Risk model

| Category | Weight |
|---|---:|
| OCR character confidence | 15 |
| Cross-field consistency | 20 |
| Image forensics / splicing indicators | 20 |
| Stamp and seal analysis | 15 |
| Signature integrity indicators | 10 |
| Synthetic registry reconciliation | 10 |
| Structural metadata | 10 |

Each category returns available/unavailable. Available categories use concern scores 0–100; higher means more concern. Score:
`sum(weight * concern) / sum(weights for available categories)`.
Coverage is the sum of available weights. Unavailable categories are not silently assigned zero.

Bands: 0–24 Lower concern, 25–49 Some indicators, 50–74 Elevated concern, 75–100 High concern. These are screening labels, not probabilities or legal conclusions.
