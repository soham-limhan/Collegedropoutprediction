"""
Machine Learning model for student dropout prediction.

Provides a small, self-contained interface used by the app and routes:
- MLModel.train_model(df)
- MLModel.predict_dropout_probability(form_data_dict) -> (probability, risk_category, description)
- MLModel.predict_from_form_data(form_data_dict) -> dict

This implementation trains a simple Logistic Regression model if training data
is provided. If unavailable, it falls back to a lightweight heuristic so the
app continues to function.
"""

from __future__ import annotations

from typing import Dict, Any, Tuple, Optional, List

import numpy as np
import pandas as pd

try:
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except Exception:
    # If sklearn is not available at runtime, we will gracefully degrade
    SKLEARN_AVAILABLE = False


class MLModel:
    """Dropout prediction model with safe defaults."""

    def __init__(self) -> None:
        self.model: Optional[LogisticRegression] = None
        self.feature_columns: List[str] = []
        # Probability thresholds for mapping to risk categories
        self.threshold_red: float = 0.66
        self.threshold_yellow: float = 0.33

    # ------------------------------ Public API ------------------------------ #

    def train_model(self, df: pd.DataFrame) -> None:
        """Train a simple logistic regression using available columns.

        Expects df to contain a binary target column `DropoutFlag` (0/1). If not
        present, it will try to derive it from `Risk_Category` (treat Red as 1).
        """
        if df is None or len(df) == 0:
            self.model = None
            self.feature_columns = []
            return

        X, y = self._build_features_and_target(df)

        if X is None or y is None or X.empty or y.empty:
            self.model = None
            self.feature_columns = []
            return

        self.feature_columns = list(X.columns)

        if SKLEARN_AVAILABLE:
            # Use a simple, robust logistic regression
            model = LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                solver="lbfgs",
            )
            model.fit(X, y)
            self.model = model
        else:
            # If sklearn is not available, remain on heuristic mode
            self.model = None

    def predict_dropout_probability(self, form_data: Dict[str, Any]) -> Tuple[float, str, str]:
        """Return (probability, risk_category, risk_description)."""
        prob = self._predict_probability(form_data)
        risk_cat = self._probability_to_risk(prob)
        risk_desc = self._risk_category_to_description(risk_cat)
        return prob, risk_cat, risk_desc

    def predict_from_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary with prediction details."""
        prob, risk_cat, risk_desc = self.predict_dropout_probability(form_data)
        return {
            "probability": round(prob * 100, 2),
            "risk_category": risk_cat,
            "risk_description": risk_desc,
        }

    # ---------------------------- Internal Helpers ------------------------- #

    def _build_features_and_target(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Construct features X and target y from the provided DataFrame.

        Feature engineering prioritizes commonly present columns and gracefully
        handles alternates. All features are numeric and fill missing values.
        """
        work = df.copy()

        # Target: prefer DropoutFlag, else derive from Risk_Category
        if "DropoutFlag" in work.columns:
            y = work["DropoutFlag"].astype(int)
        elif "Risk_Category" in work.columns:
            y = work["Risk_Category"].astype(str).str.strip().str.lower().eq("red").astype(int)
        else:
            return None, None

        # Base numeric features
        work["Aggregate_Grade"] = self._coalesce_grade_columns(work)
        work["Number_of_Absences"] = self._coalesce_absences_columns(work)

        # Optional numeric features if available
        for col in [
            "Age",
            "Study_Time",
            "Number_of_Failures",
            "Health_Status",
            "Mother_Education",
            "Father_Education",
            "Travel_Time",
        ]:
            if col in work.columns:
                work[col] = pd.to_numeric(work[col], errors="coerce")

        # Binary encodings for simple categoricals
        work["Gender_M"] = (
            work.get("Gender", pd.Series(index=work.index, dtype=object))
            .astype(str)
            .str.strip()
            .str.upper()
            .eq("M")
            .astype(int)
        )
        work["Internet_Access_yes"] = (
            work.get("Internet_Access", pd.Series(index=work.index, dtype=object))
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("yes")
            .astype(int)
        )

        candidate_features = [
            "Aggregate_Grade",
            "Number_of_Absences",
            "Age",
            "Study_Time",
            "Number_of_Failures",
            "Health_Status",
            "Mother_Education",
            "Father_Education",
            "Travel_Time",
            "Gender_M",
            "Internet_Access_yes",
        ]

        X = work[[c for c in candidate_features if c in work.columns]].copy()
        X = X.apply(pd.to_numeric, errors="coerce").fillna(0.0)

        return X, y

    def _coalesce_grade_columns(self, df: pd.DataFrame) -> pd.Series:
        if "Aggregate_Grade" in df.columns:
            return pd.to_numeric(df["Aggregate_Grade"], errors="coerce")
        # Fallback: mean of the available grade columns
        parts = []
        for alt in ["Final_Grade", "Grade_2", "Grade_1"]:
            if alt in df.columns:
                parts.append(pd.to_numeric(df[alt], errors="coerce"))
        if parts:
            return pd.concat(parts, axis=1).mean(axis=1)
        return pd.Series(0.0, index=df.index)

    def _coalesce_absences_columns(self, df: pd.DataFrame) -> pd.Series:
        for name in ["Number_of_Absences", "Absences"]:
            if name in df.columns:
                return pd.to_numeric(df[name], errors="coerce")
        return pd.Series(0.0, index=df.index)

    def _vectorize_single(self, form_data: Dict[str, Any]) -> pd.DataFrame:
        """Build a single-row DataFrame with the same columns as training."""
        # Extract with defaults
        def _to_float(val: Any, default: float) -> float:
            try:
                return float(val)
            except (TypeError, ValueError):
                return default

        def _to_int(val: Any, default: int) -> int:
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

        gender = str(form_data.get("gender", "M")).strip().upper()
        internet = str(form_data.get("internet_access", "yes")).strip().lower()

        row = {
            "Aggregate_Grade": _to_float(form_data.get("aggregate_grade", form_data.get("Final_Grade", 12)), 12.0),
            "Number_of_Absences": _to_int(form_data.get("absences", form_data.get("Number_of_Absences", 0)), 0),
            "Age": _to_int(form_data.get("age", 18), 18),
            "Study_Time": _to_int(form_data.get("study_time", form_data.get("Study_Time", 2)), 2),
            "Number_of_Failures": _to_int(form_data.get("number_of_failures", form_data.get("Number_of_Failures", 0)), 0),
            "Health_Status": _to_int(form_data.get("health_status", form_data.get("Health_Status", 3)), 3),
            "Mother_Education": _to_int(form_data.get("mother_education", form_data.get("Mother_Education", 2)), 2),
            "Father_Education": _to_int(form_data.get("father_education", form_data.get("Father_Education", 2)), 2),
            "Travel_Time": _to_int(form_data.get("travel_time", form_data.get("Travel_Time", 1)), 1),
            "Gender_M": 1 if gender == "M" else 0,
            "Internet_Access_yes": 1 if internet == "yes" else 0,
        }

        X = pd.DataFrame([row], dtype=float)

        # Align to training columns if available
        if self.feature_columns:
            for col in self.feature_columns:
                if col not in X.columns:
                    X[col] = 0.0
            X = X[self.feature_columns]

        return X.fillna(0.0)

    def _predict_probability(self, form_data: Dict[str, Any]) -> float:
        # Trained model path
        if self.model is not None and self.feature_columns:
            X = self._vectorize_single(form_data)
            try:
                proba = float(self.model.predict_proba(X)[:, 1][0])
                return max(0.0, min(1.0, proba))
            except Exception:
                # Fall through to heuristic if something goes wrong
                pass

        # Heuristic fallback when model is not trained
        absences = self._safe_float(form_data.get("absences", form_data.get("Number_of_Absences", 0)), 0.0)
        grade = self._safe_float(
            form_data.get("aggregate_grade", form_data.get("Final_Grade", form_data.get("Grade_2", form_data.get("Grade_1", 12)))),
            12.0,
        )
        gender = str(form_data.get("gender", "M")).strip().upper()
        internet = str(form_data.get("internet_access", "yes")).strip().lower()

        # Simple linear score then squashed by sigmoid
        score = 0.0
        score += 0.06 * (absences - 10)  # more absences -> higher risk
        score += -0.08 * (grade - 12)    # higher grade -> lower risk
        score += 0.10 if gender == "M" else 0.0
        score += 0.10 if internet == "no" else 0.0

        prob = 1.0 / (1.0 + np.exp(-score))
        return float(max(0.0, min(1.0, prob)))

    def _probability_to_risk(self, prob: float) -> str:
        if prob >= self.threshold_red:
            return "Red"
        if prob >= self.threshold_yellow:
            return "Yellow"
        return "Green"

    def _risk_category_to_description(self, risk: str) -> str:
        r = str(risk).strip().lower()
        if r == "red":
            return "Required mentorship"
        if r == "yellow":
            return "Requires small attention"
        if r == "green":
            return "Performance is better"
        return "Unknown"

    def _safe_float(self, val: Any, default: float) -> float:
        try:
            return float(val)
        except (TypeError, ValueError):
            return default


