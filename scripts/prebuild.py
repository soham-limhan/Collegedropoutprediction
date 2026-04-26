"""
Pre-build script: trains (or re-uses) the ML model and saves the artifacts
to models/dropout_model.joblib + models/model_meta.json so the Netlify
function bundle ships with a ready-to-use model.

Run locally before deploy:
    python scripts/prebuild.py

Netlify runs it automatically via netlify.toml build command.
"""

import os
import sys

# Make project root importable
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

import json
import pandas as pd
import ml_runtime

CSV_FILE = os.path.join(ROOT, "student_dropout_with_risk.csv")
JSON_FILE = os.path.join(ROOT, "students_100.json")
FEATURES = ['Age', 'GPA', 'Absences', 'Financial_Aid', 'Study_Hours', 'Gender_M']
TARGET = 'Dropout'


def build_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out['Age'] = df['Age'] if 'Age' in df.columns else 20
    out['Absences'] = df['Number_of_Absences'] if 'Number_of_Absences' in df.columns else 0
    if 'Grade_1' in df.columns:
        out['GPA'] = (df['Grade_1'] / 20.0 * 4.0).clip(0, 4)
    else:
        out['GPA'] = 3.0
    out['Study_Hours'] = (out['GPA'] * 5).clip(lower=0)
    if 'Internet_Access' in df.columns:
        out['Financial_Aid'] = (
            df['Internet_Access'].astype(str).str.strip().str.lower()
            .map({'yes': 1, 'no': 0}).fillna(0).astype(int)
        )
    else:
        out['Financial_Aid'] = 0
    if 'Gender' in df.columns:
        out['Gender_M'] = df['Gender'].astype(str).str.upper().map({'M': 1, 'F': 0}).fillna(0).astype(int)
    else:
        out['Gender_M'] = 0
    if 'Dropped_Out' in df.columns:
        out['Dropout'] = (df['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes').astype(int).values
    else:
        out['Dropout'] = (df['Risk_Category'].astype(str).str.strip().str.lower() == 'red').astype(int).values
    return out


def main():
    print("[prebuild] Loading student data …")
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
        df = pd.DataFrame(records)
        print(f"[prebuild] Loaded {len(df)} students from JSON.")
    else:
        df = pd.read_csv(CSV_FILE)
        print(f"[prebuild] Loaded {len(df)} students from CSV.")

    training = build_training_frame(df)
    X = training[FEATURES]
    y = training[TARGET]

    print("[prebuild] Training logistic regression model …")
    model, meta = ml_runtime.train_and_save(X, y, FEATURES, ROOT)
    acc = meta.get('metrics', {}).get('accuracy', 0)
    auc = meta.get('metrics', {}).get('roc_auc', None)
    print(f"[prebuild] ✅ Model trained — Accuracy: {acc:.3f}  ROC-AUC: {auc}")
    print(f"[prebuild] Model saved to: {os.path.join(ROOT, 'models', 'dropout_model.joblib')}")


if __name__ == "__main__":
    main()
