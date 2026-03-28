import unittest
import pandas as pd
import numpy as np
from src.data_loader import engineer_features

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        self.config = {
            'data': {'target': 'pi'},
            'feature_engineering': {'missing_threshold': 0.5}
        }
        self.df = pd.DataFrame({
            'id': [1, 2, 3, 4],
            'pi': [0, 1, 0, 1],
            'amnt': [5, 20, 80, 150],
            'age': [20, 30, 50, 70],
            'hhincome': [1, 2, 3, 4],
            'missing_col': [None, None, None, 1] # 75% missing
        })

    def test_engineer_features_drops_columns(self):
        df_processed = engineer_features(self.df.copy(), self.config)
        self.assertNotIn('missing_col', df_processed.columns)
        self.assertIn('id', df_processed.columns) # Should be safe

    def test_engineer_features_creates_bins(self):
        df_processed = engineer_features(self.df.copy(), self.config)
        self.assertIn('amnt_bin', df_processed.columns)
        self.assertIn('age_group', df_processed.columns)
        self.assertEqual(df_processed['amnt_bin'].iloc[0], 'Low')
        self.assertEqual(df_processed['age_group'].iloc[3], 'Senior')

    def test_interaction_terms(self):
        df_processed = engineer_features(self.df.copy(), self.config)
        self.assertIn('amnt_income_interaction', df_processed.columns)
        self.assertEqual(df_processed['amnt_income_interaction'].iloc[1], 40)

if __name__ == '__main__':
    unittest.main()
