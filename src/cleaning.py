"""
src/cleaning.py
---------------
Deterministic Data Cleaning Module for Customer Reviews.

Applies clean, rule-based Pandas operations on raw cosmetics review data:
1. Removes missing or empty review text and strips HTML tags.
2. Strips whitespace from review_title, author, and brand_name.
3. Validates review_rating to ensure values are between 1.0 and 5.0.
4. Parses review_date into datetime format without dropping rows.
5. Converts price and mrp to numeric values while preserving anomalies.
6. Preserves optional fields (review_label, product_tags) without filling artificial values.
"""

import os
import re
import pandas as pd

DEFAULT_INPUT_PATH = "data/nyka_top_brands_cosmetics_product_reviews.csv"
DEFAULT_OUTPUT_PATH = "data/processed/nykaa_cleaned.csv"


def strip_html_tags(text):
    """Removes HTML tags from a text string."""
    if isinstance(text, str):
        return re.sub(r"<[^<]+?>", "", text).strip()
    return ""


def normalize_whitespace(text):
    """Strips and normalizes consecutive whitespace in a string."""
    if isinstance(text, str):
        return " ".join(text.split())
    return ""


def clean_reviews_dataframe(
    df,
    input_path=DEFAULT_INPUT_PATH,
    output_path=DEFAULT_OUTPUT_PATH
):
    """
    Cleans the raw reviews DataFrame using deterministic Pandas rules.

    Returns:
        tuple: (cleaned_df, report_dict)
    """
    df = df.copy()
    rows_before = len(df)

    # 1. Clean review_text: remove missing values, strip HTML tags and whitespace
    df = df.dropna(subset=["review_text"]).copy()
    df["review_text"] = df["review_text"].astype(str).str.replace(r"<[^<]+?>", "", regex=True).str.strip()
    df = df[df["review_text"] != ""].copy()

    # 2. Clean review_title: strip whitespace, keep missing values as NaN
    if "review_title" in df.columns:
        df["review_title"] = df["review_title"].str.strip()

    # 3. Clean author: strip whitespace, keep missing values as NaN
    if "author" in df.columns:
        df["author"] = df["author"].str.strip()

    # 4. Clean brand_name: strip whitespace, keep missing values as NaN
    if "brand_name" in df.columns:
        df["brand_name"] = df["brand_name"].str.strip()

    # 5. Clean review_rating: keep only valid numeric ratings between 1.0 and 5.0
    rating_col = "review_rating" if "review_rating" in df.columns else ("rating" if "rating" in df.columns else None)
    if rating_col:
        df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
        df = df[df[rating_col].between(1.0, 5.0)].copy()

    # 6. Parse review_date to datetime (preserve rows even if date is missing)
    if "review_date" in df.columns:
        df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")

    # 7. Convert price and mrp to numeric (anomalies preserved per project guidelines)
    for col in ["price", "mrp"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 8. Ensure boolean flags remain boolean
    for bool_col in ["is_a_buyer", "pro_user"]:
        if bool_col in df.columns:
            df[bool_col] = df[bool_col].astype(bool)

    # Calculate summary metrics
    rows_after = len(df)
    rows_removed = rows_before - rows_after

    report = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_removed,
        "rows_removed_total": rows_removed,
        "missing_values_after": df.isnull().sum().to_dict(),
    }

    # Save cleaned dataset if output_path is provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Cleaned dataset saved to: '{output_path}'")

    return df, report
