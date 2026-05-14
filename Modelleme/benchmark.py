import os
import sys
import argparse
import logging
import pandas as pd
from datetime import datetime

# Import local modules
from src.run_thesis_experiments import run_experiment_suite
from src.benchmark_suite import main as run_math_benchmarks
from src.visualize_results import (
    plot_experiment_results, plot_benchmarks,
    plot_convergence_curves, plot_rf_convergence,
    print_results_table,
)

def setup_master_logging():
    logging.basicConfig(
        level=logging.INFO,
        force=True,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("reports/master_benchmark.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("MasterBenchmark")

def main():
    parser = argparse.ArgumentParser(description="Master Benchmark Script for Thesis Results")
    parser.add_argument("--fast", action="store_true", help="Run in fast mode (reduced iterations)")
    parser.add_argument("--skip-math", action="store_true", help="Skip mathematical benchmark validation")
    args = parser.parse_all() if hasattr(parser, 'parse_all') else parser.parse_args()

    os.makedirs("reports", exist_ok=True)
    logger = setup_master_logging()
    
    start_time = datetime.now()
    logger.info("="*50)
    logger.info("🚀 STARTING MASTER BENCHMARK SUITE FOR THESIS")
    logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*50)

    try:
        # Phase 1: Real-Data Experiments (Baseline, PSO, ABC, Hybrid ABC-PSO)
        logger.info("\n[PHASE 1] Running Machine Learning Experiments on Payment Data...")
        # Note: run_experiment_suite reads settings from config.yaml
        run_experiment_suite(config_path="config.yaml")
        
        # Phase 2: Mathematical Benchmarks (sphere, rastrigin, etc.)
        if not args.skip_math:
            logger.info("\n[PHASE 2] Running Mathematical Benchmark Validations...")
            # We call the main function from benchmark_suite
            run_math_benchmarks()
        else:
            logger.info("\n[PHASE 2] Skipping Mathematical Benchmarks as requested.")

        # Phase 3: Visualization & Reporting
        logger.info("\n[PHASE 3] Generating Visualizations and Comparison Reports...")
        plot_experiment_results(json_path="reports/experiment_results.json")
        plot_rf_convergence(json_path="reports/convergence_rf.json")
        print_results_table(json_path="reports/experiment_results.json")
        if not args.skip_math:
            plot_benchmarks(json_path="reports/benchmark_results.json")
            plot_convergence_curves(json_path="reports/benchmark_results.json")

        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("\n" + "="*50)
        logger.info("✅ MASTER BENCHMARK COMPLETED SUCCESSFULLY")
        logger.info(f"Total Duration: {duration}")
        logger.info("Check the 'reports/' folder for all plots and tables.")
        logger.info("="*50)

        # Print quick summary from the exported JSON
        if os.path.exists("reports/experiment_results.json"):
            results_df = pd.read_json("reports/experiment_results.json")
            print("\n📈 QUICK PERFORMANCE SUMMARY:")
            print("-" * 30)
            print(results_df[['method', 'accuracy', 'f1_weighted']].to_string(index=False))
            print("-" * 30)

    except Exception as e:
        logger.error(f"❌ Master Benchmark failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
