import yaml
import pandas as pd
from src.data_loader import load_and_merge_data
import logging
logging.basicConfig(level=logging.DEBUG)

with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Run just the merging part
def debug_load(config):
    ind_path = config['data']['ind_path']
    tran_path = config['data']['tran_path']
    ind_df = pd.read_csv(ind_path, low_memory=False, nrows=100)
    tran_df = pd.read_csv(tran_path, low_memory=False, nrows=100)
    print("ind_df columns:", ind_df.columns.tolist()[:5])
    print("tran_df columns:", tran_df.columns.tolist()[:5])
    merged_df = pd.merge(tran_df, ind_df, on='id', how='left')
    print("merged_df columns:", merged_df.columns.tolist()[:5])
    return merged_df

df = debug_load(config)
try:
    print('Testing groupby id:')
    trans_counts = df.groupby('id').size()
    print('Success')
except Exception as e:
    print(f'Error: {repr(e)}')

import sys
sys.exit(0)
