import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Ensure src can be imported
sys.path.append(os.getcwd())

from src.config import load_config
from src.data_loader import load_and_merge_data

def generate_eda_report():
    print("Loading configuration...")
    config = load_config()
    
    print("Loading data...")
    df = load_and_merge_data(config)
    
    if df is None:
        print("Data loading failed.")
        return

    report_path = "reports/eda_summary.md"
    os.makedirs("reports", exist_ok=True)
    
    with open(report_path, "w") as f:
        f.write("# Exploratory Data Analysis Report\n\n")
        
        # 1. Data Structure
        f.write("## 1. Data Structure\n")
        f.write(f"- **Rows**: {df.shape[0]}\n")
        f.write(f"- **Columns**: {df.shape[1]}\n\n")
        f.write("### Columns:\n")
        f.write("```\n")
        for col in df.columns:
            f.write(f"{col}: {df[col].dtype}\n")
        f.write("```\n\n")
        
        # 2. Missing Values
        f.write("## 2. Missing Values\n")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if missing.empty:
            f.write("No missing values found.\n")
        else:
            f.write("| Column | Missing Count | Percentage |\n")
            f.write("|---|---|---|\n")
            for col, count in missing.items():
                pct = (count / len(df)) * 100
                f.write(f"| {col} | {count} | {pct:.2f}% |\n")
        f.write("\n")
        
        # 3. Target Distribution
        target = config['data']['target']
        f.write(f"## 3. Target Distribution ({target})\n")
        if target in df.columns:
            dist = df[target].value_counts(normalize=True) * 100
            f.write("| Class | Percentage |\n")
            f.write("|---|---|\n")
            for cls, pct in dist.items():
                f.write(f"| {cls} | {pct:.2f}% |\n")
                
            # Plot
            plt.figure(figsize=(10, 6))
            sns.countplot(x=target, data=df)
            plt.title(f"Distribution of {target}")
            plt.savefig("reports/target_distribution.png")
            f.write("\n![Target Distribution](target_distribution.png)\n")
        else:
            f.write(f"Target column '{target}' not found.\n")
            
        # 4. Numerical & Feature Analysis
        f.write("\n## 4. Feature Analysis (New Engineering)\n")
        
        # Log Amnt Distribution
        if 'log_amnt' in df.columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(df['log_amnt'], kde=True)
            plt.title("Distribution of Log Transformed Amount")
            plt.savefig("reports/log_amnt_dist.png")
            f.write("### Log Transformed Amount\n")
            f.write("![Log Amnt](log_amnt_dist.png)\n\n")

        # Age Group Distribution
        if 'age_group' in df.columns:
            plt.figure(figsize=(10, 6))
            sns.countplot(x='age_group', data=df)
            plt.title("Distribution of Age Groups")
            plt.xticks(rotation=45)
            plt.savefig("reports/age_group_dist.png")
            f.write("### Age Groups\n")
            f.write("![Age Group](age_group_dist.png)\n\n")

        # Temporal Analysis
        if 'is_payday' in df.columns:
            payday_counts = df['is_payday'].value_counts(normalize=True) * 100
            f.write(f"### Payday Transactions: {payday_counts.get(1, 0):.2f}%\n\n")

        # 5. Numerical Summary
        f.write("\n## 5. Numerical Summary\n")
        desc = df.describe()
        f.write(desc.to_markdown())
        
        print(f"EDA report generated at {report_path}")

if __name__ == "__main__":
    generate_eda_report()
