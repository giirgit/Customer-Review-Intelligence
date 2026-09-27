"""
Creates a representative sample of reviews from the cleaned dataset.

Uses stratified sampling across brand_name and review_rating with a fixed
random seed (42) to maintain fair representation of brands and ratings.
"""

import os
import pandas as pd

CLEANED_DATA_PATH = "data/processed/nykaa_cleaned.csv"
SAMPLED_OUTPUT_PATH = "data/processed/sampled_reviews_1500.csv"


def create_representative_sample(
    input_path=CLEANED_DATA_PATH,
    output_path=SAMPLED_OUTPUT_PATH,
    sample_size=1500,
    random_seed=42
):
    """
    Selects a stratified sample of reviews based on brand_name and review_rating.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}")

    df = pd.read_csv(input_path, low_memory=False)
    print(f"Loaded cleaned dataset with {len(df):,} total rows.")

    # 1. Filter out missing or empty review text
    df = df[df["review_text"].notna() & (df["review_text"].astype(str).str.strip() != "")].copy()

    # 2. Check available rows against requested sample size
    if len(df) <= sample_size:
        sampled_df = df.copy()
    else:
        # 3. Stratified sampling by brand_name and review_rating
        strat_cols = [col for col in ["brand_name", "review_rating"] if col in df.columns]

        if strat_cols:
            fraction = sample_size / len(df)
            sampled_df = df.groupby(strat_cols, group_keys=False, observed=False).apply(
                lambda group: group.sample(frac=fraction, random_state=random_seed) if len(group) > 0 else group
            )

            # Adjust to exact sample_size if needed due to group-level rounding
            if len(sampled_df) > sample_size:
                sampled_df = sampled_df.sample(n=sample_size, random_state=random_seed)
            elif len(sampled_df) < sample_size:
                remaining_indices = df.index.difference(sampled_df.index)
                needed = sample_size - len(sampled_df)
                extra_rows = df.loc[remaining_indices].sample(n=needed, random_state=random_seed)
                sampled_df = pd.concat([sampled_df, extra_rows])
        else:
            # Fallback random sample if stratification columns are missing
            sampled_df = df.sample(n=sample_size, random_state=random_seed)

    # 4. Reset index and save output
    sampled_df = sampled_df.reset_index(drop=True)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    sampled_df.to_csv(output_path, index=False)
    print(f"Saved {len(sampled_df):,} sampled reviews to '{output_path}'.")

    return sampled_df
