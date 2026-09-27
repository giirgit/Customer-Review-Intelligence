-- ============================================================================
-- SQLITE DATABASE SCHEMA & TECHNICAL VALIDATION QUERIES
-- Database Path: data/processed/review_intelligence.db
-- Purpose: Technical database creation and data load verification
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. DATABASE SCHEMA CREATION
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    overall_sentiment TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS review_aspects (
    aspect_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id TEXT NOT NULL,
    aspect TEXT NOT NULL,
    aspect_sentiment TEXT NOT NULL,
    issue TEXT,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 2. TECHNICAL VALIDATION QUERIES
-- ----------------------------------------------------------------------------

-- Check Row Counts
SELECT 'reviews' AS table_name, COUNT(*) AS row_count FROM reviews
UNION ALL
SELECT 'review_aspects' AS table_name, COUNT(*) AS row_count FROM review_aspects;

-- Verify Primary Key Uniqueness on reviews table
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT review_id) AS distinct_ids,
    CASE 
        WHEN COUNT(*) = COUNT(DISTINCT review_id) THEN 'PASS: All review_ids are unique'
        ELSE 'FAIL: Duplicate review_ids detected'
    END AS primary_key_status
FROM reviews;

-- Foreign Key Integrity Check
PRAGMA foreign_key_check;

-- Table Schema Information
PRAGMA table_info(reviews);
PRAGMA table_info(review_aspects);
