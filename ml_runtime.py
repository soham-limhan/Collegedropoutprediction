"""Train/load logistic regression, persist with joblib, expose metrics and local explanations."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split


def _paths(base_dir: str) -> Tuple[str, str]:
    d = os.path.join(base_dir, "models")
    return os.path.join(d, "dropout_model.joblib"), os.path.join(d, "model_meta.json")


def train_and_save(
    X: pd.DataFrame,
    y: pd.Series,
    feature_names: List[str],
    base_dir: str,
) -> Tuple[LogisticRegression, Dict[str, Any]]:
    """Fit model, compute hold-out metrics, save artifacts."""
    os.makedirs(os.path.join(base_dir, "models"), exist_ok=True)
    strat = y if y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=strat
    )
    model = LogisticRegression(solver="liblinear", random_state=42, max_iter=200)
    model.fit(X_train, y_train)
    proba_test = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    try:
        auc = float(roc_auc_score(y_test, proba_test))
    except Exception:
        auc = None
    meta: Dict[str, Any] = {
        "features": feature_names,
        "metrics": {
            "accuracy": acc,
            "roc_auc": auc,
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
            "n_total": int(len(X)),
        },
        "coefficients": {name: float(c) for name, c in zip(feature_names, model.coef_[0])},
        "intercept": float(model.intercept_[0]),
    }
    mpath, jpath = _paths(base_dir)
    joblib.dump(model, mpath)
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return model, meta


def try_load(base_dir: str) -> Optional[Tuple[LogisticRegression, Dict[str, Any]]]:
    mpath, jpath = _paths(base_dir)
    if not (os.path.isfile(mpath) and os.path.isfile(jpath)):
        return None
    try:
        model = joblib.load(mpath)
        with open(jpath, encoding="utf-8") as f:
            meta = json.load(f)
        return model, meta
    except Exception:
        return None


def load_or_train(
    X: pd.DataFrame,
    y: pd.Series,
    feature_names: List[str],
    base_dir: str,
    data_rows: int,
) -> Tuple[LogisticRegression, Dict[str, Any]]:
    """Load persisted model if meta row count matches; otherwise train."""
    loaded = try_load(base_dir)
    if loaded is not None:
        model, meta = loaded
        if meta.get("metrics", {}).get("n_total") == data_rows and meta.get("features") == feature_names:
            return model, meta
    return train_and_save(X, y, feature_names, base_dir)


def explain_instance(
    model: LogisticRegression,
    feature_names: List[str],
    x: np.ndarray,
) -> List[Dict[str, Any]]:
    """Per-feature contribution coef_i * x_i (local linear explanation)."""
    coef = model.coef_[0]
    out: List[Dict[str, Any]] = []
    for i, name in enumerate(feature_names):
        contrib = float(coef[i] * x[0, i])
        out.append(
            {
                "feature": name,
                "contribution": round(contrib, 5),
                "coefficient": float(coef[i]),
                "value": float(x[0, i]),
            }
        )
    out.sort(key=lambda r: abs(r["contribution"]), reverse=True)
    return out


def retrain_after_data_change(
    X: pd.DataFrame,
    y: pd.Series,
    feature_names: List[str],
    base_dir: str,
) -> Tuple[LogisticRegression, Dict[str, Any]]:
    """Force retrain (e.g. after add/delete student)."""
    return train_and_save(X, y, feature_names, base_dir)
