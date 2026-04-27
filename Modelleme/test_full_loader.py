import yaml
import logging
from src.data_loader import load_and_merge_data

logging.basicConfig(level=logging.DEBUG)

with open('config.yaml') as f:
    config = yaml.safe_load(f)

merged_df = load_and_merge_data(config)
if merged_df is not None:
    print("Success, merged_df shape:", merged_df.shape)
else:
    print("Function returned None")
