import sys
import os
import logging
from src.config import load_config
from src.data_loader import load_and_merge_data
from src.train import train_pipeline
from src.utils import setup_logging

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Machine Learning Pipeline")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    try:
        config = load_config()
        logger.info("Configuration loaded successfully.")
    except Exception as e:
        logger.critical(f"Failed to load configuration: {e}", exc_info=True)
        return

    # Load data
    df = load_and_merge_data(config)
    
    if df is not None:
        logger.info("Data is ready for processing.")
        train_pipeline(df, config)
    else:
        logger.warning("No data found or data loading failed.")

if __name__ == "__main__":
    main()
