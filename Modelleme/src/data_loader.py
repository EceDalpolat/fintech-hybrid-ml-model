import pandas as pd
import os
import numpy as np
import logging
from sklearn.base import BaseEstimator, TransformerMixin

# Setup logger
logger = logging.getLogger(__name__)

class DataFrameSelector(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names):
        self.attribute_names = attribute_names
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return X[self.attribute_names]

def load_and_merge_data(config):
    """
    Load individual and transaction datasets, merge them, and perform initial cleaning.
    
    Args:
        config (dict): Configuration dictionary.
        
    Returns:
        pd.DataFrame: Merged and processed dataframe.
    """
    
    ind_path = config['data']['ind_path']
    tran_path = config['data']['tran_path']
    
    if not os.path.exists(ind_path) or not os.path.exists(tran_path):
        logger.error(f"One or more data files not found: {ind_path}, {tran_path}")
        return None
        
    try:
        logger.info("Loading datasets...")
        ind_df = pd.read_csv(ind_path, low_memory=False)
        tran_df = pd.read_csv(tran_path, low_memory=False)
        
        logger.info(f"Individual data shape: {ind_df.shape}")
        logger.info(f"Transaction data shape: {tran_df.shape}")
        
        logger.info("Merging datasets...")
        merged_df = pd.merge(tran_df, ind_df, on='id', how='left')
        logger.info(f"Merged data shape: {merged_df.shape}")
        
        # Basic Date Processing
        if 'date' in merged_df.columns:
            logger.info("Processing date column...")
            merged_df['date'] = pd.to_datetime(merged_df['date'], format='%Y-%m-%d', errors='coerce')
            merged_df['month'] = merged_df['date'].dt.month
            merged_df['day'] = merged_df['date'].dt.day
            merged_df['day_of_week'] = merged_df['date'].dt.dayofweek
            merged_df['is_weekend'] = merged_df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
            # Payday usually happens around 15th or end of month (30/31)
            merged_df['is_payday'] = merged_df['day'].apply(lambda x: 1 if x in [1, 2, 14, 15, 16, 30, 31] else 0)
            merged_df.drop(columns=['date'], inplace=True)
            
        # Drop columns defined in config
        drop_cols = config.get('feature_engineering', {}).get('drop_cols', [])
        existing_cols_to_drop = [c for c in drop_cols if c in merged_df.columns]
        if existing_cols_to_drop:
            logger.info(f"Dropping columns: {existing_cols_to_drop}")
            merged_df.drop(columns=existing_cols_to_drop, inplace=True)
        
        # Advanced Feature Engineering
        merged_df = engineer_features(merged_df, config)
        
        logger.info(f"Final processed data shape: {merged_df.shape}")
        return merged_df
        
    except Exception as e:
        logger.error(f"Error loading/processing data: {e}", exc_info=True)
        return None

def engineer_features(df, config):
    """
    Apply advanced feature engineering.
    """
    logger.info("Applying advanced feature engineering...")
    
    # 1. Drop columns with too many missing values
    threshold = config.get('feature_engineering', {}).get('missing_threshold', 0.8)
    null_pct = df.isnull().mean()
    drop_cols = null_pct[null_pct > threshold].index.tolist()
    
    # Ensure we don't drop target or essential keys
    target_col = config['data'].get('target', 'pi')
    safe_cols = ['id', target_col]
    drop_cols = [c for c in drop_cols if c not in safe_cols]
    
    if drop_cols:
        logger.info(f"Dropping {len(drop_cols)} columns with > {threshold*100}% missing values.")
        df.drop(columns=drop_cols, inplace=True)

    # 2. Amount Processing (Log Transform)
    if 'amnt' in df.columns:
        df['amnt'] = df['amnt'].fillna(0)
        # Log-transform is usually better for skewed currency data
        df['log_amnt'] = np.log1p(df['amnt'])
        
        # Keep binning as well but more granular
        bins = [-1, 5, 20, 50, 150, float('inf')]
        labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
        df['amnt_bin'] = pd.cut(df['amnt'], bins=bins, labels=labels)
        
    # 3. Binning 'age'
    if 'age' in df.columns:
        median_age = df['age'].median()
        df['age'] = df['age'].fillna(median_age)
        bins = [0, 18, 30, 50, 70, 120]
        labels = ['Student', 'Young-Adult', 'Mid-Career', 'Steady', 'Senior']
        df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels)

    # 4. Temporal Features (Payday etc.)
    # We had 'month' and 'is_weekend' from load_and_merge_data
    # Let's add 'is_payday' (around 15th and end of month)
    # Note: 'day' column needs to be extracted if available
    
    # 5. Interaction Features
    if 'hhincome' in df.columns and 'log_amnt' in df.columns:
        df['amnt_income_interaction'] = df['log_amnt'] * (df['hhincome'].fillna(1))

    return df
