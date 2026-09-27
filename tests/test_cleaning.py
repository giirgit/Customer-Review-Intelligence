"""
tests/test_cleaning.py
-----------------------
Unit tests for deterministic Pandas cleaning operations.
"""

import unittest
import pandas as pd
from src.cleaning import strip_html_tags, normalize_whitespace, clean_reviews_dataframe

class TestCleaning(unittest.TestCase):
    def test_strip_html_tags(self):
        self.assertEqual(strip_html_tags("Great product! <br/><b>Highly recommended</b>"), "Great product! Highly recommended")
        self.assertEqual(strip_html_tags("No tags here"), "No tags here")

    def test_normalize_whitespace(self):
        self.assertEqual(normalize_whitespace("  Lots of   extra    spaces \n and newlines\t "), "Lots of extra spaces and newlines")

    def test_clean_reviews_dataframe(self):
        raw_data = pd.DataFrame({
            "review_id": ["REV_1", "REV_2", "REV_3", "REV_4"],
            "product_id": ["P1", "P1", "P2", "P3"],
            "review_text": [
                "  <br/>Amazing item!  ",
                "   ",
                "Good product",
                "Broken item"
            ],
            "rating": [5.0, 4.0, 6.0, 1.0],
            "review_date": ["2024-01-01", "2024-01-02", "2024-01-03", None]
        })

        df_cleaned, summary = clean_reviews_dataframe(raw_data, input_path="test.csv", output_path=None)

        self.assertEqual(summary["rows_before"], 4)
        self.assertEqual(summary["rows_after"], 2)
        self.assertEqual(summary["rows_removed_total"], 2)
        self.assertEqual(df_cleaned["review_text"].iloc[0], "Amazing item!")

if __name__ == "__main__":
    unittest.main()
