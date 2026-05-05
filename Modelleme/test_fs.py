import pandas as pd
import numpy as np
import logging
from src.config import load_config
from src.data_loader import load_and_merge_data
from src.train import build_preprocessor
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

logging.basicConfig(level=logging.ERROR)
config = load_config()
df = load_and_merge_data(config)
target_col = config['data'].get('target', 'pi')
df = df.dropna(subset=[target_col])

# Aggregation from data_loader
counts = df[target_col].value_counts(normalize=True)
rare_classes = counts[counts < 0.03].index.tolist()
if rare_classes:
    df[target_col] = df[target_col].replace(rare_classes, 99.0)

X = df.drop(columns=[target_col])
y = df[target_col]

le = LabelEncoder()
y_encoded = le.fit_transform(y)
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

preprocessor = build_preprocessor(X_train, fast_mode=True)
fs_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
fs = SelectFromModel(fs_model, threshold='median') # Select top 50% features
rf = RandomForestClassifier(n_estimators=500, max_depth=30, random_state=42, n_jobs=-1)

pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('feature_selection', fs),
    ('classifier', rf)
])

pipe.fit(X_train, y_train)
preds = pipe.predict(X_test)
print(f"RF with Feature Selection Accuracy: {accuracy_score(y_test, preds):.4f}")
