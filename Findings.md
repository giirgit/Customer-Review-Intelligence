# Customer Review Intelligence — Final Findings

## Executive Summary

The analysed review sample is strongly positive overall, with:

- **75.57% positive**
- **12.68% mixed**
- **10.72% negative**
- **1.03% neutral**

However, aggregate sentiment hides important product-specific issues.

Aspect-level analysis identified recurring pain points around:

- finish
- pigmentation
- shade match
- longevity
- hair effect
- price/value
- texture
- application

The strongest business insight from the project is that high overall positive sentiment does not mean every product attribute is performing well.

---

## Overall Sentiment

Out of 970 analysed reviews:

| Sentiment | Reviews | Percentage |
|---|---:|---:|
| Positive | 733 | 75.57% |
| Mixed | 123 | 12.68% |
| Negative | 104 | 10.72% |
| Neutral | 10 | 1.03% |

The majority of feedback is positive.

Therefore, the most useful analysis is not simply overall sentiment, but identifying which specific aspects are responsible for dissatisfaction.

---

## Rating vs Sentiment Validation

The extracted sentiment closely follows the original star ratings.

| Rating | Dominant Sentiment | Percentage |
|---|---|---:|
| 1★ | Negative | 94.55% |
| 2★ | Negative | 85.19% |
| 3★ | Mixed | 45.16% |
| 4★ | Positive | 67.42% |
| 5★ | Positive | 92.90% |

The strong alignment between star ratings and extracted sentiment provides a useful validation signal for the LLM-based sentiment extraction.

---

## Highest-Priority Product Pain Points

The strongest product issues were identified using two measures:

**Negative Rate**

How often an aspect is negative when customers mention it.

**Negative Weight**

How much that negative aspect contributes to all aspect feedback for the product.

### 1. Maybelline Color Sensational Matte Metallic Lipstick

**Issue:** Finish

- 7 finish mentions
- 4 negative
- **57.14% negative rate**
- **19.05% negative weight**

Finish represents the largest high-weight product pain point identified in the analysis.

---

### 2. L'Oreal Superliner Black Lacquer

**Issue:** Price / Value

- 3 mentions
- 3 negative
- **100% negative rate**
- **16.67% negative weight**

All observed price/value mentions were negative.

Because the number of mentions is small, this should be treated as an investigation signal.

---

### 3. L'Oreal Matte Signature Eyeliner

**Issue:** Longevity

- 3 mentions
- 2 negative
- **66.67% negative rate**
- **15.38% negative weight**

Longevity appears to be an important recurring issue in the analysed reviews for this product.

---

### 4. Maybelline V-Face Duo Stick

Two strong issues were found.

#### Pigmentation

- 12 mentions
- 5 negative
- **41.67% negative rate**
- **14.29% negative weight**

#### Shade Match

- 5 mentions
- 4 negative
- **80% negative rate**
- **11.43% negative weight**

Within the analysed reviews, colour-related attributes represent a meaningful source of dissatisfaction for this product.

---

### 5. Herbal Essences Strawberry & Mint Shampoo

**Issue:** Hair Effect

- 14 mentions
- 6 negative
- **42.86% negative rate**
- **13.95% negative weight**

Hair-effect complaints represent one of the most important product-level pain points identified for this product.

---

### 6. Kay Beauty Creme Blush

**Issue:** Price / Value

- 4 mentions
- 3 negative
- **75% negative rate**
- **13.64% negative weight**

Price/value appears to be a significant concern within the analysed feedback for this product.

---

# Brand-Level Findings

## Herbal Essences

The strongest recurring negative theme was:

### Hair Effect

- 110 mentions
- 21 negative
- **19.09% negative rate**
- **6.67% negative weight within brand feedback**

Other notable issues:

- scalp effect: **41.67% negative**
- price/value: **23.81% negative**
- formula: **17.65% negative**

### Interpretation

Hair-related performance is the most important recurring customer issue for Herbal Essences in the analysed sample.

---

## Kay Beauty

The strongest recurring negative theme was:

### Price / Value

- 56 mentions
- 21 negative
- **37.50% negative rate**
- **2.71% negative weight**

Other issues:

- quantity: **53.85% negative**
- packaging: **28.57% negative**
- longevity: **12.12% negative**
- coverage: **13.79% negative**

### Interpretation

Customers generally respond positively to many Kay Beauty product attributes, but value perception appears to be one of the clearest recurring concerns in the analysed sample.

---

## L'Oreal Paris

The strongest recurring negative theme was:

### Price / Value

- 25 mentions
- 12 negative
- **48% negative rate**
- **5.45% negative weight**

Other notable issues:

- quantity: **66.67% negative**
- fragrance: **60% negative**
- skin feel: **50% negative**
- formula: **45.45% negative**
- finish: **29.41% negative**

### Interpretation

Price/value is an important broad complaint theme in the analysed sample, while product-experience issues also appear around quantity, formula, fragrance and skin feel.

---

## Lakme

Important negative themes included:

- price/value: **27.59% negative**
- texture: **26.92% negative**
- coverage: **29.41% negative**
- application: **23.08% negative**
- longevity: **17.65% negative**

### Interpretation

Lakme feedback is distributed across several product-use attributes rather than being dominated by one single issue.

---

## Maybelline New York

The clearest recurring issue was:

### Pigmentation

- 45 mentions
- 13 negative
- **28.89% negative rate**
- **4.14% negative weight**

Other notable issues:

- finish: **21.95% negative**
- shade match: **16.67% negative**

### Interpretation

Colour-related performance appears to be one of the major recurring areas of dissatisfaction across the Maybelline products analysed.

---

# Products With Highest Negative or Mixed Sentiment

Among products with at least five analysed reviews:

| Product | Negative or Mixed % |
|---|---:|
| L'Oreal Superliner Black Lacquer | 83.33% |
| L'Oreal Age 20+ Skin Perfect Cream | 72.73% |
| NYX Liquid Suede Cream Lipstick | 70.00% |
| Maybelline V-Face Duo Stick | 62.50% |
| L'Oreal Matte Signature Eyeliner | 60.00% |
| Kay Beauty Creme Blush | 50.00% |
| Lakme 9to5 Primer + Matte Liquid Lip Color | 50.00% |

These should be treated as products requiring further investigation rather than being labelled as the worst products.

---

# Discount vs Price/Value Sentiment

The hypothesis tested was:

> Are larger listed discounts associated with more positive price/value sentiment?

Results:

| Discount Band | Positive | Negative |
|---|---:|---:|
| No discount | 66.67% | 30.56% |
| 10–20% | 56.25% | 43.75% |
| 20–30% | 56.82% | 40.91% |
| 30%+ | 64.00% | 32.00% |

There is no clear monotonic relationship.

Higher listed discounts did not consistently correspond to more positive customer perceptions of price/value in the analysed sample.

### Interpretation

Price/value perception may reflect factors beyond discount level, such as:

- product performance
- quantity
- quality
- effectiveness
- longevity
- overall product experience

These factors were not individually tested as causes of price/value sentiment in this analysis.

Therefore, the results support only the conclusion that **listed discount level alone does not show a clear relationship with price/value sentiment**.

---

# Business Recommendations

1. Prioritise issues using both **negative rate** and **negative weight**.

2. Investigate recurring high-impact product issues such as:
   - finish
   - pigmentation
   - shade match
   - longevity
   - hair effect
   - price/value

3. Review actual complaint text before recommending a product change.

4. Do not compare brands using raw complaint counts because brand representation differs in the final sample.

5. Treat extreme percentages based on very small numbers of mentions cautiously.

6. Do not assume discounting alone will improve customer perception of value.

---

# Final Business Insight

The analysed reviews are positive overall, but aggregate sentiment hides important product-specific dissatisfaction.

Aspect-level review intelligence makes it possible to distinguish between:

- what customers generally like
- what customers repeatedly dislike
- how frequently an aspect receives negative feedback
- how much weight that issue carries within total product feedback

This allows customer review data to move beyond simple star ratings and become a more useful source of product and business intelligence.