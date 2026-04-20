# Classification of Payment Preferences in Digital Payment Systems using Hybrid Machine Learning Models

This repository contains the source code and methodology for the thesis titled **"Classification of Payment Preferences in Digital Payment Systems using Hybrid Machine Learning Models: A DCPC 2024 Analysis"**.

## Project Overview
This project implements a high-performance machine learning pipeline to classify consumer payment preferences (PI) using transaction and individual-level data. The primary contribution is the development and evaluation of a hybrid **ABC-PSO (Artificial Bee Colony - Particle Swarm Optimization)** algorithm for hyperparameter optimization of Random Forest and KNN models.

## Key Features

### 1. Advanced Preprocessing & Feature Engineering
- **Outlier Management**: Strategic use of Z-Score and Robust IQR methods for noise reduction and suppression.
- **Missing Value Imputation**: Implementation of **KNN Imputation** for high-fidelity data recovery.
- **Hybrid Categorical Encoding**: Combination of **One-Hot Encoding** (for low cardinality) and **Target Encoding** (for high cardinality).
- **Feature Extraction**: Domain-specific features including temporal interactions (payday, month-end), transaction velocity, and income ratios.

### 2. Hybrid Optimization (ABC-PSO)
- **PSO Component**: Accelerates convergence towards global optima.
- **ABC Component**: Enhances exploration through onlooker and scout bee mechanisms.
- **Hybrid Integration**: Combines the strengths of both meta-heuristics for a "Best Accuracy Push".

### 3. Interpretability & Reporting
- **SHAP Analysis**: Global and local feature importance using SHapley Additive exPlanations.
- **Convergence Plots**: Visual comparison of PSO, ABC, and Hybrid ABC-PSO performance.
- **Comprehensive Metrics**: Accuracy, F1-Weighted, Precision, and Recall comparison tables.

## Project Structure
- `Modelleme/src/`: Core source code (DataLoader, Algorithms, Trainers).
- `Modelleme/data/`: Placeholder for raw and processed datasets.
- `Modelleme/reports/`: Generated plots, SHAP summaries, and performance tables.
- `Modelleme/run_full_thesis_pipeline.py`: Master script to execute the entire experiment suite.

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Configure your paths and parameters in `config.yaml`.
3. Run the analysis: `python run_full_thesis_pipeline.py`

---
*Developed as part of the TEZ project by Ece Dalpolat.*