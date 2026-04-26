import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, make_response
from io import StringIO
import json
from typing import Any, Dict, Optional
import os
from collections import OrderedDict
import math
import requests as http_requests

import ml_runtime

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
except ImportError:
    Limiter = None  # type: ignore
    get_remote_address = None  # type: ignore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Detect Netlify serverless environment (set in netlify.toml [build.environment])
IS_NETLIFY = os.environ.get("NETLIFY", "").lower() in ("true", "1", "yes")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-change-me-in-production")

if Limiter is not None:
    limiter = Limiter(get_remote_address, app=app, default_limits=["400 per day", "120 per hour"])
else:
    limiter = None


def _rate_limit(rule: str):
    """Apply rate limit if Flask-Limiter is installed."""
    def decorator(fn):
        if limiter is not None:
            return limiter.limit(rule)(fn)
        return fn
    return decorator

CSV_FILENAME = 'student_dropout_with_risk.csv'
JSON_OUTPUT_FILENAME = 'students_100.json'

# --- 1. LOAD CSV, CREATE JSON, AND LIGHTWEIGHT MODEL SETUP ---
# In a real application, you would connect to MySQL and load a pre-trained model.

def load_students_from_csv(csv_path: str, limit: Optional[int] = 100) -> pd.DataFrame:
    """Load first N students from CSV, ensure a Name column with human-friendly names, include some Red-category students, and return DataFrame."""
    full_df = pd.read_csv(csv_path)
    df = full_df.copy() if limit is None else full_df.head(limit).copy()

    # Ensure at least some red-category students are present (target at least 5)
    target_min_red = 5
    risk_col = 'Risk_Category' if 'Risk_Category' in full_df.columns else None
    if risk_col is not None:
        def _norm(val):
            return str(val).strip().lower()
        current_red = df[df[risk_col].apply(_norm) == 'red']
        if len(current_red) < target_min_red:
            needed = target_min_red - len(current_red)
            pool_red = full_df[full_df[risk_col].apply(_norm) == 'red']
            pool_red = pool_red.iloc[limit:] if len(pool_red) > limit else pool_red
            # Exclude rows already in df by index if overlapping
            pool_red = pool_red[~pool_red.index.isin(df.index)]
            if needed > 0 and len(pool_red) > 0:
                add_rows = pool_red.head(needed)
                # Replace the last 'needed' non-red rows in df with these red rows
                non_red_idx = df[df[risk_col].apply(_norm) != 'red'].index.tolist()
                replace_idx = non_red_idx[-len(add_rows):] if len(non_red_idx) >= len(add_rows) else non_red_idx
                for rep_i, add_row in zip(replace_idx, add_rows.to_dict(orient='records')):
                    df.loc[rep_i] = add_row

    # Add human-friendly names if missing
    if 'Name' not in df.columns:
        first_names = [
            'Aarav','Aditi','Arjun','Isha','Kabir','Kavya','Rohan','Saanvi','Vihaan','Zara',
            'Ananya','Dev','Ira','Meera','Neel','Reyansh','Sara','Tara','Veda','Yash'
        ]
        last_names = [
            'Sharma','Verma','Patel','Iyer','Mukherjee','Gupta','Kapoor','Singh','Khan','Das',
            'Bose','Ghosh','Mehta','Varma','Nair','Kulkarni','Chopra','Reddy','Jain','Tripathi'
        ]
        names = []
        for i in range(len(df)):
            fn = first_names[i % len(first_names)]
            ln = last_names[i % len(last_names)]
            names.append(f"{fn} {ln}")
        df['Name'] = names

    # Add risk description mapping column for convenience
    if risk_col is not None:
        def describe_risk(val: str) -> str:
            v = str(val).strip().lower()
            if v == 'red':
                return 'Required mentorship'
            if v == 'yellow':
                return 'Requires small attention'
            if v == 'green':
                return 'Performance is better'
            return 'Unknown'
        df['Risk_Description'] = df[risk_col].apply(describe_risk)

    return df

def write_students_json(df: pd.DataFrame, json_path: str) -> None:
    """Write the given DataFrame to a JSON file (records orientation)."""
    # Ensure native JSON types
    records = json.loads(df.to_json(orient='records'))
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def write_students_csv(df: pd.DataFrame, csv_path: str) -> None:
    """Write the DataFrame to CSV."""
    df.to_csv(csv_path, index=False, encoding='utf-8')

def load_students_initial(csv_path: str, json_path: str) -> pd.DataFrame:
    """Load persisted students preferring JSON; fall back to full CSV and persist to JSON.
    This ensures adds/deletes survive app restarts.
    """
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
            df = pd.DataFrame(records)
            if not df.empty:
                return df
        except Exception:
            pass
    # Fallback to CSV (load full dataset, not truncated)
    df = load_students_from_csv(csv_path, limit=None)
    # Persist to JSON for future startups
    write_students_json(df, json_path)
    return df

# Load students from JSON if available, else full CSV; persist to JSON
_csv_path = os.path.join(os.path.dirname(__file__), CSV_FILENAME)
_json_path = os.path.join(os.path.dirname(__file__), JSON_OUTPUT_FILENAME)
STUDENTS_DF = load_students_initial(_csv_path, _json_path)

DASHBOARD_DATA = STUDENTS_DF.copy()

# --- Simple illustrative ML model using a few engineered features from CSV ---
# This keeps the existing predictor demo functional with available columns.

def build_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Build a minimal training frame using available CSV columns.
    We map: Age -> Age, Number_of_Absences -> Absences, Risk_Score -> Study_Hours proxy,
    Gender -> Gender_M, Internet_Access -> Financial_Aid proxy.
    """
    out = pd.DataFrame()
    out['Age'] = df['Age'] if 'Age' in df.columns else 20
    out['Absences'] = df['Number_of_Absences'] if 'Number_of_Absences' in df.columns else 0
    # Use Grade_1 as a rough GPA proxy if present; else fallback to 3.0
    if 'Grade_1' in df.columns:
        out['GPA'] = (df['Grade_1'] / 20.0 * 4.0).clip(0, 4)
    else:
        out['GPA'] = 3.0
    # Use Risk_Score as a rough inverse of Study_Hours proxy
    out['Study_Hours'] = (out['GPA'] * 5).clip(lower=0) if 'Risk_Score' not in df.columns else (20 - (df['Risk_Score'] - df['Risk_Score'].min())).clip(lower=0)
    # Map Internet_Access yes/no to 1/0 as financial aid proxy
    if 'Internet_Access' in df.columns:
        out['Financial_Aid'] = df['Internet_Access'].astype(str).str.strip().str.lower().map({'yes': 1, 'no': 0}).fillna(0).astype(int)
    else:
        out['Financial_Aid'] = 0
    # Gender_M
    if 'Gender' in df.columns:
        out['Gender_M'] = df['Gender'].astype(str).str.upper().map({'M': 1, 'F': 0}).fillna(0).astype(int)
    else:
        out['Gender_M'] = 0
    if 'Dropped_Out' in df.columns:
        out['Dropout'] = (df['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes').astype(int).values
    else:
        out['Dropout'] = (df['Risk_Category'].astype(str).str.strip().str.lower() == 'red').astype(int).values
    return out


def _rebuild_dashboard_dropout(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    if 'Dropped_Out' in d.columns:
        d['DropoutFlag'] = (d['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes').astype(int)
    else:
        d['DropoutFlag'] = (d['Risk_Category'].astype(str).str.strip().str.lower() == 'red').astype(int)
    return d


FEATURES = ['Age', 'GPA', 'Absences', 'Financial_Aid', 'Study_Hours', 'Gender_M']
TARGET = 'Dropout'

DASHBOARD_DATA = _rebuild_dashboard_dropout(DASHBOARD_DATA)
TRAINING_DF = build_training_frame(DASHBOARD_DATA)
X = TRAINING_DF[FEATURES]
y = TRAINING_DF[TARGET]

model, MODEL_META = ml_runtime.load_or_train(X, y, FEATURES, BASE_DIR, len(STUDENTS_DF))

MODEL_FEATURES = FEATURES


def refresh_ml_stack() -> None:
    """Retrain logistic model after student data changes."""
    global model, MODEL_META, TRAINING_DF, DASHBOARD_DATA
    DASHBOARD_DATA = _rebuild_dashboard_dropout(STUDENTS_DF)
    TRAINING_DF = build_training_frame(DASHBOARD_DATA)
    Xn = TRAINING_DF[FEATURES]
    yn = TRAINING_DF[TARGET]
    model, MODEL_META = ml_runtime.retrain_after_data_change(Xn, yn, FEATURES, BASE_DIR)


print(f"Loaded {len(STUDENTS_DF)} students from CSV and wrote {JSON_OUTPUT_FILENAME}.")

# --- 2. FLASK ROUTES ---

@app.route('/')
def home():
    """Serves the homepage with Add Student and Quick Predictor."""
    return render_template('home.html')


@app.route('/dashboard')
def index():
    """Serves the interactive dashboard page."""
    return render_template('dashboard.html')

@app.route('/add_student', methods=['POST'])
def add_student():
    """Add a new student to the in-memory dataset and rewrite the JSON (first 100)."""
    global STUDENTS_DF, DASHBOARD_DATA
    try:
        data = request.json or {}
        # --- Input constraints & normalization ---
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        gender = (data.get('gender') or 'M').strip().upper()
        if gender not in ('M', 'F'):
            return jsonify({'error': 'Gender must be M or F'}), 400
        try:
            age = int(data.get('age', 18))
        except Exception:
            return jsonify({'error': 'Age must be an integer'}), 400
        if age < 10 or age > 60:
            return jsonify({'error': 'Age must be between 10 and 60'}), 400
        try:
            absences = int(data.get('absences', 0))
        except Exception:
            return jsonify({'error': 'Absences must be an integer'}), 400
        if absences < 0 or absences > 365:
            return jsonify({'error': 'Absences must be between 0 and 365'}), 400
        try:
            agg = float(data.get('aggregate_grade', 12))
        except Exception:
            return jsonify({'error': 'Aggregate grade must be a number'}), 400
        if agg < 0 or agg > 20:
            return jsonify({'error': 'Aggregate grade must be between 0 and 20'}), 400
        internet = str(data.get('internet_access', 'yes')).strip().lower()
        if internet not in ('yes', 'no'):
            return jsonify({'error': 'Internet access must be yes or no'}), 400
        desired_zone = (data.get('desired_risk_zone') or '').strip()
        if desired_zone and desired_zone not in ('Red', 'Yellow', 'Green'):
            return jsonify({'error': 'Desired risk zone must be Red, Yellow, or Green'}), 400

        # Build a single-row frame from incoming data, mapping to CSV-like columns
        row = {}
        row['Name'] = name or f"Student {len(STUDENTS_DF) + 1}"
        row['Gender'] = gender
        row['Age'] = age
        row['Number_of_Absences'] = absences
        row['Aggregate_Grade'] = agg
        row['Grade_1'] = agg
        row['Grade_2'] = agg
        row['Final_Grade'] = agg
        row['Internet_Access'] = internet
        row['School'] = data.get('school', 'GP')
        row['Address'] = data.get('address', 'U')
        row['Family_Size'] = data.get('family_size', 'GT3')
        row['Parental_Status'] = data.get('parental_status', 'T')
        row['Mother_Education'] = data.get('mother_education', 2)
        row['Father_Education'] = data.get('father_education', 2)
        row['Travel_Time'] = data.get('travel_time', 1)
        row['Study_Time'] = data.get('study_time', 2)
        row['Number_of_Failures'] = data.get('number_of_failures', 0)
        row['Health_Status'] = data.get('health_status', 3)

        # Build features for prediction using same mapping as training
        gender_m = 1 if str(row['Gender']).upper() == 'M' else 0
        gpa = max(0.0, min(4.0, (row['Aggregate_Grade'] / 20.0) * 4.0))
        financial_aid = 1 if str(row['Internet_Access']).strip().lower() == 'yes' else 0
        # Study hours proxy: from GPA if no risk score given
        risk_score = data.get('risk_score')
        if risk_score is not None:
            try:
                risk_score = float(risk_score)
            except Exception:
                risk_score = None
        if risk_score is None:
            study_hours = max(0.0, gpa * 5)
        else:
            # Mirror earlier mapping: higher risk score implies fewer hours
            # Use current dataset min for stability
            if 'Risk_Score' in STUDENTS_DF.columns and len(STUDENTS_DF) > 0:
                base_min = float(STUDENTS_DF['Risk_Score'].min())
            else:
                base_min = 0.0
            study_hours = max(0.0, 20 - (risk_score - base_min))

        features = np.array([[row['Age'], gpa, row['Number_of_Absences'], financial_aid, study_hours, gender_m]])
        prob = float(model.predict_proba(features)[0][1])
        if prob >= 0.66:
            predicted_risk = 'Red'
            risk_desc = 'Required mentorship'
        elif prob >= 0.33:
            predicted_risk = 'Yellow'
            risk_desc = 'Requires small attention'
        else:
            predicted_risk = 'Green'
            risk_desc = 'Performance is better'

        # Rule-based overrides (priority: Red > Yellow > Green)
        # - if absences >= 20 and aggregate grade < 7: Red
        # - else if absences >= 15 and aggregate grade < 15: Yellow
        # - else if absences >= 5 and aggregate grade > 15: Green
        if absences >= 20 and agg < 7:
            predicted_risk = 'Red'
            risk_desc = 'Required mentorship'
        elif absences >= 15 and agg < 15:
            predicted_risk = 'Yellow'
            risk_desc = 'Requires small attention'
        elif absences >= 5 and agg > 15:
            predicted_risk = 'Green'
            risk_desc = 'Performance is better'

        if desired_zone in ['Red', 'Yellow', 'Green']:
            risk_cat = desired_zone
        else:
            risk_cat = predicted_risk

        row['Risk_Category'] = risk_cat
        row['Risk_Description'] = risk_desc
        row['Risk_Score'] = round(prob * 100, 2)

        # Append to STUDENTS_DF
        STUDENTS_DF = pd.concat([STUDENTS_DF, pd.DataFrame([row])], ignore_index=True)
        # Rewrite JSON and CSV to persist across restarts
        write_students_json(STUDENTS_DF, os.path.join(os.path.dirname(__file__), JSON_OUTPUT_FILENAME))
        write_students_csv(STUDENTS_DF, os.path.join(os.path.dirname(__file__), CSV_FILENAME))
        # Reload DataFrame from JSON for consistency
        with open(os.path.join(os.path.dirname(__file__), JSON_OUTPUT_FILENAME), 'r', encoding='utf-8') as f:
            STUDENTS_DF = pd.DataFrame(json.load(f))
        refresh_ml_stack()
        return jsonify({'status': 'ok', 'risk_category': risk_cat, 'probability': round(prob * 100, 2)})
    except Exception as e:
        app.logger.error(f"Add student error: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/students')
def students():
    """Return the latest 100 students with names and risk info (tail)."""
    df = STUDENTS_DF.tail(100).copy()
    # Sort by Risk_Category: Red (0), Yellow (1), Green (2), others (3)
    def _rank(val):
        v = str(val).strip().lower()
        if v == 'red':
            return 0
        if v == 'yellow':
            return 1
        if v == 'green':
            return 2
        return 3
    if 'Risk_Category' in df.columns:
        df['__risk_order'] = df['Risk_Category'].apply(_rank)
        df = df.sort_values(['__risk_order'], kind='stable').drop(columns=['__risk_order'])
    # Include original global index for stable editing
    df['_idx'] = df.index.astype(int)
    records = json.loads(df.to_json(orient='records'))
    resp = make_response(jsonify(records))
    resp.headers['Cache-Control'] = 'no-store'
    return resp

@app.route('/risk_summary')
def risk_summary():
    """Return counts for red/yellow/green and total students."""
    try:
        if 'Risk_Category' in STUDENTS_DF.columns:
            cats = STUDENTS_DF['Risk_Category'].astype(str).str.strip().str.lower()
            red = int((cats == 'red').sum())
            yellow = int((cats == 'yellow').sum())
            green = int((cats == 'green').sum())
        else:
            # Fallback using DropoutFlag if Risk_Category not present
            flags = DASHBOARD_DATA['DropoutFlag'] if 'DropoutFlag' in DASHBOARD_DATA.columns else pd.Series([0] * len(STUDENTS_DF))
            red = int(flags.sum())
            yellow = 0
            green = int(len(STUDENTS_DF) - red)
        total = int(len(STUDENTS_DF))
        return jsonify({'total': total, 'red': red, 'yellow': yellow, 'green': green})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict', methods=['POST'])
@_rate_limit("30 per minute")
def predict():
    """API endpoint for receiving student data and returning a prediction."""
    try:
        data = request.json or {}

        gender_m = 1 if data.get('gender') == 'M' else 0

        row = [[
            float(data.get('age', 20)),
            float(data.get('gpa', 3.0)),
            float(data.get('absences', 5)),
            float(data.get('financial_aid', 0)),
            float(data.get('study_hours', 20)),
            gender_m
        ]]
        input_df = pd.DataFrame(row, columns=MODEL_FEATURES)
        probability = float(model.predict_proba(input_df)[0][1])
        explanation = ml_runtime.explain_instance(model, MODEL_FEATURES, input_df.values)

        result: Dict[str, Any] = {
            'ok': True,
            'probability': round(probability * 100, 2),
            'prediction_text': "HIGH RISK" if probability > 0.5 else "LOW RISK",
            'explanation': explanation[:4],
            'model_metrics': MODEL_META.get('metrics', {}),
        }

        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Prediction error: {e}")
        return jsonify({'ok': False, 'error': {'code': 'predict_failed', 'message': str(e)}}), 400


@app.route('/api/model_metrics')
def api_model_metrics():
    """Hold-out metrics and coefficients for the current model."""
    return jsonify({'ok': True, 'meta': MODEL_META, 'features': MODEL_FEATURES})


@app.route('/export/students.csv')
def export_students_csv():
    """Download full student table as CSV."""
    buf = StringIO()
    STUDENTS_DF.to_csv(buf, index=False)
    resp = make_response(buf.getvalue())
    resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
    resp.headers['Content-Disposition'] = 'attachment; filename=students_export.csv'
    return resp


@app.route('/dashboard_data')
def dashboard_data():
    """API endpoint to fetch data required for dashboard charts."""
    # 1. Dropout by Gender (using DropoutFlag)
    gender_col = 'Gender' if 'Gender' in DASHBOARD_DATA.columns else None
    absences_col = 'Number_of_Absences' if 'Number_of_Absences' in DASHBOARD_DATA.columns else None

    if gender_col is not None:
        gender_dropout = DASHBOARD_DATA.groupby(gender_col)['DropoutFlag'].agg(['mean', 'count']).reset_index()
        gender_dropout['Dropout_Rate'] = round(gender_dropout['mean'] * 100, 1)
        gender_records = gender_dropout.rename(columns={gender_col: 'Gender'})[['Gender', 'Dropout_Rate']].to_dict('records')
    else:
        gender_records = []

    # 2. Dropout by Absences Bins
    if absences_col is not None:
        DASHBOARD_DATA['Absence_Level'] = pd.cut(
            DASHBOARD_DATA[absences_col],
            bins=[-0.1, 10, 20, 1000],
            include_lowest=True,
            right=False,
            labels=['Low', 'Medium', 'High']
        )
        absences_dropout = (
            DASHBOARD_DATA
            .groupby('Absence_Level', observed=True)['DropoutFlag']
            .mean()
            .reset_index()
        )
        absences_dropout['Dropout_Rate'] = round(absences_dropout['DropoutFlag'] * 100, 1)
        absences_records = absences_dropout[['Absence_Level', 'Dropout_Rate']].to_dict('records')
    else:
        absences_records = []

    return jsonify({
        'gender_data': json.loads(json.dumps(gender_records)),
        'absences_data': json.loads(json.dumps(absences_records))
    })


@app.route('/mentor_advice', methods=['POST'])
def mentor_advice():
    """Return mentor advice for a given student name or index using heuristics from JSON data."""
    try:
        data = request.json or {}
        name = (data.get('name') or '').strip()
        index = data.get('index')

        # Load latest persisted dataset
        json_path = os.path.join(os.path.dirname(__file__), JSON_OUTPUT_FILENAME)
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
            df = pd.DataFrame(records)
        else:
            df = STUDENTS_DF.copy()

        sel = None
        if index is not None and str(index) != '':
            try:
                i = int(index)
                if i < 0 or i >= len(df):
                    return jsonify({'error': 'Index out of range'}), 400
                sel = df.iloc[i].to_dict()
            except Exception:
                return jsonify({'error': 'Invalid index'}), 400
        elif name:
            mask = df['Name'].astype(str).str.strip().str.lower() == name.lower()
            if not mask.any():
                return jsonify({'error': 'Student not found'}), 404
            sel = df[mask].iloc[0].to_dict()
        else:
            return jsonify({'error': 'Provide name or index'}), 400

        # Helpers to sanitize numbers for JSON
        def _to_int_safe(v, default=0):
            try:
                if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) or pd.isna(v):
                    return default
                return int(v)
            except Exception:
                return default

        def _to_float_or_none(v):
            try:
                if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) or pd.isna(v):
                    return None
                f = float(v)
                if math.isnan(f) or math.isinf(f):
                    return None
                return f
            except Exception:
                return None

        # Extract features
        absences_val = sel.get('Number_of_Absences', sel.get('Absences', 0))
        absences = _to_int_safe(absences_val, 0)
        agg_val = sel.get('Aggregate_Grade', sel.get('Final_Grade', sel.get('Grade_2', sel.get('Grade_1', 12))))
        agg = _to_float_or_none(agg_val)
        if agg is None:
            agg = 12.0
        risk_cat = str(sel.get('Risk_Category', '')).strip() or 'Unknown'
        internet = str(sel.get('Internet_Access', 'yes')).strip().lower()
        health = _to_float_or_none(sel.get('Health_Status'))
        failures = _to_int_safe(sel.get('Number_of_Failures'), 0)

        # Heuristic advice rules (extendable)
        advice = []
        if risk_cat.lower() == 'red' or (absences >= 20 and agg < 7):
            advice.append('Assign a dedicated mentor and weekly check-ins.')
            advice.append('Create a structured study plan with daily goals.')
            advice.append('Coordinate with parents/guardians for support alignment.')
        elif risk_cat.lower() == 'yellow' or (absences >= 15 and agg < 15):
            advice.append('Schedule bi-weekly mentorship sessions focusing on weak subjects.')
            advice.append('Encourage peer study groups and provide practice resources.')
        else:
            advice.append('Maintain current progress with monthly check-ins.')
            advice.append('Offer enrichment materials to sustain motivation.')

        if absences >= 10:
            advice.append('Implement attendance accountability and address root causes of absence.')
        if internet == 'no':
            advice.append('Provide offline study materials and campus resource access.')
        if isinstance(failures, (int, float)) and failures > 0:
            advice.append('Remediation plan for previously failed subjects.')
        if isinstance(health, (int, float)) and health is not None and health <= 2:
            advice.append('Consult counseling/health services to address wellbeing concerns.')

        # Remove duplicates while preserving order
        advice = list(OrderedDict.fromkeys(advice))

        return jsonify({
            'student': sel.get('Name', 'Student'),
            'risk_category': risk_cat,
            'absences': absences,
            'aggregate_grade': round(agg, 2) if agg is not None else None,
            'advice': advice
        })
    except Exception as e:
        app.logger.error(f"mentor_advice error: {e}")
        return jsonify({'error': str(e)}), 400



@app.route('/students_view')
def students_view():
    return render_template('students_view.html')


@app.route('/print_report')
def print_report():
    return render_template('print_report.html')

@app.route('/edit_student', methods=['GET', 'POST'])
def edit_student():
    """Edit a student by index. GET serves form, POST updates the record.
    Supports both 'index' (visible order) and 'gindex' (global DataFrame index).
    """
    global STUDENTS_DF, DASHBOARD_DATA
    # Prefer global index if provided
    if request.method == 'GET':
        idx_str = request.args.get('gindex') or request.args.get('index')
    else:
        body = request.json or {}
        idx_str = request.args.get('gindex') or request.args.get('index') or body.get('gindex') or body.get('index')
    try:
        if idx_str is None:
            return jsonify({'error': 'index is required'}), 400
        idx = int(idx_str)
        if idx < 0 or idx >= len(STUDENTS_DF):
            return jsonify({'error': 'index out of range'}), 400
    except Exception:
        return jsonify({'error': 'invalid index'}), 400

    if request.method == 'GET':
        s = json.loads(STUDENTS_DF.iloc[[idx]].to_json(orient='records'))[0]
        rz = str(s.get('Risk_Category') or '').strip()
        if rz not in ('Red', 'Yellow', 'Green'):
            rz = ''
        return render_template(
            'edit_student.html',
            idx=idx,
            name=str(s.get('Name', '')),
            gender=s.get('Gender', ''),
            age=s.get('Age', ''),
            absences=s.get('Number_of_Absences', s.get('Absences', '')),
            aggregate=s.get('Aggregate_Grade', s.get('Final_Grade', s.get('Grade_2', s.get('Grade_1', '')))),
            internet=str(s.get('Internet_Access', '')).lower(),
            risk_zone=rz,
        )

    # POST: update record
    try:
        data = request.json or {}
        # Update basic fields
        if 'name' in data:
            STUDENTS_DF.at[idx, 'Name'] = data['name']
        if 'gender' in data:
            STUDENTS_DF.at[idx, 'Gender'] = data['gender']
        if 'age' in data:
            STUDENTS_DF.at[idx, 'Age'] = int(data['age'])
        if 'absences' in data:
            STUDENTS_DF.at[idx, 'Number_of_Absences'] = int(data['absences'])
        if 'internet_access' in data:
            STUDENTS_DF.at[idx, 'Internet_Access'] = str(data['internet_access']).lower()
        if 'aggregate_grade' in data:
            try:
                agg = float(data['aggregate_grade'])
            except Exception:
                agg = None
            if agg is not None:
                STUDENTS_DF.at[idx, 'Aggregate_Grade'] = agg
                STUDENTS_DF.at[idx, 'Grade_1'] = agg
                STUDENTS_DF.at[idx, 'Grade_2'] = agg
                STUDENTS_DF.at[idx, 'Final_Grade'] = agg

        # Recompute risk using ML + rule overrides on the updated row
        desired = str(data.get('desired_risk_zone') or '').strip()
        row_now = STUDENTS_DF.iloc[idx].to_dict()
        gender_m = 1 if str(row_now.get('Gender', '')).upper() == 'M' else 0
        agg_now = float(row_now.get('Aggregate_Grade', row_now.get('Final_Grade', row_now.get('Grade_2', row_now.get('Grade_1', 12)))))
        gpa_now = max(0.0, min(4.0, (agg_now / 20.0) * 4.0))
        absences_now = int(row_now.get('Number_of_Absences', row_now.get('Absences', 0)))
        internet_now = str(row_now.get('Internet_Access', 'yes')).strip().lower()
        financial_aid_now = 1 if internet_now == 'yes' else 0
        # Estimate study hours similar to add_student logic
        if 'Risk_Score' in STUDENTS_DF.columns and len(STUDENTS_DF) > 0:
            base_min_now = float(STUDENTS_DF['Risk_Score'].min())
        else:
            base_min_now = 0.0
        study_hours_now = max(0.0, gpa_now * 5)

        features_now = np.array([[row_now.get('Age', 18), gpa_now, absences_now, financial_aid_now, study_hours_now, gender_m]])
        prob_now = float(model.predict_proba(features_now)[0][1])
        if prob_now >= 0.66:
            predicted_risk_now = 'Red'
            risk_desc_now = 'Required mentorship'
        elif prob_now >= 0.33:
            predicted_risk_now = 'Yellow'
            risk_desc_now = 'Requires small attention'
        else:
            predicted_risk_now = 'Green'
            risk_desc_now = 'Performance is better'

        # Rule-based overrides (priority: Red > Yellow > Green)
        if absences_now >= 20 and agg_now < 7:
            predicted_risk_now = 'Red'
            risk_desc_now = 'Required mentorship'
        elif absences_now >= 15 and agg_now < 15:
            predicted_risk_now = 'Yellow'
            risk_desc_now = 'Requires small attention'
        elif absences_now >= 5 and agg_now > 15:
            predicted_risk_now = 'Green'
            risk_desc_now = 'Performance is better'

        if desired in ['Red', 'Yellow', 'Green']:
            STUDENTS_DF.at[idx, 'Risk_Category'] = desired
            STUDENTS_DF.at[idx, 'Risk_Description'] = risk_desc_now
        else:
            STUDENTS_DF.at[idx, 'Risk_Category'] = predicted_risk_now
            STUDENTS_DF.at[idx, 'Risk_Description'] = risk_desc_now
        STUDENTS_DF.at[idx, 'Risk_Score'] = round(prob_now * 100, 2)

        write_students_json(STUDENTS_DF, os.path.join(os.path.dirname(__file__), JSON_OUTPUT_FILENAME))
        write_students_csv(STUDENTS_DF, os.path.join(os.path.dirname(__file__), CSV_FILENAME))
        refresh_ml_stack()

        return jsonify({'status': 'ok'})
    except Exception as e:
        app.logger.error(f"Edit student error: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/delete_student', methods=['POST'])
def delete_student():
    """Delete a student by index or by name (first match)."""
    try:
        global STUDENTS_DF, DASHBOARD_DATA
        data = request.json or {}
        idx = data.get('index')
        name = (data.get('name') or '').strip()

        deleted_label = None
        if idx is not None and str(idx) != '':
            try:
                i = int(idx)
            except Exception:
                return jsonify({'error': 'Invalid index'}), 400
            if i < 0 or i >= len(STUDENTS_DF):
                return jsonify({'error': 'Index out of range'}), 400
            deleted_label = str(STUDENTS_DF.iloc[i].get('Name', f'Index {i}'))
            STUDENTS_DF = STUDENTS_DF.drop(STUDENTS_DF.index[i]).reset_index(drop=True)
        elif name:
            mask = STUDENTS_DF['Name'].astype(str).str.strip().str.lower() == name.lower()
            matches = STUDENTS_DF[mask]
            if matches.empty:
                return jsonify({'error': 'No student found with that name'}), 404
            first_idx = matches.index[0]
            deleted_label = str(STUDENTS_DF.loc[first_idx].get('Name', ''))
            STUDENTS_DF = STUDENTS_DF.drop(first_idx).reset_index(drop=True)
        else:
            return jsonify({'error': 'Provide index or name'}), 400

        # Recompute dashboard and persist JSON/CSV
        write_students_json(STUDENTS_DF, os.path.join(os.path.dirname(__file__), JSON_OUTPUT_FILENAME))
        write_students_csv(STUDENTS_DF, os.path.join(os.path.dirname(__file__), CSV_FILENAME))
        # Reload DataFrame from JSON for consistency
        with open(os.path.join(os.path.dirname(__file__), JSON_OUTPUT_FILENAME), 'r', encoding='utf-8') as f:
            STUDENTS_DF = pd.DataFrame(json.load(f))
        refresh_ml_stack()
        return jsonify({'status': 'ok', 'deleted': deleted_label})
    except Exception as e:
        app.logger.error(f"Delete student error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/ai_support')
def ai_support():
    """Serves the AI Support chat page for students, parents, and teachers."""
    return render_template('ai_support.html')


@app.route('/ai_support_chat', methods=['POST'])
def ai_support_chat():
    """Handles AI support chat messages via Ollama student-advisor LLM.
    On Netlify (IS_NETLIFY=True) returns a graceful 503 since Ollama is not
    available in the serverless environment.
    """
    # --- Netlify / serverless: Ollama is not available ---
    if IS_NETLIFY:
        return jsonify({
            'error': (
                'The AI chat feature requires a local Ollama instance and is not available '
                'in the hosted (Netlify) deployment. Run the app locally to use AI chat.'
            )
        }), 503

    try:
        data = request.json or {}
        user_message = (data.get('message') or '').strip()
        role = (data.get('role') or 'student').strip().lower()
        student_name = (data.get('student_name') or '').strip()
        history = data.get('history', [])

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # --- Build student context ---
        json_path = os.path.join(os.path.dirname(__file__), JSON_OUTPUT_FILENAME)
        student_context = ""
        if student_name:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                df_ctx = pd.DataFrame(records)
            else:
                df_ctx = STUDENTS_DF.copy()
            mask = df_ctx['Name'].astype(str).str.strip().str.lower() == student_name.lower()
            if mask.any():
                sel = df_ctx[mask].iloc[0].to_dict()
                student_context = (
                    f"Student Profile:\n"
                    f"  Name: {sel.get('Name', 'Unknown')}\n"
                    f"  Age: {sel.get('Age', 'N/A')}\n"
                    f"  Gender: {sel.get('Gender', 'N/A')}\n"
                    f"  Absences: {sel.get('Number_of_Absences', sel.get('Absences', 'N/A'))}\n"
                    f"  Aggregate Grade: {sel.get('Aggregate_Grade', sel.get('Final_Grade', sel.get('Grade_2', sel.get('Grade_1', 'N/A'))))}\n"
                    f"  Internet Access: {sel.get('Internet_Access', 'N/A')}\n"
                    f"  Risk Category: {sel.get('Risk_Category', 'N/A')}\n"
                    f"  Risk Score: {sel.get('Risk_Score', 'N/A')}\n"
                )
            else:
                student_context = f"Note: Student '{student_name}' was not found in the system.\n"
        else:
            try:
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        records = json.load(f)
                    df_all = pd.DataFrame(records)
                else:
                    df_all = STUDENTS_DF.copy()
                cats = df_all['Risk_Category'].astype(str).str.strip().str.lower() if 'Risk_Category' in df_all.columns else pd.Series([])
                red    = int((cats == 'red').sum())
                yellow = int((cats == 'yellow').sum())
                green  = int((cats == 'green').sum())
                total  = int(len(df_all))
                student_context = (
                    f"Cohort Overview — {total} students total:\n"
                    f"  High Risk (Red): {red} | Medium Risk (Yellow): {yellow} | Low Risk (Green): {green}\n"
                )
            except Exception as exc:
                app.logger.warning(f"Could not build cohort context: {exc}")
                student_context = "Cohort data available in system.\n"

        role_desc = {
            'student': "You are speaking with a student. Be empathetic and motivating.",
            'parent':  "You are speaking with a parent. Give clear, actionable guidance.",
            'teacher': "You are speaking with a teacher. Give data-driven insights."
        }.get(role, "You are speaking with an educator. Provide helpful guidance.")

        system_prompt = (
            f"You are 'Student Advisor', an expert AI specialising in dropout prevention.\n"
            f"{role_desc}\n\nCurrent Data Context:\n{student_context}\n"
            f"Be empathetic, specific, and solution-focused."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for turn in history[-10:]:
            if turn.get('role') in ('user', 'assistant') and turn.get('content'):
                messages.append({"role": turn['role'], "content": turn['content']})
        messages.append({"role": "user", "content": user_message})

        ollama_payload = {"model": "student-advisor", "messages": messages, "stream": False}
        try:
            resp = http_requests.post(
                "http://localhost:11434/api/chat",
                json=ollama_payload,
                timeout=120
            )
            resp.raise_for_status()
            assistant_reply = resp.json().get('message', {}).get('content', '').strip()
            if not assistant_reply:
                assistant_reply = "I couldn't generate a response. Please try again."
        except http_requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to Ollama. Please ensure the student-advisor model is running on localhost:11434.'}), 503
        except http_requests.exceptions.Timeout:
            return jsonify({'error': 'The AI model took too long to respond. Please try a shorter question.'}), 504
        except Exception as e:
            app.logger.error(f"Ollama error: {e}")
            return jsonify({'error': f'AI model error: {str(e)}'}), 500

        return jsonify({'reply': assistant_reply, 'role': role})

    except Exception as e:
        app.logger.error(f"ai_support_chat error: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/students_list')
def api_students_list():
    """Return a compact list of student names for the AI support dropdown."""
    try:
        names = STUDENTS_DF['Name'].dropna().astype(str).tolist() if 'Name' in STUDENTS_DF.columns else []
        return jsonify({'students': names})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Log the successful training and start the server
    print("----------------------------------------------------------------------")
    print("FLASK APP READY: Running Dropout Predictor.")
    print("Access the homepage at: http://127.0.0.1:5000/")
    print("Dashboard at: http://127.0.0.1:5000/dashboard")
    print("AI Support at: http://127.0.0.1:5000/ai_support")
    print("----------------------------------------------------------------------")
    app.run(debug=True)
