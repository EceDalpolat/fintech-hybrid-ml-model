import os
import sys
from run_full_thesis_pipeline import run_full_pipeline

def main():
    print("Generating actual final results instead of dummy data...")
    # Ensure we are in the Modellme directory
    if os.path.basename(os.getcwd()) != "Modelleme":
        print("Please run this script from the 'Modelleme' directory.")
        sys.exit(1)
        
    run_full_pipeline("config.yaml")

if __name__ == "__main__":
    main()
