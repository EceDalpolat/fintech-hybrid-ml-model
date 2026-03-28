import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from src.config import load_config
from src.data_loader import load_and_merge_data

def check():
    config = load_config()
    df = load_and_merge_data(config)
    target_col = config['data'].get('target', 'pi')
    df = df.dropna(subset=[target_col])
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=config['data'].get('test_size', 0.2), 
        random_state=42
    )

    print(f"Test Set Size: {len(y_test)}")
    
    for i in [50, 100, 150]:
        try:
            model = joblib.load(f"reports/best_model_iter{i}.pkl")
            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)
            f1 = f1_score(y_test, preds, average='weighted')
            print(f"--- Iteration {i} Results ---")
            print(f"Accuracy: {acc:.4f}")
            print(f"F1 Score: {f1:.4f}")
            print(f"Params: {model.named_steps['classifier'].get_params()}")
        except Exception as e:
            print(f"Iter {i} not ready: {e}")

if __name__ == "__main__":
    check()
