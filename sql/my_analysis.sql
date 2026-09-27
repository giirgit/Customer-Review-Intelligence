-- ============================================================
-- Customer Review Intelligence — Final SQL Analysis
-- SQLite
-- Tables:
--   reviews        : one row per analysed review
--   review_aspects : one row per extracted aspect mention
-- ============================================================


-- 1. What is the overall customer sentiment across the analysed reviews?
SELECT
    overall_sentiment,
    COUNT(*) AS review_count,
    ROUND(
        100.0 * COUNT(*) / (SELECT COUNT(*) FROM reviews),
        2
    ) AS percentage
FROM reviews
GROUP BY overall_sentiment
ORDER BY review_count DESC;


-- 2. What is the customer sentiment distribution for each product,
--    and which sentiment ranks highest?
WITH sentiment_counts AS (
    SELECT
        product_id,
        brand_name,
        product_title,
        overall_sentiment,
        COUNT(*) AS sentiment_count
    FROM reviews
    GROUP BY
        product_id,
        brand_name,
        product_title,
        overall_sentiment
),
product_totals AS (
    SELECT
        product_id,
        COUNT(*) AS total_reviews
    FROM reviews
    GROUP BY product_id
),
ranked_sentiments AS (
    SELECT
        sc.product_id,
        sc.brand_name,
        sc.product_title,
        sc.overall_sentiment,
        sc.sentiment_count,
        pt.total_reviews,
        ROUND(100.0 * sc.sentiment_count / pt.total_reviews, 2) AS sentiment_pct,
        RANK() OVER (
            PARTITION BY sc.product_id
            ORDER BY sc.sentiment_count DESC
        ) AS sentiment_rank
    FROM sentiment_counts sc
    INNER JOIN product_totals pt
        ON sc.product_id = pt.product_id
)
SELECT *
FROM ranked_sentiments
ORDER BY product_id, sentiment_rank, overall_sentiment;


-- 3. Which aspects recur within each product, and with what sentiment?
SELECT
    r.product_id,
    r.brand_name,
    r.product_title,
    a.aspect,
    a.aspect_sentiment,
    COUNT(*) AS mention_count
FROM reviews r
INNER JOIN review_aspects a
    ON r.review_id = a.review_id
GROUP BY
    r.product_id,
    r.brand_name,
    r.product_title,
    a.aspect,
    a.aspect_sentiment
ORDER BY
    r.product_id,
    mention_count DESC;


-- 4. For each product + aspect + sentiment, what percentage of ALL
--    aspect mentions for that product does it represent?
WITH sentiment_counts AS (
    SELECT
        r.product_id,
        r.product_title,
        r.brand_name,
        a.aspect,
        a.aspect_sentiment,
        COUNT(*) AS sentiment_count
    FROM reviews r
    INNER JOIN review_aspects a
        ON r.review_id = a.review_id
    GROUP BY
        r.product_id,
        r.product_title,
        r.brand_name,
        a.aspect,
        a.aspect_sentiment
),
product_totals AS (
    SELECT
        r.product_id,
        COUNT(*) AS total_aspect_mentions
    FROM reviews r
    INNER JOIN review_aspects a
        ON r.review_id = a.review_id
    GROUP BY r.product_id
)
SELECT
    s.product_id,
    s.product_title,
    s.brand_name,
    s.aspect,
    s.aspect_sentiment,
    s.sentiment_count,
    p.total_aspect_mentions,
    ROUND(
        100.0 * s.sentiment_count / p.total_aspect_mentions,
        2
    ) AS sentiment_weight_pct
FROM sentiment_counts s
INNER JOIN product_totals p
    ON s.product_id = p.product_id
ORDER BY
    s.product_id,
    sentiment_weight_pct DESC;


-- 5. For each product and aspect, what % of mentions are negative?
--    This measures NEGATIVITY when that aspect is discussed.
--    Minimum 3 mentions avoids treating one-off mentions as strong evidence.
SELECT
    r.product_id,
    r.brand_name,
    r.product_title,
    a.aspect,
    COUNT(*) AS total_aspect_mentions,
    SUM(CASE WHEN a.aspect_sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_mentions,
    ROUND(
        100.0 * SUM(CASE WHEN a.aspect_sentiment = 'negative' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS negative_rate_pct
FROM reviews r
INNER JOIN review_aspects a
    ON r.review_id = a.review_id
GROUP BY
    r.product_id,
    r.brand_name,
    r.product_title,
    a.aspect
HAVING COUNT(*) >= 3
ORDER BY
    negative_rate_pct DESC,
    total_aspect_mentions DESC;


-- 6. Which product pain points deserve priority?
--    negative_rate_pct = severity when the aspect is mentioned
--    negative_weight_pct = how much of ALL product aspect feedback
--                          is this negative issue
WITH product_aspect AS (
    SELECT
        r.product_id,
        r.brand_name,
        r.product_title,
        a.aspect,
        COUNT(*) AS aspect_mentions,
        SUM(CASE WHEN a.aspect_sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_mentions
    FROM reviews r
    INNER JOIN review_aspects a
        ON r.review_id = a.review_id
    GROUP BY
        r.product_id,
        r.brand_name,
        r.product_title,
        a.aspect
),
product_totals AS (
    SELECT
        r.product_id,
        COUNT(*) AS all_aspect_mentions
    FROM reviews r
    INNER JOIN review_aspects a
        ON r.review_id = a.review_id
    GROUP BY r.product_id
)
SELECT
    pa.product_id,
    pa.brand_name,
    pa.product_title,
    pa.aspect,
    pa.aspect_mentions,
    pa.negative_mentions,
    ROUND(
        100.0 * pa.negative_mentions / pa.aspect_mentions,
        2
    ) AS negative_rate_pct,
    ROUND(
        100.0 * pa.negative_mentions / pt.all_aspect_mentions,
        2
    ) AS negative_weight_pct
FROM product_aspect pa
INNER JOIN product_totals pt
    ON pa.product_id = pt.product_id
WHERE pa.negative_mentions > 0
  AND pa.aspect_mentions >= 3
ORDER BY
    negative_weight_pct DESC,
    negative_rate_pct DESC;


-- 7. Which aspects are recurring pain points within each brand?
--    Use rates rather than raw brand counts because the final 970-review
--    sample is not perfectly balanced across brands.
WITH brand_aspect AS (
    SELECT
        r.brand_name,
        a.aspect,
        COUNT(*) AS aspect_mentions,
        SUM(CASE WHEN a.aspect_sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_mentions
    FROM reviews r
    INNER JOIN review_aspects a
        ON r.review_id = a.review_id
    GROUP BY
        r.brand_name,
        a.aspect
),
brand_totals AS (
    SELECT
        r.brand_name,
        COUNT(*) AS all_aspect_mentions
    FROM reviews r
    INNER JOIN review_aspects a
        ON r.review_id = a.review_id
    GROUP BY r.brand_name
)
SELECT
    ba.brand_name,
    ba.aspect,
    ba.aspect_mentions,
    ba.negative_mentions,
    ROUND(
        100.0 * ba.negative_mentions / ba.aspect_mentions,
        2
    ) AS negative_rate_pct,
    ROUND(
        100.0 * ba.negative_mentions / bt.all_aspect_mentions,
        2
    ) AS negative_weight_within_brand_pct
FROM brand_aspect ba
INNER JOIN brand_totals bt
    ON ba.brand_name = bt.brand_name
WHERE ba.negative_mentions > 0
  AND ba.aspect_mentions >= 5
ORDER BY
    ba.brand_name,
    negative_weight_within_brand_pct DESC,
    negative_rate_pct DESC;


-- 8. How does star rating align with LLM-classified overall sentiment?
WITH rating_sentiment AS (
    SELECT
        review_rating,
        overall_sentiment,
        COUNT(*) AS sentiment_count
    FROM reviews
    WHERE review_rating IS NOT NULL
    GROUP BY review_rating, overall_sentiment
),
rating_totals AS (
    SELECT
        review_rating,
        COUNT(*) AS total_reviews
    FROM reviews
    WHERE review_rating IS NOT NULL
    GROUP BY review_rating
)
SELECT
    rs.review_rating,
    rs.overall_sentiment,
    rs.sentiment_count,
    rt.total_reviews,
    ROUND(
        100.0 * rs.sentiment_count / rt.total_reviews,
        2
    ) AS sentiment_pct
FROM rating_sentiment rs
INNER JOIN rating_totals rt
    ON rs.review_rating = rt.review_rating
ORDER BY
    rs.review_rating,
    sentiment_pct DESC;


-- 9. Are larger LISTED discounts associated with more positive
--    price/value feedback?
--    Important: price is a listed product price, NOT confirmed price paid
--    by the reviewer. This is association, not causation.
WITH price_value_reviews AS (
    SELECT
        r.review_id,
        r.product_id,
        r.brand_name,
        r.product_title,
        r.mrp,
        r.price,
        a.aspect_sentiment,
        CASE
            WHEN r.mrp IS NULL OR r.mrp <= 0 OR r.price IS NULL THEN NULL
            ELSE 100.0 * (r.mrp - r.price) / r.mrp
        END AS discount_pct
    FROM reviews r
    INNER JOIN review_aspects a
        ON r.review_id = a.review_id
    WHERE a.aspect = 'price_value'
),
bucketed AS (
    SELECT
        *,
        CASE
            WHEN discount_pct IS NULL THEN 'Unknown'
            WHEN discount_pct <= 0 THEN 'No discount'
            WHEN discount_pct <= 10 THEN '0-10%'
            WHEN discount_pct <= 20 THEN '10-20%'
            WHEN discount_pct <= 30 THEN '20-30%'
            ELSE '30%+'
        END AS discount_band
    FROM price_value_reviews
),
band_counts AS (
    SELECT
        discount_band,
        aspect_sentiment,
        COUNT(*) AS sentiment_count
    FROM bucketed
    WHERE discount_band <> 'Unknown'
    GROUP BY discount_band, aspect_sentiment
),
band_totals AS (
    SELECT
        discount_band,
        COUNT(*) AS total_price_value_mentions
    FROM bucketed
    WHERE discount_band <> 'Unknown'
    GROUP BY discount_band
)
SELECT
    bc.discount_band,
    bc.aspect_sentiment,
    bc.sentiment_count,
    bt.total_price_value_mentions,
    ROUND(
        100.0 * bc.sentiment_count / bt.total_price_value_mentions,
        2
    ) AS sentiment_pct
FROM band_counts bc
INNER JOIN band_totals bt
    ON bc.discount_band = bt.discount_band
ORDER BY
    CASE bc.discount_band
        WHEN 'No discount' THEN 1
        WHEN '0-10%' THEN 2
        WHEN '10-20%' THEN 3
        WHEN '20-30%' THEN 4
        WHEN '30%+' THEN 5
        ELSE 6
    END,
    sentiment_pct DESC;


-- 10. Which products have the highest share of negative/mixed reviews?
--     Minimum 5 sampled reviews reduces unstable rankings.
SELECT
    product_id,
    brand_name,
    product_title,
    COUNT(*) AS sampled_review_count,
    SUM(CASE WHEN overall_sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_reviews,
    SUM(CASE WHEN overall_sentiment = 'mixed' THEN 1 ELSE 0 END) AS mixed_reviews,
    ROUND(
        100.0 * SUM(
            CASE WHEN overall_sentiment IN ('negative', 'mixed') THEN 1 ELSE 0 END
        ) / COUNT(*),
        2
    ) AS negative_or_mixed_pct
FROM reviews
GROUP BY
    product_id,
    brand_name,
    product_title
HAVING COUNT(*) >= 5
ORDER BY
    negative_or_mixed_pct DESC,
    sampled_review_count DESC;


-- 11. What are customers actually complaining about?
--     Use this after identifying an important product/aspect above.
--     It returns the original review text and the LLM-extracted issue.
SELECT
    r.brand_name,
    r.product_title,
    r.review_rating,
    a.aspect,
    a.issue,
    r.review_text
FROM reviews r
INNER JOIN review_aspects a
    ON r.review_id = a.review_id
WHERE a.aspect_sentiment = 'negative'
  AND a.issue IS NOT NULL
ORDER BY
    r.brand_name,
    r.product_title,
    a.aspect;


-- 12. Optional Power BI summary table:
--     one row per product + aspect, with positive/neutral/negative counts.
SELECT
    r.product_id,
    r.brand_name,
    r.product_title,
    a.aspect,
    COUNT(*) AS total_mentions,
    SUM(CASE WHEN a.aspect_sentiment = 'positive' THEN 1 ELSE 0 END) AS positive_mentions,
    SUM(CASE WHEN a.aspect_sentiment = 'neutral' THEN 1 ELSE 0 END) AS neutral_mentions,
    SUM(CASE WHEN a.aspect_sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_mentions,
    ROUND(
        100.0 * SUM(CASE WHEN a.aspect_sentiment = 'negative' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS negative_rate_pct
FROM reviews r
INNER JOIN review_aspects a
    ON r.review_id = a.review_id
GROUP BY
    r.product_id,
    r.brand_name,
    r.product_title,
    a.aspect
ORDER BY
    r.brand_name,
    r.product_title,
    total_mentions DESC;
