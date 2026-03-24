"""Smoke tests for Flask routes."""
import json
import os
import sys

import pytest

# Project root on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def test_home_ok(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Dropout" in r.data


def test_risk_summary_json(client):
    r = client.get("/risk_summary")
    assert r.status_code == 200
    data = r.get_json()
    assert "total" in data
    assert "red" in data


def test_predict_ok(client):
    r = client.post(
        "/predict",
        data=json.dumps(
            {
                "age": 20,
                "gpa": 3.0,
                "absences": 5,
                "financial_aid": 1,
                "study_hours": 20,
                "gender": "F",
            }
        ),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("ok") is True
    assert "probability" in data
    assert "explanation" in data


def test_model_metrics(client):
    r = client.get("/api/model_metrics")
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("ok") is True
    assert "meta" in data


def test_export_csv(client):
    r = client.get("/export/students.csv")
    assert r.status_code == 200
    assert r.headers.get("Content-Type", "").startswith("text/csv")
