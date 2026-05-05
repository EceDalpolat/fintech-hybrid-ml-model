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
            merged_df['is_month_end'] = merged_df['date'].dt.is_month_end.astype(int)
            merged_df['is_month_start'] = merged_df['date'].dt.is_month_start.astype(int)
            merged_df.drop(columns=['date'], inplace=True)
            
        # Advanced Feature Engineering (must run before dropping 'id')
        merged_df = aggregate_user_behavior(merged_df)
        merged_df = engineer_features(merged_df, config)
        
        # Target Class Aggregation (to boost accuracy for minority classes)
        target_col = config['data'].get('target', 'pi')
        if target_col in merged_df.columns:
            merged_df = aggregate_target_classes(merged_df, target_col, threshold=0.03)

        # Drop columns defined in config
        drop_cols = config.get('feature_engineering', {}).get('drop_cols', [])
        existing_cols_to_drop = [c for c in drop_cols if c in merged_df.columns]
        if existing_cols_to_drop:
            logger.info(f"Dropping columns: {existing_cols_to_drop}")
            merged_df.drop(columns=existing_cols_to_drop, inplace=True)
        
        logger.info(f"Final processed data shape: {merged_df.shape}")
        return merged_df
        
    except Exception as e:
        logger.error(f"Error loading/processing data: {e}", exc_info=True)
        return None

def aggregate_user_behavior(df):
    """
    Generate user-centric features to capture behavioral patterns.
    """
    logger.info("Aggregating user behavior...")
    
    # 1. Transaction Frequency
    trans_counts = df.groupby('id').size().reset_index(name='user_trans_count')
    df = pd.merge(df, trans_counts, on='id', how='left')
    
    # 2. Amount Aggregates
    if 'amnt' in df.columns:
        amt_aggs = df.groupby('id')['amnt'].agg(['mean', 'std', 'max']).reset_index()
        amt_aggs.columns = ['id', 'user_avg_amnt', 'user_std_amnt', 'user_max_amnt']
        df = pd.merge(df, amt_aggs, on='id', how='left')
        df['user_std_amnt'] = df['user_std_amnt'].fillna(0) # For users with 1 transaction
        
    # 3. Categorical Diversity (How many different payment types does this user use?)
    if 'pi' in df.columns:
        pi_diversity = df.groupby('id')['pi'].nunique().reset_index(name='user_pi_diversity')
        df = pd.merge(df, pi_diversity, on='id', how='left')
        
    return df

def handle_outliers(df, columns, method='iqr', action='suppress', z_thresh=3.0):
    """
    Handle outliers in numerical columns using IQR or Z-Score.
    
    Args:
        df (pd.DataFrame): Input dataframe.
        columns (list): List of numerical columns.
        method (str): 'iqr' or 'zscore'.
        action (str): 'suppress' (capping) or 'drop'.
        z_thresh (float): Z-Score threshold.
        
    Returns:
        pd.DataFrame: Processed dataframe.
    """
    df_out = df.copy()
    for col in columns:
        if col not in df_out.columns:
            continue
            
        if method == 'iqr':
            Q1 = df_out[col].quantile(0.25)
            Q3 = df_out[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
        else: # zscore
            mean = df_out[col].mean()
            std = df_out[col].std()
            lower_bound = mean - z_thresh * std
            upper_bound = mean + z_thresh * std
            
        if action == 'suppress':
            df_out[col] = np.clip(df_out[col], lower_bound, upper_bound)
            logger.debug(f"Suppressed outliers for {col} using {method}")
        elif action == 'drop':
            initial_count = len(df_out)
            df_out = df_out[(df_out[col] >= lower_bound) & (df_out[col] <= upper_bound)]
            logger.debug(f"Dropped {initial_count - len(df_out)} outlier rows for {col}")
            
    return df_out

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
        
        # --- NEW: Outlier Suppression (Z-Score & IQR) as discussed ---
        # We first suppress outliers on absolute amnt before log transform
        df = handle_outliers(df, ['amnt'], method='iqr', action='suppress')
        
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
        
        # --- NEW: Outlier Suppression for Age ---
        df = handle_outliers(df, ['age'], method='zscore', action='suppress', z_thresh=3.0)
        
        bins = [0, 18, 30, 50, 70, 120]
        labels = ['Student', 'Young-Adult', 'Mid-Career', 'Steady', 'Senior']
        df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels)

    # 5. Interaction Features
    if 'hhincome' in df.columns and 'log_amnt' in df.columns:
        df['amnt_income_interaction'] = df['log_amnt'] * (df['hhincome'].fillna(1))
        # NEW: Ratio of amount to estimated monthly income (assuming income is annual)
        df['amnt_income_ratio'] = df['amnt'] / (df['hhincome'].fillna(1).replace(0, 1) / 12)

    return df

def aggregate_target_classes(df, target_col, threshold=0.05):
    """
    Groups classes with frequency lower than threshold into a single class (99.0).
    """
    logger.info(f"Checking for rare classes in {target_col} (threshold={threshold})...")
    counts = df[target_col].value_counts(normalize=True)
    rare_classes = counts[counts < threshold].index.tolist()
    
    if rare_classes:
        logger.info(f"Aggregating {len(rare_classes)} rare classes into '99.0': {rare_classes}")
        df[target_col] = df[target_col].replace(rare_classes, 99.0)
        
    return df

