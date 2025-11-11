# --- HOME PAGE HTML ---
HOME_HTML = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Dropic.ai Dropout Predictions</title>
    <script src=\"https://cdn.tailwindcss.com\"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .card { background-color: white; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1); transition: transform .15s ease, box-shadow .15s ease; }
        .card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px -4px rgba(0,0,0,0.12), 0 6px 10px -6px rgba(0,0,0,0.1); }
        input, select { transition: box-shadow .2s ease, border-color .2s ease; }
        input:focus, select:focus { outline: none; box-shadow: 0 0 0 3px rgba(59,130,246,.25); border-color: #3b82f6; }
    </style>
    <script src=\"https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js\"></script>
</head>
<body class=\"min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 md:p-8\">
    <div class=\"max-w-7xl mx-auto\">
    <!-- Top Bar with Expanding Menu -->
    <div class=\"flex items-center justify-between mb-6\">
        <div class=\"flex items-center gap-3\">
            <button id=\"menuToggle\" aria-label=\"Open menu\" class=\"p-2 rounded-md border border-gray-300 hover:bg-gray-100\">
                <svg xmlns=\"http://www.w3.org/2000/svg\" fill=\"none\" viewBox=\"0 0 24 24\" stroke-width=\"1.5\" stroke=\"currentColor\" class=\"w-6 h-6\">
                    <path stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5\" />
                </svg>
            </button>
            <h1 class=\"text-2xl md:text-4xl font-extrabold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent\">Dropic.ai- Dropout Predictions</h1>
        </div>
        <div class=\"hidden md:block\"><a href=\"/dashboard\" class=\"text-blue-600 hover:underline\">Go to Dashboard</a></div>
    </div>

    <!-- Expanding Menu Panel -->
    <div id=\"menuPanel\" class=\"hidden mb-6 p-4 card\">
        <div class=\"grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3\">
            <button id=\"btnListStudents\" class=\"py-2 px-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 active:scale-95 transition text-sm\">Full list of students</button>
            <button id=\"btnAddStudent\" class=\"py-2 px-3 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 active:scale-95 transition text-sm\">Add student</button>
            <button id=\"btnDeleteStudent\" class=\"py-2 px-3 rounded-lg bg-rose-600 text-white hover:bg-rose-700 active:scale-95 transition text-sm\">Delete student</button>
            <button id=\"btnPrintReport\" class=\"py-2 px-3 rounded-lg bg-gray-700 text-white hover:bg-gray-800 active:scale-95 transition text-sm\">Print report</button>
        </div>
        <!-- Inline delete controls (toggle visible on click) -->
        <div id=\"deleteControls\" class=\"hidden mt-4 border rounded-lg p-3\">
            <div class=\"text-sm text-gray-700 mb-2\">Delete by index (0-based) or by name (first match):</div>
            <div class=\"flex flex-col sm:flex-row gap-2\">
                <input id=\"delIndex\" type=\"number\" placeholder=\"Index e.g. 0\" class=\"p-2 border rounded-md w-full sm:w-48\" />
                <input id=\"delName\" type=\"text\" placeholder=\"Name (optional)\" class=\"p-2 border rounded-md w-full\" />
                <button id=\"confirmDelete\" class=\"py-2 px-3 rounded-lg bg-rose-600 text-white hover:bg-rose-700\">Delete</button>
            </div>
            <div id=\"deleteResult\" class=\"mt-2 text-sm\"></div>
        </div>
    </div>

    <!-- Risk Summary Graph -->
    <div class=\"p-6 card mb-8\">
        <h2 class=\"text-2xl font-bold text-blue-700 mb-2\">Overall Risk Summary</h2>
        <p class=\"text-gray-600 mb-4\">Total students: <span id=\"totalStudents\" class=\"font-semibold\">0</span></p>
        <div class=\"grid grid-cols-1 md:grid-cols-3 gap-4 mb-4\">
            <div class=\"p-4 rounded-lg bg-red-50 border border-red-200 hover:shadow-md transition\">
                <div class=\"text-sm text-red-700 font-semibold\">Red (High Risk)</div>
                <div id=\"countRed\" class=\"text-2xl font-extrabold text-red-700\">0</div>
            </div>
            <div class=\"p-4 rounded-lg bg-yellow-50 border border-yellow-200 hover:shadow-md transition\">
                <div class=\"text-sm text-yellow-700 font-semibold\">Yellow (Medium Risk)</div>
                <div id=\"countYellow\" class=\"text-2xl font-extrabold text-yellow-700\">0</div>
            </div>
            <div class=\"p-4 rounded-lg bg-green-50 border border-green-200 hover:shadow-md transition\">
                <div class=\"text-sm text-green-700 font-semibold\">Green (Low Risk)</div>
                <div id=\"countGreen\" class=\"text-2xl font-extrabold text-green-700\">0</div>
            </div>
        </div>
        <canvas id=\"riskChart\" height=\"100\"></canvas>
    </div>

    <div class=\"grid grid-cols-1 lg:grid-cols-2 gap-8\">
        <!-- Add Student -->
        <div class=\"p-6 card\">
            <h2 class=\"text-2xl font-bold text-blue-700 mb-4 border-b pb-2\">Add Student</h2>
            <form id=\"addStudentForm\" class=\"space-y-4\">
                <div>
                    <label class=\"block text-sm font-medium text-gray-700\">Name</label>
                    <input type=\"text\" name=\"name\" required class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\" placeholder=\"Ritika Singh\" />
                </div>
                <div class=\"grid grid-cols-2 gap-4\">
                    <div>
                        <label class=\"block text-sm font-medium text-gray-700\">Gender</label>
                        <select name=\"gender\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\"><option value=\"F\">Female</option><option value=\"M\">Male</option></select>
                    </div>
                    <div>
                        <label class=\"block text-sm font-medium text-gray-700\">Age</label>
                        <input type=\"number\" name=\"age\" min=\"10\" max=\"60\" value=\"18\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\" />
                    </div>
                </div>
                <div>
                    <label class=\"block text-sm font-medium text-gray-700\">Absences</label>
                    <input type=\"number\" name=\"absences\" min=\"0\" max=\"365\" value=\"0\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\" />
                </div>
                <div class=\"grid grid-cols-3 gap-4\">
                    <div>
                        <label class=\"block text-sm font-medium text-gray-700\">Aggregate Grade (0-20)</label>
                        <input type=\"number\" step=\"0.1\" name=\"aggregate_grade\" min=\"0\" max=\"20\" value=\"12\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\" />
                    </div>
                    <div>
                        <label class=\"block text-sm font-medium text-gray-700\">Internet Access</label>
                        <select name=\"internet_access\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\"><option value=\"yes\">Yes</option><option value=\"no\">No</option></select>
                    </div>
                    <div>
                        <label class=\"block text-sm font-medium text-gray-700\">Desired Risk Zone (optional)</label>
                        <select name=\"desired_risk_zone\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\">
                            <option value=\"\">-- None --</option>
                            <option value=\"Red\">Red</option>
                            <option value=\"Yellow\">Yellow</option>
                            <option value=\"Green\">Green</option>
                        </select>
                    </div>
                </div>
                <button type=\"submit\" class=\"w-full py-2 px-4 rounded-lg text-white bg-blue-600 hover:bg-blue-700\">Add Student</button>
            </form>
            <div id=\"addStudentResult\" class=\"mt-4 text-sm text-gray-700\"></div>
        </div>

        <!-- Quick Predictor -->
        <div class=\"p-6 card\">
            <h2 class=\"text-2xl font-bold text-blue-700 mb-4 border-b pb-2\">Quick Predictor</h2>
            <form id=\"quickPredictForm\" class=\"space-y-4\">
                <div class=\"grid grid-cols-2 gap-4\">
                    <div>
                        <label class=\"block text-sm font-medium text-gray-700\">Age</label>
                        <input type=\"number\" name=\"age\" value=\"18\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\" />
                    </div>
                    <div>
                        <label class=\"block text-sm font-medium text-gray-700\">Gender</label>
                        <select name=\"gender\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\"><option value=\"F\">Female</option><option value=\"M\">Male</option></select>
                    </div>
                </div>
                <div class=\"grid grid-cols-3 gap-4\">
                    <div>
                        <label class=\"block text-sm font-medium text-gray-700\">GPA</label>
                        <input type=\"number\" step=\"0.01\" min=\"0\" max=\"4\" name=\"gpa\" value=\"3.0\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\" />
                    </div>
                    <div>
                        <label class=\"block text-sm font-medium text-gray-700\">Absences</label>
                        <input type=\"number\" min=\"0\" name=\"absences\" value=\"5\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\" />
                    </div>
                    <div>
                        <label class=\"block text-sm font-medium text-gray-700\">Study Hours</label>
                        <input type=\"number\" min=\"0\" name=\"study_hours\" value=\"20\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\" />
                    </div>
                </div>
                <div>
                    <label class=\"block text-sm font-medium text-gray-700\">Financial Aid</label>
                    <select name=\"financial_aid\" class=\"mt-1 block w-full rounded-lg border-gray-300 p-2 border\"><option value=\"1\">Yes</option><option value=\"0\">No</option></select>
                </div>
                <button type=\"submit\" class=\"w-full py-2 px-4 rounded-lg text-white bg-emerald-600 hover:bg-emerald-700\">Predict</button>
            </form>
            <div id=\"quickPredictResult\" class=\"mt-4 p-4 border rounded-lg hidden\"></div>
        </div>
    </div>

    <!-- Mentor Advice Chatbot -->
    <div id="mentorPanel" class="mt-8 p-6 card hidden">
        <h2 class="text-2xl font-bold text-blue-700 mb-4 border-b pb-2">Mentor AI Assistant</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="md:col-span-1">
                <label class="block text-sm font-medium text-gray-700">Choose Student</label>
                <select id="mentorStudent" class="mt-1 block w-full rounded-lg border-gray-300 p-2 border"></select>
                <div class="text-xs text-gray-500 mt-1">Or enter a name below</div>
                <input id="mentorName" type="text" placeholder="Type full name (optional)" class="mt-1 block w-full rounded-lg border-gray-300 p-2 border" />
                <button id="askAdvice" class="mt-3 w-full py-2 px-4 rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition">Get Mentor Advice</button>
            </div>
            <div class="md:col-span-2">
                <div id="adviceBox" class="p-4 border rounded-lg bg-gray-50 text-sm min-h-24">Select a student and click Get Mentor Advice.</div>
            </div>
        </div>
    </div>

    <!-- Floating action button to open Mentor AI -->
    <button id="openMentor" aria-expanded="false" aria-controls="mentorPanel" title="Open Mentor AI"
            class="fixed bottom-6 right-6 px-4 py-3 rounded-full shadow-lg text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition focus:outline-none">
        Mentor AI
    </button>

    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('addStudentForm').addEventListener('submit', handleAddStudent);
            document.getElementById('quickPredictForm').addEventListener('submit', handleQuickPredict);
            initMenu();
            fetchRiskSummary();
            // Toggle Mentor panel
            const openBtn = document.getElementById('openMentor');
            const mentorPanel = document.getElementById('mentorPanel');
            openBtn.addEventListener('click', () => {
                mentorPanel.classList.toggle('hidden');
                const expanded = !mentorPanel.classList.contains('hidden');
                openBtn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
                if (expanded) {
                    initMentorDropdown();
                }
            });
        });

        function initMenu() {
            const toggle = document.getElementById('menuToggle');
            const panel = document.getElementById('menuPanel');
            const btnList = document.getElementById('btnListStudents');
            const btnAdd = document.getElementById('btnAddStudent');
            const btnDel = document.getElementById('btnDeleteStudent');
            const btnPrint = document.getElementById('btnPrintReport');
            const delCtrls = document.getElementById('deleteControls');
            const confirmDel = document.getElementById('confirmDelete');
            const delResult = document.getElementById('deleteResult');

            toggle.addEventListener('click', () => panel.classList.toggle('hidden'));
            btnList.addEventListener('click', () => { window.location.href = '/students_view'; });
            btnAdd.addEventListener('click', () => { document.getElementById('addStudentForm').scrollIntoView({behavior: 'smooth'}); });
            btnDel.addEventListener('click', () => { delCtrls.classList.toggle('hidden'); });
            btnPrint.addEventListener('click', () => {
                const full = confirm('Click OK for full report, or Cancel to print a single student.');
                if (full) {
                    window.open('/print_report', '_blank');
                    return;
                }
                const idx = prompt('Enter student index (0-based), or leave blank to search by name:');
                if (idx && idx.trim() !== '') {
                    window.open('/print_report?index=' + encodeURIComponent(idx.trim()), '_blank');
                    return;
                }
                const name = prompt('Enter full name to print report for:');
                if (name && name.trim() !== '') {
                    window.open('/print_report?name=' + encodeURIComponent(name.trim()), '_blank');
                } else {
                    alert('No student specified.');
                }
            });

            confirmDel.addEventListener('click', async () => {
                delResult.textContent = 'Deleting...';
                try {
                    const payload = { index: document.getElementById('delIndex').value, name: document.getElementById('delName').value };
                    const res = await fetch('/delete_student', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || 'Delete failed');
                    delResult.className = 'mt-2 text-sm text-green-700';
                    delResult.textContent = `Deleted: ${data.deleted}`;
                    fetchRiskSummary();
                } catch (e) {
                    delResult.className = 'mt-2 text-sm text-red-700';
                    delResult.textContent = 'Error: ' + e.message;
                }
            });
        }

        async function fetchRiskSummary() {
            try {
                const res = await fetch('/risk_summary');
                if (!res.ok) throw new Error('Failed to load risk summary');
                const s = await res.json();
                document.getElementById('totalStudents').textContent = s.total;
                document.getElementById('countRed').textContent = s.red;
                document.getElementById('countYellow').textContent = s.yellow;
                document.getElementById('countGreen').textContent = s.green;
                renderRiskChart(s);
            } catch (e) {
                console.error('risk summary error', e);
            }
        }

        let riskChartInstance = null;
        function renderRiskChart(s) {
            if (riskChartInstance) riskChartInstance.destroy();
            const ctx = document.getElementById('riskChart').getContext('2d');
            riskChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Red', 'Yellow', 'Green'],
                    datasets: [{
                        label: 'Students',
                        data: [s.red, s.yellow, s.green],
                        backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
                        borderColor: ['#dc2626', '#d97706', '#059669'],
                        borderWidth: 1,
                        borderRadius: 8,
                    }]
                },
                options: {
                    responsive: true,
                    scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
                    plugins: { legend: { display: false } }
                }
            });
        }

        async function handleAddStudent(e) {
            e.preventDefault();
            const form = e.target;
            const payload = Object.fromEntries(new FormData(form).entries());
            // Basic validation: enforce desired risk zone if provided
            if (payload.desired_risk_zone && !['Red','Yellow','Green'].includes(payload.desired_risk_zone)) {
                alert('Invalid desired risk zone.');
                return;
            }
            const resBox = document.getElementById('addStudentResult');
            resBox.textContent = 'Adding student...';
            try {
                const res = await fetch('/add_student', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || 'Unknown error');
                resBox.textContent = `Added ${payload.name}. Risk: ${data.risk_category} (${data.probability}%)`;
                alert(`Student "${payload.name}" added successfully in category: ${data.risk_category}.`);
                // Refresh risk summary and students dropdown
                fetchRiskSummary();
                if (typeof initStudentsDropdown === 'function') {
                    initStudentsDropdown();
                }
                // Navigate to list and highlight new student; list sorted by Red, Yellow, Green
                if (payload.name) {
                    const q = new URLSearchParams({ search: payload.name, highlight: payload.name }).toString();
                    window.location.href = '/students_view?' + q;
                }
            } catch (err) {
                resBox.textContent = 'Failed to add: ' + err.message;
            }
        }

        async function handleQuickPredict(e) {
            e.preventDefault();
            const form = e.target;
            const payload = {
                age: form.age.value,
                gpa: form.gpa.value,
                absences: form.absences.value,
                study_hours: form.study_hours.value,
                gender: form.gender.value,
                financial_aid: form.financial_aid.value,
            };
            const box = document.getElementById('quickPredictResult');
            box.className = 'mt-4 p-4 border rounded-lg';
            box.textContent = 'Predicting...';
            try {
                const res = await fetch('/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || 'Unknown error');
                box.classList.remove('hidden');
                box.textContent = `${data.prediction_text} (${data.probability}%)`;
            } catch (err) {
                box.textContent = 'Prediction failed: ' + err.message;
            }
        }

        async function initMentorDropdown() {
            try {
                const res = await fetch('/students');
                if (!res.ok) throw new Error('Failed to load students');
                const students = await res.json();
                const mentorSel = document.getElementById('mentorStudent');
                if (!mentorSel) return;
                if (mentorSel.options.length > 0) return; // already populated
                mentorSel.innerHTML = '';
                students.forEach((s, idx) => {
                    const option = document.createElement('option');
                    const globalIdx = (s._idx !== undefined && s._idx !== null) ? s._idx : idx;
                    option.value = globalIdx;
                    option.textContent = `${s.Name || ('Student ' + (idx+1))}`;
                    mentorSel.appendChild(option);
                });

                const adviceBtn = document.getElementById('askAdvice');
                const adviceBox = document.getElementById('adviceBox');
                adviceBtn.onclick = async () => {
                    adviceBox.textContent = 'Thinking...';
                    try {
                        const nameInput = (document.getElementById('mentorName').value || '').trim();
                        const idxSel = mentorSel.value;
                        const payload = nameInput ? { name: nameInput } : { index: Number(idxSel) };
                        const r = await fetch('/mentor_advice', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                        const d = await r.json();
                        if (!r.ok) throw new Error(d.error || 'Failed to get advice');
                        const items = (d.advice || []).map(t => `<li class=\"list-disc ml-5\">${t}</li>`).join('');
                        adviceBox.innerHTML = `
                            <div class=\"mb-2\"><b>Student:</b> ${d.student}</div>
                            <div class=\"mb-2\"><b>Risk:</b> ${d.risk_category} • <b>Absences:</b> ${d.absences} • <b>Aggregate:</b> ${d.aggregate_grade}</div>
                            <div class=\"mb-1\"><b>Recommended Steps:</b></div>
                            <ul>${items}</ul>
                        `;
                    } catch (e) {
                        adviceBox.textContent = 'Error: ' + e.message;
                    }
                };
            } catch (e) {
                console.error('initMentorDropdown error', e);
            }
        }
    </script>
</body>
</html>
"""
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template_string, make_response
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import json
from typing import Optional
import os
from collections import OrderedDict
import math

app = Flask(__name__)

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

# Prepare dashboard data from CSV columns
# Map Gender to a concise form if needed
DASHBOARD_DATA = STUDENTS_DF.copy()

# Compute a binary dropout flag from Dropped_Out (Yes/No) if available
if 'Dropped_Out' in DASHBOARD_DATA.columns:
    DASHBOARD_DATA['DropoutFlag'] = (DASHBOARD_DATA['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes').astype(int)
else:
    # Fallback: derive from Risk_Category (treat Red as high-risk ~ dropout)
    DASHBOARD_DATA['DropoutFlag'] = (DASHBOARD_DATA['Risk_Category'].astype(str).str.strip().str.lower() == 'red').astype(int)

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
    out['Dropout'] = DASHBOARD_DATA['DropoutFlag']
    return out

TRAINING_DF = build_training_frame(DASHBOARD_DATA)
FEATURES = ['Age', 'GPA', 'Absences', 'Financial_Aid', 'Study_Hours', 'Gender_M']
TARGET = 'Dropout'

X = TRAINING_DF[FEATURES]
y = TRAINING_DF[TARGET]

model = LogisticRegression(solver='liblinear', random_state=42)
model.fit(X, y)

MODEL_FEATURES = FEATURES
print(f"Loaded {len(STUDENTS_DF)} students from CSV and wrote {JSON_OUTPUT_FILENAME}.")

# --- 2. FLASK ROUTES ---

@app.route('/')
def home():
    """Serves the homepage with Add Student and Quick Predictor."""
    return HOME_HTML

@app.route('/dashboard')
def index():
    """Serves the interactive dashboard page."""
    return DASHBOARD_HTML

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
        DASHBOARD_DATA = STUDENTS_DF.copy()
        if 'Dropped_Out' in DASHBOARD_DATA.columns:
            DASHBOARD_DATA['DropoutFlag'] = (DASHBOARD_DATA['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes').astype(int)
        else:
            DASHBOARD_DATA['DropoutFlag'] = (DASHBOARD_DATA['Risk_Category'].astype(str).str.strip().str.lower() == 'red').astype(int)
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
def predict():
    """API endpoint for receiving student data and returning a prediction."""
    try:
        data = request.json or {}

        # 1. Feature Preprocessing (must match training data prep)
        # Convert gender to numerical (Gender_M)
        gender_m = 1 if data.get('gender') == 'M' else 0

        # Create input array matching the MODEL_FEATURES order
        input_data = np.array([[
            float(data.get('age', 20)),
            float(data.get('gpa', 3.0)),
            float(data.get('absences', 5)),
            float(data.get('financial_aid', 0)),
            float(data.get('study_hours', 20)),
            gender_m
        ]])

        # 2. Prediction
        probability = model.predict_proba(input_data)[0][1]

        result = {
            'probability': round(probability * 100, 2),
            'prediction_text': "HIGH RISK" if probability > 0.5 else "LOW RISK"
        }

        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e), 'message': 'Invalid input data or server error.'}), 400


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



# --- 3. SINGLE-FILE HTML TEMPLATE ---
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI College Dropout Predictor</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Load Inter font -->
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f4f6f9;
        }
        .card {
            background-color: white;
            border-radius: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
        }
    </style>
    <!-- Load Chart.js for interactive charts -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
</head>
<body class="p-4 md:p-8">

    <header class="text-center mb-8">
        <h1 class="text-4xl font-extrabold text-blue-800">Student Success AI Dashboard</h1>
        <p class="text-gray-600 mt-2">Predicting college dropout risk using machine learning.</p>
        <div class="mt-3">
            <a href="/" class="text-blue-600 hover:underline">Back to Home</a>
        </div>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- SIDEBAR: PREDICTION TOOL -->
        <div class="lg:col-span-1 p-6 card h-fit sticky top-8">
            <h2 class="text-2xl font-bold text-blue-700 mb-4 border-b pb-2">Individual Risk Predictor</h2>
            <form id="predictionForm" class="space-y-4">
                
                <!-- Age -->
                <div>
                    <label for="age" class="block text-sm font-medium text-gray-700">Age</label>
                    <input type="number" id="age" name="age" required min="18" max="60" value="20"
                           class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">
                </div>
                
                <!-- GPA -->
                <div>
                    <label for="gpa" class="block text-sm font-medium text-gray-700">Current GPA (0.0 to 4.0)</label>
                    <input type="number" id="gpa" name="gpa" required step="0.01" min="0" max="4.0" value="3.0"
                           class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">
                </div>
                
                <!-- Absences -->
                <div>
                    <label for="absences" class="block text-sm font-medium text-gray-700">Total Absences</label>
                    <input type="number" id="absences" name="absences" required min="0" max="100" value="5"
                           class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">
                </div>

                <!-- Study Hours -->
                <div>
                    <label for="study_hours" class="block text-sm font-medium text-gray-700">Weekly Study Hours</label>
                    <input type="number" id="study_hours" name="study_hours" required min="0" max="100" value="20"
                           class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">
                </div>

                <!-- Gender -->
                <div>
                    <label for="gender" class="block text-sm font-medium text-gray-700">Gender</label>
                    <select id="gender" name="gender" 
                            class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">
                        <option value="F">Female</option>
                        <option value="M">Male</option>
                    </select>
                </div>
                
                <!-- Financial Aid -->
                <div>
                    <label for="financial_aid" class="block text-sm font-medium text-gray-700">Receives Financial Aid</label>
                    <select id="financial_aid" name="financial_aid" 
                            class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">
                        <option value="1">Yes</option>
                        <option value="0">No</option>
                    </select>
                </div>
                
                <button type="submit"
                        class="w-full py-2 px-4 border border-transparent rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition duration-150">
                    Predict Dropout Risk
                </button>
            </form>

            <!-- Prediction Result -->
            <div id="predictionResult" class="mt-6 p-4 border-2 border-gray-200 rounded-lg text-center hidden">
                <h3 class="text-lg font-semibold text-gray-800">Predicted Risk:</h3>
                <p id="riskText" class="text-3xl font-extrabold mt-1"></p>
                <p class="text-sm text-gray-500 mt-1">Probability: <span id="probabilityValue" class="font-bold text-gray-700"></span>%</p>
            </div>

            <!-- Student Selector -->
            <div class="mt-8">
                <h2 class="text-xl font-bold text-blue-700 mb-2">Browse First 100 Students</h2>
                <label for="studentSelect" class="block text-sm font-medium text-gray-700">Student</label>
                <select id="studentSelect" class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"></select>
                <div id="selectedStudent" class="mt-4 p-4 border rounded-lg hidden">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <button id="studentNameBtn" type="button" class="font-semibold text-blue-700 hover:underline text-left" aria-expanded="false">
                                <span id="studentName"></span>
                            </button>
                            <p class="text-sm text-gray-500" id="studentMeta"></p>
                        </div>
                        <span id="riskBadge" class="px-3 py-1 rounded-full text-white text-sm font-semibold"></span>
                    </div>
                    <div id="studentDetails" class="mt-4 hidden">
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                            <div><span class="text-gray-500">School:</span> <span id="dSchool" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Address:</span> <span id="dAddress" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Family Size:</span> <span id="dFamilySize" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Parental Status:</span> <span id="dParental" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Mother Education:</span> <span id="dMEdu" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Father Education:</span> <span id="dFEdu" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Travel Time:</span> <span id="dTravel" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Study Time:</span> <span id="dStudy" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Failures:</span> <span id="dFails" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Internet:</span> <span id="dInternet" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Health:</span> <span id="dHealth" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Absences:</span> <span id="dAbsences" class="font-medium"></span></div>
                            <div><span class="text-gray-500">Grades (G1/G2/Final):</span> <span id="dGrades" class="font-medium"></span></div>
                        </div>
                        <div class="mt-3 text-sm"><span class="text-gray-500">Risk Note:</span> <span id="dRiskDesc" class="font-medium"></span></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- MAIN CONTENT: INTERACTIVE DASHBOARD -->
        <div class="lg:col-span-2 space-y-8">

            <!-- Global Risk Summary -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Dropout Rate by Gender Chart -->
                <div class="p-6 card">
                    <h3 class="text-xl font-semibold text-blue-700 mb-4">Dropout Rate by Gender</h3>
                    <canvas id="genderChart"></canvas>
                </div>
                
                <!-- Dropout Rate by Absences Chart -->
                <div class="p-6 card">
                    <h3 class="text-xl font-semibold text-blue-700 mb-4">Dropout Risk by Absence Level</h3>
                    <canvas id="absencesChart"></canvas>
                </div>
            </div>

            <!-- Global Data Visualization -->
            <div class="p-6 card">
                <h3 class="text-xl font-semibold text-blue-700 mb-4">Risk Factor Distribution (Placeholder)</h3>
                <!-- In a real app, this would show interactive scatter plots, etc. -->
                <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
                    <p class="text-gray-500">
                        This section is reserved for interactive data visualizations (like GPA vs. Absences scatter plots) 
                        fetched from your live MySQL database to explore global risk trends.
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // --- JAVASCRIPT FOR INTERACTION ---

        document.addEventListener('DOMContentLoaded', () => {
            fetchDashboardData();
            initStudentsDropdown();
            document.getElementById('predictionForm').addEventListener('submit', handlePrediction);
        });

        async function handlePrediction(event) {
            event.preventDefault();
            const form = event.target;
            const resultDiv = document.getElementById('predictionResult');
            const riskText = document.getElementById('riskText');
            const probabilityValue = document.getElementById('probabilityValue');

            const data = {
                age: form.age.value,
                gpa: form.gpa.value,
                absences: form.absences.value,
                study_hours: form.study_hours.value,
                gender: form.gender.value,
                financial_aid: form.financial_aid.value,
            };

            riskText.textContent = 'Calculating...';
            resultDiv.classList.remove('hidden');
            resultDiv.className = 'mt-6 p-4 border-2 rounded-lg text-center'; // Reset classes

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error('Server returned an error for prediction.');
                }

                const result = await response.json();
                
                riskText.textContent = result.prediction_text;
                probabilityValue.textContent = result.probability;
                
                // Styling based on risk level
                if (result.probability > 50) {
                    resultDiv.classList.add('border-red-500', 'bg-red-50');
                    riskText.classList.add('text-red-600');
                    riskText.classList.remove('text-green-600');
                } else {
                    resultDiv.classList.add('border-green-500', 'bg-green-50');
                    riskText.classList.add('text-green-600');
                    riskText.classList.remove('text-red-600');
                }

            } catch (error) {
                console.error('Prediction failed:', error);
                riskText.textContent = 'Error';
                probabilityValue.textContent = 'N/A';
                resultDiv.classList.add('border-yellow-500', 'bg-yellow-50');
            }
        }

        let genderChartInstance = null;
        let absencesChartInstance = null;

        async function fetchDashboardData() {
            try {
                const response = await fetch('/dashboard_data');
                if (!response.ok) throw new Error('Failed to fetch dashboard data');
                const data = await response.json();
                
                renderGenderChart(data.gender_data);
                renderAbsencesChart(data.absences_data);

            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            }
        }

        async function initStudentsDropdown() {
            try {
                const res = await fetch('/students');
                if (!res.ok) throw new Error('Failed to load students');
                const students = await res.json();
                const select = document.getElementById('studentSelect');
                select.innerHTML = '';
                students.forEach((s, idx) => {
                    const option = document.createElement('option');
                    option.value = idx;
                    option.textContent = `${s.Name || ('Student ' + (idx+1))}`;
                    select.appendChild(option);
                });
                select.addEventListener('change', () => renderSelectedStudent(students[select.value]));
                if (students.length > 0) {
                    select.value = 0;
                    renderSelectedStudent(students[0]);
                }
            } catch (e) {
                console.error('initStudentsDropdown error', e);
            }
        }

        function renderSelectedStudent(s) {
            const container = document.getElementById('selectedStudent');
            const nameEl = document.getElementById('studentName');
            const nameBtn = document.getElementById('studentNameBtn');
            const metaEl = document.getElementById('studentMeta');
            const badge = document.getElementById('riskBadge');
            const details = document.getElementById('studentDetails');
            const setText = (id, val) => document.getElementById(id).textContent = (val ?? 'N/A');
            if (!s) { container.classList.add('hidden'); return; }
            nameEl.textContent = s.Name || 'Student';
            const gender = s.Gender === 'M' ? 'Male' : (s.Gender === 'F' ? 'Female' : String(s.Gender));
            const age = s.Age ?? 'N/A';
            const abs = s.Number_of_Absences ?? s.Absences ?? 'N/A';
            metaEl.textContent = `Gender: ${gender} • Age: ${age} • Absences: ${abs}`;
            const risk = String(s.Risk_Category || '').toLowerCase();
            badge.textContent = (s.Risk_Category || 'Unknown');
            badge.className = 'px-3 py-1 rounded-full text-white text-sm font-semibold';
            if (risk === 'red') {
                badge.classList.add('bg-red-600');
            } else if (risk === 'yellow') {
                badge.classList.add('bg-yellow-500');
            } else if (risk === 'green') {
                badge.classList.add('bg-green-600');
            } else {
                badge.classList.add('bg-gray-500');
            }
            container.classList.remove('hidden');

            // Populate details
            setText('dSchool', s.School);
            setText('dAddress', s.Address);
            setText('dFamilySize', s.Family_Size);
            setText('dParental', s.Parental_Status);
            setText('dMEdu', s.Mother_Education);
            setText('dFEdu', s.Father_Education);
            setText('dTravel', s.Travel_Time);
            setText('dStudy', s.Study_Time);
            setText('dFails', s.Number_of_Failures);
            setText('dInternet', s.Internet_Access);
            setText('dHealth', s.Health_Status);
            setText('dAbsences', s.Number_of_Absences ?? s.Absences);
            setText('dGrades', `${s.Aggregate_Grade ?? s.Final_Grade ?? s.Grade_2 ?? s.Grade_1 ?? 'N/A'}`);
            setText('dRiskDesc', s.Risk_Description || '');

            // Toggle details on name click
            const expanded = details.classList.contains('hidden') ? 'false' : 'true';
            nameBtn.setAttribute('aria-expanded', expanded);
            nameBtn.onclick = () => {
                details.classList.toggle('hidden');
                nameBtn.setAttribute('aria-expanded', details.classList.contains('hidden') ? 'false' : 'true');
            };
        }
        
        function renderGenderChart(data) {
            if (genderChartInstance) genderChartInstance.destroy();

            const ctx = document.getElementById('genderChart').getContext('2d');
            genderChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(d => d.Gender === 'M' ? 'Male' : 'Female'),
                    datasets: [{
                        label: 'Dropout Rate (%)',
                        data: data.map(d => d.Dropout_Rate),
                        backgroundColor: ['#3b82f6', '#ef4444'], // Blue and Red
                        borderColor: ['#2563eb', '#dc2626'],
                        borderWidth: 1,
                        borderRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: { display: true, text: 'Dropout Rate (%)' }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + context.parsed.y + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        function renderAbsencesChart(data) {
            if (absencesChartInstance) absencesChartInstance.destroy();

            const ctx = document.getElementById('absencesChart').getContext('2d');
            absencesChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(d => d.Absence_Level),
                    datasets: [{
                        label: 'Dropout Rate (%)',
                        data: data.map(d => d.Dropout_Rate),
                        borderColor: '#10b981', // Emerald Green
                        backgroundColor: 'rgba(16, 185, 129, 0.2)',
                        tension: 0.4,
                        fill: true,
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: { display: true, text: 'Dropout Rate (%)' }
                        },
                        x: {
                            title: { display: true, text: 'Absence Level' }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + context.parsed.y + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
    </script>
</body>
</html>
"""

# --- Students List View ---
STUDENTS_VIEW_HTML = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Students - Dropic.ai</title>
  <script src=\"https://cdn.tailwindcss.com\"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
    body { font-family: 'Inter', sans-serif; background: #f4f6f9; }
    .card { background: white; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,.1), 0 2px 4px -2px rgba(0,0,0,.1); }
  </style>
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js\"></script>
  </head>
  <body class=\"p-4 md:p-8\">
    <div class=\"flex items-center justify-between mb-6\">
      <h1 class=\"text-2xl md:text-3xl font-extrabold text-blue-800\">Full list of students</h1>
      <a class=\"text-blue-600 hover:underline\" href=\"/\">Back to Home</a>
    </div>
    <div class=\"p-4 card\">
      <div class=\"mb-3 flex items-center gap-2\">
        <input id=\"searchInput\" type=\"text\" class=\"border rounded p-2 w-full md:w-96\" placeholder=\"Search by name...\" />
        <button id=\"searchBtn\" class=\"px-3 py-2 bg-blue-600 text-white rounded\">Search</button>
        <button id=\"clearBtn\" class=\"px-3 py-2 bg-gray-100 border rounded\">Clear</button>
      </div>
      <div class=\"overflow-x-auto\">
        <table class=\"min-w-full text-sm\">
          <thead class=\"bg-gray-100 text-gray-700\">
            <tr>
              <th class=\"text-left px-3 py-2\">#</th>
              <th class=\"text-left px-3 py-2\">Name</th>
              <th class=\"text-left px-3 py-2\">Gender</th>
              <th class=\"text-left px-3 py-2\">Age</th>
              <th class=\"text-left px-3 py-2\">Absences</th>
              <th class=\"text-left px-3 py-2\">Aggregate Grade</th>
              <th class=\"text-left px-3 py-2\">Risk</th>
              <th class=\"text-left px-3 py-2\">Note</th>
              <th class=\"text-left px-3 py-2\"></th>
            </tr>
          </thead>
          <tbody id=\"rows\" class=\"divide-y\"></tbody>
        </table>
      </div>
    </div>

    <script>
      document.addEventListener('DOMContentLoaded', async () => {
        try {
          const res = await fetch('/students');
          const students = await res.json();
          const tbody = document.getElementById('rows');
          const params = new URLSearchParams(window.location.search);
          const initialSearch = params.get('search') || '';
          const highlight = (params.get('highlight') || '').toLowerCase();
          const searchInput = document.getElementById('searchInput');
          const searchBtn = document.getElementById('searchBtn');
          const clearBtn = document.getElementById('clearBtn');
          searchInput.value = initialSearch;

          function render(list) {
            tbody.innerHTML = '';
            list.forEach((s, i) => {
            const tr = document.createElement('tr');
            const risk = String(s.Risk_Category || '').toLowerCase();
            let badge = '<span class=\"px-2 py-0.5 rounded-full text-white text-xs bg-gray-500\">Unknown</span>';
            if (risk === 'red') badge = '<span class=\"px-2 py-0.5 rounded-full text-white text-xs bg-red-600\">Red</span>';
            else if (risk === 'yellow') badge = '<span class=\"px-2 py-0.5 rounded-full text-white text-xs bg-yellow-500\">Yellow</span>';
            else if (risk === 'green') badge = '<span class=\"px-2 py-0.5 rounded-full text-white text-xs bg-green-600\">Green</span>';
            tr.innerHTML = `
              <td class=\"px-3 py-2 text-gray-500\">${i}</td>
              <td class=\"px-3 py-2 font-medium\">${s.Name ?? 'Student'}</td>
              <td class=\"px-3 py-2\">${s.Gender ?? ''}</td>
              <td class=\"px-3 py-2\">${s.Age ?? ''}</td>
              <td class=\"px-3 py-2\">${s.Number_of_Absences ?? s.Absences ?? ''}</td>
              <td class=\"px-3 py-2\">${s.Aggregate_Grade ?? s.Final_Grade ?? s.Grade_2 ?? s.Grade_1 ?? 'N/A'}</td>
              <td class=\"px-3 py-2\">${badge}</td>
              <td class=\"px-3 py-2\">${s.Risk_Description ?? ''}</td>
              <td class=\"px-3 py-2\"><a class=\"text-blue-600 hover:underline\" href=\"/edit_student?gindex=${encodeURIComponent(String(s._idx))}\">Edit</a></td>
            `;
              if (highlight && String(s.Name || '').toLowerCase() === highlight) {
                tr.classList.add('bg-yellow-50');
              }
            tbody.appendChild(tr);
            });
          }

          function sortByRisk(list) {
            const rank = (rc) => {
              const v = String(rc || '').toLowerCase();
              if (v === 'red') return 0;
              if (v === 'yellow') return 1;
              if (v === 'green') return 2;
              return 3;
            };
            return [...list].sort((a,b) => rank(a.Risk_Category) - rank(b.Risk_Category));
          }

          function filterList() {
            const q = searchInput.value.trim().toLowerCase();
            if (!q) { render(sortByRisk(students)); return; }
            const filtered = students.filter(s => String(s.Name || '').toLowerCase().includes(q));
            render(sortByRisk(filtered));
          }

          render(sortByRisk(students));
          if (initialSearch) filterList();
          searchBtn.addEventListener('click', filterList);
          clearBtn.addEventListener('click', () => { searchInput.value = ''; render(students); });
        } catch (e) { console.error(e); }
      });
    </script>
  </body>
</html>
"""

@app.route('/students_view')
def students_view():
    return render_template_string(STUDENTS_VIEW_HTML)

# --- Printable Report ---
PRINT_REPORT_HTML = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Dropic.ai Report</title>
  <script src=\"https://cdn.tailwindcss.com\"></script>
  <style>
    @media print { .no-print { display: none; } }
  </style>
</head>
<body class=\"p-6\">
  <div class=\"flex items-center justify-between mb-4\">
    <h1 class=\"text-2xl font-bold\">Dropic.ai- Dropout Predictions Report</h1>
    <button class=\"no-print px-3 py-2 bg-gray-800 text-white rounded\" onclick=\"window.print()\">Print</button>
  </div>
  <div id=\"summary\" class=\"mb-4\"></div>
  <div class=\"overflow-x-auto\">
    <table class=\"min-w-full text-sm\">
      <thead class=\"bg-gray-100\">
        <tr>
          <th class=\"text-left px-3 py-2\">Name</th>
          <th class=\"text-left px-3 py-2\">Gender</th>
          <th class=\"text-left px-3 py-2\">Age</th>
          <th class=\"text-left px-3 py-2\">Absences</th>
          <th class=\"text-left px-3 py-2\">Aggregate Grade</th>
          <th class=\"text-left px-3 py-2\">Risk</th>
        </tr>
      </thead>
      <tbody id=\"rows\" class=\"divide-y\"></tbody>
    </table>
  </div>
  <script>
    document.addEventListener('DOMContentLoaded', async () => {
      const params = new URLSearchParams(window.location.search);
      const idx = params.get('index');
      const name = params.get('name');

      const studentsRes = await fetch('/students');
      const students = await studentsRes.json();

      let selected = null;
      if (idx !== null && idx !== '') {
        const i = parseInt(idx, 10);
        if (!Number.isNaN(i) && i >= 0 && i < students.length) {
          selected = students[i];
        }
      } else if (name) {
        selected = students.find(s => String(s.Name || '').toLowerCase() === String(name).toLowerCase());
      }

      const tbody = document.getElementById('rows');
      tbody.innerHTML = '';
      const renderRow = (s) => {
        const tr = document.createElement('tr');
        const risk = String(s.Risk_Category || '').toLowerCase();
        let label = 'Unknown';
        if (risk === 'red') label = 'Red';
        else if (risk === 'yellow') label = 'Yellow';
        else if (risk === 'green') label = 'Green';
        tr.innerHTML = `
          <td class=\"px-3 py-2\">${s.Name ?? ''}</td>
          <td class=\"px-3 py-2\">${s.Gender ?? ''}</td>
          <td class=\"px-3 py-2\">${s.Age ?? ''}</td>
          <td class=\"px-3 py-2\">${s.Number_of_Absences ?? s.Absences ?? ''}</td>
          <td class=\"px-3 py-2\">${s.Aggregate_Grade ?? s.Final_Grade ?? s.Grade_2 ?? s.Grade_1 ?? 'N/A'}</td>
          <td class=\"px-3 py-2\">${label}</td>
        `;
        tbody.appendChild(tr);
      };

      if (selected) {
        document.getElementById('summary').textContent = 'Report for: ' + (selected.Name || 'Student');
        renderRow(selected);
      } else {
        // Full report: show totals summary header
        // Fetch risk summary for counts
        try {
          const sres = await fetch('/risk_summary');
          const s = await sres.json();
          document.getElementById('summary').innerHTML = `
            <div>Total students: <b>${s.total}</b> — 
            <span class=\"text-red-600\">Red: <b>${s.red}</b></span>, 
            <span class=\"text-yellow-600\">Yellow: <b>${s.yellow}</b></span>, 
            <span class=\"text-green-600\">Green: <b>${s.green}</b></span></div>`;
        } catch (e) {
          document.getElementById('summary').textContent = 'Full report';
        }
        students.forEach(renderRow);
      }
    });
  </script>
</body>
</html>
"""

@app.route('/print_report')
def print_report():
    return render_template_string(PRINT_REPORT_HTML)

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
        form_html = """
        <!DOCTYPE html>
        <html lang=\"en\"><head>
        <meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>Edit Student</title>
        <script src=\"https://cdn.tailwindcss.com\"></script>
        </head><body class=\"p-6\">
        <div class=\"mb-4\"><a class=\"text-blue-600 hover:underline\" href=\"/students_view\">Back</a></div>
        <h1 class=\"text-2xl font-bold mb-4\">Edit Student</h1>
        <form id="editForm" class="space-y-4 max-w-xl\">
            <input type="hidden" name="gindex" value="{{ idx }}" />
            <div><label class="block text-sm">Name</label><input name="name" class="border p-2 w-full rounded" value="{{ name }}" /></div>
            <div class="grid grid-cols-2 gap-3"> 
                <div><label class="block text-sm">Gender</label>
                    <select name="gender" class="border p-2 w-full rounded"><option value="F" {{ 'selected' if gender=='F' else '' }}>Female</option><option value="M" {{ 'selected' if gender=='M' else '' }}>Male</option></select>
                </div>
                <div><label class="block text-sm">Age</label><input type="number" name="age" class="border p-2 w-full rounded" value="{{ age }}" /></div>
            </div>
            <div class="grid grid-cols-3 gap-3">
                <div><label class="block text-sm">Absences</label><input type="number" name="absences" class="border p-2 w-full rounded" value="{{ absences }}" /></div>
                <div><label class="block text-sm">Aggregate Grade (0-20)</label><input type="number" step="0.1" min="0" max="20" name="aggregate_grade" class="border p-2 w-full rounded" value="{{ aggregate }}" /></div>
                <div><label class="block text-sm">Internet</label>
                    <select name="internet_access" class="border p-2 w-full rounded"><option value="yes" {{ 'selected' if internet=='yes' else '' }}>Yes</option><option value="no" {{ 'selected' if internet=='no' else '' }}>No</option></select>
                </div>
            </div>
            <div><label class="block text-sm">Desired Risk Zone</label>
                <select name="desired_risk_zone" class="border p-2 w-full rounded\">
                    <option value=\"\">-- None --</option>
                    <option value=\"Red\">Red</option>
                    <option value=\"Yellow\">Yellow</option>
                    <option value=\"Green\">Green</option>
                </select>
            </div>
            <button class="px-4 py-2 bg-blue-600 text-white rounded" type="submit">Save</button>
        </form>
        <script>
        document.getElementById('editForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = Object.fromEntries(new FormData(e.target).entries());
            const res = await fetch('/edit_student?gindex=' + encodeURIComponent(payload.gindex || payload.index), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            const data = await res.json();
            if (!res.ok) { alert('Update failed: ' + (data.error||'Unknown')); return; }
            alert('Updated'); window.location.href = '/students_view';
        });
        </script>
        </body></html>
        """
        name_value = str(s.get('Name',''))
        gender_value = s.get('Gender','')
        age_value = s.get('Age','')
        absences_value = s.get('Number_of_Absences', s.get('Absences',''))
        aggregate_value = s.get('Aggregate_Grade', s.get('Final_Grade', s.get('Grade_2', s.get('Grade_1',''))))
        internet_value = str(s.get('Internet_Access','')).lower()
        return render_template_string(form_html, idx=idx, name=name_value, gender=gender_value, age=age_value, absences=absences_value, aggregate=aggregate_value, internet=internet_value)

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

        # Refresh dashboard data
        DASHBOARD_DATA = STUDENTS_DF.copy()
        if 'Dropped_Out' in DASHBOARD_DATA.columns:
            DASHBOARD_DATA['DropoutFlag'] = (DASHBOARD_DATA['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes').astype(int)
        else:
            DASHBOARD_DATA['DropoutFlag'] = (DASHBOARD_DATA['Risk_Category'].astype(str).str.strip().str.lower() == 'red').astype(int)

        write_students_json(STUDENTS_DF, os.path.join(os.path.dirname(__file__), JSON_OUTPUT_FILENAME))
        write_students_csv(STUDENTS_DF, os.path.join(os.path.dirname(__file__), CSV_FILENAME))

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
        DASHBOARD_DATA = STUDENTS_DF.copy()
        if 'Dropped_Out' in DASHBOARD_DATA.columns:
            DASHBOARD_DATA['DropoutFlag'] = (DASHBOARD_DATA['Dropped_Out'].astype(str).str.strip().str.lower() == 'yes').astype(int)
        else:
            DASHBOARD_DATA['DropoutFlag'] = (DASHBOARD_DATA['Risk_Category'].astype(str).str.strip().str.lower() == 'red').astype(int)
        return jsonify({'status': 'ok', 'deleted': deleted_label})
    except Exception as e:
        app.logger.error(f"Delete student error: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Log the successful training and start the server
    print("----------------------------------------------------------------------")
    print("FLASK APP READY: Running Dropout Predictor.")
    print("Access the homepage at: http://127.0.0.1:5000/")
    print("Dashboard at: http://127.0.0.1:5000/dashboard")
    print("----------------------------------------------------------------------")
    # In a production environment, you would use a WSGI server (like gunicorn)
    # and properly load the model from a file using joblib or pickle.
    app.run(debug=True)
