"""
run_portfolio_pipeline.py
--------------------------
End-to-End Customer Review Intelligence Pipeline Runner.

Execution Workflow:
1. Load raw review CSV dataset.
2. Clean data using deterministic rules (src.cleaning).
3. Generate a stratified sample of 1,500 reviews (src.sample_reviews).
4. Extract sentiment, aspects, and issues using Gemini LLM (src.simple_llm_extraction).
5. Save structured tables to CSV and SQLite database.
"""

import os
import pandas as pd

from src.cleaning import clean_reviews_dataframe
from src.sample_reviews import create_representative_sample
from src.simple_llm_extraction import process_reviews_batch, save_to_csv_and_sqlite

# Configuration & File Paths
RAW_DATA_PATH = "data/nyka_top_brands_cosmetics_product_reviews.csv"
CLEANED_DATA_PATH = "data/processed/nykaa_cleaned.csv"
SAMPLED_DATA_PATH = "data/processed/sampled_reviews_1500.csv"
DB_PATH = "data/processed/review_intelligence.db"

SAMPLE_SIZE = 1500
RANDOM_SEED = 42
GEMINI_MODEL = "gemini-flash-lite-latest"


def run_portfolio_pipeline():
    """
    Executes the complete portfolio pipeline from raw data to SQLite database.
    """
    print("Starting Customer Review Intelligence Pipeline...")

    # Step 1: Load raw reviews
    print(f"\n[Step 1] Loading raw data from '{RAW_DATA_PATH}'...")
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data file not found: {RAW_DATA_PATH}")

    raw_df = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    print(f"Loaded {len(raw_df):,} raw reviews.")

    # Step 2: Clean data using deterministic rules
    print("\n[Step 2] Cleaning reviews...")
    if not os.path.exists(CLEANED_DATA_PATH):
        clean_df, _ = clean_reviews_dataframe(
            raw_df,
            input_path=RAW_DATA_PATH,
            output_path=CLEANED_DATA_PATH
        )
        print(f"Cleaned dataset saved with {len(clean_df):,} rows.")
    else:
        print(f"Cleaned dataset already exists at: '{CLEANED_DATA_PATH}'")

    # Step 3: Create representative sample (1,500 reviews, seed=42)
    print(f"\n[Step 3] Sampling {SAMPLE_SIZE} reviews (stratified by brand and rating)...")
    if not os.path.exists(SAMPLED_DATA_PATH):
        sampled_df = create_representative_sample(
            input_path=CLEANED_DATA_PATH,
            output_path=SAMPLED_DATA_PATH,
            sample_size=SAMPLE_SIZE,
            random_seed=RANDOM_SEED
        )
    else:
        print(f"Sampled dataset already exists at: '{SAMPLED_DATA_PATH}'")
        sampled_df = pd.read_csv(SAMPLED_DATA_PATH, low_memory=False)

    # Step 4: Extract sentiment, aspects, and issues using Gemini LLM
    print(f"\n[Step 4] Running Gemini LLM extraction ({GEMINI_MODEL})...")
    df_reviews_summary, df_aspects = process_reviews_batch(
        sampled_df,
        model=GEMINI_MODEL,
        checkpoint_interval=50
    )

    # Step 5: Save structured outputs to CSV and SQLite database
    print("\n[Step 5] Saving structured outputs to CSV and SQLite database...")
    save_to_csv_and_sqlite(df_reviews_summary, df_aspects, db_path=DB_PATH)

    print("\nPipeline execution complete!")


if __name__ == "__main__":
    run_portfolio_pipeline()
