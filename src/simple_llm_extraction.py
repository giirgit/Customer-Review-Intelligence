"""
Extracts structured information from customer reviews using Gemini.

For each review, the model identifies:
- overall sentiment
- product aspects
- sentiment for each aspect
- specific customer issues

Progress is saved periodically so extraction can resume if interrupted.
"""

import os
import json
import time
import sqlite3
from typing import List, Optional
import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv(override=True)

# -------------------------------------------------------------
# PYDANTIC STRUCTURED OUTPUT SCHEMA
# -------------------------------------------------------------

class AspectItem(BaseModel):
    aspect: str = Field(
        description="Standardized product aspect name (e.g., shade_match, pigmentation, coverage, texture, application, longevity, packaging, fragrance, finish, price_value, quantity, effectiveness, hair_effect, skin_feel, scalp_effect, formula, quality)"
    )
    aspect_sentiment: str = Field(
        description="Sentiment for this specific aspect: 'positive', 'neutral', or 'negative'"
    )
    issue: Optional[str] = Field(
        default=None,
        description="Concise description of the problem if aspect_sentiment is negative or mixed, otherwise null"
    )


class ReviewExtractionResult(BaseModel):
    overall_sentiment: str = Field(
        description="Overall sentiment category: 'positive', 'neutral', 'negative', or 'mixed'."
    )
    aspects: List[AspectItem] = Field(
        default_factory=list,
        description="List of distinct product aspects explicitly discussed in the review text."
    )


# -------------------------------------------------------------
# GEMINI SYSTEM PROMPT & CLIENT
# -------------------------------------------------------------

SYSTEM_PROMPT = """You are an objective Customer Review Intelligence AI.
Your job is to convert unstructured customer feedback into structured intelligence.

STRICT SEMANTIC RULES:
1. overall_sentiment MUST be one of: ["positive", "neutral", "negative", "mixed"].
   - Read the ENTIRE review before classifying sentiment.
   - Use "mixed" when meaningful positive AND negative opinions are BOTH present in the review.
   - Negation matters deeply:
     - "not good" / "not great" is NEGATIVE or NEUTRAL, NOT positive.
     - "without causing hairfall" or "no hairfall" is NOT a hairfall complaint.
     - "Anti Hair Fall" / "Anti-dandruff" is a claimed product benefit, NOT evidence that the product caused hairfall.
   - Explicit satisfaction statements (e.g. "I am satisfied", "loved it") are "positive", NOT neutral.

2. aspects list:
   - Extract EVERY distinct product aspect explicitly supported by the review text.
   - Do NOT invent aspects or complaints not present in the text.
   - Do NOT force an aspect when the review is vague (e.g. "Good product" -> aspects: []).
   - Use concise, standardized aspect names for SQL grouping (examples: shade_match, pigmentation, coverage, texture, application, longevity, packaging, fragrance, finish, price_value, quantity, effectiveness, hair_effect, skin_feel, scalp_effect, formula, quality).
   - A review may legitimately discuss multiple aspects.

3. aspect_sentiment MUST be one of: ["positive", "neutral", "negative"].

4. issue:
   - If the customer explicitly describes a specific problem, store a concise, specific description in "issue" (e.g. "causes hairfall and dryness", "too expensive for 6ml", "requires a separate sharpener").
   - Set "issue" to null if no problem is described or if aspect_sentiment is positive/neutral.
"""


def get_gemini_client():
    """Instantiates Google GenAI client using GEMINI_API_KEY from environment."""
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() == "" or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is missing or set to placeholder in .env file.")
    return genai.Client(api_key=api_key)


# -------------------------------------------------------------
# SINGLE REVIEW EXTRACTION
# -------------------------------------------------------------

def extract_single_review(review_id, review_text, model="gemini-flash-lite-latest"):
    """
    Extracts overall sentiment, aspects, and issues for a single review using Gemini.
    Retries temporary rate-limit (429) errors, but fails immediately on auth errors.
    """
    user_prompt = f'REVIEW TEXT:\n"{review_text}"'
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            client = get_gemini_client()
            response = client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ReviewExtractionResult,
                    temperature=0.0
                )
            )
            data = json.loads(response.text)
            result = ReviewExtractionResult(**data).model_dump()
            result["review_id"] = str(review_id)
            result["extraction_method"] = "llm"
            return result

        except Exception as err:
            err_str = str(err).lower()

            # Fail fast on authentication, API key, permission, or billing errors
            if any(k in err_str for k in ["401", "api_key", "permission", "unauthenticated", "billing", "forbidden"]):
                print(f"[AUTH ERROR] Unrecoverable Gemini API error on review {review_id}: {err}")
                raise err

            # Retry on temporary rate-limit errors (429 / resource_exhausted)
            if any(k in err_str for k in ["429", "resource_exhausted", "quota"]):
                if attempt < max_retries:
                    wait_time = 15 * attempt
                    print(f"Rate limit reached on review {review_id} (attempt {attempt}/{max_retries}). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[RATE LIMIT ERROR] Rate limit persisted after {max_retries} attempts: {err}")
                    raise err

            # Any other unexpected network or API error: raise and stop
            print(f"[API ERROR] Gemini extraction failed on review {review_id}: {err}")
            raise err


# -------------------------------------------------------------
# CHECKPOINT & RESUME HELPERS
# -------------------------------------------------------------

def load_existing_checkpoint(csv_dir="data/processed"):
    """
    Loads existing reviews_summary.csv and review_aspects.csv if present.
    Returns (df_reviews, df_aspects, set_of_processed_review_ids).
    """
    reviews_csv = os.path.join(csv_dir, "reviews_summary.csv")
    aspects_csv = os.path.join(csv_dir, "review_aspects.csv")

    processed_ids = set()
    df_reviews = pd.DataFrame()
    df_aspects = pd.DataFrame()

    if os.path.exists(reviews_csv):
        try:
            df_reviews = pd.read_csv(reviews_csv, dtype={"review_id": str})
            if not df_reviews.empty and "review_id" in df_reviews.columns:
                df_reviews = df_reviews.drop_duplicates(subset=["review_id"]).copy()
                processed_ids = set(df_reviews["review_id"].astype(str).str.strip())
        except Exception as e:
            print(f"Warning: could not read existing {reviews_csv}: {e}")

    if os.path.exists(aspects_csv):
        try:
            df_aspects = pd.read_csv(aspects_csv, dtype={"review_id": str})
            if not df_aspects.empty and "review_id" in df_aspects.columns:
                df_aspects = df_aspects[df_aspects["review_id"].astype(str).str.strip().isin(processed_ids)].copy()
        except Exception as e:
            print(f"Warning: could not read existing {aspects_csv}: {e}")

    return df_reviews, df_aspects, processed_ids


def save_checkpoint(df_reviews, df_aspects, csv_dir="data/processed"):
    """Saves current reviews and aspects DataFrames to checkpoint CSV files."""
    os.makedirs(csv_dir, exist_ok=True)
    reviews_csv = os.path.join(csv_dir, "reviews_summary.csv")
    aspects_csv = os.path.join(csv_dir, "review_aspects.csv")

    df_reviews_clean = df_reviews.drop_duplicates(subset=["review_id"]).copy()
    df_reviews_clean.to_csv(reviews_csv, index=False)
    df_aspects.to_csv(aspects_csv, index=False)


# -------------------------------------------------------------
# BATCH EXTRACTION ORCHESTRATOR
# -------------------------------------------------------------

def process_reviews_batch(
    reviews_df,
    model=None,
    checkpoint_interval=50,
    csv_dir="data/processed"
):
    """
    Processes a DataFrame of reviews with checkpoint/resume support.
    Extracts sentiment, aspects, and complaints using Gemini.
    """
    selected_model = model or os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    df_existing_reviews, df_existing_aspects, processed_ids = load_existing_checkpoint(csv_dir)

    # Filter for reviews that have not been processed yet
    reviews_to_process = reviews_df[~reviews_df["review_id"].astype(str).str.strip().isin(processed_ids)].copy()
    total_requested = len(reviews_df)
    already_done = total_requested - len(reviews_to_process)

    if already_done > 0:
        print(f"Resuming: {already_done:,} reviews already processed. {len(reviews_to_process):,} remaining.")
    else:
        print(f"Starting Gemini extraction for {total_requested:,} reviews...")

    if reviews_to_process.empty:
        print("All requested reviews have already been processed.")
        return df_existing_reviews, df_existing_aspects

    reviews_list = df_existing_reviews.to_dict("records") if not df_existing_reviews.empty else []
    aspects_list = df_existing_aspects.to_dict("records") if not df_existing_aspects.empty else []

    for i, (_, row) in enumerate(reviews_to_process.iterrows(), 1):
        r_id = str(row["review_id"]).strip()
        r_text = str(row["review_text"])

        print(f"[{i}/{len(reviews_to_process)}] Extracting Review ID {r_id} via Gemini...")
        time.sleep(4.1)  # Free-tier rate limit pacing (~15 requests per minute)

        extracted = extract_single_review(r_id, r_text, model=selected_model)

        # Build review-level record preserving all original columns from the row
        review_record = row.to_dict()
        review_record["review_id"] = r_id
        review_record["overall_sentiment"] = extracted.get("overall_sentiment", "neutral")
        review_record["extraction_method"] = "llm"
        reviews_list.append(review_record)

        # Build aspect-level records
        for asp in extracted.get("aspects", []):
            aspects_list.append({
                "review_id": r_id,
                "aspect": str(asp.get("aspect", "")).strip().lower().replace(" ", "_"),
                "aspect_sentiment": str(asp.get("aspect_sentiment", "neutral")).strip().lower(),
                "issue": asp.get("issue")
            })

        # Save checkpoint periodically or on the last item
        if i % checkpoint_interval == 0 or i == len(reviews_to_process):
            df_cur_reviews = pd.DataFrame(reviews_list)
            df_cur_aspects = pd.DataFrame(aspects_list)
            save_checkpoint(df_cur_reviews, df_cur_aspects, csv_dir=csv_dir)
            print(f"Checkpoint saved: {len(df_cur_reviews):,} total reviews saved.")

    df_final_reviews = pd.DataFrame(reviews_list)
    df_final_aspects = pd.DataFrame(aspects_list)

    print(f"Completed extraction. Total reviews: {len(df_final_reviews):,}, Total aspects: {len(df_final_aspects):,}.")
    return df_final_reviews, df_final_aspects


# -------------------------------------------------------------
# CSV & SQLITE SAVING LOGIC
# -------------------------------------------------------------

def save_to_csv_and_sqlite(
    df_reviews,
    df_aspects,
    csv_dir="data/processed",
    db_path="data/processed/review_intelligence.db"
):
    """
    Saves final extracted DataFrames to CSV files and loads them into SQLite database.
    """
    os.makedirs(csv_dir, exist_ok=True)
    output_dir = os.path.dirname(db_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    reviews_csv_path = os.path.join(csv_dir, "reviews_summary.csv")
    aspects_csv_path = os.path.join(csv_dir, "review_aspects.csv")

    df_reviews_clean = df_reviews.drop_duplicates(subset=["review_id"]).copy()

    df_reviews_clean.to_csv(reviews_csv_path, index=False)
    df_aspects.to_csv(aspects_csv_path, index=False)

    print(f"Saved CSV: '{reviews_csv_path}' ({len(df_reviews_clean):,} rows)")
    print(f"Saved CSV: '{aspects_csv_path}' ({len(df_aspects):,} rows)")

    # SQLite Database Persistence
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS review_aspects;")
    cursor.execute("DROP TABLE IF EXISTS reviews;")

    cursor.execute("""
        CREATE TABLE reviews (
            review_id TEXT PRIMARY KEY,
            product_id TEXT,
            brand_name TEXT,
            product_title TEXT,
            review_title TEXT,
            review_text TEXT,
            review_date TEXT,
            review_rating REAL,
            is_a_buyer INTEGER,
            pro_user INTEGER,
            review_label TEXT,
            mrp REAL,
            price REAL,
            product_rating REAL,
            product_rating_count REAL,
            product_tags TEXT,
            product_url TEXT,
            overall_sentiment TEXT NOT NULL,
            extraction_method TEXT NOT NULL DEFAULT 'llm'
        );
    """)

    cursor.execute("""
        CREATE TABLE review_aspects (
            aspect_id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id TEXT NOT NULL,
            aspect TEXT NOT NULL,
            aspect_sentiment TEXT NOT NULL,
            issue TEXT,
            FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE
        );
    """)

    df_reviews_clean.to_sql("reviews", conn, if_exists="append", index=False)
    if not df_aspects.empty:
        df_aspects.to_sql("review_aspects", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    print(f"Database loaded successfully: '{db_path}'")
