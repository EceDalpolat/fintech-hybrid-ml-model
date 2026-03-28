import unittest
import pandas as pd
from src.train import build_preprocessor
from sklearn.pipeline import Pipeline

class TestModel(unittest.TestCase):
    def setUp(self):
        self.X = pd.DataFrame({
            'numeric_col': [1.0, 2.0, 3.0],
            'categorical_col': ['a', 'b', 'a']
        })

    def test_build_preprocessor(self):
        preprocessor = build_preprocessor(self.X)
        transformers = preprocessor.transformers
        self.assertEqual(len(transformers), 2)
        
        # Check if numeric and categorical columns are correctly identified
        num_cols = transformers[0][2]
        cat_cols = transformers[1][2]
        
        self.assertIn('numeric_col', num_cols)
        self.assertIn('categorical_col', cat_cols)

if __name__ == '__main__':
    unittest.main()
